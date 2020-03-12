import os
from importlib import reload
from unittest import TestCase, mock

from mbed_targets._internal import configuration


class TestMbedApiAuthToken(TestCase):
    @mock.patch.dict(os.environ, {"MBED_API_AUTH_TOKEN": "sometoken"})
    def test_returns_api_token_set_in_env(self):
        reload(configuration)

        self.assertEqual(configuration.MBED_API_AUTH_TOKEN, "sometoken")


class TestDatabaseMode(TestCase):
    def test_returns_database_mode_set_in_env(self):
        for mode in configuration.DatabaseMode:
            with mock.patch.dict(os.environ, {"MBED_DATABASE_MODE": mode.name}), self.subTest(mode.name):
                reload(configuration)
                # Need to compare against enum object, as reload breaks regular comparison
                self.assertEqual(configuration.MBED_DATABASE_MODE, configuration.DatabaseMode[mode.name])

    def test_returns_default_database_mode_if_not_set_in_env(self):
        self.assertEqual(configuration.MBED_DATABASE_MODE, configuration.DatabaseMode.AUTO)

    @mock.patch.dict(os.environ, {"MBED_DATABASE_MODE": "FAST_PLEASE"})
    def test_invalid_mode_setting_falls_back_to_auto(self):
        reload(configuration)
        self.assertEqual(configuration.MBED_DATABASE_MODE, configuration.DatabaseMode.AUTO)
