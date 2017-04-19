import os.path
import subprocess

import pkg_resources
import setuptools  # pylint: disable=unused-import


def get_package_revision(package_name):
    # type: (str) -> str
    """Determine the Git commit hash for the Shopify package.

    If the package is installed in "develop" mode the SHA is retrieved using Git. Otherwise it will be retrieved from
    the package's Egg metadata. Returns an empty string if the package is not installed or does not contain revision
    information.
    """
    egg_info = pkg_resources.working_set.find(pkg_resources.Requirement.parse(package_name))
    if egg_info is None:
        return ''
    if os.path.exists(os.path.join(egg_info.location, '.git')):
        return str(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=egg_info.location).decode()).strip()
    if egg_info.has_metadata('git_sha.txt'):
        return egg_info.get_metadata('git_sha.txt')

    return ''


def write_package_revision(cmd, _, filename):
    # type: (setuptools.Command, str, str) -> None
    """Write the Git commit hash for the package that is currently being built.

    If the build is not occurring from a Git checkout the current revision must be stored in a text file named
    "REVISION".

    This function should not be called except via setuptools, by specifying an 'egg_info.writers' entrypoint as follows:

        setuptools.setup(
            name='test_packaging',
            ...
            install_requires=[
                'shopify_python'
            ],
            ...
            entry_points={
                'egg_info.writers': [
                    'git_sha.txt = shopify_python.packaging:write_package_revision',
                ],
            }
            ...
        )

    """
    git_sha = None
    if os.path.exists('.git'):
        git_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    elif os.path.exists('REVISION'):
        with open('REVISION') as revision_file:
            git_sha = revision_file.read().strip()
    if git_sha is not None:
        cmd.write_or_delete_file("Git SHA", filename, git_sha)
