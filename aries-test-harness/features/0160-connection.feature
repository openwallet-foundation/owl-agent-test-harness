@RFC0160 @AIP10
Feature: RFC 0160 Aries agent connection functions

   @T001-RFC0160 @critical @AcceptanceTest @MobileTest
   Scenario Outline: establish a connection between two agents
      Given we have "2" agents
         | name  | role    |
         | Acme  | inviter |
         | Bob   | invitee |
      When "Acme" generates a connection invitation
      And "Bob" receives the connection invitation
      And "Bob" sends a connection request to "Acme"
      And "Acme" receives the connection request
      And "Acme" sends a connection response to "Bob"
      And "Bob" receives the connection response
      And "Acme" sends <message> to "Bob"
      Then "Acme" and "Bob" have a connection

      Examples:
         | message   |
         | trustping |
         # | acks      | *Note* in RFC 0302: Aries Interop Profile, it states that Acknowledgements are part of AIP 1.0, however, agents under test have
                        # implemented trustping which is not part of the AIP 1.0. The acks is removed here in favor of trustping until the RFC is changed or
                        # the agents under test implement acks.

   #@T001.2-RFC0160 @critical @AcceptanceTest @Deprecated
   #Scenario Outline: establish a connection between two agents with role reversal

   @T002-RFC0160 @critical @AcceptanceTest
   Scenario Outline: Connection established between two agents but inviter sends next message to establish full connection state
      Given we have "2" agents
         | name  | role    |
         | Acme | inviter |
         | Bob   | invitee |
      When "Acme" generates a connection invitation
      And "Bob" receives the connection invitation
      And "Bob" sends a connection request to "Acme"
      And "Acme" receives the connection request
      And "Acme" sends a connection response to "Bob"
      And "Bob" receives the connection response
      And "Acme" sends <message> to "Bob"
      Then "Acme" and "Bob" have a connection

      Examples:
         | message   |
         | trustping |
         # | acks      | *Note* in RFC 0302: Aries Interop Profile, it states that Acknowledgements are part of AIP 1.0, however, agents under test have
                        # implemented trustping which is not part of the AIP 1.0. The acks is removed here in favor of trustping until the RFC is changed or
                        # the agents under test implement acks.

   @T003-RFC0160 @normal @SingleUseInvite @ExceptionTest @allure.issue:https://github.com/hyperledger/aries-cloudagent-python/issues/418
   Scenario: Inviter Sends invitation for one agent second agent tries after connection
      Given we have "3" agents
         | name    | role              |
         | Acme   | inviter           |
         | Bob     | invitee           |
         | Mallory | inviteinterceptor |
      And "Acme" generated a single-use connection invitation
      And "Bob" received the connection invitation
      And "Bob" sent a connection request to "Acme"
      And "Acme" receives the connection request
      And "Acme" sends a connection response to "Bob"
      And "Bob" receives the connection response
      And "Acme" and "Bob" have a connection
      When "Mallory" sends a connection request to "Acme" based on the connection invitation
      Then "Acme" sends a request_not_accepted error

   @T004-RFC0160 @normal @SingleUseInvite @ExceptionTest @allure.issue:https://github.com/hyperledger/aries-cloudagent-python/issues/418
   Scenario: Inviter Sends invitation for one agent second agent tries during first share phase
      Given we have "3" agents
         | name    | role              |
         | Acme   | inviter           |
         | Bob     | invitee           |
         | Mallory | inviteinterceptor |
      And "Acme" generated a single-use connection invitation
      And "Bob" received the connection invitation
      And "Bob" sent a connection request to "Acme"
      When "Mallory" sends a connection request to "Acme" based on the connection invitation
      Then "Acme" sends a request_not_accepted error

   @T005-RFC0160 @wip @minor @MultiUseInvite @DerivedFunctionalTest @NeedsReview
   Scenario: Inviter Sends invitation for multiple agents
      Given we have "3" agents
         | name    | role              |
         | Acme   | inviter           |
         | Bob     | invitee           |
         | Mallory | inviteinterceptor |
      And "Acme" generated a multi-use connection invitation
      And "Bob" receives the connection invitation
      And "Bob" sends a connection request to "Acme"
      And "Acme" receives the connection request
      And "Acme" sends a connection response to "Bob"
      When "Mallory" sends a connection request to "Acme" based on the connection invitation
      Then "Acme" sends a connection response to "Mallory"
   #And "Acme" and "Bob" are able to complete the connection
   #And "Acme" and "Mallory" are able to complete the connection

   @T006-RFC0160 @trivial @DerivedFunctionalTest
   Scenario: Establish a connection between two agents who already have a connection initiated from invitee
      Given we have "2" agents
         | name  | role    |
         | Acme | inviter |
         | Bob   | invitee |
      And "Acme" and "Bob" have an existing connection
      When "Bob" generates a connection invitation
      And "Bob" and "Acme" complete the connection process
      Then "Acme" and "Bob" have another connection

   @T007-RFC0160 @wip @normal @ExceptionTest @SingleTryOnException @NeedsReview
   Scenario Outline: Establish a connection between two agents but gets a request not accepted report problem message
      Given we have "2" agents
         | name  | role    |
         | Acme | inviter |
         | Bob   | invitee |
      And "Bob" has <problem>
      When "Acme" generates a connection invitation
      And "Bob" receives the connection invitation
      And "Bob" sends a connection request to "Acme"
      Then "Acme" sends an request not accepted error
      And the state of "Acme" is reset to Null
      And the state of "Bob" is reset to Null

      Examples:
         | problem                    |
         | Invalid DID Method         |
         | unknown endpoint protocols |
