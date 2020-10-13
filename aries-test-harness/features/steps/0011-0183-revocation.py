# -----------------------------------------------------------
# Behave Step Definitions for Credential Revocation 0011 and Revocation Notification Protocol 0183
# used to revoke issued credentials.
#
# GitHub Issue(s) for Test Development:
# https://app.zenhub.com/workspaces/von---verifiable-organization-network-5adf53987ccbaa70597dbec0/issues/hyperledger/aries-agent-test-harness/102
#
# 0011 Revocation RFC: 
# https://github.com/hyperledger/aries-rfcs/tree/9b0aaa39df7e8bd434126c4b33c097aae78d65bf/features/0160-connection-protocol#0160-connection-protocol
#
# 0183 Revocation Notification RFC:
# https://github.com/hyperledger/aries-rfcs/tree/master/features/0183-revocation-notification
#
# Current AIP version level of test coverage: N/A - Revocation is not apart of any AIP Version
#  
# -----------------------------------------------------------

from behave import *
import json
from agent_backchannel_client import agent_backchannel_GET, agent_backchannel_POST, expected_agent_state

@when('{issuer} revokes the credential')
def step_impl(context, issuer):

    issuer_url = context.config.userdata.get(issuer)

    credential_revocation = {
        "cred_rev_id": context.cred_rev_id,
        "rev_registry_id": context.rev_reg_id,
        "publish_immediately": True,
    }

    (resp_status, resp_text) = agent_backchannel_POST(issuer_url + "/agent/command/", "revocation", operation="revoke", data=credential_revocation)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    #resp_json = json.loads(resp_text)

    # Check the Holder wallet for the credential
    # Should be a 200 since the revoke doesn't remove the cred from the holders wallet. 
    # What else to check?
    (resp_status, resp_text) = agent_backchannel_GET(context.config.userdata.get(context.holder_name) + "/agent/command/", "credential", id=context.credential_id_dict[context.schema['schema_name']])
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'


@when('"{prover}" makes the {presentation} of the proof with the revoked credential')
def step_impl(context, prover, presentation):
    # swap previous cred ID with current?

    # Then call prover makes the presentation of the proof
    context.execute_steps('''
        When "''' + prover + '''" makes the {presentation} of the proof
    '''.format(presentation=presentation))

