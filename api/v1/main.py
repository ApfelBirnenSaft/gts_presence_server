from fastapi import APIRouter, HTTPException

router = APIRouter()

def start_up():
    pass

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
def get(path):
    raise HTTPException(410, detail="Gone\nThe API v1 has been shutdown")