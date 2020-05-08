from behave import *
import json
from agent_backchannel_client import agent_backchannel_GET, agent_backchannel_POST, connection_status

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


@when('"{issuer}" sends a credential offer')
def step_impl(context, issuer):
    pass

@when('"{receiver}" sends a credential request')
def step_impl(context, receiver):
    pass

@when('"{issuer}" issues a credential')
def step_impl(context, issuer):
    pass

@when('"{receiver}" receives and acknowledges the credential')
def step_impl(context, receiver):
    pass

@then('"{issuer}" has an acknowledged credential issue')
def step_impl(context, issuer):
    pass

@then('"{issuer}" has received a credential')
def step_impl(context, issuer):
    pass
