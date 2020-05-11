Feature: Aries agent issue credential functions RFC 0036

  Background: create a schema and credential definition in order to issue a credential
    Given "Alice" has a public did
    When "Alice" creates a new schema
    And "Alice" creates a new credential definition
    Then "Alice" has an existing schema
    And "Alice" has an existing credential definition

  @T001-API10-RFC0036 @wip @AcceptanceTest @P1 @NeedsReview
  Scenario: Issue a credential with the Holder beginning with a proposal
    Given "2" agents
      | name  | role   |
      | Alice | issuer |
      | Bob   | holder |
    And "Alice" and "Bob" have an existing connection
    When "Bob" proposes a credential to "Alice"
    And "Alice" offers a credential
    And "Bob" requests the credential
    And "Alice" issues the credential
    And "Bob" acknowledges the credential issue
    Then "Bob" has the credential issued

  @T002-API10-RFC0036 @wip @AcceptanceTest @P2 @NeedsReview
    Scenario: Issue a credential with the Holder beginning with a proposal with negotiation
    Given "2" agents
      | name  | role   |
      | Alice | issuer |
      | Bob   | holder |
    And "Alice" and "Bob" have an existing connection
    And "Bob" proposes a credential
    And "Alice" offers a credential
    When "Bob" negotiates the offer with another proposal of the credential
    And "Alice" Offers the credential
    And "Bob" requests the credential
    And "Alice" issues the credential
    And "Bob" acknowledges the credential issue
    Then "Bob" has the credential issued
  
  @T003-API10-RFC0036 @wip @AcceptanceTest @P1 @NeedsReview
  Scenario: Issue a credential with the Issuer beginning with an offer
    Given "2" agents
      | name  | role   |
      | Alice | issuer |
      | Bob   | holder |
    And "Alice" and "Bob" have an existing connection
    When "Alice" offers a credential
    And "Bob" requests the credential
    And "Alice" issues the credential
    And "Bob" acknowledges the credential issue
    Then "Bob" has the credential issued

  @T004-API10-RFC0036 @wip @AcceptanceTest @P2 @NeedsReview
  Scenario: Issue a credential with the Issuer beginning with an offer with negotiation
    Given "2" agents
      | name  | role   |
      | Alice | issuer |
      | Bob   | holder |
    And "Alice" and "Bob" have an existing connection
    And "Alice" offers a credential
    When "Bob" negotiates the offer with a proposal of the credential
    And "Alice" Offers the credential
    And "Bob" requests the credential
    And "Alice" issues the credential
    And "Bob" acknowledges the credential issue
    Then "Bob" has the credential issued

  @T005-API10-RFC0036 @wip @AcceptanceTest @P3 @NeedsReview
  Scenario: Issue a credential with negotiation beginning from a credential request
    Given "2" agents
      | name  | role   |
      | Alice | issuer |
      | Bob   | holder |
    And "Alice" and "Bob" have an existing connection
    When "Bob" requests the credential
    And "Alice" offers credential
    When "Bob" negotiates the offer with a proposal of the credential
    And "Alice" offers credential
    And "Alice" issues the credential
    And "Bob" acknowledges the credential issue
    Then "Bob" has the credential issued

  @T006-API10-RFC0036 @wip @AcceptanceTest @P1 @NeedsReview
  Scenario: Issue a credential with the Holder beginning with a request and is accepted
    Given "2" agents
      | name  | role   |
      | Alice | issuer |
      | Bob   | holder |
    And "Alice" and "Bob" have an existing connection
    When "Bob" requests the credential
    And "Alice" issues the credential
    And "Bob" acknowledges the credential issue
    Then "Bob" has the credential issued




  @T001.1-API10-RFC0036 @orig
  # this test may be overtaken by the ones above, will remove when it is confirmed.
  Scenario: issue a credential from one agent to another with manual flow
     Given "Alice" and "Bob" have an existing connection
       And "Alice" has an existing schema and credential definition
      When "Alice" sends a credential offer
       And "Bob" sends a credential request
       And "Alice" issues a credential
       And "Bob" receives and acknowledges the credential
      Then "Alice" has an acknowledged credential issue
       And "Bob" has received a credential

  @T002.1-API10-RFC0036 @orig
  # desire to remove this as a formal test. The automated flow may be useful but not sure it should be expressed at this level.
  Scenario: issue a credential from one agent to another with automated flow
     Given "Alice" and "Bob" have an existing connection
       And "Alice" has an existing schema and credential definition
      When "Alice" initiates an automated credential issuance
       And "Bob" sends a credential request
       And "Bob" receives and acknowledges the credential
      Then "Bob" has received a credential
