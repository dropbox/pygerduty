from __future__ import absolute_import

import httpretty
import pygerduty.v2
import textwrap

###################
# Version 2 Tests #
###################

@httpretty.activate
def test_get_incident_v2():
    body = open('tests/fixtures/get_incident_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK",
        body=body, status=200)
    p = pygerduty.v2.PagerDuty("password")
    incident = p.incidents.show("PT4KHLK")

    assert incident.self_ == 'https://api.pagerduty.com/incidents/PT4KHLK'
    assert len(incident.pending_actions) == 2
    assert incident.service.type == 'generic_email_reference'
    assert len(incident.assignments) == 1


@httpretty.activate
def test_list_incidents_v2():
    body = open('tests/fixtures/incident_list_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents", responses=[
            httpretty.Response(body=body, status=200),
            httpretty.Response(body=textwrap.dedent("""\
                {
                    "limit": 25,
                    "more": false,
                    "offset": 1,
                    "incidents": [],
                    "total": null
                }
            """), status=200),
        ],
    )

    p = pygerduty.v2.PagerDuty("password")
    incidents = [s for s in p.incidents.list()]

    assert len(incidents) == 1
    assert incidents[0].created_at == '2015-10-06T21:30:42Z'
    assert incidents[0].self_ == 'https://api.pagerduty.com/incidents/PT4KHLK'
    assert len(incidents[0].pending_actions) == 2
