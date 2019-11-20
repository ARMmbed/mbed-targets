"""Interface for the ."""

import logging

from mbed_targets._internal import target_database

logger = logging.getLogger(__name__)


class MbedTarget:
    """Container and renderer for Mbed OS build results."""

    def __init__(self, target_database_entry):
        """Create a new instance of a target.
        :param dict target_database_entry: A single entity retrieved from the target API.
        """
        self._target_entry = target_database_entry
        self._attributes = self._target_entry.get("attributes", {})
        self._features = self._attributes.get("features", {})

    @property
    def board_type(self):
        """Compilation target.
        :rtype: str
        """
        return self._attributes.get("board_type", "")

    @property
    def platform_name(self):
        """Human readable name.
        :rtype: str
        """
        return self._attributes.get("name", "")

    @property
    def mbed_os_support(self):
        """List of Mbed OS versions supported.
        :rtype: list
        """
        return self._features.get("mbed_os_support", [])

    @property
    def mbed_enabled(self):
        """List of enabled Mbed OS support.
        :rtype: list
        """
        return self._features.get("mbed_enabled", [])

    @property
    def product_code(self):
        """Product code which uniquely identifies a platform for the online compiler.
        :rtype: str
        """
        return self._attributes.get("product_code", "")


class MbedTargets:
    """Interface to the Online Target Database."""

    def __init__(self):
        """Retrieve target data from the online database."""
        self._target_data = target_database.get_target_data()

    def __iter__(self):
        """Return the iterator object itself."""
        # Create a new iterator
        self._target_iterator = iter(self._target_data)
        return self

    def __next__(self):
        """Return the next item from the container.
        :return: An instance of a Mbed target database entry.
        :rtype: MbedTarget
        """
        # Iterate over the target data and return a new MbedTarget instance for each database entry
        return MbedTarget(next(self._target_iterator))
