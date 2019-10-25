"""Tests for `mbed_targets`."""

import unittest

# Unit under test
import mbed_targets._internal.target_database as target_database


# Fake data from the API
FAKE_TARGET_API_DATA = {
    "data": [
        {
            "attributes": {
                "features": {
                    "mbed_os_support": [
                        "Mbed OS 5.10",
                        "Mbed OS 5.11",
                        "Mbed OS 5.8",
                        "Mbed OS 5.9"
                    ],
                    "mbed_enabled": [
                        "Basic"
                    ]
                },
                "board_type": "COMPILATION_TARGET_1",
                "name": "Board A",
                "product_code": "11",
            }
        },
        {
            "attributes": {
                "features": {
                    "mbed_os_support": [
                        "Mbed OS 5.13",
                        "Mbed OS 2"
                    ]
                },
                "board_type": "COMPILATION_TARGET_1",
                "name": "Board B",
                "product_code": "12",
            }
        },
        {
            "attributes": {
                "features": {
                    "mbed_os_support": [
                        "Mbed OS 5.12"
                    ]
                },
                "board_type": "COMPILATION_TARGET_2",
                "name": "Board C",
                "product_code": "21",
            }
        },
        {
            "attributes": {
                "features": {
                    "mbed_enabled": [
                        "Advanced"
                    ]
                },
                "board_type": "COMPILATION_TARGET_3",
                "name": "Board C",
                "product_code": "21",
            }
        },
        {
            "attributes": {
                "features": {
                },
                "board_type": "No mbed_os_support data",
                "name": "No mbed_os_support data",
            }
        },
        {
            "attributes": {
                "features": {
                    "mbed_os_support": [
                        "Mbed OS 5"
                    ]
                },
                "name": "No board_type data",
                "product_code": "33",
            }
        },
        {
            "attributes": {
                "features": {
                    "mbed_os_support": [
                        "Mbed OS 5"
                    ]
                },
                "board_type": "No name data",
                "product_code": "44",
            }
        },
        {
            "attributes": {
                "features": {
                    "mbed_os_support": [
                        "Mbed OS 5"
                    ]
                },
                "board_type": "No product_code",
                "name": "No product_code",
            }
        },
        {
            "attributes": {
                "features": {
                    "mbed_enabled": [
                        "Advanced"
                    ]
                },
                "board_type": "COMPILATION_TARGET_?",
                "name": "Board missing from Mbed OS",
                "product_code": "666",
            }
        },
    ]
}


class TestGetTargetData(unittest.TestCase):
    """Tests for the method `target_database._get_target_data`."""

    @requests_mock.mock()
    def test_invalid_data(self, mock_request):
        mock_request.get(target_database._TARGET_API, text="invalid_json")
        target_db = target_database.TargetDatabase()
        self.assertEqual(target_db.target_data, [])

    @requests_mock.mock()
    def test_404(self, mock_request):
        mock_request.get(target_database._TARGET_API, status_code=404)

        mbed_os_versions, compilation_targets = mbed_os_targets._get_target_boards()
        self.assertEqual(mbed_os_versions, [])
        self.assertEqual(compilation_targets, {})

    @requests_mock.mock()
    def test_get_targets(self, mock_request):
        expected_compilation_target = {
            'COMPILATION_TARGET_1': {
                'platform_ids': ['11', '12'],
                'names': ['Board A', 'Board B'],
                'supported_os_versions': ['5.13', '5.11', '5.10', '5.9', '5.8', '2.0'],
                'test_os_versions': ['5.13', '2.0']
            },
            'COMPILATION_TARGET_2': {
                'platform_ids': ['21'],
                'names': ['Board C'],
                'supported_os_versions': ['5.12'],
                'test_os_versions': ['5.13', '5.12']
            }
        }

        mock_request.get(target_database._TARGET_API, json=FAKE_TARGET_API_DATA)

        all_os_versions, compilation_targets = mbed_os_targets._get_target_boards()
        self.assertEqual(all_os_versions, EXPECTED_ALL_OS_VERSIONS)
        self.assertEqual(compilation_targets, expected_compilation_target)
