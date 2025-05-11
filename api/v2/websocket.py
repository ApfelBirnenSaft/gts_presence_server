import asyncio
import json
import secrets
import time
import jwt
import uuid
from typing import cast
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlmodel import select
from srptools import SRPServerSession, SRPContext, constants, utils
import logging

logger = logging.getLogger("uvicorn.error")

from api.database import get_session, async_session
from api.models import *
from utils import get_datetime_utc

JWT_SECRET_KEY = "837rv0h23r823g9fdr5g8iuftz6fw039gf94ciko35h7w38ugzfi3"
JWT_ALG = "HS256"

router = APIRouter()

connected_clients: set[WebSocket] = set()

PRIME = constants.PRIME_2048
GEN = constants.PRIME_2048_GEN

def start_up():
    asyncio.create_task(heartbeat())

async def emit(message: dict):
    to_remove = set()
    for client in connected_clients:
        try:
            await client.send_json(message)
        except Exception:
            to_remove.add(client)
            _ = client.close(reason="ping failed")
    connected_clients.difference_update(to_remove)

HEARTBEAT_INTERVAL = datetime.timedelta(seconds=10)
HEARTBEAT_TIMEOUT = datetime.timedelta(seconds=12)
    
async def heartbeat():
    while True:
        async with async_session() as session:
            payload = {
                "type": "ping",
                "versions": await get_versions_dict(session=session),
                "timestamp": get_datetime_utc().isoformat()
            }
            await emit(payload)
        await asyncio.sleep(HEARTBEAT_INTERVAL.total_seconds())

@router.websocket("")
async def websocket_handler(websocket: WebSocket, session: AsyncSession = Depends(get_session)):
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info(f"ws connected; {len(connected_clients)} clients connected")
    last_pong_time = get_datetime_utc()

    async def check_timeout():
        nonlocal last_pong_time
        while True:
            await asyncio.sleep(max(HEARTBEAT_INTERVAL.total_seconds(), (last_pong_time + HEARTBEAT_TIMEOUT - get_datetime_utc()).total_seconds() + .1))
            #logger.debug(f"ws time out check")
            if get_datetime_utc() - last_pong_time > (HEARTBEAT_TIMEOUT):
                await websocket.close(reason="timed out")
                logger.info(f"ws timed out")
                break

    async def receive():
        nonlocal last_pong_time
        try:
            while True:
                data = await websocket.receive_json()
                try:
                    if data["type"] == "pong":
                        last_pong_time = get_datetime_utc()
                        #logger.debug("ws pong received")
                except:
                    pass
        except WebSocketDisconnect:
            connected_clients.remove(websocket)
            logger.info(f"ws connected; {len(connected_clients)} clients connected")
    await asyncio.gather(check_timeout(), receive())