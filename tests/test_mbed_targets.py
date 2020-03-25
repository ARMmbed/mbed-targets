#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Tests for `mbed_targets.mbed_targets`."""

import json
from dataclasses import asdict
from unittest import mock, TestCase

from mbed_targets import MbedTarget
from mbed_targets.exceptions import UnknownTarget
from mbed_targets.mbed_targets import MbedTargets
from tests.factories import make_dummy_internal_target_data


@mock.patch("mbed_targets._internal.target_database.get_online_target_data")
class TestMbedTargets(TestCase):
    """Tests for the class `MbedTargets`."""

    def test_iteration_is_repeatable(self, mocked_get_target_data):
        """Test MbedTargets is an iterable and not an exhaustable iterator."""
        fake_target_data = make_dummy_internal_target_data()
        mocked_get_target_data.return_value = fake_target_data

        mbed_targets = MbedTargets.from_online_database()
        tgts_a = [t for t in mbed_targets]
        tgts_b = [t for t in mbed_targets]

        self.assertEqual(tgts_a, tgts_b, "The lists are equal as mbed_targets was not exhausted on the first pass.")

    def test_mbed_target_found_in_targets_membership_test(self, mocked_get_target_data):
        """Tests the __contains__ method was implemented correctly."""
        target_data = make_dummy_internal_target_data()
        mocked_get_target_data.return_value = target_data

        mbed_targets = MbedTargets.from_online_database()
        target, *_ = mbed_targets

        self.assertIn(target, mbed_targets)

    def test_membership_test_returns_false_for_non_mbed_target(self, mocked_get_target_data):
        """Tests the __contains__ method was implemented correctly."""
        target_data = make_dummy_internal_target_data()
        mocked_get_target_data.return_value = target_data

        mbed_targets = MbedTargets.from_online_database()

        self.assertFalse("a" in mbed_targets)

    def test_len_targets(self, mocked_get_target_data):
        """Test len(MbedTargets()) matches len(target_database)."""
        target_data = make_dummy_internal_target_data()
        mocked_get_target_data.return_value = target_data

        self.assertEqual(len(MbedTargets.from_online_database()), len(target_data))

    def test_get_target_success(self, mocked_get_target_data):
        """Check an MbedTarget can be looked up by arbitrary parameters."""
        fake_target_data = [
            {"attributes": {"product_code": "0300"}},
            {"attributes": {"product_code": "0200"}},
            {"attributes": {"product_code": "0100"}},
        ]
        mocked_get_target_data.return_value = fake_target_data

        mbed_targets = MbedTargets.from_online_database()
        target = mbed_targets.get_target(lambda target: target.product_code == "0100")

        self.assertEqual(target.product_code, "0100", "Target's product code should match the given product code.")

    def test_get_target_failure(self, mocked_get_target_data):
        """Check MbedTargets handles queries without a match."""
        mocked_get_target_data.return_value = []

        mbed_targets = MbedTargets.from_online_database()

        with self.assertRaises(UnknownTarget):
            mbed_targets.get_target(lambda target: target.product_code == "unknown")

    @mock.patch("mbed_targets._internal.target_database.get_offline_target_data")
    def test_json_dump_from_raw_and_fitered_data(self, mocked_get_offline_target_data, mocked_get_online_target_data):
        raw_target_data = [
            {"attributes": {"product_code": "0200", "board": "test"}},
            {"attributes": {"product_code": "0100", "board": "test2"}},
        ]
        mocked_get_online_target_data.return_value = raw_target_data

        targets = [MbedTarget.from_online_target_entry(t) for t in raw_target_data]
        filtered_target_data = [asdict(target) for target in targets]
        mocked_get_offline_target_data.return_value = filtered_target_data

        # MbedTargets.from_online_database handles "raw" target entries from the online db
        mbed_targets = MbedTargets.from_online_database()
        json_str_from_raw = mbed_targets.json_dump()
        t1_raw, t2_raw = mbed_targets

        # MbedTargets.from_offline_database expects the data to have been "filtered" through the MbedTargets interface
        mbed_targets_offline = MbedTargets.from_offline_database()
        json_str_from_filtered = mbed_targets_offline.json_dump()
        t1_filt, t2_filt = mbed_targets_offline

        self.assertEqual(
            json_str_from_raw,
            json.dumps([asdict(t1_raw), asdict(t2_raw)], indent=4),
            "JSON string should match serialised target __dict__.",
        )

        self.assertEqual(json_str_from_filtered, json.dumps([t1_filt.__dict__, t2_filt.__dict__], indent=4))
