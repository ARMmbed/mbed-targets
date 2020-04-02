#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Internal helper to retrieve target information from the online database."""

import pathlib
from http import HTTPStatus
import json
from json.decoder import JSONDecodeError
import logging
from typing import List, Optional, Dict, Any

import requests

from mbed_targets._internal.exceptions import ResponseJSONError, TargetAPIError

from mbed_targets.config import config


INTERNAL_PACKAGE_DIR = pathlib.Path(__file__).parent
SNAPSHOT_FILENAME = "targets_database_snapshot.json"

logger = logging.getLogger(__name__)


def get_target_database_path() -> pathlib.Path:
    """Return the path to the offline target database."""
    return pathlib.Path(INTERNAL_PACKAGE_DIR, "data", SNAPSHOT_FILENAME)


_TARGET_API = "https://os.mbed.com/api/v4/targets"


def get_offline_target_data() -> Any:
    """Loads target data from JSON stored in repository.

    Returns:
        The target database as retrieved from the local database.

    Raises:
        ResponseJSONError: error decoding the local database JSON.
    """
    targets_json_path = get_target_database_path()
    try:
        return json.loads(targets_json_path.read_text())
    except JSONDecodeError as json_err:
        raise ResponseJSONError(f"Invalid JSON received from '{targets_json_path}'.") from json_err


def get_online_target_data() -> List[dict]:
    """Retrieves target data from the online API.

    Returns:
        The target database as retrieved from the targets API

    Raises:
        ResponseJSONError: error decoding the reponse JSON.
        TargetAPIError: error retrieving data from the Target API.
    """
    target_data: List[dict] = [{}]
    response = _get_request()
    if response.status_code != HTTPStatus.OK:
        raise TargetAPIError(_response_error_code_to_str(response))

    try:
        json_data = response.json()
    except JSONDecodeError as json_err:
        raise ResponseJSONError(f"Invalid JSON received from '{_TARGET_API}'.") from json_err

    try:
        target_data = json_data["data"]
    except KeyError as key_err:
        raise ResponseJSONError(
            f"JSON received from '{_TARGET_API}' is missing the 'data' field."
            f"Fields found in JSON Response: {json_data.keys()}"
        ) from key_err

    return target_data


def _response_error_code_to_str(response: requests.Response) -> str:
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        return (
            f"Authentication failed for '{_TARGET_API}'. Please check that the environment variable "
            f"'MBED_API_AUTH_TOKEN' is correctly configured with a private access token."
        )
    else:
        return f"An HTTP {response.status_code} was received from '{_TARGET_API}' containing:\n{response.text}"


def _get_request() -> requests.Response:
    """Make a get request to the API, ensuring the correct headers are set."""
    header: Optional[Dict[str, str]] = None
    mbed_api_auth_token = config.MBED_API_AUTH_TOKEN
    if mbed_api_auth_token:
        header = {"Authorization": f"Bearer {mbed_api_auth_token}"}

    try:
        return requests.get(_TARGET_API, headers=header)
    except requests.exceptions.ConnectionError as connection_error:
        logger.warning("There was an error connecting to the online database. Please check your internet connection.")
        raise TargetAPIError("Failed to connect to the online database.") from connection_error
