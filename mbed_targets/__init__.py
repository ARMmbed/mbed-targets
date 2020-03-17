"""mbed-targets provides an abstraction layer for boards and platforms supported by Mbed OS.

This package is intended for use by developers using Mbed OS.

Configuration
-------------

For details about configuration of this module, look at `mbed_targets.config`.
"""
from mbed_targets._version import __version__
from mbed_targets.mbed_targets import (
    get_target_by_product_code,
    get_target_by_online_id,
    MbedTarget,
)
from mbed_targets import exceptions
