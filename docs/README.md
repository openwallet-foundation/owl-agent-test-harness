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

Want to add your Aries component to this page? You need to add a runset to the
[Aries Agent Test Harness](https://github.com/hyperledger/aries-agent-test-harness).

## Latest Interoperability Results

| Test Agent | Scope | Exceptions | ACA-Py | AF-Go | AFJ | AF-.NET | **All Tests** |
| ----- | ----- | ----- | :----: | :----: | :----: | :----: | :----: |
| [ACA-Py](acapy.md)| AIP 1, 2 | None | 49 / 49<br>100% | 4 / 6<br>66% | 30 / 36<br>83% | 36 / 51<br>70% | **109 / 130<br>83%** |
| [AF-Go](afgo.md)| AIP 2 | None | 4 / 6<br>66% | 6 / 6<br>100% | 0 / 0<br>0% | 0 / 0<br>0% | **10 / 12<br>83%** |
| [AFJ](javascript.md)| AIP 1 | Revocation | 30 / 36<br>83% | 0 / 0<br>0% | 17 / 17<br>100% | 27 / 36<br>75% | **64 / 77<br>83%** |
| [AF-.NET](dotnet.md)| AIP 1 | Proof Proposal | 36 / 51<br>70% | 0 / 0<br>0% | 27 / 36<br>75% | 12 / 12<br>100% | **65 / 87<br>74%** |

- Where the row and column are the same Test Agent, the results include only the tests where the Test Agent plays ALL of the roles (ACME, Bob, Faber and Mallory)
- The results in the "All Tests" column include tests involving the "Test Agent" in ANY of the roles.
- Wondering what the results mean? Please read the brief [introduction to Aries interoperability](aries-interop-intro.md) for some background.
- Select the "Test Agent" links to drill down into the tests being run for each Test Agent.


*Results last updated: Thu Jul 15 03:52:18 UTC 2021*

