# Aries Cloud Agent Python Interoperability

## Runsets with ACA-Py

| Runset | ACME<br>(Issuer) | Bob<br>(Holder) | Faber<br>(Verfier) | Mallory<br>(Holder) | Scope | Results | 
| ------ | :--------------: | :-------------: | :----------------: | :-----------------: | ----- | :-----: | 
| [acapy-afgo](#runset-acapy-afgo) | acapy-main | afgo-master | acapy-main | acapy-main | pre-AIP 2.0 | [**0 / 5<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-afgo/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-afj](#runset-acapy-afj) | acapy-main | javascript | acapy-main | acapy-main | AIP 1.0 | [**13 / 18<br>72%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors) |
| [acapy-dotnet](#runset-acapy-dotnet) | acapy-main | dotnet-master | acapy-main | acapy-main | AIP 1.0 | [**25 / 25<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-dotnet/reports/latest/index.html?redirect=false#behaviors) |
| [acapy](#runset-acapy) | acapy-main | acapy-main | acapy-main | acapy-main | AIP 1.0 | [**42 / 42<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy/reports/latest/index.html?redirect=false#behaviors) |

## Runset Notes

### Runset **acapy-afgo**

Runset Name: ACA-PY to AF-Go

```tip
**Latest results: 0 out of 5 (0%)**


*Last run: Wed Mar 17 17:08:11 PDT 2021*
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
**Latest results: 13 out of 18 (72%)**


*Last run: Wed Mar 17 18:36:01 PDT 2021*
```

#### Current Runset Status

Only about half of the tests are currently running. The issues seem to be related to the set of tags
of the test cases being run as a number of the revocation tests are running and shouldn't be. As well,
the tests with the holder proposing a proof are not running, as that feature is not supported in AFJ.

*Status Note Updated: 2021.03.08*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-javascript/reports/latest)


### Runset **acapy-dotnet**

Runset Name: ACA-PY to AF-.NET

```tip
**Latest results: 25 out of 25 (100%)**


*Last run: Wed Mar 17 17:30:45 PDT 2021*
```

#### Current Runset Status

All of the tests are currently running.

*Status Note Updated: 2021.03.05*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-dotnet/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-dotnet/reports/latest)


### Runset **acapy**

Runset Name: ACA-PY to ACA-Py

```tip
**Latest results: 42 out of 42 (100%)**


*Last run: Wed Mar 17 17:13:23 PDT 2021*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.03.05*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/acapy/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy/reports/latest)

Jump back to the [interoperability summary](./README.md).

