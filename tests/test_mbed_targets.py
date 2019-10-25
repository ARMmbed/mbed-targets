"""Tests for `mbed_targets`."""

import unittest

# Unit under test
import mbed_targets




class TestMbedTargets(unittest.TestCase):

    def test_init(self):
        instance = mbed_targets.MbedTargets()
        self.assertTrue(instance)

