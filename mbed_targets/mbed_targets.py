#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Interface to the Target Database."""
import json

from dataclasses import asdict
from collections.abc import Set
from typing import Iterator, Iterable, Any, Callable

from mbed_targets._internal import target_database

from mbed_targets.exceptions import UnknownTarget
from mbed_targets.mbed_target import MbedTarget


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

    def get_target(self, matching: Callable) -> MbedTarget:
        """Returns first MbedTarget for which `matching` returns True.

        Args:
            matching: A function which will be called for each target in database

        Raises:
            UnknownTarget: the given product code was not found in the target database.
        """
        try:
            return next(target for target in self if matching(target))
        except StopIteration:
            raise UnknownTarget()

    def json_dump(self) -> str:
        """Return the contents of the target database as a json string."""
        return json.dumps([asdict(t) for t in self], indent=4)
