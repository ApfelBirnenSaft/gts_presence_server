from contextlib import asynccontextmanager
from typing import Any, Literal
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn.logging

from api.v1.main import router as api_v1_router, start_up as api_v1_startup
from api.v2.main import router as api_v2_router, start_up as api_v2_startup
from api.database import create_all_tables

import Secrets

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    api_v1_startup()
    api_v2_startup()
    yield
    print("shutdown")

app = FastAPI(lifespan=lifespan, version="2.0.0")

app.include_router(api_v1_router, prefix="/api/v1", deprecated=True)
app.include_router(api_v2_router, prefix="/api/v2")

flutter_build_dir = "WebApp"

app.mount("/", StaticFiles(directory=flutter_build_dir, html=True), name="flutter")

if __name__ == "__main__":
    protocol:Literal["h1", "h2", "h3"] = "h1"
    if protocol == "h1":
        import uvicorn
        uvicorn.run("server:app", host=Secrets.server_host, port=Secrets.server_port, reload=True, log_level="debug", use_colors=True)
    else:
        import hypercorn
        import hypercorn.asyncio
        from hypercorn.config import Config
        config = Config()
        config.certfile = "cert.pem"
        config.keyfile = "key.pem"
        config.use_reloader = True
        if protocol == "h2":
            config.bind = [f"{Secrets.server_host}:{Secrets.server_port}"]
        else:
            config.quic_bind = [f"{Secrets.server_host}:{Secrets.server_port}"]
        
        import asyncio
        asyncio.run(hypercorn.asyncio.serve(app, config))
