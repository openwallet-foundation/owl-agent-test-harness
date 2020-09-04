# Aries Agent Test Harness: Test Coverage
The following test coverage is as of September 1, 2020. 

**AIP 1.0 Status:** 

 - Full Coverage of Positive Test Scenarios
 - Minimal Coverage of Exception and Negative Test Scenarios

**Terminology**
*Directly Tested*: There is a Test Scenario that has it as it's goal to test that protocol feature.
*Tested as Inclusion*: The Test Scenario's focus is not on this test case however it uses all or portions of other tests that use the protocol feature.
*Tested Indicrectly*: The Test Scenario is testing a Protocol that is using, as part of it's operations, another protocol. 

The  [Google Sheets Version of Coverage Matrix](https://docs.google.com/spreadsheets/d/175TOl6O_S6fOq403x0781N2YX5ZuPKXqKz5RR7Bunq0/edit?usp=sharing) is also made available for better viewing.

|   |  |  |  |  | **Tested Indirectly** | **Tested Indirectly** | **Tested Indirectly** | **Tested Indirectly** |
| :---: | :---: | :---: | :---: | :---: | :---: | --- | --- | --- |
|  **RFC** | **Feature Variation** | **Test Type(s)** | **Directly Tested** | **Tested as Inclusion** | [**RFC0056 Service Decorator**](https://github.com/hyperledger/aries-rfcs/tree/master/features/0056-service-decorator) | [**RFC0035 Report Problem**](https://github.com/hyperledger/aries-rfcs/tree/master/features/0035-report-problem) | [**RFC0025 DIDComm Transports**](https://github.com/hyperledger/aries-rfcs/tree/master/features/0025-didcomm-transports) | [**RFC0015 Acks**](https://github.com/hyperledger/aries-rfcs/tree/master/features/0015-acks) |
|  [RFC0160 - Connection Protocol](https://github.com/hyperledger/aries-rfcs/tree/master/features/0160-connection-protocol) | Establish Connection w/ Trust Ping | Functional | T001-AIP10-RFC0160 | T001-AIP10-RFC0036 |  |  | X |  |
|   |  |  |  | T002-AIP10-RFC0036 |  |  | X |  |
|   |  |  |  | T003-AIP10-RFC0036 |  |  | X |  |
|   |  |  |  | T004-AIP10-RFC0036 |  |  | X |  |
|   |  |  |  | T001-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T001.2-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T001.3-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T001.4-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T002-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T003-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T003.1-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T006-AIP10-RFC0037 |  |  | X |  |
|   | Establish Connection w/ Acks | Functional |  |  |  |  | X |  |
|   | Establish Connection Reversed Roles | Functional | T001.2-AIP10-RFC0160 |  |  |  | X |  |
|   | Establish Connection final acknowledgment comes from inviter | Functional | T002-AIP10-RFC0160 |  |  |  | X |  |
|   | Establish Connection Single Use Invite | Functional, Exception | T003-AIP10-RFC0160 |  |  |  | X |  |
|   |  |  | T004-AIP10-RFC0160 |  |  |  | X |  |
|   | Establish Connection Mult Use Invite | Functional | T005-AIP10-RFC0160 (wip) |  |  |  | X |  |
|   | Establish Multiple Connections Between the Same Agents | Functional | T006-AIP10-RFC0160 |  |  |  | X |  |
|   | Establish Connection Single Try on Exception | Funtional, Exception | T007-AIP10-RFC0160 (wip) |  |  | X | X |  |
|  [RFC0036 - Issue Credential](https://github.com/hyperledger/aries-rfcs/tree/master/features/0036-issue-credential) | Issue Credential Start w/ Proposal | Functional | T001-AIP10-RFC0036 | T001-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T001.2-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T001.3-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T001.4-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T002-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T003-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T003.1-AIP10-RFC0037 |  |  | X |  |
|   |  |  |  | T006-AIP10-RFC0037 |  |  | X |  |
|   | Issue Credential Negotiated w/ Proposal | Functional | T002-AIP10-RFC0036 |  |  |  | X |  |
|   | Issue Credential Start w/ Offer | Functional | T003-AIP10-RFC0036 |  |  |  | X |  |
|   | Issue Credential w/ Offer w/ Negotiation | Functional | T004-AIP10-RFC0036 |  |  |  | X |  |
|   | Issue Credential Start w/ Request w/ Negotiation | Functional | T005-AIP10-RFC0036 (wip) |  |  |  | X |  |
|   | Issue Credential Start w/ Request | Functional | T006-AIP10-RFC0036 (wip) |  |  |  | X |  |
|  [RFC0037 - Present Proof](https://github.com/hyperledger/aries-rfcs/tree/master/features/0036-issue-credential) | Present Proof w/o Proposal, Verifier is not the Issuer, 1 Cred Type | Functional | T001-AIP10-RFC0037 |  |  |  | X | X |
|   |  |  | T001.2-AIP10-RFC0037 |  |  |  | X | X |
|   |  |  | T001.3-AIP10-RFC0037 |  |  |  | X | X |
|   | Present Proof w/o Proposal, Verifier is the Issuer, 1 Cred Type | Functional | T001-AIP10-RFC0037 |  |  |  | X | X |
|   |  |  | T001.2-AIP10-RFC0037 |  |  |  | X | X |
|   |  |  | T001.3-AIP10-RFC0037 |  |  |  | X | X |
|   | Present Proof w/o Proposal, Verifier is the Issuer, Multi Cred Types | Functional | T001.4-AIP10-RFC0037 |  |  |  | X | X |
|   | Present Proof w/o Proposal, Verifier is not the Issuer, Multi Cred Types | Functional | T001.4-AIP10-RFC0037 |  |  |  | X | X |
|   | Present Proof Connectionless w/o Proposal | Functional | T002-AIP10-RFC0037 |  |  |  | X | X |
|   | Present Proof w/ Proposal as Response to a Request w/ Same Cred Type Different Attribute, Verifier is the Issuer | Functional | T003-AIP10-RFC0037 |  |  |  | X | X |
|   | Present Proof w/ Proposal as Response to a Request w/ Same Cred Type Different Attribute, Verifier is not the Issuer | Functional | T003-AIP10-RFC0037 |  |  |  | X | X |
|   | Present Proof w/ Proposal as Response to a Request w/ Different Cred Type, Verifier is the Issuer | Functional | T003.1-AIP10-RFC0037 |  |  |  | X | X |
|   | Present Proof w/ Proposal as Response to a Request w/ Different Cred Type, Verifier is not the Issuer | Functional | T003.1-AIP10-RFC0037 |  |  |  | X | X |
|   | Present Proof Connectionless w/ Proposal, Verifier is the Issuer | Functional | T004-AIP10-RFC0037 (wip) |  | X |  | X | X |
|   | Present Proof Connectionless w/ Proposal, Verifier is not the Issuer | Functional | T004-AIP10-RFC0037 (wip) |  | X |  | X | X |
|   | Present Proof w/o Proposal, Verifier Rejects Presentation | Functional, Exception | T005-AIP10-RFC0037 (wip) |  |  | X | X |  |
|   | Present Proof Start w/ Proposal | Functional | T006-AIP10-RFC0037 |  |  |  | X | X |