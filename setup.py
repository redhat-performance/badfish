""" Setup script for the badfish application.

"""
from distutils import log
from itertools import chain
from os import walk
from os.path import join
from subprocess import check_call
from subprocess import CalledProcessError

from setuptools import Command
from setuptools import find_packages
from setuptools import setup


def _listdir(root):
    """ Recursively list all files under 'root'.

    """
    for path, _, names in walk(root):
        yield path, tuple(join(path, name) for name in names)
    return


_DATA = "etc/",

_CONFIG = {
    "name": "badfish",
    "author": "Gonzalo Rafuls",
    "author_email": "grafuls@gmail.com",
    "url": "",
    "package_dir": {"": "src"},
    "packages": find_packages("src"),
    "entry_points": {
        "console_scripts": ("cli = badfish.cli:main",),
    },
    "data_files": list(chain.from_iterable(_listdir(root) for root in _DATA))
}


def _version():
    """ Get the local package version.

    """
    path = join("src", _CONFIG["name"], "__version__.py")
    namespace = {}
    with open(path) as stream:
        exec(stream.read(), namespace)
    return namespace["__version__"]


class _CustomCommand(Command):
    """ Abstract base class for a custom setup command.

    """
    # Each user option is a tuple consisting of the option's long name (ending
    # with "=" if it accepts an argument), its single-character alias, and a
    # description.
    description = ""
    user_options = []  # this must be a list

    def initialize_options(self):
        """ Set the default values for all user options.

        """
        return

    def finalize_options(self):
        """ Set final values for all user options.

        This is run after all other option assignments have been completed
        (e.g. command-line options, other commands, etc.)

        """
        return

    def run(self):
        """ Execute the command.

        Raise SystemExit to indicate failure.

        """
        raise NotImplementedError


class UpdateCommand(_CustomCommand):
    """ Custom setup command to pull from a remote branch.

    """
    description = "update from a remote branch"
    user_options = [
        ("remote=", "r", "remote name [default: tracking remote]"),
        ("branch=", "b", "branch name [default: tracking branch]"),
    ]

    def initialize_options(self):
        """ Set the default values for all user options.

        """
        self.remote = ""  # default to tracking remote
        self.branch = ""  # default to tracking branch
        return

    def run(self):
        """ Execute the command.

        """
        args = {"remote": self.remote, "branch": self.branch}
        cmdl = "git pull --ff-only {remote:s} {branch:s}".format(**args)
        try:
            check_call(cmdl.split())
        except CalledProcessError:
            raise SystemExit(1)
        log.info("package version is now {:s}".format(_version()))
        return


def main():
    """ Execute the setup commands.

    """
    _CONFIG["version"] = _version()
    _CONFIG["cmdclass"] = {"update": UpdateCommand}
    setup(**_CONFIG)
    return 0


# Make the script executable.

if __name__ == "__main__":
    raise SystemExit(main())
