import os
import py  # pylint: disable=unused-import
import pytest
from git import repo
from shopify_python import git_utils


@pytest.fixture
def python_file(main_repo):
    # type: (repo.Repo) -> str
    file_lines = [
        "import os",
        "def foo():",
        "    return 4"
    ]
    file_path = os.path.join(main_repo.working_dir, 'program.py')

    with open(file_path, 'w') as writing_file:
        writing_file.writelines(file_lines)
    return file_path


@pytest.fixture
def python_script(main_repo):
    # type: (repo.Repo) -> str
    file_lines = [
        "#!/usr/bin/env python3",
        "import os",
        "def bar():",
        "    return 6"
    ]
    file_path = os.path.join(main_repo.working_dir, 'program')

    with open(file_path, 'w') as writing_file:
        writing_file.writelines(file_lines)
    return file_path


@pytest.fixture
def non_python_file(main_repo):
    # type: (repo.Repo) -> str
    file_lines = [
        "[MASTER]",
        "",
        "# Minimum lines number of a similarity.",
        "min-similarity-lines=4"
    ]
    file_path = os.path.join(main_repo.working_dir, 'non_program')
    with open(file_path, 'w') as writing_file:
        writing_file.writelines(file_lines)
    return file_path


@pytest.fixture
def remote_repo(tmpdir):
    # type: ('py.path.LocalPath') -> repo.Repo
    return repo.Repo.init(str(tmpdir.join('remote')), bare=True)


@pytest.fixture
def main_repo(tmpdir, remote_repo):
    # type: ('py.path.LocalPath', repo.Repo) -> repo.Repo
    to_dir = str(tmpdir.join('main'))
    new_repo = repo.Repo.clone_from(remote_repo.git_dir, to_dir)

    file_name = os.path.join(new_repo.working_dir, 'new_file')
    open(str(file_name), 'wb').close()
    new_repo.index.add([str(file_name)])
    new_repo.index.commit("initial commit")
    new_repo.remote('origin').push('master')

    return new_repo


def test_detects_changed_python_files(main_repo, python_file, python_script):
    # type: (repo.Repo, str, str) -> None

    main_repo.create_head('foo').checkout()
    main_repo.index.add([python_file, python_script])
    main_repo.index.commit("adding python files")

    changed_files = git_utils.changed_python_files_in_tree(main_repo.working_dir)
    assert sorted(changed_files) == [
        os.path.basename(python_script),
        os.path.basename(python_file),
    ]


def test_doesnt_include_changed_nonpython_files(main_repo, python_file, non_python_file):
    # type: (repo.Repo, str, str) -> None

    main_repo.create_head('foo').checkout()
    main_repo.index.add([python_file, non_python_file])
    main_repo.index.commit("adding mixed files")

    changed_files = git_utils.changed_python_files_in_tree(main_repo.working_dir)
    assert changed_files == [os.path.basename(python_file)]


def test_only_include_modified_locally(main_repo, python_file):
    # type: (repo.Repo, str) -> None

    starting_commit = main_repo.commit()

    # Add a file and push it to origin/master
    origin = main_repo.remote('origin')
    other_file = os.path.join(main_repo.working_dir, 'other_file.py')
    open(other_file, 'w').close()
    main_repo.index.add([other_file])
    remote_master_commit = main_repo.index.commit("adding other file")
    origin.push()

    # Set local master back 1 commit
    main_repo.active_branch.commit = 'HEAD~1'

    # Create a new branch from here, add files
    main_repo.create_head('foo').checkout()
    main_repo.index.add([python_file])
    local_master_commit = main_repo.index.commit("adding python file")

    # current commit should have same parents as remote master (diverged tree)
    assert local_master_commit.parents == [starting_commit]
    assert remote_master_commit.parents == [starting_commit]
    assert local_master_commit != remote_master_commit

    # only the one new file is added
    assert git_utils.changed_python_files_in_tree(main_repo.working_dir) == [os.path.basename(python_file)]


def test_cant_find_remote_origin(main_repo, remote_repo):
    # type: (repo.Repo, repo.Repo) -> None
    main_repo.create_remote('foo', remote_repo.working_dir)
    main_repo.delete_remote('origin')

    with pytest.raises(git_utils.GitUtilsException) as ex:
        git_utils.changed_python_files_in_tree(main_repo.working_dir)
    assert "Unable to locate remote branch origin/master" in ex.exconly()


def test_cant_find_origin_master(main_repo, remote_repo):
    # type: (repo.Repo, repo.Repo) -> None

    remote_foo = remote_repo.create_head('foo')
    remote_repo.head.reference = remote_foo
    remote_repo.delete_head('master')

    main_repo.remotes[0].fetch(prune=True)

    with pytest.raises(git_utils.GitUtilsException) as ex:
        git_utils.changed_python_files_in_tree(main_repo.working_dir)
    assert "Unable to locate remote branch origin/master" in ex.exconly()


def test_dont_include_deleted_files(main_repo, python_file):
    # type: (repo.Repo, str) -> None

    origin = main_repo.remote('origin')
    main_repo.index.add([python_file])
    main_repo.index.commit("adding python file")
    origin.push('master')

    main_repo.create_head('foo').checkout()
    main_repo.index.remove([python_file])
    main_repo.index.commit("removing python file")

    assert git_utils.changed_python_files_in_tree(main_repo.working_dir) == []


def test_include_modified_files(main_repo, python_file):
    # type: (repo.Repo, str) -> None

    origin = main_repo.remote('origin')
    main_repo.index.add([python_file])
    main_repo.index.commit("adding python file")
    origin.push()

    main_repo.create_head('foo').checkout()
    with open(os.path.join(main_repo.working_dir, python_file), 'a') as appending_file:
        appending_file.writelines('# Adding comment at the end')

    main_repo.index.add([python_file])
    main_repo.index.commit("modifying python file")
    assert git_utils.changed_python_files_in_tree(main_repo.working_dir) == [os.path.basename(python_file)]


def test_dont_include_uncommited_or_untracked_files(main_repo, python_file):
    # type: (repo.Repo, str) -> None

    assert os.path.exists(os.path.join(main_repo.working_dir, os.path.basename(python_file)))
    assert git_utils.changed_python_files_in_tree(main_repo.working_dir) == []
    main_repo.index.add([python_file])
    assert git_utils.changed_python_files_in_tree(main_repo.working_dir) == []
    main_repo.index.commit("adding python file")
    assert git_utils.changed_python_files_in_tree(main_repo.working_dir) == [os.path.basename(python_file)]


def test_dont_include_scripts_with_extensions(main_repo):
    # type: (repo.Repo) -> None

    file_path = os.path.join(main_repo.working_dir, 'other_file.sh')
    with open(file_path, 'w') as writing_file:
        writing_file.writelines([
            "#!/usr/bin/env python3",
            "import os",
            "def bar():",
            "    return 6"
        ])
    main_repo.index.add([file_path])
    main_repo.index.commit("adding script file with .sh extension")
    assert git_utils.changed_python_files_in_tree(main_repo.working_dir) == []


def test_dont_include_binary_files(main_repo):
    # type: (repo.Repo) -> None

    file_path = os.path.join(main_repo.working_dir, 'other_file')
    with open(file_path, 'wb') as writing_file:
        writing_file.write(bytearray(b'{\x03\xff\x00d'))
    main_repo.index.add([file_path])
    main_repo.index.commit("adding binary file")
    assert git_utils.changed_python_files_in_tree(main_repo.working_dir) == []


def test_autopep_files(tmpdir):
    # type: ('py.path.LocalPath') -> None
    file_lines = [
        "def foo():\n",
        "    return 1\n",
        "def bar():\n",
        "    return 2\n",
    ]
    file1_path = os.path.join(str(tmpdir), 'file1.py')
    file2_path = os.path.join(str(tmpdir), 'file2.py')
    with open(file1_path, 'w') as file1:
        file1.writelines(file_lines)

    file_lines.insert(2, "\n")
    file_lines.insert(2, "\n")
    assert len(file_lines) == 6

    with open(file2_path, 'w') as file2:
        file2.writelines(file_lines)
    files_to_autopep = [file1_path, file2_path]

    git_utils.autopep_files(files_to_autopep, 79)
    assert len(files_to_autopep) == 2

    for fixed_file in files_to_autopep:
        with open(fixed_file) as file_to_check:
            assert file_to_check.readlines() == file_lines


def test_linter(tmpdir):
    # type: ('py.path.LocalPath') -> None
    open(os.path.join(str(tmpdir), '__init__.py'), 'w')

    file_lines = [
        "def foo():\n",
        "  return 1\n"
    ]
    file_path = os.path.join(str(tmpdir), 'file.py')
    with open(file_path, 'w') as file_to_write:
        file_to_write.writelines(file_lines)

    lint_results = [x for x in git_utils.pylint_files([str(tmpdir)])]

    expected_failure = 'file.py:2: warning (W0311, bad-indentation, ) Bad indentation. Found 2 spaces, expected 4'
    assert lint_results[1].strip().endswith(expected_failure)


def test_linter_with_config(tmpdir):
    # type: ('py.path.LocalPath') -> None
    open(os.path.join(str(tmpdir), '__init__.py'), 'w')

    file_lines = [
        "def my_function():    \n"
        "  return 1\n"
    ]
    python_files = [os.path.join(str(tmpdir), filename) for filename in ['file1.py', 'file2.py']]
    for path in python_files:
        with open(path, 'w') as file_to_write:
            file_to_write.writelines(file_lines)

    pylintrc_lines = [
        "[MESSAGES CONTROL]\n",
        "disable=bad-indentation,missing-docstring\n"
    ]
    pylintrc_path = os.path.join(str(tmpdir), 'pylintrc')
    with open(pylintrc_path, 'w') as rcfile:
        rcfile.writelines(pylintrc_lines)

    msg_template = '"{path}:{line}:{column} {msg_id}({symbol}) {msg}"'
    options = {
        'rcfile': pylintrc_path,
        'ignore': os.path.basename(python_files[0]),
        'msg-template': msg_template,
    }
    lint_results = [x for x in git_utils.pylint_files([str(tmpdir)], **options)]

    assert len(lint_results) == 3
    assert lint_results[1].strip().endswith('file2.py:1: convention (C0303, trailing-whitespace, ) Trailing whitespace')


def test_passing_linter(tmpdir):
    # type: ('py.path.LocalPath') -> None
    open(os.path.join(str(tmpdir), '__init__.py'), 'w')

    file_lines = [
        "def my_function():\n"
        '    """This is a docstring."""\n',
        "    return 1\n"
    ]
    file_path = os.path.join(str(tmpdir), 'file.py')
    with open(file_path, 'w') as file_to_write:
        file_to_write.writelines(file_lines)

    lint_results = [x for x in git_utils.pylint_files([str(tmpdir)])]
    assert lint_results == []
