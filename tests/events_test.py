import httpretty
import json
import textwrap
import pygerduty.events
import pygerduty.events_v2

from pygerduty.events import INTEGRATION_API_URL
from pygerduty.events_v2 import INTEGRATION_API_URL as INTEGRATION_API_URL_V2
from pygerduty.common import Requester


@httpretty.activate
def test_create_event():
    body = textwrap.dedent("""
    	{
  			"status": "success",
  			"message": "Event processed",
			"incident_key": "srv01/HTTP"
	    }
    """)
    httpretty.register_uri(
        httpretty.POST, INTEGRATION_API_URL,
        body=body, status=200)

    requester = Requester()
    p = pygerduty.events.Events('my_key', requester)
    request_json = open('tests/fixtures/event_request.json').read()

    request = json.loads(request_json)

    response = p.create_event(
        request['description'],
        request['event_type'],
        request['details'],
        request['incident_key'],
    )

    assert response == 'srv01/HTTP'


@httpretty.activate
def test_enqueue_event_v2():
    response = {
        "status": "success",
        "message": "Event processed",
        "dedup_key": "Service (P123456) Test Dedup Key"
    }
    httpretty.register_uri(
        httpretty.POST, INTEGRATION_API_URL_V2,
        body=textwrap.dedent(json.dumps(response)), status=200)

    E = pygerduty.events_v2.Events('fake_integration_key')

    request = {}
    with open('tests/fixtures/event_request_v2.json') as fp:
        request = json.load(fp)

    dedup_key = E.enqueue(**request)
    assert dedup_key == response['dedup_key']
