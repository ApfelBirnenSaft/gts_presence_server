import base64
from functools import wraps
import os
import random
import secrets
import time
from typing import Callable, Dict, cast, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Response, status, Query
from fastapi.responses import JSONResponse
import sqlalchemy
from sqlmodel import Session, select
from pydantic import BaseModel
import datetime
import hmac
import jwt
import hashlib
from srptools import SRPServerSession, SRPContext, constants, utils, hex_from_b64
from sqlalchemy.ext.asyncio import AsyncSession
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

from api.database import get_session, async_session, versioning
from api.models import *
from utils import get_datetime_utc

from .websocket import router as ws_router, emit, start_up as ws_startup, JWT_SECRET_KEY, JWT_ALG

SESSION_DURATION = datetime.timedelta(hours=1)

PRIME = constants.PRIME_2048
GEN = constants.PRIME_2048_GEN

def decode_token(token: str) -> dict:
    try:
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALG])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token abgelaufen")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Ungültiges Token")

def start_up():
    ws_startup()

def calc_hmac(data: bytes, key: bytes) -> str:
    h = hmac.new(key, data, hashlib.sha256)
    return h.hexdigest()

def verify_hmac(data: bytes, key: bytes, expected_hmac: str) -> bool:
    return hmac.compare_digest(calc_hmac(data, key), expected_hmac)

router = APIRouter()
router.include_router(ws_router, prefix="/ws")

def verify(sec_lvl: int):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with async_session() as session:
                request: Request = kwargs["request"]
                remote_challange = request.headers["Auth-Challenge"]
                auth_id_token = request.headers["Auth-Id-Token"]

                auth_id = decode_token(auth_id_token)

                auth_session = await session.get(AuthSession, auth_id["session_id"])

                if not auth_session:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="auth: auth session not found")

                if auth_id["user_id"] != auth_session.user_id:
                    await session.delete(auth_session)
                    await session.commit()
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="auth: employee id mismatch, session deleted")
                
                employee = await session.get(Employee, auth_id["user_id"])
                if not employee:
                    await session.delete(auth_session)
                    await session.commit()
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="auth: employee not found, session deleted")
                
                authed = verify_hmac(bytes.fromhex(auth_session.challange), auth_session.key.encode(), remote_challange)
                if not authed:
                    await session.delete(auth_session)
                    await session.commit()
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="auth: verification failed")

                if employee.sec_lvl < sec_lvl:
                    auth_session.challange = generate_challenge()
                    await session.commit()
                    await session.refresh(auth_session)
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="auth: insufficient sec level", headers={"X-Challenge": auth_session.challange})
                
                request.state.auth_key = auth_session.key
                result = await func(*args, **kwargs)

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
        context = SRPContext(user_data.username, user_data.password, prime=PRIME, generator=GEN)
        username, verifier, salt = context.get_user_data_triplet()
        if isinstance(verifier, bytes): verifier = verifier.decode()
        if isinstance(salt, bytes): salt = salt.decode()
        employee = Employee(username=username, salt=cast(str, salt), verifier=cast(str, verifier), sec_lvl=1, first_name=user_data.first_name, last_name=user_data.last_name, title=user_data.title, salutation=user_data.salutation)
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
    username: str
    password: str
@router.post("/set_pw")
async def set_pw(user_data: NewPwPost, session: AsyncSession = Depends(get_session)):
    employee = (await session.execute(select(Employee).where(Employee.username == user_data.username))).scalar_one_or_none()
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

def verify_and_decrypt(json_payload: dict, key_hex: str) -> dict:
    # === Schlüssel aus SRP-Key ableiten ===
    key_bytes = bytes.fromhex(key_hex)
    key_enc = hashlib.sha256(key_bytes + b'enc').digest()[:32]
    key_mac = hashlib.sha256(key_bytes + b'mac').digest()[:32]

    # === Base64-Daten aus JSON extrahieren ===
    iv = base64.b64decode(json_payload['iv'])
    ciphertext = base64.b64decode(json_payload['ciphertext'])
    mac_received = base64.b64decode(json_payload['mac'])

    # === MAC prüfen ===
    mac_calculated = hmac.new(key_mac, iv + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(mac_received, mac_calculated):
        raise ValueError("❌ Ungültige Signatur (HMAC)")

    # === Entschlüsselung (AES-CBC) ===
    cipher = Cipher(algorithms.AES(key_enc), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # === Padding entfernen (PKCS7) ===
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    return json.loads(plaintext.decode('utf-8'))

@router.post('/secure')
@verify(1)
async def secure_test(request:Request):
    #auth_key = request.state.auth_key
    #print(verify_and_decrypt(await request.json(), auth_key)["users"])
    return JSONResponse(content={"details": "verified"})

@router.get('/test')
async def get_data(request:Request, version_ids_json: str = Query(), session: AsyncSession = Depends(get_session)):
    await emit("test called")
    version_ids: Dict[str, int] = json.loads(version_ids_json)
    #await session.delete((await session.get(Employee, 4)))
    #session.add(StudentNote.get_version_class()(version_operation=versioning.Operation.INSERT, id=1, date_time=get_datetime_utc(), issuer_id=1, student_id=1, note="Notiz 1"))
    #await session.commit()
    data = {}
    classes: dict[str, type[DBModel]] = {}
    versioned_classes: dict[str, type[VersionedDBModel]] = {"employee": Employee, "activity": Activity}
    for cls_str, version_id in version_ids.items():
        if cls_str in classes:
            cls = classes[cls_str]
        elif cls_str in versioned_classes:
            versioned_cls = versioned_classes[cls_str]
            data[cls_str] = await versioned_cls.get_changes(session, version_id, None)
        else:
            raise HTTPException(404, detail=f"tried to get non-existend object \"{cls_str}\"")
    return JSONResponse(content=data)

# Temporärer Speicher für aktive SRP-Sessions
def generate_challenge(length: int = 16) -> str:
    return secrets.token_hex(length)
