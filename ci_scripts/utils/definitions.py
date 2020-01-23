"""Place to store all project-specific constants for the ci scripts."""
import os
import enum
from typing import List

PROJECT_ROOT = os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), '..',
                 '..'))
PROJECT_CONFIG = os.path.join(os.path.dirname(__file__), '..',
                              "pyproject.toml")
NEWS_DIR = os.path.realpath(os.path.join(PROJECT_ROOT, 'news'))
VERSION_FILE_PATH = os.path.realpath(
    os.path.join(PROJECT_ROOT, 'mbed_targets', '_version.py')
)
CHANGELOG_FILE_PATH = os.path.realpath(
    os.path.join(PROJECT_ROOT, 'CHANGELOG.md')
)
BETA_BRANCH = 'beta'
MASTER_BRANCH = 'master'
RELEASE_BRANCH_PATTERN = r"^release.*$"
REMOTE_ALIAS = 'origin'
LOGGER_FORMAT = '%(levelname)s: %(message)s'
MODULE_TO_DOCUMENT = 'mbed_targets'
DOCUMENTATION_DEFAULT_OUTPUT_PATH = os.path.realpath(
    os.path.join(PROJECT_ROOT, "docs", "user_docs", "local_output")
)

# Environment variables
ENVVAR_GIT_TOKEN = 'GITHUB_TOKEN'


class CommitType(enum.Enum):
    """Type of commits."""
    DEVELOPMENT = 1
    BETA = 2
    RELEASE = 3

    @staticmethod
    def choices() -> List[str]:
        """Gets a list of all possible commit types.

        Returns:
            a list of commit types
        """
        return [t.name.lower() for t in CommitType]

    @staticmethod
    def parse(type_str: str) -> 'CommitType':
        """Determines the commit type from a string.

        Args:
            type_str: string to parse.

        Returns:
            corresponding commit type.
        """
        try:
            return CommitType[type_str.upper()]
        except KeyError as e:
            raise ValueError(f'Unknown commit type: {type_str}. {e}')
