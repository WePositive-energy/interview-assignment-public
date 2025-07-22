import asyncio
import logging
from functools import partial

import uvicorn
from pydantic import BaseModel
from typer import Typer

from interview_assignment.settings import RuntimeSettings, Settings
from interview_assignment.utils import setupLogging

from .utils import setupMotoServer

app = Typer()


class State(BaseModel):
    runtime_settings: RuntimeSettings
    settings: Settings


state: State


def run(reload: bool):
    runtime_settings = state.runtime_settings
    log = logging.getLogger(__name__)
    run = partial(
        uvicorn.run,
        "interview_assignment.main:app",
        host=runtime_settings.fastapi_host,
        port=runtime_settings.fastapi_port,
        reload=reload,
    )
    if runtime_settings.fastapi_proxy_headers:
        log.debug("Forwarding proxy headers")
        run = partial(run, proxy_headers=True)
    if runtime_settings.fastapi_forwarded_allow_ips is not None:
        log.debug(
            "Allowing forwarded requests from %s",
            runtime_settings.fastapi_forwarded_allow_ips,
        )
        run = partial(
            run, forwarded_allow_ips=runtime_settings.fastapi_forwarded_allow_ips
        )

    run()


@app.callback()
def main():
    """Serves the application in dev or prod mode."""
    global state
    runtime_settings = RuntimeSettings()
    settings = Settings()  # pyright:ignore[reportCallIssue]
    state = State(settings=settings, runtime_settings=runtime_settings)
    setupLogging(runtime_settings)
    asyncio.run(setupMotoServer(settings))


@app.command()
def dev():
    """Run in development mode, which auto reloads the application."""
    run(reload=True)


@app.command()
def prod():
    """Run in prod mode."""
    run(reload=False)
