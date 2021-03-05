# Aries Interoperability Testing Overview


This web site shows the current status of Aries Interoperability.

The latest interoperability test results are provided below. Each item is for a test runset, a combination
of Aries agents and frameworks running a subset of the overall tests in the repository. The subset of tests
run represent the set of tests expected to be supported by the combination of components being tested.

The following test agents are currently included in the runsets:

- [Aries Cloud Agent Python](https://github.com/hyperledger/aries-cloudagent-python)
- [Aries Framework .NET](https://github.com/hyperledger/aries-framework-dotnet)
- [Aries Framework - JavaScript](https://github.com/hyperledger/aries-framework-javascript)
- [Aries Framework Go](https://github.com/hyperledger/aries-framework-go)

Want to add your Aries component to this page? You need to add a runset to the
[Aries Agent Test Harness](https://github.com/hyperledger/aries-agent-test-harness).

## Summary

Results last updated: Thu Mar 4 18:05:45 PST 2021

|   #   | Runset Name     | Scope | Passed Tests |
| :---- | :-------------- | ----- | -----------: |
| 1 | [ACA-PY and AF-Go](./acapy-afgo.md) | AIP 2.0 RFC0023 Only | **0 / 5** (0%) |
| 2 | [ACA-PY and AF-.NET](./acapy-dotnet.md) | AIP 1.0 except proof proposals | **25 / 25** (100%) |
| 3 | [ACA-PY to ACA-Py All Tests](./acapy-full.md) | All tests | **41 / 81** (50%) |
| 4 | [ACA-PY and AF-JS](./acapy-javascript.md) | AIP 1.0 except revocation | **15 / 30** (50%) |
| 5 | [ACA-PY to ACA-Py Passing Tests](./acapy.md) | AIP 1.0, AIP 2.0 (RFC0023 Only) | **41 / 41** (100%) |
| 6 | [AF-Go to AF-Go Passing Tests](./afgo.md) | AP 2.0 RFC0023 Only | **3 / 5** (60%) |
| 7 | [AF-.NET to AF-.NET Passing Tests](./dotnet.md) | AIP 1.0 except revocation and proof proposals | **13 / 13** (100%) |
| 8 | [AF-JS to AF-.NET Passing Tests](./javascript-dotnet.md) | AIP 1.0 except revocation and proof proposals | **12 / 13** (92%) |
| 9 | [AF-JS to AF-JS Passing Tests](./javascript.md) | AIP 1.0 except revocation | **17 / 18** (94%) |

