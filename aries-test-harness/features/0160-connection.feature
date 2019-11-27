Feature: showing off behave

  Scenario: run a simple test
     Given we have behave installed
      When we implement a test
      Then behave will test it for us!

  Scenario: establish a connection between two agents
     Given we have two agents Alice and Bob
      When Alice generates a connection invitation
       And Bob accepts the connection invitation
      Then Alice and Bob have a connection

  Scenario: send a trust ping between two agents
     Given Alice and Bob have an existing connection
      When Alice sends a trust ping to Bob
      Then Bob receives a trust ping from Alice
