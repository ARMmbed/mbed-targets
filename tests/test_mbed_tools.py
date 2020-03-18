import pdoc
from unittest import TestCase

from mbed_targets.mbed_tools import config_variables


class TestConfigVariables(TestCase):
    def test_expected_config_variables_are_exposed(self):
        exposed = set(variable.name for variable in config_variables)
        expected = set(variable.name for variable in pdoc.Module("mbed_targets.config").variables())
        self.assertEqual(exposed, expected)
