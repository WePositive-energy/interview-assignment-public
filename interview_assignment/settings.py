from enum import StrEnum
from functools import lru_cache
from typing import Literal

from aioboto3 import Session
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentEnum(StrEnum):
    DEVELOPMENT = "DEVELOPMENT"
    CI = "CI"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=[".env", ".env.docker"], extra="ignore")
    environment: EnvironmentEnum = EnvironmentEnum.DEVELOPMENT
    sns_incoming_topic_arn: str
    sqs_command_queue_url: str
    aws_region: str
    aws_endpoint_url: str | None = "http://localhost:3000"


class RuntimeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=[".env", ".env.docker"], extra="ignore")
    fastapi_port: int = 8000
    fastapi_host: str = "127.0.0.1"
    fastapi_root_path: str | None = None
    fastapi_proxy_headers: bool = False
    fastapi_forwarded_allow_ips: str | None = None
    log_level: Literal["DEBUG", "INFO", "ERROR"] = "INFO"


@lru_cache
def get_settings() -> Settings:
    # settings values are picked up automatically from .env or environment variables
    return Settings()  # pyright:ignore[reportCallIssue]


@lru_cache
def get_session() -> Session:  # pragma: no cover
    return Session()
