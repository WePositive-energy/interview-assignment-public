import asyncio
import json
import logging
from typing import TYPE_CHECKING

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
def main():
    settings = get_settings()
    runtime_settings = RuntimeSettings()
    setupLogging(runtime_settings)
    asyncio.run(monitor_sns_topic(settings))


async def monitor_sns_topic(settings: Settings):
    logger = logging.getLogger(__name__)
    logger.info("Subscribing to sns messages")
    session = get_session()
    topic_arn = settings.sns_incoming_topic_arn
    queue_name = "temp_sns_monitoring_topic"
    async with session.client(  # type:ignore
        "sqs", region_name=settings.aws_region, endpoint_url=settings.aws_endpoint_url
    ) as client:
        response = await client.create_queue(QueueName=queue_name)
        queue_url = response["QueueUrl"]
        queue_attributes = await client.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["QueueArn"]
        )
        queue_arn = queue_attributes["Attributes"]["QueueArn"]

    async with session.client(  # type:ignore
        "sns", region_name=settings.aws_region, endpoint_url=settings.aws_endpoint_url
    ) as client:
        response = await client.subscribe(
            TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn
        )
        subscription_arn = response["SubscriptionArn"]

    async with session.client(  # type:ignore
        "sqs", region_name=settings.aws_region, endpoint_url=settings.aws_endpoint_url
    ) as client:
        try:
            while True:
                response = await client.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20,
                )

                # Process messages
                messages = response.get("Messages", [])
                for message in messages:
                    try:
                        if TYPE_CHECKING:
                            assert "Body" in message
                        try:
                            message["Body"] = json.loads(message["Body"])
                        except json.JSONDecodeError:
                            continue
                        logger.info(
                            "Received message\n%s", json.dumps(message, indent=4)
                        )
                    finally:
                        if TYPE_CHECKING:
                            assert "ReceiptHandle" in message
                        # Delete message after processing (to avoid redelivery)
                        await client.delete_message(
                            QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"]
                        )
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            logger.info("Unsubscribing from sns messages")
            async with session.client(  # type:ignore
                "sns",
                region_name=settings.aws_region,
                endpoint_url=settings.aws_endpoint_url,
            ) as client:
                await client.unsubscribe(SubscriptionArn=subscription_arn)


if __name__ == "__main__":
    app()
