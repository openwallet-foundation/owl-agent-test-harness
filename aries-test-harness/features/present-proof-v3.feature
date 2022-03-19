@PresentProofV3 @DIDComm-V2 @UsesCustomParameters
Feature: Aries agent present proof v3

   @T001-PresentProofV3 @RFC0510 @WACI @CredFormat_JSON-LD @Schema_Citizenship_Context @CredProposalStart
   Scenario Outline: Present Proof of specific types and proof is acknowledged with a Citizenship credential type with a DID Exchange Connection
      Given "2" agents
         | name  | role     |
         | Faber | verifier |
         | Bob   | prover   |
      And "Acme" is running with parameters "{"mime-type":["didcomm/v2"]}"
      And "Bob" is running with parameters "{"mime-type":["didcomm/v2"]}"
      And "Faber" is running with parameters "{"mime-type":["didcomm/v2"]}"

      Given "Bob" has an issued credential with formats from Acme with <credential_data>

      When "Faber" creates a didcomm v2 invitation with goal code "streamlined-vp"
      And "Bob" accepts the didcomm v2 invitation from "Faber"
      And "Bob" sends a presentation proposal to "Faber"
      And "Faber" has received a didcomm v2 message from "Bob" and created a connection
      And "Faber" sends a <request_for_proof> presentation with formats to "Bob"
      And "Bob" makes the <presentation> of the proof with formats
      And "Faber" acknowledges the proof with formats

      Then "Bob" has the proof with formats verified

      @ProofType_Ed25519Signature2018 @DidMethod_key
      Examples:
         | issuer | credential_data  | request_for_proof                | presentation                    |
         | Acme   | Data_Citizenship | proof_request_citizenship_dif_pe | presentation_citizenship_dif_pe |

      @RFC0646 @ProofType_BbsBlsSignature2020 @DidMethod_key
      Examples:
         | issuer | credential_data  | request_for_proof                                 | presentation                    |
         | Acme   | Data_Citizenship | proof_request_citizenship_dif_pe_limit_disclosure | presentation_citizenship_dif_pe |
