"""Synchronise the offline target database with the online database.

This utility performs the following actions:
* Downloads the latest online target database
* Saves the database to a local file in the mbed-targets repository
* Creates a new branch and commits the new target database
* Pushes the branch to the mbed-targets remote and raises a github PR as Monty Bot.
"""

import argparse
import datetime
import json
import logging
import sys

from pathlib import Path
from typing import NamedTuple, List

from github import Github, GithubException

from mbed_tools_lib.exceptions import ToolsError
from mbed_tools_lib.logging import log_exception, set_log_level
from mbed_tools_ci_scripts.utils.configuration import configuration, ConfigurationVariable
from mbed_tools_ci_scripts.utils import git_helpers
from mbed_targets.mbed_targets import MbedTargets

logger = logging.getLogger()

TARGET_DATABASE_PATH = Path(
    configuration.get_value(ConfigurationVariable.PROJECT_ROOT), "mbed_targets", "_internal", "data", "targets.json"
)


class PullRequestInfo(NamedTuple):
    """Data structure containing info required to raise a Github PR."""

    repo: str
    head_branch: str
    base_branch: str
    subject: str
    body: str


def save_target_database(target_database_text: str, output_file_path: Path) -> None:
    """Save the target database as a file named targets.json.

    Args:
        target_database_text: json formatted text to save to targets.json

    Returns:
        The path to targets.json.
    """
    output_file_path.parent.mkdir(exist_ok=True)
    output_file_path.write_text(target_database_text)


def diff_objects_from_json_str(incoming_text: str, current_text: str) -> List[dict]:
    """Convert two json strings to objects and take the difference."""
    current = json.loads(current_text)
    incoming = json.loads(incoming_text)
    return [i for i in current + incoming if i not in current or i not in incoming]


def create_new_boards_news_item_text(new_targets: dict) -> str:
    """Create a new news item string from the list of new targets."""
    item_str = "New boards added:"
    board_names = ", ".join(target["attributes"]["board_type"] for target in new_targets)
    return f"{item_str} {board_names}"


def write_news_file(item_text: str, file_name: str) -> Path:
    """Write some text to a news file in the news directory of the repository."""
    news_file_path = Path(configuration.get_value(ConfigurationVariable.PROJECT_ROOT), "news", f"{file_name}.feature")
    inc = 0
    while news_file_path.exists():
        inc += 1
        news_file_path = news_file_path.with_name(f"{file_name}{inc:0=2}.feature")

    news_file_path.write_text(item_text)
    return news_file_path


def git_commit_and_push(files_to_commit: List[Path], branch_name: str, commit_msg: str) -> None:
    """Commit a file to the git remote, on a new branch, as Monty Bot.

    If the given branch doesn't exist then a new branch will be created.

    Args:
        files_to_commit: list of paths to the files to commit.
        branch_name: branch to add the commit to.
        commit_msg: the commit message.
    """
    logger.info(f"Committing '{files_to_commit}' to branch '{branch_name}' with commit message '{commit_msg}'.")
    with git_helpers.ProjectTempClone("master") as temp_clone:
        temp_clone.configure_for_github()
        temp_clone.fetch()
        temp_clone.create_branch(branch_name)
        temp_clone.checkout_branch(branch_name)
        temp_clone.add(files_to_commit)
        temp_clone.commit(commit_msg)
        temp_clone.pull()
        temp_clone.push()


def raise_github_pr(pr_info: PullRequestInfo) -> None:
    """Raise a PR on github using the GIT_TOKEN environment variable to authenticate.

    Args:
        pr_info: data structure containing information about the PR to raise.
    """
    logger.info(f"Raising PR {pr_info!r}")
    git_token = configuration.get_value(ConfigurationVariable.GIT_TOKEN)
    github_instance = Github(git_token)
    repo = github_instance.get_repo(pr_info.repo)
    try:
        repo.create_pull(title=pr_info.subject, body=pr_info.body, head=pr_info.head_branch, base=pr_info.base_branch)
    except GithubException as err:
        logging.info(err.data["errors"][0]["message"])


def parse_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", default=0)
    parser.add_argument("--head-branch", default=f"sync-target-db")
    parser.add_argument("--base-branch", default="master")
    parser.add_argument("--pr-subject", default="Update target database.")
    parser.add_argument("--pr-description", default="")
    return parser.parse_args()


def main(args: argparse.Namespace) -> int:
    """Main entry point."""
    set_log_level(args.verbose)
    pr_info = PullRequestInfo(
        repo="ARMMbed/mbed-targets",
        head_branch=args.head_branch,
        base_branch=args.base_branch,
        subject=args.pr_subject,
        body=args.pr_description,
    )
    try:
        targets = MbedTargets().json_dump()
        if TARGET_DATABASE_PATH.exists():
            diff_objects = diff_objects_from_json_str(targets, TARGET_DATABASE_PATH.read_text())
            if not diff_objects:
                logger.info("No changes to commit. Exiting.")
                return 0
            news_item_text = create_new_boards_news_item_text(diff_objects)
        else:
            news_item_text = "Added offline target database"

        news_file_path = write_news_file(news_item_text, f"{datetime.date.today().strftime('%Y%m%d')}")
        save_target_database(targets, TARGET_DATABASE_PATH)
        git_commit_and_push([TARGET_DATABASE_PATH, news_file_path], pr_info.head_branch, pr_info.subject)
        raise_github_pr(pr_info)
        return 0
    except ToolsError as tools_error:
        log_exception(logger, tools_error)
        return 1


if __name__ == "__main__":
    sys.exit(main(parse_args()))