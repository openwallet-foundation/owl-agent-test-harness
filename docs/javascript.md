# Aries Framework JavaScript Interoperability

## Runsets with AFJ

| Runset | ACME<br>(Issuer) | Bob<br>(Holder) | Faber<br>(Verifier) | Mallory<br>(Holder) | Scope | Results | 
| ------ | :--------------: | :-------------: | :----------------: | :-----------------: | ----- | :-----: | 
| [acapy-afj](#runset-acapy-afj) | acapy-main<br>0.8.1 | javascript<br> | acapy-main<br>0.8.1 | acapy-main<br>0.8.1 | AIP 1.0 | [**0 / 39<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors) |
| [afj-acapy](#runset-afj-acapy) | javascript<br> | acapy-main<br>0.8.1 | javascript<br> | javascript<br> | AIP 1.0 | [**0 / 28<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-acapy/reports/latest/index.html?redirect=false#behaviors) |
| [afj-findy](#runset-afj-findy) | javascript<br> | findy<br>0.30.63 | javascript<br> | javascript<br> | AIP 1.0 | [**0 / 17<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-findy/reports/latest/index.html?redirect=false#behaviors) |
| [afj](#runset-afj) | javascript<br> | javascript<br> | javascript<br> | javascript<br> | AIP 1.0 | [**0 / 28<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/javascript/reports/latest/index.html?redirect=false#behaviors) |
| [ariesvcx-javascript](#runset-ariesvcx-javascript) | aries-vcx<br>1.0.0 | javascript<br> | aries-vcx<br>1.0.0 | aries-vcx<br>1.0.0 | AIP 1.0 | [**0 / 20<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/aries-vcx-b-javascript/reports/latest/index.html?redirect=false#behaviors) |
| [findy-javascript](#runset-findy-javascript) | findy<br>0.30.63 | javascript<br> | findy<br>0.30.63 | findy<br>0.30.63 | AIP 1.0 | [**0 / 17<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-javascript/reports/latest/index.html?redirect=false#behaviors) |
| [javascript-ariesvcx](#runset-javascript-ariesvcx) | javascript<br> | aries-vcx<br>1.0.0 | javascript<br> | javascript<br> | AIP 1.0 | [**0 / 18<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-aries-vcx/reports/latest/index.html?redirect=false#behaviors) |

## Runset Notes

### Runset **acapy-afj**

Runset Name: ACA-PY to AFJ

```tip
**Latest results: 0 out of 39 (0%)**


*Last run: Wed Apr 12 00:22:49 UTC 2023*
```

#### Current Runset Status

Most of the tests are running. The tests not passing are being investigated.

*Status Note Updated: 2021.03.18*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-javascript/reports/latest)


### Runset **afj-acapy**

Runset Name: AFJ to ACA-PY

```tip
**Latest results: 0 out of 28 (0%)**


*Last run: Wed Apr 12 01:12:15 UTC 2023*
```

#### Current Runset Status

All AIP10 tests are currently running.

*Status Note Updated: 2021.03.17*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/javascript-b-acapy/reports/latest)


### Runset **afj-findy**

Runset Name: AFJ to findy

```tip
**Latest results: 0 out of 17 (0%)**


*Last run: Wed Apr 12 01:22:13 UTC 2023*
```

#### Current Runset Status

All of the tests being executed in this runset are failing. There is an issue with afj sending the connection
response, and throws an error processing inbound message.

*Status Note Updated: 2021.09.28*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-findy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/javascript-b-findy/reports/latest)


### Runset **afj**

Runset Name: AFJ to AFJ

```tip
**Latest results: 0 out of 28 (0%)**


*Last run: Wed Apr 12 01:22:31 UTC 2023*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.03.05*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/javascript/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/javascript/reports/latest)


### Runset **ariesvcx-javascript**

Runset Name: aries-vcx to javascript

```tip
**Latest results: 0 out of 20 (0%)**


*Last run: Wed Apr 12 02:02:28 UTC 2023*
```

#### Current Runset Status
```warning
No test status note is available for this runset. Please update: .github/workflows/test-harness-ariesvcx-javascript.yml.
```

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/aries-vcx-b-javascript/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/aries-vcx-b-javascript/reports/latest)


### Runset **findy-javascript**

Runset Name: findy to AFJ

```tip
**Latest results: 0 out of 17 (0%)**


*Last run: Wed Apr 12 02:15:16 UTC 2023*
```

#### Current Runset Status

All of the tests being executed in this runset are passing. 

*Status Note Updated: 2021.10.15*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-javascript/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/findy-b-javascript/reports/latest)


### Runset **javascript-ariesvcx**

Runset Name: javascript to aries-vcx

```tip
**Latest results: 0 out of 18 (0%)**


*Last run: Wed Apr 12 03:05:17 UTC 2023*
```

#### Current Runset Status
```warning
No test status note is available for this runset. Please update: .github/workflows/test-harness-javascript-ariesvcx.yml.
```

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-aries-vcx/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/javascript-b-aries-vcx/reports/latest)

Jump back to the [interoperability summary](./README.md).

