from __future__ import absolute_import

import httpretty
import pygerduty
import pygerduty.v2
import pytest

###################
# Version 1 Tests #
###################

@httpretty.activate
def test_unknown_subdomain():
    httpretty.register_uri(
        httpretty.GET, "https://contosso.pagerduty.com/api/v1/users/ABCDEFG",
        body='{"error":{"message":"Account Not Found","code":2007}}', status=404)

    p = pygerduty.PagerDuty("contosso", "password")

    with pytest.raises(pygerduty.NotFound):
        p.users.show("ABCDEFG")

###################
# Version 2 Tests #
###################

@httpretty.activate
def test_v2_domain():
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/users/EFGHIJK",
        body='{"error": {"message":"API Not found", "code":207}}', status=404)
    p = pygerduty.v2.PagerDuty("password")

    with pytest.raises(pygerduty.common.NotFound):
        p.users.show("EFGHIJK")
