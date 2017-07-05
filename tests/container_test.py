from __future__ import absolute_import

import pygerduty
import pygerduty.v2

###################
# Version 1 Tests #
###################

def test_to_json_v1():
    p = pygerduty.PagerDuty("contosso", "password")
    collection = pygerduty.Collection(p)

    container1 = pygerduty.Container(collection, name='first')
    container2 = pygerduty.Container(collection, container=container1)

    assert {'container': {'name': 'first'}} == container2.to_json()


def test_to_json_list_convertion_v1():
    p = pygerduty.PagerDuty("contosso", "password")
    collection = pygerduty.Collection(p)

    container = pygerduty.Container(collection, handlers=['first', 'second'])
    assert {'handlers': ['first', 'second']} == container.to_json()

###################
# Version 2 Tests #
###################


def test_to_json_v2():
    p = pygerduty.v2.PagerDuty("password")
    collection = pygerduty.v2.Collection(p)

    container1 = pygerduty.v2.Container(collection, name='test1')
    container2 = pygerduty.v2.Container(collection, container=container1)

    assert {'container': {'name': 'test1'}} == container2.to_json()


def test_to_json_list_convertion_v2():
    p = pygerduty.v2.PagerDuty("password")
    collection = pygerduty.Collection(p)

    container = pygerduty.v2.Container(collection, handlers=['test1', 'test2'])

    assert {'handlers': ['test1', 'test2']} == container.to_json()
