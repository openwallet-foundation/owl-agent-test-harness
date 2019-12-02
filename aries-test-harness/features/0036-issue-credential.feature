Feature: Aries agent issue credential functions RFC 0036

  Scenario: issue a credential from one agent to another
     Given "Alice" and "Bob" have an existing connection
      When "Alice" sends a credential offer
       And "Bob" sends a credential request
       And "Alice" issues a credential
       And "Bob" receives and acknowledges the credential
      Then "Alice" has an acknowledged credential issue
       And "Bob" has received a credential
