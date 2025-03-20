@revocation @RFC0183 @AIP20
Feature: RFC 0183 Aries agent credential revocation and revocation notification, anoncreds-specific

   Background: create a schema and credential definition in order to issue a credential
      Given "Acme" has a public did
      And "Acme" is ready to issue a credential

   @T001.2a-HIPE0011 @normal @AcceptanceTest @Schema_DriversLicense_v2_Revoc @MobileTest @RFC0441 @CredFormat_Anoncreds @Anoncreds
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


