from typing import Optional
from behave import when, then
from behave.runner import Context
from agent_backchannel_client import (
    agent_backchannel_POST,
    expected_agent_state,
)


@when('"{recipient}" requests mediation from "{mediator}"')
def step_impl(context: Context, recipient: str, mediator: str):
    recipient_url: str = context.config.userdata.get(recipient)
    connection_id: str = context.connection_id_dict[recipient][mediator]

    (resp_status, resp_text) = agent_backchannel_POST(
        f"{recipient_url}/agent/command/",
        "mediation",
        operation="send-request",
        id=connection_id,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"


@when('"{mediator}" grants the mediation request from "{recipient}"')
def step_impl(context: Context, mediator: str, recipient: str):
    mediator_url: str = context.config.userdata.get(mediator)

    # We don't have the thread id, so we use the connection id as an identifier
    connection_id: str = context.connection_id_dict[mediator][recipient]

    (resp_status, resp_text) = agent_backchannel_POST(
        f"{mediator_url}/agent/command/",
        "mediation",
        operation="send-grant",
        id=connection_id,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"


@when('"{mediator}" denies the mediation request from "{recipient}"')
def step_impl(context: Context, mediator: str, recipient: str):
    mediator_url: str = context.config.userdata.get(mediator)

    # We don't have the thread id, so we use the connection id as an identifier
    connection_id: str = context.connection_id_dict[mediator][recipient]

    (resp_status, resp_text) = agent_backchannel_POST(
        f"{mediator_url}/agent/command/",
        "mediation",
        operation="send-deny",
        id=connection_id,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"


@then('"{recipient}" has "{mediator}" set up as a mediator')
def step_impl(context: Context, recipient: str, mediator: str):
    recipient_url: str = context.config.userdata.get(recipient)
    recipient_connection_id: str = context.connection_id_dict[recipient][mediator]
    mediator_url: str = context.config.userdata.get(mediator)
    mediator_connection_id: str = context.connection_id_dict[mediator][recipient]

    # assert recipient has state grant-received
    assert expected_agent_state(
        recipient_url,
        "mediation",
        recipient_connection_id,
        "grant-received",
        wait_time=60.0,
    )

    # assert mediator has state grant-sent
    assert expected_agent_state(
        mediator_url, "mediation", mediator_connection_id, "grant-sent", wait_time=60.0
    )


@then('"{mediator}" has denied the mediation request from "{recipient}"')
def step_impl(context: Context, mediator: str, recipient: str):
    recipient_url: str = context.config.userdata.get(recipient)
    recipient_connection_id: str = context.connection_id_dict[recipient][mediator]
    mediator_url: str = context.config.userdata.get(mediator)
    mediator_connection_id: str = context.connection_id_dict[mediator][recipient]

    # assert recipient has state deny-received
    assert expected_agent_state(
        recipient_url,
        "mediation",
        recipient_connection_id,
        "deny-received",
        wait_time=60.0,
    )

    # assert mediator has state deny-sent
    assert expected_agent_state(
        mediator_url, "mediation", mediator_connection_id, "deny-sent", wait_time=60.0
    )


@given('"{sender}" and "{receiver}" create a new didexchange connection')
@when(
    '"{sender}" and "{receiver}" create a new didexchange connection using "{mediator}" as a mediator'
)
def step_impl(context, sender: str, receiver: str, mediator: Optional[str] = None):
    # If mediator is passed, append it to the send invitation message
    if mediator:
        send_invitation = f"""
            When "{sender}" sends an explicit invitation to "{receiver}" using "{mediator}" as a mediator
        """
    else:
        send_invitation = f"""
            When "{sender}" sends an explicit invitation to "{receiver}"
        """

    # Almost all agents only allow mediation to be set-up once for a given connection
    # Reusing existing connections could mean mediation has already been set-up.
    context.use_existing_connection = False
    context.use_existing_connection_successful = False
    context.execute_steps(
        f"""
        {send_invitation}
        And "{receiver}" receives the invitation
        When "{receiver}" sends the request to "{sender}"
        And "{sender}" receives the request
        And "{sender}" sends a response to "{receiver}"
        And "{receiver}" receives the response
        And "{receiver}" sends complete to "{sender}"
        Then "{sender}" and "{receiver}" have a connection
    """
    )
