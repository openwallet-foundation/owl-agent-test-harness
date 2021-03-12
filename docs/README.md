# Aries Interoperability Testing Overview


This web site shows the current status of Aries Interoperability.

The latest interoperability test results are provided below. Each item is for a test runset, a combination
of Aries agents and frameworks running a subset of the overall tests in the repository. The subset of tests
run represent the set of tests expected to be supported by the combination of components being tested.

The following test agents are currently included in the runsets:

- [Aries Cloud Agent Python](https://github.com/hyperledger/aries-cloudagent-python) (ACA-Py)
- [Aries Framework .NET](https://github.com/hyperledger/aries-framework-dotnet) (AF-.NET)
- [Aries Framework JavaScript](https://github.com/hyperledger/aries-framework-javascript) (AFJ)
- [Aries Framework Go](https://github.com/hyperledger/aries-framework-go) (AF-Go)

Want to add your Aries component to this page? You need to add a runset to the
[Aries Agent Test Harness](https://github.com/hyperledger/aries-agent-test-harness).

## Summary

|   #   | Runset Name [Details] | Scope | Exceptions | Results [Summary by RFC] |
| :---- | :-------------------- | ----- | ---------- | ------------------------ |
| 1 | [ACA-PY to AF-Go](./acapy-afgo.md) | pre-AIP 2.0 | None | [**0 / 5** (0%)](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-afgo/reports/latest/index.html?redirect=false#behaviors) |
| 2 | [ACA-PY to AFJ](./acapy-afj.md) | AIP 1.0 | Revocation | [**13 / 18** (72%)](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors) |
| 3 | [ACA-PY to AF-.NET](./acapy-dotnet.md) | AIP 1.0 | Proof Proposals | [**25 / 25** (100%)](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-dotnet/reports/latest/index.html?redirect=false#behaviors) |
| 4 | [ACA-PY to ACA-Py](./acapy.md) | AIP 1.0 | None | [**41 / 41** (100%)](https://allure.vonx.io/api/allure-docker-service/projects/acapy/reports/latest/index.html?redirect=false#behaviors) |
| 5 | [AF-Go to AF-Go](./afgo.md) | pre-AIP 2.0 | None | [**3 / 5** (60%)](https://allure.vonx.io/api/allure-docker-service/projects/afgo/reports/latest/index.html?redirect=false#behaviors) |
| 6 | [AFJ to AF-.NET](./afj-dotnet.md) | AIP 1.0 | Revocation and Proof Proposals | [**13 / 13** (100%)](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-dotnet/reports/latest/index.html?redirect=false#behaviors) |
| 7 | [AFJ to AFJ](./afj.md) | AIP 1.0 | Revocation | [**17 / 18** (94%)](https://allure.vonx.io/api/allure-docker-service/projects/javascript/reports/latest/index.html?redirect=false#behaviors) |
| 8 | [AF-.NET to AF-.NET](./dotnet.md) | AIP 1.0 | Revocation and Proof Proposals | [**13 / 13** (100%)](https://allure.vonx.io/api/allure-docker-service/projects/dotnet/reports/latest/index.html?redirect=false#behaviors) |

*Results last updated: Thu Mar 11 16:38:13 PST 2021*

