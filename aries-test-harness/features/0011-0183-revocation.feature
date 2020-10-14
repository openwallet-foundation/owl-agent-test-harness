Feature: Aries agent credential revocation and revocation notification RFC 0011 0183

   Background: create a schema and credential definition in order to issue a credential
      Given "Acme" has a public did
      And "Acme" is ready to issue a credential

   @T001-RFC0011 @P1 @AcceptanceTest @Schema_DriversLicense_Revoc @Indy
   Scenario Outline: Credential revoked by Issuer and Holder attempts to prove
      Given "2" agents
         | name  | role     |
         | Bob   | prover   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from <issuer> with <credential_data>
      When <issuer> revokes the credential
      And "Faber" sends a <request_for_proof> presentation to "Bob"
      And "Bob" makes the <presentation> of the proof
      And "Faber" acknowledges the proof
      Then "Bob" has the proof unacknowledged

      Examples:
         | issuer | credential_data   | request_for_proof              | presentation                  |
         | Acme   | Data_DL_MaxValues | proof_request_DL_revoc_address | presentation_DL_revoc_address |


   @T002-RFC0011 @P1 @AcceptanceTest @Schema_DriversLicense_Revoc @Indy
   Scenario Outline: Credential revoked and replaced with a new updated credential, holder proves claims with the updated credential
      Given "2" agents
         | name  | role     |
         | Bob   | prover   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from <issuer> with <credential_data>
      When <issuer> revokes the credential
      And <issuer> issues a new credential to "Bob" with <new_credential_data>
      And "Faber" sends a <request_for_proof> presentation to "Bob"
      And "Bob" makes the <presentation> of the proof
      And "Faber" acknowledges the proof
      Then "Bob" has the proof acknowledged

      Examples:
         | issuer | credential_data   | new_credential_data | request_for_proof              | presentation                  |
         | Acme   | Data_DL_MinValues | Data_DL_MaxValues   | proof_request_DL_revoc_address | presentation_DL_revoc_address |


   @T003-RFC0011 @P2 @AcceptanceTest @Schema_DriversLicense_Revoc @Indy
   Scenario Outline: Proof in process while Issuer revokes credential before presentation
      Given "2" agents
         | name  | role     |
         | Bob   | prover   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from <issuer> with <credential_data>
      When "Faber" sends a <request_for_proof> presentation to "Bob"
      And <issuer> revokes the credential
      And "Bob" makes the <presentation> of the proof
      And "Faber" acknowledges the proof
      Then "Bob" has the proof unacknowledged

      Examples:
         | issuer | credential_data   | request_for_proof              | presentation                  |
         | Acme   | Data_DL_MaxValues | proof_request_DL_revoc_address | presentation_DL_revoc_address |


   @T004-RFC0011 @P2 @ExceptionTest @Schema_DriversLicense_Revoc @wip @Indy
   Scenario Outline: Credential revoked and replaced with a new updated credential, holder proves claims with the updated credential but presents the revoked credential
      Given "2" agents
         | name  | role     |
         | Bob   | prover   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from <issuer> with <credential_data>
      When <issuer> revokes the credential
      And <issuer> issues a new credential to "Bob" with <new_credential_data>
      And "Faber" sends a <request_for_proof> presentation to "Bob"
      And "Bob" makes the <presentation> of the proof with the revoked credential
      Then "Bob" has the proof acknowledged

      Examples:
         | issuer | credential_data   | new_credential_data | request_for_proof              | presentation                  |
         | Acme   | Data_DL_MinValues | Data_DL_MaxValues   | proof_request_DL_revoc_address | presentation_DL_revoc_address |


   @T005-RFC0011 @P2 @AcceptanceTest @Schema_DriversLicense_Revoc @wip @NeedsReview
   Scenario Outline: Credential is revoked inside the timeframe
      Given "3" agents
         | name  | role     |
         | Acme  | issuer   |
         | Bob   | holder   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" had an issued credential from "Acme" with <credential_data>
      And "Acme" has revoked the credential within <timeframe>
      When "Faber" sends a <request_for_proof> presentation to "Bob" with credential validity during <timeframe>
      And "Bob" makes the <presentation> of the proof with the revoked credential
      And "Faber" acknowledges the proof
      Then "Bob" has the proof acknowledged

      Examples:
         | issuer | credential_data   | timeframe                      | request_for_proof        | presentation            |
         | Acme   | Data_DL_MinValues | calculated from execution time | proof_request_DL_address | presentation_DL_address |


   @T006-RFC0011 @P2 @AcceptanceTest @Schema_DriversLicense_Revoc @wip @NeedsReview
   Scenario Outline: Credential is revoked before the timeframe
      Given "3" agents
         | name  | role     |
         | Acme  | issuer   |
         | Bob   | holder   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" had an issued credential from "Acme" with <credential_data>
      And "Acme" has revoked the credential before <timeframe>
      When "Faber" sends a <request_for_proof> presentation to "Bob" with credential validity during <timeframe>
      And "Bob" makes the <presentation> of the proof with the revoked credential
      Then "Bob" has the proof unacknowledged

      Examples:
         | issuer | credential_data   | timeframe                      | request_for_proof        | presentation            |
         | Acme   | Data_DL_MinValues | calculated from execution time | proof_request_DL_address | presentation_DL_address |


   @T007-RFC0011 @P2 @AcceptanceTest @Schema_DriversLicense_Revoc @wip @NeedsReview
   Scenario Outline: Credential is revoked after the timeframe
      Given "3" agents
         | name  | role     |
         | Acme  | issuer   |
         | Bob   | holder   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" had an issued credential from "Acme" with <credential_data>
      And "Acme" has revoked the credential after <timeframe>
      When "Faber" sends a <request_for_proof> presentation to "Bob" with credential validity during <timeframe>
      And "Bob" makes the <presentation> of the proof with the revoked credential
      And "Faber" acknowledges the proof
      Then "Bob" has the proof acknowledged

      Examples:
         | issuer | credential_data   | timeframe                      | request_for_proof        | presentation            |
         | Acme   | Data_DL_MinValues | calculated from execution time | proof_request_DL_address | presentation_DL_address |


   @T008-RFC0011 @P2 @DerivedTest @Schema_DriversLicense_Revoc @wip @NeedsReview
   Scenario Outline: Credential is revoked during a timeframe with an open ended FROM or TO date
      Given "3" agents
         | name  | role     |
         | Acme  | issuer   |
         | Bob   | holder   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" had an issued credential from "Acme" with <credential_data>
      And "Acme" has revoked the credential within <timeframe>
      When "Faber" sends a <request_for_proof> presentation to "Bob" with credential validity during <timeframe>
      And "Bob" makes the <presentation> of the proof with the revoked credential
      And "Faber" acknowledges the proof
      Then "Bob" has the proof acknowledged

      Examples:
         | issuer | credential_data   | timeframe       | request_for_proof        | presentation            |
         | Acme   | Data_DL_MinValues | Open Ended TO   | proof_request_DL_address | presentation_DL_address |
         | Acme   | Data_DL_MinValues | Open Ended FROM | proof_request_DL_address | presentation_DL_address |


   @T009-RFC0011 @P3 @DerivedTest @NegativeTest @Schema_DriversLicense_Revoc @wip @NeedsReview
   Scenario Outline: Revoke attempt be done by the holder or a verifier
      Given "3" agents
         | name  | role     |
         | Acme  | issuer   |
         | Bob   | holder   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from "Acme" with <credential_data>
      When <role> revokes the credential
      Then <role> will get an error stating ...
      And "Bob" can make a proof with the credential

      Examples:
         | issuer | credential_data   | role     | request_for_proof        | presentation            |
         | Acme   | Data_DL_MaxValues | holder   | proof_request_DL_address | presentation_DL_address |
         | Acme   | Data_DL_MaxValues | verifier | proof_request_DL_address | presentation_DL_address |


   @T010-RFC0011 @P3 @DerivedTest @NegativeTest @Schema_DriversLicense @wip @NeedsReview
   Scenario Outline: Attempt to revoke an unrevokable credential.
      Given "3" agents
         | name  | role     |
         | Acme  | issuer   |
         | Bob   | holder   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from "Acme" with <credential_data>
      When "Acme" revokes the credential
      Then "Acme" receives an error stating …
      And "Bob" can make a proof with the credential

      Examples:
         | issuer | credential_data   | request_for_proof        | presentation            |
         | Acme   | Data_DL_MinValues | proof_request_DL_address | presentation_DL_address |


   @T011-RFC0011 @P2 @AcceptanceTest @Schema_DriversLicense_Revoc @wip @NeedsReview
   Scenario Outline: Issuer revokes multiple credentials in the same transaction
      Given "3" agents
         | name  | role     |
         | Acme  | issuer   |
         | Bob   | holder   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from "Acme" with <credential_data>
      And "Faber" has an issued credential from "Acme" with <credential_data_2>
      When "Acme" revokes "Bob’s" credential
      And "Acme" revokes "Faber’s" credential
      Then "Bob" cannot make a proof with the credential
      And "Faber" cannot make a proof with the credential

      Examples:
         | issuer | credential_data   | request_for_proof        | presentation            |
         | Acme   | Data_DL_MaxValues | proof_request_DL_address | presentation_DL_address |


   @T001-RFC0183 @P1 @AcceptanceTest @Schema_DriversLicense_Revoc @wip @NeedsReview
   Scenario Outline: Issuer revokes a credential and then sends notification
      Given "3" agents
         | name  | role     |
         | Acme  | issuer   |
         | Bob   | holder   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from "Acme" with <credential_data>
      When "Acme" revokes the credential
      And "Acme" sends a revocation notification
      Then "Bob" receives the revocation notification
      And "Bob" cannot make a proof with the credential

      Examples:
         | issuer | credential_data   | request_for_proof        | presentation            |
         | Acme   | Data_DL_MaxValues | proof_request_DL_address | presentation_DL_address |

   @T002-RFC0183 @P2 @AcceptanceTest @Schema_DriversLicense_Revoc @wip @NeedsReview
   Scenario Outline: Issuer revokes multiple credentials for multiple holders and sends notification
      Given "3" agents
         | name  | role     |
         | Acme  | issuer   |
         | Bob   | holder   |
         | Faber | verifier |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from "Acme" with <credential_data>
      And “Faber” has an issued credential from "Acme" with <credential_data_2>
      When "Acme" revokes "Bob’s" credential
      And "Acme" sends a revocation notification to "Bob"
      And "Acme" revokes "Faber’s" credential
      And "Acme" sends a revocation notification to "Faber"
      Then "Bob" receives the revocation notification
      And "Faber" receives the revocation notification
      And "Bob" cannot make a proof with the credential
      And "Faber" cannot make a proof with the credential

      Examples:
         | issuer | credential_data   | request_for_proof        | presentation            |
         | Acme   | Data_DL_MaxValues | proof_request_DL_address | presentation_DL_address |
