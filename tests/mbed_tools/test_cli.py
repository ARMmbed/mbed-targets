"""Tests for `mbed_targets.mbed_tools.cli`."""
from unittest import TestCase

from mbed_targets.mbed_tools.list_all import list_all
from mbed_targets.mbed_tools.cli import cli


class TestCli(TestCase):
    """Tests for the entry point cli."""

    def test_exposes_list_all_as_entry_point(self):
        """Expose cli as list_all."""
        self.assertEqual(cli, list_all)
