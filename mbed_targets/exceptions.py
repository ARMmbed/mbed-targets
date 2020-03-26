#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Public exceptions exposed by the package."""

from mbed_tools_lib.exceptions import ToolsError


class MbedTargetsError(ToolsError):
    """Base exception for mbed-targets."""


class TargetBuildAttributesError(ToolsError):
    """Build attributes for target cannot be retrieved."""


class UnknownTarget(MbedTargetsError):
    """Requested target was not found."""


class UnsupportedMode(MbedTargetsError):
    """The Database Mode is unsupported."""


class TargetDatabaseError(MbedTargetsError):
    """Failed to get the target data from the database."""
