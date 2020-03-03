"""Internal helper to retrieve target information from the online database."""

import os
import pathlib
from http import HTTPStatus
import json
from json.decoder import JSONDecodeError
from typing import List, Optional, Dict, Any

import dotenv
import requests

from mbed_tools_lib.exceptions import ToolsError


INTERNAL_PACKAGE_DIR = pathlib.Path(__file__).parent
SNAPSHOT_FILENAME = "targets_database_snapshot.json"


def get_target_database_path() -> pathlib.Path:
    """Return the path to the offline target database."""
    return pathlib.Path(INTERNAL_PACKAGE_DIR, "data", SNAPSHOT_FILENAME)


# Search for the .env file containing the MBED_API_AUTH_TOKEN environment variable.
# We want this to execute at import time.
dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True), override=True)


_AUTH_TOKEN_ENV_VAR = "MBED_API_AUTH_TOKEN"
_TARGET_API = "https://os.mbed.com/api/v4/targets"


class TargetDatabaseError(ToolsError):
    """Target database error."""


class TargetAPIError(TargetDatabaseError):
    """API request failed."""


class ResponseJSONError(TargetDatabaseError):
    """HTTP response JSON parsing failed."""


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
            f"'{_AUTH_TOKEN_ENV_VAR}' is correctly configured with a private access token."
        )
    else:
        return f"An HTTP {response.status_code} was received from '{_TARGET_API}' containing:\n{response.text}"


def _get_request() -> requests.Response:
    """Make a get request to the API, ensuring the correct headers are set."""
    token = os.getenv(_AUTH_TOKEN_ENV_VAR)
    header: Optional[Dict[str, str]] = None
    if token:
        header = {"Authorization": f"Bearer {token}"}

    return requests.get(_TARGET_API, headers=header)
