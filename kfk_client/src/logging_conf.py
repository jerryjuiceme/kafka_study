import logging
from logging.config import dictConfig

from src.config import settings


def configure_logging(level=settings.logging.log_level):
    logging.basicConfig(
        level=level,
        datefmt=settings.logging.datefmt,
        format=settings.logging.log_format,
    )
