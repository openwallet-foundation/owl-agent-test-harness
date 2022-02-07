@RFC0025 @AIP10 @AIP20 @UsesCustomParameters
Feature: RFC 0025 DIDComm Transports
  In order to communicate with otehr agents,
  As an Agent
  I want to various transprot protocol.


  @T001-RFC0025
  Scenario Outline: Create connection between two agents with overlapping transports
    Given we have "2" agents
      | name | role      |
      | Acme | responder |
      | Bob  | requester |
    And "Acme" is running with parameters "{"inbound_transports": <acme-inbound-transports>, "outbound_transports": <acme-outbound-transports> }"
    And "Bob" is running with parameters "{"inbound_transports": <bob-inbound-transports>, "outbound_transports": <bob-outbound-transports> }"

    When "Acme" and "Bob" create a new connection

    Then the invitation serviceEndpoint should use the "<acme-inbound-transports>" protocol scheme

    @Transport_HTTP @RFC0023 @DIDExchangeConnection
    Examples: DIDExchange connection with both agents using HTTP for inbound and outbound transport
      | acme-inbound-transports | acme-outbound-transports | bob-inbound-transports | bob-outbound-transports |
      | ["http"]                | ["http"]                 | ["http"]               | ["http"]                |

    @Transport_HTTP @RFC0160
    Examples: 0160 connection with both agents using HTTP for inbound and outbound transport
      | acme-inbound-transports | acme-outbound-transports | bob-inbound-transports | bob-outbound-transports |
      | ["http"]                | ["http"]                 | ["http"]               | ["http"]                |

    @Transport_WS @RFC0023 @DIDExchangeConnection
    Examples: DIDExchange connection with both agents using WS for inbound and outbound transport
      | acme-inbound-transports | acme-outbound-transports | bob-inbound-transports | bob-outbound-transports |
      | ["ws"]                  | ["ws"]                   | ["ws"]                 | ["ws"]                  |

    @Transport_WS @RFC0160
    Examples: 0160 connection with both agents using WS for inbound and outbound transport
      | acme-inbound-transports | acme-outbound-transports | bob-inbound-transports | bob-outbound-transports |
      | ["ws"]                  | ["ws"]                   | ["ws"]                 | ["ws"]                  |

    @Transport_HTTP @Transport_WS @RFC0023 @DIDExchangeConnection
    Examples: DIDExchange connection with both agents using HTTP and WS for inbound and outbound transport
      | acme-inbound-transports | acme-outbound-transports | bob-inbound-transports | bob-outbound-transports |
      | ["http", "ws"]          | ["http", "ws"]           | ["http", "ws"]         | ["http", "ws"]          |
      | ["ws", "http"]          | ["ws", "http"]           | ["ws", "http"]         | ["ws", "http"]          |

    @Transport_HTTP @Transport_WS @RFC0160
    Examples: 0160 connection with both agents using HTTP and WS for inbound and outbound transport
      | acme-inbound-transports | acme-outbound-transports | bob-inbound-transports | bob-outbound-transports |
      | ["http", "ws"]          | ["http", "ws"]           | ["http", "ws"]         | ["http", "ws"]          |
      | ["ws", "http"]          | ["ws", "http"]           | ["ws", "http"]         | ["ws", "http"]          |

    @Transport_HTTP @Transport_WS @RFC0023 @DIDExchangeConnection
    Examples: DIDExchange connection with one agent using http for inbound and the other usign ws
      | acme-inbound-transports | acme-outbound-transports | bob-inbound-transports | bob-outbound-transports |
      | ["http"]                | ["ws"]                   | ["ws"]                 | ["http"]                |
      | ["ws"]                  | ["http"]                 | ["http"]               | ["ws"]                  |

    @Transport_HTTP @Transport_WS @RFC0160
    Examples: 0160 connection with one agent using http for inbound and the other usign ws
      | acme-inbound-transports | acme-outbound-transports | bob-inbound-transports | bob-outbound-transports |
      | ["http"]                | ["ws"]                   | ["ws"]                 | ["http"]                |
      | ["ws"]                  | ["http"]                 | ["http"]               | ["ws"]                  |

  @T002-RFC0025 @DIDExchangeConnection @RFC0023
  Scenario Outline: Fail creating a connection between two agents that have mismatching transports configured
    Given we have "2" agents
      | name | role      |
      | Acme | responder |
      | Bob  | requester |
    And "Acme" is running with parameters "{"inbound_transports": <acme-inbound-transports>, "outbound_transports": <acme-outbound-transports> }"
    And "Bob" is running with parameters "{"inbound_transports": <bob-inbound-transports>, "outbound_transports": <bob-outbound-transports> }"

    When "Acme" sends an explicit invitation to "Bob"
    And "Bob" receives the invitation
    When "Bob" sends the request to "Acme"
    Then "Acme" does not receive the request

    @Transport_HTTP @Transport_WS
    Examples:
      | acme-inbound-transports | acme-outbound-transports | bob-inbound-transports | bob-outbound-transports |
      | ["http"]                | ["http"]                 | ["ws"]                 | ["ws"]                  |
      | ["ws"]                  | ["ws"]                   | ["http"]               | ["http"]                |

    @Transport_HTTP @Transport_WS @RFC0160 @wip
    Examples:
      | acme-inbound-transports | acme-outbound-transports | bob-inbound-transports | bob-outbound-transports |
      | ["http"]                | ["http", "ws"]           | ["ws"]                 | ["http", "ws"]          |
      | ["ws"]                  | ["http", "ws"]           | ["http"]               | ["http", "ws"]          |