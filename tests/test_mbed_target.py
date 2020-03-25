#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Tests for `mbed_targets.mbed_target`."""

import pathlib
from pyfakefs.fake_filesystem_unittest import Patcher
from unittest import TestCase

# Import from top level as this is the expected interface for users
from mbed_targets import MbedTarget
from mbed_targets.mbed_target import get_target_build_attributes
from mbed_targets.exceptions import TargetBuildAttributesError
from tests.factories import make_mbed_target


class TestMbedTarget(TestCase):
    """Tests for the class `MbedTarget`."""

    def test_offline_database_entry(self):
        """Given an entry from the offline database, an MbedTarget is generated with the correct information."""
        mbed_target = MbedTarget.from_offline_target_entry(
            {
                "mbed_os_support": ["Mbed OS 5.15"],
                "mbed_enabled": ["Basic"],
                "board_type": "B_1",
                "board_name": "Board 1",
                "product_code": "P1",
                "target_type": "platform",
                "slug": "Le Slug",
            }
        )

        self.assertEqual("B_1", mbed_target.board_type)
        self.assertEqual("Board 1", mbed_target.board_name)
        self.assertEqual(("Mbed OS 5.15",), mbed_target.mbed_os_support)
        self.assertEqual(("Basic",), mbed_target.mbed_enabled)
        self.assertEqual("P1", mbed_target.product_code)
        self.assertEqual("platform", mbed_target.target_type)
        self.assertEqual("Le Slug", mbed_target.slug)
        self.assertEqual((), mbed_target.build_variant)

    def test_build_variant_hack(self):
        mbed_target = make_mbed_target(board_type="lpc55s69")

        self.assertEqual(mbed_target.build_variant, ("S", "NS"))

    def test_empty_database_entry(self):
        """Given no data, and MbedTarget is created with no information."""
        mbed_target = MbedTarget.from_online_target_entry({})

        self.assertEqual("", mbed_target.board_type)
        self.assertEqual("", mbed_target.board_name)
        self.assertEqual((), mbed_target.mbed_os_support)
        self.assertEqual((), mbed_target.mbed_enabled)
        self.assertEqual("", mbed_target.product_code)
        self.assertEqual("", mbed_target.target_type)
        self.assertEqual("", mbed_target.slug)

    def test_online_database_entry(self):
        online_data = {
            "type": "target",
            "id": "1",
            "attributes": {
                "features": {
                    "mbed_enabled": ["Advanced"],
                    "mbed_os_support": [
                        "Mbed OS 5.10",
                        "Mbed OS 5.11",
                        "Mbed OS 5.12",
                        "Mbed OS 5.13",
                        "Mbed OS 5.14",
                        "Mbed OS 5.15",
                        "Mbed OS 5.8",
                        "Mbed OS 5.9",
                    ],
                    "antenna": ["Connector", "Onboard"],
                    "certification": [
                        "Anatel (Brazil)",
                        "AS/NZS (Australia and New Zealand)",
                        "CE (Europe)",
                        "FCC/CFR (USA)",
                        "IC RSS (Canada)",
                        "ICASA (South Africa)",
                        "KCC (South Korea)",
                        "MIC (Japan)",
                        "NCC (Taiwan)",
                        "RoHS (Europe)",
                    ],
                    "communication": ["Bluetooth & BLE"],
                    "interface_firmware": ["DAPLink", "J-Link"],
                    "target_core": ["Cortex-M4"],
                    "mbed_studio_support": ["Build and run"],
                },
                "board_type": "MTB_UBLOX_NINA_B1",
                "flash_size": 512,
                "name": "u-blox NINA-B1",
                "product_code": "0455",
                "ram_size": 64,
                "target_type": "module",
                "hidden": False,
                "device_name": "nRF52832_xxAA",
                "slug": "u-blox-nina-b1",
            },
        }
        mbed_target = MbedTarget.from_online_target_entry(online_data)

        self.assertEqual(online_data["attributes"]["board_type"], mbed_target.board_type)
        self.assertEqual(online_data["attributes"]["name"], mbed_target.board_name)
        self.assertEqual(tuple(online_data["attributes"]["features"]["mbed_os_support"]), mbed_target.mbed_os_support)
        self.assertEqual(tuple(online_data["attributes"]["features"]["mbed_enabled"]), mbed_target.mbed_enabled)
        self.assertEqual(online_data["attributes"]["product_code"], mbed_target.product_code)
        self.assertEqual(online_data["attributes"]["target_type"], mbed_target.target_type)
        self.assertEqual(online_data["attributes"]["slug"], mbed_target.slug)
        self.assertEqual(tuple(), mbed_target.build_variant)


class TestGetBuildAttributes(TestCase):
    def test_get_target_build_attributes(self):
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
            mbed_target = make_mbed_target(board_name="Target_3")
            expected_result = {
                "attribute_1": "Hello indeed!",
                "device_has": ["element_1", "element_3"],
                "labels": {"Target", "Target_2", "Target_3"},
            }
            result = get_target_build_attributes(mbed_target, str(path))

        self.assertEqual(result, expected_result)

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
            board_name = "Im_not_in_targets_json"
            mbed_target = make_mbed_target(board_name=board_name)
            with self.assertRaises(TargetBuildAttributesError) as context:
                get_target_build_attributes(mbed_target, str(path))
            self.assertEqual(str(context.exception), f"Target attributes for {board_name} not found.")

    def test_get_target_build_attributes_bad_path(self):
        path = str(pathlib.Path("i", "am", "bad"))
        mbed_target = make_mbed_target(board_name="Target_3")
        with self.assertRaises(TargetBuildAttributesError) as context:
            get_target_build_attributes(mbed_target, path)
        self.assertIn("No such file or directory:", str(context.exception))
