import asyncio
from typing import cast
import websockets
import json
import requests
from srptools import SRPClientSession, SRPContext, constants
from hashlib import sha1
import hmac, time

def calc_hmac(data: bytes, key: bytes) -> str:
    h = hmac.new(key, data, sha1)
    return h.hexdigest()

ENCODING = "UTF-8"

# Userdaten (müssen mit Serverdaten übereinstimmen!)
USERNAME = "ASt"
PASSWORD = "pass"

PRIME = constants.PRIME_2048
GEN = constants.PRIME_2048_GEN

async def srp_auth():
    uri = "ws://localhost:8000/api/v2/ws/"

    async with websockets.connect(uri) as websocket:
        # Step 1: Init mit Username senden
        await websocket.send(json.dumps({
            "type": "init",
            "username": USERNAME
        }))

        # Antwort mit Salt und B empfangen
        response = await websocket.recv()
        data = json.loads(response)
        print(data)
        #assert data["type"] == "init"
        salt:str = data["salt"]
        server_public:str = data["server_public"]

        client_session = SRPClientSession(SRPContext(USERNAME, PASSWORD, prime=PRIME, generator=GEN))
        client_session.process(server_public, salt)
        client_public = client_session.public
        if isinstance(client_public, bytes): client_public = client_public.decode()
        client_session_key_proof  = client_session.key_proof
        if isinstance(client_session_key_proof, bytes): client_session_key_proof = client_session_key_proof.decode()

        # Step 2: Verify senden
        await websocket.send(json.dumps({
            "type": "verify",
            "username": USERNAME,
            "client_public": client_public,
            "client_session_key_proof": client_session_key_proof 
        }))

        # Serverantwort mit M2 empfangen
        response = await websocket.recv()
        data = json.loads(response)
        if data["type"] == "success":
            server_session_key_proof_hash = data.pop("server_session_key_proof_hash")
            if client_session.verify_proof(server_session_key_proof_hash.encode()):
                print("✅ Authentifizierung erfolgreich")
                session_id = str(data["session_id"])
                key = client_session.key
                if isinstance(key, bytes): key = key.decode()
                url = "http://localhost:8000/api/v2/secure"
                challange = data["challange"]
                print(session_id)
                print("key", key)
                print("challenga", challange)
                return
                for i in range(2):
                    hmac_value = calc_hmac(bytes.fromhex(challange), key)
                    headers = {
                        "Auth-Challange": hmac_value,
                        "Auth-Username": "ASt",
                        "Auth-Session-id": session_id,
                    }
                    response = requests.request("GET", url, json={}, headers=headers)
                    print(response.status_code, response.content)
                    challange = response.headers["X-Challenge"]
            else:
                print("❌ M2 nicht gültig")
        else:
            print(f"❌ Fehler: {data['message']}")

if __name__ == "__main__":
    asyncio.run(srp_auth())
