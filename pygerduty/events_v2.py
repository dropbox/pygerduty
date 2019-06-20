# These methods are compatible with Pagerduty Events API v2
#  - https://v2.developer.pagerduty.com/docs/events-api-v2
#  - https://support.pagerduty.com/docs/pd-cef

from six.moves import urllib
from .exceptions import Error, IntegrationAPIError, BadRequest, NotFound
from .common import (
    _json_dumper,
    Requester,
)


INTEGRATION_API_URL = "https://events.pagerduty.com/v2/enqueue"


class Events(object):
    def __init__(self, routing_key, requester=None):
        self.routing_key = routing_key
        self.headers = {
            "Content-type": "application/json",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "X-Routing-Key": self.routing_key
        }
        if requester is None:
            self.requester = Requester()
        else:
            self.requester = requester

    def enqueue(self, **kwargs):
        # Required (according to documentation) PD-CEF fields
        data = {"event_action": kwargs['event_action']}
        data['payload'] = kwargs.get('payload', {})
        for key in ['summary', 'source', 'severity']:
            if key in kwargs:
                data['payload'][key] = kwargs[key]
            elif key not in data['payload']:
                raise KeyError(key)

        # Optional event fields
        for key in ['dedup_key', 'routing_key', 'images', 'links']:
            if key in kwargs.keys():
                data[key] = kwargs[key]

        # Optional PD-CEF fields
        for key in ['component', 'group', 'class',
                    'custom_details', 'timestamp']:
            if key in kwargs.keys():
                data['payload'][key] = kwargs[key]

        request = urllib.request.Request(INTEGRATION_API_URL,
                                         data=_json_dumper(data).encode('utf-8'),
                                         headers=self.headers)
        response = self.requester.execute_request(request)

        if not response.get("status", "failure") == "success":
            raise IntegrationAPIError(response["message"], kwargs['event_action'])
        return response["dedup_key"]

    def resolve_incident(self, **kwargs):
        """ Causes the referenced incident to enter resolved state.
        Send a resolve event when the problem that caused the initial
        trigger has been fixed.
        """
        kwargs['event_action'] = 'resolve'
        return self.enqueue(**kwargs)

    def acknowledge_incident(self, **kwargs):
        """ Causes the referenced incident to enter the acknowledged state.
        Send an acknowledge event when someone is presently working on the
        incident.
        """
        kwargs['event_action'] = 'acknowledge'
        return self.enqueue(**kwargs)

    def trigger_incident(self, **kwargs):
        """ Report a new or ongoing problem. When PagerDuty receives a trigger,
        it will either open a new incident, or add a new log entry to an
        existing incident.
        """
        kwargs['event_action'] = 'trigger'
        return self.enqueue(**kwargs)
