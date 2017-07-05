from __future__ import absolute_import

import pygerduty.v2

###################
# Version 2 Tests #
###################

def test_id_to_obj():

    kwargs = {
        "escalation_policy_id": "PIJ90N7",
    }
    new_key = pygerduty.v2.Collection.cut_suffix("escalation_policy_id")
    assert new_key == 'escalation_policy'

    new_kwargs = pygerduty.v2.Collection.id_to_obj(new_key, kwargs["escalation_policy_id"])
    assert new_kwargs == {
        "id": "PIJ90N7",
        "type": "escalation_policy"
    }


def test_ids_to_objs():

    kwargs = {
        "service_ids": [
            "PF9KMXH",
            "PIJ90N7"
        ]
    }
    new_key = pygerduty.v2.Collection.cut_suffix("service_ids")
    assert new_key == "service"

    new_kwargs = pygerduty.v2.Collection.ids_to_objs(new_key, kwargs["service_ids"])
    assert new_kwargs == [
        {
            "id": "PF9KMXH",
            "type": "service"
        },
        {
            "id": "PIJ90N7",
            "type": "service"
        }
    ]


def test_process_kwargs_id():

    kwargs = {
        "name": "default-email",
        "description": "default email service",
        "escalation_policy_id": "PIJ90N7",
        "service_key": "default-email"
    }

    new_kwargs = pygerduty.v2.Collection.process_kwargs(kwargs)

    assert new_kwargs == {
        "name": "default-email",
        "description": "default email service",
        "escalation_policy": {
            "id": "PIJ90N7",
            "type": "escalation_policy"
        },
        "service_key": "default-email"
    }


def test_process_kwargs_ids():

    kwargs = {
        "start_time": "2012-06-16T13:00:00-04:00Z",
        "end_time": "2012-06-16T14:00:00-04:00Z",
        "description": "Description goes here",
        "service_ids": [
            "PF9KMXH",
            "P45HJSK"
        ]
    }

    new_kwargs = pygerduty.v2.Collection.process_kwargs(kwargs)

    assert new_kwargs == {
        "start_time": "2012-06-16T13:00:00-04:00Z",
        "end_time": "2012-06-16T14:00:00-04:00Z",
        "description": "Description goes here",
        "services": [
            {
                "id": "PF9KMXH",
                "type": "service"
            },
            {
                "id": "P45HJSK",
                "type": "service"
            }
        ]
    }



