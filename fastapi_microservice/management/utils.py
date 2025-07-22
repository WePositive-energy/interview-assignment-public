import logging
import sys

from fastapi_microservice.settings import RuntimeSettings


def setupLogging(settings: RuntimeSettings):
    """Setup application loggin"""
    format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    logging.basicConfig(stream=sys.stdout, level=settings.log_level, format=format)
