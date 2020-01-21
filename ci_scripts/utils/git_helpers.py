import subprocess
import os
from .definitions import ENVVAR_GIT_TOKEN, REMOTE_ALIAS


class GitWrapper(object):
    def git_url_ssh_to_https(self, url: str):
        """Convert a git url
        url will look like
        https://github.com/ARMmbed/mbed-cloud-api-contract.git
        or
        git@github.com:ARMmbed/mbed-cloud-api-contract.git
        we want:
        https://${GH_TOKEN}@github.com/ARMmbed/mbed-cloud-api-contract.git
        """
        path = url.split('github.com', 1)[1][1:].strip()
        new = 'https://{GITHUB_TOKEN}@github.com/%s' % path
        print('rewriting git url to: %s' % new)
        return new.format(GH_TOKEN=os.getenv(ENVVAR_GIT_TOKEN))

    def checkout(self, branch):
        subprocess.check_call(['git', 'checkout', '-f', branch])

    def add(self, path):
        if isinstance(path, list):
            for element in path:
                self.add(element)
        else:
            subprocess.check_call(['git', 'add', path])

    def commit(self, message):
        subprocess.check_call(['git', 'commit', '-m', message])

    def get_current_branch(self):
        return subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode(
            'utf-8').strip()

    def get_commit_count(self):
        return subprocess.check_output(
            ['git', 'rev-list', '--count', 'HEAD']).decode('utf-8').strip()

    def get_commit_hash(self):
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode(
            'utf-8').strip()

    def get_branch_point(self, commit1, commit2):
        return subprocess.check_output(
            ['git', 'merge-base', commit1, commit2]).decode('utf-8').strip()

    def merge(self, branch):
        subprocess.check_call(
            ['git', 'merge', '--no-commit', '--strategy-option', 'theirs',
             branch])
        self.commit('Merge from %s' % branch)

    def get_remote_url(self):
        return subprocess.check_output(
            ['git', 'remote', 'get-url', REMOTE_ALIAS]).decode('utf-8').strip()

    def cherry_pick(self, commit_hash):
        subprocess.check_call(['git', 'cherry-pick', commit_hash])

    def set_remote_url(self, url):
        subprocess.check_call(['git', 'remote', 'set-url', REMOTE_ALIAS, url])

    def get_remote_branch(self, branch):
        return '%s/%s' % (REMOTE_ALIAS, branch)

    def set_upstream_branch(self, branch):
        subprocess.check_call(
            ['git', 'branch', '--set-upstream-to',
             self.get_remote_branch(branch)])

    # the output of the git command looks like:
    # 'A       docs/news/789.feature'
    def get_changes(self, commit1, commit2, dir=None):
        diff_command = ['git', 'diff', '%s...%s' % (commit1, commit2),
                        '--name-status']
        if dir:
            diff_command.append(dir)
        return subprocess.check_output(diff_command).decode('utf-8')

    def delete_branch(self, branch):
        subprocess.check_call(['git', 'branch', '-D', branch])

    def branch_exists(self, branch):
        branches = subprocess.check_output(['git', 'branch']).decode(
            'utf-8').strip()
        return len([line for line in branches.splitlines() if
                    line.replace('*', '').split() == branch.split()]) > 0

    def get_changes_list(self, change_type, commit1, commit2, dir=None):
        file_diff = self.get_changes(commit1, commit2, dir)
        return [(line.strip()[len(change_type):]).strip() for line in
                file_diff.splitlines() if
                line.lower().strip().startswith(change_type)]

    def push(self):
        subprocess.check_call(['git', 'push', '--follow-tags'])

    def pull(self):
        subprocess.check_call(['git', 'pull', '--quiet'])

    def force_pull(self):
        subprocess.check_call(['git', 'pull', '--force', '--quiet'])

    def push_tag(self):
        subprocess.check_call(['git', 'push', '-f', '--tags'])

    def force_push(self):
        subprocess.check_call(['git', 'push', '-f'])

    def force_push_tag(self):
        subprocess.check_call(['git', 'push', '-f', '--tags'])

    def setup_env(self):
        subprocess.check_call(
            ['git', 'config', '--global', 'user.name', 'monty-bot'])
        subprocess.check_call(
            ['git', 'config', '--global', 'user.email', 'monty-bot@arm.com'])
        self.set_remote_url(self.git_url_ssh_to_https(self.get_remote_url()))
