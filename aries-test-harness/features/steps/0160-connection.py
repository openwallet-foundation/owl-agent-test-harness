# -----------------------------------------------------------
# Behave Step Definitions for the Connection Protocol 0160
# used to establish connections between Aries Agents.
# 0160 connection-protocol RFC: 
# https://github.com/hyperledger/aries-rfcs/tree/9b0aaa39df7e8bd434126c4b33c097aae78d65bf/features/0160-connection-protocol#0160-connection-protocol
#
# Current AIP version level of test coverage: 1.0
#  
# -----------------------------------------------------------

from behave import given, when, then
import json
from agent_backchannel_client import agent_backchannel_GET, agent_backchannel_POST, connection_status


@given('we have two agents "{inviter}" and "{invitee}"')
def step_impl(context, inviter, invitee):
    """Determine there are 2 agents running based on data in the Behave input file behave.ini."""
    inviter_url = context.config.userdata.get(inviter)
    invitee_url = context.config.userdata.get(invitee)
    assert inviter_url is not None and 0 < len(inviter_url)
    assert invitee_url is not None and 0 < len(invitee_url)
    # TODO need to assert if the URLs are up (200) before continuing with the test, and message if they are not (404?).

@when('"{inviter}" generates a connection invitation')
def step_impl(context, inviter):
    inviter_url = context.config.userdata.get(inviter)

    (resp_status, resp_text) = agent_backchannel_POST(inviter_url + "/agent/command/", "connection", operation="create-invitation")
    assert resp_status == 200

    resp_json = json.loads(resp_text)
    context.inviter_invitation = resp_json["invitation"]
    context.inviter_connection_id = resp_json["connection_id"]

    # get connection and verify status
    assert connection_status(inviter_url, context.inviter_connection_id, "invitation")

@when('"{invitee}" receives the connection invitation')
def step_impl(context, invitee):
    invitee_url = context.config.userdata.get(invitee)

    data = context.inviter_invitation
    (resp_status, resp_text) = agent_backchannel_POST(invitee_url + "/agent/command/", "connection", operation="receive-invitation", data=data)
    assert resp_status == 200

    resp_json = json.loads(resp_text)
    context.invitee_connection_id = resp_json["connection_id"]

    # get connection and verify status
    assert connection_status(invitee_url, context.invitee_connection_id, ["invitation", "request"])

""" @when('"{invitee}" sends a connection response')
def step_impl(context, invitee):
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.invitee_connection_id

    # get connection and verify status
    assert connection_status(invitee_url, invitee_connection_id, ["invitation", "request"])

    (resp_status, resp_text) = agent_backchannel_POST(invitee_url + "/agent/command/", "connection", operation="accept-invitation", id=invitee_connection_id)
    assert resp_status == 200

    # get connection and verify status
    assert connection_status(invitee_url, invitee_connection_id, "request") """

# Replaced the function above because according to the RFC the invitee does not send a connection response, the inviter does.
@when('"{inviter}" sends a connection response')
def step_impl(context, inviter):
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.inviter_connection_id

    # get connection and verify status
    assert connection_status(inviter_url, inviter_connection_id, ["request", "response"])

    (resp_status, resp_text) = agent_backchannel_POST(inviter_url + "/agent/command/", "connection", operation="accept-request", id=inviter_connection_id)
    assert resp_status == 200

    # get connection and verify status
    assert connection_status(inviter_url, inviter_connection_id, "response")

@when('"{invitee}" sends a connection request')
def step_impl(context, invitee):
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.invitee_connection_id

    # get connection and verify status
    assert connection_status(invitee_url, invitee_connection_id, ["invitation", "request"])

    # TODO There doesn't seem to be an operation/event for send connection request
    (resp_status, resp_text) = agent_backchannel_POST(invitee_url + "/agent/command/", "connection", operation="accept-invitation", id=invitee_connection_id)
    assert resp_status == 200

    # get connection and verify status
    # TODO request should be requested according to the RFC
    assert connection_status(invitee_url, invitee_connection_id, "request")

@when('"{inviter}" receives the connection request')
def step_impl(context, inviter):
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.inviter_connection_id

    # get connection and verify status
    assert connection_status(inviter_url, inviter_connection_id, ["invitation", "request"])

    (resp_status, resp_text) = agent_backchannel_POST(inviter_url + "/agent/command/", "connection", operation="accept-request", id=inviter_connection_id)
    assert resp_status == 200

    # get connection and verify status
    assert connection_status(inviter_url, inviter_connection_id, ["request", "response"])

@when('"{inviter}" accepts the connection response')
def step_impl(context, inviter):
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.inviter_connection_id

    # get connection and verify status
    assert connection_status(inviter_url, inviter_connection_id, ["invitation", "request"])

    (resp_status, resp_text) = agent_backchannel_POST(inviter_url + "/agent/command/", "connection", operation="accept-request", id=inviter_connection_id)
    assert resp_status == 200

    # get connection and verify status
    assert connection_status(inviter_url, inviter_connection_id, ["request", "response"])

@when('"{invitee}" sends a response ping')
def step_impl(context, invitee):
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.invitee_connection_id

    # get connection and verify status
    assert connection_status(invitee_url, invitee_connection_id, ["request", "response"])

    data = {"comment": "Hello from " + invitee}
    (resp_status, resp_text) = agent_backchannel_POST(invitee_url + "/agent/command/", "connection", operation="send-ping", id=invitee_connection_id, data=data)
    assert resp_status == 200

    # get connection and verify status
    assert connection_status(invitee_url, invitee_connection_id, "active")

@when('"{inviter}" receives the response ping')
def step_impl(context, inviter):
    # extra step to force status to 'active' for VCX
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.inviter_connection_id

    data = {"comment": "Hello from " + inviter}
    (resp_status, resp_text) = agent_backchannel_POST(inviter_url + "/agent/command/", "connection", operation="send-ping", id=inviter_connection_id, data=data)
    assert resp_status == 200

    # get connection and verify status
    assert connection_status(inviter_url, inviter_connection_id, "active")

@then('"{inviter}" and "{invitee}" have a connection')
def step_impl(context, inviter, invitee):
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.inviter_connection_id
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.invitee_connection_id

    # get connection and verify status for inviter
    assert connection_status(inviter_url, inviter_connection_id, "response")

    # get connection and verify status for invitee
    assert connection_status(invitee_url, invitee_connection_id, "active")


@given('"{sender}" and "{receiver}" have an existing connection')
def step_impl(context, sender, receiver):
    context.execute_steps(u'''
       Given we have two agents "''' + sender + '''" and "''' + receiver + '''"
        When "''' + sender + '''" generates a connection invitation
         And "''' + receiver + '''" receives the connection invitation
         And "''' + receiver + '''" sends a connection response
         And "''' + sender + '''" accepts the connection response
         And "''' + receiver + '''" sends a response ping
         And "''' + sender + '''" receives the response ping
        Then "''' + sender + '''" and "''' + receiver + '''" have a connection
    ''')

@when(u'"{sender}" sends a trust ping')
def step_impl(context, sender):
    sender_url = context.config.userdata.get(sender)
    sender_connection_id = context.inviter_connection_id

    # get connection and verify status
    assert connection_status(sender_url, sender_connection_id, "active")

    data = {"comment": "Hello from " + sender}
    (resp_status, resp_text) = agent_backchannel_POST(sender_url + "/agent/command/", "connection", operation="send-ping", id=sender_connection_id, data=data)
    assert resp_status == 200

    # get connection and verify status
    assert connection_status(sender_url, sender_connection_id, "active")

@then('"{receiver}" receives the trust ping')
def step_impl(context, receiver):
    # TODO
    pass

# Attempt to use Data tables coming in from the feature file
# Will contain agent name and role
@given(u'we have two agents')
def step_impl(context):
    """Determine there are at least 2 agents running based on data in the Behave input file behave.ini."""
    
    for row in context.table:
        if row['role'] == 'inviter':
            context.inviter_url = context.config.userdata.get(row['name'])
            context.inviter_name = context.config.userdata.get(row['name'])
            assert context.inviter_url is not None and 0 < len(context.inviter_url)
        elif row['role'] == 'invitee':
            context.invitee_url = context.config.userdata.get(row['name'])
            context.invitee_name = context.config.userdata.get(row['name'])
            assert context.invitee_url is not None and 0 < len(context.invitee_url)
        else:
            print("Data table in step contains an unrecognized role, must be inviter or invitee")


@given('"{invitee}" has sent a connection request to "{inviter}"')
def step_impl(context, invitee, inviter):
    context.execute_steps('''
        When "''' + invitee + '''" generates a connection invitation
         And "''' + inviter + '''" receives the connection invitation
         And "''' + inviter + '''" sends a connection request
    ''')


@given('"{inviter}" has accepted the connection request by sending a connection response')
def step_impl(context, inviter):
    context.execute_steps('''When "''' + inviter + '''" accepts the connection response''')
    #context.execute_steps('''And Alice acceptss the connection response''')
    #context.execute_steps('''
    #    And {inviter} accepts the connection response
    #'''.format(inviter=inviter))


@given(u'"{invitee}" is in the state of complete')
def step_impl(context, invitee):
    # inviter_url = context.config.userdata.get(inviter)
    # inviter_connection_id = context.inviter_connection_id
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.invitee_connection_id

    # get connection and verify status
    # TODO this status should be complete, change in client backchannel to map complete to active
    assert connection_status(invitee_url, invitee_connection_id, "active")


@given(u'"{inviter}" is in the state of responded')
def step_impl(context, inviter):
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.inviter_connection_id

    # get connection and verify status
    # TODO this status should be responded, change in client backchannel to map responded to response
    assert connection_status(inviter_url, inviter_connection_id, "response")


@when(u'"{sender}" sends acks to "{reciever}"')
def step_impl(context, sender):
    receiver_url = context.config.userdata.get(receiver)
    receiver_connection_id = context.inviter_connection_id
    sender_connection_id = context.invitee_connection_id

    # get connection and verify status of the reciever
    assert connection_status(receiver_url, receiver_connection_id, "response")

    data = {"comment": "acknowledgement from " + sender}
    (resp_status, resp_text) = agent_backchannel_POST(receiver_url + "/agent/command/", "connection", operation="send-ping", id=sender_connection_id, data=data)
    # ack not yet implemented. Use line below when it is and remove the upper send-ping call
    #(resp_status, resp_text) = agent_backchannel_POST(sender_url + "/agent/command/", "connection", operation="ack", id=sender_connection_id, data=data)
    assert resp_status == 200

    # get connection and verify status
    assert connection_status(receiver_url, receiver_connection_id, "active")

@when(u'"{sender}" sends trustping to "{reciever}"')
def step_impl(context, sender):
    receiver_url = context.config.userdata.get(receiver)
    receiver_connection_id = context.inviter_connection_id
    sender_connection_id = context.invitee_connection_id

    # get connection and verify status of the reciever
    assert connection_status(receiver_url, receiver_connection_id, "response")

    data = {"comment": "acknowledgement from " + sender}
    (resp_status, resp_text) = agent_backchannel_POST(receiver_url + "/agent/command/", "connection", operation="send-ping", id=sender_connection_id, data=data)
    assert resp_status == 200

    # get connection and verify status
    assert connection_status(receiver_url, receiver_connection_id, "active")

@then(u'"{inviter}" is in the state of complete')
def step_impl(context, inviter):
    # get connection and verify status
    # TODO this status should be complete, change in client backchannel to map complete to active
    assert connection_status(context.config.userdata.get(inviter), context.inviter_connection_id, "active")

