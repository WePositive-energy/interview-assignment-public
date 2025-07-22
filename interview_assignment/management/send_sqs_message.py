import asyncio
import logging
from typing import Annotated

import typer

from interview_assignment.settings import (
    RuntimeSettings,
    Settings,
    get_session,
    get_settings,
)
from interview_assignment.utils import setupLogging

app = typer.Typer()


@app.command()
def main(payload: Annotated[str, typer.Argument()]):
    settings = get_settings()
    runtime_settings = RuntimeSettings()
    setupLogging(runtime_settings)
    asyncio.run(send_sqs_message(settings, payload))


async def send_sqs_message(settings: Settings, payload: str):
    logger = logging.getLogger(__name__)
    logger.info(f"Sending sqs message with payload {payload}")
    session = get_session()
    async with session.client(  # type:ignore
        "sqs", region_name=settings.aws_region, endpoint_url=settings.aws_endpoint_url
    ) as client:
        await client.send_message(
            QueueUrl=settings.sqs_command_queue_url, MessageBody=payload
        )
        logger.info("Sent message successfully")


if __name__ == "__main__":
    app()
