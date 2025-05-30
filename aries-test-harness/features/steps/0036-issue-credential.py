import json
import time
from copy import deepcopy
from random import randint
from time import sleep

from agent_backchannel_client import (agent_backchannel_GET,
                                      agent_backchannel_POST,
                                      expected_agent_state)
from agent_test_utils import get_schema_name
from behave import given, then, when

# This step is defined in another feature file
# Given "Acme" and "Bob" have an existing connection


SCHEMA_TEMPLATE = {
    "schema_name": "test_schema.",
    "schema_version": "1.0.0",
    "attributes": ["attr_1", "attr_2", "attr_3"],
}

SCHEMA_TEMPLATE_ANONCREDS = {
    "schema": {
        "name": "test_schema.",
        "version": "1.0.0",
        "attrNames": ["attr_1", "attr_2", "attr_3"],
    },
    "options":{}
}

CRED_DEF_TEMPLATE = {
    "support_revocation": False,
    "schema_id": "",
    "tag": str(randint(1, 10000)),
}

CREDENTIAL_ATTR_TEMPLATE = [
    {"name": "attr_1", "value": "value_1"},
    {"name": "attr_2", "value": "value_2"},
    {"name": "attr_3", "value": "value_3"},
]

CRED_DEF_TEMPLATE_ANONCREDS = {
    "credential_definition": {
        "schemaId": "placeholder",
        "tag": str(randint(1, 10000)),
        "issuerId": "placeholder",
    },
    "options": {}
}

CRED_FORMAT_INDY = "indy"
CRED_FORMAT_JSON_LD = "json-ld"


@given('"{issuer}" has a public did')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)

    (resp_status, resp_text) = agent_backchannel_GET(
        issuer_url + "/agent/command/", "did"
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"

    resp_json = json.loads(resp_text)
    issuer_did = resp_json

    # check for a schema already loaded in the context. If it is not, load the template
    if not context.schema:
        if context.anoncreds:
            context.schema = SCHEMA_TEMPLATE_ANONCREDS.copy()
            context.schema["schema_name"] = get_schema_name(context) + issuer
        else:
            context.schema = SCHEMA_TEMPLATE.copy()
            context.schema["schema_name"] = get_schema_name(context) + issuer

    context.issuer_did = issuer_did["did"]
    context.issuer_did_dict[get_schema_name(context)] = issuer_did["did"]


@given('"{issuer}" is ready to issue a credential')
def step_impl(context, issuer):
    # TODO remove these references to schema and cred def, move them to one call to the API and let the Backchannel take care of
    # what to do to be ready to issue a credential
    context.execute_steps(
        f"""
      When "{issuer}" creates a new schema
       And "{issuer}" creates a new credential definition
      Then "{issuer}" has an existing schema
       And "{issuer}" has an existing credential definition
    """
    )


@when('"{issuer}" creates a new schema')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)

    # check for a schema template already loaded in the context. If it is, it was loaded from an external Schema, so use it.
    if context.schema:
        schema = context.schema
        if context.anoncreds:
            schema["schema"]["issuerId"] = context.issuer_did_dict[get_schema_name(context)]
        schema["issuer_id"] = context.issuer_did_dict[get_schema_name(context)]
    else:
        schema = SCHEMA_TEMPLATE.copy()
        schema["schema_name"] = schema["schema_name"] + issuer
        schema["issuer_id"] = context.issuer_did

    (resp_status, resp_text) = agent_backchannel_POST(
        issuer_url + "/agent/command/", "schema", data=schema, anoncreds=context.anoncreds
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"

    resp_json = json.loads(resp_text)

    # if the schema id contains indy then convert it to a legacy id.
    if "indy" in resp_json["schema_id"]:
        context.issuer_schema_id_dict[get_schema_name(context)] = convert_fully_qualified_indy_schema_id_to_legacy(resp_json["schema_id"])
    else:
        context.issuer_schema_id_dict[get_schema_name(context)] = resp_json[
            "schema_id"
        ]


@when('"{issuer}" creates a new credential definition')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)
    schema_name = get_schema_name(context)

    if context.anoncreds:
        cred_def = deepcopy(CRED_DEF_TEMPLATE_ANONCREDS)
        cred_def["credential_definition"]["schemaId"] = context.issuer_schema_id_dict[schema_name]
        cred_def["credential_definition"]["issuerId"] = context.issuer_did_dict[schema_name]
        cred_def["credential_definition"]["tag"] = str(randint(1, 10000))
    else:
        cred_def = CRED_DEF_TEMPLATE.copy()
        cred_def["schema_id"] = context.issuer_schema_id_dict[schema_name]
        cred_def["issuer_id"] = context.issuer_did_dict[schema_name]
        cred_def["tag"] = str(randint(1, 10000))

    if context.support_revocation:
        if context.anoncreds:
            cred_def["options"]["support_revocation"] = context.support_revocation
        else:
            cred_def["support_revocation"] = context.support_revocation

    (resp_status, resp_text) = agent_backchannel_POST(
        issuer_url + "/agent/command/", "credential-definition", data=cred_def, anoncreds=context.anoncreds
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"

    resp_json = json.loads(resp_text)
    if context.support_revocation:
        # Could make a call to get the rev reg creation time for calculating non revocation intervals
        # context.cred_rev_creation_time = resp_json["created"]
        context.cred_rev_creation_time = time.time()

    # if the credential definition id contains indy then convert it to a legacy id.
    if "indy" in resp_json["credential_definition_id"]:
        context.credential_definition_id_dict[get_schema_name(context)] = convert_fully_qualified_indy_cred_def_id_to_legacy(resp_json["credential_definition_id"])
    else:
        context.credential_definition_id_dict[get_schema_name(context)] = resp_json["credential_definition_id"]

@then('"{issuer}" has an existing schema')
def step_impl(context, issuer):
    schema_name = get_schema_name(context)
    issuer_url = context.config.userdata.get(issuer)
    issuer_schema_id = context.issuer_schema_id_dict[schema_name]

    (resp_status, resp_text) = agent_backchannel_GET(
        issuer_url + "/agent/command/", "schema", id=issuer_schema_id, anoncreds=context.anoncreds
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"

    resp_json = json.loads(resp_text)

    context.issuer_schema_dict[schema_name] = resp_json


@then('"{issuer}" has an existing credential definition')
def step_impl(context, issuer):
    schema_name = get_schema_name(context)
    issuer_url = context.config.userdata.get(issuer)
    issuer_credential_definition_id = context.credential_definition_id_dict[schema_name]

    (resp_status, resp_text) = agent_backchannel_GET(
        issuer_url + "/agent/command/",
        "credential-definition",
        id=issuer_credential_definition_id,
        anoncreds=context.anoncreds,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"

    resp_json = json.loads(resp_text)

    context.issuer_credential_definition_dict[schema_name] = resp_json


@given('"{issuer}" has an existing schema and credential definition')
def step_impl(context, issuer):
    context.execute_steps(
        f"""
     Given "{issuer}" has a public did
      When "{issuer}" creates a new schema
       And "{issuer}" creates a new credential definition
      Then "{issuer}" has an existing schema
       And "{issuer}" has an existing credential definition
    """
    )


@when('"{issuer}" initiates an automated credential issuance')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)
    issuer_did = context.issuer_did
    issuer_connection_id = context.connection_id_dict[issuer][context.holder_name]
    issuer_schema = context.issuer_schema
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

    (resp_status, resp_text) = agent_backchannel_POST(
        issuer_url + "/agent/command/",
        "issue-credential",
        operation="send",
        data=credential_offer,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"

    resp_json = json.loads(resp_text)
    # FIXME: this doesn't assign anything out of the scope of this function. BUG??
    issuer_credential_definition = resp_json


@given('"{holder}" proposes a credential to "{issuer}"')
@when('"{holder}" proposes a credential to "{issuer}"')
def step_impl(context, holder, issuer):
    holder_url = context.config.userdata.get(holder)
    schema_name = get_schema_name(context)

    # check for a schema template already loaded in the context. If it is, it was loaded from an external Schema, so use it.
    cred_data = context.credential_data or CREDENTIAL_ATTR_TEMPLATE.copy()

    issuer_did = context.issuer_did_dict[schema_name]
    issuer_schema = context.issuer_schema_dict[schema_name]
    issuer_cred_def = context.issuer_credential_definition_dict[schema_name]
    credential_offer = {
        "schema_issuer_did": issuer_did,
        "issuer_did": issuer_did,
        "schema_name": issuer_schema["name"],
        "cred_def_id": issuer_cred_def["id"],
        "schema_version": issuer_schema["version"],
        "credential_proposal": {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
            "attributes": cred_data,
        },
        "connection_id": context.connection_id_dict[holder][issuer],
        "schema_id": issuer_schema["id"],
    }

    (resp_status, resp_text) = agent_backchannel_POST(
        holder_url + "/agent/command/",
        "issue-credential",
        operation="send-proposal",
        data=credential_offer,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"
    resp_json = json.loads(resp_text)

    # Check the State of the credential
    assert resp_json["state"] == "proposal-sent"

    # Get the thread ID from the response text.
    context.cred_thread_id = resp_json["thread_id"]

# Some agents will have qualifed ids like did:indy:bcovrin:test:PDTK22oZnNyDSEn3XedwMq/anoncreds/v0/SCHEMA/test_schema.Acme/1.0.0
# This function will strip it down to the id only, so remove the prefix and the suffix that has : or / in it and match the regex /^([a-zA-Z0-9]{21,22}):2:(.+):([0-9.]+)$/
def convert_fully_qualified_indy_cred_def_id_to_legacy(id):
    parts = id.split(":")
    id_part = parts[-1].split("/")[0]
    schema_name = parts[-1].split("/")[4]
    schema_id = parts[-1].split("/")[5]
    cred_def_id = "CL"
    return f"{id_part}:3:{cred_def_id}:{schema_name}:{schema_id}"
    
def convert_fully_qualified_indy_schema_id_to_legacy(id):
    parts = id.split(":")
    id_part = parts[-1].split("/")[0]
    schema_name = parts[-1].split("/")[4]
    version = parts[-1].split("/")[5]
    return f"{id_part}:2:{schema_name}:{version}"

@given('"{issuer}" offers a credential')
@when('"{issuer}" offers a credential')
@when('"{issuer}" offers the credential')
@when('"{issuer}" sends a credential offer')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)

    # Sometimes proposal arrives only after send-offer is called, hence the sleep
    sleep(1)

    # If context has the credential thread id then the proposal was done.
    if context.cred_thread_id:
        (resp_status, resp_text) = agent_backchannel_POST(
            issuer_url + "/agent/command/",
            "issue-credential",
            operation="send-offer",
            id=context.cred_thread_id,
        )
        assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"
        resp_json = json.loads(resp_text)
        if "thread_id" in resp_json:
            context.cred_thread_id = resp_json["thread_id"]

    # if context does not have the credential thread id then the proposal was not the starting point for the protocol.
    else:
        cred_data = context.credential_data or CREDENTIAL_ATTR_TEMPLATE.copy()

        credential_offer = {
            "cred_def_id": context.issuer_credential_definition_dict[
                context.schema["schema_name"]
            ]["id"],
            "credential_preview": {
                "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
                "attributes": cred_data,
            },
            "connection_id": context.connection_id_dict[issuer][context.holder_name],
        }

        (resp_status, resp_text) = agent_backchannel_POST(
            issuer_url + "/agent/command/",
            "issue-credential",
            operation="send-offer",
            data=credential_offer,
        )
        assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"
        resp_json = json.loads(resp_text)
        if "thread_id" in resp_json:
            context.cred_thread_id = resp_json["thread_id"]

    # Check the state of the holder after issuers call of send-offer
    # TODO Removing this line causes too many failures in Acapy-Dotnet Acapy-Afgo.
    sleep(3)
    assert expected_agent_state(
        context.holder_url, "issue-credential", context.cred_thread_id, "offer-received"
    )

@given('"{issuer}" creates a credential offer')
@when('"{issuer}" creates a credential offer')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)

    cred_data = context.credential_data or CREDENTIAL_ATTR_TEMPLATE.copy()

    cred_def_id = context.issuer_credential_definition_dict[get_schema_name(context)]["id"]

    credential_offer = {
        "cred_def_id": cred_def_id,
        "credential_preview": {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
            "attributes": cred_data,
        }
    }

    (resp_status, resp_text) = agent_backchannel_POST(
        issuer_url + "/agent/command/",
        "issue-credential",
        operation="create-offer",
        data=credential_offer,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"
    resp_json = json.loads(resp_text)

    assert "record" in resp_json
    context.cred_thread_id = resp_json["record"]["thread_id"]
    context.credential_offer = resp_json["message"]


@when('"{holder}" requests the credential')
@when('"{holder}" sends a credential request')
def step_impl(context, holder):
    holder_url = context.holder_url

    sleep(1)

    # If @indy then we can be sure we cannot start the protocol from this command. We can be sure that we have previously
    # received the thread_id.
    # if "Indy" in context.tags:
    if context.cred_thread_id:
        (resp_status, resp_text) = agent_backchannel_POST(
            holder_url + "/agent/command/",
            "issue-credential",
            operation="send-request",
            id=context.cred_thread_id,
        )
    # If we are starting from here in the protocol you won't have the cred_ex_id or the thread_id
    else:
        (resp_status, resp_text) = agent_backchannel_POST(
            holder_url + "/agent/command/",
            "issue-credential",
            operation="send-request",
            id=context.connection_id_dict[holder][context.issuer_name],
        )

    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"
    resp_json = json.loads(resp_text)

    # If the protocol starts with a request we need a thread_id to call the issue command
    if "cred_thread_id" not in context:
        context.cred_thread_id = resp_json["thread_id"]


@when('"{issuer}" issues the credential')
@when('"{issuer}" issues a credential')
def step_impl(context, issuer):
    issuer_url = context.config.userdata.get(issuer)

    cred_data = context.credential_data or CREDENTIAL_ATTR_TEMPLATE.copy()

    # a credential preview shouldn't have to be here with a cred_ex_id being passed
    credential_preview = {
        "credential_preview": {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
            "attributes": cred_data,
        },
        "comment": "issuing credential",
    }

    (resp_status, resp_text) = agent_backchannel_POST(
        issuer_url + "/agent/command/",
        "issue-credential",
        operation="issue",
        id=context.cred_thread_id,
        data=credential_preview,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"
    resp_json = json.loads(resp_text)
    # assert resp_json["state"] == "credential-issued"

    # Verify holder status
    sleep(1.0)
    # assert expected_agent_state(context.holder_url, "issue-credential", context.cred_thread_id, "credential-received")


@when('"{holder}" acknowledges the credential issue')
@when('"{holder}" receives and acknowledges the credential')
def step_impl(context, holder):
    holder_url = context.config.userdata.get(holder)

    # a credential id shouldn't be needed with a cred_ex_id being passed
    credential_id = {
        "credential_id": context.cred_thread_id,
    }

    # (resp_status, resp_text) = agent_backchannel_POST(holder_url + "/agent/command/", "credential", operation="store", id=context.holder_cred_ex_id)
    sleep(3)
    (resp_status, resp_text) = agent_backchannel_POST(
        holder_url + "/agent/command/",
        "issue-credential",
        operation="store",
        id=context.cred_thread_id,
        data=credential_id,
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"
    resp_json = json.loads(resp_text)
    assert resp_json["state"] == "done"

    # Store credential id
    context.credential_id_dict[context.schema["schema_name"]].append(
        resp_json["credential_id"]
    )

    # Verify issuer status
    # This is returning none instead of Done. Should this be the case. Needs investigation.
    # assert expected_agent_state(context.issuer_url, "issue-credential", context.cred_thread_id, "done")

    # if the credential supports revocation, get the Issuers webhook callback JSON from the store command
    # From that JSON save off the credential revocation identifier, and the revocation registry identifier.
    if context.support_revocation:
        (resp_status, resp_text) = agent_backchannel_GET(
            context.config.userdata.get(context.issuer_name) + "/agent/response/",
            "revocation-registry",
            id=context.cred_thread_id,
        )
        assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"
        resp_json = json.loads(resp_text)
        context.cred_rev_id = resp_json["revocation_id"]
        context.rev_reg_id = resp_json["revoc_reg_id"]


@then('"{holder}" has the credential issued')
def step_impl(context, holder):

    holder_url = context.config.userdata.get(holder)
    # get the credential from the holders wallet
    (resp_status, resp_text) = agent_backchannel_GET(
        holder_url + "/agent/command/",
        "credential",
        id=context.credential_id_dict[context.schema["schema_name"]][-1],
    )
    assert resp_status == 200, f"resp_status {resp_status} is not 200; {resp_text}"
    resp_json = json.loads(resp_text)
    if "state" in resp_json and resp_json["state"] == "N/A":
        # backchannel can't get the credential
        pass
    else:
        schema_name = context.schema["schema_name"]
        credentials = context.credential_id_dict[schema_name]

        # Check with last credential id
        assert resp_json["referent"] == credentials[-1]
        # Some agents don't return or have a schema id or cred_def_id, so only check it it exists.
        if "schema_id" in resp_json:
            if "indy" in resp_json["schema_id"]:
                assert convert_fully_qualified_indy_schema_id_to_legacy(resp_json["schema_id"]) == context.issuer_schema_id_dict[schema_name]
            else:
                assert resp_json["schema_id"] == context.issuer_schema_id_dict[schema_name]
        if "cred_def_id" in resp_json:
            if "indy" in resp_json["cred_def_id"]:
                assert convert_fully_qualified_indy_cred_def_id_to_legacy(resp_json["cred_def_id"]) == context.credential_definition_id_dict[schema_name]
            else:
                assert (
                    resp_json["cred_def_id"]
                    == context.credential_definition_id_dict[schema_name]
                )

    # Make sure the issuer is not holding the credential
    # get the credential from the holders wallet
    # TODO this expected error is not displaying in the agent output until after all the tests are executed. Uncomment this out when
    # there is a solution to the error messaging happening at the end.
    # (resp_status, resp_text) = agent_backchannel_GET(context.issuer_url + "/agent/command/", "credential", id=context.credential_id_dict[context.schema['schema_name']])
    # assert resp_status == 404, f'resp_status {resp_status} is not 404; {resp_text}'


@when('"{holder}" negotiates the offer with a proposal of the credential to "{issuer}"')
@when(
    '"{holder}" negotiates the offer with another proposal of the credential to "{issuer}"'
)
def step_impl(context, holder, issuer):
    context.execute_steps(
        f"""
        When "{holder}" proposes a credential to "{issuer}"
    """
    )
