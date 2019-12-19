"""Tests for `mbed_targets`."""

import unittest
import requests_mock

# Unit under test
import mbed_targets._internal.target_database as target_database


class TestGetTargetData(unittest.TestCase):
    """Tests for the method `target_database.get_target_data`."""

    @requests_mock.mock()
    def test_404(self, mock_request):
        mock_request.get(target_database._TARGET_API, status_code=404, text="Not Found")
        target_data = target_database.get_target_data()
        self.assertIsNone(target_data, "Target data is expected to be empty on an error")

    @requests_mock.mock()
    def test_401(self, mock_request):
        mock_request.get(target_database._TARGET_API, status_code=401)
        target_data = target_database.get_target_data()
        self.assertIsNone(target_data, "Target data is expected to be empty on an error")

    @requests_mock.mock()
    def test_200_invalid_json(self, mock_request):
        mock_request.get(target_database._TARGET_API, text="invalid_json")
        target_data = target_database.get_target_data()
        self.assertIsNone(target_data, "Target data is expected to be empty on an error")

    @requests_mock.mock()
    def test_200_no_data(self, mock_request):
        mock_request.get(target_database._TARGET_API, json={})
        target_data = target_database.get_target_data()
        self.assertIsNone(target_data, "Target data is expected to be empty on an error")

    @requests_mock.mock()
    def test_200_value_data(self, mock_request):
        mock_request.get(target_database._TARGET_API, json={"data": 42})
        target_data = target_database.get_target_data()
        self.assertEqual(42, target_data, "Target data is should match the contents of the target API data")
