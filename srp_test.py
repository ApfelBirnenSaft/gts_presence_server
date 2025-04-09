from srptools import SRPContext, SRPServerSession, SRPClientSession, constants
import os

# -------- Registrierung (Client) --------

# Benutzername + Passwort
username = 'alice'
password = 'geheim123'

# Salt zufällig erzeugen (32 Byte empfohlen)
salt = os.urandom(16)

# SRP-Kontext (N, g, Hash)
ctx = SRPContext(username, password, salt)

# Verifier berechnen
verifier = ctx.verifier

# Das wird auf dem Server gespeichert:
server_db = {
    'alice': {
        'salt': salt,
        'verifier': verifier,
    }
}

print("📝 Registrierung abgeschlossen.")
print("Salt:", salt.hex())
print("Verifier:", verifier.hex())

# -------- Login (Client initiiert) --------

# Client erzeugt a & A
client = SRPClientSession(username, password, salt)
A = client.public

# Server erhält A und antwortet mit B und Salt
user_data = server_db['alice']
server = SRPServerSession(user_data['verifier'], A)
B = server.public

# Client erhält B, berechnet shared key
client.process_challenge(B)
client_proof = client.key_proof  # M1

# Server prüft den Client
server.verify_proof(client_proof)

# Server gibt eigenen Proof zurück
server_proof = server.key_proof  # M2

# Client prüft den Server
client.verify_proof(server_proof)

# Beide haben denselben geheimen Schlüssel K
print("🔐 Login erfolgreich!")
print("Client-Session-Key:", client.key.hex())
print("Server-Session-Key:", server.key.hex())
