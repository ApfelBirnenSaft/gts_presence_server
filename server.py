from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.v1.main import router as api_v1_router
import os

app = FastAPI()

# API-Routen mounten
app.include_router(api_v1_router, prefix="/api/v1")

flutter_build_dir = "WebApp"

# Statische Dateien aus dem Root des Build-Verzeichnisses
app.mount("/", StaticFiles(directory=flutter_build_dir, html=True), name="flutter")

# Optional: Wenn du willst, dass "/" explizit index.html liefert (nicht nötig wenn `html=True`)
@app.get("/")
def index():
    return FileResponse(os.path.join(flutter_build_dir, "index.html"))