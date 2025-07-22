import logging
from functools import partial

import uvicorn
from pydantic import BaseModel
from typer import Typer

from fastapi_microservice.settings import RuntimeSettings

from .utils import setupLogging

app = Typer()


class State(BaseModel):
    settings: RuntimeSettings


state: State


def run(reload: bool):
    settings = state.settings
    log = logging.getLogger(__name__)
    run = partial(
        uvicorn.run,
        "fastapi_microservice.main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=reload,
    )
    if settings.fastapi_proxy_headers:
        log.debug("Forwarding proxy headers")
        run = partial(run, proxy_headers=True)
    if settings.fastapi_forwarded_allow_ips is not None:
        log.debug(
            "Allowing forwarded requests from %s", settings.fastapi_forwarded_allow_ips
        )
        run = partial(run, forwarded_allow_ips=settings.fastapi_forwarded_allow_ips)

    run()


@app.callback()
def main():
    """Serves the application in dev or prod mode."""
    global state
    settings = RuntimeSettings()
    state = State(settings=settings)
    setupLogging(settings)


@app.command()
def dev():
    """Run in development mode, which auto reloads the application."""
    run(reload=True)


@app.command()
def prod():
    """Run in prod mode."""
    run(reload=False)
