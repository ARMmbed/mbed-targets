"""Tests for sync_target_database.py."""
import json

from unittest import TestCase, mock

from ci_scripts import sync_target_database


TARGET_1 = """    {
        "type": "target",
        "id": "1",
        "attributes": {
            "features": {
                "mbed_enabled": [
                    "Advanced"
                ],
                "mbed_os_support": [
                    "Mbed OS 5.10",
                    "Mbed OS 5.11",
                    "Mbed OS 5.12",
                    "Mbed OS 5.13",
                    "Mbed OS 5.14",
                    "Mbed OS 5.15",
                    "Mbed OS 5.8",
                    "Mbed OS 5.9"
                ],
                "antenna": [
                    "Connector",
                    "Onboard"
                ],
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
                    "RoHS (Europe)"
                ],
                "communication": [
                    "Bluetooth & BLE"
                ],
                "interface_firmware": [
                    "DAPLink",
                    "J-Link"
                ],
                "target_core": [
                    "Cortex-M4"
                ],
                "mbed_studio_support": [
                    "Build and run"
                ]
            },
            "board_type": "MTB_UBLOX_NINA_B1",
            "flash_size": 512,
            "name": "u-blox NINA-B1",
            "product_code": "0455",
            "ram_size": 64,
            "target_type": "module",
            "hidden": false,
            "device_name": "nRF52832_xxAA"
        }
    }"""

TARGET_2 = """    {
        "type": "target",
        "id": "2",
        "attributes": {
            "features": {
                "mbed_enabled": [
                    "Advanced"
                ],
                "mbed_os_support": [
                    "Mbed OS 5.10",
                    "Mbed OS 5.11",
                    "Mbed OS 5.12",
                    "Mbed OS 5.13",
                    "Mbed OS 5.14",
                    "Mbed OS 5.15",
                    "Mbed OS 5.8",
                    "Mbed OS 5.9"
                ],
                "antenna": [
                    "Connector"
                ],
                "certification": [
                    "AS/NZS (Australia and New Zealand)",
                    "CE (Europe)",
                    "FCC/CFR (USA)",
                    "IC RSS (Canada)"
                ],
                "communication": [
                    "LoRa"
                ],
                "interface_firmware": [
                    "DAPLink"
                ],
                "target_core": [
                    "Cortex-M3"
                ],
                "mbed_studio_support": [
                    "Build and run"
                ]
            },
            "board_type": "MTB_MTS_XDOT",
            "flash_size": 256,
            "name": "Multitech xDOT",
            "product_code": "0453",
            "ram_size": 64,
            "target_type": "module",
            "hidden": false,
            "device_name": "STM32L151CC"
        }
    }"""

ONLINE_TARGET_DATABASE = f"[{TARGET_1}, {TARGET_2}]"

OFFLINE_TARGET_DATABASE = f"[{TARGET_1}]"

EXPECTED_DIFF = f"[{TARGET_2}]"


class TestSyncTargetDB(TestCase):
    def test_diff_objects_from_json_returns_diffs(self):
        with mock.patch("ci_scripts.sync_target_database.MbedTargets") as mock_online_targets:
            mock_online_targets.json_dump.return_value = ONLINE_TARGET_DATABASE
            diffs = sync_target_database.diff_objects_from_json_str(
                mock_online_targets.json_dump(), OFFLINE_TARGET_DATABASE
            )
            self.assertEqual(diffs, json.loads(EXPECTED_DIFF), "Actual diff and expected diff should match")

    def test_diff_objects_from_json_returns_none_when_no_change(self):
        diffs = sync_target_database.diff_objects_from_json_str(OFFLINE_TARGET_DATABASE, OFFLINE_TARGET_DATABASE)
        self.assertEqual(diffs, [], "Should return an empty list when no diff")

    def test_news_file_item_text_formatting(self):
        with mock.patch("ci_scripts.sync_target_database.Path", autospec=True) as mock_path:
            mock_path().exists.return_value = False
            text = sync_target_database.create_new_boards_news_item_text(json.loads(ONLINE_TARGET_DATABASE))
            self.assertEqual(
                text, "New boards added: MTB_UBLOX_NINA_B1, MTB_MTS_XDOT", "Text should be formatted correctly."
            )

    def test_news_file_name_suffix_increments_when_path_exists(self):
        with mock.patch("ci_scripts.sync_target_database.Path", autospec=True) as mock_path:

            def side_effect(arg):
                mock_path().name = arg
                return mock_path()

            mock_path().with_name.side_effect = side_effect
            mock_path().exists.side_effect = [True, True, False]
            news_file_path = sync_target_database.write_news_file("news item", "news")
            self.assertEqual(
                "news02.feature", news_file_path.name, "News file name should have a incremented suffix of 02"
            )
