#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Tests for `mbed_targets.get_target`."""
from unittest import mock, TestCase

# Import from top level as this is the expected interface for users
from mbed_targets import get_target_by_online_id, get_target_by_product_code
from mbed_targets.get_target import (
    _DatabaseMode,
    _get_database_mode,
    get_target,
)
from mbed_targets.config import config
from mbed_targets.exceptions import UnknownTarget, UnsupportedMode
from tests.factories import make_mbed_target


@mock.patch("mbed_targets.get_target.MbedTargets", autospec=True)
@mock.patch("mbed_targets.get_target.config", spec_set=config)
class TestGetTarget(TestCase):
    def test_online_mode(self, config, mocked_targets):
        config.MBED_DATABASE_MODE = "ONLINE"
        fn = mock.Mock()

        subject = get_target(fn)

        self.assertEqual(subject, mocked_targets.from_online_database().get_target.return_value)
        mocked_targets.from_online_database().get_target.assert_called_once_with(fn)

    def test_offline_mode(self, config, mocked_targets):
        config.MBED_DATABASE_MODE = "OFFLINE"
        fn = mock.Mock()

        subject = get_target(fn)

        self.assertEqual(subject, mocked_targets.from_offline_database().get_target.return_value)
        mocked_targets.from_offline_database().get_target.assert_called_once_with(fn)

    def test_auto_mode_calls_offline_targets_first(self, config, mocked_targets):
        config.MBED_DATABASE_MODE = "AUTO"
        fn = mock.Mock()

        subject = get_target(fn)

        self.assertEqual(subject, mocked_targets.from_offline_database().get_target.return_value)
        mocked_targets.from_online_database().get_target.assert_not_called()
        mocked_targets.from_offline_database().get_target.assert_called_once_with(fn)

    def test_auto_mode_falls_back_to_online_database_when_target_not_found(self, config, mocked_targets):
        config.MBED_DATABASE_MODE = "AUTO"
        mocked_targets.from_offline_database().get_target.side_effect = UnknownTarget
        fn = mock.Mock()

        subject = get_target(fn)

        self.assertEqual(subject, mocked_targets.from_online_database().get_target.return_value)
        mocked_targets.from_offline_database().get_target.assert_called_once_with(fn)
        mocked_targets.from_online_database().get_target.assert_called_once_with(fn)


class TestGetTargetByProductCode(TestCase):
    @mock.patch("mbed_targets.get_target.get_target")
    def test_matches_targets_by_product_code(self, get_target):
        product_code = "swag"

        self.assertEqual(get_target_by_product_code(product_code), get_target.return_value)

        # Test callable matches correct targets
        fn = get_target.call_args[0][0]

        matching_target = make_mbed_target(product_code=product_code)
        not_matching_target = make_mbed_target(product_code="whatever")

        self.assertTrue(fn(matching_target))
        self.assertFalse(fn(not_matching_target))


class TestGetTargetByOnlineId(TestCase):
    @mock.patch("mbed_targets.get_target.get_target")
    def test_matches_targets_by_online_id(self, get_target):
        target_type = "platform"

        self.assertEqual(get_target_by_online_id(slug="slug", target_type=target_type), get_target.return_value)

        # Test callable matches correct targets
        fn = get_target.call_args[0][0]

        matching_target_1 = make_mbed_target(target_type=target_type, slug="slug")
        matching_target_2 = make_mbed_target(target_type=target_type, slug="SlUg")
        not_matching_target = make_mbed_target(target_type=target_type, slug="whatever")

        self.assertTrue(fn(matching_target_1))
        self.assertTrue(fn(matching_target_2))
        self.assertFalse(fn(not_matching_target))


@mock.patch("mbed_targets.get_target.config", spec_set=config)
class TestGetDatabaseMode(TestCase):
    def test_returns_configured_database_mode(self, config):
        config.MBED_DATABASE_MODE = "OFFLINE"
        self.assertEqual(_get_database_mode(), _DatabaseMode.OFFLINE)

    def test_raises_when_configuration_is_not_supported(self, config):
        config.MBED_DATABASE_MODE = "NOT_VALID"
        with self.assertRaises(UnsupportedMode):
            _get_database_mode()
