import os
import sys
import typing  # pylint: disable=unused-import
import autopep8
from git import repo
from git.refs import head  # pylint: disable=unused-import
from pylint import lint
from pylint import utils  # pylint: disable=unused-import
from pylint.reporters import text


class GitUtilsException(Exception):
    pass


def _remote_origin_master(git_repo):
    # type: (repo.Repo) -> head.Head
    remote_master = git_repo.heads.master.tracking_branch()
    if not remote_master or not remote_master.is_valid():
        raise GitUtilsException("Unable to locate remote branch origin/master")
    return remote_master


def _modified_in_branch(git_repo, other_ref):
    # type: (repo.Repo, head.Head) -> typing.Sequence[str]
    common_commit = git_repo.merge_base(git_repo.active_branch, other_ref)[0]
    diffs = common_commit.diff(git_repo.active_branch.commit)
    changed_files = []
    for diff in diffs:
        if not diff.deleted_file:
            changed_files.append(diff.b_path)
    return changed_files


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


# Options are defined here: https://pypi.python.org/pypi/autopep8#usage
_AutopepOptions = typing.NamedTuple('_AutopepOptions', [  # pylint: disable=global-variable,invalid-name
    ('aggressive', int),
    ('diff', bool),
    ('exclude', typing.Set[typing.List[str]]),
    ('experimental', bool),
    ('global_config', typing.Optional[typing.List[str]]),
    ('ignore', str),
    ('ignore_local_config', bool),
    ('in_place', bool),
    ('indent_size', int),
    ('jobs', int),
    ('line_range', typing.Optional[typing.Sequence]),
    ('list_fixes', bool),
    ('max_line_length', int),
    ('pep8_passes', int),
    ('recursive', bool),
    ('select', typing.Set[str]),
    ('verbose', int),
])


def autopep_files(files, max_line_length):
    # type: (typing.List[str], int) -> None
    files = files[:]
    options = _AutopepOptions(aggressive=1,  # pylint:disable=not-callable
                              diff=False,
                              exclude=set(),
                              experimental=False,
                              global_config=None,
                              ignore='',
                              ignore_local_config=False,
                              in_place=True,
                              indent_size=4,
                              jobs=0,
                              line_range=None,
                              list_fixes=False,
                              max_line_length=max_line_length,
                              pep8_passes=-1,
                              recursive=False,
                              select={'W', 'E'},
                              verbose=0)
    autopep8.fix_multiple_files(files, options, sys.stdout)


class _CustomPylintReporter(text.ColorizedTextReporter):

    def __init__(self):
        # type: () -> None
        super(_CustomPylintReporter, self).__init__()
        self.raw_messages = []  # type: typing.List[utils.Message]

    def handle_message(self, msg):
        # type: (utils.Message) -> None
        self.raw_messages.append(msg)
        super(_CustomPylintReporter, self).handle_message(msg)


def pylint_files(files, **kwargs):
    # type: (typing.List[str], **str) -> typing.Iterable[utils.Message]
    kwargs['reports'] = 'n'
    pylint_args = ["--{}={}".format(key, value) for key, value in kwargs.items()]

    reporter = _CustomPylintReporter()
    lint.Run(files + pylint_args, exit=False, reporter=reporter)

    return reporter.raw_messages
