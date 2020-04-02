#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Interface for accessing Mbed Target data.

An instance of `mbed_targets.mbed_target.MbedTarget` can be retrieved by calling one of the public functions.
"""
import logging
from enum import Enum
from typing import Callable

from mbed_targets.config import config
from mbed_targets.exceptions import UnknownTarget, UnsupportedMode
from mbed_targets.mbed_target import MbedTarget
from mbed_targets.mbed_targets import MbedTargets


logger = logging.getLogger(__name__)


def get_target_by_product_code(product_code: str) -> MbedTarget:
    """Returns first `mbed_targets.mbed_target.MbedTarget` matching given product code.

    Args:
        product_code: the product code to look up in the database.

    Raises:
        UnknownTarget: a target with a matching product code was not found in the target database.
    """
    return get_target(lambda target: target.product_code == product_code)


def get_target_by_online_id(slug: str, target_type: str) -> MbedTarget:
    """Returns first `mbed_targets.mbed_target.MbedTarget` matching given online id.

    Args:
        slug: The slug to look up in the database.
        target_type: The target type to look up in the database, normally one of `platform` or `module`.

    Raises:
        UnknownTarget: a target with a matching slug and target type could not be found in the target database.
    """
    matched_slug = slug.casefold()
    return get_target(lambda target: target.slug.casefold() == matched_slug and target.target_type == target_type)


def get_target(matching: Callable) -> MbedTarget:
    """Returns first `mbed_targets.mbed_target.MbedTarget` for which `matching` is True.

    Uses database mode configured in the environment, to find MbedTarget.

    Args:
        matching: A function which will be called for each target in database

    Raises:
        UnknownTarget: a target matching the criteria could not be found in the target database.
    """
    database_mode = _get_database_mode()

    if database_mode == _DatabaseMode.OFFLINE:
        logger.info("Using the offline database (only) to identify Mbed Targets.")
        return MbedTargets.from_offline_database().get_target(matching)

    if database_mode == _DatabaseMode.ONLINE:
        logger.info("Using the online database (only) to identify Mbed Targets.")
        return MbedTargets.from_online_database().get_target(matching)
    try:
        logger.info("Using the online database to identify Mbed Targets.")
        return MbedTargets.from_offline_database().get_target(matching)
    except UnknownTarget:
        logger.info("Unable to identify an Mbed Target using the offline database, trying the online database.")
        return MbedTargets.from_online_database().get_target(matching)


class _DatabaseMode(Enum):
    """Selected database mode."""

    OFFLINE = 0
    ONLINE = 1
    AUTO = 2


def _get_database_mode() -> _DatabaseMode:
    database_mode = config.MBED_DATABASE_MODE
    try:
        return _DatabaseMode[database_mode]
    except KeyError:
        raise UnsupportedMode(f"{database_mode} is not a supported database mode.")
