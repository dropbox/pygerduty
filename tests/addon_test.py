from __future__ import absolute_import

import httpretty
import pygerduty
import pygerduty.v2


###################
# Version 2 Tests #
###################

@httpretty.activate
def test_get_addon_v2():
    body = open('tests/fixtures/addon_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/addons/PKX7F81",
        body=body, status=200)

    p = pygerduty.v2.PagerDuty("password")
    addon = p.addons.show("PKX7F81")

    assert addon.id == "PKX7F81"
    assert addon.type == "incident_show_addon"
    assert addon.name == "Service Runbook"
    assert addon.src == "https://intranet.example.com/runbook.html"
    assert addon.services[0].id == "PIJ90N7"

@httpretty.activate
def test_update_addon_v2():
    body_req = open('tests/fixtures/addon_update_request_v2.json').read()
    body_resp = open('tests/fixtures/addon_update_response_v2.json').read()
    httpretty.register_uri(
        httpretty.PUT, "https://api.pagerduty.com/addons/PKX7F81",
        body=body_req,
        responses=[httpretty.Response(body=body_resp, status=200)])

    p = pygerduty.v2.PagerDuty("password")
    addon = p.addons.update("PKX7F81")

    assert addon.id == "PKX7F81"
    assert addon.type == "incident_show_addon"
    assert addon.name == "Service Runbook"
    assert addon.src == "https://intranet.example.com/runbook.html"
    assert addon.services[0].id == "PIJ90N7"
