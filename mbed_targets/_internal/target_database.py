"""Internal helper to retrieve target information from the online database"""

import os
import logging

import requests
from json.decoder import JSONDecodeError

logger = logging.getLogger(__name__)

_AUTH_TOKEN_ENV_VAR = "MBED_TARGET_DB_AUTH_TOKEN"
_TARGET_API = "https://os.mbed.com/api/v4/targets"


def _get_target_data():
    """Retrieve list of build targets and OS versions to determine versions of the OS to test against.

    """
    target_data = []

    response = requests.get(_TARGET_API)

    if response.status_code == 200:
        try:
            json_data = response.json()
        except JSONDecodeError:
            logging.error("Invalid JSON received from %s" % _TARGET_API)
        else:
            try:
                target_data = json_data["data"]
            except KeyError:
                logging.error("Invalid JSON received from %s" % _TARGET_API)
    elif response.status_code == 401:
        logger.error(f"{_TARGET_API} authentication failed. Please check that the environment variable "
                     f"'{_AUTH_TOKEN_ENV_VAR}' is correctly configured with a private access token.")
    else:
        logger.error(f"{_TARGET_API} returned HTTP: {response.status_code} with the content:\n{response.text}")

    return target_data


class TargetDatabase:

    def __init__(self):
        self._target_data = None

    @property
    def target_data(self):
        """Return target data, retrieving it from the API if not already in memory."""
        if self._target_data is None:
            self._target_data = _get_target_data()

        return self._target_data
