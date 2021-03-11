from __future__ import absolute_import

import httpretty
import pygerduty.v2
import textwrap

###################
# Version 2 Tests #
###################


@httpretty.activate
def test_get_extension_v2():
    body = open('tests/fixtures/get_extension_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/extensions/PPGPXHO",
        body=body, status=200)
    p = pygerduty.v2.PagerDuty("password")
    extension = p.extensions.show("PPGPXHO")

    assert extension.self_ == 'https://api.pagerduty.com/extensions/PPGPXHO'
    assert extension.endpoint_url == 'https://example.com/recieve_a_pagerduty_webhook'
    assert len(extension.extension_objects) == 1
    ext_obj = extension.extension_objects[0]
    assert ext_obj.id == 'PIJ90N7'


@httpretty.activate
def test_list_extensions_v2():
    body = open('tests/fixtures/extensions_list_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/extensions", responses=[
            httpretty.Response(body=body, status=200),
            httpretty.Response(body=textwrap.dedent("""\
                {
                    "limit": 25,
                    "more": false,
                    "offset": 1,
                    "extensions": [],
                    "total": null
                }
            """), status=200),
        ],
    )

    p = pygerduty.v2.PagerDuty("password")
    extensions = [s for s in p.extensions.list()]

    assert len(extensions) == 2
    assert extensions[0].self_ == 'https://api.pagerduty.com/extensions/PPGPXHO'
    assert extensions[0].endpoint_url == 'https://example.com/recieve_a_pagerduty_webhook'
    assert len(extensions[0].extension_objects) == 1
    ext_obj0 = extensions[0].extension_objects[0]
    assert ext_obj0.id == 'PIJ90N7'

    assert extensions[1].self_ == 'https://api.pagerduty.com/extensions/PPGPXHI'
    assert extensions[1].endpoint_url == 'https://example.com/recieve_a_pagerduty_webhook_2'
    assert len(extensions[1].extension_objects) == 1
    ext_obj1 = extensions[1].extension_objects[0]
    assert ext_obj1.id == 'PIJ90N8'


@httpretty.activate
def test_enable_extension_v2():
    body = open('tests/fixtures/get_extension_v2.json').read()
    httpretty.register_uri(
        httpretty.POST, "https://api.pagerduty.com/extensions/PPGPXHO/enable",
        body=body, status=200)
    p = pygerduty.v2.PagerDuty("password")
    extension = p.extensions.enable("PPGPXHO")

    assert extension.self_ == 'https://api.pagerduty.com/extensions/PPGPXHO'
    assert extension.endpoint_url == 'https://example.com/recieve_a_pagerduty_webhook'
    assert len(extension.extension_objects) == 1
    ext_obj = extension.extension_objects[0]
    assert ext_obj.id == 'PIJ90N7'
