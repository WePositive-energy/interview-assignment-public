import logging

import pytest
from httpx import ASGITransport, AsyncClient
from moto.server import ThreadedMotoServer
from pydantic_settings import SettingsConfigDict

from interview_assignment.main import app, get_settings
from interview_assignment.settings import Settings


@pytest.fixture(name="log", scope="session")
def log_fixture() -> logging.Logger:
    log = logging.getLogger("unittests")
    log.setLevel(logging.DEBUG)
    return log


class TestSettings(Settings):
    model_config = SettingsConfigDict(env_file=[])


@pytest.fixture(name="settings", scope="session")
def settings_fixture() -> TestSettings:
    return TestSettings(
        sns_incoming_topic_arn="test_topic",
        sqs_command_queue_url="test_command_topic",
        aws_region="eu-west-1",
    )


@pytest.fixture
async def client(settings: TestSettings):
    app.dependency_overrides = {}
    app.dependency_overrides[get_settings] = lambda: settings
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


# Note: pick an appropriate fixture "scope" for your use case
@pytest.fixture(scope="module")
def moto_server():
    """Fixture to run a mocked AWS server for testing."""
    # Note: pass `port=0` to get a random free port.
    server = ThreadedMotoServer(port=0)
    server.start()
    host, port = server.get_host_and_port()
    yield f"http://{host}:{port}"
    server.stop()
