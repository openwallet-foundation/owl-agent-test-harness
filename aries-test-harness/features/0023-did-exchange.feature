Feature: Establishing DID Based Relationships RFC 0023

   @T001-RFC0023 @P1 @critical @AcceptanceTest @RFC0023 @wip
   Scenario: Establish a DID based connection between two agents with an explicit invitation
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      When "Bob" sends an explicit invitation
      And "Acme" receives the invitation
      And "Acme" sends the request to "Bob"
      And "Bob" receives the request
      And "Bob" sends a response to "Acme"
      And "Acme" receives the response
      And "Acme" sends complete to "Bob"
      Then "Acme" and "Bob" have a DID based connection

