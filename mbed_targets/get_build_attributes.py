#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Interface for accessing Mbed Target build attributes.

An instance of 'mbed_targets.mbed_target_build_attributes.MbedTargetBuildAttributes`
can be retrieved by calling one of the public functions.
"""
from mbed_targets.mbed_target import MbedTarget
from mbed_targets.mbed_target_build_attributes import MbedTargetBuildAttributes


def get_build_attributes_by_board_type(board_type: str, path_to_targets_json: str) -> MbedTargetBuildAttributes:
    """Returns the build attributes for the target whose name matches the build_type.

    The build attributes are as defined in the targets.json file linked to.

    Args:
        board_type: the board type as found in MbedTarget/the online database
        path_to_targets_json: path to Mbed OS's targets.json file

    Raises:
        TargetBuildAttributesError: an error has occurred while fetching build attributes
    """
    return MbedTargetBuildAttributes.from_board_type(board_type, path_to_targets_json)


def get_build_attributes_by_mbed_target(
    mbed_target: MbedTarget, path_to_targets_json: str
) -> MbedTargetBuildAttributes:
    """Returns the build attributes for the Mbed Target.

    The build attributes are as defined in the targets.json file linked to.

    Args:
        mbed_target: the Mbed Target object representing the target data from the online database
        path_to_targets_json: path to Mbed OS's targets.json file

    Raises:
        TargetBuildAttributesError: an error has occurred while fetching build attributes
    """
    return get_build_attributes_by_board_type(mbed_target.board_type, path_to_targets_json)
