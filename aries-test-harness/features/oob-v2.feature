@DIDComm-V2 @OobV2 @UsesCustomParameters
Feature: DIDComm V2 Establishing Connections

   @T001-OobV2
   Scenario: Establish a connection between two agents using DIDComm V2
      Given we have "2" agents
         | name | role     |
         | Acme | inviter  |
         | Bob  | invitee  |

      And "Acme" is running with parameters "{"mime-type":["didcomm/v2"]}"
      And "Bob" is running with parameters "{"mime-type":["didcomm/v2"]}"

      When "Acme" creates a didcomm v2 invitation
      And "Bob" accepts the didcomm v2 invitation from "Acme"

      # Bob must send a message to acme
      And "Bob" requests mediation from "Acme"
      And "Acme" has received a didcomm v2 message from "Bob" and created a connection

      Then "Acme" and "Bob" have a didcomm v2 connection
