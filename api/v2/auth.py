import asyncio
import base64
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import hashlib
import hmac
import json
import os
from typing import Callable, Optional, Union, cast
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
import jwt
from pydantic import BaseModel, UUID4
import datetime
from diskcache import Cache
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from srptools import SRPServerSession, SRPContext, constants

from api.models import Employee
from utils import verify_hmac, calc_hmac, generate_challenge, get_datetime_utc
from .websocket import JWT_SECRET_KEY, JWT_ALG
from api.database import async_session, get_session

GEN = '2'
PRIME = '''\
AC6BDB41324A9A9BF166DE5E1389582FAF72B6651987EE07FC3192943DB56050A37329CB\
B4A099ED8193E0757767A13DD52312AB4B03310DCD7F48A9DA04FD50E8083969EDB767B0\
CF6095179A163AB3661A05FBD5FAAAE82918A9962F0B93B855F97993EC975EEAA80D740A\
DBF4FF747359D041D5C33EA71D281E446B14773BCA97B43A23FB801676BD207A436C6481\
F1D2B9078717461A5B9D32E688F87748544523B524B0D57D5EA77A2775D2ECFA032CFBDB\
F52FB3786160279004E57AE6AF874E7303CE53299CCC041C7BC308D82A5698F3A8D0C382\
71AE35F8E9DBFBB694B5C803D89F7AE435DE236D525F54759B65E372FCD68EF20FA7111F\
9E4AFF73
'''

SESSION_DURATION = datetime.timedelta(hours=1)
CONTEXT_DURATION = datetime.timedelta(seconds=30)

cache = Cache("./cache")
executor = ThreadPoolExecutor()

router = APIRouter()
        
class AuthSession(BaseModel):
    id: UUID4
    user_id: int
    challenge: str
    key: str
    created_at: datetime.datetime
    valid_for: datetime.timedelta

    @staticmethod
    def chache_key(id: UUID4) -> str: return f"session:{id.hex}"
        
class AuthContext(BaseModel):
    id: UUID4
    user_id: int
    privat: str
    created_at: datetime.datetime
    valid_for: datetime.timedelta

    @staticmethod
    def chache_key(id: UUID4) -> str: return f"context:{id.hex}"
        
class PasswordSetToken(BaseModel):
    id: UUID4
    user_id: int
    code: str
    created_at: datetime.datetime
    valid_for: datetime.timedelta

    @staticmethod
    def chache_key(id: UUID4) -> str: return f"pw_reset:{id.hex}"

def store_in_cache(obj: Union[AuthSession, AuthContext, PasswordSetToken]):
    key = type(obj).chache_key(obj.id)
    cache.set(key, obj.model_dump_json(), expire=obj.valid_for.total_seconds())

def get_from_cache(type_: Union[type[AuthSession], type[AuthContext], type[PasswordSetToken]], id_: UUID4) -> Optional[Union[AuthSession, AuthContext, PasswordSetToken]]:
    key = type_.chache_key(id_)
    value = cache.get(key)
    return type_.model_validate_json(value) if isinstance(value, str) else None

def delete_from_cache(obj: Union[AuthSession, AuthContext, PasswordSetToken]) -> None:
    key = type(obj).chache_key(obj.id)
    cache.delete(key)

def calc_jwt(employee:Employee, session_id:uuid.UUID) -> str:
    payload = {
        "user_id": employee.id,
        "session_id": session_id.hex,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict:
    try:
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALG])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token abgelaufen")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Ungültiges Token")

def verify(sec_lvl: int):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs["request"]
            remote_challange = request.headers["Auth-Challenge"]
            auth_id_token = request.headers["Auth-Id-Token"]

            auth_id = decode_token(auth_id_token)

            auth_session = cast(Optional[AuthSession], await asyncio.get_event_loop().run_in_executor(executor, get_from_cache, AuthSession, uuid.UUID(hex=auth_id["session_id"])))

            if not auth_session:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="auth: auth session not found")

            if auth_id["user_id"] != auth_session.user_id:
                await asyncio.get_event_loop().run_in_executor(executor, delete_from_cache, auth_session)
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="auth: employee id mismatch, session deleted")
            
            async with async_session.begin() as session:
                employee = await session.get(Employee, auth_id["user_id"])
                if not employee:
                    await asyncio.get_event_loop().run_in_executor(executor, delete_from_cache, auth_session)
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="auth: employee not found, session deleted")
                
                authed = verify_hmac(calc_hmac(bytes.fromhex(auth_session.challenge), bytes.fromhex(auth_session.key)), remote_challange)
                if not authed:
                    await asyncio.get_event_loop().run_in_executor(executor, delete_from_cache, auth_session)
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="auth: verification failed, session deleted")

                if employee.sec_lvl < sec_lvl:
                    auth_session.challenge = generate_challenge()
                    await asyncio.get_event_loop().run_in_executor(executor, store_in_cache, auth_session)
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="auth: insufficient sec level", headers={"X-Challenge": auth_session.challenge})
                
                request.state.auth_session = auth_session
                request.state.db_session = session
                result = await func(*args, **kwargs)

            auth_session.challenge = generate_challenge()
            await asyncio.get_event_loop().run_in_executor(executor, store_in_cache, auth_session)

            if isinstance(result, Response):
                result.headers["X-Challenge"] = auth_session.challenge
                return result
            else:
                raise
        return wrapper
    return decorator

def verify_and_decrypt(json_payload: dict, key_hex: str) -> dict:
    key_bytes = bytes.fromhex(key_hex)
    key_enc = hashlib.sha256(key_bytes + b'enc').digest()[:32]
    key_mac = hashlib.sha256(key_bytes + b'mac').digest()[:32]

    iv = base64.b64decode(json_payload['iv'])
    ciphertext = base64.b64decode(json_payload['ciphertext'])
    mac_received = base64.b64decode(json_payload['mac'])

    mac_calculated = hmac.new(key_mac, iv + ciphertext, hashlib.sha256).digest()
    if not verify_hmac(mac_received, mac_calculated):
        raise ValueError("❌ Ungültige Signatur (HMAC)")

    cipher = Cipher(algorithms.AES(key_enc), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    return json.loads(plaintext.decode('utf-8'))

def encrypt_and_sign(data: dict, key_hex: str) -> dict:
    key_bytes = bytes.fromhex(key_hex)
    key_enc = hashlib.sha256(key_bytes + b'enc').digest()[:32]
    key_mac = hashlib.sha256(key_bytes + b'mac').digest()[:32]

    plaintext = json.dumps(data).encode('utf-8')

    padder = padding.PKCS7(128).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()

    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key_enc), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    mac = hmac.new(key_mac, iv + ciphertext, hashlib.sha256).digest()

    return {
        'iv': base64.b64encode(iv).decode('utf-8'),
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
        'mac': base64.b64encode(mac).decode('utf-8')
    }

class InitRequest(BaseModel):
    username: str
class InitResponse(BaseModel):
    session_token: str
    server_public: str
    salt: str
@router.post('/init', response_model=InitResponse)
async def init_auth(data: InitRequest, session: AsyncSession = Depends(get_session)):
    employee = (await session.execute(select(Employee).where(Employee.username == data.username))).scalar_one_or_none()
    if not employee:
        raise HTTPException(404, detail="User not found")
    
    server_session = SRPServerSession(SRPContext(username=employee.username, prime=PRIME, generator=GEN, hash_func=constants.HASH_SHA_256), employee.verifier)
    server_public = server_session.public
    if isinstance(server_public, bytes): server_public = server_public.decode()

    auth_context = AuthContext(id=uuid.uuid4(), user_id=employee.id_strict, privat=str(server_session.private), created_at=get_datetime_utc(), valid_for=CONTEXT_DURATION)
    store_in_cache(auth_context)

    session_token = calc_jwt(employee, auth_context.id)

    return InitResponse(session_token=session_token, server_public=cast(str, server_public), salt=employee.salt)

class FinalizeRequest(BaseModel):
    client_session_key_proof: str
    client_public: str
    session_token: str
class FinalizeResponse(BaseModel):
    server_session_key_proof_hash: str
    user_encrypted: dict
    jwt_id_token: str
    challenge: str
@router.post('/finalize', response_model=FinalizeResponse)
async def finalize_auth(data: FinalizeRequest, session: AsyncSession = Depends(get_session)):
    session_token = decode_token(data.session_token)
    employee = await session.get(Employee, session_token["user_id"])

    if employee == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    
    auth_context = cast(Optional[AuthContext], get_from_cache(AuthContext, uuid.UUID(session_token["session_id"])))

    if auth_context == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "auth_context_session not found")
    
    if employee.id != auth_context.user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="user_id of auth_context and of jwt token do not match")

    server_session = SRPServerSession(SRPContext(username=employee.username, prime=PRIME, generator=GEN, hash_func=constants.HASH_SHA_256), employee.verifier, private=auth_context.privat)
    server_session.process(data.client_public, employee.salt)
    try:
        assert server_session.verify_proof(data.client_session_key_proof.encode())
        server_session_key_proof_hash = server_session.key_proof_hash
        if isinstance(server_session_key_proof_hash, bytes): server_session_key_proof_hash = server_session_key_proof_hash.decode()
        key = server_session.key
        if isinstance(key, bytes): key = key.decode()
        auth_session = AuthSession(id=uuid.uuid4(), user_id=employee.id_strict, challenge=generate_challenge(), key=cast(str, key), created_at=get_datetime_utc(), valid_for=SESSION_DURATION)
        store_in_cache(auth_session)

        jwt = calc_jwt(employee=employee, session_id=auth_session.id)

        delete_from_cache(auth_context)
    except ValueError as e:
        delete_from_cache(auth_context)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return FinalizeResponse(server_session_key_proof_hash=cast(str, server_session_key_proof_hash), user_encrypted=encrypt_and_sign(employee.model_dump(mode="json"), auth_session.key), jwt_id_token=jwt, challenge=auth_session.challenge)