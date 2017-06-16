from __future__ import absolute_import

import httpretty
import pygerduty.v2
import textwrap

###################
# Version 2 Tests #
###################

@httpretty.activate
def test_get_schedule_v2():
    body = open('tests/fixtures/schedule_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/schedules/PI7DH85",
        body=body, status=200)
    p = pygerduty.v2.PagerDuty("contosso", "password")
    schedule = p.schedules.show("PI7DH85")

    assert schedule.self_ == "https://api.pagerduty.com/schedules/PI7DH85"
    assert len(schedule.schedule_users) == 1
    assert len(schedule.schedule_layers) == 1
    assert schedule.schedule_layers[0].start == "2015-11-06T21:00:00-05:00"


@httpretty.activate
def test_list_schedules_v2():
    body = open('tests/fixtures/schedule_list_v2.json').read()
    httpretty.register_uri(
	    httpretty.GET, "https://api.pagerduty.com/schedules",
	    body=body, status=200)
    p = pygerduty.v2.PagerDuty("contosso", "password")
    schedules = [s for s in p.schedules.list()]

    assert len(schedules) == 1
    assert schedules[0].name == 'Daily Engineering Rotation'
    assert schedules[0].self_ == 'https://api.pagerduty.com/schedules/PI7DH85'
    assert len(schedules[0].escalation_policies) == 1
