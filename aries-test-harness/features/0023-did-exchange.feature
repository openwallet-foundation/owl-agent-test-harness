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

   @T003-RFC0023 @P1 @critical @AcceptanceTest @RFC0023
   Scenario: Establish a connection with DID Exchange between two agents with an implicit invitation
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      When "Bob" sends an implicit invitation
      And "Acme" receives the invitation
      And "Acme" sends the request to "Bob"
      And "Bob" receives the request
      And "Bob" sends a response to "Acme"
      And "Acme" receives the response
      And "Acme" sends complete to "Bob"
      Then "Acme" and "Bob" have a connection

   @T004-RFC0023 @P1 @critical @AcceptanceTest @RFC0023
   Scenario: Establish a connection with DID Exchange between two agents with an implicit invitation with role reversal
      Given we have "2" agents
         | name | role      |
         | Acme | responder |
         | Bob  | requester |
      When "Acme" sends an implicit invitation
      And "Bob" receives the invitation
      And "Bob" sends the request to "Acme"
      And "Acme" receives the request
      And "Acme" sends a response to "Bob"
      And "Bob" receives the response
      And "Bob" sends complete to "Acme"
      Then "Bob" and "Acme" have a connection

   @T005-RFC0023 @P3 @normal @AcceptanceTest @ExceptionTest @RFC0023 @wip
   Scenario Outline: Establish a connection with DID Exchange between two agents with an explicit invitation but invitation is rejected and connection process restarted
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      When "Bob" sends an implicit invitation
      And "Acme" receives the invitation
      And "Acme" rejects the invitation
      And "Acme" restarts the connection process
      Then a successful connection can be established between "Acme" and "Bob"

   @T006-RFC0023 @P3 @normal @AcceptanceTest @ExceptionTest @RFC0023 @wip
   Scenario Outline: Establish a connection with DID Exchange between two agents with an explicit invitation but invitation is rejected and connection process abandoned
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      When "Bob" sends an implicit invitation
      And "Acme" receives the invitation
      And "Acme" rejects the invitation
      And "Acme" abandons the connection process
      Then a connection can be established between "Acme" and "Bob" given that invitation

   @T007-RFC0023 @P3 @normal @AcceptanceTest @NegativeTest @ExceptionTest @RFC0023
   Scenario Outline: Establish a connection with DID Exchange between two agents with attempt to continue after protocol is completed
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
      And "Bob" sends a response to "Acme"
      Then "Acme" sends a problem_report to "Bob"
      And "Acme" and "Bob" still have a completed connection

   @T008-RFC0023 @P3 @normal @AcceptanceTest @ExceptionTest @NegativeTest @RFC0023 @wip
   Scenario: Establish a connection with DID Exchange and responder rejects the request
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      When "Bob" sends an explicit invitation
      And "Acme" receives the invitation
      And "Acme" sends the request to "Bob"
      And "Bob" receives the request
      And "Bob" rejects the request because of <reason>
      Then the connection is abandoned
      And "Acme" and "Bob" do not have a connection
      And establishing the connection cannot be continued

      Examples:
         | reason                                  |
         | Unsupported DID method for provided DID |
         | Expired Invitation                      |
         | DID Doc Invalid                         |
         | Unsupported key type                    |
         | Unsupported endpoint protocol           |
         | Missing reference to invitation         |
         | unknown processing error                |

   @T009-RFC0023 @P3 @normal @AcceptanceTest @ExceptionTest @NegativeTest @RFC0023 @wip
   Scenario: Establish a connection with DID Exchange and requester rejects the response
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
      And "Acme" rejects the response because of <reason>
      Then the connection is abandoned
      And "Acme" and "Bob" do not have a connection
      And establishing the connection cannot be continued

      Examples:
         | reason                                  |
         | Unsupported DID method for provided DID |
         | Expired request                         |
         | DID Doc Invalid                         |
         | Unsupported key type                    |
         | Unsupported endpoint protocol           |
         | Invalid signature                       |
         | unknown processing error                |