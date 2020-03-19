from unittest import TestCase

from mbed_targets.mbed_tools import config_variables


class TestConfigVariables(TestCase):
    def test_expected_config_variables_are_exposed(self):
        exposed = set(variable.name for variable in config_variables)
        expected = {"MBED_DATABASE_MODE", "MBED_API_AUTH_TOKEN"}
        self.assertEqual(exposed, expected)
