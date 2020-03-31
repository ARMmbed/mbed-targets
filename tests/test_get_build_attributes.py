#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase, mock
from mbed_targets.mbed_target_build_attributes import MbedTargetBuildAttributes
from mbed_targets.get_build_attributes import get_build_attributes_by_board_type, get_build_attributes_by_mbed_target
from tests.factories import make_mbed_target


class TestGetBuildAttributes(TestCase):
    @mock.patch("mbed_targets.get_build_attributes.MbedTargetBuildAttributes", spec_set=MbedTargetBuildAttributes)
    def test_get_by_board_type(self, mock_build_attributes_class):
        board_type = "Board Type"
        path_to_targets_json = "somewhere/targets.json"

        result = get_build_attributes_by_board_type(board_type, path_to_targets_json)

        self.assertEqual(result, mock_build_attributes_class.from_board_type.return_value)
        mock_build_attributes_class.from_board_type.assert_called_once_with(board_type, path_to_targets_json)

    @mock.patch("mbed_targets.get_build_attributes.get_build_attributes_by_board_type")
    def test_get_by_mbed_target(self, mock_get_build_attributes_by_board_type):
        mbed_target = make_mbed_target()
        path_to_targets_json = "somewhere/targets.json"

        result = get_build_attributes_by_mbed_target(mbed_target, path_to_targets_json)

        self.assertEqual(result, mock_get_build_attributes_by_board_type.return_value)
        mock_get_build_attributes_by_board_type.assert_called_once_with(mbed_target.board_type, path_to_targets_json)
