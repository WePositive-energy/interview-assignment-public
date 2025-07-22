import logging
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from .models.base import BaseModel
from .settings import RuntimeSettings, Settings
from .types.hello_world import HelloWorldResponse


@lru_cache
def get_settings() -> Settings:
    # settings values are picked up automatically from .env or environment variables
    return Settings()  # pyright:ignore[reportCallIssue]


log = logging.getLogger(__name__)
settings = RuntimeSettings()
kwargs: dict[str, Any] = {}
if settings.fastapi_root_path is not None:  # pragma: no cover
    log.debug("Setting root_path to %s", settings.fastapi_root_path)
    kwargs["root_path"] = settings.fastapi_root_path

app = FastAPI(**kwargs)


async def get_session(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[AsyncSession, Any]:
    engine = create_async_engine(settings.sqlalchemy_db_uri, echo=False)
    async with AsyncSession(engine) as session:
        yield session
        await session.close()


@app.get("/")
async def root(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HelloWorldResponse:
    return HelloWorldResponse(message=f"Hello World {settings.sample_setting}")


@app.get("/db")
async def db_function(
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    pass


@app.post("/db")
async def post_db_function(
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    base = BaseModel(name="test")
    session.add(base)
    await session.flush()
    await session.refresh(base)

    return base


@app.get("/health")
async def health() -> Literal["OK"]:
    return "OK"
