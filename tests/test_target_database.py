"""Tests for `mbed_targets`."""

from unittest import TestCase

import requests_mock

# Unit under test
import mbed_targets._internal.target_database as target_database


class TestGetTargetData(TestCase):
    """Tests for the method `target_database.get_target_data`."""

    @requests_mock.mock()
    def test_401(self, mock_request):
        """Given a 401 error code, TargetAPIError is raised."""
        mock_request.get(
            target_database._TARGET_API, status_code=401
        )
        with self.assertRaises(target_database.TargetAPIError):
            target_database.get_target_data()

    @requests_mock.mock()
    def test_404(self, mock_request):
        """Given a 404 error code, TargetAPIError is raised."""
        mock_request.get(
            target_database._TARGET_API, status_code=404, text="Not Found"
        )
        with self.assertRaises(target_database.TargetAPIError):
            target_database.get_target_data()

    @requests_mock.mock()
    def test_200_invalid_json(self, mock_request):
        """Given a valid response but invalid json, JSONDecodeError is raised."""
        mock_request.get(target_database._TARGET_API, text="invalid json")
        with self.assertRaises(target_database.ResponseJSONError):
            target_database.get_target_data()

    @requests_mock.mock()
    def test_200_no_data_field(self, mock_request):
        """Given a valid response but no data field, ResponseJSONError is raised."""
        mock_request.get(target_database._TARGET_API, json={"notdata": []})
        with self.assertRaises(target_database.ResponseJSONError):
            target_database.get_target_data()

    @requests_mock.mock()
    def test_200_value_data(self, mock_request):
        """Given a valid response, target data is set from the returned json."""
        mock_request.get(target_database._TARGET_API, json={"data": 42})
        target_data = target_database.get_target_data()
        self.assertEqual(42, target_data, "Target data should match the contents of the target API data")
