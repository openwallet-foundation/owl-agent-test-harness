from behave import when
import json
from agent_backchannel_client import (
    agent_backchannel_POST
)

@when('"{sender}" sends a connectionless out of band invitation to "{receiver}" with "{message_type}"')
def step_impl(context, sender: str, receiver: str, message_type: str):
    sender_url = context.config.userdata.get(sender)

    if message_type == "credential-offer":
        attachment = context.credential_offer
    elif message_type == "proof-request":
        attachment = context.proof_request
    else:
        raise Exception(f"Unsupported message type {message_type}")


    data = {
        "attachments": [attachment]
    }

    (resp_status, resp_text) = agent_backchannel_POST(
        sender_url + "/agent/command/",
        "out-of-band",
        operation="send-invitation-message",
        data=data,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"

    resp_json = json.loads(resp_text)
    assert resp_json["state"] == "invitation-sent"
    context.responder_invitation = resp_json["invitation"]

    # Check to see if the responder name is the same as this person. If not, it is a 3rd person acting as an issuer that needs a connection
    # TODO: it would be nicer to pass the names on every call to remove the need for global keeping of who's the requester / responder
    if context.responder_name != sender:
        context.responder_name = sender
        context.responder_url = sender_url
    if context.requester_name != receiver:
        context.requester_name = receiver
        context.requester_url = context.config.userdata.get(receiver)
