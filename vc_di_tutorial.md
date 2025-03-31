
# Tutorial - Adding Data Integrity (VC_DI) Support to OATH

## Background and Relevant Documents

VC_DI support within Aca-Py is detailed here: https://aca-py.org/latest/design/AnoncredsW3CCompatibility/.

For issuing, we use the RFC 0809 VC-DI Attachments (https://identity.foundation/aries-rfcs/latest/features/0809-w3c-data-integrity-credential-attachment/).

For presenting, we use the RFC 0510 DIF Presentation Exchange Attachments (https://identity.foundation/aries-rfcs/latest/aip2/0510-dif-pres-exch-attach/).


## Support within Aca-Py Demo and Integration Tests

You can run the Aca-Py demo (alice/faber) to see VC_DI credentials in action.

Run the following in two separate shells:

```bash
AGENT_PORT_OVERRIDE=8010 ./run_demo run faber --wallet-type askar-anoncreds --revocation --cred-type vc_di
```

```bash
./run_demo run alice --wallet-type askar-anoncreds
```

(If you tack on the `--events` parameter you can see the message formats that are being being exchanged.)

You can also access the agents' swagger pages at http://localhost:8011 and http://localhost:8031 (based on the above ports) and try out the endpoints yourself.  Check out the code within the alice/faber demo to see exactly what endpoints and payload formats are used.

Aca-Py has some VC_DI-enabled integration tests, you can try running:

```bash
AGENT_PORT_OVERRIDE=9010 ./run_bdd -t @cred_type_vc_di
```

## Introduction to the OATH Test Harness and Backchannels

If you're not familiar with the test harness approach and design please review the architecture and developer docs within this repo.  You should be able to build the docker images and run some tests before you attempt to make any changes to the code or tests.

You can view the swagger UI for the backchannels as follows.

First start the agents (without running the test scenarios):

```
./manage start -d acapy-main
```

Download and run a Swagger UI image:

```
docker pull swaggerapi/swagger-ui
docker run -p 8081:8080 -e SWAGGER_JSON=/mnt/openapi-spec.yml -v ${PWD}/docs/assets:/mnt swaggerapi/swagger-ui
```

Now open your browser with `http://localhost:8081` - you can pick which of the 4 agents you want to connect to.

You can shut down the agents (and other services) using `./manage stop`.

If you run the tests with the `-nohup` option then the test harness will leave all the docker containers running once the tests complete:

```bash
./manage run -d acapy-main -nohup -t ... etc ...
```

You can use this feature (in combination with the Swagger UI) to inspect the agent or backchannel state once the tests have completed (to help diagnose a failed test for example), and then shut everything down with `./manage stop`.


## OATH Test Case(s) to Update with VC_DI Support

We'll just use existing tests cases, but we'll add support for the VC_DI exchange format.

Let's add VC_DI to a couple of existing AnonCreds-format tests - there is a small subset that have been specifically tested with Aca-Py (and with a credo holder):

```bash
BACKCHANNEL_EXTRA_acapy_main="{\"wallet-type\":\"askar-anoncreds\"}" ./manage run -d acapy-main -t @AcceptanceTest -t @AIP10,@RFC0441,@RFC0211,@T001-RFC0453,@T001-RFC0454b -t ~@wip -t ~@DIDExchangeConnection -t ~@T004-RFC0211 -t ~@QualifiedDIDs -t ~@T001-RFC0183 -t @Anoncreds
```

(It's a big set of tags to run only 4 tests, but these are the filters used by the credo runsets.  You can also add `-b credo` to run with credo as the holder (note that these tests currently fail with credo).)

You should be able to run these tests and have them all pass (using Aca-Py for all agents).  This also tells us the exact tests we need to update.


### Updating the Gherkin Tests

Take a look through the underlying code for the tests which are executed in the above runset:

- The test features are identified in the test logs, for example:

```
@RFC0453 @AIP20
Feature: RFC 0453 Aries Agent Issue Credential v2 # features/0453-issue-credential-v2.feature:2

  @T001-RFC0453 @RFC0592 @critical @AcceptanceTest @Schema_DriversLicense_v2 @RFC0160 @Anoncreds
  Scenario Outline: Issue a Indy credential with the Holder beginning with a proposal -- @2.1   # features/0453-issue-credential-v2.feature:28
    Given "2" agents                                                                            # features/steps/0160-connection.py:22 0.001s
      | name | role   |
      | Acme | issuer |
      | Bob  | holder |
    Given "Acme" has a public did                                                               # features/steps/0036-issue-credential.py:57 0.021s
```

- the steps within the `.feature` file are implemented in Python code located in the `features/steps` directory (also indicated in the test logs), for example:

```
@given('"{issuer}" has a public did')
def step_impl(context, issuer):
    ...
```

- for our updates, we're leveraging existing steps and just adding VC_DI support
- note that the test scenarios can be configured via parameters or tags - for example `"<credential_type>"` vs `@CredFormat_Anoncreds` are both used (in different tests) to specify AnonCreds credential format:

```
    @RFC0160 @Anoncreds
    Examples:
      | credential_type | credential_data   |
      | anoncreds       | Data_DL_MaxValues |

vs:

      @CredFormat_Anoncreds @RFC0592 @Schema_DriversLicense_v2 @CredProposalStart @Anoncreds
      Examples:
         | issuer | credential_data   | request_for_proof               | presentation                   |
         | Acme   | Data_DL_MaxValues | proof_request_DL_address_v2     | presentation_DL_address_v2     |
```

- the test data (for creating schemas, credentials and presentations) is in the `features/data` directory
- there are direct references in the Python code (in both the test harness and backchannels) to the credential format.


### Code Support for AnonCreds Credential Format - Overview

If you've reviewed the backchannel documentation and/or taken a look at the swagger UI as described above, you will know that the backchannel endpoints of interest are:

`/agent/command/issue-credential-v2/...` and `/agent/command/proof-v2/...`

These translate to aca-py endpoints (for example look at `http://localhost:9022`):

`/issue-credential-2.0/...` and `/present-proof-2.0/...`

These are the same endpoints used for "AnonCreds" format credentials, and the magic is in the data payloads, so theoretically we shouldn't have to do any changes to the aca-py backchannel code.  

HOWEVER a quick search reveals that there is specific logic around `credential_format` checks for `"indy"`, `"anoncreds"` or `"json-ld"`.

(For the `"vc_di"` credential format, the credential issue process is like `"anoncreds"`, and the presentation is like `"json-ld"`.)

We also need to add a webhook handler for VC_DI format (`handle_issue_credential_v2_0_vc_di()`).

In `aries-test-harness/agent_test_utils.py` there are references to `AnonCreds`:

- in `amend_filters_with_runtime_data()` need to add an `if "vc_di" in filters:` block to handle all the `replace_me` parameters
- in `amend_filters_with_runtime_data()` the `if "json-ld" in filters:` block needs to handle any vc_di-specific parameters

And the following test harness code has references to `AnonCreds` and needs review:

```
./aries-test-harness/features/steps/0454-present-proof-v2-v3.py:30:        if context.current_cred_format == "indy" or context.current_cred_format == "anoncreds":
./aries-test-harness/features/steps/0454-present-proof-v2-v3.py:69:        context.current_cred_format = "anoncreds"
./aries-test-harness/features/steps/0454-present-proof-v2-v3.py:269:        if context.current_cred_format == "indy" or context.current_cred_format == "anoncreds":
./aries-test-harness/features/steps/0453-issue-credential-v2.py:13:CRED_FORMAT_ANONCREDS = "anoncreds"
./aries-test-harness/features/steps/0011-0183-revocation.py:41:        "anoncreds": cred_format == "anoncreds",
./aries-test-harness/features/steps/0011-0183-revocation.py:61:    if cred_format == "anoncreds":
./aries-test-harness/features/environment.py:454:        if context and "Anoncreds" in context.tags:
```

We'll look at the specific Python updates that are required as we update each test scenario.


### Test Scenario to Issue a VC_DI Credential

This is the existing test with AnonCreds support - `@T001-RFC0453` (features/0453-issue-credential-v2.feature:28):

```
  @T001-RFC0453 @RFC0592 @critical @AcceptanceTest @Schema_DriversLicense_v2
  Scenario Outline: Issue a Indy credential with the Holder beginning with a proposal
    Given "2" agents
      | name | role   |
      | Acme | issuer |
      | Bob  | holder |
    Given "Acme" has a public did
    And "Acme" is ready to issue a credential
    And "Acme" and "Bob" have an existing connection
    When "Bob" proposes a "<credential_type>" credential to "Acme" with <credential_data>
    And "Acme" offers the "<credential_type>" credential
    And "Bob" requests the "<credential_type>" credential
    And "Acme" issues the "<credential_type>" credential
    And "Bob" acknowledges the "<credential_type>" credential issue
    Then "Bob" has the "<credential_type>" credential issued

    @RFC0160 @Anoncreds
    Examples:
      | credential_type | credential_data   |
      | anoncreds       | Data_DL_MaxValues |
```

We can add another "example" to use the VC_DI format:

```
    @RFC0160 @Anoncreds @CredFormat_VC_DI
    Examples:
      | credential_type | credential_data   |
      | vc_di           | Data_DL_MaxValues |
```

Note the use of the `@Anoncreds` tag - this indicates that the agent wallet (Aca-Py specifically) must support AnonCreds.  This is a bit confusing, since we're now adding a new credential format (VC_DI) which is also going to get a new tag later on.  But for now just go with it ...

We also add a new tag here - `@CredFormat_VC_DI` - the test doesn't actually rely on this tag, but we can use it for filtering when we run the tests.

#### Test Data

The data files for the AnonCreds credential type (as indicated by the `@Schema_DriversLicense_v2` tag) are:

```
./features/data/anoncreds_schema_driverslicense_v2.json
./features/data/cred_data_anoncreds_schema_driverslicense_v2.json
```

There are different schema formats for `Indy` and `AnonCreds` credential formats.  VC_DI will use the same format as `AnonCreds` so we can just re-use those same data files.

There are "AnonCreds" versions of the `cred_data_*.json` files - the difference is that the "AnonCreds" version contains the "anoncreds" filter (and we will use this to add the "vc_di" filter as well), and the "non-AnonCreds" version contains filters for "indy" and "json-ld".  The file name has to correspond to the schema file name, hence the need for two `cred_def_*.json` files.

We will add a filter as follows - remember we can run the aca-py alice/faber demo with the `--events` flag to help figure this out.

For `cred_data_anoncreds_schema_driverslicense_v2.json` we just need to add a `"vc_di"` filter:

```
      "filters": {
         "anoncreds": {
            "cred_def_id": "replace_me"
         },
         "vc_di": {
            "cred_def_id": "replace_me"
         }
      }
```

Pretty straightforward!

#### Test Code

From the code overview above, we need to look at the following to support issuing VC_DI credentials.

In the Aca-Py backchannel:

- add the credential format to the mapping:

```
    self.credFormatFilterTranslationDict = {
        "indy": "indy",
        "json-ld": "ld_proof",
        "anoncreds": "anoncreds",
        "vc_di": "vc_di",
    }
```

- update the credential issue process to treat `"vc_di"` like `"anoncreds"`, for the most part we just need to do this:

```
    if cred_format == "indy" or cred_format == "anoncreds" or cred_format == "vc_di":
```

- add a webhook handler for VC_DI format (`handle_issue_credential_v2_0_vc_di()`)

```
    async def handle_issue_credential_v2_0_vc_di(self, message: Mapping[str, Any]):
        pass
```

(That's enough for now - we'll need to fill this in when we add revocation support.  See `handle_issue_credential_v2_0_anoncreds()` for example.)

(The backchannel has a lot of references to "anoncreds" in the context of checking if we need to be running on an `askar-anoncreds` wallet - we can just leave all this code alone, since `vc_di` behaves just like `anoncreds` in this context.)

In `aries-test-harness/agent_test_utils.py` there are references to `AnonCreds`:

- in `amend_filters_with_runtime_data()` need to add an `if "vc_di" in filters:` block to handle all the `replace_me` parameters

```
    if "vc_di" in filters:
        if (
            "schema_issuer_did" in filters["vc_di"]
            and filters["vc_di"]["schema_issuer_did"] == "replace_me"
        ):
            filters["vc_di"]["schema_issuer_did"] = context.issuer_did_dict[schema_name]
        if (
            "issuer_did" in filters["vc_di"]
            and filters["vc_di"]["issuer_did"] == "replace_me"
        ):
            filters["vc_di"]["issuer_did"] = context.issuer_did_dict[schema_name]
        if (
            "cred_def_id" in filters["vc_di"]
            and filters["vc_di"]["cred_def_id"] == "replace_me"
        ):
            filters["vc_di"]["cred_def_id"] = context.issuer_credential_definition_dict[schema_name]["id"]
        if (
            "schema_id" in filters["vc_di"]
            and filters["vc_di"]["schema_id"] == "replace_me"
        ):
            filters["vc_di"]["schema_id"] = context.issuer_schema_dict[schema_name]["id"]
```

And the following test harness code has references to `AnonCreds` and needs review:

```
./aries-test-harness/features/steps/0453-issue-credential-v2.py:13:CRED_FORMAT_ANONCREDS = "anoncreds"
./aries-test-harness/features/environment.py:454:        if context and "Anoncreds" in context.tags:
```

In `0453-issue-credential-v2.py` we need to add a parameter for the new credential format, and update the format checks:

```
CRED_FORMAT_VC_DI = "vc_di"

...

    if cred_format == CRED_FORMAT_INDY or cred_format == CRED_FORMAT_ANONCREDS or cred_format == CRED_FORMAT_VC_DI:
```

In `environment.py` the "anoncreds" references are all related to the wallet type, which will have the same behaviour for our new credential format.

#### Running the Tests

Re-build your docker images and run the tests:

```bash
docker rmi -f aries-test-harness acapy-main-agent-backchannel
./manage build -a acapy-main
BACKCHANNEL_EXTRA_acapy_main="{\"wallet-type\":\"askar-anoncreds\"}" ./manage run -d acapy-main -t  @CredFormat_VC_DI
```

Everything "should" pass :-)


### Test Scenario to Present a VC_DI Presentation

For this test we just need to add suport for VC_DI presentations (it used the same credential that we just implemented above).

`@T001-RFC0454b` (features/0454-present-proof-v2.feature:77)

```
   @T001-RFC0454b @critical @AcceptanceTest
   Scenario Outline: Present Proof of specific types and proof is acknowledged with a Drivers License credential type with a DID Exchange Connection
      Given "2" agents
         | name  | role     |
         | Faber | verifier |
         | Bob   | prover   |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential with formats from <issuer> with <credential_data>
      When "Faber" sends a <request_for_proof> presentation with formats to "Bob"
      And "Bob" makes the <presentation> of the proof with formats
      And "Faber" acknowledges the proof with formats
      Then "Bob" has the proof with formats verified

      @AIP20 @CredFormat_Anoncreds @RFC0592 @Schema_DriversLicense_v2 @Anoncreds
      Examples:
         | issuer | credential_data   | request_for_proof               | presentation                   |
         | Acme   | Data_DL_MaxValues | proof_request_DL_address_v2     | presentation_DL_address_v2     |
```

We can add (note there are 2 tags - `@CredFormat_VC_DI` and `@Anoncreds` - the latter indicates the wallet type, which must be `AnonCreds`):

```
      @AIP20 @RFC0592 @Schema_DriversLicense_v2 @Anoncreds @CredFormat_VC_DI
      Examples:
         | issuer | credential_data   | request_for_proof               | presentation                   |
         | Acme   | Data_DL_MaxValues | proof_request_DL_address_v2     | presentation_DL_address_v2     |
```

#### Test Data

The data files for the anoncreds cred type are:

```
./features/data/proof_request_DL_address_v2.json
./features/data/presentation_DL_address_v2.json
```

The proof request (and presentation) will be a bit more complicated - they need to be in "dif" format, so we need to translate what's happening with the "anoncreds" version.  The data for existing "dif" type presentation requests is in:

```
./features/data/proof_request_DL_address_v2_dif_pe.json
./features/data/presentation_DL_address_v2_dif_pe.json
```

Also we are lucky we can look at the aca-py alice/faber demo for some clues.

For the VC_DI presentation request, we will create `features/data/proof_request_DL_address_v2_vc_di.json`:

```
{
    "presentation_request":
    {
        "options":
        {
            "challenge": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
            "domain": "4jt78h47fh47"
        },
        "presentation_definition":
        {
            "id": "5591656f-5b5d-40f8-ab5c-9041c8e3a6a0",
            "name": "Address Verification",
            "purpose": "We need to verify your address",
            "format":
            {
                "di_vc":
                {
                    "proof_type":
                    [
                        "DataIntegrityProof"
                    ],
                    "cryptosuite":
                    [
                        "anoncreds-2023",
                        "eddsa-rdfc-2022"
                    ]
                }
            },
            "input_descriptors":
            [
                {
                    "id": "drivers_license_input_1",
                    "name": "American Drivers License",
                    "schema":
                    [
                        {
                            "uri": "https://www.w3.org/2018/credentials#VerifiableCredential"
                        }
                    ],
                    "constraints":
                    {
                        "statuses":
                        {
                            "active":
                            {
                                "directive": "disallowed"
                            }
                        },
                        "limit_disclosure": "required",
                        "fields":
                        [
                            {
                                "path":
                                [
                                    "$.issuer"
                                ],
                                "filter":
                                {
                                    "type": "string",
                                    "const": "replace_me"
                                }
                            },
                            {
                                "path":
                                [
                                    "$.credentialSubject.address"
                                ]
                            }
                        ]
                    }
                }
            ]
        }
    }
}
```

... and for the presentation - `features/data/presentation_DL_address_v2_vc_di.json`:

```
{
   "presentation": {
     "record_ids": {
       "drivers_license_input_1": ["Schema_DriversLicense_v2"]
     }
   }
}
```

#### Test Code

From the code overview above, we need to look at the following to support VC_DI presentations.

No changes required to the Aca-Py backchannel.

In `aries-test-harness/agent_test_utils.py`:

- in `amend_presentation_definition_with_runtime_data()` the `if "json-ld" in filters:` block needs to handle any vc_di-specific parameters:

```
    # note the format_type here is "di_vc"
    vc_di_vp_proof_type = format.get("di_vc")
    if vc_di_vp_proof_type:
        # Only vc_di with a single proof type replaced is supported ATM
        vc_di_vp_proof_type = format.get("vc_di", {}).get("proof_type", [])
        # TODO for JSON-LD credentials the proof type can be specified in a tag, for example "ProofType_Ed25519Signature2018"
        # (for now, for vc_di, we'll just take whatever is in the test data file)
        # However for VC_DI we need to insert the issuer DID as a credential filter
        schema_name = get_schema_name(context)
        for descriptor in pd["input_descriptors"]:
            constraint_fields = descriptor["constraints"]["fields"]
            for field in constraint_fields:
                if "$.issuer" in field["path"] and field["filter"]["const"] == "replace_me":
                    field["filter"]["const"] = context.issuer_did_dict[schema_name]
```

And in the test harness code (`features/steps/0454-present-proof-v2-v3.py`) "vc_di" presentations need to be handled like "json-ld":

```
    ...
    elif context.current_cred_format == "json-ld" or context.current_cred_format == "vc_di":
    ...
```

#### Running the Tests

Re-build your docker images and run the tests:

```bash
docker rmi -f aries-test-harness acapy-main-agent-backchannel
./manage build -a acapy-main
BACKCHANNEL_EXTRA_acapy_main="{\"wallet-type\":\"askar-anoncreds\"}" ./manage run -d acapy-main -t  @CredFormat_VC_DI
```

(This will run both of our new tests.)  Everything "should" pass :-)


### Test Scenario to Present a VC_DI Presentation with Revocation Support

*Note that this section is incomplete, it's an exercise for the student :-)*

This test just adds revocation to the above credential and presentation:

`@T001.2a-HIPE0011` (features/0183-revocation-anoncreds.feature:24)

```
   Background: create a schema and credential definition in order to issue a credential
      Given "Acme" has a public did
      And "Acme" is ready to issue a credential

   @T001.2a-HIPE0011 @normal @AcceptanceTest @Schema_DriversLicense_v2_Revoc @MobileTest @RFC0441
   Scenario Outline: Credential revoked by Issuer and Holder attempts to prove with a prover that doesn't care if it was revoked
      Given "2" agents
         | name  | role     |
         | Bob   | prover   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential with formats from <issuer> with <credential_data>
      When <issuer> revokes the credential
      When "Faber" sends a <request_for_proof> presentation with formats to "Bob"
      And "Bob" makes the <presentation> of the proof with formats
      And "Faber" acknowledges the proof with formats
      Then "Bob" has the proof with formats verified

      Examples:
         | issuer | credential_data   | request_for_proof                 | presentation                     |
         | Acme   | Data_DL_MaxValues | proof_request_DL_v2_revoc_address | presentation_DL_v2_revoc_address |
```

- and we add (and update) (note we have to move the anoncreds-specific tags to the anoncreds-specific example):

```
      Examples: @CredFormat_Anoncreds @Anoncreds
         | issuer | credential_data   | request_for_proof                 | presentation                     |
         | Acme   | Data_DL_MaxValues | proof_request_DL_v2_revoc_address | presentation_DL_v2_revoc_address |

      Examples: @CredFormat_VC_DI @VC_DI
         | issuer | credential_data   | request_for_proof                 | presentation                     |
         | Acme   | Data_DL_MaxValues | proof_request_DL_v2_revoc_address | presentation_DL_v2_revoc_address |
```

#### Test Data

The data file updates are similar to the above, but we use separate files for the revocation-supported version:

```
./features/data/anoncreds_schema_driverslicense_v2_revoc.json
./features/data/cred_data_anoncreds_schema_driverslicense_v2_revoc.json
./features/data/proof_request_DL_revoc_address.json
./features/data/presentation_DL_v2_revoc_address.json
```

File content TBD.

#### Test Code

From the code overview above, we need to look at the following to ensure revocation is supported in VC_DI presentations.

No changes required to the Aca-Py backchannel.

The following test harness code has references to `AnonCreds` and needs review:

```
./aries-test-harness/features/steps/0011-0183-revocation.py:41:        "anoncreds": cred_format == "anoncreds",
./aries-test-harness/features/steps/0011-0183-revocation.py:61:    if cred_format == "anoncreds":
```

Code changes TBD.


### Running the New Test Scenarios

TBD


### Add to Runsets of Existing Test Scenarios

Since these tests require the agents (or at least Aca-Py) to run with an AnonCreds wallet, the tests should be added to the existing AnonCreds scenarios:

```
.github/workflows/test-harness-acapy-anoncreds.yml
.github/workflows/test-harness-acapy-credo-anoncreds.yml
```

