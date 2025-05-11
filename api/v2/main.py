from typing import Dict, cast, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Response, status, Query
from fastapi.responses import JSONResponse
import sqlalchemy
from sqlmodel import select
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session, AppendOnlyDBModel, VersionedDBModel
from api.models import Employee, Activity, StudentActivityPresence, Student, StudentNote, StudentAbsentIrregular, StudentAbsentRegular, get_versions_dict
from .auth import router as auth_router, verify, verify_and_decrypt, encrypt_and_sign, AuthSession, PRIME, GEN, constants, SRPContext

from .websocket import router as ws_router, emit, start_up as ws_startup

def start_up():
    ws_startup()

router = APIRouter()
router.include_router(ws_router, prefix="/ws")
router.include_router(auth_router, prefix="/auth")

class NewEmployeePost(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    title: Optional[str]
    salutation: str
@router.post("/user", response_model=Employee)
async def create_user(user_data: NewEmployeePost, session: AsyncSession = Depends(get_session)):
    try:
        context = SRPContext(user_data.username, user_data.password, prime=PRIME, generator=GEN, hash_func=constants.HASH_SHA_256)
        username, verifier, salt = context.get_user_data_triplet()
        if isinstance(verifier, bytes): verifier = verifier.decode()
        if isinstance(salt, bytes): salt = salt.decode()
        employee = Employee(username=username, salt=cast(str, salt), verifier=cast(str, verifier), sec_lvl=1, first_name=user_data.first_name, last_name=user_data.last_name, title=user_data.title, salutation=user_data.salutation, monday_homework_room_id=None, tuesday_homework_room_id=None, wednesday_homework_room_id=None, thursday_homework_room_id=None, monday_school_club_id=None, tuesday_school_club_id=None, wednesday_school_club_id=None, thursday_school_club_id=None)
        session.add(employee)
        await session.commit()
        await session.refresh(employee)
    except sqlalchemy.exc.IntegrityError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="IntegrityError: username may already exist")
    return employee

@router.get("/users", response_model=list[Employee])
async def read_users(session: AsyncSession = Depends(get_session)):
    return (await session.execute(select(Employee))).scalars()

class NewPwPost(BaseModel):
    user_id: int
    password: str # TODO: calculate verifier and salt  by client
    #verifier: str
    #salt: str
@router.post("/set_pw")
async def set_pw(data: NewPwPost, session: AsyncSession = Depends(get_session)):
    employee = (await session.get(Employee, data.user_id))
    if isinstance(employee, Employee):
        context = SRPContext(employee.username, data.password, prime=PRIME, generator=GEN)
        _, verifier, salt = context.get_user_data_triplet()
        if isinstance(verifier, bytes): verifier = verifier.decode()
        if isinstance(salt, bytes): salt = salt.decode()
        verifier = cast(str, verifier)
        salt = cast(str, salt)
        employee.verifier = verifier
        employee.salt = salt
        await session.commit()
        return None
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="username not found")
    

class LoginRequest(BaseModel):
    username: str
    password: str
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    username: str
@router.post('/login', response_model=LoginResponse)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    employee = (await session.execute(select(Employee).where(Employee.username == data.username))).scalar_one_or_none()
    if isinstance(employee, Employee):
        if employee.username == data.password:
            return LoginResponse(access_token="", refresh_token="", username=employee.username)
        else:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    raise HTTPException(status.HTTP_404_NOT_FOUND)

@router.post('/secure')
@verify(1)
async def secure_test(request:Request):
    #auth_key = request.state.auth_key
    #print(verify_and_decrypt(await request.json(), auth_key)["users"])
    return JSONResponse(content={"details": "verified"})

@router.get('/get_versions')
async def get_versions(session: AsyncSession = Depends(get_session)):
    return await get_versions_dict(session)

@router.get('/get_data')
@verify(1)
async def get_data(request:Request):
    #await emit("test called")
    version_ids: Dict[str, int] = {key: int(value) for key, value in request.query_params.items()}
    data = {}
    append_classes: dict[str, type[AppendOnlyDBModel]] = {"student_activity_presence": StudentActivityPresence}
    versioned_classes: dict[str, type[VersionedDBModel]] = {
        "employee": Employee,
        "activity": Activity,
        "student": Student,
        "student_note": StudentNote,
        "student_absent_irregular": StudentAbsentIrregular,
        "student_absent_regular": StudentAbsentRegular}
    for cls_str, version_id in version_ids.items():
        if cls_str in append_classes:
            cls = append_classes[cls_str]
            data[cls_str] = await cls.get_new(request.state.db_session, version_id, None)
        elif cls_str in versioned_classes:
            versioned_cls = versioned_classes[cls_str]
            data[cls_str] = await versioned_cls.get_changes(request.state.db_session, version_id, None)
        else:
            raise HTTPException(404, detail=f"tried to get non-existend class '{cls_str}'")
    return JSONResponse(content=encrypt_and_sign(data, request.state.auth_session.key))
