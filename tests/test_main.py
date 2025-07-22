from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from pytest import MonkeyPatch
from pytest_mock import MockFixture
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from fastapi_microservice import main
from fastapi_microservice.models.base import BaseModel
from fastapi_microservice.settings import Settings


async def test_get_root(client: AsyncClient, settings: Settings):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": f"Hello World {settings.sample_setting}"}


async def test_get_settings(monkeypatch: MonkeyPatch):
    main.get_settings.cache_clear()
    monkeypatch.setenv("SAMPLE_SETTING", "-23")
    uri = "postgresql://test:test2@test3/test4"
    monkeypatch.setenv("SQLALCHEMY_DB_URI", uri)
    actual_settings = main.get_settings()
    assert isinstance(actual_settings, Settings)
    assert actual_settings.sample_setting == -23
    assert actual_settings.sqlalchemy_db_uri == uri


async def test_get_session(settings: Settings, mocker: MockFixture):
    """Test that the database session is started correctly on endpoints that need it."""

    main.app.dependency_overrides = {}
    main.app.dependency_overrides[main.get_settings] = lambda: settings
    mock_engine = AsyncMock()
    mock_create_engine = mocker.patch.object(
        main, "create_async_engine", return_value=mock_engine
    )
    mock_session_instance = AsyncMock()
    mock_session = AsyncMock(return_value=mock_session_instance)
    mock_session.__aenter__.return_value = mock_session_instance

    mock_async_session = mocker.patch.object(
        main, "AsyncSession", return_value=mock_session
    )
    async with AsyncClient(
        transport=ASGITransport(app=main.app), base_url="http://test"
    ) as client:
        await client.get("/db")
    mock_create_engine.assert_called_once_with(settings.sqlalchemy_db_uri, echo=False)
    mock_async_session.assert_called_once_with(mock_engine)
    mock_session_instance.close.assert_called_once_with()


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("test", [1, 2, 3, 4, 5, 6])
async def test_db_post(test: int, client: AsyncClient, session: AsyncSession):
    response = await client.post("/db")
    assert response.status_code == 200
    result = await session.exec(select(BaseModel))
    assert len(result.all()) == 1
    assert response.json()["name"] == "test"


@pytest.mark.asyncio(loop_scope="session")
async def test_health(
    client: AsyncClient,
):
    response = await client.get("http://server/health")

    assert response.status_code == 200
    assert response.json() == "OK"
