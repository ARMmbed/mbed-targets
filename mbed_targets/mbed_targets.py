"""Interface to the Mbed Targets module."""

import logging
from typing import List

from mbed_targets._internal import target_database

logger = logging.getLogger(__name__)


class MbedTarget:
    """Container and renderer for Mbed OS build results."""

    def __init__(self, target_database_entry: dict):
        """Create a new instance of a target.

        Args:
            target_database_entry: A single entity retrieved from the target API.
        """
        self._target_entry = target_database_entry
        self._attributes = self._target_entry.get("attributes", {})
        self._features = self._attributes.get("features", {})

    @property
    def board_type(self) -> str:
        """States type of the compilation target."""
        return self._attributes.get("board_type", "")

    @property
    def platform_name(self) -> str:
        """Human readable name."""
        return self._attributes.get("name", "")

    @property
    def mbed_os_support(self) -> List[str]:
        """List of Mbed OS versions supported."""
        return self._features.get("mbed_os_support", [])

    @property
    def mbed_enabled(self) -> List[str]:
        """List of enabled Mbed OS support."""
        return self._features.get("mbed_enabled", [])

    @property
    def product_code(self) -> str:
        """Product code which uniquely identifies a platform for the online compiler."""
        return self._attributes.get("product_code", "")


class MbedTargets:
    """Interface to the Online Target Database."""

    def __init__(self):
        """Retrieve target data from the online database."""
        self._target_data = target_database.get_target_data()

    def __iter__(self) -> 'MbedTargets':
        """Return the iterator object itself."""
        # Create a new iterator
        self._target_iterator = iter(self._target_data)
        return self

    def __next__(self) -> MbedTarget:
        """Return the next item from the container.

        Returns:
            An instance of a Mbed target database entry.
        """
        # Iterate over the target data and return a new MbedTarget instance for each database entry
        return MbedTarget(next(self._target_iterator))
