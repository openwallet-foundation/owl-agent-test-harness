# -----------------------------------------------------------
# Behave Step Definitions for the DID Excahnge Protocol 0023
# used to establish connections between Aries Agents based on DIDs.
# 0023 DID Excahnge RFC: 
# https://github.com/hyperledger/aries-rfcs/blob/master/features/0023-did-exchange/README.md
#
# Current AIP version level of test coverage: N/A
# Current DID Exchange version level of test coverage 1.0
#  
# -----------------------------------------------------------

from behave import given, when, then
import json
from agent_backchannel_client import agent_backchannel_GET, agent_backchannel_POST, expected_agent_state


@when('"{responder}" sends an explicit invitation')
def step_impl(context, responder):

    data = {
        "include_handshake": True,
        "use_public_did": False
    }

    (resp_status, resp_text) = agent_backchannel_POST(context.responder_url + "/agent/command/", "out-of-band", operation="send-invitation-message", data=data)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    resp_json = json.loads(resp_text)
    assert resp_json["state"] == "invitation-sent"
    context.responder_invitation = resp_json["invitation"]

    # check and see if the connection_id_dict exists
    # if it does, it was probably used to create another connection in a 3+ agent scenario
    # so that means we need to keep the connection ids around for use in the scenario
    # so we will not create a new dict which will reset the dict
    #if hasattr(context, 'temp_connection_id_dict'):
    #    context.temp_connection_id_dict[responder] = resp_json["connection_id"]
    #else:
    #    context.temp_connection_id_dict = {responder: resp_json["connection_id"]}

    # Check to see if the responder_name exists in context. If not, antother suite is using it so set the responder name and url
    #if not hasattr(context, 'responder_name') or context.responder_name != responder:
    #    context.responder_url = responder_url
    #    context.responder_name = responder

    # get connection and verify status
    #assert expected_agent_state(responder_url, "connection", context.temp_connection_id_dict[responder], "invitation-sent")


@when('"{requester}" receives the invitation')
def step_impl(context, requester):

    data = context.responder_invitation
    (resp_status, resp_text) = agent_backchannel_POST(context.requester_url + "/agent/command/", "out-of-band", operation="recieve-invitation", data=data)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    resp_json = json.loads(resp_text)

    if not hasattr(context, 'connection_id_dict'):
        context.connection_id_dict = {}
        context.connection_id_dict[requester] = {}
    
    context.connection_id_dict[requester][context.responder_name] = resp_json["connection_id"]

    # Also add the responder into the main connection_id_dict. if the len is 0 that means its already been cleared and this may be Mallory.
    if len(context.temp_connection_id_dict) != 0:
        context.connection_id_dict[context.responder_name] = {requester: context.temp_connection_id_dict[context.responder_name]}
        #clear the temp connection id dict used in the initial step. We don't need it anymore.
        context.temp_connection_id_dict.clear()

    # Check to see if the requester_name exists in context. If not, antother suite is using it so set the requester name and url
    if not hasattr(context, 'requester_name'):
        context.requester_url = requester_url
        context.requester_name = requester

    # get connection and verify status
    assert expected_agent_state(requester_url, "didexchange", context.connection_id_dict[requester][context.responder_name], "invited")


@when('"{requester}" sends the request to "{responder}"')
def step_impl(context, requester, responder):
    requester_url = context.config.userdata.get(requester)
    requester_connection_id = context.connection_id_dict[requester][responder]
    responder_url = context.config.userdata.get(responder)
    responder_connection_id = context.connection_id_dict[responder][requester]

    # get connection and verify status
    assert expected_agent_state(requester_url, "didexchange", requester_connection_id, "invitation-recieved")
    #assert expected_agent_state(responder_url, "connection", responder_connection_id, "invitation-sent")

    (resp_status, resp_text) = agent_backchannel_POST(requester_url + "/agent/command/", "didexchange", operation="send-request", id=requester_connection_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    assert expected_agent_state(requester_url, "connection", requester_connection_id, "request-sent")


@when('"{responder}" receives the request')
def step_impl(context, responder):
    responder_url = context.config.userdata.get(responder)
    responder_connection_id = context.connection_id_dict[responder][context.requester_name]

    # responder already recieved the connection request in the accept-invitation call so get connection and verify status=requested.
    #assert expected_agent_state(responder_url, "didexchange", responder_connection_id, "request-recieved")
    (resp_status, resp_text) = agent_backchannel_POST(responder_url + "/agent/command/", "didexchange", operation="recieve-request", id=responder_connection_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    assert expected_agent_state(requester_url, "connection", requester_connection_id, "request-recieved")


@when('"{responder}" sends a response to "{requester}"')
def step_impl(context, responder, requester):
    responder_url = context.config.userdata.get(responder)
    #responder_connection_id = context.connection_id_dict[responder]
    responder_connection_id = context.connection_id_dict[responder][requester]
    requester_url = context.config.userdata.get(requester)
    requester_connection_id = context.connection_id_dict[requester][responder]

    # get connection and verify status
    assert expected_agent_state(responder_url, "connection", responder_connection_id, "request-recieved")
    assert expected_agent_state(requester_url, "connection", requester_connection_id, "request-sent")

    (resp_status, resp_text) = agent_backchannel_POST(responder_url + "/agent/command/", "didexchange", operation="send-response", id=responder_connection_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    assert expected_agent_state(responder_url, "connection", responder_connection_id, "response-sent")


@when('"{requester}" receives the response')
def step_impl(context, requester):
    requester_url = context.config.userdata.get(requester)
    requester_connection_id = context.connection_id_dict[requester][context.responder_name]

    # requester already recieved the connection response in the accept-request call so get connection and verify status=responded.
    assert expected_agent_state(requester_url, "didexchange", requester_connection_id, "response-recieved")


@when('"{requester}" sends complete to "{responder}"')
def step_impl(context, requester, responder):
    requester_url = context.config.userdata.get(requester)
    requester_connection_id = context.connection_id_dict[requester][context.responder_name]

    # get connection and verify status
    assert expected_agent_state(requester_url, "connection", requester_connection_id, "response-recieved")

    data = {"comment": "Hello from " + requester}
    (resp_status, resp_text) = agent_backchannel_POST(requester_url + "/agent/command/", "didexchange", operation="send-complete", id=requester_connection_id, data=data)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    assert expected_agent_state(requester_url, "connection", requester_connection_id, "completed")


@then('"{responder}" and "{requester}" have a DID based connection')
def step_impl(context, responder, requester):
    responder_url = context.config.userdata.get(responder)
    responder_connection_id = context.connection_id_dict[responder][requester]
    requester_url = context.config.userdata.get(requester)
    requester_connection_id = context.connection_id_dict[requester][responder]

    (resp_status, resp_text) = agent_backchannel_POST(responder_url + "/agent/command/", "didexchange", operation="recieved-complete", id=requester_connection_id, data=data)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status for responder
    assert expected_agent_state(responder_url, "connection", responder_connection_id, "completed")

    # get connection and verify status for requester
    assert expected_agent_state(requester_url, "connection", requester_connection_id, "completed")


