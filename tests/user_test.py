from __future__ import absolute_import

import httpretty
import pygerduty
import pygerduty.v2
import textwrap


authorization_token = 'y_NbAkKc66ryYTWUXYEu'
@httpretty.activate
def test_get_user_v1():
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
def test_get_user_contact_methods_v1():
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

@httpretty.activate
def test_get_user_v2():
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/users/PXPGF42",
        body=textwrap.dedent("""\
            {
              "user": {
                "id": "PXPGF42",
                "avatar_url": "https://secure.gravatar.com/avatar/6e1b6fc29a03fc3c13756bd594e314f7.png?d=mm&r=PG",
                "summary": "Betty Simpson",
                "self": "https://api.pagerduty.com/users/PXPGF42",
                "html_url": "https://subdomain.pagerduty.com/users/PXPGF42",
                "type": "user",
                "color": "green",
                "email": "betty@example.com",
                "invitation_sent": true,
                "job_title": "Developer",
                "name": "Betty Simpson",
                "role": "admin",
                "time_zone": "Eastern Time (US & Canada)",
                "description": "Betty Simpson",
                "user_url": "/users/PXPGF42"
              }
            }
            """),
        status=200,
        )

    p = pygerduty.v2.PagerDuty("contosso", "password")
    user = p.users.show("PXPGF42")

    assert user.id == "PXPGF42"
    assert user.name == "Betty Simpson"
    assert user.role == "admin"
    assert user.self_ == 'https://api.pagerduty.com/users/PXPGF42'

@httpretty.activate
def test_get_user_contact_methods_v2():
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/users/PXPGF42",
        body=textwrap.dedent("""\
            {
              "user": {
                "id": "PXPGF42",
                "avatar_url": "https://secure.gravatar.com/avatar/6e1b6fc29a03fc3c13756bd594e314f7.png?d=mm&r=PG",
                "summary": "Betty Simpson",
                "self": "https://api.pagerduty.com/users/PXPGF42",
                "html_url": "https://subdomain.pagerduty.com/users/PXPGF42",
                "type": "user",
                "color": "green",
                "email": "betty@example.com",
                "invitation_sent": true,
                "job_title": "Developer",
                "name": "Betty Simpson",
                "role": "admin",
                "time_zone": "Eastern Time (US & Canada)",
                "description": "Betty Simpson",
                "user_url": "/users/PXPGF42"
              }
            }"""), status=200),
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/users/PXPGF42/contact_methods",
        body=textwrap.dedent("""\
            {
              "contact_methods": [
                {
                  "address": "betty@example.com",
                  "id": "PZMO0JF",
                  "self": "https://api.pagerduty.com/users/PXPGF42/contact_method/PZMO0JF",
                  "label": "Default",
                  "send_short_email": false,
                  "send_html_email": true,
                  "type": "email",
                  "html_url": null,
                  "user_id": "PXPGF42"
                },
               {
                  "address": "7483784787",
                  "id": "PWEN34G",
                  "self": "https://api.pagerduty.com/users/PXPGF42/contact_method/PWEN34G",
                  "label": "Default",
                  "send_short_email": false,
                  "send_html_email": true,
                  "type": "SMS",
                  "html_url": null,
                  "user_id": "PXPGF42"
               },
               {
                  "address": "7483784787",
                  "id": "PZMP0KL",
                  "self": "https://api.pagerduty.com/users/PXPGF42/contact_method/PZMP0KL",
                  "label": "Default",
                  "send_short_email": false,
                  "send_html_email": true,
                  "type": "phone",
                  "html_url": null,
                  "user_id": "PXPGF42"
               }
              ]
            }"""), status=200)

    p = pygerduty.v2.PagerDuty("contosso", "password")

    user = p.users.show("PXPGF42")

    contact_methods = [c for c in user.contact_methods.list()]

    assert len(contact_methods) == 3
    assert len([c for c in contact_methods if c.type == "email"]) == 1
    assert len([c for c in contact_methods if c.type == "phone"]) == 1
    assert len([c for c in contact_methods if c.type == "SMS"]) == 1
    assert user.self_ == 'https://api.pagerduty.com/users/PXPGF42'

