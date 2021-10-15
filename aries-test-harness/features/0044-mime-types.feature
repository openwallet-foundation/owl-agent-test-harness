@RFC0044 @AIP20
Feature: RFC0044 didcomm mime types

   @T001-RFC0044
   Scenario: Perform DID Exchange between two agents that have the same default envelope MIME type
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      And "Acme" is running with parameters "{"mime-type":"didcomm/aip2;env=rfc19"}"
      And "Bob" is running with parameters "{"mime-type":"didcomm/aip2;env=rfc19"}"
      When "Bob" sends an explicit invitation
      And "Acme" receives the invitation
      And "Acme" sends the request to "Bob"
      And "Bob" receives the request
      And "Bob" sends a response to "Acme"
      And "Acme" receives the response
      And "Acme" sends complete to "Bob"
      Then "Acme" and "Bob" have a connection

   @T002-RFC0044
   Scenario Outline: Perform DID Exchange between two permissive agents that have different default envelope MIME types
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      And "Acme" is running with parameters "{"mime-type":<acme-mime-type>}"
      And "Bob" is running with parameters "{"mime-type":<bob-mime-type>}"
      When "Bob" sends an explicit invitation
      And "Acme" receives the invitation
      And "Acme" sends the request to "Bob"
      And "Bob" receives the request
      And "Bob" sends a response to "Acme"
      And "Acme" receives the response
      And "Acme" sends complete to "Bob"
      Then "Acme" and "Bob" have a connection

      Examples:
         | acme-mime-type | bob-mime-type |
         | "didcomm/aip1" | "didcomm/v2"  |
         | "didcomm/v2"   | "didcomm/aip1"|
