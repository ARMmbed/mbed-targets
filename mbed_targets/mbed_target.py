#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Representation of an Mbed Target and related utilities."""
from dataclasses import dataclass
from typing import Tuple, cast


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
            # Online database has inconsistently cased board types.
            # Since this field is used to match against `targets.json`, we need to ensure consistency is maintained.
            board_type=target_attrs.get("board_type", "").upper(),
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
