from behave import *
import json
from agent_proxy_utils import agent_proxy_GET, agent_proxy_POST


@given('we have behave installed')
def step_impl(context):
    pass

@when('we implement a test')
def step_impl(context):
    assert True is not False

@then('behave will test it for us!')
def step_impl(context):
    assert context.failed is False


@given('we have two agents Alice and Bob')
def step_impl(context):
    pass

@when('Alice generates a connection invitation')
def step_impl(context):
    (resp_status, resp_text) = agent_proxy_POST("http://localhost:8020/agent/command/", "connection", operation="create-invitation")

    assert resp_status == 200
    context.alice_invitation = resp_text

@when('Bob accepts the connection invitation')
def step_impl(context):
    alice_invitation = json.loads(context.alice_invitation)
    data = alice_invitation["invitation"]
    (resp_status, resp_text) = agent_proxy_POST("http://localhost:8020/agent/command/", "connection", operation="receive-invitation", data=data)
    assert resp_status == 200

@then('Alice and Bob have a connection')
def step_impl(context):
    (resp_status, resp_text) = agent_proxy_GET("http://localhost:8020/agent/command/", "connection")
    assert resp_status == 200


@given('Alice and Bob have an existing connection')
def step_impl(context):
    context.execute_steps(u'''
        When Alice generates a connection invitation
         And Bob accepts the connection invitation
        Then Alice and Bob have a connection
    ''')

@when('Alice sends a trust ping to Bob')
def step_impl(context):
    pass

@then('Bob receives a trust ping from Alice')
def step_impl(context):
    pass

