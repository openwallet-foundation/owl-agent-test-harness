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
