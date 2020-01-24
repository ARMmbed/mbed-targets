"""Performs package releasing (part of the CI process)."""
import sys

import argparse
import datetime
import logging
import subprocess
from generate_news import version_project
from utils.configuration import configuration, ConfigurationVariable
from utils.definitions import CommitType
from utils.filesystem_helpers import cd
from utils.git_helpers import GitWrapper
from utils.logging import log_exception, set_log_level

ENVVAR_TWINE_REPOSITORY = 'TWINE_REPOSITORY'
ENVVAR_TWINE_USERNAME = 'TWINE_USERNAME'
ENVVAR_TWINE_REPOSITORY_URL = 'TWINE_REPOSITORY_URL'
logger = logging.getLogger(__name__)


def tag_and_release(mode: CommitType) -> None:
    """Tags and releases.

    Updates repository with changes and releases package to PyPI for general availability.

    Args:
        mode: release mode

    """
    version = version_project(mode)
    logger.info(f'Current version: {version}')
    if mode == CommitType.DEVELOPMENT:
        return
    _check_credentials()
    _update_repository(mode, version)
    _release_to_pypi()


def _update_repository(mode: CommitType, version: str) -> None:
    git = GitWrapper()
    git.configure_for_github()
    if mode == CommitType.RELEASE:
        logger.info(f'Committing release [{version}]...')
        git.add(
            configuration.get_value(ConfigurationVariable.VERSION_FILE_PATH))
        git.add(
            configuration.get_value(ConfigurationVariable.CHANGELOG_FILE_PATH))
        git.add(configuration.get_value(ConfigurationVariable.NEWS_DIR))
        time_str = datetime.datetime.utcnow().strftime(
            "%Y-%m-%d %H:%M")
        git.commit(
            f':checkered_flag: :newspaper: releasing version {version} @ {time_str}\n[skip ci]')
        git.push()
        git.pull()
    logger.info(f'Tagging commit')
    git.create_tag(version, message=f'release {version}')
    git.force_push_tag()


def _check_credentials() -> None:
    # Checks the GitHub token is defined
    configuration.get_value(ConfigurationVariable.GIT_TOKEN)
    # Checks that twine username is defined
    configuration.get_value(ENVVAR_TWINE_USERNAME)
    # Checks that twine repository is defined
    configuration.get_value_or_default(
        ENVVAR_TWINE_REPOSITORY_URL, configuration.get_value(
            ENVVAR_TWINE_REPOSITORY))


def _release_to_pypi() -> None:
    logger.info('Releasing to PyPI')
    logger.info('Generating a release package')
    root = configuration.get_value(ConfigurationVariable.PROJECT_ROOT)
    with cd(root):
        subprocess.check_call(
            [sys.executable, 'setup.py', 'clean', '--all', 'sdist',
             'bdist_wheel',
             '--dist-dir', 'release-dist'])
        logger.info('Uploading to PyPI')
        subprocess.check_call(
            [sys.executable, '-m', 'twine', 'upload', '/release-dist/*'])


def main() -> int:
    """Commands.

    Returns:
        success code (0) if successful; failure code otherwise.
    """
    parser = argparse.ArgumentParser(
        description='Releases the project.')
    parser.add_argument('-t', '--release-type',
                        help='type of release to perform',
                        required=True,
                        type=str, choices=CommitType.choices())
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Verbosity, by default errors are reported.")
    args = parser.parse_args()
    set_log_level(args.verbose)
    try:
        tag_and_release(CommitType.parse(args.release_type))
    except Exception as e:
        log_exception(logger, e)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
