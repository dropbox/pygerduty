from __future__ import absolute_import

import httpretty
import pygerduty.v2
import textwrap

###################
# Version 2 Tests #
###################


@httpretty.activate
def test_list_oncalls_v2():
    body = open('tests/fixtures/oncalls_list_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/oncalls", responses=[
            httpretty.Response(body=body, status=200),
            httpretty.Response(body=textwrap.dedent("""\
                {
                    "limit": 25,
                    "more": false,
                    "offset": 1,
                    "oncalls": [],
                    "total": null
                }
            """), status=200),
        ],
    )

    p = pygerduty.v2.PagerDuty("password")
    oncalls = [s for s in p.oncalls.list()]

    assert len(oncalls) == 2
    assert oncalls[0].user.type == 'user_reference'
    assert oncalls[0].user.self_ == 'https://api.pagerduty.com/users/PT23IWX'
    assert oncalls[0].schedule.type == 'schedule_reference'
    assert oncalls[0].schedule.self_ == 'https://api.pagerduty.com/schedules/PI7DH85'
    assert oncalls[0].escalation_policy.type == 'escalation_policy_reference'
    assert oncalls[0].escalation_policy.self_ == 'https://api.pagerduty.com/escalation_policies/PT20YPA'
    assert oncalls[0].start == '2015-03-06T15:28:51-05:00'
    assert oncalls[0].end == '2015-03-07T15:28:51-05:00'

    assert oncalls[1].user.type == 'user_reference'
    assert oncalls[1].user.self_ == 'https://api.pagerduty.com/users/PT23IEW'
    assert oncalls[1].schedule.type == 'schedule_reference'
    assert oncalls[1].schedule.self_ == 'https://api.pagerduty.com/schedules/PI7DD43'
    assert oncalls[1].escalation_policy.type == 'escalation_policy_reference'
    assert oncalls[1].escalation_policy.self_ == 'https://api.pagerduty.com/escalation_policies/PT20YPB'
    assert oncalls[1].start == '2015-03-06T15:28:51-05:00'
    assert oncalls[1].end == '2015-05-07T15:28:51-05:00'

@httpretty.activate
def test_list_oncalls_filtered_v2():
    body = open('tests/fixtures/oncalls_filtered_v2.json').read()
    httpretty.register_uri(
        httpretty.GET, "https://api.pagerduty.com/oncalls", responses=[
            httpretty.Response(body=body, status=200),
            httpretty.Response(body=textwrap.dedent("""\
                {
                    "limit": 25,
                    "more": false,
                    "offset": 1,
                    "oncalls": [],
                    "total": null
                }
            """), status=200),
        ],
    )

    p = pygerduty.v2.PagerDuty("password")
    oncalls = [s for s in p.oncalls.list(schedule_ids=['PI7DH85'])]

    assert len(oncalls) == 1
    assert oncalls[0].user.type == 'user_reference'
    assert oncalls[0].user.self_ == 'https://api.pagerduty.com/users/PT23IWX'
    assert oncalls[0].schedule.type == 'schedule_reference'
    assert oncalls[0].schedule.self_ == 'https://api.pagerduty.com/schedules/PI7DH85'
    assert oncalls[0].escalation_policy.type == 'escalation_policy_reference'
    assert oncalls[0].escalation_policy.self_ == 'https://api.pagerduty.com/escalation_policies/PT20YPA'
    assert oncalls[0].start == '2015-03-06T15:28:51-05:00'
    assert oncalls[0].end == '2015-03-07T15:28:51-05:00'

def test_oncall_ids():
    p = pygerduty.v2.PagerDuty("password")
    collection = pygerduty.v2.Collection(p)

    oncall = pygerduty.v2.Oncall(
            collection=collection,
            user=None,
            schedule={'id': 'schedule'},
            escalation_policy={'id': 'escalation_policy'})
    assert oncall.id == ':schedule:escalation_policy'

    oncall = pygerduty.v2.Oncall(
            collection=collection,
            user={'id': 'user'},
            schedule=None,
            escalation_policy={'id': 'escalation_policy'})
    assert oncall.id == 'user::escalation_policy'

    oncall = pygerduty.v2.Oncall(
            collection=collection,
            user={'id': 'user'},
            schedule={'id': 'schedule'},
            escalation_policy=None)
    assert oncall.id == 'user:schedule:'
