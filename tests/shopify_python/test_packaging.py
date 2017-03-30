from __future__ import print_function

import contextlib
import subprocess
import typing  # pylint: disable=unused-import

from git import repo
import py  # pylint: disable=unused-import
import pytest


@pytest.fixture
def package_source_root(tmpdir):
    # type: ('py.path.LocalPath') -> 'py.path.LocalPath'
    root = tmpdir.join('test_packaging')

    root.join('setup.py').write("""
import setuptools
setuptools.setup(
    name='test_packaging',
    install_requires=[
        'shopify_python'
    ],
    entry_points={
        'egg_info.writers': [
            'git_sha.txt = shopify_python.packaging:write_package_revision',
        ],
    }
)
    """, ensure=True)
    return root


@pytest.fixture
def git_package_root(package_source_root):
    # type: ('py.path.LocalPath') -> 'py.path.LocalPath'
    package_repo = repo.Repo.init(str(package_source_root))
    package_repo.index.add(['setup.py'])
    package_repo.index.commit('initial commit')
    return package_source_root


@pytest.fixture
def revision_file_contents():
    # type: () -> str
    return '0080d5ea79fa9513cd7a1b5aeef19858cf52430f'


@pytest.fixture
def package_root_with_revision_file(package_source_root, revision_file_contents):
    # type: ('py.path.LocalPath', str) -> 'py.path.LocalPath'
    package_source_root.join('REVISION').write(revision_file_contents)
    return package_source_root


@contextlib.contextmanager
def package_installed(path, develop_mode):
    # type: ('py.path.LocalPath', bool) -> typing.Iterator[None]

    # sdist is what initializes the egg-info.
    try:
        subprocess.check_output(['python', 'setup.py', 'sdist'], cwd=str(path))
    except subprocess.CalledProcessError as exc:
        print(exc.output)
        raise

    base_command = ['pip', 'install']
    flags = ['-e'] if develop_mode else []
    arguments = [str(path)]

    try:
        subprocess.check_output(base_command + flags + arguments)
    except subprocess.CalledProcessError as exc:
        print(exc.output)
        raise

    yield

    try:
        subprocess.check_output(['pip', 'uninstall', '-y', 'test_packaging'])
    except subprocess.CalledProcessError as exc:
        print(exc.output)
        raise


# We can't just call shopify_python.packaging.get_package_revision within the current interpreter because pkg_resources
# initializes its DB of package info when first invoked and then doesn't update (after, for example, we install the
# test package).
def call_get_package_revision():
    # type: () -> str
    return str(subprocess.check_output(['python', '-c', '\n'.join([
        "import shopify_python.packaging",
        "print(shopify_python.packaging.get_package_revision('test-packaging'))"
    ])]).decode()).strip()


@pytest.mark.parametrize('develop_mode', [True, False])
def test_git_package(develop_mode, git_package_root):
    # type: (bool, 'py.path.LocalPath') -> None
    git_sha = str(repo.Repo(str(git_package_root)).commit())
    with package_installed(git_package_root, develop_mode=develop_mode):
        assert git_sha == call_get_package_revision()


@pytest.mark.parametrize('develop_mode', [True, False])
def test_with_revision_file(develop_mode, package_root_with_revision_file, revision_file_contents):
    # type: (bool, 'py.path.LocalPath', str) -> None
    with package_installed(package_root_with_revision_file, develop_mode=develop_mode):
        assert revision_file_contents == call_get_package_revision()


@pytest.mark.parametrize('develop_mode', [True, False])
def test_without_revision_info(develop_mode, package_source_root):
    # type: (bool, 'py.path.LocalPath') -> None
    with package_installed(package_source_root, develop_mode=develop_mode):
        assert call_get_package_revision() == ''


def test_uninstalled_package():
    # type: () -> None
    assert call_get_package_revision() == ''
