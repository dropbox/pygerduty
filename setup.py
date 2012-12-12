#!/usr/bin/env python

from distutils.core import setup

kwargs = {
    "name": "pygerduty",
    "version": "0.11",
    "py_modules": ["pygerduty"],
    "data_files": ["README.md", "LICENSE"],
    "description": "Python Client Library for PagerDuty's REST API",
    "author": "Gary M. Josack",
    "author_email": "gary@dropbox.com",
    "license": "MIT",
    "classifiers": [
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
}

setup(**kwargs)
