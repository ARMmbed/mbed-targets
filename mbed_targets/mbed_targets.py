"""Interface to the Mbed Targets module."""

from typing import List, Iterator

from mbed_targets._internal import target_database
from mbed_tools_lib.exceptions import ToolsError


class UnknownTarget(ToolsError):
    """Raised when a requested target was not found."""


class MbedTarget:
    """Container and renderer for Mbed OS build results."""

    def __init__(self, target_database_entry: dict):
        """Create a new instance of a target.

        Args:
            target_database_entry: A single entity retrieved from the target API.
        """
        self._target_entry: dict = target_database_entry
        self._attributes: dict = self._target_entry.get("attributes", {})
        self._features: dict = self._attributes.get("features", {})

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

    def __init__(self) -> None:
        """Retrieve target data from the online database.

        Raises:
            TargetDatabaseError: Failed to get the target data.
        """
        self._target_data: List[dict] = target_database.get_target_data()

    def __iter__(self) -> Iterator["MbedTarget"]:
        """Yield an MbedTarget on each iteration."""
        for target in self._target_data:
            yield MbedTarget(target)

    def get_target(self, product_code: str) -> "MbedTarget":
        """Look up an MbedTarget by its product code.

        Args:
            product_code: the product code.

        Raises:
            UnknownTarget: the given product code was not found in the target database.
        """
        try:
            return next(
                target for target in self if target.product_code == product_code
            )
        except StopIteration:
            raise UnknownTarget(
                f"Failed to find a target with a product code of '{product_code}'."
            )
