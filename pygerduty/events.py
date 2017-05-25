from v2 import Pagerduty

class IncidentManager(Pagerduty):
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


