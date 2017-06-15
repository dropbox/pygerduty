from __future__ import absolute_import

import httpretty
import pygerduty.v2
import textwrap

###################
# Version 2 Tests #
###################

@httpretty.activate
def test_get_incident_v2():
    body = open('tests/fixtures/incident_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK",
        body=body, status=200)
    p = pygerduty.v2.PagerDuty("contosso", "password")
    incident = p.incidents.show("PT4KHLK")

    assert incident.self_ == 'https://api.pagerduty.com/incidents/PT4KHLK'
    assert len(incident.pending_actions) == 2
    assert incident.service.type == 'generic_email_reference'
    assert len(incident.assignments) == 1
