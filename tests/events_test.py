import httpretty
import json
import textwrap
import pygerduty.events

from pygerduty.events import INTEGRATION_API_URL
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

