#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""mbed-targets provides an abstraction layer for hardware supported by Mbed OS.

This package is intended for use by developers using Mbed OS.

Querying board database
-----------------------

For the interface to query board database, look at `mbed_targets.get_board`.

Fetching target data
____________________

For the interface to extract target data from their definitions in Mbed OS,
look at `mbed_targets.get_target`.

Configuration
-------------

For details about configuration of this module, look at `mbed_targets.config`.
"""
from mbed_targets import exceptions
from mbed_targets._version import __version__
from mbed_targets.get_target import (
    get_target_by_name,
    get_target_by_board_type,
)
from mbed_targets.get_board import (
    get_board_by_product_code,
    get_board_by_online_id,
)
from mbed_targets.board import Board
from mbed_targets.target import Target
