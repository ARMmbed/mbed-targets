"""Interface to the Mbed Targets module.

mbed targets supports an online and offline mode, which instructs targets where to look up the target database.

The entry points to the API are:
- `get_target_by_product_code` function, which looks up an MbedTarget from its product code
- `get_target_by_online_id` function, which looks up an MbedTarget by its slug and type
The lookup can be from either the online or offline database, depending on the given mode.
The mode can be one of the following DatabaseMode enum fields:
    AUTO: the offline database is searched first, if the target isn't found the online database is searched.
    ONLINE: the online database is always used.
    OFFLINE: the offline database is always used.
"""
import functools
import json
import logging

from collections.abc import Set
from enum import Enum
from typing import Iterator, Iterable, Tuple, Any, Dict, Union, cast

from mbed_targets._internal import target_database
from mbed_tools_lib.exceptions import ToolsError


logger = logging.getLogger(__name__)


TargetDatabaseQueryValue = Union[str, Tuple]
TargetDatabaseQuery = Dict[str, TargetDatabaseQueryValue]


@functools.total_ordering
class MbedTarget:
    """Representation of an Mbed Target."""

    def __init__(self, target_database_entry: dict):
        """Create a new instance of a target.

        Args:
            target_database_entry: A single entity retrieved from the target API.
        """
        self._target_entry: dict = target_database_entry
        self._attributes: dict = self._target_entry.get("attributes", {})
        self._features: dict = self._attributes.get("features", {})

    def __eq__(self, other: object) -> bool:
        """Targets with matching product_codes, board_types and platform_names are equal."""
        if not isinstance(other, self.__class__):
            return NotImplemented

        return (self.product_code, self.board_type, self.board_name, self.slug) == (
            other.product_code,
            other.board_type,
            other.board_name,
            other.slug,
        )

    def __hash__(self) -> int:
        """Make object hashable."""
        return hash(self.product_code) ^ hash(self.board_type) ^ hash(self.board_name) ^ hash(self.slug)

    def __repr__(self) -> str:
        """Return object repr."""
        state = ", ".join(f"{i}={v}" for i, v in self._attributes.items() if i != "features")
        return f"{self.__class__.__name__}({state})"

    def __lt__(self, other: object) -> bool:
        """Compare less than another instance with a greater product_code."""
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.product_code < other.product_code

    @property
    def board_type(self) -> str:
        """States board type of the Mbed Target."""
        return self._attributes.get("board_type", "")

    @property
    def board_name(self) -> str:
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

    @property
    def slug(self) -> str:
        """Slug which in combination with board_type, uniquely identifies a platform on the website/api."""
        return self._attributes.get("slug", "")

    @property
    def build_variant(self) -> Tuple[Any, ...]:
        """Build variant for the compiler."""
        # NOTE: Currently we hard code the build variant for a single board type.
        # This is simply so we can demo the tools to PE. This must be removed and replaced with a proper mechanism for
        # determining the build variant for all platforms. We probably need to add this information to the targets
        # database.
        if "lpc55s69" in self.board_type.lower():
            return ("S", "NS")
        return ()


class DatabaseMode(Enum):
    """Select the database mode."""

    OFFLINE = 0
    ONLINE = 1
    AUTO = 2


def get_target_by_product_code(product_code: str, mode: DatabaseMode = DatabaseMode.AUTO) -> MbedTarget:
    """Get an MbedTarget by its product code.

    Args:
        product_code: the product code to look up in the database.
        mode: a DatabaseMode enum field.
    """
    return _get_target({"product_code": product_code}, mode=mode)


def get_target_by_online_id(slug: str, board_type: str, mode: DatabaseMode = DatabaseMode.AUTO) -> MbedTarget:
    """Get an MbedTarget by its online id.

    Args:
        slug: The slug to look up in the database.
        board_type: The board type to look up in the database.
        mode: A DatabaseMode enum field.
    """
    return _get_target({"slug": slug, "board_type": board_type}, mode=mode)


class UnknownTarget(ToolsError):
    """Requested target was not found."""


class UnsupportedMode(ToolsError):
    """The Database Mode is unsupported."""


class MbedTargets(Set):
    """Interface to the Target Database.

    MbedTargets is initialised with an Iterable[MbedTarget]. The classmethods
    can be used to construct MbedTargets with data from either the online or offline database.
    """

    @classmethod
    def from_offline_database(cls) -> "MbedTargets":
        """Initialise with the offline target database."""
        return cls(MbedTarget(t) for t in target_database.get_offline_target_data())

    @classmethod
    def from_online_database(cls) -> "MbedTargets":
        """Initialise with the online target database."""
        return cls(MbedTarget(t) for t in target_database.get_online_target_data())

    def __init__(self, target_data: Iterable["MbedTarget"]) -> None:
        """Initialise with a list of targets.

        Args:
            target_data: iterable of target data from a target database source.
        """
        self._target_data = tuple(target_data)

    def __iter__(self) -> Iterator["MbedTarget"]:
        """Yield an MbedTarget on each iteration."""
        for target in self._target_data:
            yield target

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

    def get_target(self, **query: TargetDatabaseQueryValue) -> "MbedTarget":
        """Look up an MbedTarget.

        Args:
            query: dict which key/value pairs represent expected target property/value pairs

        Raises:
            UnknownTarget: the given product code was not found in the target database.
        """
        try:
            return next(target for target in self if _target_matches_query(target, query))
        except StopIteration:
            raise UnknownTarget(f"Failed to find a target for query: {query}.")

    def json_dump(self) -> str:
        """Return the contents of the target database as a json string."""
        return json.dumps([t._target_entry for t in self], indent=4)


def _get_target(query: TargetDatabaseQuery, mode: DatabaseMode = DatabaseMode.AUTO) -> MbedTarget:
    if mode == DatabaseMode.OFFLINE:
        return MbedTargets.from_offline_database().get_target(**query)
    if mode == DatabaseMode.ONLINE:
        return MbedTargets.from_online_database().get_target(**query)
    if mode == DatabaseMode.AUTO:
        return _try_mbed_targets_offline_and_online(**query)
    else:
        raise UnsupportedMode(f"{mode} is not a supported database mode.")


def _target_matches_query(target: MbedTarget, query: TargetDatabaseQuery) -> bool:
    for query_key, query_value in query.items():
        target_value = getattr(target, query_key)
        if not _values_equal(target_value, query_value):
            return False
    return True


def _values_equal(value_1: Any, value_2: Any) -> bool:
    """Compares two values. If both are strings, peforms a case insensitive comparison."""
    if isinstance(value_1, str) and isinstance(value_2, str):
        value_1 = value_1.casefold()
        value_2 = value_2.casefold()
    return cast(bool, value_1 == value_2)


def _try_mbed_targets_offline_and_online(**query: TargetDatabaseQueryValue) -> MbedTarget:
    """Try an offline database lookup before falling back to the online database."""
    try:
        return MbedTargets.from_offline_database().get_target(**query)
    except UnknownTarget:
        logger.warning("Could not find the requested target in the offline database. Checking the online database.")
        return MbedTargets.from_online_database().get_target(**query)
