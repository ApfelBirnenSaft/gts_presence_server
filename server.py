import sys, subprocess
print(sys.executable)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.v1.main import router as api_v1_router
from api.v2.main import router as api_v2_router
import os

from api.database import create_db_and_tables

app = FastAPI()

# API-Routen mounten
app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(api_v2_router, prefix="/api/v2")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

flutter_build_dir = "WebApp"

# Statische Dateien aus dem Root des Build-Verzeichnisses
app.mount("/", StaticFiles(directory=flutter_build_dir, html=True), name="flutter")

# Optional: Wenn du willst, dass "/" explizit index.html liefert (nicht nötig wenn `html=True`)
@app.get("/")
def index():
    return FileResponse(os.path.join(flutter_build_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", reload=True)