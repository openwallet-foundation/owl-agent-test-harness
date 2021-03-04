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

Results last updated: Wed Mar 3 17:24:00 PST 2021

|   #   | Runset Name     | Passed Tests |
| :---: | :-------------: | :-------------: |
| 1 | [ACA-PY Issuer/Verifier and Aries Framework Go Holder/Prover](#1-acapy-afgo) | **0 / 5** (0%) |
| 2 | [acapy-dotnet](#2-acapy-dotnet) | **25 / 25** (100%) |
| 3 | [acapy-full](#3-acapy-full) | **41 / 81** (50%) |
| 4 | [acapy-javascript](#4-acapy-javascript) | **15 / 30** (50%) |
| 5 | [acapy](#5-acapy) | **40 / 41** (97%) |
| 6 | [afgo](#6-afgo) | **3 / 5** (60%) |
| 7 | [dotnet](#7-dotnet) | **13 / 13** (100%) |
| 8 | [javascript-dotnet](#8-javascript-dotnet) | **13 / 13** (100%) |
| 9 | [javascript](#9-javascript) | **18 / 18** (100%) |

## 1 acapy-afgo

Name: **ACA-PY Issuer/Verifier and Aries Framework Go Holder/Prover**

No summary is available for this runset. Please add it to the file .github/workflows/test-harness-acapy-afgo.yml.

|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) |
| :------------: | :----------: | :-------------: | :--------------: |
| acapy-master | afgo-master | acapy-master | acapy-master |

**Latest results: 0 out of 5 (0%)**

Test Status Notes: No summary is available for this runset. Please add it to the file .github/workflows/test-harness-acapy-afgo.yml.

See the full test run results and history for the runset [acapy-b-afgo](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-afgo/reports/latest)

## 2 acapy-dotnet

Name: **acapy-dotnet**


 This test run uses the current main branch of ACA-Py for all of the agents except Bob (holder),
 which uses the master branch of Aries Framework .NET. It skips tests that are known not to work with
 the Aries Framework .NET as the holder, notably those that involve Proof Proposals and DID Exchange (RFC0023).
 


|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) |
| :------------: | :----------: | :-------------: | :--------------: |
| acapy-master | dotnet-master | acapy-master | acapy-master |

**Latest results: 25 out of 25 (100%)**

Test Status Notes: 

We currently have four tests failing that appear to be tests that use RFC0023 DID Exchange, which

is not supported.  This is an issue with tagging in the test suite, and is an expected failure. Issue #169

submitted to the Aries Agent Test Harness.




See the full test run results and history for the runset [acapy-b-dotnet](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-dotnet/reports/latest)

## 3 acapy-full

Name: **acapy-full**

No summary is available for this runset. Please add it to the file .github/workflows/test-harness-acapy-full.yml.

|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) |
| :------------: | :----------: | :-------------: | :--------------: |
| acapy-master | acapy-master | acapy-master | acapy-master |

**Latest results: 41 out of 81 (50%)**

Test Status Notes: No summary is available for this runset. Please add it to the file .github/workflows/test-harness-acapy-full.yml.

See the full test run results and history for the runset [acapy-full](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-full/reports/latest)

## 4 acapy-javascript

Name: **acapy-javascript**

No summary is available for this runset. Please add it to the file .github/workflows/test-harness-acapy-javascript.yml.

|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) |
| :------------: | :----------: | :-------------: | :--------------: |
| acapy-master | javascript | acapy-master | acapy-master |

**Latest results: 15 out of 30 (50%)**

Test Status Notes: No summary is available for this runset. Please add it to the file .github/workflows/test-harness-acapy-javascript.yml.

See the full test run results and history for the runset [acapy-b-javascript](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-javascript/reports/latest)

## 5 acapy

Name: **acapy**

No summary is available for this runset. Please add it to the file .github/workflows/test-harness-acapy.yml.

|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) |
| :------------: | :----------: | :-------------: | :--------------: |
| acapy-master | acapy-master | acapy-master | acapy-master |

**Latest results: 40 out of 41 (97%)**

Test Status Notes: No summary is available for this runset. Please add it to the file .github/workflows/test-harness-acapy.yml.

See the full test run results and history for the runset [acapy](https://allure.vonx.io/allure-docker-service-ui/projects/acapy/reports/latest)

## 6 afgo

Name: **afgo**

No summary is available for this runset. Please add it to the file .github/workflows/test-harness-afgo.yml.

|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) |
| :------------: | :----------: | :-------------: | :--------------: |
| afgo-master | afgo-master | afgo-master | afgo-master |

**Latest results: 3 out of 5 (60%)**

Test Status Notes: No summary is available for this runset. Please add it to the file .github/workflows/test-harness-afgo.yml.

See the full test run results and history for the runset [afgo](https://allure.vonx.io/allure-docker-service-ui/projects/afgo/reports/latest)

## 7 dotnet

Name: **dotnet**

No summary is available for this runset. Please add it to the file .github/workflows/test-harness-dotnet.yml.

|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) |
| :------------: | :----------: | :-------------: | :--------------: |
| dotnet-master | dotnet-master | dotnet-master | dotnet-master |

**Latest results: 13 out of 13 (100%)**

Test Status Notes: No summary is available for this runset. Please add it to the file .github/workflows/test-harness-dotnet.yml.

See the full test run results and history for the runset [dotnet](https://allure.vonx.io/allure-docker-service-ui/projects/dotnet/reports/latest)

## 8 javascript-dotnet

Name: **javascript-dotnet**

No summary is available for this runset. Please add it to the file .github/workflows/test-harness-javascript-dotnet.yml.

|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) |
| :------------: | :----------: | :-------------: | :--------------: |
| javascript | dotnet-master | javascript | javascript |

**Latest results: 13 out of 13 (100%)**

Test Status Notes: No summary is available for this runset. Please add it to the file .github/workflows/test-harness-javascript-dotnet.yml.

See the full test run results and history for the runset [javascript-b-dotnet](https://allure.vonx.io/allure-docker-service-ui/projects/javascript-b-dotnet/reports/latest)

## 9 javascript

Name: **javascript**

No summary is available for this runset. Please add it to the file .github/workflows/test-harness-javascript.yml.

|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) |
| :------------: | :----------: | :-------------: | :--------------: |
| javascript | javascript | javascript | javascript |

**Latest results: 18 out of 18 (100%)**

Test Status Notes: No summary is available for this runset. Please add it to the file .github/workflows/test-harness-javascript.yml.

See the full test run results and history for the runset [javascript](https://allure.vonx.io/allure-docker-service-ui/projects/javascript/reports/latest)


