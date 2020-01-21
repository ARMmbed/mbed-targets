"""
Ensures news file are created for all new changes to the project.
"""
import sys

import argparse
import logging
import os
import re
from utils.definitions import PROJECT_ROOT, MASTER_BRANCH, BETA_BRANCH, \
    RELEASE_BRANCH_PATTERN, NEWS_DIR
from utils.git_helpers import GitWrapper
from utils.logging import log_exception, set_log_level

logger = logging.getLogger(__name__)

VALID_EXTENSIONS = ['misc', 'doc', 'removal', 'bugfix', 'feature', 'major']
NEWS_FILE_NAME_FORMAT = r"^[0-9]+.[a-z]+$"


class NewsFileValidator:
    """
    Verification of the individual news files: naming, existence, content
    """

    def __init__(self, full_path):
        self._news_file_path = full_path

    def _verify_news_file_name(self):
        basename = str(os.path.basename(
            self._news_file_path)) if self._news_file_path else None
        if (not basename) or (not re.search(NEWS_FILE_NAME_FORMAT, basename)):
            raise ValueError(
                f'Incorrect news file name [{basename}]. It must follow the following format: {NEWS_FILE_NAME_FORMAT}'
            )
        for extension in VALID_EXTENSIONS:
            if extension in basename:
                break
        else:
            raise ValueError(
                'News file extension must be one of the following: %s' % (
                    ', '.join(VALID_EXTENSIONS)
                )
            )

    def _verify_news_file_content(self):
        if not os.path.exists(self._news_file_path):
            raise FileNotFoundError(self._news_file_path)
        with open(self._news_file_path, 'r') as fh:
            file_content = fh.read()
        if not file_content:
            raise ValueError(f'Empty news file `{self._news_file_path}`')
        if len(file_content.splitlines()) > 1:
            raise ValueError('News file must only contain 1-line sentence')

    def verify(self):
        """
        Verifies news file follows standards
        """
        logger.info('Verifying %s' % self._news_file_path)
        self._verify_news_file_name()
        self._verify_news_file_content()


class NewsFileDiscoverer:
    """
    Checks that all new PRs comprise a news file and that such files follow the standard
    """

    def __init__(self):
        self.git = GitWrapper()
        self.current_branch = self.git.get_current_branch()
        self.master_branch = MASTER_BRANCH

    def find_news_file(self):
        """
        Determines a list of all the news files which were added as part of the PR.
        :return: list of introduced news files
        """

        if not os.path.exists(NEWS_DIR):
            NotADirectoryError(
                f'News files directory was not specified and default path `{NEWS_DIR}` does not exist'
            )
        logger.info(
            f':: Looking for news files in `{NEWS_DIR}` [{self.current_branch}]'
        )
        self.git.checkout(self.current_branch)
        self.git.set_upstream_branch(self.current_branch)
        self.git.pull()
        current_commit_hash = self.git.get_commit_hash()
        # Delete `master` as it may already exist and be set to the one of interest
        if self.git.branch_exists(self.master_branch):
            self.git.delete_branch(self.master_branch)
        self.git.checkout(self.master_branch)
        self.git.set_upstream_branch(self.master_branch)
        self.git.pull()
        master_branch_commit_hash = self.git.get_commit_hash()
        self.git.checkout(self.current_branch)
        added_news = self.git.get_changes_list(
            'a', self.git.get_branch_point(
                master_branch_commit_hash, current_commit_hash),
            current_commit_hash,
            os.path.relpath(NEWS_DIR,
                            os.path.commonprefix([NEWS_DIR, PROJECT_ROOT]))
        )
        extension_to_exclude = ['.toml', '.rst']
        return [path for path in added_news if
                len([ex for ex in extension_to_exclude if ex in path]) == 0]

    def verify(self):
        """
        Checks that news files were added in the current branch as part of the PR's changes
        The files are then individually checked in order to ensure they follow the standard in terms of naming and content.
        """
        if self.current_branch in [MASTER_BRANCH, BETA_BRANCH] or re.search(
                RELEASE_BRANCH_PATTERN, self.current_branch):
            logger.info(
                f'No need for news file on branch [{self.current_branch}]'
            )
            return
        added_news = self.find_news_file()
        if not added_news or len(added_news) == 0:
            FileNotFoundError(
                f'PR must contain a news file in {NEWS_DIR}. See README.md'
            )
        logger.info(
            f'{len(added_news)} new news files found in `{NEWS_DIR}`'
        )
        logger.info(':: Checking news files format')
        for news_file in added_news:
            NewsFileValidator(news_file).verify()


def main():
    """
    Asserts that the new PR comprises at least one news file and that such file is correct with regards to the standard.
    An exception is raised if a problem with the news file was found.
    """
    parser = argparse.ArgumentParser(
        description='Publish target data report to AWS.')
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Verbosity, by default errors are reported.")
    args = parser.parse_args()
    set_log_level(args.verbose)
    try:
        NewsFileDiscoverer().verify()
    except Exception as e:
        log_exception(logger, e)
        sys.exit(1)


if __name__ == '__main__':
    main()
