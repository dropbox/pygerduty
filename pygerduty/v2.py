import copy
import re
import six
from six.moves import urllib
from .common import (
    Requester,
    _lower,
    _upper,
    _singularize,
    _pluralize,
    _json_dumper,
)

__author__ = "Gary M. Josack <gary@dropbox.com>"
from .version import __version__, version_info  # noqa

TRIGGER_LOG_ENTRY_RE = re.compile(
    r'log_entries/(?P<log_entry_id>[A-Z0-9]+)'
)

# TODO:
# Support for Log Entries
# Support for Reports


class Error(Exception):
    pass


class BadRequest(Error):
    def __init__(self, payload, *args, **kwargs):
        # Error Reponses don't always contain all fields.
        # Sane defaults must be set.
        self.code = payload.get("error", {}).get('code', 99999)
        self.errors = payload.get("error", {}).get('errors', [])
        self.message = payload.get("error", {}).get('message', str(payload))

        Error.__init__(self, *args, **kwargs)

    def __str__(self):
        return "{0} ({1}): {2}".format(
            self.message, self.code, self.errors)


class NotFound(Error):
    pass


class Collection(object):
    paginated = True
    default_query_params = {}

    def __init__(self, pagerduty, base_container=None):
        self.name = getattr(self, "name", False) or _lower(self.__class__.__name__)
        self.sname = getattr(self, "sname", False) or _singularize(self.name)
        self.container = (getattr(self, "container", False) or
                          globals()[_upper(self.sname)])

        self.pagerduty = pagerduty
        self.base_container = base_container

    def create(self, **kwargs):
        path = "{0}".format(self.name)
        if self.base_container:
            path = "{0}/{1}/{2}".format(
                self.base_container.collection.name,
                self.base_container.id, self.name)

        data = {self.sname: {}}

        extra_headers = {}
        if "requester_id" in kwargs:
            extra_headers["From"] = kwargs.pop("requester_id")
        new_kwargs = Collection.process_kwargs(kwargs)
        data[self.sname] = new_kwargs
        response = self.pagerduty.request("POST", path, data=_json_dumper(data), extra_headers=extra_headers)
        return self.container(self, **response.get(self.sname, {}))

    @staticmethod
    def process_kwargs(kwargs):
        new_kwargs = {}
        for kwarg_key, kwarg_value in kwargs.items():
            if kwarg_key.endswith('_id'):
                new_key = Collection.cut_suffix(kwarg_key)
                new_kwargs[new_key] = Collection.id_to_obj(new_key, kwarg_value)
            elif kwarg_key.endswith('_ids'):
                new_key = Collection.cut_suffix(kwarg_key)
                new_kwargs[_pluralize(new_key)] = Collection.ids_to_objs(new_key, kwarg_value)
            else:
                new_kwargs[kwarg_key] = kwarg_value
        return new_kwargs

    @staticmethod
    def cut_suffix(key):
        if key.endswith('_id'):
            return key[:-3]
        elif key.endswith('_ids'):
            return key[:-4]
        else:
            return key

    @staticmethod
    def id_to_obj(key, value):
        return {
            "id": value,
            "type": key
        }

    @staticmethod
    def ids_to_objs(key, value):
        new_kwargs = []
        for v in value:
            new_kwarg = Collection.id_to_obj(key, v)
            new_kwargs.append(new_kwarg)
        return new_kwargs

    def _apply_default_kwargs(self, kwargs):
        for k, v in self.default_query_params.items():
            if k not in kwargs:
                kwargs[k] = v
        return kwargs

    def update(self, entity_id, **kwargs):
        path = "{0}/{1}".format(self.name, entity_id)
        if self.base_container:
            path = "{0}/{1}/{2}/{3}".format(
                self.base_container.collection.name,
                self.base_container.id, self.name, entity_id)

        data = {self.sname: {}}

        extra_headers = {}
        if "requester_id" in kwargs:
            extra_headers["From"] = kwargs.pop("requester_id")

        data[self.sname] = kwargs

        response = self.pagerduty.request("PUT", path, data=_json_dumper(data),
                                          extra_headers=extra_headers)
        return self.container(self, **response.get(self.sname, {}))

    def _list_response(self, response):
        entities = []
        for entity in response.get(self.name, []):
            entities.append(self.container(self, **entity))
        return entities

    def _list_no_pagination(self, **kwargs):
        path = self.name
        if self.base_container:
            path = "{0}/{1}/{2}".format(
                self.base_container.collection.name,
                self.base_container.id, self.name)
        suffix_path = kwargs.pop("_suffix_path", None)

        if suffix_path is not None:
            path += "/{0}".format(suffix_path)

        response = self.pagerduty.request("GET", path, query_params=kwargs)

        return self._list_response(response)

    def list(self, **kwargs):
        kwargs = self._apply_default_kwargs(kwargs)
        # Some APIs are paginated. If they are, and the user isn't doing
        # pagination themselves, let's do it for them
        if not self.paginated or any(key in kwargs for key in ('offset', 'limit')):
            for i in self._list_no_pagination(**kwargs):
                yield i

        else:
            offset = 0
            limit = self.pagerduty.page_size
            seen_items = set()
            while True:
                these_kwargs = copy.copy(kwargs)
                these_kwargs.update({
                    'limit': limit,
                    'offset': offset,
                })
                this_paginated_result = self._list_no_pagination(**these_kwargs)

                if not this_paginated_result:
                    break

                for item in this_paginated_result:
                    if item.id in seen_items:
                        continue
                    seen_items.add(item.id)
                    yield item

                offset += len(this_paginated_result)
                if len(this_paginated_result) > limit:
                    # sometimes pagerduty decides to ignore your limit and
                    # just return everything. it seems to only do this when
                    # you're near the last page.
                    break

    def count(self, **kwargs):
        path = "{0}/count".format(self.name)
        response = self.pagerduty.request("GET", path, query_params=kwargs)
        return response.get("total", None)

    def show(self, entity_id, **kwargs):
        kwargs = self._apply_default_kwargs(kwargs)
        path = "{0}/{1}".format(self.name, entity_id)
        if self.base_container:
            path = "{0}/{1}/{2}/{3}".format(
                self.base_container.collection.name,
                self.base_container.id, self.name, entity_id)
        response = self.pagerduty.request(
            "GET", path, query_params=kwargs)

        if response.get(self.sname):
            return self.container(self, **response.get(self.sname, {}))
        else:
            return self.container(self, **response)

    def delete(self, entity_id):
        path = "{0}/{1}".format(self.name, entity_id)
        if self.base_container:
            path = "{0}/{1}/{2}/{3}".format(
                self.base_container.collection.name,
                self.base_container.id, self.name, entity_id)

        response = self.pagerduty.request("DELETE", path)
        return response


class MaintenanceWindows(Collection):
    def list(self, **kwargs):
        path = self.name

        if "type" in kwargs:
            path = "{0}/{1}".format(self.name, kwargs["type"])
            del kwargs["type"]

        response = self.pagerduty.request("GET", path, query_params=kwargs)
        return self._list_response(response)

    def update(self, entity_id, **kwargs):
        path = "{0}/{1}".format(self.name, entity_id)
        response = self.pagerduty.request("PUT", path, data=_json_dumper(kwargs))
        return self.container(self, **response.get(self.sname, {}))


class Incidents(Collection):
    def update(self, requester_id, *args):
        path = "{0}".format(self.name)
        extra_headers = {"From": requester_id}
        data = {self.name: args}
        response = self.pagerduty.request("PUT", path, data=_json_dumper(data), extra_headers=extra_headers)
        return self.container(self, **response.get(self.sname, {}))


class Services(Collection):
    def disable(self, entity_id, requester_id):
        path = "{0}/{1}".format(self.name, entity_id)
        extra_headers = {"From": requester_id}
        data = {"status": "disable"}
        response = self.pagerduty.request("PUT", path, data=_json_dumper(data), extra_headers=extra_headers)
        return response

    def enable(self, entity_id):
        path = "{0}/{1}".format(self.name, entity_id)
        data = {"status": "enable"}
        response = self.pagerduty.request("PUT", path, data=_json_dumper(data))
        return response

    def regenerate_key(self, entity_id):
        path = "{0}/{1}/regenerate_key".format(self.name, entity_id)
        response = self.pagerduty.request("POST", path, data="")
        return self.container(self, **response.get(self.sname, {}))


class Teams(Collection):
    pass


class Alerts(Collection):
    pass


class Overrides(Collection):
    paginated = False


class EscalationPolicies(Collection):
    pass


class EscalationRules(Collection):
    paginated = False

    def update(self, entity_id, **kwargs):
        path = "{0}/{1}/{2}/{3}".format(
            self.base_container.collection.name,
            self.base_container.id, self.name, entity_id)
        response = self.pagerduty.request("PUT", path, data=_json_dumper(kwargs))
        return self.container(self, **response.get(self.sname, {}))


class Schedules(Collection):
    def update(self, entity_id, **kwargs):
        path = "{0}/{1}".format(self.name, entity_id)
        data = {"overflow": kwargs["overflow"],
                "schedule": kwargs["schedule"]}
        response = self.pagerduty.request("PUT", path, data=_json_dumper(data))
        return self.container(self, **response.get(self.sname, {}))


class ScheduleUsers(Collection):
    """This class exists because Users returned from a Schedule query are not
    paginated, whereas responses for Users class are. This causes a pagination
    bug if removed."""
    name = 'users'
    paginated = False


class Users(Collection):
    pass


class Restrictions(Collection):
    pass


class NotificationRules(Collection):
    paginated = False


class ContactMethods(Collection):
    paginated = False


class EmailFilters(Collection):
    pass


class LogEntries(Collection):
    # https://support.pagerduty.com/v1/docs/retrieve-trigger-event-data-using-the-api#section-how-to-obtain-the-data  # noqa
    default_query_params = {'include': ['channels']}


class Notes(Collection):
    paginated = False

    def update(self, *args, **kwargs):
        raise NotImplementedError()

    def count(self, *args, **kwargs):
        raise NotImplementedError()

    def show(self, *args, **kwargs):
        raise NotImplementedError()

    def delete(self, *args, **kwargs):
        raise NotImplementedError()


class Container(object):
    ATTR_NAME_OVERRIDE_KEY = '_attr_name_override'

    def __init__(self, collection, **kwargs):
        # This class depends on the existence on the _kwargs attr.
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

        for key, value in kwargs.items():
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
        attrs = ["{0}={1}".format(k, repr(v)) for k, v in self._kwargs.items()]
        return "<{0}: {1}>".format(self.__class__.__name__, ", ".join(attrs))

    def __repr__(self):
        return str(self)

    def to_json(self):
        json_dict = {}
        overriden_attrs = dict()
        if self._attr_overrides:
            for key, value in self._attr_overrides.items():
                overriden_attrs[value] = key
        for key, value in self._kwargs.items():
            if key in overriden_attrs:
                key = overriden_attrs[key]
            if isinstance(value, Container):
                json_dict[key] = value.to_json()
            elif isinstance(value, list):
                json_dict[key] = []
                for v in value:
                    if isinstance(v, Container):
                        json_dict[key].append(v.to_json())
                    else:
                        json_dict[key].append(v)
            else:
                json_dict[key] = value
        return json_dict


class Incident(Container):
    def __init__(self, *args, **kwargs):
        Container.__init__(self, *args, **kwargs)
        self.log_entries = LogEntries(self.pagerduty, self)
        self.notes = Notes(self.pagerduty, self)

    def _do_action(self, verb, requester, **kwargs):
        path = '{0}/{1}'.format(self.collection.name, self.id)
        data = {
            "incident": {
                "type": "incident_reference",
                "status": verb
            }
        }
        extra_headers = {'From': requester}
        return self.pagerduty.request('PUT', path, data=_json_dumper(data), extra_headers=extra_headers)

    def resolve(self, requester):
        """Resolve this incident.
        :param requester: The email address of the individual acknowledging.
        """
        self._do_action('resolved', requester=requester)

    def acknowledge(self, requester):
        """Acknowledge this incident.
        :param requester: The email address of the individual acknowledging.
        """
        self._do_action('acknowledged', requester=requester)

    def snooze(self, requester, duration):
        """Snooze incident.
        :param requester: The email address of the individual requesting snooze.
        """
        path = '{0}/{1}/{2}'.format(self.collection.name, self.id, 'snooze')
        data = {"duration": duration}
        extra_headers = {"From": requester}
        return self.pagerduty.request('POST', path, data=_json_dumper(data), extra_headers=extra_headers)

    def get_trigger_log_entry(self, **kwargs):
        match = TRIGGER_LOG_ENTRY_RE.search(self.trigger_details_html_url)
        return self.log_entries.show(match.group('log_entry_id'), **kwargs)

    def reassign(self, user_ids, requester):
        """Reassign this incident to a user or list of users

        :param user_ids: A non-empty list of user ids
        :param requester: The email address of individual requesting reassign
        """
        path = '{0}'.format(self.collection.name)
        assignments = []
        if not user_ids:
            raise Error('Must pass at least one user id')
        for user_id in user_ids:
            ref = {
                "assignee": {
                    "id": user_id,
                    "type": "user_reference"
                }
            }
            assignments.append(ref)
        data = {
            "incidents": [
                {
                    "id": self.id,
                    "type": "incident_reference",
                    "assignments": assignments
                }
            ]
        }
        extra_headers = {"From": requester}
        return self.pagerduty.request('PUT', path, data=_json_dumper(data), extra_headers=extra_headers)


class Note(Container):
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
        self.users = ScheduleUsers(self.pagerduty, self)


class ScheduleUser(Container):
    pass


class Team(Container):
    pass


class Restriction(Container):
    pass


class User(Container):
    def __init__(self, *args, **kwargs):
        Container.__init__(self, *args, **kwargs)
        self.notification_rules = NotificationRules(self.pagerduty, self)
        self.contact_methods = ContactMethods(self.pagerduty, self)
        self.schedules = Schedules(self.pagerduty, self)
        self.escalation_policies = EscalationPolicies(self.pagerduty, self)
        self.log_entries = LogEntries(self.pagerduty, self)


class Entry(Container):
    pass


class LogEntry(Container):
    pass


class FinalSchedule(Container):
    pass


class RenderSchedule(Container):
    pass


class PagerDuty(object):
    def __init__(self, api_token, timeout=10, page_size=25,
                 proxies=None, parse_datetime=False):

        self.api_token = api_token
        self._host = "api.pagerduty.com"
        self._api_base = "https://{0}/".format(self._host)
        self.timeout = timeout
        self.page_size = page_size
        self.requester = Requester(timeout=timeout, proxies=proxies, parse_datetime=parse_datetime)

        # Collections
        self.incidents = Incidents(self)
        self.alerts = Alerts(self)
        self.schedules = Schedules(self)
        self.escalation_policies = EscalationPolicies(self)
        self.users = Users(self)
        self.services = Services(self)
        self.maintenance_windows = MaintenanceWindows(self)
        self.teams = Teams(self)
        self.log_entries = LogEntries(self)

    @staticmethod
    def _process_query_params(query_params):
        new_qp = []
        for key, value in query_params.items():
            if isinstance(value, (list, set, tuple)):
                for elem in value:
                    new_qp.append(("{0}[]".format(key), elem))
            else:
                new_qp.append((key, value))

        return urllib.parse.urlencode(new_qp)

    def request(self, method, path, query_params=None, data=None,
                extra_headers=None):

        auth = "Token token={0}".format(self.api_token)
        headers = {
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Content-type": "application/json",
            "Authorization": auth
        }

        if extra_headers:
            headers.update(extra_headers)

        if query_params is not None:
            query_params = self._process_query_params(query_params)

        url = urllib.parse.urljoin(self._api_base, path)

        if query_params:
            url += "?{0}".format(query_params)

        if isinstance(data, six.text_type):
            data = data.encode("utf-8")

        request = urllib.request.Request(url, data=data, headers=headers)
        request.get_method = lambda: method.upper()

        return self.requester.execute_request(request)
