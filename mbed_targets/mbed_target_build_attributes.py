#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Module describing how to build a specific target."""
from dataclasses import dataclass
from typing import FrozenSet, Dict, Optional

from mbed_targets.exceptions import TargetBuildAttributesError
from mbed_targets._internal import target_attributes


@dataclass(frozen=True, order=True)
class MbedTargetBuildAttributes:
    """Representation of a target definition in Mbed OS library's targets.json file.

    These attributes contains the specific information needed to build Mbed applications for this target.

    Attributes:
        labels: Sections of Mbed OS to be included in builds for this target.
        features: Sections of Mbed OS features to be included in builds for this target.
        components: Sections of Mbed OS components to be included in builds for this target.
        config: Configuration defaults for this target to be used in builds.
        supported_toolchains: Toolchains that can be used to build for this target.
        default_toolchain: Default toolchain used for this target.
    """

    labels: FrozenSet[str]
    features: FrozenSet[str]
    components: FrozenSet[str]
    config: Dict[str, str]
    supported_toolchains: FrozenSet[str]
    default_toolchain: Optional[str]

    @classmethod
    def from_board_type(cls, mbed_target_board_type: str, path_to_targets_json: str) -> "MbedTargetBuildAttributes":
        """Construct MbedTargetBuildAttributes with data from Mbed OS library's targets.json file.

        Args:
            mbed_target_board_type: an MbedTarget object representing the target to find build attributes for
            path_to_targets_json: path to targets.json, located in the Mbed OS library

        Raises:
            TargetBuildAttributesError: an error has occurred while fetching build attributes
        """
        try:
            attributes = target_attributes.get_target_attributes(path_to_targets_json, mbed_target_board_type)
        except (FileNotFoundError, target_attributes.TargetAttributesError) as e:
            raise TargetBuildAttributesError(e) from e

        return cls(
            labels=frozenset(attributes.get("labels", set()).union(attributes.get("extra_labels", set()))),
            features=frozenset(attributes.get("features", set())),
            components=frozenset(attributes.get("components", set())),
            config=attributes.get("config"),
            supported_toolchains=frozenset(attributes.get("supported_toolchains", [])),
            default_toolchain=attributes.get("default_toolchain", None),
        )
