@RFC0434 @AIP20
Feature: RFC 0434 Intiating exchange using the Out of Band protocol
   In order to intiate the exchange with another agent,
   As a sender or a receiver,
   I want to use Out of Band(RFC0434) protocols to accomplish this.


   @T001-RFC0434 @RFC0036 @critical @AcceptanceTest
   Scenario: Something Something Something
      Given we have "2" agents
         | name | role   |
         | Acme | issuer |
         | Bob  | holder |
      Given "Acme" is ready to issue a "indy" credential
      When "Acme" creates a credential offer
      And "Acme" sends a connectionless out of band invitation to "Bob" with "credential-offer"
      And "Bob" receives the invitation
      And "Bob" requests the credential
      And "Acme" issues the credential
      And "Bob" acknowledges the credential issue
      Then "Bob" has the credential issued


   @T002-RFC0434 @RFC0453 @critical @AcceptanceTest @Schema_DriversLicense_v2
   Scenario Outline: Something Something Something v2
      Given we have "2" agents
         | name | role   |
         | Acme | issuer |
         | Bob  | holder |
      Given "Acme" is ready to issue a "indy" credential
      When "Acme" creates an "indy" credential offer with <credential_data>
      And "Acme" sends a connectionless out of band invitation to "Bob" with "credential-offer"
      And "Bob" receives the invitation
      And "Bob" requests the "indy" credential
      And "Acme" issues the "indy" credential
      And "Bob" acknowledges the "indy" credential issue
      Then "Bob" has the "indy" credential issued

      Examples:
         | credential_data   |
         | Data_DL_MaxValues |
