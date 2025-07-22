import logging
from contextlib import asynccontextmanager
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI

from .settings import RuntimeSettings, Settings, get_settings
from .types.hello_world import HelloWorldResponse
from .utils import setupLogging
from .websockets import websocket_router

runtime_settings = RuntimeSettings()
kwargs: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    setupLogging(runtime_settings)
    logger = logging.getLogger(__name__)
    logger.info("Starting application...")

    try:
        yield  # Application runs here
    finally:
        logger.info("Shutting down application...")


app = FastAPI(**kwargs, lifespan=lifespan)
app.include_router(websocket_router)


@app.get("/")
async def root(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HelloWorldResponse:
    return HelloWorldResponse(message=f"Hello World {settings.environment}")


@app.get("/health")
async def health() -> Literal["OK"]:
    return "OK"
