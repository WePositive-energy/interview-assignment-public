from interview_assignment.settings import Settings, get_session


async def setupMotoServer(settings: Settings):
    session = get_session()
    queue_name = settings.sqs_command_queue_url.split("/")[-1]
    async with session.client(  # type:ignore
        "sqs", region_name=settings.aws_region, endpoint_url=settings.aws_endpoint_url
    ) as client:
        await client.create_queue(QueueName=queue_name)
    topic_name = settings.sns_incoming_topic_arn.split(":")[-1]
    async with session.client(  # type:ignore
        "sns", region_name=settings.aws_region, endpoint_url=settings.aws_endpoint_url
    ) as client:
        await client.create_topic(Name=topic_name)
