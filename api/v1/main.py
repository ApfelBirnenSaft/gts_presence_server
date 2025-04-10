from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/")
def get():
    return HTTPException(410)