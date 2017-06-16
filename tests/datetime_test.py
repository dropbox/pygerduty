from __future__ import absolute_import

import datetime
import httpretty
import pygerduty
import pygerduty.v2
import pytest
import textwrap
import uuid

###################
# Version 1 Tests #
###################

@httpretty.activate
def test_loads_with_datetime():
    body = open('tests/fixtures/incident_resp_v1.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://acme.pagerduty.com/api/v1/incidents/PIJ90N7",
        body=body, status=200
    )

    pd = pygerduty.PagerDuty("acme", "password", parse_datetime=True)
    incident = pd.incidents.show("PIJ90N7")

    assert incident.last_status_change_on == datetime.datetime(2012, 12, 22, 0, 35, 22)
    assert incident.created_on == datetime.datetime(2012, 12, 22, 0, 35, 21)

    assert incident.assigned_to[0].at == datetime.datetime(2012, 12, 22, 0, 35, 21)

    assert incident.pending_actions[0].at == datetime.datetime(2014, 1, 1, 8, 0)
    assert incident.pending_actions[1].at == datetime.datetime(2014, 1, 1, 10, 0)
    assert incident.pending_actions[2].at == datetime.datetime(2014, 1, 1, 11, 0)


@httpretty.activate
def test_loads_without_datetime():
    body = open('tests/fixtures/incident_resp_v1.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://acme.pagerduty.com/api/v1/incidents/PIJ90N7",
        body=body, status=200
    )

    pd = pygerduty.PagerDuty("acme", "password", parse_datetime=False)
    incident = pd.incidents.show("PIJ90N7")

    assert incident.last_status_change_on == "2012-12-22T00:35:22Z"
    assert incident.created_on == "2012-12-22T00:35:21Z"

    assert incident.assigned_to[0].at == "2012-12-22T00:35:21Z"

    assert incident.pending_actions[0].at == "2014-01-01T08:00:00Z"
    assert incident.pending_actions[1].at == "2014-01-01T10:00:00Z"
    assert incident.pending_actions[2].at == "2014-01-01T11:00:00Z"

def test_datetime_encoder_decoder():
    obj = {
        "d": datetime.datetime(2014, 1, 1, 8, 0),
        "s": "string",
        "i": 10,
    }

    # Make sure we can roundtrip
    assert obj == pygerduty._json_loader(pygerduty._json_dumper(obj))

    # Test our encoder uses default properly
    with pytest.raises(TypeError) as excinfo:
        pygerduty._json_dumper({"test": uuid.uuid4()})
    excinfo.match(r"UUID\('.*'\) is not JSON serializable")

###################
# Version 2 Tests #
###################

@httpretty.activate
def test_loads_with_datetime_v2():
    body = open('tests/fixtures/incident_resp_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK",
        body=body, status=200
    )

    pd = pygerduty.v2.PagerDuty("testing", "password", parse_datetime=True)
    incident = pd.incidents.show("PT4KHLK")

    assert incident.last_status_change_at == datetime.datetime(2015, 10, 6, 21, 38, 23)
    assert incident.created_at == datetime.datetime(2015, 10, 6, 21, 30, 42)

    assert incident.assignments[0].at == datetime.datetime(2015, 11, 10, 0, 31, 52)

    assert incident.pending_actions[0].at == datetime.datetime(2015, 11, 10, 1, 2, 52)
    assert incident.pending_actions[1].at == datetime.datetime(2015, 11, 10, 4, 31, 52)


@httpretty.activate
def test_loads_without_datetime_v2():
    body = open('tests/fixtures/incident_resp_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PT4KHLK",
        body=body, status=200
    )

    pd = pygerduty.v2.PagerDuty("acme", "password", parse_datetime=False)
    incident = pd.incidents.show("PT4KHLK")

    assert incident.last_status_change_at == "2015-10-06T21:38:23Z"
    assert incident.created_at == "2015-10-06T21:30:42Z"

    assert incident.assignments[0].at == "2015-11-10T00:31:52Z"

    assert incident.pending_actions[0].at == "2015-11-10T01:02:52Z"
    assert incident.pending_actions[1].at == "2015-11-10T04:31:52Z"


def test_datetime_encoder_decoder_v2():
    obj = {
        "d": datetime.datetime(2014, 1, 1, 8, 0),
        "s": "string",
        "i": 10,
    }

    # Make sure we can roundtrip
    assert obj == pygerduty.common._json_loader(pygerduty.common._json_dumper(obj))

    # Test our encoder uses default properly
    with pytest.raises(TypeError) as excinfo:
        pygerduty.common._json_dumper({"test": uuid.uuid4()})
    excinfo.match(r"UUID\('.*'\) is not JSON serializable")
