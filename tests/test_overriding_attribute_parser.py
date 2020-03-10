"""Tests for parsing the attributes for targets in targets.json that override."""
from unittest import TestCase, mock

from mbed_targets._internal.target_attribute_hierarchy_parsers.overriding_attribute_parser import (
    get_overriding_attributes_for_target,
    _targets_override_hierarchy,
    _determine_overridden_attributes,
)
from mbed_targets._internal.target_attribute_hierarchy_parsers.accumulating_attribute_parser import (
    ALL_ACCUMULATING_ATTRIBUTES,
)


class TestGetOverridingAttributes(TestCase):
    @mock.patch(
        "mbed_targets._internal.target_attribute_hierarchy_parsers."
        "overriding_attribute_parser._targets_override_hierarchy"
    )
    @mock.patch(
        "mbed_targets._internal.target_attribute_hierarchy_parsers."
        "overriding_attribute_parser._determine_overridden_attributes"
    )
    def test_correctly_calls(self, _determine_overridden_attributes, _targets_override_hierarchy):
        target_name = "Target_Name"
        all_targets_data = {target_name: {"attribute_1": ["something"]}}
        result = get_overriding_attributes_for_target(all_targets_data, target_name)

        _targets_override_hierarchy.assert_called_once_with(all_targets_data, target_name)
        _determine_overridden_attributes.assert_called_once_with(_targets_override_hierarchy.return_value)
        self.assertEqual(result, _determine_overridden_attributes.return_value)


class TestParseHierarchy(TestCase):
    def test_overwrite_hierarchy_single_inheritance(self):
        all_targets_data = {
            "D": {"attribute_1": ["some things"]},
            "C": {"inherits": ["D"], "attribute_2": "something else"},
            "B": {},
            "A": {"inherits": ["C"], "attribute_3": ["even more things"]},
        }
        result = _targets_override_hierarchy(all_targets_data, "A")

        self.assertEqual(result, [all_targets_data["A"], all_targets_data["C"], all_targets_data["D"]])

    def test_overwrite_hierarchy_multiple_inheritance(self):
        all_targets_data = {
            "F": {"attribute_1": "some thing"},
            "E": {"attribute_2": "some other thing"},
            "D": {"inherits": ["F"]},
            "C": {"inherits": ["E"]},
            "B": {"inherits": ["C", "D"]},
            "A": {"inherits": ["B"]},
        }
        result = _targets_override_hierarchy(all_targets_data, "A")

        self.assertEqual(
            result,
            [
                all_targets_data["A"],
                all_targets_data["B"],
                all_targets_data["C"],
                all_targets_data["E"],
                all_targets_data["D"],
                all_targets_data["F"],
            ],
        )


class TestOverridingAttributes(TestCase):
    def test_determine_overwritten_attributes(self):
        override_order = [
            {"attribute_1": "1"},
            {"attribute_1": "I should be overridden", "attribute_2": "2"},
            {"attribute_3": "3"},
        ]
        expected_attributes = {"attribute_1": "1", "attribute_2": "2", "attribute_3": "3"}

        result = _determine_overridden_attributes(override_order)
        self.assertEqual(result, expected_attributes)

    def test_remove_accumulating_attributes(self):
        override_order = [
            {ALL_ACCUMULATING_ATTRIBUTES[0]: "1"},
            {"attribute": "Normal override attribute"},
            {ALL_ACCUMULATING_ATTRIBUTES[1]: "3"},
        ]
        expected_attributes = {"attribute": "Normal override attribute"}

        result = _determine_overridden_attributes(override_order)
        self.assertEqual(result, expected_attributes)
