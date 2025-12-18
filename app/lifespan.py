from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from app.infrastructure.database.engine import engine
from app.shared.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup
    setup_logging()
    logger.info("Application startup initiated")
    logger.info(f"App: {app.title} v{app.version}")
    logger.info("Database engine initialized")

    yield

    # Shutdown
    logger.info("Application shutdown initiated")
    await engine.dispose()
    logger.info("Database connections closed")
    logger.info("Application shutdown complete")
