"""Internal helper to retrieve target information from the online database."""

from http import HTTPStatus

from json.decoder import JSONDecodeError
from typing import List

import requests


_AUTH_TOKEN_ENV_VAR = "MBED_API_AUTH_TOKEN"
_TARGET_API = "https://os.mbed.com/api/v4/targets"


class ToolsError(Exception):
    """Base class for tools errors."""

    # TODO: move to mbed-tools-lib


class TargetDatabaseError(ToolsError):
    """Target database error."""


class TargetAPIError(TargetDatabaseError):
    """API request failed."""


class ResponseJSONError(TargetDatabaseError):
    """HTTP reponse JSON parsing failed."""


def get_target_data() -> List[dict]:
    """Retrieves list of build targets and OS versions to determine versions of the OS to test against.

    Returns:
        The target database as retrieved from the targets API

    Raises:
        ResponseJSONError: error decoding the reponse JSON.
        TargetAPIError: error retrieving data from the Target API.
    """
    target_data: List[dict] = [{}]
    response = requests.get(_TARGET_API)

    if response.status_code != HTTPStatus.OK:
        raise TargetAPIError(_response_error_code_to_str(response))

    try:
        json_data = response.json()
    except JSONDecodeError as json_err:
        raise ResponseJSONError(
            f"Invalid JSON received from '{_TARGET_API}'."
        ) from json_err

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
