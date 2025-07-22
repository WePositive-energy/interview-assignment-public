from enum import Enum
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentEnum(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    CI = "CI"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=[".env", ".env.docker"], extra="ignore")
    sample_setting: int
    sqlalchemy_db_uri: str
    environment: EnvironmentEnum = EnvironmentEnum.DEVELOPMENT


class RuntimeSettings(BaseSettings):
    fastapi_port: int = 8000
    fastapi_host: str = "127.0.0.1"
    fastapi_root_path: str | None = None
    fastapi_proxy_headers: bool = False
    fastapi_forwarded_allow_ips: str | None = None
    log_level: Literal["DEBUG", "INFO", "ERROR"] = "INFO"
