"""Interface to the Mbed Targets module.

mbed targets supports an online and offline mode, which instructs targets where to look up the target database.

The entry point to the API is the `get_targets` factory function, which accepts a DatabaseMode enum field as a
positional argument.

The returned object is an instance of MbedTargets, which is a Collection of mbed enabled targets.

A single target is represented by the MbedTarget immutable value object.

"""

import json

from collections.abc import Collection
from enum import Enum
from typing import Iterator, Tuple, Any

from mbed_targets._internal import target_database
from mbed_tools_lib.exceptions import ToolsError


class UnknownTarget(ToolsError):
    """Raised when a requested target was not found."""


class UnsupportedMode(ToolsError):
    """The Database Mode is unsupported."""


class MbedTarget:
    """Representation of an mbed target device."""

    def __init__(self, target_database_entry: dict):
        """Create a new instance of a target.

        Args:
            target_database_entry: A single entity retrieved from the target API.
        """
        self._target_entry: dict = target_database_entry
        self._attributes: dict = self._target_entry.get("attributes", {})
        self._features: dict = self._attributes.get("features", {})

    def __eq__(self, other: object) -> bool:
        """Targets with matching product_codes are equal."""
        if not isinstance(other, MbedTarget):
            return NotImplemented

        return self.product_code == other.product_code

    def __hash__(self) -> int:
        """Make object hashable for use in sets."""
        return hash(self.product_code)

    @property
    def board_type(self) -> str:
        """States type of the compilation target."""
        return self._attributes.get("board_type", "")

    @property
    def platform_name(self) -> str:
        """Human readable name."""
        return self._attributes.get("name", "")

    @property
    def mbed_os_support(self) -> Tuple[Any, ...]:
        """Mbed OS versions supported."""
        return tuple(self._features.get("mbed_os_support", ()))

    @property
    def mbed_enabled(self) -> Tuple[Any, ...]:
        """Enabled Mbed OS support."""
        return tuple(self._features.get("mbed_enabled", ()))

    @property
    def product_code(self) -> str:
        """Product code which uniquely identifies a platform for the online compiler."""
        return self._attributes.get("product_code", "")


class DatabaseMode(Enum):
    """Select the database mode."""

    OFFLINE = 0
    ONLINE = 1


class MbedTargets(Collection):
    """Interface to the Online Target Database."""

    _target_data: Any

    def __iter__(self) -> Iterator["MbedTarget"]:
        """Yield an MbedTarget on each iteration."""
        for target in self._target_data:
            yield MbedTarget(target)

    def __len__(self) -> int:
        """Return the length of the target data."""
        return len(self._target_data)

    def __contains__(self, item: object) -> Any:
        """Check if item is in the collection of targets.

        Args:
            item: An instance of MbedTarget.
        """
        if not isinstance(item, MbedTarget):
            return False

        return any(x == item for x in self)

    def get_target(self, product_code: str) -> "MbedTarget":
        """Look up an MbedTarget by its product code.

        Args:
            product_code: the product code.

        Raises:
            UnknownTarget: the given product code was not found in the target database.
        """
        try:
            return next(target for target in self if target.product_code == product_code)
        except StopIteration:
            raise UnknownTarget(f"Failed to find a target with a product code of '{product_code}'.")

    def json_dump(self) -> str:
        """Return the contents of the target database as a json string."""
        return json.dumps(list(self._target_data), indent=4)


class MbedTargetsOffline(MbedTargets):
    """Interface to the Offline Target Database."""

    def __init__(self) -> None:
        """Initialise with the offline target database."""
        self._target_data = target_database.get_offline_target_data()


class MbedTargetsOnline(MbedTargets):
    """Interface to the Online Target Database."""

    def __init__(self) -> None:
        """Initialise with the online target database."""
        self._target_data = target_database.get_online_target_data()


def get_targets(mode: DatabaseMode) -> MbedTargets:
    """Factory function returning the appropriate MbedTargets class for the given DatabaseMode.

    Args:
        mode: a DatabaseMode enum field.
    """
    if mode == DatabaseMode.OFFLINE:
        return MbedTargetsOffline()
    if mode == DatabaseMode.ONLINE:
        return MbedTargetsOnline()
    else:
        raise UnsupportedMode(f"{mode} is not a supported database mode.")
