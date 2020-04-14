Feature: Aries agent connection functions RFC 0160

   @T001-API10-RFC0160 @P1 @AcceptanceTest @NeedsReview
   Scenario Outline: establish a connection between two agents
      #Given we have two agents "Alice" and "Bob"
      Given we have "2" agents
         | name  | role    |
         | Alice | inviter |
         | Bob   | invitee |
      When "Alice" generates a connection invitation
      And "Bob" receives the connection invitation
      And "Bob" sends a connection request to "Alice"
      And "Alice" receives the connection request
      And "Alice" sends a connection response to "Bob"
      And "Bob" receives the connection response
      And "Bob" sends <message> to "Alice"
      Then "Alice" and "Bob" have a connection

      Examples:
         | message   |
         | acks      |
         | trustping |

   @T001.2-API10-RFC0160 @P1 @AcceptanceTest @NeedsReview
   Scenario Outline: establish a connection between two agents with role reversal
      #Given we have two agents "Alice" and "Bob"
      Given we have "2" agents
         | name  | role    |
         | Alice | invitee |
         | Bob   | inviter |
      When "Bob" generates a connection invitation
      And "Alice" receives the connection invitation
      And "Alice" sends a connection request to "Bob"
      And "Bob" receives the connection request
      And "Bob" sends a connection response to "Alice"
      And "Alice" receives the connection response
      And "Alice" sends <message> to "Bob"
      Then "Bob" and "Alice" have a connection

      Examples:
         | message   |
         | acks      |
         | trustping |


   @T002-API10-RFC0160 @P1 @AcceptanceTest @NeedsReview
   Scenario Outline: Connection established between two agents but inviter sends next message to establish full connection state
      Given we have "2" agents
         | name  | role    |
         | Alice | inviter |
         | Bob   | invitee |
      When "Alice" generates a connection invitation
      And "Bob" receives the connection invitation
      And "Bob" sends a connection request to "Alice"
      And "Alice" receives the connection request
      And "Alice" sends a connection response to "Bob"
      And "Bob" receives the connection response
      And "Alice" sends <message> to "Bob"
      Then "Alice" and "Bob" have a connection

      Examples:
         | message   |
         | acks      |
         | trustping |


   @T003-API10-RFC0160 @SingleUseInvite @P2 @ExceptionTest @NeedsReview @WillFail @OutstandingBug..418..https://github.com/hyperledger/aries-cloudagent-python/issues/418
   Scenario: Inviter Sends invitation for one agent second agent tries after connection
      Given we have "3" agents
         | name    | role              |
         | Alice   | inviter           |
         | Bob     | invitee           |
         | Mallory | inviteinterceptor |
      And "Alice" generated a single-use connection invitation
      And "Bob" received the connection invitation
      And "Bob" sent a connection request to "Alice"
      And "Alice" receives the connection request
      And "Alice" sends a connection response to "Bob"
      And "Bob" receives the connection response
      And "Alice" and "Bob" have a connection
      When "Mallory" sends a connection request to "Alice" based on the connection invitation
      Then "Alice" sends a request_not_accepted error

   @T004-API10-RFC0160 @SingleUseInvite @P2 @ExceptionTest @NeedsReview @WillFail @OutstandingBug..418..https://github.com/hyperledger/aries-cloudagent-python/issues/418
   Scenario: Inviter Sends invitation for one agent second agent tries during first share phase
      Given we have "3" agents
         | name    | role              |
         | Alice   | inviter           |
         | Bob     | invitee           |
         | Mallory | inviteinterceptor |
      And "Alice" generated a single-use connection invitation
      And "Bob" received the connection invitation
      And "Bob" sent a connection request to "Alice"
      When "Mallory" sends a connection request to "Alice" based on the connection invitation
      Then "Alice" sends a request_not_accepted error

   @T005-API10-RFC0160 @MultiUseInvite @P3 @DerivedFunctionalTest @NeedsReview @wip
   Scenario: Inviter Sends invitation for multiple agents
      Given we have "3" agents
         | name    | role              |
         | Alice   | inviter           |
         | Bob     | invitee           |
         | Mallory | inviteinterceptor |
      And "Alice" generated a multi-use connection invitation
      And "Bob" received the connection invitation
      And "Bob" sent a connection request
      And "Alice" sent a connection response to "Bob"
      When "Mallory" sends a connection request based on the connection invitation
      Then "Alice" sent a connection response to "Mallory"

   @T006-API10-RFC0160 @P4 @DerivedFunctionalTest @NeedsReview
   Scenario: Establish a connection between two agents who already have a connection initiated from invitee
      Given we have "2" agents
         | name  | role    |
         | Alice | inviter |
         | Bob   | invitee |
      And "Alice" and "Bob" have an existing connection
      When "Bob" generates a connection invitation
      And "Bob" and "Alice" complete the connection process
      Then "Alice" and "Bob" have another connection
