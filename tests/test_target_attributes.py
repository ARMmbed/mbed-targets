"""Tests for `mbed_targets.target_attributes`."""
import pathlib
from pyfakefs.fake_filesystem_unittest import Patcher
from unittest import TestCase, mock

from mbed_targets._internal.target_attributes import (
    ParsingTargetsJSONError,
    TargetAttributesNotFoundError,
    get_target_attributes,
    _read_targets_json,
    _extract_target_attributes,
)


class TestExtractTargetAttributes(TestCase):
    def test_no_target_found(self):
        all_targets_data = {
            "Target_1": "some attributes",
            "Target_2": "some more attributes",
        }
        with self.assertRaises(TargetAttributesNotFoundError):
            _extract_target_attributes(all_targets_data, "Unlisted_Target")

    def test_target_found(self):
        target_attributes = {"attribute1": "something"}

        all_targets_data = {
            "Target_1": target_attributes,
            "Target_2": "some more attributes",
        }
        # When not explicitly included public is assumed to be True
        self.assertEqual(_extract_target_attributes(all_targets_data, "Target_1"), target_attributes)

    def test_target_public(self):
        all_targets_data = {
            "Target_1": {"attribute1": "something", "public": True},
            "Target_2": "some more attributes",
        }
        # The public attribute affects visibility but is removed from result
        self.assertEqual(_extract_target_attributes(all_targets_data, "Target_1"), {"attribute1": "something"})

    def test_target_private(self):
        all_targets_data = {
            "Target_1": {"attribute1": "something", "public": False},
            "Target_2": "some more attributes",
        }
        with self.assertRaises(TargetAttributesNotFoundError):
            _extract_target_attributes(all_targets_data, "Target_1"),


class TestReadTargetsJSON(TestCase):
    def test_valid_path(self):
        contents = """{
            "Target_Name": {
                "attribute_1": []
            }
        }"""
        with Patcher() as patcher:
            path = pathlib.Path("/test/targets.json")
            patcher.fs.create_file(str(path), contents=contents)
            result = _read_targets_json(path)

            self.assertEqual(type(result), dict)

    def test_invalid_path(self):
        path = pathlib.Path("i_dont_exist")

        with self.assertRaises(FileNotFoundError):
            _read_targets_json(path)

    def test_malformed_json(self):
        contents = """{
            "Target_Name": {
                []
            }
        }"""
        with Patcher() as patcher:
            path = pathlib.Path("/test/targets.json")
            patcher.fs.create_file(str(path), contents=contents)

            with self.assertRaises(ParsingTargetsJSONError):
                _read_targets_json(path)


class TestGetTargetAttributes(TestCase):
    @mock.patch("mbed_targets._internal.target_attributes._read_targets_json")
    @mock.patch("mbed_targets._internal.target_attributes._extract_target_attributes")
    @mock.patch("mbed_targets._internal.target_attributes.get_labels_for_target")
    def test_gets_attributes_for_target(self, get_labels_for_target, extract_target_attributes, read_targets_json):
        targets_json_path = "mbed-os/targets/targets.json"
        target_name = "My_Target"
        result = get_target_attributes(targets_json_path, target_name)

        read_targets_json.assert_called_once_with(pathlib.Path(targets_json_path))
        extract_target_attributes.assert_called_once_with(read_targets_json.return_value, target_name)
        get_labels_for_target.assert_called_once_with(read_targets_json.return_value, target_name)
        self.assertEqual(result, extract_target_attributes.return_value)
