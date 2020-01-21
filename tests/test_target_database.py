"""Tests for `mbed_targets`."""

import unittest
import requests_mock

# Unit under test
import mbed_targets._internal.target_database as target_database


class TestGetTargetData(unittest.TestCase):
    """Tests for the method `target_database.get_target_data`."""

    @requests_mock.mock()
    def test_404(self, mock_request):
        """Given a 404 response, target data is not set."""
        mock_request.get(target_database._TARGET_API, status_code=404, text="Not Found")
        target_data = target_database.get_target_data()
        self.assertIsNone(target_data, "Target data is expected to be empty on an error")

    @requests_mock.mock()
    def test_401(self, mock_request):
        """Given a 401 response, target data is not set."""
        mock_request.get(target_database._TARGET_API, status_code=401)
        target_data = target_database.get_target_data()
        self.assertIsNone(target_data, "Target data is expected to be empty on an error")

    @requests_mock.mock()
    def test_200_invalid_json(self, mock_request):
        """Given a valid response but invalid json, target data is not set."""
        mock_request.get(target_database._TARGET_API, text="invalid_json")
        target_data = target_database.get_target_data()
        self.assertIsNone(target_data, "Target data is expected to be empty on an error")

    @requests_mock.mock()
    def test_200_no_data(self, mock_request):
        """Given a valid response but no json data, target data is not set."""
        mock_request.get(target_database._TARGET_API, json={})
        target_data = target_database.get_target_data()
        self.assertIsNone(target_data, "Target data is expected to be empty on an error")

    @requests_mock.mock()
    def test_200_value_data(self, mock_request):
        """Given a valid response, target data is set from the returned json."""
        mock_request.get(target_database._TARGET_API, json={"data": 42})
        target_data = target_database.get_target_data()
        self.assertEqual(42, target_data, "Target data is should match the contents of the target API data")
