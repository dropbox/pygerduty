#!/usr/bin/env python

from setuptools import setup

with open('pygerduty/version.py') as version_file:
    exec(compile(version_file.read(), version_file.name, 'exec'))

kwargs = {
    "name": "pygerduty",
    "version": str(__version__),  # noqa
    "packages": ["pygerduty"],
    "scripts": ["bin/grab_oncall.py"],
    "description": "Python Client Library for PagerDuty's REST API",
    "author": "Gary M. Josack",
    "maintainer": "Gary M. Josack",
    "author_email": "gary@dropbox.com",
    "maintainer_email": "gary@dropbox.com",
    "license": "MIT",
    "url": "https://github.com/dropbox/pygerduty",
    "download_url": "https://github.com/dropbox/pygerduty/archive/master.tar.gz",
    "classifiers": [
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
}

setup(**kwargs)
