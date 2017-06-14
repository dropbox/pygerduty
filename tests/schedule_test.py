from __future__ import absolute_import

import httpretty
import pygerduty.v2
import textwrap

@httpretty.activate
def test_get_schedule_v1():
    body = open('tests/fixtures/schedule_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/schedules/PI7DH85",
        body=body, status=200)
    p = pygerduty.v2.PagerDuty("contosso", "password")
    schedule = p.schedules.show("PI7DH85")
    print schedule
    assert schedule.self_ == "https://api.pagerduty.com/schedules/PI7DH85"
    assert len(schedule.schedule_users) == 1
