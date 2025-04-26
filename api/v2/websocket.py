import asyncio
import os
import secrets
import jwt
from typing import cast
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from srptools import SRPServerSession, SRPContext, constants, utils

from ..database import get_session, async_session
from ..models import *

JWT_SECRET_KEY = "837rv0h23r823g9fdr5g8iuftz6fw039gf94ciko35h7w38ugzfi3"
JWT_ALG = "HS256"

def calc_jwt(employee:Employee, session_id:str) -> str:
    payload = {
        "user_id": employee.id,
        "session_id": session_id,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

router = APIRouter()

connected_clients: set[WebSocket] = set()

PRIME = constants.PRIME_2048
GEN = constants.PRIME_2048_GEN

def start_up():
    asyncio.create_task(heartbeat())

def generate_challenge(length: int = 16) -> str:
    return secrets.token_hex(length)

async def emit(message: str):
    to_remove = set()
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception:
            to_remove.add(client)
            _ = client.close(reason="ping failed")
    connected_clients.difference_update(to_remove)
    
async def heartbeat():
    while True:
        async with async_session() as session:
            await emit("ping")
        await asyncio.sleep(10)

@router.websocket("/")
async def websocket_auth(websocket: WebSocket, session: AsyncSession = Depends(get_session)):
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"ws connected; {len(connected_clients)} clients connected")
    try:
        server_session:Optional[tuple[SRPServerSession, datetime.datetime, Employee]] = None
        while True:
            data = await websocket.receive_json()

            if server_session == None:
                if not data.get("type") == "init":
                    raise
                username = data.get("username")
                employee = (await session.execute(select(Employee).where(Employee.username == username))).scalar_one_or_none()
                if not employee:
                    await websocket.send_json({"type": "error", "message": "User not found"})
                    continue

                server_session = SRPServerSession(SRPContext(username=username, prime=PRIME, generator=GEN), employee.verifier), datetime.datetime.now(), employee
                server_public = server_session[0].public
                if isinstance(server_public, bytes): server_public = server_public.decode()

                await websocket.send_json({
                    "type": "init",
                    "salt": employee.salt,
                    "server_public": server_public
                })

            elif server_session != None and server_session[1] + datetime.timedelta(seconds=10) > datetime.datetime.now():
                if not data.get("type") == "verify":
                    raise 
                username = data.get("username")
                if server_session[2].username != username:
                    await websocket.send_json({"type": "error", "message": "different username then frst step"})
                    continue
                client_public:str = data["client_public"]
                client_session_key_proof:str = data["client_session_key_proof"]

                try:
                    server_session[0].process(client_public, server_session[2].salt)
                    assert server_session[0].verify_proof(client_session_key_proof.encode())
                    server_session_key_proof_hash = server_session[0].key_proof_hash
                    if isinstance(server_session_key_proof_hash, bytes): server_session_key_proof_hash = server_session_key_proof_hash.decode()
                    key = server_session[0].key
                    if isinstance(key, bytes): key = key.decode()
                    auth_session = AuthSession(id=os.urandom(16).hex(), challange=generate_challenge(), key=cast(str, key), user_id=server_session[2].id_strict)
                    session.add(auth_session)
                    await session.commit()
                    await session.refresh(auth_session)

                    jwt = calc_jwt(employee=server_session[2], session_id=auth_session.id)

                    await websocket.send_json({"type": "success", "server_session_key_proof_hash": server_session_key_proof_hash, "challange": auth_session.challange, "jwt_id_token": jwt})
                    server_session = None
                except Exception as e:
                    print(e)
                    await websocket.send_json({"type": "error", "message": "Authentication failed"})
                    server_session = None
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print(f"ws connected; {len(connected_clients)} clients connected")