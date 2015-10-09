from __future__ import absolute_import

import httpretty
import pygerduty
import pytest

@httpretty.activate
def test_unknown_subdomain():
    httpretty.register_uri(
        httpretty.GET, "https://contosso.pagerduty.com/api/v1/users/ABCDEFG",
        body='{"error":{"message":"Account Not Found","code":2007}}', status=404)

    p = pygerduty.PagerDuty("contosso", "password")

    with pytest.raises(pygerduty.NotFound):
        p.users.show("ABCDEFG")
