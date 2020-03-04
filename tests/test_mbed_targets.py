"""Tests for `mbed_targets`."""

import json

from unittest import mock, TestCase

# Import from top level as this is the expected interface for users
from mbed_targets import MbedTarget, DatabaseMode, get_target_by_product_code, get_target_by_online_id
from mbed_targets.mbed_targets import MbedTargets, UnknownTarget, UnsupportedMode, _get_target, _target_matches_query


def _make_mbed_target(
    board_type=None, board_name=None, mbed_os_support=None, mbed_enabled=None, product_code=None, slug=None
):
    return MbedTarget(
        {
            "attributes": dict(
                board_type=board_type,
                product_code=product_code,
                name=board_name,
                slug=slug,
                features=dict(mbed_os_support=mbed_os_support, mbed_enabled=mbed_enabled),
            )
        }
    )


def _make_dummy_internal_target_data():
    return [dict(attributes=dict(board_type=str(i), board_name=str(i), product_code=str(i))) for i in range(10)]


class TestMbedTarget(TestCase):
    """Tests for the class `MbedTarget`."""

    def test_nominal_database_entry(self):
        """Given database entry data, an MbedTarget is generated with the correct information."""
        mbed_target = _make_mbed_target(
            mbed_os_support=["Mbed OS 5.15"],
            mbed_enabled=["Basic"],
            board_type="B_1",
            board_name="Board 1",
            product_code="P1",
            slug="Le Slug",
        )

        self.assertEqual("B_1", mbed_target.board_type)
        self.assertEqual("Board 1", mbed_target.board_name)
        self.assertEqual(("Mbed OS 5.15",), mbed_target.mbed_os_support)
        self.assertEqual(("Basic",), mbed_target.mbed_enabled)
        self.assertEqual("P1", mbed_target.product_code)
        self.assertEqual("Le Slug", mbed_target.slug)
        self.assertEqual((), mbed_target.build_variant)

    def test_build_variant_hack(self):
        mbed_target = _make_mbed_target(board_type="lpc55s69")

        self.assertEqual(mbed_target.build_variant, ("S", "NS"))

    def test_empty_database_entry(self):
        """Given no data, and MbedTarget is created with no information."""
        mbed_target = MbedTarget({})

        self.assertEqual("", mbed_target.board_type)
        self.assertEqual("", mbed_target.board_name)
        self.assertEqual((), mbed_target.mbed_os_support)
        self.assertEqual((), mbed_target.mbed_enabled)
        self.assertEqual("", mbed_target.product_code)
        self.assertEqual("", mbed_target.slug)

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
        tgt = _make_mbed_target(product_code="0100", board_name="a", board_type="b", slug="c")

        self.assertEqual(
            hash(tgt), hash(tgt.product_code) ^ hash(tgt.board_name) ^ hash(tgt.board_type) ^ hash(tgt.slug)
        )

    def test_hash_and_eq_are_consistent(self):
        tgt_1 = _make_mbed_target(product_code="0100", board_type="a")
        tgt_2 = _make_mbed_target(product_code="0100", board_type="a")
        tgts = dict()
        tgts[tgt_1] = "test"

        self.assertEqual(tgt_1, tgt_2)
        self.assertEqual(tgts[tgt_2], "test")

    def test_repr_string_is_correctly_formed(self):
        tgt = _make_mbed_target(board_type="a", product_code="b", board_name="c", slug="d")

        self.assertEqual(repr(tgt), f"MbedTarget(board_type=a, product_code=b, name=c, slug=d)")

    def test_compares_lt_target_with_greater_product_code(self):
        tgt_a = _make_mbed_target(board_type="a", product_code="01", board_name="c")
        tgt_b = _make_mbed_target(board_type="0", product_code="02", board_name="cd")

        self.assertEqual(tgt_a < tgt_b, True)

    def test_lt_raises_type_error_with_non_mbed_target(self):
        tgt_a = _make_mbed_target(board_type="a", product_code="00", board_name="ab")
        other = "a"

        with self.assertRaises(TypeError):
            tgt_a < other


@mock.patch("mbed_targets.mbed_targets.MbedTargets", autospec=True)
class TestGetTarget(TestCase):
    def test_calls_correct_targets_class_for_mode(self, mocked_targets):
        test_data = {
            DatabaseMode.ONLINE: mocked_targets.from_online_database,
            DatabaseMode.OFFLINE: mocked_targets.from_offline_database,
        }

        for mode, mock_db in test_data.items():
            with self.subTest(mode):
                _get_target({"product_code": "0100"}, mode)

                mock_db().get_target.assert_called_once_with(product_code="0100")

    def test_raises_error_when_invalid_mode_given(self, mocked_targets):
        with self.assertRaises(UnsupportedMode):
            _get_target("", "")

    def test_auto_mode_calls_offline_targets_first(self, mocked_targets):
        product_code = "0100"
        mocked_targets.from_offline_database().get_target.return_value = _make_mbed_target(product_code=product_code)
        mocked_targets.from_online_database().get_target.return_value = _make_mbed_target(product_code=product_code)

        _get_target({"product_code": product_code}, DatabaseMode.AUTO)

        mocked_targets.from_online_database().get_target.assert_not_called()
        mocked_targets.from_offline_database().get_target.assert_called_once_with(product_code=product_code)

    def test_falls_back_to_online_database_when_target_not_found(self, mocked_targets):
        product_code = "0100"
        mocked_targets.from_offline_database().get_target.side_effect = UnknownTarget
        mocked_targets.from_online_database().get_target.return_value = _make_mbed_target(product_code=product_code)

        _get_target({"product_code": product_code}, DatabaseMode.AUTO)

        mocked_targets.from_offline_database().get_target.assert_called_once()
        mocked_targets.from_online_database().get_target.assert_called_once_with(product_code=product_code)


class TestGetTargetByProductCode(TestCase):
    @mock.patch("mbed_targets.mbed_targets._get_target")
    def test_forwards_the_call_to_get_target(self, _get_target):
        product_code = "swag"
        mode = DatabaseMode.OFFLINE
        subject = get_target_by_product_code(product_code, mode=mode)

        self.assertEqual(subject, _get_target.return_value)
        _get_target.assert_called_once_with({"product_code": product_code}, mode=mode)


class TestGetTargetByOnlineId(TestCase):
    @mock.patch("mbed_targets.mbed_targets._get_target")
    def test_forwards_the_call_to_get_target(self, _get_target):
        slug = "SOME_SLUG"
        board_type = "platform"
        mode = DatabaseMode.ONLINE
        subject = get_target_by_online_id(slug=slug, board_type=board_type, mode=mode)

        self.assertEqual(subject, _get_target.return_value)
        _get_target.assert_called_once_with({"slug": slug, "board_type": board_type}, mode=mode)


@mock.patch("mbed_targets._internal.target_database.get_offline_target_data")
class TestMbedTargets(TestCase):
    """Tests for the class `MbedTargets`."""

    def test_iteration_is_repeatable(self, mocked_get_target_data):
        """Test MbedTargets is an iterable and not an exhaustable iterator."""
        fake_target_data = _make_dummy_internal_target_data()
        mocked_get_target_data.return_value = fake_target_data

        mbed_targets = MbedTargets.from_offline_database()
        tgts_a = [t for t in mbed_targets]
        tgts_b = [t for t in mbed_targets]

        self.assertEqual(tgts_a, tgts_b, "The lists are equal as mbed_targets was not exhausted on the first pass.")

    def test_mbed_target_found_in_targets_membership_test(self, mocked_get_target_data):
        """Tests the __contains__ method was implemented correctly."""
        target_data = _make_dummy_internal_target_data()
        mocked_get_target_data.return_value = target_data

        mbed_targets = MbedTargets.from_offline_database()
        target, *_ = mbed_targets

        self.assertIn(target, mbed_targets)

    def test_membership_test_returns_false_for_non_mbed_target(self, mocked_get_target_data):
        """Tests the __contains__ method was implemented correctly."""
        target_data = _make_dummy_internal_target_data()
        mocked_get_target_data.return_value = target_data

        mbed_targets = MbedTargets.from_offline_database()

        self.assertFalse("a" in mbed_targets)

    def test_len_targets(self, mocked_get_target_data):
        """Test len(MbedTargets()) matches len(target_database)."""
        target_data = _make_dummy_internal_target_data()
        mocked_get_target_data.return_value = target_data

        self.assertEqual(len(MbedTargets.from_offline_database()), len(target_data))

    def test_get_target_success(self, mocked_get_target_data):
        """Check an MbedTarget can be looked up by arbitrary parameters."""
        fake_target_data = [
            {"attributes": {"product_code": "0300", "board_type": "module"}},
            {"attributes": {"product_code": "0200", "board_type": "platform"}},
            {"attributes": {"product_code": "0100", "board_type": "platform"}},
        ]
        mocked_get_target_data.return_value = fake_target_data

        mbed_targets = MbedTargets.from_offline_database()
        target = mbed_targets.get_target(product_code="0100", board_type="platform")

        self.assertEqual(target.product_code, "0100", "Target's product code should match the given product code.")
        self.assertEqual(target.board_type, "platform", "Target's board type should match the given product type.")

    def test_get_target_failure(self, mocked_get_target_data):
        """Check MbedTargets handles queries without a match."""
        mocked_get_target_data.return_value = []

        mbed_targets = MbedTargets.from_offline_database()

        with self.assertRaises(UnknownTarget):
            mbed_targets.get_target(board_name="unknown product code")

    def test_json_dump(self, mocked_get_target_data):
        fake_target_data = [
            {"attributes": {"product_code": "0200", "board": "test"}},
            {"attributes": {"product_code": "0100", "board": "test"}},
        ]
        mocked_get_target_data.return_value = fake_target_data

        mbed_targets = MbedTargets.from_offline_database()
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

        tgts_off = MbedTargets.from_offline_database()
        tgts_on = MbedTargets.from_online_database()
        diff_base_on = tgts_on - tgts_off
        diff_base_off = tgts_off - tgts_on

        self.assertEqual(len(diff_base_on), 1)
        self.assertEqual(len(diff_base_off), 0)

    def test_subtracting_targets_returns_targets_instance(self, mocked_offline_target_data):
        mocked_offline_target_data.return_value = _make_dummy_internal_target_data()

        tgts_one = MbedTargets.from_offline_database()
        tgts_two = MbedTargets.from_offline_database()

        self.assertTrue(isinstance(tgts_one - tgts_two, MbedTargets))

    def test_difference_operator_raises_for_non_targets_instance(self, mocked_offline_target_data):
        mocked_offline_target_data.return_value = _make_dummy_internal_target_data()

        tgts = MbedTargets.from_offline_database()

        with self.assertRaises(TypeError):
            tgts - 1


class TestTargetMatchesQuery(TestCase):
    def test_matches_target_using_query_dict(self):
        mbed_target = _make_mbed_target(product_code="0123")
        self.assertTrue(_target_matches_query(mbed_target, {"product_code": "0123"}))

    def test_strings_are_compared_case_insensitively(self):
        mbed_target = _make_mbed_target(slug="FOO-bar-123")
        self.assertTrue(_target_matches_query(mbed_target, {"slug": "foo-BAR-123"}))
