"""Tests for `mbed_targets`."""

import json

from unittest import mock, TestCase

# Import from top level as this is the expected interface for users
from mbed_targets import MbedTarget, DatabaseMode, get_target
from mbed_targets.mbed_targets import MbedTargets, MbedTargetsOnline, MbedTargetsOffline, UnknownTarget, UnsupportedMode


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

    def test_hash_is_equal_to_hash_of_target_properties(self):
        tgt = _make_mbed_target(product_code="0100", platform_name="a", board_type="b")
        self.assertEqual(hash(tgt), hash(tgt.product_code) ^ hash(tgt.platform_name) ^ hash(tgt.board_type))

    def test_hash_and_eq_are_consistent(self):
        tgt_1 = _make_mbed_target(product_code="0100", board_type="a")
        tgt_2 = _make_mbed_target(product_code="0100", board_type="a")
        self.assertEqual(tgt_1, tgt_2)
        tgts = dict()
        tgts[tgt_1] = "test"
        self.assertEqual(tgts[tgt_2], "test")

    def test_repr_string_is_correctly_formed(self):
        tgt = _make_mbed_target(board_type="a", product_code="b", platform_name="c")
        self.assertEqual(repr(tgt), f"MbedTarget(board_type=a, product_code=b, name=c)")


@mock.patch("mbed_targets.mbed_targets.MbedTargetsOnline", autospec=True)
@mock.patch("mbed_targets.mbed_targets.MbedTargetsOffline", autospec=True)
class TestGetTarget(TestCase):
    def test_calls_correct_targets_class_for_mode(self, mocked_offline_targets, mocked_online_targets):
        test_data = {
            DatabaseMode.ONLINE: mocked_online_targets,
            DatabaseMode.OFFLINE: mocked_offline_targets,
        }
        for mode, mock_db in test_data.items():
            with self.subTest(mode):
                get_target("0100", mode)
                mock_db().get_target.assert_called_once_with("0100")

    def test_raises_error_when_invalid_mode_given(self, mocked_offline_targets, mocked_online_targets):
        with self.assertRaises(UnsupportedMode):
            get_target("", "")

    def test_auto_mode_calls_offline_targets_first(self, mocked_offline_targets, mocked_online_targets):
        product_code = "0100"
        mocked_offline_targets().get_target.return_value = _make_mbed_target(product_code=product_code)
        mocked_online_targets().get_target.return_value = _make_mbed_target(product_code=product_code)
        get_target(product_code, DatabaseMode.AUTO)
        mocked_online_targets().get_target.assert_not_called()
        mocked_offline_targets().get_target.assert_called_once_with(product_code)

    def test_falls_back_to_online_database_when_target_not_found(self, mocked_offline_targets, mocked_online_targets):
        product_code = "0100"
        mocked_offline_targets().get_target.side_effect = UnknownTarget
        mocked_online_targets().get_target.return_value = _make_mbed_target(product_code=product_code)
        get_target(product_code, DatabaseMode.AUTO)
        mocked_offline_targets().get_target.assert_called_once()
        mocked_online_targets().get_target.assert_called_once_with(product_code)


@mock.patch("mbed_targets._internal.target_database.get_offline_target_data")
class TestMbedTargets(TestCase):
    """Tests for the class `MbedTargets`."""

    def test_iteration_is_repeatable(self, mocked_get_target_data):
        """Test MbedTargets is an iterable and not an exhaustable iterator."""
        fake_target_data = _make_dummy_internal_target_data()
        mocked_get_target_data.return_value = fake_target_data
        mbed_targets = MbedTargetsOffline()
        tgts_a = [t for t in mbed_targets]
        tgts_b = [t for t in mbed_targets]
        self.assertEqual(tgts_a, tgts_b, "The lists are equal as mbed_targets was not exhausted on the first pass.")

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
        self.assertEqual(online_targets.json_dump(), json.dumps(online_target_data, indent=4))
        self.assertEqual(offline_targets.json_dump(), json.dumps(offline_target_data, indent=4))

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
        target_data = _make_dummy_internal_target_data()
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
        mbed_targets = MbedTargetsOffline()
        target = mbed_targets.get_target(expected_product_code)
        self.assertEqual(
            expected_product_code, target.product_code, "Target's product code should match the given product code."
        )

    def test_lookup_by_product_code_failure(self, mocked_get_target_data):
        """Check MbedTargets handles getting an unknown product code."""
        mocked_get_target_data.return_value = []
        mbed_targets = MbedTargetsOffline()
        with self.assertRaises(UnknownTarget):
            mbed_targets.get_target("unknown product code")

    def test_json_dump(self, mocked_get_target_data):
        fake_target_data = [
            {"attributes": {"product_code": "0200", "board": "test"}},
            {"attributes": {"product_code": "0100", "board": "test"}},
        ]
        mocked_get_target_data.return_value = fake_target_data

        mbed_targets = MbedTargetsOffline()
        json_str = mbed_targets.json_dump()
        self.assertEqual(
            json.loads(json_str), fake_target_data, "Deserialised JSON string should match original target data"
        )

    @mock.patch("mbed_targets._internal.target_database.get_online_target_data")
    def test_subtracting_targets_takes_difference_non_symmetric(
        self, mocked_online_target_data, mocked_offline_target_data
    ):
        tgt_data_off = _make_dummy_internal_target_data()
        tgt_data_on = _make_dummy_internal_target_data()
        tgt_data_off.pop()
        mocked_offline_target_data.return_value = tgt_data_off
        mocked_online_target_data.return_value = tgt_data_on
        tgts_off = MbedTargetsOffline()
        tgts_on = MbedTargetsOnline()
        diff_base_on = tgts_on - tgts_off
        diff_base_off = tgts_off - tgts_on
        self.assertEqual(len(diff_base_on), 1)
        self.assertEqual(len(diff_base_off), 0)

    def test_subtracting_targets_returns_targets_instance(self, mocked_offline_target_data):
        mocked_offline_target_data.return_value = _make_dummy_internal_target_data()
        tgts_one = MbedTargetsOffline()
        tgts_two = MbedTargetsOffline()
        self.assertTrue(isinstance(tgts_one - tgts_two, MbedTargets))

    def test_difference_operator_raises_for_non_targets_instance(self, mocked_offline_target_data):
        mocked_offline_target_data.return_value = _make_dummy_internal_target_data()
        tgts = MbedTargetsOffline()
        with self.assertRaises(TypeError):
            tgts - 1
