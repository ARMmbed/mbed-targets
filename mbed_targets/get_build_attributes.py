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
from mbed_project import MbedProgram


def get_build_attributes_by_board_type(board_type: str, path_to_mbed_program: str) -> MbedTargetBuildAttributes:
    """Returns the build attributes for the target whose name matches the build_type.

    The build attributes are as defined in the targets.json file linked to.

    Args:
        board_type: the board type as found in MbedTarget/the online database
        path_to_mbed_program: path to Mbed OS program

    Raises:
        TargetBuildAttributesError: an error has occurred while fetching build attributes
    """
    mbed_program = MbedProgram.from_existing_local_program_directory(path_to_mbed_program)
    path_to_targets_json = mbed_program.mbed_os.targets_json_file
    return MbedTargetBuildAttributes.from_board_type(board_type, path_to_targets_json)


def get_build_attributes_by_mbed_target(
    mbed_target: MbedTarget, path_to_mbed_program: str
) -> MbedTargetBuildAttributes:
    """Returns the build attributes for the Mbed Target.

    The build attributes are as defined in the targets.json file linked to.

    Args:
        mbed_target: the Mbed Target object representing the target data from the online database
        path_to_mbed_program: path to Mbed OS program

    Raises:
        TargetBuildAttributesError: an error has occurred while fetching build attributes
    """
    return get_build_attributes_by_board_type(mbed_target.board_type, path_to_mbed_program)
