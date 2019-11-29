from behave import *
import json
from agent_proxy_utils import agent_proxy_GET, agent_proxy_POST


@given('we have two agents "{inviter}" and "{invitee}"')
def step_impl(context, inviter, invitee):
    print(inviter, invitee)
    inviter_url = context.config.userdata.get(inviter)
    invitee_url = context.config.userdata.get(invitee)
    print(inviter_url, invitee_url)
    assert inviter_url is not None and 0 < len(inviter_url)
    assert invitee_url is not None and 0 < len(invitee_url)

@when('"{inviter}" generates a connection invitation')
def step_impl(context, inviter):
    inviter_url = context.config.userdata.get(inviter)

    (resp_status, resp_text) = agent_proxy_POST(inviter_url + "/agent/command/", "connection", operation="create-invitation")

    assert resp_status == 200
    context.alice_invitation = resp_text

@when('"{invitee}" accepts the connection invitation')
def step_impl(context, invitee):
    invitee_url = context.config.userdata.get(invitee)

    alice_invitation = json.loads(context.alice_invitation)
    data = alice_invitation["invitation"]
    (resp_status, resp_text) = agent_proxy_POST(invitee_url + "/agent/command/", "connection", operation="receive-invitation", data=data)
    assert resp_status == 200

@then('"{inviter}" and "{invitee}" have a connection')
def step_impl(context, inviter, invitee):
    inviter_url = context.config.userdata.get(inviter)
    invitee_url = context.config.userdata.get(invitee)

    (resp_status, resp_text) = agent_proxy_GET(inviter_url + "/agent/command/", "connection")
    assert resp_status == 200

    (resp_status, resp_text) = agent_proxy_GET(invitee_url + "/agent/command/", "connection")
    assert resp_status == 200


@given('"{sender}" and "{receiver}" have an existing connection')
def step_impl(context, sender, receiver):
    print(sender, receiver)
    context.execute_steps(u'''
       Given we have two agents "''' + sender + '''" and "''' + receiver + '''"
        When "''' + sender + '''" generates a connection invitation
         And "''' + receiver + '''" accepts the connection invitation
        Then "''' + sender + '''" and "''' + receiver + '''" have a connection
    ''')

@when('"{sender}" sends a trust ping to "{receiver}"')
def step_impl(context, sender, receiver):
    pass

@then('"{receiver}" receives a trust ping from "{sender}"')
def step_impl(context, sender, receiver):
    pass

