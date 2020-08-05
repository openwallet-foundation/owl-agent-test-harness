# Managing Connection IDs in Tests<!-- omit in toc -->

## Storage

Many times in a single test scenario there may be 1-n connections to be aware of between the players involved in the scenario. Acme is connected to Bob, and different connection ids are used for both directions depending on which player is acting at the time; Acme to Bob, and Bob to Acme. The connections may extend to other participating players as well, Acme to Faber, Bob to Faber. With those relationships alone, the tests have to manage 6 connection ids. 

The connection tests uses a dictionary of dictionaries to store these relationships. When a new connection is made between two parties, the tests will create a dictionary keyed by the first player, that contains another dictionary keyed by the second player, that contains the connection id for the relationship. It will do the same thing for the other direction of the relationship as well, in order to get the connection id for that direction of the relationship. The dictionary for the Bob Acme relationship will look like this;
```
['Bob']['Acme']['30e86995-a2f7-442c-942c-96497aefad8d']
['Acme']['Bob']['9c0d9f2c-23c1-4384-b89e-950f97a7f173']
```
With all three players mentioned above, participating in one scenario, the dictionary will look like this once all connections have been established through the connection steps definitions;
```
['Bob']['Acme']['30e86995-a2f7-442c-942c-96497aefad8d']
['Bob']['Faber']['2c75d023-91dc-43b6-9103-b25af582fc6c']
['Acme']['Bob']['9c0d9f2c-23c1-4384-b89e-950f97a7f173']
['Acme']['Faber']['3514daa2-f9a1-492f-94f5-386b03fb8d31']
['Faber']['Bob']['f907c1e2-abe1-4c27-b9e2-e19f403cdfb5']
['Faber']['Acme']['b1faea96-84bd-4c3c-b4a9-3d99a6d51030']
```
If the connection step definitions are used in other non connection related tests, like issue credential or proof to establish the connection between two players, then these tests are taking advantage of this relationship storage mechanism. 

## Accessing
This connection id dictionary is actually stored in the `context` object in test harness, and because the `context` object is passed into ever step definition in the test scenario, it can be accessed from anywhere in the test scenario.  Retrieving the connection id for a relationship is done like this;
```
connection_id = context.connection_id_dict['player1']['player2']
```
Lets say you are writing a step def where Bob is going make a request to Acme, like `Bob proposes a credential to Acme`. The call may need Bob's connection id for the relationship to Acme.  Doing this would look like the following;
```
connection_id = context.connection_id_dict['Bob']['Acme']
```
Since player names are always passed into step definitions as variables representing their roles, ie. `holder proposes a credential to issuer`, the code will actually look like this. 
```
connection_id = context.connection_id_dict[holder][issuer]
```
Connection IDs are always needed at the beginning of a protocol, if not throughout other parts of the protocol as well. Having all ids necessary within the scenario easily accessible at any time, will make writing and maintaining agent tests simpler. 