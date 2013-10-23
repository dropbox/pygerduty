import urllib
import urllib2
import urlparse
import base64

try:
    import json
except ImportError:
    import simplejson as json


__author__ = "Gary M. Josack <gary@dropbox.com>"
__version__ = "0.16"


# TODO:
# Support for Log Entries
# Support for Reports


class Error(Exception):
    pass

class IntegrationAPIError(Error):
    def __init__(self, message, event_type):
        self.event_type = event_type
        self.message = message

    def __str__(self):
        return "Creating %s event failed: %s" % (self.event_type,
                                                 self.message)

class BadRequest(Error):
    def __init__(self, payload, *args, **kwargs):
        # Error Reponses don't always contain all fields.
        # Sane defaults must be set.
        self.code = payload["error"].get('code', 99999)
        self.errors = payload["error"].get('errors', [])
        self.message = payload["error"].get('message', "")

        Error.__init__(self, *args, **kwargs)

    def __str__(self):
        return "%s (%s): %s" % (
            self.message, self.code, self.errors)


class NotFound(Error):
    pass


class Collection(object):

    def __init__(self, pagerduty, base_container=None):
        self.name = getattr(self, "name", False) or _lower(self.__class__.__name__)
        self.sname = getattr(self, "sname", False) or _singularize(self.name)
        self.container = (getattr(self, "container", False) or
                          globals()[_upper(self.sname)])

        self.pagerduty = pagerduty
        self.base_container = base_container

    def create(self, **kwargs):
        path = "%s" % self.name
        if self.base_container:
            path = "%s/%s/%s" % (
                self.base_container.collection.name,
                self.base_container.id, self.name)

        data = {self.sname: {}}

        # requester_id needs to be up a level
        if "requester_id" in kwargs:
            data["requester_id"] = kwargs["requester_id"]
            del kwargs["requester_id"]

        data[self.sname] = kwargs

        response = self.pagerduty.request("POST", path, data=json.dumps(data))
        return self.container(self, **response.get(self.sname, {}))

    def update(self, entity_id, **kwargs):
        path = "%s/%s" % (self.name, entity_id)
        if self.base_container:
            path = "%s/%s/%s/%s" % (
                self.base_container.collection.name,
                self.base_container.id, self.name, entity_id)

        data = {self.sname: {}}

        # requester_id needs to be up a level
        if "requester_id" in kwargs:
            data["requester_id"] = kwargs["requester_id"]
            del kwargs["requester_id"]

        data[self.sname] = kwargs

        response = self.pagerduty.request("PUT", path, data=json.dumps(data))
        return self.container(self, **response.get(self.sname, {}))

    def _list_response(self, response):
        entities = []
        for entity in response.get(self.name, []):
            entities.append(self.container(self, **entity))
        return entities

    def list(self, **kwargs):
        path = self.name
        if self.base_container:
            path = "%s/%s/%s" % (
                self.base_container.collection.name,
                self.base_container.id, self.name)
        response = self.pagerduty.request("GET", path, query_params=kwargs)
        return self._list_response(response)

    def count(self, **kwargs):
        path = "%s/count" % self.name
        response = self.pagerduty.request("GET", path, query_params=kwargs)
        return response.get("total", None)

    def show(self, entity_id, **kwargs):
        path = "%s/%s" % (self.name, entity_id)
        if self.base_container:
            path = "%s/%s/%s/%s" % (
                self.base_container.collection.name,
                self.base_container.id, self.name, entity_id)

        response = self.pagerduty.request(
            "GET", path, query_params=kwargs)
        if response.get(self.sname):
            return self.container(self, **response.get(self.sname, {}))
        else:
            return self.container(self, **response)

    def delete(self, entity_id):
        path = "%s/%s" % (self.name, entity_id)
        if self.base_container:
            path = "%s/%s/%s/%s" % (
                self.base_container.collection.name,
                self.base_container.id, self.name, entity_id)

        response = self.pagerduty.request("DELETE", path)
        return response


class MaintenanceWindows(Collection):
    def list(self, **kwargs):
        path = self.name

        if "type" in kwargs:
            path = "%s/%s" % (self.name, kwargs["type"])
            del kwargs["type"]

        response = self.pagerduty.request("GET", path, query_params=kwargs)
        return self._list_response(response)

    def update(self, entity_id, **kwargs):
        path = "%s/%s" % (self.name, entity_id)
        response = self.pagerduty.request("PUT", path, data=json.dumps(kwargs))
        return self.container(self, **response.get(self.sname, {}))


class Incidents(Collection):
    def update(self, requester_id, *args):
        path = "%s" % self.name
        data = {"requester_id": requester_id, self.name: args}
        response = self.pagerduty.request("PUT", path, data=json.dumps(data))
        return self.container(self, **response.get(self.sname, {}))


class Services(Collection):
    def disable(self, entity_id, requester_id):
        path = "%s/%s/disable" % (self.name, entity_id)
        data = {"requester_id": requester_id}
        response = self.pagerduty.request("PUT", path, data=json.dumps(data))
        return response

    def enable(self, entity_id):
        path = "%s/%s/enable" % (self.name, entity_id)
        response = self.pagerduty.request("PUT", path, data="")
        return response

    def regenerate_key(self, entity_id):
        path = "%s/%s/regenerate_key" % (self.name, entity_id)
        response = self.pagerduty.request("POST", path, data="")
        return self.container(self, **response.get(self.sname, {}))


class Alerts(Collection):
    pass


class Overrides(Collection):
    pass


class Entries(Collection):
    pass


class EscalationPolicies(Collection):
    pass


class EscalationRules(Collection):
    def update(self, entity_id, **kwargs):
        path = "%s/%s/%s/%s" % (
            self.base_container.collection.name,
            self.base_container.id, self.name, entity_id)
        response = self.pagerduty.request("PUT", path, data=json.dumps(kwargs))
        return self.container(self, **response.get(self.sname, {}))


class Schedules(Collection):
    def update(self, entity_id, **kwargs):
        path = "%s/%s" % (self.name, entity_id)
        data = {"schedule": kwargs['schedules']
                }
        response = self.pagerduty.request("PUT", path, data=json.dumps(data))
        return self.container(self, **response.get(self.sname, {}))


class ScheduleUsers(Collection):
    pass


class Users(Collection):
    pass


class Restrictions(Collection):
    pass


class NotificationRules(Collection):
    pass


class ContactMethods(Collection):
    pass


class EmailFilters(Collection):
    pass


class Container(object):
    ATTR_NAME_OVERRIDE_KEY = '_attr_name_override'
    def __init__(self, collection, **kwargs):
        # This class depends on the existance on the _kwargs attr.
        # Use object's __setattr__ to initialize.
        object.__setattr__(self, "_kwargs", {})

        self.collection = collection
        self.pagerduty = collection.pagerduty
        self._attr_overrides = kwargs.pop(Container.ATTR_NAME_OVERRIDE_KEY, None)

        def _check_kwarg(key, value):
            if isinstance(value, dict):
                value[Container.ATTR_NAME_OVERRIDE_KEY] = self._attr_overrides
                container = globals().get(_upper(_singularize(key)))
                if container is not None and issubclass(container, Container):
                    _collection = globals().get(_upper(_pluralize(key)),
                                                Collection)
                    return container(_collection(self.pagerduty), **value)
                else:
                    return Container(Collection(self.pagerduty), **value)
            return value

        for key, value in kwargs.iteritems():
            if self._attr_overrides and key in self._attr_overrides:
                key = self._attr_overrides[key]
            if isinstance(value, list):
                self._kwargs[key] = []
                for item in value:
                    sname = _singularize(key)
                    self._kwargs[key].append(_check_kwarg(sname, item))
            else:
                self._kwargs[key] = _check_kwarg(key, value)

    def __getattr__(self, name):
        if name not in self._kwargs:
            raise AttributeError(name)
        return self._kwargs[name]

    def __setattr__(self, name, value):
        if name not in self._kwargs:
            return object.__setattr__(self, name, value)
        self._kwargs[name] = value

    def __str__(self):
        attrs = ["%s=%s" % (k, repr(v)) for k, v in self._kwargs.iteritems()]
        return "<%s: %s>" % (self.__class__.__name__, ", ".join(attrs))

    def __repr__(self):
        return str(self)

    def to_json(self):
        json_dict = {}
        overriden_attrs = dict()
        if self._attr_overrides:
            for key, value in self._attr_overrides.iteritems():
                overriden_attrs[value] = key
        for key, value in self._kwargs.iteritems():
            if key in overriden_attrs:
                key = overriden_attrs[key]
            if isinstance(value, Container):
                json_dict[key] = value.to_json()
            elif isinstance(value, list):
                json_dict[key] = []
                for v in value:
                    json_dict[key].append(v.to_json())
            else:
                json_dict[key] = value
        return json_dict


class Incident(Container):
    pass


class Alert(Container):
    pass


class EmailFilter(Container):
    pass


class MaintenanceWindow(Container):
    pass


class Override(Container):
    pass


class NotificationRule(Container):
    pass


class ContactMethod(Container):
    pass


class EscalationPolicy(Container):
    def __init__(self, *args, **kwargs):
        Container.__init__(self, *args, **kwargs)
        self.escalation_rules = EscalationRules(self.pagerduty, self)


class EscalationRule(Container):
    pass


class RuleObject(Container):
    pass


class ScheduleLayer(Container):
    pass


class Service(Container):
    def __init__(self, *args, **kwargs):
        Container.__init__(self, *args, **kwargs)
        self.email_filters = EmailFilters(self.pagerduty, self)


class Schedule(Container):
    def __init__(self, *args, **kwargs):
        # The json representation of Schedule has a field called
        # "users". Rename it to schedule_users to avoid conflict with
        # Users
        kwargs[Container.ATTR_NAME_OVERRIDE_KEY] = {"users": "schedule_users"}
        Container.__init__(self, *args, **kwargs)
        self.overrides = Overrides(self.pagerduty, self)
        self.users = Users(self.pagerduty, self)
        self.entries = Entries(self.pagerduty, self)


class ScheduleUser(Container):
    pass


class Restriction(Container):
    pass


class User(Container):
    def __init__(self, *args, **kwargs):
        Container.__init__(self, *args, **kwargs)
        self.notification_rules = NotificationRules(self.pagerduty, self)
        self.contact_methods = ContactMethods(self.pagerduty, self)


class Entry(Container):
    pass


class PagerDuty(object):

    INTEGRATION_API_URL =\
        "https://events.pagerduty.com/generic/2010-04-15/create_event.json"

    def __init__(self, subdomain, api_token=None, timeout=10, basic_auth=None):
        if not any([api_token, basic_auth]):
            raise Error("Must use exactly one authentication method.")
        if api_token and basic_auth:
            raise Error("Must use exactly one authentication method.")

        self.api_token = api_token
        self.basic_auth = basic_auth
        self.subdomain = subdomain
        self._host = "%s.pagerduty.com" % subdomain
        self._api_base = "https://%s/api/v1/" % self._host
        self.timeout = timeout

        # Collections
        self.incidents = Incidents(self)
        self.alerts = Alerts(self)
        self.schedules = Schedules(self)
        self.escalation_policies = EscalationPolicies(self)
        self.users = Users(self)
        self.services = Services(self)
        self.maintenance_windows = MaintenanceWindows(self)

    def create_event(self, service_key, description, event_type,
                     details, incident_key):
        headers = {
            "Content-type": "application/json",
        }

        data = {
            "service_key": service_key,
            "event_type": event_type,
            "description": description,
            "details": details,
            "incident_key": incident_key
        }

        request = urllib2.Request(PagerDuty.INTEGRATION_API_URL,
                                  data=json.dumps(data),
                                  headers=headers)
        response = self.execute_request(request)

        if not response["status"] == "success":
            raise IntegrationAPIError(event_type, response["message"])
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
                         incident_key=None, details=None):
        """ Report a new or ongoing problem. When PagerDuty receives a trigger,
        it will either open a new incident, or add a new log entry to an
        existing incident.
        """

        return self.create_event(service_key, description, "trigger",
                                 details, incident_key)

    def execute_request(self, request):
        try:
            response = urllib2.urlopen(request).read()
        except urllib2.HTTPError, err:
            if err.code / 100 == 2:
                response = err.read()
            elif err.code == 400:
                raise BadRequest(json.loads(err.read()))
            elif err.code == 404:
                raise NotFound("URL (%s) Not Found." % request.get_full_url())
            else:
                raise

        try:
            response = json.loads(response)
        except ValueError:
            response = None

        return response

    def request(self, method, path, query_params=None, data=None,
                extra_headers=None):
        auth = None
        if self.api_token:
            auth = "Token token=%s" % self.api_token,
        elif self.basic_auth:
            b64_string = "%s:%s" % self.basic_auth
            auth = "Basic %s" % base64.b64encode(b64_string)

        headers = {
            "Content-type": "application/json",
            "Authorization": auth
        }

        if extra_headers:
            headers.update(extra_headers)

        if query_params is not None:
            query_params = urllib.urlencode(query_params)

        url = urlparse.urljoin(self._api_base, path)
        if query_params:
            url += "?%s" % query_params

        request = urllib2.Request(url, data=data, headers=headers)
        request.get_method = lambda: method.upper()

        return self.execute_request(request)


def _lower(string):
    """Custom lower string function.

    Examples:
        FooBar -> foo_bar
    """
    if not string:
        return ""

    new_string = [string[0].lower()]
    for char in string[1:]:
        if char.isupper():
            new_string.append("_")
        new_string.append(char.lower())

    return "".join(new_string)


def _upper(string):
    """Custom upper string function.

    Examples:
        foo_bar -> FooBar
    """
    return string.title().replace("_", "")


def _singularize(string):
    """Hacky singularization function."""

    if string.endswith("ies"):
        return string[:-3] + "y"
    if string.endswith("s"):
        return string[:-1]
    return string


def _pluralize(string):
    """Hacky pluralization function."""

    if string.endswith("y"):
        return string[:-1] + "ies"
    if not string.endswith("s"):
        return string + "s"
    return string
