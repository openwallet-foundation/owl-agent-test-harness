from behave import *
import json
from agent_backchannel_client import agent_backchannel_GET, agent_backchannel_POST, connection_status
from time import sleep

@given(u'"{prover}" has an issued credential from {issuer}')
def step_impl(context, prover, issuer):
    # create the Connection between the prover and the issuer
    # TODO: May need to check for an existing connection here instead of creating one.
    context.execute_steps('''
        Given "''' + issuer + '''" and "''' + prover + '''" have an existing connection
    ''')

    # make sure the issuer has the credential definition
    context.execute_steps('''
     Given "''' + issuer + '''" has a public did
      When "''' + issuer + '''" creates a new schema
       And "''' + issuer + '''" creates a new credential definition
      Then "''' + issuer + '''" has an existing schema
       And "''' + issuer + '''" has an existing credential definition
    ''')

    # setup the holder and issuer for the issue cred sceneario below. The data table in the tests does not setup a holder.
    # The prover is also the holder.
    context.holder_url = context.config.userdata.get(prover)
    context.holder_name = prover
    assert context.holder_url is not None and 0 < len(context.holder_url)
    # The issuer was not in the data table, it was in the gherkin scenario outline examples, so get it and assign it.
    context.issuer_url = context.config.userdata.get(issuer)
    context.issuer_name = issuer
    assert context.issuer_url is not None and 0 < len(context.issuer_url)

    # issue the credential to prover
    context.execute_steps('''
        When  "''' + issuer + '''" offers a credential
        And "''' + prover + '''" requests the credential
        And  "''' + issuer + '''" issues the credential
        And "''' + prover + '''" acknowledges the credential issue
        Then "''' + prover + '''" has the credential issued
    ''')



#@given('"{holder}" proposes a credential to "{issuer}"')
#@when('"{holder}" proposes a credential to "{issuer}"')
# def step_impl(context, holder, issuer):
#     holder_url = context.config.userdata.get(holder)
#     #holder_connection_id = context.connection_id_dict[holder]

#     credential_offer = {
#         "schema_issuer_did": context.issuer_did,
#         "issuer_did": context.issuer_did,
#         "schema_name": context.issuer_schema["name"],
#         "cred_def_id": context.issuer_credential_definition["id"],
#         "schema_version": context.issuer_schema["version"],
#         "credential_proposal": {
#             "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
#             "attributes": CREDENTIAL_ATTR_TEMPLATE.copy(),
#         },
#         #"connection_id": context.connection_id_dict[issuer],
#         "connection_id": context.connection_id_dict[holder],
#         "schema_id": context.issuer_schema["id"],
#     }

#     #(resp_status, resp_text) = agent_backchannel_POST(holder_url + "/agent/command/", "issue-credential", operation="send-proposal", id=holder_connection_id, data=credential_offer)
#     (resp_status, resp_text) = agent_backchannel_POST(holder_url + "/agent/command/", "issue-credential", operation="send-proposal", data=credential_offer)
#     assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
#     resp_json = json.loads(resp_text)

#     # Check the State of the credential
#     assert resp_json["state"] == "proposal_sent"

#     # Get the Credential Exchange ID from the response text.
#     # I may need to save off the credential_exchange_id for Bob here but will see.
#     context.holder_cred_ex_id = resp_json["credential_exchange_id"]
#     context.cred_thread_id = resp_json["thread_id"]

@when('"{verifier}" sends a request for proof presentation to "{prover}"')
def step_impl(context, verifier, prover):
    verifier_url = context.verifier_url
    prover_url = context.prover_url

    # Check the beginning state for both roles. Maybe this doesn't matter?

    # Admin API has a create presentation request. This should probably be called here before the request.
    # However, I wouldn't know to do that based on the RFC. 

    # Construct the presentation proposal
    # presentation_proposal = {
    #     "connection_id": context.connection_id_dict[verifier][prover],
    #     "presentation_proposal": {
    #         "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/request-presentation",
    #         "comment": "This is a comment for the request for presentation.",
    #         "request_presentations~attach": {
    #             "@id": "libindy-request-presentation-0",
    #             "mime-type": "application/json",
    #             "data":  {
    #                 "requested_values": "Province",
    #                 "requested_predicates": {
    #                     "AgeOver19": {
    #                         "name": "age",
    #                         "p_type": ">=",
    #                         "p_value": 19
    #                     }
    #                 }
    #             }
    #         }
    #     }
    # }

    # presentation_proposal = {
    #     "connection_id": context.connection_id_dict[verifier][prover],
    #     "presentation_proposal": {
    #         "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/request-presentation",
    #         "comment": "This is a comment for the request for presentation.",
    #         "request_presentations~attach": {
    #             "@id": "libindy-request-presentation-0",
    #             "mime-type": "application/json",
    #             "data":  {
    #                 "requested_values": [
    #                     {
    #                         "attr_1",
    #                         "attr_2"
    #                     } 
    #                 ]
    #             }
    #         }
    #     }
    # }

    # presentation_proposal = {
    #     "connection_id": context.connection_id_dict[verifier][prover],
    #     "presentation_proposal": {
    #         "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/request-presentation",
    #         "comment": "This is a comment for the request for presentation.",
    #         "request_presentations~attach": {
    #             "@id": "libindy-request-presentation-0",
    #             "mime-type": "application/json",
    #             "data":  {
    #                 "requested_values": {
    #                     "attr_1": {
    #                         "name": "attr_1"
    #                     },
    #                     "restrictions": [
    #                         {
    #                             "schema_name": "test_schema.",
    #                             "schema_version": "1.0.0"
    #                         }
    #                     ]
    #                 }
    #             }
    #         }
    #     }
    # }

    presentation_proposal = {
        "connection_id": context.connection_id_dict[verifier][prover],
        "presentation_proposal": {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/request-presentation",
            "comment": "This is a comment for the request for presentation.",
            "request_presentations~attach": {
                "@id": "libindy-request-presentation-0",
                "mime-type": "application/json",
                "data":  {
                    "requested_values": {
                        "attr_1": {
                            "name": "attr_1",
                            "restrictions": [
                                {
                                    "schema_name": "test_schema.",
                                    "schema_version": "1.0.0"
                                }
                            ]
                        }
                    }
                }
            }
        }
    }

    # send presentation request
    (resp_status, resp_text) = agent_backchannel_POST(verifier_url + "/agent/command/", "proof", operation="send-request", data=presentation_proposal)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    resp_json = json.loads(resp_text)
    # check the state of the presentation from the verifiers perspective
    assert resp_json["state"] == "request_sent"

    # save off anything that is returned in the response to use later?
    context.presentation_thread_id = resp_json["thread_id"]
    context.verifier_presentation_exchange_id = resp_json["presentation_exchange_id"]
    context.presentation_request = resp_json["presentation_request"]

    # check the state of the presentation from the provers perspective through the webhook
    sleep(1)
    (resp_status, resp_text) = agent_backchannel_GET(context.prover_url + "/agent/response/", "proof", id=context.presentation_thread_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    resp_json = json.loads(resp_text)
    context.prover_presentation_exchange_id = resp_json["presentation_exchange_id"]
    assert resp_json["state"] == "request_received"

@when('"{prover}" makes the presentation of the proof')
def step_impl(context, prover):
    prover_url = context.prover_url


    # construct the presentation
    # presentation = {
    #     "connection_id": context.connection_id_dict[prover][context.verifier_name],
    #     "requested_predicates": {
    #         "AgeOver19": {
    #             "cred_id": context.credential_id
    #         }
    #     },
    #     "self_attested_attributes": {
    #         "whatever": "ohhhhh",
    #         "whatever2": "ahhhhh"
    #     },
    #     "requested_attributes": {
    #         "Province": {
    #             "revealed": True,
    #             "cred_id": context.credential_id
    #         }
    #     }
    # }

    presentation = {
        "comment": "This is a comment for the send presentation.",
        "connection_id": context.connection_id_dict[prover][context.verifier_name],
        "requested_attributes": {
            "attr_1": {
                "revealed": True,
                "cred_id": context.credential_id
            }
        }
    }

    (resp_status, resp_text) = agent_backchannel_POST(prover_url + "/agent/command/", "proof", operation="send-presentation", id=context.prover_presentation_exchange_id, data=presentation)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    resp_json = json.loads(resp_text)
    assert resp_json["state"] == "presentation_sent"

    # check the state of the presentation from the verifier's perspective through the webhook
    (resp_status, resp_text) = agent_backchannel_GET(context.verifier_url + "/agent/response/", "proof", id=context.presentation_thread_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    resp_json = json.loads(resp_text)
    assert resp_json["state"] == "presentation_received"

@when('"{verifier}" acknowledges the proof')
def step_impl(context, verifier):
    verifier_url = context.verifier_url

    (resp_status, resp_text) = agent_backchannel_POST(verifier_url + "/agent/command/", "proof", operation="verify-presentation", id=context.prover_presentation_exchange_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    resp_json = json.loads(resp_text)
    assert resp_json["state"] == "verified"

@then('"{prover}" has the proof acknowledged')
def step_impl(context, prover):
    prover_url = context.prover_url

    # check the state of the presentation from the prover's perspective through the webhook
    (resp_status, resp_text) = agent_backchannel_GET(context.prover_url + "/agent/response/", "proof", id=context.presentation_thread_id)
    assert resp_status == 200, f'resp_status {resp_status} is not 200; {resp_text}'
    resp_json = json.loads(resp_text)
    assert resp_json["state"] == "presentation_acked"
