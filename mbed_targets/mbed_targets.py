"""Interface for the ."""

import logging

from mbed_targets._internal import target_database

logger = logging.getLogger(__name__)


class MbedTargets:
    """Container and renderer for Mbed OS build results."""

    def __init__(self):
        self._target_db = target_database.TargetDatabase()
