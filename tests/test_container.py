from __future__ import absolute_import

import pygerduty


def test_to_json():
    p = pygerduty.PagerDuty("contosso", "password")
    collection = pygerduty.Collection(p)

    container1 = pygerduty.Container(collection, name='first')
    container2 = pygerduty.Container(collection, container=container1)

    assert {'container': {'name': 'first'}} == container2.to_json()


def test_to_json_list_convertion():
    p = pygerduty.PagerDuty("contosso", "password")
    collection = pygerduty.Collection(p)

    container = pygerduty.Container(collection, handlers=['first', 'second'])
    assert {'handlers': ['first', 'second']} == container.to_json()
