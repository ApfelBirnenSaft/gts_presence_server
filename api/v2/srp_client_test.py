import asyncio
import base64
import hashlib
from typing import Union, cast
import websockets
import json
import requests
from srptools import SRPClientSession, SRPContext, constants
from hashlib import sha256
import hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def calc_hmac(data: bytes, key: bytes) -> str:
    h = hmac.new(key, data, sha256)
    return h.hexdigest()

def verify_hmac(calculated_hmac:Union[str, bytes], expected_hmac: Union[str, bytes]) -> bool:
    return hmac.compare_digest(
        calculated_hmac.encode() if isinstance(calculated_hmac, str) else calculated_hmac,
        expected_hmac.encode() if isinstance(expected_hmac, str) else expected_hmac
    )

ENCODING = "UTF-8"

# Userdaten (müssen mit Serverdaten übereinstimmen!)
USERNAME = "ASt"
PASSWORD = "pass"

PRIME = constants.PRIME_2048
GEN = constants.PRIME_2048_GEN

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

async def srp_auth():
    uri = "http://192.168.2.102:3010/api/v2/"
    #uri = "ws://localhost:3012/api/v2/ws/"
        # Step 1: Init mit Username senden
    data = requests.post(
        uri + "auth/init",
        json={
            "username": USERNAME
        }
    ).json()

    # Antwort mit Salt und B empfangen
    print(json.dumps(data, indent=4))
    #assert data["type"] == "init"
    salt:str = data["salt"]
    server_public:str = data["server_public"]

    client_session = SRPClientSession(SRPContext(USERNAME, PASSWORD, prime=PRIME, generator=GEN, hash_func=constants.HASH_SHA_256))
    client_session.process(server_public, salt)
    client_public = client_session.public
    if isinstance(client_public, bytes): client_public = client_public.decode()
    client_session_key_proof  = client_session.key_proof
    if isinstance(client_session_key_proof, bytes): client_session_key_proof = client_session_key_proof.decode()

    # Step 2: Verify senden
    data = requests.post(
        uri + "auth/finalize",
        json={
            "session_token": data["session_token"],
            "client_public": client_public,
            "client_session_key_proof": client_session_key_proof 
        }
    ).json()

    print(json.dumps(data, indent=4))

    server_session_key_proof_hash = data.pop("server_session_key_proof_hash")
    if client_session.verify_proof(server_session_key_proof_hash.encode()):
        print("✅ Authentifizierung erfolgreich")
        key = client_session.key
        jwt_id_token = data["jwt_id_token"]
        if isinstance(key, bytes): key = key.decode()
        challange = data["challenge"]
        print(key)
        #return
        for i in range(2):
            hmac_value = calc_hmac(bytes.fromhex(challange), bytes.fromhex(cast(str, key)))
            headers = {
                "Auth-Challenge": hmac_value,
                "Auth-Id-Token": jwt_id_token,
            }
            print(headers)
            response = requests.get(uri + "get_data", params={
                "employee":1,
                "activity":3,
                "student_activity_presence":5,
                "student":2,
                "student_note":0,
                "student_absent_irregular":0,
                "student_absent_regular":0}, headers=headers)
            print(response.status_code)
            data = verify_and_decrypt(response.json(), cast(str, key))
            print(json.dumps(data))
            challange = response.headers["X-Challenge"]
    else:
        print("❌ M2 nicht gültig")

if __name__ == "__main__":
    asyncio.run(srp_auth())
    
    #challange = "d85577f7976aed5683993434b728cd9f"
    #key = "93672dd2434663c7f0935184008d3432df0ef605a745f0ffd085ffb9245088da"
    #print(list(bytes.fromhex(key)))
    #print(list(bytes.fromhex(challange)))
    #print(hmac.new(bytes.fromhex(key), bytes.fromhex(challange), sha256).hexdigest())
    #print(list(hmac.new(cast(str, key).encode(), bytes.fromhex(challange), sha256).digest()))
