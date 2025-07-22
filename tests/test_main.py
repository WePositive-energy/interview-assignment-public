import pytest
from httpx import AsyncClient
from pytest import MonkeyPatch

from interview_assignment import main
from interview_assignment.settings import EnvironmentEnum, Settings


async def test_get_settings(monkeypatch: MonkeyPatch):
    main.get_settings.cache_clear()
    monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
    monkeypatch.setenv("sqs_command_queue_url", "test_queue_url")
    monkeypatch.setenv("sns_incoming_topic_arn", "test_topic")
    monkeypatch.setenv("aws_region", "test_region")
    actual_settings = main.get_settings()
    assert isinstance(actual_settings, Settings)
    assert actual_settings.environment == EnvironmentEnum.PRODUCTION
    assert actual_settings.sqs_command_queue_url == "test_queue_url"
    assert actual_settings.sns_incoming_topic_arn == "test_topic"
    assert actual_settings.aws_region == "test_region"


async def test_get_root(client: AsyncClient, settings: Settings):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": f"Hello World {settings.environment}"}


@pytest.mark.asyncio(loop_scope="session")
async def test_health(
    client: AsyncClient,
):
    response = await client.get("http://server/health")

    assert response.status_code == 200
    assert response.json() == "OK"
