#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Representation of an Mbed Target and related utilities."""
from dataclasses import dataclass
from typing import Any, Tuple, cast

from mbed_targets.exceptions import TargetBuildAttributesError
from mbed_targets._internal import target_attributes


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
        return target_attributes.get_target_attributes(path_to_targets_json, mbed_target.board_type)
    except (FileNotFoundError, target_attributes.TargetAttributesError) as e:
        raise TargetBuildAttributesError(e) from e
