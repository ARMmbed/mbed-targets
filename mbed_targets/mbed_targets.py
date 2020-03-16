"""Interface to the Mbed Targets module.

mbed targets supports an online and offline mode, which instructs targets where to look up the target database.

An MbedTarget can be retrieved by calling one of the public functions. All of which return an instance
of MbedTarget.
"""
from dataclasses import dataclass, asdict
import json
import logging

from collections.abc import Set
from typing import Iterator, Iterable, Tuple, Any, Dict, Union, cast

from mbed_targets._internal import target_database
from mbed_targets._internal import target_attributes
from mbed_targets.exceptions import UnknownTarget, TargetBuildAttributesError
from mbed_targets._internal.configuration import DatabaseMode, MBED_DATABASE_MODE


logger = logging.getLogger(__name__)


TargetDatabaseQueryValue = Union[str, Tuple]
TargetDatabaseQuery = Dict[str, TargetDatabaseQueryValue]


@dataclass(frozen=True, order=True)
class MbedTarget:
    """Representation of an Mbed Target.

    Attributes:
        board_type: Type of board the target represents.
        board_name: Human readable name.
        product_code: Uniquely identifies a platform for the online compiler.
        target_type: Identifies if the target is a module or a platform.
        slug: Identifies a platform's page on the mbed website, used with target_type to identify the target.
        build_variant: Build variant for the compiler.
        mbed_os_support: Mbed OS versions supported.
        mbed_enabled: Enabled Mbed OS support.
    """

    board_type: str
    board_name: str
    product_code: str
    target_type: str
    slug: str
    build_variant: Tuple[str, ...]
    mbed_os_support: Tuple[str, ...]
    mbed_enabled: Tuple[str, ...]

    @classmethod
    def from_online_target_entry(cls, target_entry: dict) -> "MbedTarget":
        """Create a new instance of MbedTarget from an online target database entry.

        Args:
            target_entry: A single entity retrieved from the target API.
        """
        target_attrs = target_entry.get("attributes", {})
        target_features = target_attrs.get("features", {})

        return cls(
            board_type=target_attrs.get("board_type", ""),
            board_name=target_attrs.get("name", ""),
            mbed_os_support=tuple(target_features.get("mbed_os_support", [])),
            mbed_enabled=tuple(target_features.get("mbed_enabled", [])),
            product_code=target_attrs.get("product_code", ""),
            target_type=target_attrs.get("target_type", ""),
            slug=target_attrs.get("slug", ""),
            # NOTE: Currently we hard code the build variant for a single board type.
            # This is simply so we can demo the tools to PE. This must be removed and replaced with a proper mechanism
            # for determining the build variant for all platforms. We probably need to add this information to the
            # targets database.
            build_variant=cast(Tuple, ("S", "NS") if "lpc55s69" in target_attrs.get("board_type", "") else ()),
        )

    @classmethod
    def from_offline_target_entry(cls, target_entry: dict) -> "MbedTarget":
        """Construct an MbedTarget with data from the offline database snapshot."""
        return cls(
            board_type=target_entry.get("board_type", ""),
            board_name=target_entry.get("board_name", ""),
            product_code=target_entry.get("product_code", ""),
            target_type=target_entry.get("target_type", ""),
            slug=target_entry.get("slug", ""),
            mbed_os_support=tuple(target_entry.get("mbed_os_support", [])),
            mbed_enabled=tuple(target_entry.get("mbed_enabled", [])),
            build_variant=tuple(target_entry.get("build_variant", [])),
        )


def get_target_by_product_code(product_code: str) -> MbedTarget:
    """Get an MbedTarget by its product code.

    Args:
        product_code: the product code to look up in the database.
    """
    return _get_target({"product_code": product_code})


def get_target_by_online_id(slug: str, target_type: str) -> MbedTarget:
    """Get an MbedTarget by its online id.

    Args:
        slug: The slug to look up in the database.
        target_type: The board type to look up in the database.
    """
    return _get_target({"slug": slug, "target_type": target_type})


def get_target_build_attributes(mbed_target: MbedTarget, path_to_targets_json: str) -> Any:
    """Parses targets.json and returns a dict of build attributes for the Mbed target.

    These attributes contains the specific information needed to build Mbed applications for this target.

    Args:
        mbed_target: an MbedTarget object representing the target to find build attributes for
        path_to_targets_json: path to a targets.json file found in the Mbed OS library

    Returns:
        A dict containing the parsed attributes from targets.json

    Raises:
        TargetBuildAttributesError: an error has occurred while fetching build attributes
    """
    try:
        return target_attributes.get_target_attributes(path_to_targets_json, mbed_target.board_name)
    except (FileNotFoundError, target_attributes.TargetAttributesError) as e:
        raise TargetBuildAttributesError(e) from e


class MbedTargets(Set):
    """Interface to the Target Database.

    MbedTargets is initialised with an Iterable[MbedTarget]. The classmethods
    can be used to construct MbedTargets with data from either the online or offline database.
    """

    @classmethod
    def from_offline_database(cls) -> "MbedTargets":
        """Initialise with the offline target database.

        Raises:
            TargetDatabaseError: Could not retrieve data from the target database.
        """
        return cls(MbedTarget.from_offline_target_entry(t) for t in target_database.get_offline_target_data())

    @classmethod
    def from_online_database(cls) -> "MbedTargets":
        """Initialise with the online target database.

        Raises:
            TargetDatabaseError: Could not retrieve data from the target database.
        """
        return cls(MbedTarget.from_online_target_entry(t) for t in target_database.get_online_target_data())

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
        return json.dumps([asdict(t) for t in self], indent=4)


def _get_target(query: TargetDatabaseQuery) -> MbedTarget:
    if MBED_DATABASE_MODE == DatabaseMode.OFFLINE:
        return MbedTargets.from_offline_database().get_target(**query)
    if MBED_DATABASE_MODE == DatabaseMode.ONLINE:
        return MbedTargets.from_online_database().get_target(**query)
    return _try_mbed_targets_offline_and_online(**query)


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
