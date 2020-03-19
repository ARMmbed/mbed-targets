import os
from unittest import TestCase, mock

from mbed_targets.config import config


class TestMbedApiAuthToken(TestCase):
    @mock.patch.dict(os.environ, {"MBED_API_AUTH_TOKEN": "sometoken"})
    def test_returns_api_token_set_in_env(self):
        self.assertEqual(config.MBED_API_AUTH_TOKEN, "sometoken")


class TestDatabaseMode(TestCase):
    @mock.patch.dict(os.environ, {"MBED_DATABASE_MODE": "ONLINE"})
    def test_returns_database_mode_set_in_env(self):
        self.assertEqual(config.MBED_DATABASE_MODE, "ONLINE")

    def test_returns_default_database_mode_if_not_set_in_env(self):
        self.assertEqual(config.MBED_DATABASE_MODE, "AUTO")
