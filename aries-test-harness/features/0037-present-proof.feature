Feature: Aries agent present proof functions RFC 0037

   @T001-API10-RFC0037 @P1 @AcceptanceTest @Indy
   Scenario Outline: Present Proof where the prover does not propose a presentation of the proof and is acknowledged
      Given "2" agents
         | name  | role     |
         | Faber | verifier |
         | Bob   | prover   |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from <issuer>
      When "Faber" sends a request for proof presentation to "Bob"
      And "Bob" makes the presentation of the proof
      And "Faber" acknowledges the proof
      Then "Bob" has the proof acknowledged

      Examples:
         | issuer |
         | Acme   |
         | Faber  |


   @T001.2-API10-RFC0037 @P1 @AcceptanceTest @Schema_DriversLicense @Indy
   Scenario Outline: Present Proof of specific types and proof is acknowledged
      Given "2" agents
         | name  | role     |
         | Faber | verifier |
         | Bob   | prover   |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from <issuer> with <credential_data>
      When "Faber" sends a <request_for_proof> presentation to "Bob"
      And "Bob" makes the <presentation> of the proof
      And "Faber" acknowledges the proof
      Then "Bob" has the proof acknowledged

      Examples:
         | issuer | credential_data   | request_for_proof            | presentation                |
         | Acme   | Data_DL_MaxValues | proof_request_DL_address     | presentation_DL_address     |
         | Faber  | Data_DL_MinValues | proof_request_DL_age_over_19 | presentation_DL_age_over_19 |


   @T001.3-API10-RFC0037 @P1 @AcceptanceTest @Schema_Biological_Indicators @Indy
   Scenario Outline: Present Proof of specific types and proof is acknowledged
      Given "2" agents
         | name  | role     |
         | Faber | verifier |
         | Bob   | prover   |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from <issuer> with <credential_data>
      When "Faber" sends a <request for proof> presentation to "Bob"
      And "Bob" makes the <presentation> of the proof
      And "Faber" acknowledges the proof
      Then "Bob" has the proof acknowledged

      Examples:
         | issuer | credential_data          | request for proof                    | presentation                        |
         | Acme   | Data_BI_NormalizedValues | proof_request_biological_indicator_a | presentation_biological_indicator_a |

   @T001.4-API10-RFC0037 @P1 @AcceptanceTest @Schema_Biological_Indicators @Schema_Health_Consent @Indy
   Scenario Outline: Present Proof of specific types and proof is acknowledged
      Given "2" agents
         | name  | role     |
         | Faber | verifier |
         | Bob   | prover   |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from <issuer> with <credential_data>
      When "Faber" sends a <request for proof> presentation to "Bob"
      And "Bob" makes the <presentation> of the proof
      And "Faber" acknowledges the proof
      Then "Bob" has the proof acknowledged

      Examples:
         | issuer | credential_data      | request for proof            | presentation                |
         | Faber  | Data_BI_HealthValues | proof_request_health_consent | presentation_health_consent |

   @T002-API10-RFC0037 @P1 @AcceptanceTest @wip @NeedsReview @Indy
   Scenario Outline: Present Proof where the prover and verifier are connectionless, the prover does not propose a presentation of the proof, and is acknowledged
      Given "2" agents
         | name  | role     |
         | Faber | verifier |
         | Bob   | prover   |
      And "Faber" and "Bob" do not have a connection
      And "Bob" has an issued credential from <issuer>
      When "Faber" sends a request for proof presentation to "Bob"
      And "Bob" makes the presentation of the proof
      And "Faber" acknowledges the proof
      Then "Bob" has the proof acknowledged

      Examples:
         | issuer |
         | Acme   |

   @T003-API10-RFC0037 @P1 @AcceptanceTest @wip @NeedsReview @Indy
   Scenario Outline: Present Proof where the prover has proposed the presentation of proof and is acknowledged
      Given "2" agents
         | name  | role     |
         | Faber | verifier |
         | Bob   | prover   |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from <issuer>
      When "Faber" sends a request for proof presentation to "Bob"
      And "Bob" doesn’t want to reveal what was requested so makes a presentation proposal
      And "Faber" agrees to continue so sends a request for proof presentation
      And "Bob" makes the presentation of the proof
      And "Faber" acknowledges the proof
      Then "Bob" has the proof acknowledged

      Examples:
         | issuer |
         | Acme   |
         | Faber  |

   @T004-API10-RFC0037 @P1 @AcceptanceTest @wip @NeedsReview
   Scenario Outline: Present Proof where the verifier and prover are connectionless, prover has proposed the presentation of proof, and is acknowledged
      Given "2" agents
         | name  | role     |
         | Faber | verifier |
         | Bob   | prover   |
      And "Faber" and "Bob" does not have a connection
      And "Bob" has an issued credential from <issuer>
      When "Faber" sends a request for proof presentation to "Bob"
      And "Bob" doesn’t want to reveal what was requested so makes a presentation proposal
      And "Faber" agrees to continue so sends a request for proof presentation
      And "Bob" makes the presentation of the proof
      And "Faber" acknowledges the proof
      Then "Bob" has the proof acknowledged

      Examples:
         | issuer |
         | Acme   |
         | Faber  |

   @T005-API10-RFC0037 @AcceptanceTest @ExceptionTest @P2 @wip @NeedsReview
   Scenario Outline: Present Proof where the verifier rejects the presentation of the proof
      Given "2" agents
         | name  | role     |
         | Faber | verifier |
         | Bob   | prover   |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from <issuer>
      When "Faber" sends a request for proof presentation to "Bob"
      And "Bob" makes the presentation of the proof
      And "Faber" rejects the proof so sends a presentation rejection
      Then "Bob" has the proof unacknowledged

      Examples:
         | issuer |
         | Acme   |
         | Faber  |
