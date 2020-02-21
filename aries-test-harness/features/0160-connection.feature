Feature: Aries agent connection functions RFC 0160

   Scenario: establish a connection between two agents
      Given we have two agents "Alice" and "Bob"
      When "Alice" generates a connection invitation
      And "Bob" receives the connection invitation
      And "Bob" sends a connection response
      And "Alice" accepts the connection response
      And "Bob" sends a response ping
      And "Alice" receives the response ping
      Then "Alice" and "Bob" have a connection

   @P1 @AcceptanceTest @NeedsReview
   Scenario: establish a connection between two agents
      Given we have two agents "Alice" and "Bob"
      When "Alice" generates a connection invitation
      And "Bob" receives the connection invitation
      And "Bob" sends a connection request
      And "Alice" receives the connection request
      And "Alice" sends a connection response
      Then "Alice" and "Bob" have a connection

   Scenario: send a trust ping between two agents
      Given "Alice" and "Bob" have an existing connection
      When "Alice" sends a trust ping
      Then "Bob" receives the trust ping
