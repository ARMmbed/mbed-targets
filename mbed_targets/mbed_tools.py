#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Integration with https://github.com/ARMmbed/mbed-tools."""
import pdoc
from mbed_targets.config import Config

config_variables = pdoc.Class("Config", pdoc.Module("mbed_targets.config"), Config).instance_variables()
