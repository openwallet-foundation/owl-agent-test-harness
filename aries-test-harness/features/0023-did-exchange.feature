Feature: Establishing Connections with DID Exchange RFC 0023

   @T001-RFC0023 @P1 @critical @AcceptanceTest @RFC0023
   Scenario: Establish a connection with DID Exchange between two agents with an explicit invitation
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
      Then "Acme" and "Bob" have a connection

   @T002-RFC0023 @P1 @critical @AcceptanceTest @RFC0023
   Scenario: Establish a connection with DID Exchange between two agents with an explicit invitation with role reversal
      Given we have "2" agents
         | name | role      |
         | Acme | responder |
         | Bob  | requester |
      When "Acme" sends an explicit invitation
      And "Bob" receives the invitation
      And "Bob" sends the request to "Acme"
      And "Acme" receives the request
      And "Acme" sends a response to "Bob"
      And "Bob" receives the response
      And "Bob" sends complete to "Acme"
      Then "Bob" and "Acme" have a connection

   @T003-RFC0023 @P1 @critical @AcceptanceTest @RFC0023 @wip
   Scenario: Establish a connection with DID Exchange between two agents with an implicit invitation
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      When "Bob" publishes a public DID
      When "Bob" sends an implicit invitation
      And "Acme" receives the invitation
      And "Acme" sends the request to "Bob"
      And "Bob" receives the request
      And "Bob" sends a response to "Acme"
      And "Acme" receives the response
      And "Acme" sends complete to "Bob"
      Then "Acme" and "Bob" have a connection