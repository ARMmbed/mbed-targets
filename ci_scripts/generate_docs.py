"""Generates documentation using Pdoc."""
import argparse
import logging
import sys
from subprocess import check_call

from utils.definitions import (
    MODULE_TO_DOCUMENT, DOCUMENTATION_DEFAULT_OUTPUT_PATH
)
from utils.logging import log_exception

logger = logging.getLogger(__name__)


def main(output_directory: str) -> int:
    """Triggers building the documentation.

    Module to document and the output destination path
    can be set in the utils.definitions config file.
    """
    command_list = [
        "pdoc", "--html", f"{MODULE_TO_DOCUMENT}", "--output-dir",
        f'{output_directory}', "--force", "--config",
        "show_type_annotations=True"
    ]

    logger.info('Creating Pdoc documentation.')

    try:
        check_call(command_list)
    except Exception as e:
        log_exception(logger, e)
        return 1
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_directory",
        help="Output directory for docs html files.",
        default=DOCUMENTATION_DEFAULT_OUTPUT_PATH,
    )
    args = parser.parse_args()
    sys.exit(main(output_directory=args.output_directory))
