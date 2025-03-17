@revocation @RFC0183 @AIP20
Feature: RFC 0183 Aries agent credential revocation and revocation notification, anoncreds-specific

   # note that the "indy" format should fail with an "anoncreds" wallet
   @T001.2-HIPE0011 @normal @AcceptanceTest @Schema_DriversLicense_v2_Revoc @MobileTest @RFC0441 @CredFormat_Anoncreds @Anoncreds
   Scenario Outline: Credential revoked by Issuer and Holder attempts to prove with a prover that doesn't care if it was revoked
      Given "2" agents
         | name  | role     |
         | Bob   | prover   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential with formats from <issuer> with <credential_data>
      When <issuer> revokes the credential
      And "Faber" sends a <request_for_proof> presentation to "Bob"
      And "Bob" makes the <presentation> of the proof
      And "Faber" acknowledges the proof
      Then "Bob" has the proof verified

      Examples:
         | issuer | credential_data   | request_for_proof              | presentation                  |
         | Acme   | Data_DL_MaxValues | proof_request_DL_revoc_address | presentation_DL_revoc_address |


