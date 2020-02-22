"""Tests for `mbed_targets`."""

import json

from unittest import mock, TestCase

# Import from top level as this is the expected interface for users
from mbed_targets import MbedTarget, get_targets, DatabaseMode, UnknownTarget, UnsupportedMode
from mbed_targets.mbed_targets import MbedTargetsOnline, MbedTargetsOffline


def _make_mbed_target(board_type=None, platform_name=None, mbed_os_support=None, mbed_enabled=None, product_code=None):
    return MbedTarget(
        {
            "attributes": dict(
                board_type=board_type,
                product_code=product_code,
                name=platform_name,
                features=dict(mbed_os_support=mbed_os_support, mbed_enabled=mbed_enabled),
            )
        }
    )


def _make_dummy_internal_target_data():
    return [dict(attributes=dict(board_type=str(i), platform_name=str(i), product_code=str(i))) for i in range(10)]


class TestMbedTarget(TestCase):
    """Tests for the class `MbedTarget`."""

    def test_nominal_database_entry(self):
        """Given database entry data, an MbedTarget is generated with the correct information."""
        mbed_target = _make_mbed_target(
            mbed_os_support=["Mbed OS 5.15"],
            mbed_enabled=["Basic"],
            board_type="B_1",
            platform_name="Board 1",
            product_code="P1",
        )
        self.assertEqual("B_1", mbed_target.board_type)
        self.assertEqual("Board 1", mbed_target.platform_name)
        self.assertEqual(("Mbed OS 5.15",), mbed_target.mbed_os_support)
        self.assertEqual(("Basic",), mbed_target.mbed_enabled)
        self.assertEqual("P1", mbed_target.product_code)

    def test_empty_database_entry(self):
        """Given no data, and MbedTarget is created with no information."""
        mbed_target = MbedTarget({})
        self.assertEqual("", mbed_target.board_type)
        self.assertEqual("", mbed_target.platform_name)
        self.assertEqual((), mbed_target.mbed_os_support)
        self.assertEqual((), mbed_target.mbed_enabled)
        self.assertEqual("", mbed_target.product_code)

    def test_compares_equal_when_product_codes_match(self):
        target_one = _make_mbed_target(product_code="0001")
        target_two = _make_mbed_target(product_code="0001")
        self.assertTrue(target_one == target_two)

    def test_compares_not_equal_when_product_codes_unmatched(self):
        target_one = _make_mbed_target(product_code="0001")
        target_two = _make_mbed_target(product_code="0000")
        self.assertTrue(target_one != target_two)

    def test_cannot_compare_with_non_mbed_target_instance(self):
        target = _make_mbed_target(product_code="1000")
        self.assertFalse(target == "1000")

    def test_hash_is_equal_to_hash_of_product_code(self):
        tgt = _make_mbed_target(product_code="0100")
        self.assertEqual(tgt.__hash__(), hash(tgt.product_code))

    def test_compare_equal_hashes_equal(self):
        tgt_1 = _make_mbed_target(product_code="0100", board_type="a")
        tgt_2 = _make_mbed_target(product_code="0100", board_type="b")
        tgts = dict()
        tgts[tgt_1] = "test"
        self.assertEqual(tgts[tgt_2], "test")


class TestMbedTargetsFactory(TestCase):
    @mock.patch("mbed_targets.mbed_targets.MbedTargetsOnline", autospec=True)
    @mock.patch("mbed_targets.mbed_targets.MbedTargetsOffline", autospec=True)
    def test_returns_correct_targets_class_for_mode(self, mocked_online_targets, mocked_offline_targets):
        tgts_online = get_targets(DatabaseMode.ONLINE)
        tgts_offline = get_targets(DatabaseMode.OFFLINE)
        self.assertTrue(isinstance(tgts_online, MbedTargetsOnline))
        self.assertTrue(isinstance(tgts_offline, MbedTargetsOffline))

    def test_raises_error_when_invalid_mode_given(self):
        with self.assertRaises(UnsupportedMode):
            get_targets("something")


@mock.patch("mbed_targets._internal.target_database.get_offline_target_data")
class TestMbedTargets(TestCase):
    """Tests for the class `MbedTargets`."""

    def test_iterator(self, mocked_get_target_data):
        """An MbedTargets object is iterable and on each iteration returns the next target data in the list."""
        # Mock the return value of the target data with something that can be validated in a iterator
        fake_target_data = [{"count": 0}, {"count": 1}, {"count": 2}]
        mocked_get_target_data.return_value = fake_target_data

        # Create an instance of the class which is to be used as the iterator
        mbed_targets = get_targets(DatabaseMode.OFFLINE)

        mbed_target_list = [mbed_target._target_entry for mbed_target in mbed_targets]
        self.assertEqual(fake_target_data, mbed_target_list, "The list comprehension should match the fake data")

        # Check the iteration is repeatable
        mbed_target_list = [mbed_target._target_entry for mbed_target in mbed_targets]
        self.assertEqual(fake_target_data, mbed_target_list, "The list comprehension should match the fake data")

        # Iterate through the list checking the value returned matched the enumerated count
        for count, target in enumerate(mbed_targets):
            self.assertEqual(count, target._target_entry["count"], "Iterator count values should match")

    @mock.patch("mbed_targets._internal.target_database.get_online_target_data")
    def test_subclass_internal_data_is_unique_per_instance(self, mocked_online_target_data, mocked_offline_target_data):
        """Test the internal target data is overriden in each subclass initaliser."""
        offline_target_data = _make_dummy_internal_target_data()
        online_target_data = [
            dict(attributes=dict(board_type=str(i), platform_name=str(i), product_code=str(i))) for i in "abcdefghij"
        ]
        mocked_offline_target_data.return_value = offline_target_data
        mocked_online_target_data.return_value = online_target_data
        online_targets = MbedTargetsOnline()
        offline_targets = MbedTargetsOffline()
        self.assertEqual(online_targets._target_data, online_target_data)
        self.assertEqual(offline_targets._target_data, offline_target_data)

    def test_mbed_target_found_in_targets_membership_test(self, mocked_get_target_data):
        """Tests the __contains__ method was implemented correctly."""
        target_data = _make_dummy_internal_target_data()
        mocked_get_target_data.return_value = target_data
        mbed_targets = MbedTargetsOffline()
        for target in mbed_targets:
            self.assertIn(target, mbed_targets)

    def test_membership_test_returns_false_for_non_mbed_target(self, mocked_get_target_data):
        """Tests the __contains__ method was implemented correctly."""
        target_data = _make_dummy_internal_target_data()
        mocked_get_target_data.return_value = target_data
        mbed_targets = MbedTargetsOffline()
        self.assertFalse("a" in mbed_targets)

    def test_len_targets(self, mocked_get_target_data):
        """Test len(MbedTargets()) matches len(target_database)."""
        target_data = [
            _make_mbed_target(board_type=str(i), platform_name=str(i), product_code=str(i)) for i in range(10)
        ]
        mocked_get_target_data.return_value = target_data
        self.assertEqual(len(MbedTargetsOffline()), len(target_data))

    def test_lookup_by_product_code_success(self, mocked_get_target_data):
        """Check an MbedTarget can be looked up by its product code."""
        fake_target_data = [
            {"attributes": {"product_code": "0200", "board": "test"}},
            {"attributes": {"product_code": "0100", "board": "test"}},
        ]
        mocked_get_target_data.return_value = fake_target_data
        expected_product_code = "0100"
        mbed_targets = get_targets(DatabaseMode.OFFLINE)
        target = mbed_targets.get_target(expected_product_code)
        self.assertEqual(
            expected_product_code, target.product_code, "Target's product code should match the given product code."
        )

    def test_lookup_by_product_code_failure(self, mocked_get_target_data):
        """Check MbedTargets handles getting an unknown product code."""
        mocked_get_target_data.return_value = []
        mbed_targets = get_targets(DatabaseMode.OFFLINE)
        with self.assertRaises(UnknownTarget):
            mbed_targets.get_target("unknown product code")

    def test_json_dump(self, mocked_get_target_data):
        fake_target_data = [
            {"attributes": {"product_code": "0200", "board": "test"}},
            {"attributes": {"product_code": "0100", "board": "test"}},
        ]
        mocked_get_target_data.return_value = fake_target_data

        mbed_targets = get_targets(DatabaseMode.OFFLINE)
        json_str = mbed_targets.json_dump()
        self.assertEqual(
            json.loads(json_str), fake_target_data, "Deserialised JSON string should match original target data"
        )
