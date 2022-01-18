# -----------------------------------------------------------
# Behave Step Definitions for Aries DIDComm File and MIME Types, RFC 0044:
# https://github.com/hyperledger/aries-rfcs/blob/main/features/0044-didcomm-file-and-mime-types/README.md
#
# -----------------------------------------------------------

from time import sleep
from behave import given, when, then
import json, time
from agent_backchannel_client import agent_backchannel_GET, agent_backchannel_POST, expected_agent_state, setup_already_connected

@given('"{agent}" is running with parameters "{parameters}"')
def step_impl(context, agent, parameters):
    agent_url = context.config.userdata.get(agent)

    params_json = json.loads(parameters)

    data = {
        "parameters": params_json
    }

    (resp_status, resp_text) = agent_backchannel_POST(agent_url + "/agent/command/", "agent", operation="start", data=data)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

@then('"{requester}" can\'t accept the invitation')
def step_impl(context, requester):
    data = context.responder_invitation
    data["use_existing_connection"] = False
    (resp_status, resp_text) = agent_backchannel_POST(context.requester_url + "/agent/command/", "out-of-band", operation="receive-invitation", data=data)

    assert resp_status == 500, f'agent command should fail but resp_status {resp_status} is not 500; {resp_text}'
