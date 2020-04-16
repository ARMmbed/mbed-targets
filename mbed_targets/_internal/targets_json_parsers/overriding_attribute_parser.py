#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Functions for parsing the inheritance for overriding attributes.

Accumulating attributes are defined and can be overridden further down the hierarchy.
The hierarchy is determined as 'depth-first' in multiple inheritance.
eg. Look first for the attribute in the current target. If not found,
look for the attribute in the first target's parent, then in the parent of the parent and so on.
If not found, look for the property in the rest of the target's parents, relative to the
current inheritance level.

This means a target on a higher level could potentially override one on a lower level.
"""
from collections import deque
from functools import reduce
from typing import Dict, List, Any, Deque, Set

from mbed_targets._internal.targets_json_parsers.accumulating_attribute_parser import ALL_ACCUMULATING_ATTRIBUTES

NON_OVERRIDING_ATTRIBUTES = ALL_ACCUMULATING_ATTRIBUTES + ("public", "inherits")


def get_overriding_attributes_for_target(all_targets_data: Dict[str, Any], target_name: str) -> Dict[str, Any]:
    """Parses the data for all targets and returns the overriding attributes for the specified target.

    Args:
        all_targets_data: a dictionary representation of the contents of targets.json
        target_name: the name of the target to find the attributes of

    Returns:
        A dictionary containing all the overriding attributes for the chosen target
    """
    override_order = _targets_override_hierarchy(all_targets_data, target_name)
    return _determine_overridden_attributes(override_order)


def get_labels_for_target(all_targets_data: Dict[str, Any], target_name: str) -> Set[str]:
    """The labels for a target are the names of all the boards (public and private) that the board inherits from.

    The order of these labels are not reflective of inheritance order.

    Args:
        all_targets_data: a dictionary representation of the contents of targets.json
        target_name: the name of the target to find the labels for

    Returns:
        A set of names of boards that make up the inheritance tree for the target
    """
    override_order = _targets_override_hierarchy(all_targets_data, target_name)
    return _extract_target_labels(override_order, target_name)


def _targets_override_hierarchy(all_targets_data: Dict[str, Any], target_name: str) -> List[dict]:
    """List all ancestors of a target in order of overriding inheritance (depth-first).

    Using a depth-first traverse of the inheritance tree, return a list of targets in the
    order of inheritance, starting with the target itself and finishing with its highest ancestor.

    Args:
        all_targets_data: a dictionary representation of all the data in a targets.json file
        target_name: the name of the target we want to calculate the attributes for

    Returns:
        A list of dicts representing each target in the hierarchy.
    """
    override_order: List[dict] = []

    still_to_visit: Deque[dict] = deque()
    still_to_visit.appendleft(all_targets_data[target_name])

    while still_to_visit:
        current_target = still_to_visit.popleft()
        override_order.append(current_target)
        for parent_target in reversed(current_target.get("inherits", [])):
            still_to_visit.appendleft(all_targets_data[parent_target])

    return override_order


def _determine_overridden_attributes(override_order: List[dict]) -> Dict[str, Any]:
    """Finds all the overrideable attributes for a target from its list of ancestors.

    Merges the attributes from all the targets in the hierarchy. Starts from the highest ancestor
    reduces down to the target itself, overriding if they define the same attribute.

    Removes any accumulating attributes - they will be handled by a separate parser.

    Args:
        override_order: list of targets in order of inheritance, starting with the target up to its highest ancestor

    Returns:
        A dictionary containing all the overridden attributes for a target
    """
    target_attributes = reduce(lambda x, y: {**x, **y}, reversed(override_order))
    overridden_attributes = _remove_unwanted_attributes(target_attributes)
    return overridden_attributes


def _remove_unwanted_attributes(target_attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Removes all non-overriding attributes.

    Defined in NON_OVERRIDING_ATTRIBUTES.
    Accumulating arguments are inherited in a different way that is handled by its own parser.
    The 'public' attribute is not inherited.
    The 'inherits' attribute is only needed to calculate the hierarchies.

    Args:
        target_attributes: a dictionary of attributes for a target

    Returns:
        The target attributes with the accumulating attributes removed.
    """
    output_dict = target_attributes.copy()
    for attribute in NON_OVERRIDING_ATTRIBUTES:
        output_dict.pop(attribute, None)
    return output_dict


def _extract_target_labels(override_order: List[dict], target_name: str) -> Set[str]:
    """Collect a set of all the board names from the inherits field in each target in the hierarchy.

    Args:
        override_order: list of targets in order of inheritance, starting with the target up to its highest ancestor
        target_name: the name of the target to find the labels for

    Returns:
        A set of names of boards that make up the inheritance tree for the target
    """
    labels = {target_name}
    for target in override_order:
        for parent in target.get("inherits", []):
            labels.add(parent)
    return labels
