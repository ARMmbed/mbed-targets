#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib
from pyfakefs.fake_filesystem_unittest import Patcher

from unittest import TestCase
from mbed_targets.mbed_target_build_attributes import MbedTargetBuildAttributes
from mbed_targets.exceptions import TargetBuildAttributesError


class TestMbedTargetBuildAttributes(TestCase):
    def test_get_target_build_attributes(self):
        contents = """{
            "Target": {
                "attribute_1": "Hello",
                "features": ["element_1"]
            },
            "Target_2": {
                "inherits": ["Target"],
                "config": {"Greeting": "Hello indeed!"},
                "features_add": ["element_2", "element_3"]
            },
            "Target_3": {
                "inherits": ["Target_2"],
                "features_remove": ["element_2"]
            }
        }"""
        with Patcher() as patcher:
            path = pathlib.Path("/test/targets.json")
            patcher.fs.create_file(str(path), contents=contents)
            board_type = "Target_3"
            result = MbedTargetBuildAttributes.from_board_type(board_type, str(path))

        self.assertEqual(result.features, frozenset(["element_1", "element_3"]))
        self.assertEqual(result.config, {"Greeting": "Hello indeed!"})

    def test_get_target_build_attributes_not_found_in_targets_json(self):
        contents = """{
            "Target": {
                "attribute_1": "Hello",
                "device_has": ["element_1"]
            },
            "Target_2": {
                "inherits": ["Target"],
                "attribute_1": "Hello indeed!",
                "device_has_add": ["element_2", "element_3"]
            },
            "Target_3": {
                "inherits": ["Target_2"],
                "device_has_remove": ["element_2"]
            }
        }"""
        with Patcher() as patcher:
            path = pathlib.Path("/test/targets.json")
            patcher.fs.create_file(str(path), contents=contents)
            board_type = "Im_not_in_targets_json"
            with self.assertRaises(TargetBuildAttributesError) as context:
                MbedTargetBuildAttributes.from_board_type(board_type, str(path))
            self.assertEqual(str(context.exception), f"Target attributes for {board_type} not found.")

    def test_get_target_build_attributes_bad_path(self):
        path = str(pathlib.Path("i", "am", "bad"))
        board_type = "Target_3"
        with self.assertRaises(TargetBuildAttributesError) as context:
            MbedTargetBuildAttributes.from_board_type(board_type, str(path))
        self.assertIn("No such file or directory:", str(context.exception))
