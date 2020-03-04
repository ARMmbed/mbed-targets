"""Tests for `mbed_targets_dependencies`."""
import pathlib
from unittest import TestCase, mock

from mbed_targets._internal.target_attributes import (
    ParsingTargetsJSONError,
    TargetAttributesNotFoundError,
    _read_targets_json,
    _extract_target_attributes,
    get_target_attributes,
)

TEST_DIR = pathlib.Path(__file__).parents[0]
PATH_TO_MOCK_TARGETS_JSON = TEST_DIR.joinpath("test_mock_sources/mock_targets.json")
PATH_TO_MALFORMED_MOCK_TARGETS_JSON = TEST_DIR.joinpath("test_mock_sources/malformed_targets.json")


class TestExtractTargetAttributes(TestCase):
    def test_target_found(self):
        target_attributes = {"attribute1": "something"}

        all_targets_data = {
            "Target_1": target_attributes,
            "Target_2": "some more attributes",
        }
        self.assertEqual(_extract_target_attributes(all_targets_data, "Target_1"), target_attributes)

    def test_no_target_found(self):
        all_targets_data = {
            "Target_1": "some attributes",
            "Target_2": "some more attributes",
        }
        with self.assertRaises(TargetAttributesNotFoundError):
            _extract_target_attributes(all_targets_data, "Unlisted_Target"),


class TestReadTargetsJSON(TestCase):
    def test_valid_path(self):
        path = pathlib.Path(PATH_TO_MOCK_TARGETS_JSON)
        result = _read_targets_json(path)

        self.assertEqual(type(result), dict)

    def test_invalid_path(self):
        path = pathlib.Path("i_dont_exist")

        with self.assertRaises(FileNotFoundError):
            _read_targets_json(path)

    def test_malformed_json(self):
        path = pathlib.Path(PATH_TO_MALFORMED_MOCK_TARGETS_JSON)

        with self.assertRaises(ParsingTargetsJSONError):
            _read_targets_json(path)


class TestGetTargetAttributes(TestCase):
    @mock.patch("mbed_targets._internal.target_attributes._read_targets_json")
    @mock.patch("mbed_targets._internal.target_attributes._extract_target_attributes")
    def test_gets_attributes_for_target(self, extract_target_attributes, read_targets_json):
        targets_json_path = "mbed-os/targets/targets.json"
        target_name = "My_Target"
        result = get_target_attributes(targets_json_path, target_name)

        read_targets_json.assert_called_once_with(pathlib.Path(targets_json_path))
        extract_target_attributes.assert_called_once_with(read_targets_json.return_value, target_name)
        self.assertEqual(result, extract_target_attributes.return_value)
