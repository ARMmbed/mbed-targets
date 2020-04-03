#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Internal helper to retrieve target attribute information.

This information is parsed from the targets.json configuration file
found in the mbed-os repo.
"""
import json
import pathlib
from json.decoder import JSONDecodeError
from typing import Dict, Any, Set, Optional

from mbed_tools_lib.exceptions import ToolsError

from mbed_targets._internal.target_attribute_hierarchy_parsers.accumulating_attribute_parser import (
    get_accumulating_attributes_for_target,
)
from mbed_targets._internal.target_attribute_hierarchy_parsers.overriding_attribute_parser import (
    get_overriding_attributes_for_target,
    get_labels_for_target,
)

INTERNAL_PACKAGE_DIR = pathlib.Path(__file__).parent
MBED_OS_METADATA_FILE = pathlib.Path(INTERNAL_PACKAGE_DIR, "data", "mbed_os_metadata.json")


class TargetAttributesError(ToolsError):
    """Target attributes error."""


class ParsingTargetsJSONError(TargetAttributesError):
    """targets.json parsing failed."""


class TargetAttributesNotFoundError(TargetAttributesError):
    """Attributes for target not found in targets.json."""


def get_target_attributes(path_to_targets_json: str, target_name: str) -> Any:
    """Retrieves attribute data taken from targets.json for a single target.

    Args:
        path_to_targets_json: an absolute or relative path to the location of targets.json.
        target_name: the name of the target also known as 'board_type' in the online database.

    Returns:
        A dictionary representation of the attributes for the target.

    Raises:
        FileNotFoundError: path provided does not lead to targets.json
        ParsingTargetJSONError: error parsing targets.json
        TargetAttributesNotFoundError: there is no target attribute data found for that target.
    """
    targets_json_path = pathlib.Path(path_to_targets_json)
    all_targets_data = _read_json_file(targets_json_path)
    build_attributes = _extract_target_attributes(all_targets_data, target_name)
    build_attributes["labels"] = get_labels_for_target(all_targets_data, target_name).union(
        _extract_core_labels(build_attributes.get("core", None))
    )
    return build_attributes


def _read_json_file(path_to_file: pathlib.Path) -> Any:
    """Reads the data from the targets.json file.

    Args:
        path_to_file: location of the targets.json file in mbed os library.

    Returns:
        A dictionary representation of all the targets.json data.

    Raises:
        ParsingTargetJSONError: error parsing targets.json
        FileNotFoundError: path provided does not lead to targets.json
    """
    try:
        return json.loads(path_to_file.read_text())
    except JSONDecodeError as json_err:
        raise ParsingTargetsJSONError(f"Invalid JSON found in '{path_to_file}'.") from json_err


def _extract_target_attributes(all_targets_data: Dict[str, Any], target_name: str) -> Any:
    """Extracts the attributes for a particular target from the targets data.

    Args:
        all_targets_data: a dictionary representation of targets.json data, still
        containing all the hierarchy structure.
        target_name: the name of the target also known as 'board_type' in the online database.

    Returns:
        A dictionary representation of the attributes of the target.

    Raises:
        TargetAttributesNotFoundError: there is no target attribute data found for that target.
    """
    if target_name not in all_targets_data:
        raise TargetAttributesNotFoundError(f"Target attributes for {target_name} not found.")

    if not all_targets_data[target_name].get("public", True):
        raise TargetAttributesNotFoundError(f"Target attributes for {target_name} not found.")

    target_attributes = get_overriding_attributes_for_target(all_targets_data, target_name)
    accumulated_attributes = get_accumulating_attributes_for_target(all_targets_data, target_name)
    target_attributes.update(accumulated_attributes)
    return target_attributes


def _extract_core_labels(target_core: Optional[str]) -> Set[str]:
    """Find the labels associated with the target's core.

    Args:
        target_core: the target core, set as a build attribute

    Returns:
        A list of labels associated with the target's core, or an empty set
        if either core is undefined or no labels found for the core.
    """
    if target_core:
        mbed_os_metadata = _read_json_file(MBED_OS_METADATA_FILE)
        return set(mbed_os_metadata["CORE_LABELS"].get(target_core, []))
    return set()
