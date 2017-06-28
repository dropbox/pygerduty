from __future__ import absolute_import

import pygerduty.v2

###################
# Version 2 Tests #
###################

def test_id_to_obj():

	kwarg = {
		"escalation_policy_id": "PIJ90N7",
	}

	new_kwarg = pygerduty.v2.Collection.id_to_obj("escalation_policy_id", kwarg["escalation_policy_id"])

	assert new_kwarg == {
		"id": "PIJ90N7",
		"type": "escalation_policy"
	}


def test_ids_to_objs():

    kwarg = {
        "service_ids": [
            "PF9KMXH",
            "PIJ90N7"
        ]
    }

    new_kwargs = pygerduty.v2.Collection.ids_to_objs("service_ids", kwarg["service_ids"])

    assert new_kwargs == [
        {
    	    "id": "PF9KMXH",
    	    "type": "services"
        },
        {
            "id": "PIJ90N7",
            "type": "services"
        }
    ]
