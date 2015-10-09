from __future__ import absolute_import

import httpretty
import pygerduty
import textwrap

@httpretty.activate
def test_get_user():
    httpretty.register_uri(
        httpretty.GET, "https://contosso.pagerduty.com/api/v1/users/PIJ90N7",
        body=textwrap.dedent("""\
            {
              "user": {
                "avatar_url": "https://secure.gravatar.com/avatar/6e1b6fc29a03fc3c13756bd594e314f7.png?d=mm&r=PG",
                "color": "dark-slate-grey",
                "email": "bart@example.com",
                "id": "PIJ90N7",
                "invitation_sent": true,
                "job_title": "Developer",
                "marketing_opt_out": true,
                "name": "Bart Simpson",
                "role": "admin",
                "time_zone": "Eastern Time (US & Canada)",
                "user_url": "/users/PIJ90N7"
              }
            }
            """), status=200)

    p = pygerduty.PagerDuty("contosso", "password")
    user = p.users.show("PIJ90N7")

    assert user.id == "PIJ90N7"
    assert user.name == "Bart Simpson"
    assert user.role == "admin"

@httpretty.activate
def test_get_user_contact_methods():
    httpretty.register_uri(
        httpretty.GET, "https://contosso.pagerduty.com/api/v1/users/PIJ90N7",
        body=textwrap.dedent("""\
            {
              "user": {
                "avatar_url": "https://secure.gravatar.com/avatar/6e1b6fc29a03fc3c13756bd594e314f7.png?d=mm&r=PG",
                "color": "dark-slate-grey",
                "email": "bart@example.com",
                "id": "PIJ90N7",
                "invitation_sent": true,
                "job_title": "Developer",
                "marketing_opt_out": true,
                "name": "Bart Simpson",
                "role": "admin",
                "time_zone": "Eastern Time (US & Canada)",
                "user_url": "/users/PIJ90N7"
              }
            }
            """), status=200),
    httpretty.register_uri(
        httpretty.GET, "https://contosso.pagerduty.com/api/v1/users/PIJ90N7/contact_methods",
        body=textwrap.dedent("""\
            {
              "contact_methods": [
                {
                  "address": "bart@example.com",
                  "email": "bart@example.com",
                  "id": "PZMO0JF",
                  "label": "Default",
                  "send_short_email": false,
                  "type": "email",
                  "user_id": "PIJ90N7"
                },
                {
                  "address": "9373249222",
                  "country_code": 1,
                  "id": "PDGR818",
                  "label": "Mobile",
                  "phone_number": "9373249222",
                  "type": "phone",
                  "user_id": "PIJ90N7"
                },
                {
                  "address": "9373249222",
                  "country_code": 1,
                  "enabled": true,
                  "id": "P25E95E",
                  "label": "Mobile",
                  "phone_number": "9373249222",
                  "type": "SMS",
                  "user_id": "PIJ90N7"
                }
              ]
            }
            """), status=200)

    p = pygerduty.PagerDuty("contosso", "password")
    user = p.users.show("PIJ90N7")
    contact_methods = [c for c in user.contact_methods.list()]

    assert len(contact_methods) == 3
    assert len([c for c in contact_methods if c.type == "email"]) == 1
    assert len([c for c in contact_methods if c.type == "phone"]) == 1
    assert len([c for c in contact_methods if c.type == "SMS"]) == 1
