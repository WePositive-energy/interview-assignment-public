# ruff: noqa: T201
from datetime import datetime, timedelta
from datetime import timezone as tz
from enum import StrEnum
from typing import Annotated

import boto3
from mypy_boto3_logs.type_defs import FilteredLogEventTypeDef
from pydantic import BaseModel
from typer import Argument, Option, Typer


class State(BaseModel):
    aws_profile: str


app = Typer()

state: State


class LaunchTypeEnum(StrEnum):
    EC2 = "EC2"
    FARGATE = "FARGATE"
    EXTERNAL = "EXTERNAL"


class Fields(StrEnum):
    timestamp = "timestamp"
    stream_name = "stream_name"
    message = "message"


def format_log(event: FilteredLogEventTypeDef, fields: list[Fields]) -> str:
    data: dict[str, str] = {}
    data["timestamp"] = (
        datetime.fromtimestamp(event.get("timestamp", 0) / 1000, tz.utc)
        .astimezone()
        .strftime("%Y-%m-%d %H:%M:%S %Z")
    )
    data["stream_name"] = event.get("logStreamName", "")
    data["message"] = event.get("message", "")
    return " - ".join([data[field] for field in fields])


@app.command()
def logs(
    end_datetime: Annotated[
        datetime, Option(help="End datetime in your current timezone.")
    ] = datetime.now(tz.utc),
    fields: list[Fields] = [Fields.timestamp, Fields.stream_name, Fields.message],
    duration: Annotated[
        int,
        Option(
            help="Duration in minutes showing logs for, counting backwards from end_datetime."
        ),
    ] = 60,
    limit: Annotated[int, Option(help="Maximum number of messages to show.")] = 100,
    log_group: Annotated[
        str, Option(help="Log group name to show messages for.")
    ] = "fastapi-microservice-template/dev",
):
    """Show logs from aws cloud watch"""
    session = boto3.session.Session(profile_name=state.aws_profile)
    client = session.client("logs")
    end_time = int(end_datetime.timestamp() * 1000)
    start_time = int((end_datetime - timedelta(minutes=duration)).timestamp() * 1000)
    try:
        response = client.filter_log_events(
            logGroupName=log_group,
            startTime=start_time,
            endTime=end_time,
            limit=limit,
        )
    except client.exceptions.InvalidParameterException as e:
        print("Invalid parameter")
        print(str(e))
        return

    logs = response["events"]
    while "nextToken" in response:
        response = client.filter_log_events(
            logGroupName=log_group,
            startTime=start_time,
            endTime=end_time,
            nextToken=response["nextToken"],
            limit=limit,
        )
        logs += response["events"]
    if len(logs) == 0:
        print("No results")
        return
    print("\n".join([format_log(event, fields) for event in logs]))


@app.command()
def run_command(
    command: Annotated[
        list[str],
        Argument(
            help="The command to run in the container. You don't need to add `poetry run` but can directly run any poetry command."
        ),
    ],
    cluster: Annotated[str, Option(help="ECS cluster name")] = "main",
    launch_type: Annotated[
        LaunchTypeEnum, Option(help="Task launch type")
    ] = LaunchTypeEnum.EC2,
    task_definition: Annotated[
        str, Option(help="Task definition name")
    ] = "fastapi-microservice-template",
):
    """
    Run a (poetry) command in an AWS ECS task.

    Examples:

        * `poetry run aws run-command alembic upgrade head`

        * `poetry run aws run-command db create-admin firstname lastname e@mail.com password`
    """
    session = boto3.session.Session(profile_name=state.aws_profile)
    client = session.client("ecs")
    client.run_task(
        taskDefinition=task_definition,
        count=1,
        cluster=cluster,
        launchType=launch_type.value,
        overrides={
            "containerOverrides": [
                {"name": "fastapi-microservice-template", "command": command}
            ]
        },
    )


@app.callback()
def main(
    aws_profile: Annotated[
        str, Option(help="The aws profile to use.")
    ] = "wepositive_software_publish",
):
    """AWS convenience functions."""
    global state
    state = State(aws_profile=aws_profile)


if __name__ == "__main__":
    app()
