#!/usr/bin/env python

from distutils.core import setup

kwargs = {
    "name": "pygerduty",
    "version": "0.1",
    "py_modules": ["pygerduty"],
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
