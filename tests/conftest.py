import logging
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from fastapi_microservice.main import app, get_session, get_settings
from fastapi_microservice.settings import EnvironmentEnum, Settings


@pytest.fixture(name="log", scope="session")
def log_fixture() -> logging.Logger:
    log = logging.getLogger("unittests")
    log.setLevel(logging.DEBUG)
    return log


class TestSettings(Settings):
    model_config = SettingsConfigDict(env_file=[])


@pytest.fixture(name="settings", scope="session")
def settings_fixture() -> TestSettings:
    orig_settings = Settings()  # pyright:ignore[reportCallIssue]
    return TestSettings(
        sample_setting=10,
        sqlalchemy_db_uri=orig_settings.sqlalchemy_db_uri,
    )


@pytest.fixture
async def client(settings: TestSettings, session: AsyncGenerator[AsyncSession, Any]):
    app.dependency_overrides = {}
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_session] = lambda: session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


async def create_database(engine: AsyncEngine, database: str, log: logging.Logger):
    conn = await engine.connect()
    conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
    try:
        await conn.execute(text(f"DROP DATABASE {database}"))
    except DBAPIError as error:
        if (
            error.orig is not None
            and hasattr(error.orig, "pgcode")
            and isinstance(
                error.orig.pgcode,  # pyright:ignore[reportUnknownMemberType,reportAttributeAccessIssue]
                str,
            )
            and error.orig.pgcode.startswith(  # pyright:ignore[reportUnknownMemberType,reportAttributeAccessIssue]
                "3D"
            )
        ):
            # database doesn't exist.
            log.info("Test database does not exist")
        else:
            await conn.close()
            raise
    log.debug("Creating database %s", database)
    await conn.execute(text(f"CREATE DATABASE {database}"))
    await conn.commit()
    await conn.close()


def get_test_database_uri(
    sqlalchemy_db_uri: URL, request: pytest.FixtureRequest
) -> URL:
    new_sqlalchemy_db_uri = sqlalchemy_db_uri.set(
        database=f"{sqlalchemy_db_uri.database}_test"
    )
    xdist_suffix = getattr(request.config, "slaveinput", {}).get("slaveid")
    if xdist_suffix is not None:
        new_sqlalchemy_db_uri = new_sqlalchemy_db_uri.set(
            database=f"{new_sqlalchemy_db_uri.database}_{xdist_suffix}"
        )
    return new_sqlalchemy_db_uri


@pytest.fixture(scope="session", name="engine")
async def engine_fixture(
    settings: Settings, request: pytest.FixtureRequest, log: logging.Logger
) -> AsyncGenerator[AsyncEngine, Any]:
    sqlalchemy_db_uri = make_url(settings.sqlalchemy_db_uri)
    assert sqlalchemy_db_uri.host in {
        "localhost",
        "127.0.0.1",
    }, "Use on localhost only."
    if settings.environment != EnvironmentEnum.CI:
        new_sqlalchemy_db_uri = get_test_database_uri(sqlalchemy_db_uri, request)
        settings.sqlalchemy_db_uri = new_sqlalchemy_db_uri.render_as_string(False)
    else:
        new_sqlalchemy_db_uri = sqlalchemy_db_uri
    assert new_sqlalchemy_db_uri.database is not None
    if settings.environment != EnvironmentEnum.CI:
        engine = create_async_engine(
            sqlalchemy_db_uri.set(database="postgres"), echo=True
        )
        await create_database(engine, new_sqlalchemy_db_uri.database, log)
        await engine.dispose()
    new_engine = create_async_engine(
        new_sqlalchemy_db_uri,
        # poolclass=NullPool,
        echo=True,
    )
    async with new_engine.begin() as conn:
        # TODO do this with alembic migrations instead
        await conn.run_sync(SQLModel.metadata.create_all)
    yield new_engine
    log.debug("Disposing of engine")
    await new_engine.dispose()


@pytest.fixture
async def session(
    engine: AsyncEngine, log: logging.Logger
) -> AsyncGenerator[AsyncSession, Any]:
    log.debug("Connecting to database %s", engine)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin() as transaction:
            async with session.begin_nested():
                log.debug("Giving session")
                yield session
            log.debug("Rolling back session")
            await transaction.rollback()
        log.debug("Closing session")
        await session.close()
