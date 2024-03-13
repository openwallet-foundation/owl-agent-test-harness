# Aries Cloud Agent Python Interoperability

## Runsets with ACA-Py

| Runset | ACME<br>(Issuer) | Bob<br>(Holder) | Faber<br>(Verifier) | Mallory<br>(Holder) | Scope | Results | 
| ------ | :--------------: | :-------------: | :----------------: | :-----------------: | ----- | :-----: | 
| [acapy-afgo](#runset-acapy-afgo) | acapy-main<br>0.12.0rc2 | afgo-interop<br>unknown | acapy-main<br>0.12.0rc2 | acapy-main<br>0.12.0rc2 | pre-AIP 2.0 | [**0 / 14<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-afgo/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-afj](#runset-acapy-afj) | acapy-main<br>0.12.0rc2 | javascript<br>0.5.0-alpha.97 | acapy-main<br>0.12.0rc2 | acapy-main<br>0.12.0rc2 | AIP 1.0 | [**38 / 39<br>97%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-aip10](#runset-acapy-aip10) | acapy-main<br>0.12.0rc2 | acapy-main<br>0.12.0rc2 | acapy-main<br>0.12.0rc2 | acapy-main<br>0.12.0rc2 | AIP 1.0 | [**35 / 35<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-aip10/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-aip20](#runset-acapy-aip20) | acapy-main<br>0.12.0rc2 | acapy-main<br>0.12.0rc2 | acapy-main<br>0.12.0rc2 | acapy-main<br>0.12.0rc2 | AIP 2.0 | [**61 / 61<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-aip20/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-ariesvcx](#runset-acapy-ariesvcx) | acapy-main<br>0.12.0rc2 | aries-vcx<br>1.0.0 | acapy-main<br>0.12.0rc2 | acapy-main<br>0.12.0rc2 | AIP 1.0 | [**18 / 18<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-aries-vcx/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-dotnet-javascript](#runset-acapy-dotnet-javascript) | acapy-main<br>0.12.0rc2 | javascript<br>0.5.0-alpha.97 | dotnet<br> | acapy-main<br>0.12.0rc2 | AIP 1.0 | [**6 / 12<br>50%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript-f-dotnet/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-dotnet](#runset-acapy-dotnet) | acapy-main<br>0.12.0rc2 | dotnet<br> | acapy-main<br>0.12.0rc2 | acapy-main<br>0.12.0rc2 | AIP 1.0 | [**0 / 12<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-dotnet/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-findy](#runset-acapy-findy) | acapy-main<br>0.12.0rc2 | findy<br>0.31.56 | acapy-main<br>0.12.0rc2 | acapy-main<br>0.12.0rc2 | AIP 1.0 | [**17 / 17<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-findy/reports/latest/index.html?redirect=false#behaviors) |
| [afgo-acapy](#runset-afgo-acapy) | afgo-interop<br>unknown | acapy-main<br>0.12.0rc2 | afgo-interop<br>unknown | afgo-interop<br>unknown | pre-AIP 2.0 | [**0 / 17<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/afgo-b-acapy/reports/latest/index.html?redirect=false#behaviors) |
| [afj-acapy](#runset-afj-acapy) | javascript<br>0.5.0-alpha.97 | acapy-main<br>0.12.0rc2 | javascript<br>0.5.0-alpha.97 | javascript<br>0.5.0-alpha.97 | AIP 1.0 | [**11 / 28<br>39%**](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-acapy/reports/latest/index.html?redirect=false#behaviors) |
| [ariesvcx-acapy](#runset-ariesvcx-acapy) | aries-vcx<br>1.0.0 | acapy-main<br>0.12.0rc2 | aries-vcx<br>1.0.0 | aries-vcx<br>1.0.0 | AIP 1.0 | [**19 / 20<br>95%**](https://allure.vonx.io/api/allure-docker-service/projects/aries-vcx-b-acapy/reports/latest/index.html?redirect=false#behaviors) |
| [dotnet-acapy](#runset-dotnet-acapy) | dotnet<br> | acapy-main<br>0.12.0rc2 | dotnet<br> | dotnet<br> | AIP 1.0 | [**0 / 12<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/dotnet-b-acapy/reports/latest/index.html?redirect=false#behaviors) |
| [findy-acapy](#runset-findy-acapy) | findy<br>0.31.56 | acapy-main<br>0.12.0rc2 | findy<br>0.31.56 | findy<br>0.31.56 | AIP 1.0 | [**17 / 17<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-acapy/reports/latest/index.html?redirect=false#behaviors) |

## Runset Notes

### Runset **acapy-afgo**

Runset Name: ACA-PY to AF-Go

```tip
**Latest results: 0 out of 14 (0%)**


*Last run: Wed Mar 13 00:19:57 UTC 2024*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.09.27*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-afgo/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-afgo/reports/latest)


### Runset **acapy-afj**

Runset Name: ACA-PY to AFJ

```tip
**Latest results: 38 out of 39 (97%)**


*Last run: Wed Mar 13 00:43:04 UTC 2024*
```

#### Current Runset Status

Most of the tests are running. The tests not passing are being investigated.

*Status Note Updated: 2021.03.18*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-javascript/reports/latest)


### Runset **acapy-aip10**

Runset Name: ACA-PY to ACA-Py

```tip
**Latest results: 35 out of 35 (100%)**


*Last run: Wed Mar 13 00:33:32 UTC 2024*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.03.18*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/acapy-aip10/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-aip10/reports/latest)


### Runset **acapy-aip20**

Runset Name: ACA-PY to ACA-Py

```tip
**Latest results: 61 out of 61 (100%)**


*Last run: Wed Mar 13 00:43:36 UTC 2024*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.03.16*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/acapy-aip20/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-aip20/reports/latest)


### Runset **acapy-ariesvcx**

Runset Name: acapy to aries-vcx

```tip
**Latest results: 18 out of 18 (100%)**


*Last run: Wed Mar 13 00:52:43 UTC 2024*
```

#### Current Runset Status
```warning
No test status note is available for this runset. Please update: .github/workflows/test-harness-acapy-ariesvcx.yml.
```

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-aries-vcx/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-aries-vcx/reports/latest)


### Runset **acapy-dotnet-javascript**

Runset Name: ACA-PY to AF-.NET to AFJ

```tip
**Latest results: 6 out of 12 (50%)**


*Last run: Wed Mar 13 00:44:17 UTC 2024*
```

#### Current Runset Status

All tests are working, except for three tests that include Faber in the test run as an issuer.
These tests are; T001-RFC0037@1.2, T001.2-RFC0037@1.2, T001.4-RFC0037@1.1 . Further investigation 
is required to determine the issue in these three tests.

*Status Note Updated: 2021.03.18*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript-f-dotnet/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-javascript-f-dotnet/reports/latest)


### Runset **acapy-dotnet**

Runset Name: ACA-PY to AF-.NET

```tip
**Latest results: 0 out of 12 (0%)**


*Last run: Wed Mar 13 00:50:05 UTC 2024*
```

#### Current Runset Status

The majority of tests are running and passing. T013-HIPE0011 is failing due to the Aries Framework Dotnet not supporting
presentations containing a non-revocation interval, with a non-revocable credential. This issue is being tracked in 
https://github.com/hyperledger/aries-framework-dotnet/issues/184

*Status Note Updated: 2021.04.08*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-dotnet/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-dotnet/reports/latest)


### Runset **acapy-findy**

Runset Name: ACA-PY to findy

```tip
**Latest results: 17 out of 17 (100%)**


*Last run: Wed Mar 13 00:59:06 UTC 2024*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.09.14*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-findy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-findy/reports/latest)


### Runset **afgo-acapy**

Runset Name: AF-Go to ACA-PY

```tip
**Latest results: 0 out of 17 (0%)**


*Last run: Wed Mar 13 01:04:00 UTC 2024*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.09.27*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/afgo-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/afgo-b-acapy/reports/latest)


### Runset **afj-acapy**

Runset Name: AFJ to ACA-PY

```tip
**Latest results: 11 out of 28 (39%)**


*Last run: Wed Mar 13 01:11:35 UTC 2024*
```

#### Current Runset Status

All AIP10 tests are currently running.

*Status Note Updated: 2021.03.17*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/javascript-b-acapy/reports/latest)


### Runset **ariesvcx-acapy**

Runset Name: aries-vcx to acapy

```tip
**Latest results: 19 out of 20 (95%)**


*Last run: Wed Mar 13 01:51:03 UTC 2024*
```

#### Current Runset Status
```warning
No test status note is available for this runset. Please update: .github/workflows/test-harness-ariesvcx-acapy.yml.
```

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/aries-vcx-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/aries-vcx-b-acapy/reports/latest)


### Runset **dotnet-acapy**

Runset Name: AF-.NET to ACA-PY

```tip
**Latest results: 0 out of 12 (0%)**


*Last run: Wed Mar 13 01:35:22 UTC 2024*
```

#### Current Runset Status

More tests are failing than are passing when Aries Framework .NET is playing the issuer role. More investigation is needed.

*Status Note Updated: 2021.03.17*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/dotnet-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/dotnet-b-acapy/reports/latest)


### Runset **findy-acapy**

Runset Name: findy to ACA-PY

```tip
**Latest results: 17 out of 17 (100%)**


*Last run: Wed Mar 13 02:09:02 UTC 2024*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.09.14*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/findy-b-acapy/reports/latest)

Jump back to the [interoperability summary](./README.md).

