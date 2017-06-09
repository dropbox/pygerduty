from __future__ import absolute_import

import datetime
import httpretty
import pygerduty
import pygerduty.v2
import pytest
import textwrap
import uuid

INCIDENT_RESPONSE = textwrap.dedent("""\
    {
      "id": "PIJ90N7",
      "incident_number": 1,
      "created_on": "2012-12-22T00:35:21Z",
      "status": "triggered",
      "pending_actions": [
        {
          "type": "escalate",
          "at": "2014-01-01T08:00:00Z"
        },
        {
          "type": "unacknowledge",
          "at": "2014-01-01T10:00:00Z"
        },
        {
          "type": "resolve",
          "at": "2014-01-01T11:00:00Z"
        }
      ],
      "html_url": "https://acme.pagerduty.com/incidents/PIJ90N7",
      "incident_key": null,
      "service": {
        "id": "PBAZLIU",
        "name": "service",
        "description": "service description",
        "html_url": "https://acme.pagerduty.com/services/PBAZLIU"
      },
      "assigned_to_user": {
        "id": "PPI9KUT",
        "name": "Alan Kay",
        "email": "alan@pagerduty.com",
        "html_url": "https://acme.pagerduty.com/users/PPI9KUT"
      },
      "assigned_to": [
        {
          "at": "2012-12-22T00:35:21Z",
          "object": {
            "id": "PPI9KUT",
            "name": "Alan Kay",
            "email": "alan@pagerduty.com",
            "html_url": "https://acme.pagerduty.com/users/PPI9KUT",
            "type": "user"
          }
        }
      ],
      "trigger_summary_data": {
        "subject": "45645"
      },
      "trigger_details_html_url": "https://acme.pagerduty.com/incidents/PIJ90N7/log_entries/PIJ90N7",
      "last_status_change_on": "2012-12-22T00:35:22Z",
      "last_status_change_by": null,
      "urgency": "high"
    }
""")

###################
# Version 1 Tests #
###################

@httpretty.activate
def test_loads_with_datetime():
    httpretty.register_uri(
        httpretty.GET, "https://acme.pagerduty.com/api/v1/incidents/PIJ90N7",
        body=INCIDENT_RESPONSE, status=200
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
    httpretty.register_uri(
        httpretty.GET, "https://acme.pagerduty.com/api/v1/incidents/PIJ90N7",
        body=INCIDENT_RESPONSE, status=200
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
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PIJ90N7",
        body=INCIDENT_RESPONSE, status=200
    )

    pd = pygerduty.v2.PagerDuty("testing", "password", parse_datetime=True)
    incident = pd.incidents.show("PIJ90N7")

    assert incident.last_status_change_on == datetime.datetime(2012, 12, 22, 0, 35, 22)
    assert incident.created_on == datetime.datetime(2012, 12, 22, 0, 35, 21)

    assert incident.assigned_to[0].at == datetime.datetime(2012, 12, 22, 0, 35, 21)

    assert incident.pending_actions[0].at == datetime.datetime(2014, 1, 1, 8, 0)
    assert incident.pending_actions[1].at == datetime.datetime(2014, 1, 1, 10, 0)
    assert incident.pending_actions[2].at == datetime.datetime(2014, 1, 1, 11, 0)


@httpretty.activate
def test_loads_without_datetime_v2():
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/incidents/PIJ90N7",
        body=INCIDENT_RESPONSE, status=200
    )

    pd = pygerduty.v2.PagerDuty("acme", "password", parse_datetime=False)
    incident = pd.incidents.show("PIJ90N7")

    assert incident.last_status_change_on == "2012-12-22T00:35:22Z"
    assert incident.created_on == "2012-12-22T00:35:21Z"

    assert incident.assigned_to[0].at == "2012-12-22T00:35:21Z"

    assert incident.pending_actions[0].at == "2014-01-01T08:00:00Z"
    assert incident.pending_actions[1].at == "2014-01-01T10:00:00Z"
    assert incident.pending_actions[2].at == "2014-01-01T11:00:00Z"

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
