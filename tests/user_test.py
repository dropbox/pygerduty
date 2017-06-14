from __future__ import absolute_import

import httpretty
import pygerduty
import pygerduty.v2
import textwrap

###################
# Version 1 Tests #
###################

@httpretty.activate
def test_get_user_v1():
    body = open('tests/fixtures/user_v1.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://contosso.pagerduty.com/api/v1/users/PIJ90N7",
        body=body, status=200)

    p = pygerduty.PagerDuty("contosso", "password")
    user = p.users.show("PIJ90N7")

    assert user.id == "PIJ90N7"
    assert user.name == "Bart Simpson"
    assert user.role == "admin"

@httpretty.activate
def test_get_user_contact_methods_v1():
    user_body = open('tests/fixtures/user_v1.json').read()
    contact_body = open('tests/fixtures/contacts_v1.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://contosso.pagerduty.com/api/v1/users/PIJ90N7",
        body=user_body, status=200),
    httpretty.register_uri(
        httpretty.GET, "https://contosso.pagerduty.com/api/v1/users/PIJ90N7/contact_methods",
        body=contact_body, status=200)

    p = pygerduty.PagerDuty("contosso", "password")
    user = p.users.show("PIJ90N7")
    contact_methods = [c for c in user.contact_methods.list()]

    assert len(contact_methods) == 3
    assert len([c for c in contact_methods if c.type == "email"]) == 1
    assert len([c for c in contact_methods if c.type == "phone"]) == 1
    assert len([c for c in contact_methods if c.type == "SMS"]) == 1

###################
# Version 2 Tests #
###################

@httpretty.activate
def test_get_user_v2():
    body = open('tests/fixtures/user_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/users/PXPGF42",
        body=body, status=200)

    p = pygerduty.v2.PagerDuty("contosso", "password")
    user = p.users.show("PXPGF42")

    assert user.id == "PXPGF42"
    assert user.name == "Betty Simpson"
    assert user.role == "admin"
    assert user.self_ == 'https://api.pagerduty.com/users/PXPGF42'

@httpretty.activate
def test_get_user_contact_methods_v2():
    user_body = open('tests/fixtures/user_v2.json').read()
    contact_body = open('tests/fixtures/contacts_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/users/PXPGF42",
        body=user_body, status=200)
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/users/PXPGF42/contact_methods",
        body=contact_body, status=200)

    p = pygerduty.v2.PagerDuty("contosso", "password")

    user = p.users.show("PXPGF42")

    contact_methods = [c for c in user.contact_methods.list()]

    assert len(contact_methods) == 3
    assert len([c for c in contact_methods if c.type == "email"]) == 1
    assert len([c for c in contact_methods if c.type == "phone"]) == 1
    assert len([c for c in contact_methods if c.type == "SMS"]) == 1
    assert user.self_ == 'https://api.pagerduty.com/users/PXPGF42'

@httpretty.activate
def test_user_notification_rules_v2():
    user_body = open('tests/fixtures/user_v2.json').read()
    notification_body = open('tests/fixtures/notification_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/users/PXPGF42",
        body=user_body, status=200)
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/users/PXPGF42/notification_rules",
        body=notification_body, status=200)

    p = pygerduty.v2.PagerDuty("contosso", "password")
    user = p.users.show("PXPGF42")

    notification_rules = [n for n in user.notification_rules.list()]

    assert len(notification_rules) == 1
    assert len([n for n in notification_rules if n.type == "assignment_notification_rule"]) == 1
    assert user.self_ == "https://api.pagerduty.com/users/PXPGF42"

def test_clean_response():
    mock_response = {
          "user" : {
            "id": "PHDGK84",
            "type": "user",
            "self": "https://api.pagerduty.com/users/PHDGK84",
            "name": "Snoopy",
            "contact_methods": [
              {
                "address": "betty@example.com",
                "id": "PZMO0JF",
                "self": "https://api.pagerduty.com/users/PHDGK84/contact_method/PZMO0JF",
                "label": "Default"
              },
              {
                "address": "8928393498",
                "id": "PZMN843",
                "self": "https://api.pagerduty.com/users/PHDGK84/contact_method/PZMN843",
                "label": "Default"
              }
            ],
           "notification_rules": [
             {
               "id": "P8WETWW",
               "contact_method": {
                 "id": "PZMO0JF",
                 "self": "https://api.pagerduty.com/users/PHDGK84/contact_method/PZMO0JF",
               }
             }
           ]
          }
        }
    clean_response = pygerduty.common.clean_response(mock_response)

    assert clean_response == {
          "user" : {
            "id": "PHDGK84",
            "type": "user",
            "self_": "https://api.pagerduty.com/users/PHDGK84",
            "name": "Snoopy",
            "contact_methods": [
              {
                "address": "betty@example.com",
                "id": "PZMO0JF",
                "self_": "https://api.pagerduty.com/users/PHDGK84/contact_method/PZMO0JF",
                "label": "Default"
              },
              {
                "address": "8928393498",
                "id": "PZMN843",
                "self_": "https://api.pagerduty.com/users/PHDGK84/contact_method/PZMN843",
                "label": "Default"
              }
            ],
           "notification_rules": [
             {
               "id": "P8WETWW",
               "contact_method": {
                 "id": "PZMO0JF",
                 "self_": "https://api.pagerduty.com/users/PHDGK84/contact_method/PZMO0JF",
               }
             }
           ]
          }
        }


