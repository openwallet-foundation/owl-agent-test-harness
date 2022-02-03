@RFC0211 @AIP20
Feature: RFC 0211 Aries Agent Mediator Coordination
  In order to coordinate mediation with another agent,
  As a recipient,
  I want to use the Coordinate Mediation (RFC0211) protocol to accomplish this.

  @T001-RFC0211 @critical @AcceptanceTest @DIDExchangeConnection
  Scenario: Request mediation with the mediator accepting the mediation request
    Given we have "2" agents
      | name | role      |
      | Acme | mediator  |
      | Bob  | recipient |
    And "Acme" and "Bob" create a new didexchange connection
    When "Bob" requests mediation from "Acme"
    And "Acme" grants the mediation request from "Bob"
    Then "Bob" has "Acme" set up as a mediator

  @T002-RFC0211 @critical @AcceptanceTest @DIDExchangeConnection
  Scenario: Request mediation with the mediator accepting the mediation request and creating a connection using the mediator
    Given we have "2" agents
      | name  | role      |
      | Acme  | mediator  |
      | Bob   | recipient |
      | Faber | sender    |
    And "Acme" and "Bob" create a new didexchange connection
    When "Bob" requests mediation from "Acme"
    And "Acme" grants the mediation request from "Bob"
    Then "Bob" has "Acme" set up as a mediator
    When "Bob" and "Faber" create a new didexchange connection using "Acme" as a mediator

  @T003-RFC0211 @critical @AcceptanceTest @DIDExchangeConnection
  Scenario: Request mediation with the mediator denying the mediation request
    Given we have "2" agents
      | name | role      |
      | Acme | mediator  |
      | Bob  | recipient |
    And "Acme" and "Bob" create a new didexchange connection
    When "Bob" requests mediation from "Acme"
    And "Acme" denies the mediation request from "Bob"
    Then "Acme" has denied the mediation request from "Bob"