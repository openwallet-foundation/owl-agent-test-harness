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
| [ACA-Py](acapy.md)| AIP 1, 2 | None | 49 / 49<br>100% | 20 / 20<br>100% | 42 / 46<br>91% | 43 / 51<br>84% | 2 / 2<br>100% | 34 / 34<br>100% | 6 / 8<br>75% | **184 / 198<br>92%** |
| [AF-Go](afgo.md)| AIP 2 | None | 20 / 20<br>100% | 23 / 23<br>100% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | **43 / 43<br>100%** |
| [AFJ](javascript.md)| AIP 1 | Revocation | 42 / 46<br>91% | 0 / 0<br>0% | 17 / 17<br>100% | 53 / 53<br>100% | 0 / 0<br>0% | 36 / 51<br>70% | 0 / 0<br>0% | **119 / 138<br>86%** |
| [AF-.NET](dotnet.md)| AIP 1 | Proof Proposal | 43 / 51<br>84% | 0 / 0<br>0% | 53 / 53<br>100% | 12 / 12<br>100% | 0 / 0<br>0% | 31 / 46<br>67% | 0 / 0<br>0% | **110 / 133<br>82%** |
| [Verity](verity.md)| AIP 1 | Credential Exchange | 2 / 2<br>100% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | **2 / 2<br>100%** |
| [Findy](findy.md)| AIP 1 | Revocation | 34 / 34<br>100% | 0 / 0<br>0% | 36 / 51<br>70% | 31 / 46<br>67% | 0 / 0<br>0% | 17 / 17<br>100% | 0 / 0<br>0% | **101 / 131<br>77%** |
| [VCX](aries-vcx.md)| AIP 1 | Proof Proposals, Public Dids, Revocations | 6 / 8<br>75% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 0 / 0<br>0% | 4 / 4<br>100% | **10 / 12<br>83%** |

- Where the row and column are the same Test Agent, the results include only the tests where the Test Agent plays ALL of the roles (ACME, Bob, Faber and Mallory)
- The results in the "All Tests" column include tests involving the "Test Agent" in ANY of the roles.
- Wondering what the results mean? Please read the brief [introduction to Aries interoperability](aries-interop-intro.md) for some background.
- Select the "Test Agent" links to drill down into the tests being run for each Test Agent.


*Results last updated: Sun Oct 24 03:52:23 UTC 2021*

