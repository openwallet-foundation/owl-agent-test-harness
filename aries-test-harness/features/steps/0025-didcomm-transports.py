import json
from behave import then
from behave.runner import Context


@then('the invitation serviceEndpoint should use the "{transport_str}" protocol scheme')
def step_impl(context: Context, transport_str: str):
    transport_list = json.loads(transport_str)

    if "DIDExchangeConnection" in context.tags:
        serviceEndpoint = context.responder_invitation["services"][0]["serviceEndpoint"]
    else:
        serviceEndpoint = context.inviter_invitation["serviceEndpoint"]

    for transport in transport_list:
        if serviceEndpoint.startswith(transport):
            return

    raise Exception(
        f"Invitation serviceEndpoint ({serviceEndpoint}) should use {transport_list} transport"
    )
