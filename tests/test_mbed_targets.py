#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Tests for `mbed_targets`."""

import json
from dataclasses import asdict
from unittest import mock, TestCase

# Import from top level as this is the expected interface for users
from mbed_targets import MbedTarget, get_target_by_product_code, get_target_by_online_id
from mbed_targets.config import config
from mbed_targets.exceptions import UnknownTarget, UnsupportedMode
from mbed_targets.mbed_targets import (
    MbedTargets,
    _DatabaseMode,
    _get_database_mode,
    _get_target,
    _target_matches_query,
)
from tests.factories import make_mbed_target, make_dummy_internal_target_data


@mock.patch("mbed_targets.mbed_targets.MbedTargets", autospec=True)
class TestGetTarget(TestCase):
    def test_calls_correct_targets_class_for_mode(self, mocked_targets):
        test_data = {
            _DatabaseMode.ONLINE: mocked_targets.from_online_database,
            _DatabaseMode.OFFLINE: mocked_targets.from_offline_database,
        }

        for mode, mock_db in test_data.items():
            with self.subTest(mode):
                with mock.patch("mbed_targets.mbed_targets.config", spec_set=config) as mocked_config:
                    mocked_config.MBED_DATABASE_MODE = mode.name
                    _get_target({"product_code": "0100"})
                    mock_db().get_target.assert_called_once_with(product_code="0100")

    @mock.patch("mbed_targets.mbed_targets.config", spec_set=config)
    def test_auto_mode_calls_offline_targets_first(self, config, mocked_targets):
        product_code = "0100"
        config.MBED_DATABASE_MODE = "AUTO"
        mocked_targets.from_offline_database().get_target.return_value = make_mbed_target(product_code=product_code)
        mocked_targets.from_online_database().get_target.return_value = make_mbed_target(product_code=product_code)

        _get_target({"product_code": product_code})

        mocked_targets.from_online_database().get_target.assert_not_called()
        mocked_targets.from_offline_database().get_target.assert_called_once_with(product_code=product_code)

    @mock.patch("mbed_targets.mbed_targets.config", spec_set=config)
    def test_falls_back_to_online_database_when_target_not_found(self, config, mocked_targets):
        product_code = "0100"
        config.MBED_DATABASE_MODE = "AUTO"
        mocked_targets.from_offline_database().get_target.side_effect = UnknownTarget
        mocked_targets.from_online_database().get_target.return_value = make_mbed_target(product_code=product_code)

        _get_target({"product_code": product_code})

        mocked_targets.from_offline_database().get_target.assert_called_once()
        mocked_targets.from_online_database().get_target.assert_called_once_with(product_code=product_code)


class TestGetTargetByProductCode(TestCase):
    @mock.patch("mbed_targets.mbed_targets._get_target")
    def test_forwards_the_call_to_get_target(self, _get_target):
        product_code = "swag"
        subject = get_target_by_product_code(product_code)

        self.assertEqual(subject, _get_target.return_value)
        _get_target.assert_called_once_with({"product_code": product_code})


class TestGetTargetByOnlineId(TestCase):
    @mock.patch("mbed_targets.mbed_targets._get_target")
    def test_forwards_the_call_to_get_target(self, _get_target):
        slug = "SOME_SLUG"
        target_type = "platform"
        subject = get_target_by_online_id(slug=slug, target_type=target_type)

        self.assertEqual(subject, _get_target.return_value)
        _get_target.assert_called_once_with({"slug": slug, "target_type": target_type})


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
            {"attributes": {"product_code": "0300", "target_type": "module"}},
            {"attributes": {"product_code": "0200", "target_type": "platform"}},
            {"attributes": {"product_code": "0100", "target_type": "platform"}},
        ]
        mocked_get_target_data.return_value = fake_target_data

        mbed_targets = MbedTargets.from_online_database()
        target = mbed_targets.get_target(product_code="0100", target_type="platform")

        self.assertEqual(target.product_code, "0100", "Target's product code should match the given product code.")
        self.assertEqual(target.target_type, "platform", "Target's board type should match the given product type.")

    def test_get_target_failure(self, mocked_get_target_data):
        """Check MbedTargets handles queries without a match."""
        mocked_get_target_data.return_value = []

        mbed_targets = MbedTargets.from_online_database()

        with self.assertRaises(UnknownTarget):
            mbed_targets.get_target(board_name="unknown product code")

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


class TestTargetMatchesQuery(TestCase):
    def test_matches_target_using_query_dict(self):
        mbed_target = make_mbed_target(product_code="0123")
        self.assertTrue(_target_matches_query(mbed_target, {"product_code": "0123"}))

    def test_strings_are_compared_case_insensitively(self):
        mbed_target = make_mbed_target(slug="FOO-bar-123")
        self.assertTrue(_target_matches_query(mbed_target, {"slug": "foo-BAR-123"}))


@mock.patch("mbed_targets.mbed_targets.config", spec_set=config)
class TestGetDatabaseMode(TestCase):
    def test_returns_configured_database_mode(self, config):
        config.MBED_DATABASE_MODE = "OFFLINE"
        self.assertEqual(_get_database_mode(), _DatabaseMode.OFFLINE)

    def test_raises_when_configuration_is_not_supported(self, config):
        config.MBED_DATABASE_MODE = "NOT_VALID"
        with self.assertRaises(UnsupportedMode):
            _get_database_mode()
