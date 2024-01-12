# https://github.com/hyperledger/aries-rfcs/tree/main/features/0793-unqualfied-dids-transition

@QualifiedDIDs @RFC0793 @UsesCustomParameters
Feature: Qualified DID - Unqualified DID Transition
   In order to more effectivley interoperate with other Aries Agents
   as an Aries Framework
   I want to support qualified did:peer DIDs


   @T001-RFC0793 @critical @AcceptanceTest
   Scenario Outline: Establish a connection with DID Exchange between two agents utilizing qualified did:peer DIDs
      Given we have "2" agents
         | name | role      | start_parameters   |
         | Acme | requester | <start_parameters> |
         | Bob  | responder | <start_parameters> |
      When "Bob" sends an invitation to "Acme" with <peer_did_method>
         | use_public_did |
         | True           |
      And "Acme" receives the invitation
      And "Acme" sends the request to "Bob"
      And "Bob" receives the request
      And "Bob" sends a response to "Acme"
      And "Acme" receives the response
      And "Acme" sends complete to "Bob"
      Then "Acme" and "Bob" have a connection

      Examples:
         | peer_did_method | start_parameters                                               |
         | unqualified     | use_running_agent                                              |
         | did:peer:1      | {"wallet-type":"askar-anoncreds", "flags":["emit-did-peer-1"]} |
         | did:peer:2      | {"wallet-type":"askar-anoncreds", "flags":["emit-did-peer-2"]} |
         | did:peer:3      | {"wallet-type":"askar-anoncreds", "flags":["emit-did-peer-3"]} |
         | did:peer:4      | {"wallet-type":"askar-anoncreds", "flags":["emit-did-peer-4"]} |
