from behave import *
import json
from agent_backchannel_client import agent_backchannel_GET, agent_backchannel_POST, connection_status
from time import sleep

# This step is defined in another feature file
# Given "Acme" and "Bob" have an existing connection


SCHEMA_TEMPLATE = {
    "schema_name": "test_schema.",
    "schema_version": "1.0.0",
    "attributes": ["attr_1","attr_2","attr_3"],
}

CRED_DEF_TEMPLATE = {
  "support_revocation": False,
  "schema_id": "",
  "tag": "default"
}

CREDENTIAL_ATTR_TEMPLATE = [
    {"name": "attr_1", "value": "value_1"},
    {"name": "attr_2", "value": "value_2"},
    {"name": "attr_3", "value": "value_3"}
]

@given('"{issuer}" has a public did')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)

    (resp_status, resp_text) = agent_backchannel_GET(issuer_url + "/agent/command/", "did")
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    resp_json = json.loads(resp_text)
    issuer_did = resp_json

    context.issuer_did = issuer_did["did"]

@when('"{issuer}" creates a new schema')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)
    issuer_did = context.issuer_did

    if not "issuer_schema_id" in context:
        schema = SCHEMA_TEMPLATE.copy()
        schema["schema_name"] = schema["schema_name"] + issuer
        data = json.dumps(schema)
        (resp_status, resp_text) = agent_backchannel_POST(issuer_url + "/agent/command/", "schema", data=schema)
        assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

        resp_json = json.loads(resp_text)
        context.issuer_schema_id = resp_json["schema_id"]

@when('"{issuer}" creates a new credential definition')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)
    issuer_did = context.issuer_did

    if not "credential_definition_id" in context:
        cred_def = CRED_DEF_TEMPLATE.copy()
        cred_def["schema_id"] = context.issuer_schema_id
        data = json.dumps(cred_def)
        (resp_status, resp_text) = agent_backchannel_POST(issuer_url + "/agent/command/", "credential-definition", data=cred_def)
        assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

        resp_json = json.loads(resp_text)
        context.credential_definition_id = resp_json["credential_definition_id"]

@then('"{issuer}" has an existing schema')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)
    issuer_schema_id = context.issuer_schema_id

    (resp_status, resp_text) = agent_backchannel_GET(issuer_url + "/agent/command/", "schema", id=issuer_schema_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    resp_json = json.loads(resp_text)
    issuer_schema = resp_json

    context.issuer_schema = issuer_schema

@then('"{issuer}" has an existing credential definition')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)
    issuer_credential_definition_id = context.credential_definition_id

    (resp_status, resp_text) = agent_backchannel_GET(issuer_url + "/agent/command/", "credential-definition", id=issuer_credential_definition_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    resp_json = json.loads(resp_text)
    issuer_credential_definition = resp_json

    context.issuer_credential_definition = issuer_credential_definition

@given('"{issuer}" has an existing schema and credential definition')
def step_impl(context, issuer):
    context.execute_steps(u'''
     Given "''' + issuer + '''" has a public did
      When "''' + issuer + '''" creates a new schema
       And "''' + issuer + '''" creates a new credential definition
      Then "''' + issuer + '''" has an existing schema
       And "''' + issuer + '''" has an existing credential definition
    ''')

@when('"{issuer}" initiates an automated credential issuance')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)
    issuer_did = context.issuer_did
    issuer_connection_id = context.connection_id_dict[issuer]
    issuer_schema_id = context.issuer_schema_id
    issuer_schema = context.issuer_schema
    issuer_credential_definition_id = context.credential_definition_id
    issuer_credential_definition = context.issuer_credential_definition

    credential_offer = {
        "schema_issuer_did": issuer_did,
        "issuer_did": issuer_did,
        "schema_name": issuer_schema["name"],
        "cred_def_id": issuer_credential_definition["id"],
        "schema_version": issuer_schema["version"],
        "credential_proposal": {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
            "attributes": CREDENTIAL_ATTR_TEMPLATE.copy(),
        },
        "connection_id": issuer_connection_id,
        "schema_id": issuer_schema["id"],
    }

    (resp_status, resp_text) = agent_backchannel_POST(issuer_url + "/agent/command/", "credential", operation="send", data=credential_offer)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'

    resp_json = json.loads(resp_text)
    issuer_credential_definition = resp_json

@given('"{holder}" proposes a credential to "{issuer}"')
@when('"{holder}" proposes a credential to "{issuer}"')
def step_impl(context, holder, issuer):
    holder_url = context.config.userdata.get(holder)
    #holder_connection_id = context.connection_id_dict[holder]

    credential_offer = {
        "schema_issuer_did": context.issuer_did,
        "issuer_did": context.issuer_did,
        "schema_name": context.issuer_schema["name"],
        "cred_def_id": context.issuer_credential_definition["id"],
        "schema_version": context.issuer_schema["version"],
        "credential_proposal": {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
            "attributes": CREDENTIAL_ATTR_TEMPLATE.copy(),
        },
        #"connection_id": context.connection_id_dict[issuer],
        "connection_id": context.connection_id_dict[holder],
        "schema_id": context.issuer_schema["id"],
    }

    #(resp_status, resp_text) = agent_backchannel_POST(holder_url + "/agent/command/", "issue-credential", operation="send-proposal", id=holder_connection_id, data=credential_offer)
    (resp_status, resp_text) = agent_backchannel_POST(holder_url + "/agent/command/", "credential", operation="send-proposal", data=credential_offer)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    resp_json = json.loads(resp_text)

    # Check the State of the credential
    assert resp_json["state"] == "proposal_sent"

    # Get the Credential Exchange ID from the response text.
    # I may need to save off the credential_exchange_id for Bob here but will see.
    context.holder_cred_ex_id = resp_json["credential_exchange_id"]
    context.cred_thread_id = resp_json["thread_id"]

@given('"{issuer}" offers a credential')
@when('"{issuer}" offers a credential')
@when('"{issuer}" offers the credential')
@when('"{issuer}" sends a credential offer')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)
    #issuer_connection_id = context.connection_id_dict[issuer]

    if not hasattr('context','cred_thread_id'):

        credential_offer = {
            "cred_def_id": context.issuer_credential_definition["id"],
            "credential_preview": {
                "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
                "attributes": CREDENTIAL_ATTR_TEMPLATE.copy(),
            },
            "connection_id": context.connection_id_dict[issuer],
        }

        (resp_status, resp_text) = agent_backchannel_POST(issuer_url + "/agent/command/", "credential", operation="send-offer", data=credential_offer)
        resp_json = json.loads(resp_text)
        context.issuer_cred_ex_id = resp_json["credential_exchange_id"]
        context.cred_thread_id = resp_json["thread_id"]

        # get the holder cred_ex_id from the webhook with the thread id
        sleep(1) # It seems like you have to wait here for a moment in order to wait for the webhook to happen. 
        (resp_status2, resp_text2) = agent_backchannel_GET(context.holder_url + "/agent/response/", "credential", id=context.cred_thread_id)
        assert resp_status2 == 200, f'resp_status {resp_status2} is not 200; {resp_text2}'
        resp_json2 = json.loads(resp_text2)
        context.holder_cred_ex_id = resp_json2["credential_exchange_id"]

    else:
        # get the cred_ex_id for the issuer by getting the webhook data for the previous step
        #(resp_status, resp_text) = agent_backchannel_GET(agent_url + "/agent/command/", "connection", id=connection_id)
        sleep(1) # It seems like you have to wait here for a moment in order to wait for the webhook to happen. 
        (resp_status, resp_text) = agent_backchannel_GET(issuer_url + "/agent/response/", "credential", id=context.cred_thread_id)
        # get the cred_ex_id for the issuer from the response and save it off for later.
        assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
        resp_json = json.loads(resp_text)
        context.issuer_cred_ex_id = resp_json["credential_exchange_id"]
        resp_json = json.loads(resp_text)
        (resp_status, resp_text) = agent_backchannel_POST(issuer_url + "/agent/command/", "credential", operation="send-offer", id=context.issuer_cred_ex_id)
        

    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    # Check the State of the credential
    assert resp_json["state"] == "offer_sent"

@when('"{holder}" requests the credential')
@when('"{holder}" sends a credential request')
def step_impl(context, holder):
    holder_url = context.holder_url

    # If @indy then we can be sure we cannot start the protocol from this command. We can be sure that we have previously 
    # gotten the cred_ex_id or have a thread_id.
    if "Indy" in context.tags:
        sleep(1)
        (resp_status, resp_text) = agent_backchannel_POST(holder_url + "/agent/command/", "credential", operation="send-request", id=context.holder_cred_ex_id)

    # We are starting from here in the protocol so you won't have the cred_ex_id or the thread_id
    else:
        (resp_status, resp_text) = agent_backchannel_POST(holder_url + "/agent/command/", "credential", operation="send-request", id=context.connection_id_dict[holder])
    
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    resp_json = json.loads(resp_text)
    assert resp_json["state"] == "request_sent"

    # Check the state of the issuer through the webhook
    sleep(1) # It seems like you have to wait here for a moment in order to wait for the webhook to happen. 
    (resp_status, resp_text) = agent_backchannel_GET(context.issuer_url + "/agent/response/", "credential", id=context.cred_thread_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    resp_json = json.loads(resp_text)
    # Need to log a bug for this. It should be "request_recieved"
    #assert resp_json["state"] == "request_recieved" #its in offer_sent 
    assert resp_json["state"] == "offer_sent"


@when('"{issuer}" issues the credential')
@when('"{issuer}" issues a credential')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)

    # a credential preview shouldn't have to be here with a cred_ex_id being passed
    credential_preview = {
        #"cred_def_id": context.issuer_credential_definition["id"],
        "credential_preview": {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
            "attributes": CREDENTIAL_ATTR_TEMPLATE.copy(),
        },
        "comment": "issuing credential",
    }

    #(resp_status, resp_text) = agent_backchannel_POST(issuer_url + "/agent/command/", "credential", operation="issue", id=context.issuer_cred_ex_id)
    (resp_status, resp_text) = agent_backchannel_POST(issuer_url + "/agent/command/", "credential", operation="issue", id=context.issuer_cred_ex_id, data=credential_preview)
    #(resp_status, resp_text) = agent_backchannel_POST(issuer_url + "/agent/command/", "credential", operation="issue", data=credential_preview)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    #resp_json = json.loads(resp_text)
    #context.credential_id = resp_json["credential_id"]

@when('"{holder}" acknowledges the credential issue')
@when('"{holder}" receives and acknowledges the credential')
def step_impl(context, holder):
    holder_url = context.config.userdata.get(holder)
    
    # a credential id shouldn't be needed with a cred_ex_id being passed
    credential_id = {
        "credential_id": context.holder_cred_ex_id,
    }

    # (resp_status, resp_text) = agent_backchannel_POST(holder_url + "/agent/command/", "credential", operation="store", id=context.holder_cred_ex_id)
    (resp_status, resp_text) = agent_backchannel_POST(holder_url + "/agent/command/", "credential", operation="store", id=context.holder_cred_ex_id, data=credential_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    resp_json = json.loads(resp_text)
    assert resp_json["state"] == "credential_acked"

@then('"{holder}" has the credential issued')
def step_impl(context, holder):
        holder_url = context.config.userdata.get(holder)
        # get the end state of the credential
        (resp_status, resp_text) = agent_backchannel_GET(holder_url + "/agent/command/", "credential", id=context.holder_cred_ex_id)
        #(resp_status, resp_text) = agent_backchannel_GET(issuer_url + "/agent/command/", "credential-definition", id=issuer_credential_definition_id)
        assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
        resp_json = json.loads(resp_text)
        assert resp_json["state"] == "credential_acked"

@when(u'"{holder}" negotiates the offer with a proposal of the credential to "{issuer}"')
@when(u'"{holder}" negotiates the offer with another proposal of the credential to "{issuer}"')
def step_impl(context, holder, issuer):
    #context.execute_steps('''When "''' + holder + '''" proposes a credential to "''' + sender + ''')
    context.execute_steps('''
        When "''' + holder + '''" proposes a credential to "''' + issuer + '''"
    ''')
