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
| [ACA-Py](acapy.md)| AIP 1, 2 | None | 95 / 96<br>98% | 4 / 31<br>12% | 65 / 79<br>82% | 30 / 36<br>83% | 0 / 2<br>0% | 34 / 34<br>100% | 36 / 38<br>94% | **258 / 304<br>84%** |
| [AF-Go](afgo.md)| AIP 2 | None | 4 / 31<br>12% | 27 / 45<br>60% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | **31 / 76<br>40%** |
| [AFJ](javascript.md)| AIP 1 | Revocation | 65 / 79<br>82% | 0 / 0<br>0% | 28 / 28<br>100% | 14 / 53<br>26% | 0 / 0<br>0% | 40 / 51<br>78% | 37 / 38<br>97% | **172 / 220<br>78%** |
| [AF-.NET](dotnet.md)| AIP 1 | Proof Proposal | 30 / 36<br>83% | 0 / 0<br>0% | 14 / 53<br>26% | 12 / 12<br>100% | 0 / 0<br>0% | 18 / 39<br>46% | 0 / 0<br>0% | **62 / 111<br>55%** |
| [Verity](verity.md)| AIP 1 | Credential Exchange | 0 / 2<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | **0 / 2<br>0%** |
| [Findy](findy.md)| AIP 1 | Revocation | 34 / 34<br>100% | 0 / 0<br>0% | 40 / 51<br>78% | 18 / 39<br>46% | 0 / 0<br>0% | 17 / 17<br>100% | 0 / 0<br>0% | **103 / 124<br>83%** |
| [VCX](aries-vcx.md)| AIP 1 | Proof Proposals, Public Dids, Revocations | 36 / 38<br>94% | 0 / 0<br>0% | 37 / 38<br>97% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 19 / 20<br>95% | **92 / 96<br>95%** |

- Where the row and column are the same Test Agent, the results include only the tests where the Test Agent plays ALL of the roles (ACME, Bob, Faber and Mallory)
- The results in the "All Tests" column include tests involving the "Test Agent" in ANY of the roles.
- Wondering what the results mean? Please read the brief [introduction to Aries interoperability](aries-interop-intro.md) for some background.
- Select the "Test Agent" links to drill down into the tests being run for each Test Agent.


*Results last updated: Tue Feb 28 03:44:21 UTC 2023*

