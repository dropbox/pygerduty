# Events module for pygerduty version 2. These methods are compatible with
# Pagerduty Events API.

import urllib
from v2 import (
    Pagerduty,
    IntegrationAPIError,
    INTEGRATION_API_URL,
)

class Events(Pagerduty):
    def create_event(self, service_key, description, event_type,
                     details, incident_key, **kwargs):

        # Only assign client/client_url/contexts if they exist, only for trigger_incident
        client = kwargs.pop('client', None)
        client_url = kwargs.pop('client_url', None)
        contexts = kwargs.pop('contexts', None)

        headers = {
            "Content-type": "application/json",
            "Accept": "application/vnd.pagerduty+json;version=2",
        }

        data = {
            "service_key": service_key,
            "event_type": event_type,
            "description": description,
            "details": details,
            "incident_key": incident_key,
            "client": client,
            "client_url": client_url,
            "contexts": contexts,
        }

        request = urllib.request.Request(PagerDuty.INTEGRATION_API_URL,
                                         data=_json_dumper(data).encode('utf-8'),
                                         headers=headers)
        response = self.execute_request(request)

        if not response["status"] == "success":
            raise IntegrationAPIError(response["message"], event_type)
        return response["incident_key"]


    def resolve_incident(self, service_key, incident_key,
                         description=None, details=None):
        """ Causes the referenced incident to enter resolved state.
        Send a resolve event when the problem that caused the initial
        trigger has been fixed.
        """

        return self.create_event(service_key, description, "resolve",
                                 details, incident_key)

    def acknowledge_incident(self, service_key, incident_key,
                             description=None, details=None):
        """ Causes the referenced incident to enter the acknowledged state.
        Send an acknowledge event when someone is presently working on the
        incident.
        """

        return self.create_event(service_key, description, "acknowledge",
                                 details, incident_key)

    def trigger_incident(self, service_key, description,
                         incident_key=None, details=None,
                         client=None, client_url=None, contexts=None):
        """ Report a new or ongoing problem. When PagerDuty receives a trigger,
        it will either open a new incident, or add a new log entry to an
        existing incident.
        """

        return self.create_event(service_key, description, "trigger",
                                 details, incident_key,
                                 client=client, client_url=client_url, contexts=contexts)


