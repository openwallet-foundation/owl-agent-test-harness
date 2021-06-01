# Aries Interoperability Information


This web site shows the current status of Aries Interoperability between Aries frameworks and agents. While
not yet included in these results, we have a working prototype for testing Aries mobile wallets using the
same tests.

The latest interoperability test results are below. Each row is a test agent, its columns
the results of tests executed in combination with other test agents.
The bolded cell per row shows the results of all tests run for the given test agent. The link on each test
agent name provides more details about results for all test combinations for that test agent. On
that page are links to a full history of the test runs and full details on every executed test. 

The following test agents are currently supported:

- [Aries Cloud Agent Python](https://github.com/hyperledger/aries-cloudagent-python) (ACA-Py)
- [Aries Framework Go](https://github.com/hyperledger/aries-framework-go) (AF-Go)
- [Aries Framework JavaScript](https://github.com/hyperledger/aries-framework-javascript) (AFJ)
- [Aries Framework .NET](https://github.com/hyperledger/aries-framework-dotnet) (AF-.NET)

Want to add your Aries component to this page? You need to add a runset to the
[Aries Agent Test Harness](https://github.com/hyperledger/aries-agent-test-harness).

## Latest Interoperability Results

| Test Agent | Scope | Exceptions | ACA-Py | AF-Go | AFJ | AF-.NET |
| ----- | ----- | ----- | :----: | :----: | :----: | :----: |
| [ACA-Py](acapy.md)| AIP 1, 2 | None | **120 / 139<br>86%** | 5 / 10<br>50% | 35 / 39<br>89% | 44 / 54<br>81% |
| [AF-Go](afgo.md)| AIP 2 | None | 5 / 10<br>50% | **8 / 14<br>57%** | 0 / 0<br>0% | 0 / 0<br>0% |
| [AFJ](javascript.md)| AIP 1 | Revocation | 35 / 39<br>89% | 0 / 0<br>0% | **71 / 83<br>85%** | 29 / 39<br>74% |
| [AF-.NET](dotnet.md)| AIP 1 | Proof Proposal | 44 / 54<br>81% | 0 / 0<br>0% | 29 / 39<br>74% | **75 / 93<br>80%** |

- The **bolded results** show all tests involving the "Test Agent", including tests involving only that Test Agent.
- Wondering what the results mean? Please read the brief [introduction to Aries interoperability](aries-interop-intro.md) for some background.
- Select the "Test Agent" links to drill down into the tests being run.


*Results last updated: Tue Jun 1 05:56:38 UTC 2021*

