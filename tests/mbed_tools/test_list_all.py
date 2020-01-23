"""Tests for `mbed_targets.mbed_tools.list_all`."""
from unittest import mock, TestCase
from click.testing import CliRunner

from mbed_targets.mbed_tools.list_all import list_all
from mbed_targets.mbed_targets import MbedTargets, MbedTarget


class TestListAll(TestCase):
    """Tests for list_all cli command."""

    @mock.patch("mbed_targets.mbed_tools.list_all.MbedTargets", spec_set=MbedTargets)
    def test_outputs_target_data(self, MbedTargets):
        """Invoking a command lists board type for all targets."""
        MbedTargets.return_value = [
            mock.Mock(spec_set=MbedTarget, board_type="foo"),
            mock.Mock(spec_set=MbedTarget, board_type="bar"),
        ]

        runner = CliRunner()
        result = runner.invoke(list_all)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "foo\nbar\n")
