@RFC0044 @AIP20 @UsesCustomParameters
Feature: RFC0044 didcomm mime types

   @T001-RFC0044
   Scenario Outline: Perform DID Exchange between two agents that have the same default envelope media profile
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      And "Acme" is running with parameters "{"mime-type":<shared-mime-type>}"
      And "Bob" is running with parameters "{"mime-type":<shared-mime-type>}"
      When "Bob" sends an explicit invitation
      And "Acme" receives the invitation
      And "Acme" sends the request to "Bob"
      And "Bob" receives the request
      And "Bob" sends a response to "Acme"
      And "Acme" receives the response
      And "Acme" sends complete to "Bob"
      Then "Acme" and "Bob" have a connection

      Examples:
         |      shared-mime-type     |
         | "didcomm/aip2;env=rfc19"  |
         | "didcomm/aip2;env=rfc587" |

   @T002-RFC0044
   Scenario Outline: Perform DID Exchange between two permissive agents that have different default envelope media profiles
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      And "Acme" is running with parameters "{"mime-type":[<acme-mime-type>,<bob-mime-type>]}"
      And "Bob" is running with parameters "{"mime-type":[<bob-mime-type>,<acme-mime-type>]}"
      When "Bob" sends an explicit invitation
      And "Acme" receives the invitation
      And "Acme" sends the request to "Bob"
      And "Bob" receives the request
      And "Bob" sends a response to "Acme"
      And "Acme" receives the response
      And "Acme" sends complete to "Bob"
      Then "Acme" and "Bob" have a connection

      Examples:
         |      acme-mime-type       |       bob-mime-type       |
         | "didcomm/aip2;env=rfc19"  | "didcomm/aip2;env=rfc587" |
         | "didcomm/aip2;env=rfc587" | "didcomm/aip2;env=rfc19"  |

   @T003-RFC0044 @ExceptionTest
   Scenario Outline: Fail DID Exchange between two agents with mismatching media profiles
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      And "Acme" is running with parameters "{"mime-type":<acme-mime-type>}"
      And "Bob" is running with parameters "{"mime-type":<bob-mime-type>}"
      When "Bob" sends an explicit invitation
      Then "Acme" can't accept the invitation

      Examples:
         |      acme-mime-type       |       bob-mime-type       |
         | "didcomm/aip2;env=rfc19"  | "didcomm/aip2;env=rfc587" |
         | "didcomm/aip2;env=rfc587" | "didcomm/aip2;env=rfc19"  |

   @T004-RFC0044
   Scenario Outline: Perform DID Exchange with OOB media type handshake, with one accept parameter
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      And "Acme" is running with parameters "{"mime-type":<acme-mime-type>}"
      And "Bob" is running with parameters "{"mime-type":<bob-mime-type>,"oob-accept":[<acme-mime-type>]}"
      When "Bob" sends an explicit invitation
      And "Acme" receives the invitation
      And "Acme" sends the request to "Bob"
      And "Bob" receives the request
      And "Bob" sends a response to "Acme"
      And "Acme" receives the response
      And "Acme" sends complete to "Bob"
      Then "Acme" and "Bob" have a connection

      Examples:
         |      acme-mime-type       |       bob-mime-type       |
         | "didcomm/aip2;env=rfc19"  | "didcomm/aip2;env=rfc587" |
         | "didcomm/aip2;env=rfc587" | "didcomm/aip2;env=rfc19"  |

   @T005-RFC0044
   Scenario Outline: Perform DID Exchange with OOB media type handshake, with two accept parameters
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      And "Acme" is running with parameters "{"mime-type":<acme-mime-type>}"
      And "Bob" is running with parameters "{"mime-type":<bob-mime-type>,"oob-accept":[<acme-mime-type>,<bob-mime-type>]}"
      When "Bob" sends an explicit invitation
      And "Acme" receives the invitation
      And "Acme" sends the request to "Bob"
      And "Bob" receives the request
      And "Bob" sends a response to "Acme"
      And "Acme" receives the response
      And "Acme" sends complete to "Bob"
      Then "Acme" and "Bob" have a connection

      Examples:
         |      acme-mime-type       |       bob-mime-type       |
         | "didcomm/aip2;env=rfc19"  | "didcomm/aip2;env=rfc587" |
         | "didcomm/aip2;env=rfc587" | "didcomm/aip2;env=rfc19"  |

   @T006-RFC0044 @ExceptionTest
   Scenario Outline: Fail DID Exchange between two agents with explicit oob accept parameter, with no matching profiles
      Given we have "2" agents
         | name | role      |
         | Acme | requester |
         | Bob  | responder |
      And "Acme" is running with parameters "{"mime-type":<acme-mime-type>}"
      And "Bob" is running with parameters "{"mime-type":<bob-mime-type>,"oob-accept":[<bob-mime-type>]}"
      When "Bob" sends an explicit invitation
      Then "Acme" can't accept the invitation

      Examples:
         |      acme-mime-type       |       bob-mime-type       |
         | "didcomm/aip2;env=rfc19"  | "didcomm/aip2;env=rfc587" |
         | "didcomm/aip2;env=rfc587" | "didcomm/aip2;env=rfc19"  |
