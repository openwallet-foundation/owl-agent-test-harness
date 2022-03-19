# -----------------------------------------------------------
# Behave Step Definitions for DIDComm V2
#
# -----------------------------------------------------------

from typing import Optional
from behave import given, when
import json, time
from agent_backchannel_client import (
    agent_backchannel_GET,
    agent_backchannel_POST,
    expected_agent_state,
    setup_already_connected,
)

@given('"{inviter}" creates a didcomm v2 invitation with goal code "{goal_code}"')
@when('"{inviter}" creates a didcomm v2 invitation with goal code "{goal_code}"')
@given('"{inviter}" creates a didcomm v2 invitation')
@when('"{inviter}" creates a didcomm v2 invitation')
def step_impl(context, inviter: str, goal_code: Optional[str] = None):
    inviter_url = context.config.userdata.get(inviter)

    data = {}

    if goal_code:
        data["goal-code"] = goal_code

    (resp_status, resp_text) = agent_backchannel_POST(
        inviter_url + "/agent/command/",
        "oob-v2",
        operation="create-invitation",
        data=data,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"

    resp_json = json.loads(resp_text)

    if not hasattr(context, "invitation_v2"):
        context.invitation_v2 = {}

    context.invitation_v2[inviter] = resp_json["invitation"]


@given('"{invitee}" accepts the didcomm v2 invitation from "{inviter}"')
@when('"{invitee}" accepts the didcomm v2 invitation from "{inviter}"')
def step_impl(context, invitee: str, inviter: str):
    invitee_url = context.config.userdata.get(invitee)

    data = {"invitation": context.invitation_v2[inviter]}

    (resp_status, resp_text) = agent_backchannel_POST(
        invitee_url + "/agent/command/",
        "oob-v2",
        operation="accept-invitation",
        data=data,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"

    resp_json = json.loads(resp_text)

    context.connection_id_dict[invitee][inviter] = resp_json["connection_id"]


@given('"{inviter}" has received a didcomm v2 message from "{invitee}" and created a connection')
@when('"{inviter}" has received a didcomm v2 message from "{invitee}" and created a connection')
def step_impl(context, inviter: str, invitee: str):
    inviter_url = context.config.userdata.get(inviter)

    invitation = context.invitation_v2[inviter]
    invitation_id = invitation["id"]

    (resp_status, resp_text) = agent_backchannel_GET(
        inviter_url + "/agent/command/",
        "oob-v2",
        operation="invitation-connection",
        id=invitation_id,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"

    resp_json = json.loads(resp_text)

    context.connection_id_dict[inviter][invitee] = resp_json["connection_id"]


@then('"{inviter}" and "{invitee}" have a didcomm v2 connection')
def step_impl(context, inviter: str, invitee: str):
    inviter_url = context.config.userdata.get(inviter)
    invitee_url = context.config.userdata.get(invitee)

    assert inviter in context.connection_id_dict, f'no connection IDs saved for "{inviter}"'
    assert invitee in context.connection_id_dict[inviter], f'no connection ID saved from "{inviter}" to "{invitee}"'
    inviter_connection_id = context.connection_id_dict[inviter][invitee]
    assert invitee in context.connection_id_dict, f'no connection IDs saved for "{invitee}"'
    assert inviter in context.connection_id_dict[invitee], f'no connection ID saved from "{invitee}" to "{inviter}"'
    invitee_connection_id = context.connection_id_dict[invitee][inviter]

    (resp_status, resp_text) = agent_backchannel_GET(
        inviter_url + "/agent/command/",
        "connection",
        id=inviter_connection_id,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"

    inviter_connection = resp_text

    (resp_status, resp_text) = agent_backchannel_GET(
        invitee_url + "/agent/command/",
        "connection",
        id=invitee_connection_id,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"

    invitee_connection = resp_text

    # TODO: how do we validate that the connection supports didcomm v2?
