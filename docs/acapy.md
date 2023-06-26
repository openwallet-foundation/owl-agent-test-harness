# Aries Cloud Agent Python Interoperability

## Runsets with ACA-Py

| Runset | ACME<br>(Issuer) | Bob<br>(Holder) | Faber<br>(Verifier) | Mallory<br>(Holder) | Scope | Results | 
| ------ | :--------------: | :-------------: | :----------------: | :-----------------: | ----- | :-----: | 
| [acapy-afgo](#runset-acapy-afgo) | acapy-main<br>0.8.2-rc0 | afgo-interop<br>unknown | acapy-main<br>0.8.2-rc0 | acapy-main<br>0.8.2-rc0 | pre-AIP 2.0 | [**3 / 14<br>21%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-afgo/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-afj](#runset-acapy-afj) | acapy-main<br>0.8.2-rc0 | javascript<br>0.4.1-alpha.4 | acapy-main<br>0.8.2-rc0 | acapy-main<br>0.8.2-rc0 | AIP 1.0 | [**38 / 39<br>97%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-aip10](#runset-acapy-aip10) | acapy-main<br>0.8.2-rc0 | acapy-main<br>0.8.2-rc0 | acapy-main<br>0.8.2-rc0 | acapy-main<br>0.8.2-rc0 | AIP 1.0 | [**35 / 35<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-aip10/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-aip20](#runset-acapy-aip20) | acapy-main<br>0.8.2-rc0 | acapy-main<br>0.8.2-rc0 | acapy-main<br>0.8.2-rc0 | acapy-main<br>0.8.2-rc0 | AIP 2.0 | [**60 / 61<br>98%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-aip20/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-ariesvcx](#runset-acapy-ariesvcx) | acapy-main<br>0.8.2-rc0 | aries-vcx<br>1.0.0 | acapy-main<br>0.8.2-rc0 | acapy-main<br>0.8.2-rc0 | AIP 1.0 | [**18 / 18<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-aries-vcx/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-findy](#runset-acapy-findy) | acapy-main<br>0.8.2-rc0 | findy<br>0.31.11 | acapy-main<br>0.8.2-rc0 | acapy-main<br>0.8.2-rc0 | AIP 1.0 | [**17 / 17<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-findy/reports/latest/index.html?redirect=false#behaviors) |
| [afgo-acapy](#runset-afgo-acapy) | afgo-interop<br>unknown | acapy-main<br>0.8.2-rc0 | afgo-interop<br>unknown | afgo-interop<br>unknown | pre-AIP 2.0 | [**1 / 17<br>5%**](https://allure.vonx.io/api/allure-docker-service/projects/afgo-b-acapy/reports/latest/index.html?redirect=false#behaviors) |
| [afj-acapy](#runset-afj-acapy) | javascript<br>0.4.1-alpha.4 | acapy-main<br>0.8.2-rc0 | javascript<br>0.4.1-alpha.4 | javascript<br>0.4.1-alpha.4 | AIP 1.0 | [**11 / 28<br>39%**](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-acapy/reports/latest/index.html?redirect=false#behaviors) |
| [ariesvcx-acapy](#runset-ariesvcx-acapy) | aries-vcx<br>1.0.0 | acapy-main<br>0.8.2-rc0 | aries-vcx<br>1.0.0 | aries-vcx<br>1.0.0 | AIP 1.0 | [**19 / 20<br>95%**](https://allure.vonx.io/api/allure-docker-service/projects/aries-vcx-b-acapy/reports/latest/index.html?redirect=false#behaviors) |
| [findy-acapy](#runset-findy-acapy) | findy<br>0.31.11 | acapy-main<br>0.8.2-rc0 | findy<br>0.31.11 | findy<br>0.31.11 | AIP 1.0 | [**17 / 17<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-acapy/reports/latest/index.html?redirect=false#behaviors) |

## Runset Notes

### Runset **acapy-afgo**

Runset Name: ACA-PY to AF-Go

```tip
**Latest results: 3 out of 14 (21%)**


*Last run: Mon Jun 26 00:27:13 UTC 2023*
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


*Last run: Mon Jun 26 00:49:05 UTC 2023*
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


*Last run: Mon Jun 26 00:40:12 UTC 2023*
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
**Latest results: 60 out of 61 (98%)**


*Last run: Mon Jun 26 00:49:23 UTC 2023*
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


*Last run: Mon Jun 26 01:15:08 UTC 2023*
```

#### Current Runset Status
```warning
No test status note is available for this runset. Please update: .github/workflows/test-harness-acapy-ariesvcx.yml.
```

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-aries-vcx/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-aries-vcx/reports/latest)


### Runset **acapy-findy**

Runset Name: ACA-PY to findy

```tip
**Latest results: 17 out of 17 (100%)**


*Last run: Mon Jun 26 01:06:28 UTC 2023*
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
**Latest results: 1 out of 17 (5%)**


*Last run: Mon Jun 26 01:09:46 UTC 2023*
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


*Last run: Mon Jun 26 01:29:15 UTC 2023*
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


*Last run: Mon Jun 26 02:23:40 UTC 2023*
```

#### Current Runset Status
```warning
No test status note is available for this runset. Please update: .github/workflows/test-harness-ariesvcx-acapy.yml.
```

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/aries-vcx-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/aries-vcx-b-acapy/reports/latest)


### Runset **findy-acapy**

Runset Name: findy to ACA-PY

```tip
**Latest results: 17 out of 17 (100%)**


*Last run: Mon Jun 26 02:21:43 UTC 2023*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.09.14*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/findy-b-acapy/reports/latest)

Jump back to the [interoperability summary](./README.md).

