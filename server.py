from contextlib import asynccontextmanager
from typing import Literal
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.v1.main import router as api_v1_router, start_up as api_v1_startup
from api.v2.main import router as api_v2_router, start_up as api_v2_startup
from api.database import create_all_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    api_v1_startup()
    api_v2_startup()
    yield
    print("shutdown")

app = FastAPI(lifespan=lifespan, debug=True)

app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(api_v2_router, prefix="/api/v2")

flutter_build_dir = "WebApp"

app.mount("/", StaticFiles(directory=flutter_build_dir, html=True), name="flutter")

if __name__ == "__main__":
    protocol:Literal["h1", "h2", "h3"] = "h1"
    if protocol == "h1":
        import uvicorn
        uvicorn.run("server:app", host="localhost", port=80, reload=True, log_level="info")
    else:
        import hypercorn
        import hypercorn.asyncio
        from hypercorn.config import Config
        config = Config()
        config.certfile = "cert.pem"
        config.keyfile = "key.pem"
        config.use_reloader = True
        if protocol == "h2":
            config.bind = ["0.0.0.0:8000"]
        else:
            config.quic_bind = ["0.0.0.0:8000"]
        
        import asyncio
        asyncio.run(hypercorn.asyncio.serve(app, config))
