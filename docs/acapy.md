# Aries Cloud Agent Python Interoperability

## Runsets with ACA-Py

| Runset | ACME<br>(Issuer) | Bob<br>(Holder) | Faber<br>(Verfier) | Mallory<br>(Holder) | Scope | Results | 
| ------ | :--------------: | :-------------: | :----------------: | :-----------------: | ----- | :-----: | 
| [acapy-afgo](#runset-acapy-afgo) | acapy-main<br>0.7.0-rc1 | afgo-interop<br>unknown | acapy-main<br>0.7.0-rc1 | acapy-main<br>0.7.0-rc1 | pre-AIP 2.0 | [**2 / 3<br>66%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-afgo/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-afj](#runset-acapy-afj) | acapy-main<br>0.7.0-rc1 | javascript<br>1.0.0 | acapy-main<br>0.7.0-rc1 | acapy-main<br>0.7.0-rc1 | AIP 1.0 | [**12 / 12<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-aip10](#runset-acapy-aip10) | acapy-main<br>0.7.0-rc1 | acapy-main<br>0.7.0-rc1 | acapy-main<br>0.7.0-rc1 | acapy-main<br>0.7.0-rc1 | AIP 1.0 | [**17 / 17<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-aip10/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-aip20](#runset-acapy-aip20) | acapy-main<br>0.7.0-rc1 | acapy-main<br>0.7.0-rc1 | acapy-main<br>0.7.0-rc1 | acapy-main<br>0.7.0-rc1 | AIP 2.0 | [**32 / 32<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-aip20/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-dotnet-javascript](#runset-acapy-dotnet-javascript) | acapy-main<br>0.7.0-rc1 | javascript<br>1.0.0 | dotnet-master<br> | acapy-main<br>0.7.0-rc1 | AIP 1.0 | [**10 / 12<br>83%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript-f-dotnet/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-dotnet](#runset-acapy-dotnet) | acapy-main<br>0.7.0-rc1 | dotnet-master<br> | acapy-main<br>0.7.0-rc1 | acapy-main<br>0.7.0-rc1 | AIP 1.0 | [**26 / 27<br>96%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-dotnet/reports/latest/index.html?redirect=false#behaviors) |
| [afgo-acapy](#runset-afgo-acapy) | afgo-interop<br>unknown | acapy-main<br>0.7.0-rc1 | afgo-interop<br>unknown | afgo-interop<br>unknown | pre-AIP 2.0 | [**2 / 3<br>66%**](https://allure.vonx.io/api/allure-docker-service/projects/afgo-b-acapy/reports/latest/index.html?redirect=false#behaviors) |
| [afj-acapy](#runset-afj-acapy) | javascript<br>1.0.0 | acapy-main<br>0.7.0-rc1 | javascript<br>1.0.0 | javascript<br>1.0.0 | AIP 1.0 | [**7 / 12<br>58%**](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-acapy/reports/latest/index.html?redirect=false#behaviors) |
| [dotnet-acapy](#runset-dotnet-acapy) | dotnet-master<br> | acapy-main<br>0.7.0-rc1 | dotnet-master<br> | dotnet-master<br> | AIP 1.0 | [**1 / 12<br>8%**](https://allure.vonx.io/api/allure-docker-service/projects/dotnet-b-acapy/reports/latest/index.html?redirect=false#behaviors) |

## Runset Notes

### Runset **acapy-afgo**

Runset Name: ACA-PY to AF-Go

```tip
**Latest results: 2 out of 3 (66%)**


*Last run: Sun Jul 11 01:22:30 UTC 2021*
```

#### Current Runset Status

None of the tests are currently working and issues have been created to try to determine three identified issues.
One might be in the test suite, while two others appear to be in the Aries Framework Go.

*Status Note Updated: 2021.03.05*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-afgo/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-afgo/reports/latest)


### Runset **acapy-afj**

Runset Name: ACA-PY to AFJ

```tip
**Latest results: 12 out of 12 (100%)**


*Last run: Sun Jul 11 01:29:22 UTC 2021*
```

#### Current Runset Status

Most of the tests are running. The tests not passing are being investigated.

*Status Note Updated: 2021.03.18*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-javascript/reports/latest)


### Runset **acapy-aip10**

Runset Name: ACA-PY to ACA-Py

```tip
**Latest results: 17 out of 17 (100%)**


*Last run: Sun Jul 11 01:34:25 UTC 2021*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.03.18*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/acapy-aip10/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-aip10/reports/latest)


### Runset **acapy-aip20**

Runset Name: ACA-PY to ACA-Py

```tip
**Latest results: 32 out of 32 (100%)**


*Last run: Sun Jul 11 01:47:04 UTC 2021*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.03.16*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/acapy-aip20/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-aip20/reports/latest)


### Runset **acapy-dotnet-javascript**

Runset Name: ACA-PY to AF-.NET to AFJ

```tip
**Latest results: 10 out of 12 (83%)**


*Last run: Sun Jul 11 01:42:45 UTC 2021*
```

#### Current Runset Status

All tests are working, except for three tests that include Faber in the test run as an issuer.
These tests are; T001-RFC0037@1.2, T001.2-RFC0037@1.2, T001.4-RFC0037@1.1 . Further investigation 
is required to determine the issue in these three tests.

*Status Note Updated: 2021.03.18*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript-f-dotnet/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-javascript-f-dotnet/reports/latest)


### Runset **acapy-dotnet**

Runset Name: ACA-PY to AF-.NET

```tip
**Latest results: 26 out of 27 (96%)**


*Last run: Sun Jul 11 01:57:24 UTC 2021*
```

#### Current Runset Status

The majority of tests are running and passing. T013-HIPE0011 is failing due to the Aries Framework Dotnet not supporting
presentations containing a non-revocation interval, with a non-revocable credential. This issue is being tracked in 
https://github.com/hyperledger/aries-framework-dotnet/issues/184

*Status Note Updated: 2021.04.08*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-dotnet/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-dotnet/reports/latest)


### Runset **afgo-acapy**

Runset Name: AF-Go to ACA-PY

```tip
**Latest results: 2 out of 3 (66%)**


*Last run: Sun Jul 11 01:53:43 UTC 2021*
```

#### Current Runset Status

None of the tests are currently working and issues have been created to try to determine three identified issues.
One might be in the test suite, while two others appear to be in the Aries Framework Go.

*Status Note Updated: 2021.03.17*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/afgo-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/afgo-b-acapy/reports/latest)


### Runset **afj-acapy**

Runset Name: AFJ to ACA-PY

```tip
**Latest results: 7 out of 12 (58%)**


*Last run: Sun Jul 11 01:57:46 UTC 2021*
```

#### Current Runset Status

All AIP10 tests are currently running, except for the tests with the holder proposing a proof, 
as that feature is not supported in AFJ.

*Status Note Updated: 2021.03.17*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/javascript-b-acapy/reports/latest)


### Runset **dotnet-acapy**

Runset Name: AF-.NET to ACA-PY

```tip
**Latest results: 1 out of 12 (8%)**


*Last run: Sun Jul 11 02:10:02 UTC 2021*
```

#### Current Runset Status

More tests are failing than are passing when Aries Framework .NET is playing the issuer role. More investigation is needed.

*Status Note Updated: 2021.03.17*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/dotnet-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/dotnet-b-acapy/reports/latest)

Jump back to the [interoperability summary](./README.md).

