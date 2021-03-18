# Aries Interoperability Information


This web site shows the current status of Aries Interoperability amongst Aries frameworks and agents. while
not included in these results yet, we have a working prototype for testing Aries mobile wallets using the
identical tests.

The latest interoperability test results are provided below. Each item is for a test runset, a combination
of Aries agents and frameworks running a subset (see scope and exceptions) of the overall tests in the repository.
The subset of tests run represent the set of tests expected to be supported by the combination of components
being tested, with a narrative on the scope on the details page.

The following test agents are currently included in the runsets:

- [Aries Cloud Agent Python](https://github.com/hyperledger/aries-cloudagent-python) (ACA-Py)
- [Aries Framework Go](https://github.com/hyperledger/aries-framework-go) (AF-Go)
- [Aries Framework JavaScript](https://github.com/hyperledger/aries-framework-javascript) (AFJ)
- [Aries Framework .NET](https://github.com/hyperledger/aries-framework-dotnet) (AF-.NET)

Want to add your Aries component to this page? You need to add a runset to the
[Aries Agent Test Harness](https://github.com/hyperledger/aries-agent-test-harness).

## Aries Continuous Interoperability Results

| Test Agent | Scope | Exceptions | ACA-Py | AF-Go | AFJ | AF-.NET |
| ----- | ----- | ----- | :----: | :----: | :----: | :----: |
| [ACA-Py](acapy.md)| AIP 1, 2 | None | **80 / 90<br>88%** | 0 / 5<br>0% | 13 / 18<br>72% | 25 / 25<br>100% |
| [AF-Go](afgo.md)| AIP 2 | None | 0 / 5<br>0% | **3 / 10<br>30%** | 0 / 0<br>0% | 0 / 0<br>0% |
| [AFJ](javascript.md)| AIP 1 | Revocation | 13 / 18<br>72% | 0 / 0<br>0% | **44 / 49<br>89%** | 13 / 13<br>100% |
| [AF-.NET](dotnet.md)| AIP 1 | Proof Proposal | 25 / 25<br>100% | 0 / 0<br>0% | 13 / 13<br>100% | **51 / 51<br>100%** |

- The **bolded results** include all tests involving the "Test Agent" (first column), including tests using only that Test Agent.
- Wondering what the results mean? Please read the brief [introduction to Aries interoperability](aries-interop-intro.md) for some background.
- Click on the "Test Agent" links to drill into the tests being run for each.


*Results last updated: Thu Mar 18 12:47:23 PDT 2021*

