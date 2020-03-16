"""Tests for `mbed_targets`."""

import os
from unittest import TestCase, mock

import requests_mock

# Unit under test
import mbed_targets._internal.target_database as target_database


class TestGetOnlineTargetData(TestCase):
    """Tests for the method `target_database.get_online_target_data`."""

    @requests_mock.mock()
    def test_401(self, mock_request):
        """Given a 401 error code, TargetAPIError is raised."""
        mock_request.get(target_database._TARGET_API, status_code=401)
        with self.assertRaises(target_database.TargetAPIError):
            target_database.get_online_target_data()

    @requests_mock.mock()
    def test_404(self, mock_request):
        """Given a 404 error code, TargetAPIError is raised."""
        mock_request.get(target_database._TARGET_API, status_code=404, text="Not Found")
        with self.assertRaises(target_database.TargetAPIError):
            target_database.get_online_target_data()

    @requests_mock.mock()
    def test_200_invalid_json(self, mock_request):
        """Given a valid response but invalid json, JSONDecodeError is raised."""
        mock_request.get(target_database._TARGET_API, text="invalid json")
        with self.assertRaises(target_database.ResponseJSONError):
            target_database.get_online_target_data()

    @requests_mock.mock()
    def test_200_no_data_field(self, mock_request):
        """Given a valid response but no data field, ResponseJSONError is raised."""
        mock_request.get(target_database._TARGET_API, json={"notdata": []})
        with self.assertRaises(target_database.ResponseJSONError):
            target_database.get_online_target_data()

    @requests_mock.mock()
    def test_200_value_data(self, mock_request):
        """Given a valid response, target data is set from the returned json."""
        mock_request.get(target_database._TARGET_API, json={"data": 42})
        target_data = target_database.get_online_target_data()
        self.assertEqual(42, target_data, "Target data should match the contents of the target API data")

    @mock.patch("mbed_targets._internal.target_database.requests")
    @mock.patch("mbed_targets._internal.target_database.MBED_API_AUTH_TOKEN", "token")
    def test_auth_header_set_with_token(self, requests):
        """Given an authorization token env variable, get is called with authorization header."""
        header = {"Authorization": f"Bearer token"}
        target_database._get_request()
        requests.get.assert_called_once_with(target_database._TARGET_API, headers=header)

    @mock.patch("mbed_targets._internal.target_database.requests")
    def test_no_auth_header_set_with_empty_token_var(self, requests):
        """Given no authorization token env variable, get is called with no header."""
        os.environ["MBED_API_AUTH_TOKEN"] = ""
        target_database._get_request()
        requests.get.assert_called_once_with(target_database._TARGET_API, headers=None)

    @mock.patch("mbed_targets._internal.target_database.requests.get")
    def test_raises_tools_error_on_connection_error(self, get):
        get.side_effect = target_database.requests.exceptions.ConnectionError
        with self.assertRaises(target_database.TargetAPIError):
            target_database._get_request()


class TestGetOfflineTargetData(TestCase):
    """Tests for the method get_offline_target_data."""

    def test_local_target_database_file_found(self):
        """Test local database is found and loaded."""
        data = target_database.get_offline_target_data()
        self.assertTrue(len(data), "Some data should be returned from local database file.")

    @mock.patch("mbed_targets._internal.target_database.get_target_database_path")
    def test_raises_on_invalid_json(self, mocked_get_file):
        """Test raises an error when the file contains invalid JSON."""
        invalid_json = "None"
        path_mock = mock.Mock()
        path_mock.read_text.return_value = invalid_json
        mocked_get_file.return_value = path_mock
        with self.assertRaises(target_database.ResponseJSONError):
            target_database.get_offline_target_data()


class TestGetLocalTargetDatabaseFile(TestCase):
    def test_returns_path_to_targets(self):
        path = target_database.get_target_database_path()
        self.assertEqual(path.exists(), True, "Path to targets should exist in the package data folder.")
