"""
Handles usage of towncrier for automated changelog generation
Handles usage of pyautoversion for versioning
"""
import sys
import argparse
import enum
import logging
import subprocess
from auto_version import auto_version_tool
from utils.definitions import PROJECT_CONFIG
from utils.logging import log_exception, set_log_level

logger = logging.getLogger(__name__)


class CommitType(enum.Enum):
    DEVELOPMENT = 1
    BETA = 2
    RELEASE = 3


def version_project(commit_type: CommitType):
    """
    Versions the project
    :param commit_type: states what is the type of the commit
    :type: CommitType
    """

    use_news_files = commit_type in [CommitType.BETA, CommitType.RELEASE]

    new_version = _calculate_version(commit_type, use_news_files)
    _generate_changelog(new_version, use_news_files)


def _calculate_version(commit_type: CommitType, use_news_files: bool):
    BUMP_TYPES = {CommitType.DEVELOPMENT: "build",
                  CommitType.BETA: "prerelease"}
    is_release = commit_type == CommitType.RELEASE
    enable_file_triggers = True if use_news_files else None
    bump = BUMP_TYPES.get(commit_type)
    old, new_version, updates = auto_version_tool.main(
        release=is_release,
        enable_file_triggers=enable_file_triggers,
        bump=bump,
        config_path=PROJECT_CONFIG,
    )
    logger.info(f'Version: {new_version}')
    return new_version


def _generate_changelog(version: str, use_news_files: bool):
    if use_news_files:
        logger.info(':: Generating a new changelog')
        subprocess.check_call(
            ['towncrier', '--yes', '--name=""', f'--version="{version}"']
        )


def main():
    parser = argparse.ArgumentParser(
        description='Versions the project.')
    parser.add_argument('-r', '--release',
                        help='Update the version for an official release',
                        action='store_true')
    parser.add_argument('-b', '--beta',
                        help='Update the version for a pre-release',
                        action='store_true')
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Verbosity, by default errors are reported.")
    args = parser.parse_args()
    commit_type = CommitType.DEVELOPMENT
    if args.release:
        commit_type = CommitType.RELEASE
    if args.beta:
        commit_type = CommitType.BETA
    set_log_level(args.verbose)

    try:
        version_project(commit_type)
    except Exception as e:
        log_exception(logger, e)
        sys.exit(1)


if __name__ == '__main__':
    main()
