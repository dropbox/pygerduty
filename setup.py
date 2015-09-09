#!/usr/bin/env python

from setuptools import setup

with open('pygerduty/version.py') as version_file:
    exec(compile(version_file.read(), version_file.name, 'exec'))

kwargs = {
    "name": "pygerduty-py3",
    "version": str(__version__),  # noqa
    "packages": ["pygerduty"],
    "scripts": ["bin/grab_oncall.py"],
    "description": "Python Client Library for PagerDuty's REST API",
    "author": "Gary M. Josack",
    "author_email": "gary@dropbox.com",
    "license": "MIT",
    "url": "https://github.com/cardforcoin/pygerduty",
    "classifiers": [
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
}

setup(**kwargs)
