# Requester Module used by REST API module as well as EVENTS API module.
import datetime
import functools
import json
from six import string_types
from six.moves import urllib

ISO8601_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


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


class Requester(object):
    def __init__(self, timeout=10, proxies=None, parse_datetime=False):
        self.timeout = timeout
        self.json_loader = json.loads

        if parse_datetime:
            self.json_loader = _json_loader

        handlers = []
        if proxies:
            handlers.append(urllib.request.ProxyHandler(proxies))
        self.opener = urllib.request.build_opener(*handlers)

    def execute_request(self, request):

        try:
            response = (self.opener.open(request, timeout=self.timeout).
                        read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code / 100 == 2:
                response = err.read().decode("utf-8")
            elif err.code == 400:
                raise BadRequest(self.json_loader(err.read().decode("utf-8")))
            elif err.code == 403:
                raise
            elif err.code == 404:
                raise NotFound("URL ({0}) Not Found.".format(
                    request.get_full_url()))
            elif err.code == 429:
                raise
            else:
                raise

        try:
            response = self.json_loader(response)
        except ValueError:
            response = None

        response = clean_response(response)

        return response


def clean_response(response):
    '''Recurse through dictionary and replace any keys "self" with
    "self_"'''
    if type(response) is list:
        for elem in response:
            clean_response(elem)
    elif type(response) is dict:
        for key, val in response.items():
            if key == 'self':
                val = response.pop('self')
                response['self_'] = val
                clean_response(val)
            else:
                clean_response(response[key])
    return response


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


class _DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.strftime(ISO8601_FORMAT)
        super(_DatetimeEncoder, self).default(obj)


def _datetime_decoder(obj):
    for k, v in obj.items():
        if isinstance(v, string_types):
            try:
                obj[k] = datetime.datetime.strptime(v, ISO8601_FORMAT)
            except ValueError:
                pass
    return obj


_json_dumper = functools.partial(json.dumps, cls=_DatetimeEncoder)
_json_loader = functools.partial(json.loads, object_hook=_datetime_decoder)
