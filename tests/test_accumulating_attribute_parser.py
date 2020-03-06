"""Tests for parsing the attributes for targets in targets.json that accumulate."""
from unittest import TestCase

from mbed_targets._internal.target_attribute_hierarchy_parsers.accumulating_attribute_parser import (
    ALL_ACCUMULATING_ATTRIBUTES,
    _targets_accumulate_hierarchy,
    _determine_accumulated_attributes,
)


class TestParseHierarchy(TestCase):
    def test_accumulate_hierarchy_single_inheritance(self):
        all_targets_data = {
            "D": {"attribute_1": ["some things"]},
            "C": {"inherits": ["D"], "attribute_2": "something else"},
            "B": {},
            "A": {"inherits": ["C"], "attribute_3": ["even more things"]},
        }
        result = _targets_accumulate_hierarchy(all_targets_data, "A")

        self.assertEqual(result, [all_targets_data["A"], all_targets_data["C"], all_targets_data["D"]])

    def test_accumulate_hierarchy_multiple_inheritance(self):
        all_targets_data = {
            "F": {"attribute_1": "some thing"},
            "E": {"attribute_2": "some other thing"},
            "D": {"inherits": ["F"]},
            "C": {"inherits": ["E"]},
            "B": {"inherits": ["C", "D"]},
            "A": {"inherits": ["B"]},
        }
        result = _targets_accumulate_hierarchy(all_targets_data, "A")

        self.assertEqual(
            result,
            [
                all_targets_data["A"],
                all_targets_data["B"],
                all_targets_data["C"],
                all_targets_data["D"],
                all_targets_data["E"],
                all_targets_data["F"],
            ],
        )


class TestAccumulatingAttributes(TestCase):
    def test_determine_accumulated_attributes_basic_add(self):
        accumulation_order = [
            {"attribute_1": "something"},
            {f"{ALL_ACCUMULATING_ATTRIBUTES[0]}_add": [2, 3]},
            {ALL_ACCUMULATING_ATTRIBUTES[0]: [1]},
        ]
        expected_attributes = {ALL_ACCUMULATING_ATTRIBUTES[0]: [1, 2, 3]}
        result = _determine_accumulated_attributes(accumulation_order)
        self.assertEqual(result, expected_attributes)

    def test_determine_accumulated_attributes_basic_remove(self):
        accumulation_order = [
            {"attribute_1": "something"},
            {f"{ALL_ACCUMULATING_ATTRIBUTES[0]}_remove": [2, 3]},
            {ALL_ACCUMULATING_ATTRIBUTES[0]: [1, 2, 3]},
        ]
        expected_attributes = {ALL_ACCUMULATING_ATTRIBUTES[0]: [1]}
        result = _determine_accumulated_attributes(accumulation_order)
        self.assertEqual(result, expected_attributes)

    def test_combination_multiple_attributes(self):
        accumulation_order = [
            {f"{ALL_ACCUMULATING_ATTRIBUTES[0]}_add": [2, 3]},
            {f"{ALL_ACCUMULATING_ATTRIBUTES[1]}_remove": ["B", "C"]},
            {ALL_ACCUMULATING_ATTRIBUTES[0]: [1]},
            {ALL_ACCUMULATING_ATTRIBUTES[1]: ["A", "B", "C"]},
        ]
        expected_attributes = {
            ALL_ACCUMULATING_ATTRIBUTES[0]: [1, 2, 3],
            ALL_ACCUMULATING_ATTRIBUTES[1]: ["A"],
        }
        result = _determine_accumulated_attributes(accumulation_order)
        self.assertEqual(result, expected_attributes)
