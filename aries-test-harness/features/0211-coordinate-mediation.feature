@RFC0211 @AIP20 @DIDExchangeConnection
Feature: RFC 0211 Aries Agent Mediator Coordination
  In order to coordinate mediation with another agent,
  As a recipient,
  I want to use the Coordinate Mediation (RFC0211) protocol to accomplish this.

  @T001-RFC0211 @critical @AcceptanceTest
  Scenario: Request mediation with the mediator accepting the mediation request
    Given we have "2" agents
      | name | role      |
      | Acme | mediator  |
      | Bob  | recipient |
    And "Acme" and "Bob" create a new didexchange connection
    When "Bob" requests mediation from "Acme"
    And "Acme" grants the mediation request from "Bob"
    Then "Bob" has "Acme" set up as a mediator

  @T002-RFC0211 @critical @AcceptanceTest
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
    When "Bob" uses "Acme" as a mediator
    And "Bob" and "Faber" create a new didexchange connection

  @T003-RFC0211 @critical @AcceptanceTest
  Scenario: Request mediation with the mediator denying the mediation request
    Given we have "2" agents
      | name | role      |
      | Acme | mediator  |
      | Bob  | recipient |
    And "Acme" and "Bob" create a new didexchange connection
    When "Bob" requests mediation from "Acme"
    And "Acme" denies the mediation request from "Bob"
    Then "Acme" has denied the mediation request from "Bob"

  @T004-RFC0211 @UsesCustomParameters @RFC0025
  Scenario Outline: Two agents creating a DIDExchange connection using a mediator
    Given we have "2" agents
      | name  | role      |
      | Acme  | mediator  |
      | Bob   | recipient |
      | Faber | sender    |
    And "Acme" is running with parameters "{"inbound_transports": <acme-inbound-transports>, "outbound_transports": <acme-outbound-transports> }"
    And "Bob" is running with parameters "{"inbound_transports": <bob-inbound-transports>, "outbound_transports": <bob-outbound-transports> }"
    And "Faber" is running with parameters "{"inbound_transports": <faber-inbound-transports>, "outbound_transports": <faber-outbound-transports> }"

    # Create connection, request mediation
    When "Acme" and "Bob" create a new didexchange connection
    And "Bob" requests mediation from "Acme"
    And "Acme" grants the mediation request from "Bob"
    Then "Bob" has "Acme" set up as a mediator

    When "Acme" and "Faber" create a new didexchange connection
    And "Faber" requests mediation from "Acme"
    And "Acme" grants the mediation request from "Faber"
    Then "Faber" has "Acme" set up as a mediator

    # Create connection through the mediator
    When "Bob" uses "Acme" as a mediator
    And "Faber" uses "Acme" as a mediator
    And "Faber" and "Bob" create a new didexchange connection

    @Transport_Http @Transport_Ws @Transport_NoInbound @normal
    Examples: Creating a DIDExchange connection using a mediator without having inbound transports
      | acme-inbound-transports | acme-outbound-transports | bob-inbound-transports | bob-outbound-transports | faber-inbound-transports | faber-outbound-transports |
      | ["ws", "http"]          | ["ws", "http"]           | []                     | ["ws", "http"]          | []                       | ["ws", "http"]            |

    # Not all agents support being started without inbound transports.
    @Transport_Http @Transport_Ws @critical
    Examples: Creating a DIDExchange connection using a mediator with overlapping transports
      | acme-inbound-transports | acme-outbound-transports | bob-inbound-transports | bob-outbound-transports | faber-inbound-transports | faber-outbound-transports |
      | ["http", "ws"]          | ["http", "ws"]           | ["http", "ws"]         | ["http", "ws"]          | ["http", "ws"]           | ["http", "ws"]            |