import base64
from functools import wraps
import os
import random
import secrets
import time
from typing import Callable, cast
from fastapi import APIRouter, HTTPException, Depends, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import sqlalchemy
from sqlmodel import Session, select
from pydantic import BaseModel
import datetime
import hmac
import hashlib
from srptools import SRPServerSession, SRPContext, constants, utils, hex_from_b64
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import *
from ..database import get_session, engine, async_session
from ..session_db import AuthSession

from .websocket import router as ws_router, emit, start_up as ws_startup

PRIME = constants.PRIME_2048
GEN = constants.PRIME_2048_GEN

def start_up():
    ws_startup()

def calc_hmac(data: bytes, key: bytes) -> str:
    h = hmac.new(key, data, hashlib.sha1)
    return h.hexdigest()

def verify_hmac(data: bytes, key: bytes, expected_hmac: str) -> bool:
    return hmac.compare_digest(calc_hmac(data, key), expected_hmac)

router = APIRouter()
router.include_router(ws_router, prefix="/ws")

def verify(sec_lvl: int):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            async with async_session() as session:
                remote_challange = request.headers["Auth-Challenge"]
                auth_session_id = int(request.headers["Auth-Session-Id"])
                auth_session = await session.get(AuthSession, auth_session_id)

                if not auth_session:
                    return HTTPException(status_code=404, detail="auth: auth session not found")

                employee_username = request.headers["Auth-Username"]
                if employee_username != auth_session.username:
                    await session.delete(auth_session)
                    await session.commit()
                    raise HTTPException(status_code=404, detail="auth: employee id mismatch, session deleted")
                
                employee = await session.get(Employee, employee_username)
                if not employee:
                    await session.delete(auth_session)
                    await session.commit()
                    raise HTTPException(status_code=404, detail="auth: employee not found, session deleted")
                
                authed = verify_hmac(bytes.fromhex(auth_session.challange), auth_session.key.encode(), remote_challange)
                if not authed:
                    await session.delete(auth_session)
                    await session.commit()
                    return JSONResponse(status_code=401, content={"detail": "auth: Unauthorized, session deleted"})

                if employee.sec_lvl < sec_lvl:
                    auth_session.challange = generate_challenge()
                    await session.commit()
                    await session.refresh(auth_session)
                    return JSONResponse(status_code=401, content={"detail": "auth: unsufficient sec level"}, headers={"X-Challenge": auth_session.challange})

                result = await func(*args, request=request, **kwargs)

                auth_session.challange = generate_challenge()
                await session.commit()
                await session.refresh(auth_session)

                if isinstance(result, Response):
                    result.headers["X-Challenge"] = auth_session.challange
                    return result
                else:
                    raise
        return wrapper
    return decorator

class EmployeePost(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    title: Optional[str]
    salutation: str
@router.post("/user", response_model=Employee)
async def create_user(user_data: EmployeePost, session: AsyncSession = Depends(get_session)):
    try:
        context = SRPContext(user_data.username, user_data.password, prime=PRIME, generator=GEN)
        username, verifier, salt = context.get_user_data_triplet()
        if isinstance(verifier, bytes): verifier = verifier.decode()
        if isinstance(salt, bytes): salt = salt.decode()
        employee = Employee(username=username, salt=cast(str, salt), verifier=cast(str, verifier), sec_lvl=1, first_name=user_data.first_name, last_name=user_data.last_name, title=user_data.title, salutation=user_data.salutation)
        session.add(employee)
        await session.commit()
        await session.refresh(employee)
    except sqlalchemy.exc.IntegrityError as e:
        raise HTTPException(409, detail="IntegrityError: username may already exist")
    return employee

@router.get("/users", response_model=list[Employee])
async def read_users(session: AsyncSession = Depends(get_session)):
    return (await session.execute(select(Employee))).scalars()

@router.post("/set_pw")
async def set_pw(user_data: EmployeePost, session: AsyncSession = Depends(get_session)):
    employee = await session.get(Employee, user_data.username)
    if isinstance(employee, Employee):
        context = SRPContext(user_data.username, user_data.password, prime=PRIME, generator=GEN)
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
        raise HTTPException(404, detail="username not found")
    

class LoginRequest(BaseModel):
    username: str
    password: str
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    username: str
@router.post('/login', response_model=LoginResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    employee = session.exec(select(Employee).filter_by(username = data.username)).first()
    if isinstance(employee, Employee):
        if employee.username == data.password:
            return LoginResponse(access_token="", refresh_token="", username=employee.username)
        else:
            raise HTTPException(401)
    raise HTTPException(404)


@router.get('/secure')
@verify(1)
async def secure_test(request:Request):
    return JSONResponse(content={"details": "verified"})

@router.get('/test')
async def test(request:Request, session: AsyncSession = Depends(get_session)):
    await emit("test called")
    return JSONResponse(content={"details": "test"})

# Temporärer Speicher für aktive SRP-Sessions
def generate_challenge(length: int = 16) -> str:
    return secrets.token_hex(length)
