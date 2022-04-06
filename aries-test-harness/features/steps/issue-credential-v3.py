from behave import *
import json
from agent_backchannel_client import agent_backchannel_POST, agent_backchannel_GET

CRED_FORMAT_INDY = "indy"
CRED_FORMAT_JSON_LD = "json-ld"


@given('"{issuer}" is ready to issue a credential using WACI')
def step_impl(context, issuer: str):
    issuer_url = context.config.userdata.get(issuer)

    data = {
        "did_method": context.did_method,
        "proof_type": context.proof_type
    }

    (resp_status, resp_text) = agent_backchannel_POST(issuer_url + "/agent/command/", "issue-credential-v3",
                                                      operation="prepare-json-ld", data=data)

    assert resp_status == 200, f'waci/prepare-json-ld: resp_status {resp_status} is not 200; {resp_text}'


@when('"{holder}" uses WACI to propose a credential to "{issuer}"')
def step_impl(context, holder, issuer):
    holder_url = context.config.userdata.get(holder)

    data = {
        "pthid": context.invitation_v2[issuer]["id"],
        "connectionID": context.connection_id_dict[holder][issuer]
    }

    (resp_status, resp_text) = agent_backchannel_POST(holder_url + "/agent/command/", "issue-credential-v3",
                                                      operation="send-proposal",
                                                      data=data)

    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    resp_json = json.loads(resp_text)

    # Get the thread ID from the response text.
    context.cred_thread_id = resp_json["thread_id"]


@then('"{issuer}" validates the proposal')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)

    (resp_status, resp_text) = agent_backchannel_GET(issuer_url + "/agent/command/", "issue-credential-v3",
                                                     id="retrieve-credential-proposal")

    credential_proposal = json.loads(resp_text)

    pthid_from_proposal = credential_proposal["pthid"]

    expected_pthid = context.invitation_v2[issuer]["id"]

    assert pthid_from_proposal == expected_pthid, \
        f"Failed to correlate the credential proposal with the out of band invitation. " \
        f"The pthid in the proposal is {pthid_from_proposal} but {expected_pthid} was expected."


@then('"{issuer}" sends a Credential Manifest along with a Credential Fulfillment preview')
def step_impl(context, issuer):
    waci_send_offer_attachments_json_file = open('features/data/waci_send_offer_attachments.json')
    waci_send_offer_attachments_json = json.load(waci_send_offer_attachments_json_file)

    # In a later step, the issuer will verify that the holder send the expected Credential Manifest ID.
    # Here we save it in the context, so it can be checked later.
    context.manifest_id = waci_send_offer_attachments_json[0]["data"]["json"]["credential_manifest"]["id"]

    issuer_url = context.config.userdata.get(issuer)

    (resp_status, resp_text) = agent_backchannel_POST(issuer_url + "/agent/command/", "issue-credential-v3",
                                                      operation="send-offer", id=context.cred_thread_id,
                                                      data=waci_send_offer_attachments_json)

    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'


@then('"{holder}" sends a Credential Application')
def step_impl(context, holder):
    waci_send_request_attachment_json_file = open('features/data/waci_send_request_attachment.json')
    waci_send_request_attachment_json = json.load(waci_send_request_attachment_json_file)
    holder_url = context.config.userdata.get(holder)

    (resp_status, resp_text) = agent_backchannel_POST(holder_url + "/agent/command/", "issue-credential-v3",
                                                      operation="send-request", id=context.cred_thread_id,
                                                      data=waci_send_request_attachment_json)

    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'


@then('"{issuer}" validates the Credential Application')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)

    (resp_status, resp_text) = agent_backchannel_GET(issuer_url + "/agent/command/", "issue-credential-v3",
                                                     id="retrieve-credential-application")

    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    credential_application_attachment = json.loads(resp_text)

    manifest_id_in_credential_application = credential_application_attachment["credential_application"]["manifest_id"]

    assert manifest_id_in_credential_application == context.manifest_id, \
        f"Credential Manifest ID in the received Credential Application ({manifest_id_in_credential_application}) " \
        f"is unknown. Was expecting {context.manifest_id}"


@then('"{issuer}" sends a Credential Fulfillment')
def step_impl(context, issuer):
    waci_issue_credential_attachment_json_file = open('features/data/waci_issue_credential_attachment.json')
    waci_issue_credential_request_attachment_json = json.load(waci_issue_credential_attachment_json_file)
    issuer_url = context.config.userdata.get(issuer)

    (resp_status, resp_text) = agent_backchannel_POST(issuer_url + "/agent/command/", "issue-credential-v3",
                                                      operation="issue", id=context.cred_thread_id,
                                                      data=waci_issue_credential_request_attachment_json)

    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'


@then('"{holder}" accepts the Credential Fulfillment')
def step_impl(context, holder):
    holder_url = context.config.userdata.get(holder)

    (resp_status, resp_text) = agent_backchannel_POST(holder_url + "/agent/command/", "issue-credential-v3",
                                                      operation="store", id=context.cred_thread_id)

    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    resp_json = json.loads(resp_text)

    state = resp_json["state"]

    assert state == "done", f"state is '{state}', expected 'done'"
