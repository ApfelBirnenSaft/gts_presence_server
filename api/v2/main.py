from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import datetime

b = datetime.datetime.now(datetime.timezone.utc).isoformat()
print(b)
b = datetime.datetime.fromisoformat(b)
print(b.isoformat())
print(b.astimezone(datetime.timezone(datetime.timedelta(hours=2))))

router = APIRouter()

# In-memory user storage for demonstration purposes
users_db = {
    "test_user": {
        "salt": "random_salt",
        "verifier": "stored_verifier"  # Replace with actual verifier
    }
}

class DataRequest(BaseModel):
    start_date_iso: str
    end_date_iso: str
class DataResponse(BaseModel):
    username: str
    A: str  # Client's public value

@router.post("/get", response_model=DataResponse)
def get(auth_request: DataRequest):
    return DataResponse()