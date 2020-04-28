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


@given(u'we have {n} agents')
def step_impl(context, n):
    """Determine there are at least 2 agents running based on data in the Behave input file behave.ini."""
    
    for row in context.table:
        if row['role'] == 'inviter':
            context.inviter_url = context.config.userdata.get(row['name'])
            context.inviter_name = row['name']
            assert context.inviter_url is not None and 0 < len(context.inviter_url)
        elif row['role'] == 'invitee':
            context.invitee_url = context.config.userdata.get(row['name'])
            context.invitee_name = row['name']
            assert context.invitee_url is not None and 0 < len(context.invitee_url)
        elif row['role'] == 'inviteinterceptor':
            context.inviteinterceptor_url = context.config.userdata.get(row['name'])
            context.inviteinterceptor_name = row['name']
            assert context.inviteinterceptor_url is not None and 0 < len(context.inviteinterceptor_url)
        else:
            print("Data table in step contains an unrecognized role, must be inviter, invitee, or inviteinterceptor")



@when('"{inviter}" generates a connection invitation')
def step_impl(context, inviter):
    inviter_url = context.config.userdata.get(inviter)

    (resp_status, resp_text) = agent_backchannel_POST(inviter_url + "/agent/command/", "connection", operation="create-invitation")
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    resp_json = json.loads(resp_text)
    context.inviter_invitation = resp_json["invitation"]
    context.connection_id_dict = {inviter: resp_json["connection_id"]}
    #context.inviter_connection_id = resp_json["connection_id"]

    # get connection and verify status
    #assert connection_status(inviter_url, context.inviter_connection_id, "invitation")
    assert connection_status(inviter_url, context.connection_id_dict[inviter], "invitation")

@given('"{invitee}" receives the connection invitation')
@when('"{invitee}" receives the connection invitation')
def step_impl(context, invitee):
    invitee_url = context.config.userdata.get(invitee)

    data = context.inviter_invitation
    (resp_status, resp_text) = agent_backchannel_POST(invitee_url + "/agent/command/", "connection", operation="receive-invitation", data=data)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    resp_json = json.loads(resp_text)
    context.connection_id_dict[invitee] = resp_json["connection_id"]
    #context.invitee_connection_id = resp_json["connection_id"]

    # get connection and verify status
    assert connection_status(invitee_url, context.connection_id_dict[invitee], "invitation")

@when('"{inviter}" sends a connection response to "{invitee}"')
@given('"{inviter}" sends a connection response to "{invitee}"')
@then('"{inviter}" sends a connection response to "{invitee}"')
def step_impl(context, inviter, invitee):
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.connection_id_dict[inviter]
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.connection_id_dict[invitee]

    print(inviter, inviter_url, inviter_connection_id)

    # get connection and verify status
    assert connection_status(inviter_url, inviter_connection_id, "request")
    assert connection_status(invitee_url, invitee_connection_id, "request")

    (resp_status, resp_text) = agent_backchannel_POST(inviter_url + "/agent/command/", "connection", operation="accept-request", id=inviter_connection_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    assert connection_status(inviter_url, inviter_connection_id, "response")

@when('"{invitee}" receives the connection response')
@given('"{invitee}" receives the connection response')
def step_impl(context, invitee):
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.connection_id_dict[invitee]

    # invitee already recieved the connection response in the accept-request call so get connection and verify status=response.
    assert connection_status(invitee_url, invitee_connection_id, "response")

@given('"{invitee}" sends a connection request to "{inviter}"')
@when('"{invitee}" sends a connection request to "{inviter}"')
def step_impl(context, invitee, inviter):
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.connection_id_dict[invitee]
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.connection_id_dict[inviter]

    # get connection and verify status
    #assert connection_status(invitee_url, invitee_connection_id, ["invitation", "request"])
    assert connection_status(invitee_url, invitee_connection_id, ["invitation"])
    assert connection_status(inviter_url, inviter_connection_id, ["invitation"])

    (resp_status, resp_text) = agent_backchannel_POST(invitee_url + "/agent/command/", "connection", operation="accept-invitation", id=invitee_connection_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    # TODO request should be requested according to the RFC
    assert connection_status(invitee_url, invitee_connection_id, "request")


@when('"{inviter}" receives the connection request')
@given('"{inviter}" receives the connection request')
def step_impl(context, inviter):
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.connection_id_dict[inviter]

    # inviter already recieved the connection request in the accept-invitation call so get connection and verify status=requested.
    assert connection_status(inviter_url, inviter_connection_id, "request")


@when('"{inviter}" accepts the connection response to "{invitee}"')
def step_impl(context, inviter, invitee):
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.connection_id_dict[inviter]
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.connection_id_dict[invitee]

    # get connection and verify status
    assert connection_status(inviter_url, inviter_connection_id, ["request"])
    assert connection_status(invitee_url, invitee_connection_id, ["request"])

    (resp_status, resp_text) = agent_backchannel_POST(inviter_url + "/agent/command/", "connection", operation="accept-request", id=inviter_connection_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    assert connection_status(inviter_url, inviter_connection_id, ["response"])
    assert connection_status(invitee_url, invitee_connection_id, ["active"])

@when('"{invitee}" sends a response ping')
def step_impl(context, invitee):
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.connection_id_dict[invitee]

    # get connection and verify status
    assert connection_status(invitee_url, invitee_connection_id, ["response"])

    data = {"comment": "Hello from " + invitee}
    (resp_status, resp_text) = agent_backchannel_POST(invitee_url + "/agent/command/", "connection", operation="send-ping", id=invitee_connection_id, data=data)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    assert connection_status(invitee_url, invitee_connection_id, "active")

@when('"{inviter}" receives the response ping')
def step_impl(context, inviter):
    # extra step to force status to 'active' for VCX
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.connection_id_dict[inviter]

    data = {"comment": "Hello from " + inviter}
    (resp_status, resp_text) = agent_backchannel_POST(inviter_url + "/agent/command/", "connection", operation="send-ping", id=inviter_connection_id, data=data)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    assert connection_status(inviter_url, inviter_connection_id, "active")

@then('"{inviter}" and "{invitee}" have a connection')
def step_impl(context, inviter, invitee):
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.connection_id_dict[inviter]
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.connection_id_dict[invitee]

    # get connection and verify status for inviter
    assert connection_status(inviter_url, inviter_connection_id, "active")

    # get connection and verify status for invitee
    assert connection_status(invitee_url, invitee_connection_id, "active")

@then('"{invitee}" is connected to "{inviter}"')
def step_impl(context, inviter, invitee):
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.connection_id_dict[inviter]
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.connection_id_dict[invitee]

    # get connection and verify status for inviter
    assert connection_status(inviter_url, inviter_connection_id, "response")
    #assert connection_status(inviter_url, inviter_connection_id, "active")

    # get connection and verify status for invitee
    assert connection_status(invitee_url, invitee_connection_id, "active")

@given('"{sender}" and "{receiver}" have an existing connection')
def step_impl(context, sender, receiver):
    context.execute_steps(u'''
        When "''' + sender + '''" generates a connection invitation
         And "''' + receiver + '''" receives the connection invitation
         And "''' + receiver + '''" sends a connection request to "''' + sender + '''"
         And "''' + sender + '''" receives the connection request
         And "''' + sender + '''" sends a connection response to "''' + receiver + '''"
         And "''' + receiver + '''" receives the connection response
         And "''' + receiver + '''" sends trustping to "''' + sender + '''"
        Then "''' + sender + '''" and "''' + receiver + '''" have a connection
    ''')

@when(u'"{sender}" sends a trust ping')
def step_impl(context, sender):
    sender_url = context.config.userdata.get(sender)
    sender_connection_id = context.connection_id_dict[sender]

    # get connection and verify status
    assert connection_status(sender_url, sender_connection_id, "active")

    data = {"comment": "Hello from " + sender}
    (resp_status, resp_text) = agent_backchannel_POST(sender_url + "/agent/command/", "connection", operation="send-ping", id=sender_connection_id, data=data)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    assert connection_status(sender_url, sender_connection_id, "active")

@then('"{receiver}" receives the trust ping')
def step_impl(context, receiver):
    # TODO
    pass


@given('"{invitee}" has sent a connection request to "{inviter}"')
def step_impl(context, invitee, inviter):
    context.execute_steps('''
        When "''' + inviter + '''" generates a connection invitation
         And "''' + invitee + '''" receives the connection invitation
         And "''' + invitee + '''" sends a connection request
    ''')

@given('"{inviter}" has accepted the connection request by sending a connection response')
def step_impl(context, inviter):
    context.execute_steps('''When "''' + inviter + '''" accepts the connection response''')


@given(u'"{invitee}" is in the state of complete')
def step_impl(context, invitee):
    # inviter_url = context.config.userdata.get(inviter)
    # inviter_connection_id = context.inviter_connection_id
    invitee_url = context.config.userdata.get(invitee)
    invitee_connection_id = context.connection_id_dict[invitee]

    # get connection and verify status
    # TODO this status should be complete, change in client backchannel to map complete to active
    assert connection_status(invitee_url, invitee_connection_id, "active")


@given(u'"{inviter}" is in the state of responded')
def step_impl(context, inviter):
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.connection_id_dict[inviter]

    # get connection and verify status
    # TODO this status should be responded, change in client backchannel to map responded to response
    assert connection_status(inviter_url, inviter_connection_id, "response")


@when(u'"{sender}" sends acks to "{reciever}"')
def step_impl(context, sender, reciever):
    sender_url = context.config.userdata.get(sender)
    sender_connection_id = context.connection_id_dict[sender]

    # get connection and verify status of the reciever
    # no need to do this here, an acks may be called at any point, can't check for state.
    #assert connection_status(sender_url, sender_connection_id, "response")

    data = {"comment": "acknowledgement from " + sender}
    # TODO acks not implemented yet, this will fail.
    (resp_status, resp_text) = agent_backchannel_POST(sender_url + "/agent/command/", "connection", operation="acks", id=sender_connection_id, data=data)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    # no need to do this here, an acks may be called at any point, can't check for state.
    # assert connection_status(sender_url, sender_connection_id, "active")

@when('"{sender}" sends trustping to "{receiver}"')
def step_impl(context, sender, receiver):
    sender_url = context.config.userdata.get(sender)
    sender_connection_id = context.connection_id_dict[sender]

    # get connection and verify status of the reciever
    # no need to do this here, a trust pint may be called at any point, can't check for state.
    #assert connection_status(sender_url, sender_connection_id, "response")

    data = {"comment": "acknowledgement from " + sender}
    (resp_status, resp_text) = agent_backchannel_POST(sender_url + "/agent/command/", "connection", operation="send-ping", id=sender_connection_id, data=data)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    # no need to do this here, a trust pint may be called at any point, can't check for state.
    #assert connection_status(sender_url, sender_connection_id, "active")

@then(u'"{inviter}" is in the state of complete')
def step_impl(context, inviter):
    # get connection and verify status
    # TODO this status should be complete, change in client backchannel to map complete to active
    assert connection_status(context.config.userdata.get(inviter), context.connection_id_dict[inviter], "active")


@given(u'"{inviter}" generated a single-use connection invitation')
def step_impl(context, inviter):
    context.execute_steps('''
        When "''' + inviter + '''" generates a connection invitation
    ''')


@given(u'"{invitee}" received the connection invitation')
def step_impl(context, invitee):
    context.execute_steps('''
        When "''' + invitee + '''" receives the connection invitation
    ''')


@given(u'"{invitee}" sent a connection request to "{inviter}"')
def step_impl(context, invitee, inviter):
    context.execute_steps('''
        When "''' + invitee + '''" sends a connection request to "''' + inviter + '''"
    ''')


@given(u'"{inviter}" and "{invitee}" have a connection')
def step_impl(context, inviter, invitee):
    context.execute_steps('''
        When "''' + invitee + '''" sends trustping to "''' + inviter + '''"
        Then "''' + inviter + '''" and "''' + invitee + '''" have a connection
        ''')


@when(u'"{inviteinterceptor}" sends a connection request to "{inviter}" based on the connection invitation')
def step_impl(context, inviteinterceptor, inviter):
    context.execute_steps('''
        When "''' + inviteinterceptor + '''" receives the connection invitation
    ''')
    inviteinterceptor_url = context.config.userdata.get(inviteinterceptor)
    inviteinterceptor_connection_id = context.connection_id_dict[inviteinterceptor]
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.connection_id_dict[inviter]

    # get connection and verify status before call
    assert connection_status(inviteinterceptor_url, inviteinterceptor_connection_id, ["invitation"])

    (resp_status, resp_text) = agent_backchannel_POST(inviteinterceptor_url + "/agent/command/", "connection", operation="accept-invitation", id=inviteinterceptor_connection_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    # get connection and verify status
    assert connection_status(inviteinterceptor_url, inviteinterceptor_connection_id, "request")

@then(u'"{inviter}" sends a request_not_accepted error')
def step_impl(context, inviter):
    inviter_url = context.config.userdata.get(inviter)
    inviter_connection_id = context.connection_id_dict[inviter]

    # TODO It is expected that accept-request should send a request not accepted error, not a 500
    (resp_status, resp_text) = agent_backchannel_POST(inviter_url + "/agent/command/", "connection", operation="accept-request", id=inviter_connection_id)
    # TODO once bug 418 has been fixed change this assert to the proper response code. 
    # bug reference URL: https://app.zenhub.com/workspaces/von---verifiable-organization-network-5adf53987ccbaa70597dbec0/issues/hyperledger/aries-cloudagent-python/418
    assert resp_status == 406, f'resp_status {resp_status} is not 406; {resp_text}'
    #assert resp_status == 500

    # Invitee should still be active based on the inviter connection id.
    #assert connection_status(inviter_url, inviter_connection_id, ["active"])

@given(u'"{inviter}" generated a multi-use connection invitation')
def step_impl(context, inviter):
    context.execute_steps('''
        When "''' + inviter + '''" generates a connection invitation
    ''')


@when(u'"{sender}" and "{receiver}" complete the connection process')
def step_impl(context, sender, receiver):
    context.execute_steps(u'''
         When "''' + receiver + '''" receives the connection invitation
         And "''' + receiver + '''" sends a connection request to "''' + sender + '''"
         And "''' + sender + '''" receives the connection request
         And "''' + sender + '''" sends a connection response to "''' + receiver + '''"
         And "''' + receiver + '''" receives the connection response
         And "''' + receiver + '''" sends trustping to "''' + sender + '''"
    ''')

@then('"{inviter}" and "{invitee}" are able to complete the connection')
def step_impl(context):
    raise NotImplementedError('STEP: Then "Alice" and "Bob" are able to complete the connection')


@then(u'"{receiver}" and "{sender}" have another connection')
def step_impl(context, receiver, sender):
    context.execute_steps(u'''
        Then "''' + sender + '''" and "''' + receiver + '''" have a connection
    ''')


@given(u'"Bob" has Invalid DID Method')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given "Bob" has Invalid DID Method')


@then(u'"Alice" sends an request not accepted error')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then "Alice" sends an request not accepted error')


@then(u'the state of "Alice" is reset to Null')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the state of "Alice" is reset to Null')


@then(u'the state of "Bob" is reset to Null')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the state of "Bob" is reset to Null')


@given(u'"Bob" has unknown endpoint protocols')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given "Bob" has unknown endpoint protocols')