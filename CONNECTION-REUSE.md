# Taking Advantage of Connection Reuse in AATH<!-- omit in toc -->

The Issue Credential and Proof tests that use DID Exchange Connections will attempt to reuse an existing connection if one was established between the agents involved from a subsequent test. This not only tests native connection reuse functionality in the agents, but also saves execution time.

There are three conditions an agent and backchannel can be in when executing these Issue Cred and Proof tests that supports connection reuse.

1/ An agent supports public DIDs, and connection reuse.

-   A connection was made in a subsequent test that used a public DID for the connection.
    
-   In the followup test for either Issue Credential or Proof that has the  And requester and responder have an existing connection  Given (precondition clause) as part of the test, and the test is tagged with `@DIDExchangeConnection`, will attempt to reuse the subsequent connection.
    
-   A call to `out-of-band/send-invitation-message`  is made with  `"use_public_did": True`  in the payload.
    
-   The backchannel, if needed, can use this to create an invitation that contains the public_did. The invitation returned must contain the Public DID for the responder.
    
-   The test harness then calls `out-of-band/receive-invitation` with  `use_existing_connection: true` in the payload.
    
-   The backchannel can use this to trigger the agent to reuse an existing connection if one exists. The connection record is returned to the test harness containing with a state of  completed, the requesters connection_id, and the did (my_did) of the requester.
    
-   The test harness recognizes that we have a completed connection and calls `GET  active-connection`  on the responder with an id of the requester's DID.
    
-   `GET  active-connection`  in the backchannel should query the agent for an active connection that contains the requester's DID. Then return the active connection record that contains the connection_id for the responder.
    
-   The test harness at this point has all the info needed to continue the test scenario using that existing connection.
    

2/ An agent doesn't support public DIDs in connections officially, however has a key in the invite (can be a public DID) that can be used to query the existing connection.

-   A connection was made in a subsequent test.
    
-   In the followup test for either Issue Credential or Proof that has the  And requester and responder have an existing connection  Given (precondition clause) as part of the test, and the test is tagged with `@DIDExchangeConnection`, will attempt to reuse the subsequent connection.
    
-   A call to  out-of-band/send-invitation-message  is made with `"use_public_did": True` in the payload.
    
-   The backchannel, can ignore the  `use_public_did`  flag and remove it from the payload if it interferes with the creation of the invitation. An invitation is returned in the response.
    
-   A call is then made to `out-of-band/receive-invitation` with `use_existing_connection: true` in the payload.
    
-   The backchannel can use this as a trigger to search for an existing connection based on some key that is available in the invitation.
    
-   The connection record is returned to the test harness containing with a state of `completed`, the requesters connection_id, and the did (my_did) of the requester.
    
-   The test harness recognizes that we have a completed connection and calls `GET  active-connection`  on the responder with an id of the requester's DID.
    
-   `GET active-connection` in the backchannel should query the agent for an active connection that contains the requester's DID. Then return the active connection record that contains the connection_id for the responder.
    
-   The test harness at this point has all the info needed to continue the test scenario based on that existing connection.
    

3/ An agent doesn't support public DIDs in Connections, and cannot reuse a connection in AATH.

-   Tests for either Issue Credential or Proof that has the `And requester and responder have an existing connection` Given (precondition clause) as part of the test and the test is tagged with `@DIDExchangeConnection`, will attempt to reuse the subsequent connection.
    
-   A call to `out-of-band/send-invitation-message`  is made with  `"use_public_did": True`  in the payload.
    
-   The backchannel should ignore the  `use_public_did`  flag and remove it from the payload if it interferes with the creation of the invitation. An invitation is returned in the response.
    
-   A call is then made to `out-of-band/receive-invitation` with  `use_existing_connection: true` in the payload.
    
-   The backchannel should ignore this flag and remove it from the data if it interferes with the operation.
-   A connection record is returned to the test harness containing with a state that is not `completed`.
-   The test harness recognizes that we don't have a completed connection continues establishing the connection.
-   The Test Harness will establish a separate connection for every subsequent test scenario in this case.