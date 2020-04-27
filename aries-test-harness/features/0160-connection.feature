Feature: Aries agent connection functions RFC 0160

   @T001-API10-RFC0160 @P1 @AcceptanceTest
   Scenario Outline: establish a connection between two agents
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
         | trustping |
         # | acks      | *Note* in RFC 0302: Aries Interop Profile, it states that Acknowledgements are part of AIP 1.0, however, agents under test have
                        # implemented trustping which is not part of the AIP 1.0. The acks is removed here in favor of trustping until the RFC is changed or
                        # the agents under test implement acks.

   @T001.2-API10-RFC0160 @P1 @AcceptanceTest
   Scenario Outline: establish a connection between two agents with role reversal
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
         | trustping |
         # | acks      | *Note* in RFC 0302: Aries Interop Profile, it states that Acknowledgements are part of AIP 1.0, however, agents under test have
                        # implemented trustping which is not part of the AIP 1.0. The acks is removed here in favor of trustping until the RFC is changed or
                        # the agents under test implement acks.


   @T002-API10-RFC0160 @P1 @AcceptanceTest
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
         | trustping |
         # | acks      | *Note* in RFC 0302: Aries Interop Profile, it states that Acknowledgements are part of AIP 1.0, however, agents under test have
                        # implemented trustping which is not part of the AIP 1.0. The acks is removed here in favor of trustping until the RFC is changed or
                        # the agents under test implement acks.


   @T003-API10-RFC0160 @SingleUseInvite @P2 @ExceptionTest @WillFail @OutstandingBug..418..https://github.com/hyperledger/aries-cloudagent-python/issues/418
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

   @T004-API10-RFC0160 @SingleUseInvite @P2 @ExceptionTest @WillFail @OutstandingBug..418..https://github.com/hyperledger/aries-cloudagent-python/issues/418
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
      And "Bob" receives the connection invitation
      And "Bob" sends a connection request to "Alice"
      And "Alice" receives the connection request
      And "Alice" sends a connection response to "Bob"
      When "Mallory" sends a connection request to "Alice" based on the connection invitation
      Then "Alice" sends a connection response to "Mallory"
   #And "Alice" and "Bob" are able to complete the connection
   #And "Alice" and "Mallory" are able to complete the connection

   @T006-API10-RFC0160 @P4 @DerivedFunctionalTest
   Scenario: Establish a connection between two agents who already have a connection initiated from invitee
      Given we have "2" agents
         | name  | role    |
         | Alice | inviter |
         | Bob   | invitee |
      And "Alice" and "Bob" have an existing connection
      When "Bob" generates a connection invitation
      And "Bob" and "Alice" complete the connection process
      Then "Alice" and "Bob" have another connection

   @T007-API10-RFC0160 @P2 @ExceptionTest @SingleTryOnException @NeedsReview @wip
   Scenario Outline: Establish a connection between two agents but gets a request not accepted report problem message
      Given we have "2" agents
         | name  | role    |
         | Alice | inviter |
         | Bob   | invitee |
      And "Bob" has <problem>
      When "Alice" generates a connection invitation
      And "Bob" receives the connection invitation
      And "Bob" sends a connection request to "Alice"
      Then "Alice" sends an request not accepted error
      And the state of "Alice" is reset to Null
      And the state of "Bob" is reset to Null

      Examples:
         | problem                    |
         | Invalid DID Method         |
         | unknown endpoint protocols |
