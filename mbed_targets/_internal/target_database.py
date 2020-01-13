"""Internal helper to retrieve target information from the online database"""

import logging

import requests
from json.decoder import JSONDecodeError

logger = logging.getLogger(__name__)

_AUTH_TOKEN_ENV_VAR = "MBED_API_AUTH_TOKEN"

_TARGET_API = "https://os.mbed.com/api/v4/targets"


def get_target_data():
    """Retrieve list of build targets and OS versions to determine versions of the OS to test against.

    :return: The target database as retrieved from the targets API, None if there was an error.
    :rtype: list(dict)
    """
    target_data = None

    response = requests.get(_TARGET_API)

    if response.status_code == 200:
        try:
            json_data = response.json()
        except JSONDecodeError:
            logger.error(f"Invalid JSON received from '{_TARGET_API}'.")
        else:
            try:
                target_data = json_data["data"]
            except KeyError:
                logger.error(f"JSON received from '{_TARGET_API}' is missing the 'data' key.")
    elif response.status_code == 401:
        logger.error(f"Authentication failed for '{_TARGET_API}'. Please check that the environment variable "
                     f"'{_AUTH_TOKEN_ENV_VAR}' is correctly configured with a private access token.")
    else:
        logger.error(f"An HTTP {response.status_code} was received from '{_TARGET_API}' containing:\n{response.text}")

    return target_data
