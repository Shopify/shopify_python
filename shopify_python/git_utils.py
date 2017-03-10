import os
import typing  # pylint: disable=unused-import
from git import repo
from git.refs import head  # pylint: disable=unused-import


class GitUtilsException(Exception):
    pass


def _remote_origin_master(git_repo):
    # type: (repo.Repo) -> head.Head
    remote_master = git_repo.heads.master.tracking_branch()
    if not remote_master or not remote_master.is_valid():
        raise GitUtilsException("Unable to locate remote branch origin/master")
    return remote_master


def _modified_in_branch(git_repo, other_ref):
    # type: (repo.Repo, head.Head) -> typing.List[str]
    commit = git_repo.active_branch.commit
    modified = [x for x in commit.diff(other_ref.commit, R=True) if not x.deleted_file]
    return [x.b_path for x in modified]


def _file_is_python(path):
    # type: (str) -> bool
    if path.endswith('.py'):
        return True
    else:
        _, extension = os.path.splitext(path)
        if not extension:
            try:
                with open(path) as might_be_python:
                    line = might_be_python.readline()
                    return line.startswith('#!') and 'python' in line
            except UnicodeDecodeError:
                pass
        return False


def changed_python_files_in_tree(root_path):
    # type: (str) -> typing.List[str]

    git_repo = repo.Repo(root_path)
    remote_master = _remote_origin_master(git_repo)
    modified = _modified_in_branch(git_repo, remote_master)
    abs_modified = [os.path.join(git_repo.working_dir, x) for x in modified]
    return [mod for (mod, abs_mod) in zip(modified, abs_modified)
            if os.path.exists(abs_mod) and os.path.isfile(abs_mod) and _file_is_python(abs_mod)]
