"""Internal helper to retrieve target attribute information.

This information is parsed from the targets.json configuration file
found in the mbed-os repo.
"""
import json
import pathlib
from typing import Dict, Any
from json.decoder import JSONDecodeError

from mbed_tools_lib.exceptions import ToolsError


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
    all_targets_data = _read_targets_json(targets_json_path)
    return _extract_target_attributes(all_targets_data, target_name)


def _read_targets_json(path_to_targets_json: pathlib.Path) -> Any:
    """Reads the data from the targets.json file.

    Args:
        path_to_targets_json: location of the targets.json file in mbed os library.

    Returns:
        A dictionary representation of all the targets.json data.

    Raises:
        ParsingTargetJSONError: error parsing targets.json
        FileNotFoundError: path provided does not lead to targets.json
    """
    try:
        return json.loads(path_to_targets_json.read_text())
    except JSONDecodeError as json_err:
        raise ParsingTargetsJSONError(f"Invalid JSON found in '{path_to_targets_json}'.") from json_err


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
    try:
        return all_targets_data[target_name]
    except KeyError:
        raise TargetAttributesNotFoundError(f"Target attributes for {target_name} not found.")
