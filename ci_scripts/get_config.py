"""Script retrieving configuration values."""
import argparse
import sys
import logging
from utils.configuration import configuration, ConfigurationVariable
from utils.logging import set_log_level, log_exception

logger = logging.getLogger(__name__)


def main() -> int:
    """Handle command line arguments to get configuration values."""
    parser = argparse.ArgumentParser(
        description='Project\'s configuration.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--config-variable',
                       help='variable key string',
                       type=str)
    group.add_argument('-k', '--key',
                       help='configuration variable',
                       type=str, choices=ConfigurationVariable.choices())
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Verbosity, by default errors are reported.")
    args = parser.parse_args()
    set_log_level(args.verbose)

    try:
        print(configuration.get_value(ConfigurationVariable.parse(
            args.key) if args.key else args.config_variable))
    except Exception as e:
        log_exception(logger, e)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
