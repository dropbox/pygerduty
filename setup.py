#!/usr/bin/env python

from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ["-v", "-r a"]
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        sys.exit(pytest.main(self.test_args))


with open('pygerduty/version.py') as version_file:
    exec(compile(version_file.read(), version_file.name, 'exec'))

kwargs = {
    "name": "pygerduty",
    "version": str(__version__),  # noqa
    "packages": ["pygerduty"],
    "scripts": ["bin/grab_oncall.py"],
    "description": "Python Client Library for PagerDuty's REST API",
    "author": "Mike Cugini",
    "maintainer": "Mike Cugini",
    "author_email": "cugini@dropbox.com",
    "maintainer_email": "cugini@dropbox.com",
    "license": "MIT",
    "url": "https://github.com/dropbox/pygerduty",
    "download_url": "https://github.com/dropbox/pygerduty/archive/master.tar.gz",
    "classifiers": [
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    "install_requires": ["six"],
    "tests_require": [
        "httpretty<1",
        "pytest>=3.0,<5.0",
        "pyparsing<3",
        "zipp<2",
    ],
    "cmdclass": {"test": PyTest}
}

setup(**kwargs)
