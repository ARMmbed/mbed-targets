"""Exceptions used internally by the mbed-targets package."""

from mbed_targets.exceptions import TargetDatabaseError


class TargetAPIError(TargetDatabaseError):
    """API request failed."""


class ResponseJSONError(TargetDatabaseError):
    """HTTP response JSON parsing failed."""
