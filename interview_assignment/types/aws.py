from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ClientMessage(BaseModel):
    """
    Message sent from a WebSocket client to the server and forwarded to an sns topic.
    """

    action: str
    payload: dict[str, Any] = Field(default_factory=dict)


class Command(BaseModel):
    """
    Command received over (via SQS/SNS) and sent to the relevant WebSocket client.
    """

    client_id: str
    command: str
    data: dict[str, Any] = Field(default_factory=dict)


class SNSMessage(BaseModel):
    """
    Minimal wrapper for SNS messages delivered via SQS.
    We only care about the 'Message' field here (the actual Command).
    All other fields normally present on SNS messages arriving over SQS are
    being ignored here.
    """

    model_config = ConfigDict(extra="ignore")

    Message: str

    def parse_inner_message(self) -> Command:
        """
        Parses the JSON inside the SNS 'Message' field.
        """
        return Command.model_validate_json(self.Message)
