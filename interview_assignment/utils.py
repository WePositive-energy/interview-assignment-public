import logging
import sys

from interview_assignment.settings import RuntimeSettings


def setupLogging(settings: RuntimeSettings):  # pragma: no cover
    """Setup application loggin"""
    format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    logging.basicConfig(stream=sys.stdout, level=settings.log_level, format=format)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("aiobotocore").setLevel(logging.WARNING)
