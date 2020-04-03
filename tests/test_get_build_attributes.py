#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase, mock
from mbed_targets.mbed_target_build_attributes import MbedTargetBuildAttributes
from mbed_targets.get_build_attributes import get_build_attributes_by_board_type, get_build_attributes_by_mbed_target
from tests.factories import make_mbed_target
from mbed_project import MbedProgram


class TestGetBuildAttributes(TestCase):
    @mock.patch("mbed_targets.get_build_attributes.MbedTargetBuildAttributes", spec_set=MbedTargetBuildAttributes)
    @mock.patch("mbed_targets.get_build_attributes.MbedProgram", spec_set=MbedProgram)
    def test_get_by_board_type(self, MbedProgram, MbedTargetBuildAttributes):
        board_type = "Board Type"
        path_to_mbed_program = "my-program"

        result = get_build_attributes_by_board_type(board_type, path_to_mbed_program)

        self.assertEqual(result, MbedTargetBuildAttributes.from_board_type.return_value)
        MbedTargetBuildAttributes.from_board_type.assert_called_once_with(
            board_type, MbedProgram.from_existing_local_program_directory.return_value.mbed_os.targets_json_file,
        )
        MbedProgram.from_existing_local_program_directory.assert_called_once_with(path_to_mbed_program)

    @mock.patch("mbed_targets.get_build_attributes.get_build_attributes_by_board_type")
    def test_get_by_mbed_target(self, mock_get_build_attributes_by_board_type):
        mbed_target = make_mbed_target()
        path_to_mbed_program = "somewhere"

        result = get_build_attributes_by_mbed_target(mbed_target, path_to_mbed_program)

        self.assertEqual(result, mock_get_build_attributes_by_board_type.return_value)
        mock_get_build_attributes_by_board_type.assert_called_once_with(mbed_target.board_type, path_to_mbed_program)
