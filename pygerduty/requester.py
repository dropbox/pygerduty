# Requester Module used by REST API module as well as EVENTS API module.

import urllib
from v2 import Pagerduty


def execute_request(pagerduty, request):

    try:
        response = (pagerduty.opener.open(request, timeout=pagerduty.timeout).
                    read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        if err.code / 100 == 2:
            response = err.read().decode("utf-8")
        elif err.code == 400:
            raise BadRequest(pagerduty.json_loader(err.read().decode("utf-8")))
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
        response = pagerduty.json_loader(response)
    except ValueError:
        response = None

    return response


