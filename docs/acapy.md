# Aries Cloud Agent Python Interoperability

## Runsets with ACA-Py

| Runset | ACME<br>(Issuer) | Bob<br>(Holder) | Faber<br>(Verifier) | Mallory<br>(Holder) | Scope | Results | 
| ------ | :--------------: | :-------------: | :----------------: | :-----------------: | ----- | :-----: | 
| [acapy-afj](#runset-acapy-afj) | acapy-main<br>1.0.0rc4 | javascript<br>0.5.0-alpha.97 | acapy-main<br>1.0.0rc4 | acapy-main<br>1.0.0rc4 | AIP 1.0 | [**37 / 39<br>94%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-aip10](#runset-acapy-aip10) | acapy-main<br>1.0.0rc4 | acapy-main<br>1.0.0rc4 | acapy-main<br>1.0.0rc4 | acapy-main<br>1.0.0rc4 | AIP 1.0 | [**35 / 35<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-aip10/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-aip20](#runset-acapy-aip20) | acapy-main<br>1.0.0rc4 | acapy-main<br>1.0.0rc4 | acapy-main<br>1.0.0rc4 | acapy-main<br>1.0.0rc4 | AIP 2.0 | [**47 / 61<br>77%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-aip20/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-ariesvcx](#runset-acapy-ariesvcx) | acapy-main<br>1.0.0rc4 | aries-vcx<br>0.64.0 | acapy-main<br>1.0.0rc4 | acapy-main<br>1.0.0rc4 | AIP 1.0 | [**19 / 28<br>67%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-aries-vcx/reports/latest/index.html?redirect=false#behaviors) |
| [afj-acapy](#runset-afj-acapy) | javascript<br>0.5.0-alpha.97 | acapy-main<br>1.0.0rc4 | javascript<br>0.5.0-alpha.97 | javascript<br>0.5.0-alpha.97 | AIP 1.0 | [**11 / 28<br>39%**](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-acapy/reports/latest/index.html?redirect=false#behaviors) |
| [ariesvcx-acapy](#runset-ariesvcx-acapy) | aries-vcx<br>0.64.0 | acapy-main<br>1.0.0rc4 | aries-vcx<br>0.64.0 | aries-vcx<br>0.64.0 | AIP 1.0 | [**11 / 28<br>39%**](https://allure.vonx.io/api/allure-docker-service/projects/aries-vcx-b-acapy/reports/latest/index.html?redirect=false#behaviors) |

## Runset Notes

### Runset **acapy-afj**

Runset Name: ACA-PY to AFJ

```tip
**Latest results: 37 out of 39 (94%)**


*Last run: Mon Jul 22 00:48:57 UTC 2024*
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


*Last run: Mon Jul 22 01:11:04 UTC 2024*
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
**Latest results: 47 out of 61 (77%)**


*Last run: Mon Jul 22 01:40:39 UTC 2024*
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
**Latest results: 19 out of 28 (67%)**


*Last run: Mon Jul 22 01:56:48 UTC 2024*
```

#### Current Runset Status

RFC0023 is disabled due to inconsistent results. RFC0793 is also being investigated: https://github.com/hyperledger/aries-vcx/issues/1252
*Status Note Updated: 2024.07.05*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-aries-vcx/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-aries-vcx/reports/latest)


### Runset **afj-acapy**

Runset Name: AFJ to ACA-PY

```tip
**Latest results: 11 out of 28 (39%)**


*Last run: Mon Jul 22 02:54:52 UTC 2024*
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
**Latest results: 11 out of 28 (39%)**


*Last run: Mon Jul 22 03:44:44 UTC 2024*
```

#### Current Runset Status

Most tests are currently struggling, due to aries-vcx reporting the wrong connection state to the
backchannel. Being resolved here: https://github.com/hyperledger/aries-vcx/issues/1253
@RFC0793 has relatively low success due to aries-vcx not supporting full range of DID methods in
these tests.
*Status Note Updated: 2024.07.05*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/aries-vcx-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/aries-vcx-b-acapy/reports/latest)

Jump back to the [interoperability summary](./README.md).

