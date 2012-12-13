#!/usr/bin/env python

from distutils.core import setup

kwargs = {
    "name": "pygerduty",
    "version": "0.11",
    "py_modules": ["pygerduty"],
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
