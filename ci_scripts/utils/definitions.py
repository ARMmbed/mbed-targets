import os

PROJECT_ROOT = os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), '..',
                 '..'))
PROJECT_CONFIG = os.path.join(os.path.dirname(__file__), '..',
                              "pyproject.toml")
NEWS_DIR = os.path.realpath(os.path.join(PROJECT_ROOT, 'news'))
BETA_BRANCH = 'beta'
MASTER_BRANCH = 'master'
RELEASE_BRANCH_PATTERN = r"^release.*$"
REMOTE_ALIAS = 'origin'
ENVVAR_GIT_TOKEN = 'GITHUB_TOKEN'
LOGGER_FORMAT = '%(levelname)s: %(message)s'
