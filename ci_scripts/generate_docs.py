"""Script to generate documentation using pdoc."""
import logging
import sys
from subprocess import check_call

from utils.definitions import MODULES_TO_DOCUMENT, DOCUMENTATION_DIR_PATH
from utils.logging import log_exception

logger = logging.getLogger(__name__)


def main() -> int:
    """Triggers building the documentation.

    Modules to document and the output destination path
    can be set in the utils.definitions config file.
    """
    command_list = [
        "pdoc", "--output-dir", f'{DOCUMENTATION_DIR_PATH}',
        "--force", "--config", "show_type_annotations=True"
    ]

    for module_name in MODULES_TO_DOCUMENT:
        command_list.append("--html")
        command_list.append(f'{module_name}')

    logger.info('Creating pdoc documentation.')

    try:
        check_call(command_list)
    except Exception as e:
        log_exception(logger, e)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
