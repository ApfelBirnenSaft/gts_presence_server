from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
def get(path):
    return HTTPException(410, detail="Gone\nThe API v1 has been shutdown")