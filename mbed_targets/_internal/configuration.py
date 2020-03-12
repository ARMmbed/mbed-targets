"""Configuration variables loaded from environment.

Settings from .env file take precedence over environment variables.
"""
import os
import dotenv
from enum import Enum
import logging

logger = logging.getLogger(__name__)


dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True), override=True)


MBED_API_AUTH_TOKEN = os.getenv("MBED_API_AUTH_TOKEN")


class DatabaseMode(Enum):
    """Selected database mode."""

    OFFLINE = 0
    ONLINE = 1
    AUTO = 2


try:
    value = os.getenv("MBED_DATABASE_MODE", "AUTO")
    MBED_DATABASE_MODE = DatabaseMode[value]
except KeyError:
    logger.warning(f"Invalid `MBED_DATABASE_MODE` env variable value '{value}'. Defaulting to 'AUTO'.")
    MBED_DATABASE_MODE = DatabaseMode.AUTO
