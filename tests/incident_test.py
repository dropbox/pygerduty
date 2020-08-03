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


@httpretty.activate
def test_verb_action_v2():
    body1 = open('tests/fixtures/incident_get_v2.json').read()
    body2 = open('tests/fixtures/incident_put_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK", responses=[
            httpretty.Response(body=body1, status=200),
            httpretty.Response(body=body2, status=200),
        ],
    )
    httpretty.register_uri(
        httpretty.PUT, "https://api.pagerduty.com/incidents/PT4KHLK",
        body=body2, status=200)
    p = pygerduty.v2.PagerDuty("password")
    incident1 = p.incidents.show('PT4KHLK')
    incident1.acknowledge(requester='eg@sample.com')
    incident2 = p.incidents.show('PT4KHLK')

    assert incident1.acknowledgements == []
    assert incident2.acknowledgements[0].acknowledger.id == 'PXPGF42'


@httpretty.activate
def test_snooze_v2():
    body1 = open('tests/fixtures/incident_get_v2.json').read()
    body2 = open('tests/fixtures/incident_snooze.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK", responses=[
            httpretty.Response(body=body1, status=200),
            httpretty.Response(body=body2, status=200),
        ],
    )

    httpretty.register_uri(
        httpretty.POST, 'https://api.pagerduty.com/incidents/PT4KHLK/snooze',
        body=body2, status=200)

    p = pygerduty.v2.PagerDuty("password")
    incident1 = p.incidents.show('PT4KHLK')
    incident1.snooze(requester='test@dropbox.com', duration=2000)
    incident2 = p.incidents.show('PT4KHLK')

    assert incident2.self_ == "https://api.pagerduty.com/incidents/PT4KHLK"
    assert len(incident2.pending_actions) == 2
    assert incident2.service.type == 'generic_email_reference'
    assert len(incident2.assignments) == 1


@httpretty.activate
def test_reassign_v2():
    body1 = open('tests/fixtures/incident_preassign.json').read()
    body2 = open('tests/fixtures/incident_postassign.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK", responses=[
            httpretty.Response(body=body1, status=200),
            httpretty.Response(body=body2, status=200),
        ],
    )
    body3 = open('tests/fixtures/incident_reassign.json').read()
    httpretty.register_uri(
        httpretty.PUT, 'https://api.pagerduty.com/incidents',
        body=body3, status=200)

    p = pygerduty.v2.PagerDuty("password")
    incident1 = p.incidents.show('PT4KHLK')
    incident1.reassign(user_ids=['PXPGF42', 'PG23GSK'], requester='test@dropbox.com')
    incident2 = p.incidents.show('PT4KHLK')

    assert len(incident1.assignments) == 0
    assert len(incident2.assignments) == 2

@httpretty.activate
def test_log_entries_count():
    body1 = open('tests/fixtures/get_incident_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK",
        body=body1, status=200)

    p = pygerduty.v2.PagerDuty("password")
    incident = p.incidents.show("PT4KHLK")
    assert str(incident.id) == "PT4KHLK"
    assert incident.created_at == '2015-10-06T21:30:42Z'

    body2 = open('tests/fixtures/incident_log_entries.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK/log_entries",
        body=body2, status=200)

    total = incident.log_entries.count()
    assert total == 12
    
@httpretty.activate
def test_log_entries_list_offset():
    body1 = open('tests/fixtures/get_incident_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK",
        body=body1, status=200)

    p = pygerduty.v2.PagerDuty("password")
    incident = p.incidents.show("PT4KHLK")
    assert str(incident.id) == "PT4KHLK"
    assert incident.created_at == '2015-10-06T21:30:42Z'

    body2 = open('tests/fixtures/incident_log_entries.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK/log_entries",
        body=body2, status=200)

    log_entries = [i for i in incident.log_entries.list(offset=0,limit=25)]
    assert len(log_entries) == 12
    assert log_entries[0].created_at == '2019-01-01T00:57:11Z'
    assert log_entries[0].self_ == 'https://api.pagerduty.com/log_entries/RP2836ITHU9F3ADA1T9MF3F97O'

@httpretty.activate
def test_log_entries_list():
    body1 = open('tests/fixtures/get_incident_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK",
        body=body1, status=200)

    p = pygerduty.v2.PagerDuty("password")
    incident = p.incidents.show("PT4KHLK")
    assert str(incident.id) == "PT4KHLK"
    assert incident.created_at == '2015-10-06T21:30:42Z'

    body2 = open('tests/fixtures/incident_log_entries.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK/log_entries",
        responses=[
            httpretty.Response(body=body2, status=200),
            httpretty.Response(body=textwrap.dedent("""\
                {
                    "limit": 25,
                    "more": false,
                    "offset": 13,
                    "log_entries": [],
                    "total": null
                }
            """), status=200)
        ]
    )

    log_entries = [i for i in incident.log_entries.list()]
    assert len(log_entries) == 12
    assert log_entries[0].created_at == '2019-01-01T00:57:11Z'
    assert log_entries[0].self_ == 'https://api.pagerduty.com/log_entries/RP2836ITHU9F3ADA1T9MF3F97O'
