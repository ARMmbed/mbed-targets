"""Handles usage of towncrier for automated changelog generation and pyautoversion for versioning."""
import sys

import argparse
import logging
import os
import subprocess
from auto_version import auto_version_tool
from utils.definitions import CommitType
from utils.configuration import configuration, ConfigurationVariable
from utils.logging import log_exception, set_log_level
from utils.filesystem_helpers import cd

logger = logging.getLogger(__name__)


def version_project(commit_type: CommitType) -> str:
    """Versions the project.

    Args:
        commit_type: states what is the type of the commit


    Returns:
        the new version
    """
    use_news_files = commit_type in [CommitType.BETA, CommitType.RELEASE]
    new_version = _calculate_version(commit_type, use_news_files)
    _generate_changelog(new_version, use_news_files)
    return new_version


def _calculate_version(commit_type: CommitType, use_news_files: bool):
    """Calculates the version for the release.

    eg. "0.1.2"

    Args:
        commit_type:
        use_news_files: Should the version be dependant on changes recorded in news files

    Returns:
        A semver-style version for the latest release
    """
    BUMP_TYPES = {CommitType.DEVELOPMENT: "build",
                  CommitType.BETA: "prerelease"}
    is_release = commit_type == CommitType.RELEASE
    enable_file_triggers = True if use_news_files else None
    bump = BUMP_TYPES.get(commit_type)
    project_config_path = configuration.get_value(
        ConfigurationVariable.PROJECT_CONFIG)
    with cd(os.path.dirname(project_config_path)):
        old, new_version, updates = auto_version_tool.main(
            release=is_release,
            enable_file_triggers=enable_file_triggers,
            bump=bump,
            config_path=project_config_path,
        )
    logger.info(':: Determining the new version')
    logger.info(f'Version: {new_version}')
    return new_version


def _generate_changelog(version: str, use_news_files: bool):
    """Creates a towncrier log of the release.

    Will only create a log entry if we are using news files.

    Args:
        version: the semver version of the release
        use_news_files: are we generating the release from news files
    """
    if use_news_files:
        logger.info(':: Generating a new changelog')
        project_config_path = configuration.get_value(
            ConfigurationVariable.PROJECT_CONFIG)
        with cd(os.path.dirname(project_config_path)):
            subprocess.check_call(
                ['towncrier', '--yes', '--name=""', f'--version="{version}"']
            )


def main():
    """Handle command line arguments to generate a version and changelog file."""
    parser = argparse.ArgumentParser(
        description='Versions the project.')
    parser.add_argument('-t', '--release-type',
                        help='type of release to perform',
                        required=True,
                        type=str, choices=CommitType.choices())
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Verbosity, by default errors are reported.")
    args = parser.parse_args()
    set_log_level(args.verbose)

    try:
        version_project(CommitType.parse(args.release_type))
    except Exception as e:
        log_exception(logger, e)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
