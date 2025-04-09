from typing import cast
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets

app = FastAPI()

# Fake-Datenbank (nur zur Demo)
fake_users_db = {
    "alice": {
        "username": "alice",
        "hashed_password": "$2a$12$AXe3rveQgofWKFWTZKXue.5AwWr7AypH5LIAUpaupCGyqmJPxdI1G",  # "secret"
        "role": "admin"
    },
    "bob": {
        "username": "bob",
        "hashed_password": "$2a$12$AXe3rveQgofWKFWTZKXue.5AwWr7AypH5LIAUpaupCGyqmJPxdI1G",  # "password"
        "role": "user"
    }
}
# ganz oben ergänzen:
refresh_token_store: dict[str, dict] = {}  # key: refresh_token


# Passwort-Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT-Konfiguration
SECRET_KEY = "geheimesjwtkey"  # später in .env!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Modelle
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

class User(BaseModel):
    username: str
    role: str

# Hilfsfunktionen
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    return fake_users_db.get(username)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return User(username=user["username"], role=user["role"])

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Auth-Abhängigkeit
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return User(username=username, role=role)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(role: str):
    def checker(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Insufficient rights")
        return user
    return checker

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

@app.post("/token", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = secrets.token_urlsafe(64)
    refresh_token_store[refresh_token] = {
        "username": user.username,
        "role": user.role,
        "expires_at": datetime.now() + timedelta(days=30)
    }

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/refresh", response_model=Token)
def refresh_token(req: RefreshRequest):
    data = refresh_token_store.get(req.refresh_token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if data["expires_at"] < datetime.utcnow():
        del refresh_token_store[req.refresh_token]
        raise HTTPException(status_code=401, detail="Refresh token expired")

    access_token = create_access_token(
        data={"sub": data["username"], "role": data["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
def logout(req: LogoutRequest):
    if req.refresh_token in refresh_token_store:
        del refresh_token_store[req.refresh_token]
    return {"message": "Logged out"}

# Beispiel-Endpunkte
@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/admin")
def read_admin(user: User = Depends(require_role("admin"))):
    return {"message": f"Welcome admin {user.username}!"}
