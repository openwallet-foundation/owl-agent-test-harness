Feature: Aries agent present proof functions RFC 0037

   @T001-API10-RFC0037 @P1 @AcceptanceTest @wip @NeedsReview @Indy
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


   @T001.2-API10-RFC0037 @P1 @AcceptanceTest @wip @NeedsReview
   Scenario Outline: Present Proof of specific types and proof is acknowledged
      Given "2" agents
         | name  | role     |
         | Faber | verifier |
         | Bob   | prover   |
      And "Faber" and "Bob" have an existing connection
      And "Bob" has an issued credential from <issuer>
      When "Faber" sends a request for proof presentation to "Bob" for <proof> with <restrictions>
      And "Bob" makes the presentation of the proof
      And "Faber" acknowledges the proof
      Then "Bob" has the proof acknowledged

      # Fyi, some of these proof examples may end up in the negative/exception test case. leaving them here for now.
      # This proof list is free to grow as cases are discovered and raised.
      Examples:
         | issuer | proof       | restrictions |
         | Acme   | address2    | schema       |
         | Faber  | zip         | cred_def_id  |
         |        | city        | attribute    |
         |        | address1    |              |
         |        | state       |              |
         |        | empty       |              |
         |        | null        |              |
         |        | true        |              |
         |        | false       |              |
         |        | max i32     |              |
         |        | max i32 + 1 |              |
         |        | i0          |              |
         |        | min i32     |              |
         |        | min i32 - 1 |              |
         |        | float 0.0   |              |
         |        | str 0.0     |              |
         |        | chr 0       |              |
         |        | chr 1       |              |
         |        | chr 2       |              |

   @T002-API10-RFC0037 @P1 @AcceptanceTest @wip @NeedsReview
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

   @T003-API10-RFC0037 @P1 @AcceptanceTest @wip @NeedsReview
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
