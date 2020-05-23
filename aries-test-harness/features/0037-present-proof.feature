Feature: Aries agent present proof functions RFC 0037 

   @T001-API10-RFC0037 @P1 @AcceptanceTest @NeedsReview @wip
   Scenario Outline: Present a proof to a verifier where the verifier has requested the proof
      Given we have "3" agents
         | name  | role     |
         | Bob   | Holder   | 
         | Faber | Issuer   |
         | Acme  | Verifier |
      And “Bob” has a credential issued from "Faber"
      And “Bob and Acme” have an existing connection
      And "Acme" sends a presentation request to "Bob" 
      And "Bob" sends a presentation response to "Acme"
      And "Acme" acknowledges the presentation response
      Then "Bob" has presented a proof to "Acme"