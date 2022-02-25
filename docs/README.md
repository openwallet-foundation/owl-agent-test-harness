# Aries Interoperability Information


This web site shows the current status of Aries Interoperability between Aries frameworks and agents. While
not yet included in these results, we have a working prototype for testing Aries mobile wallets using the
same tests.

The latest interoperability test results are below. Each row is a test agent, its columns
the results of tests executed in combination with other test agents.
The last column ("All Tests") shows the results of all tests run for the given test agent in any role. The link on each test
agent name provides more details about results for all test combinations for that test agent. On
that page are links to a full history of the test runs and full details on every executed test. 

The following test agents are currently supported:

- [Aries Cloud Agent Python](https://github.com/hyperledger/aries-cloudagent-python) (ACA-Py)
- [Aries Framework Go](https://github.com/hyperledger/aries-framework-go) (AF-Go)
- [Aries Framework JavaScript](https://github.com/hyperledger/aries-framework-javascript) (AFJ)
- [Aries Framework .NET](https://github.com/hyperledger/aries-framework-dotnet) (AF-.NET)
- [Evernym Verity](https://github.com/evernym/verity) (Verity)
- [Findy Agent](https://github.com/findy-network/findy-agent) (Findy)
- [AriesVCX](https://github.com/hyperledger/aries-vcx) (VCX)

Want to add your Aries component to this page? You need to add a runset to the
[Aries Agent Test Harness](https://github.com/hyperledger/aries-agent-test-harness).

## Latest Interoperability Results

| Test Agent | Scope | Exceptions | ACA-Py | AF-Go | AFJ | AF-.NET | Verity | Findy | VCX | **All Tests** |
| ----- | ----- | ----- | :----: | :----: | :----: | :----: | :----: | :----: | :----: | :----: |
| [ACA-Py](acapy.md)| AIP 1, 2 | None | 52 / 52<br>100% | 20 / 20<br>100% | 56 / 56<br>100% | 23 / 51<br>45% | 0 / 2<br>0% | 34 / 34<br>100% | 63 / 64<br>98% | **236 / 267<br>88%** |
| [AF-Go](afgo.md)| AIP 2 | None | 20 / 20<br>100% | 25 / 25<br>100% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | **45 / 45<br>100%** |
| [AFJ](javascript.md)| AIP 1 | Revocation | 56 / 56<br>100% | 0 / 0<br>0% | 16 / 17<br>94% | 47 / 53<br>88% | 0 / 0<br>0% | 51 / 51<br>100% | 0 / 0<br>0% | **141 / 148<br>95%** |
| [AF-.NET](dotnet.md)| AIP 1 | Proof Proposal | 23 / 51<br>45% | 0 / 0<br>0% | 47 / 53<br>88% | 6 / 12<br>50% | 0 / 0<br>0% | 25 / 39<br>64% | 0 / 0<br>0% | **72 / 126<br>57%** |
| [Verity](verity.md)| AIP 1 | Credential Exchange | 0 / 2<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | **0 / 2<br>0%** |
| [Findy](findy.md)| AIP 1 | Revocation | 34 / 34<br>100% | 0 / 0<br>0% | 51 / 51<br>100% | 25 / 39<br>64% | 0 / 0<br>0% | 17 / 17<br>100% | 0 / 0<br>0% | **110 / 124<br>88%** |
| [VCX](aries-vcx.md)| AIP 1 | Proof Proposals, Public Dids, Revocations | 63 / 64<br>98% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 33 / 34<br>97% | **96 / 98<br>97%** |

- Where the row and column are the same Test Agent, the results include only the tests where the Test Agent plays ALL of the roles (ACME, Bob, Faber and Mallory)
- The results in the "All Tests" column include tests involving the "Test Agent" in ANY of the roles.
- Wondering what the results mean? Please read the brief [introduction to Aries interoperability](aries-interop-intro.md) for some background.
- Select the "Test Agent" links to drill down into the tests being run for each Test Agent.


*Results last updated: Fri Feb 25 03:52:17 UTC 2022*

