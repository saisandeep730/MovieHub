from logging import getLogger

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.database import db_manager
from app.logging import setup_logging

logger = getLogger(__name__)

app = FastAPI(title="MovieHub Redirect Server", version="1.0.0")


@app.on_event("startup")
async def on_startup() -> None:
    setup_logging()
    logger.info("Redirect server starting up")
    await db_manager.startup()
    logger.info("Redirect server ready")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("Redirect server shutting down")
    await db_manager.shutdown()
    logger.info("Redirect server stopped")


@app.get("/health")
async def health() -> JSONResponse:
    db_ok = await db_manager.health_check()
    return JSONResponse(
        content={"status": "ok" if db_ok else "degraded", "database": "connected" if db_ok else "unreachable"}
    )
