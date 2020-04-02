#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""mbed-targets provides an abstraction layer for boards and platforms supported by Mbed OS.

This package is intended for use by developers using Mbed OS.

Querying target database
------------------------

For the interface to query target database, look at `mbed_targets.get_target`.

Parsing target build attributes
_______________________________

For the interface to extract build attributes from a targets.json file, look
at `mbed_targets.get_build_attributes`.

Configuration
-------------

For details about configuration of this module, look at `mbed_targets.config`.
"""
from mbed_targets import exceptions
from mbed_targets._version import __version__
from mbed_targets.get_build_attributes import (
    get_build_attributes_by_mbed_target,
    get_build_attributes_by_board_type,
)
from mbed_targets.get_target import (
    get_target_by_product_code,
    get_target_by_online_id,
)
from mbed_targets.mbed_target import MbedTarget
from mbed_targets.mbed_target_build_attributes import MbedTargetBuildAttributes
