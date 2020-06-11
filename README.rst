
.. image:: https://travis-ci.org/dropbox/pygerduty.svg?branch=master
    :target: https://travis-ci.org/dropbox/pygerduty

=========
Pygerduty
=========

Python Library for PagerDuty's REST API and Events API. This library was originally written to support v1 and
is currently being updated to be compatible with v2 of the API. See "Migrating from v1 to v2" for more details.

This library is currently evolving and backwards compatibility cannot always be guaranteed at this time.


Installation
============

You can install with ``pip install pygerduty``.

If you want to install from source, then ``python setup.py install``.


Requirements
============

Tested on Python 2.7, or >= 3.6.

Known to work on Python 2.6.

Documentation
=============

Pygerduty is a thin wrapper around PagerDuty's APIs. You will need to refer
to the the `PagerDuty Documentation <http://developer.pagerduty.com/>`_ for
all available parameters to pass and all available attributes on responses.

The main methods available to resources are list, show, create, update, and
delete. Not all resources have endpoints for all of the above methods. Again,
refer to the `PagerDuty Documentation <http://developer.pagerduty.com/>`_ to
see all available endpoints.

Top level resources will be accessible via the PagerDuty object and nested
resources available on containers returned from their parent resource.


Migrating from v1 to v2
=======================

In order to allow for a smooth transition between versions 1 and 2 of the library,
version 1 library remains in the file called `__init__.py` inside of the pygerduty directory.
Also in that directory you will see four other files:

- `v2.py` — This file contains all updated logic compatible with v2 of the API.
- `events.py` — PygerDuty also provides an Events API which is separate from the REST API that has had the recent update. Since the logic is mostly disjoint, we have created a new module for logic related to the Events API.
- `common.py` — This file contains all common functions used by both `v2.py` and `events.py`.
- `version.py` — Contains version info.

See the examples below to see how this affects how you will instantiate a client in v2.


Examples
========

Instantiating a client:

Version 1:

::

    import pygerduty
    pager = pygerduty.PagerDuty("foobar", "SOMEAPIKEY123456")

Version 2:

::

    import pygerduty.v2
    pager = pygerduty.v2.PagerDuty("SOMEAPIKEY123456")

Listing a resource:

::

    for schedule in pager.schedules.list():
        print(schedule.id, schedule.name)

    # PX7F8S3 Primary
    # PJ48C0S Tertiary
    # PCJ94SK Secondary

Getting all schedules associated with a user:

::

    user = pager.users.show('PDSKF08')
    for schedule in user.schedules.list():
        print(schedule.id, schedule.name)

    # PDSARUD Ops
    # PTDSKJH Support

Getting a resource by ID:

::

    schedule = pager.schedules.show("PX7F8S3")

Creating a resource:

::

    user = next(pager.users.list(query="gary", limit=1))
    override = schedule.overrides.create(
        start="2012-12-16", end="2012-12-17", user_id=user.id)

Delete a resource:

::

    schedule.overrides.delete(override.id)


Updating a resource:

::

    pagerduty.users.update(user.id, name="Gary Example")


Acknowledging a group by incidents:

::

    me = next(pager.users.list(query="me@you.com", limit=1))
    for incident in pagerduty.incidents.list(status='triggered'):
        incident.acknowledge(requester_id=me.id)
