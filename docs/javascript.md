# Aries Framework JavaScript Interoperability

## Runsets with AFJ

| Runset | ACME<br>(Issuer) | Bob<br>(Holder) | Faber<br>(Verfier) | Mallory<br>(Holder) | Scope | Results | 
| ------ | :--------------: | :-------------: | :----------------: | :-----------------: | ----- | :-----: | 
| [acapy-afj](#runset-acapy-afj) | acapy-main | javascript | acapy-main | acapy-main | AIP 1.0 | [**13 / 18<br>72%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors) |
| [afj-dotnet](#runset-afj-dotnet) | javascript | dotnet-master | javascript | javascript | AIP 1.0 | [**13 / 13<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-dotnet/reports/latest/index.html?redirect=false#behaviors) |
| [afj](#runset-afj) | javascript | javascript | javascript | javascript | AIP 1.0 | [**18 / 18<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/javascript/reports/latest/index.html?redirect=false#behaviors) |

## Runset Notes

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


### Runset **afj-dotnet**

Runset Name: AFJ to AF-.NET

```tip
**Latest results: 13 out of 13 (100%)**


*Last run: Wed Mar 17 18:02:20 PDT 2021*
```

#### Current Runset Status

All but one of the tests being executed in this runset are passing. The failure is being investigated.

*Status Note Updated: 2021.03.05*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-dotnet/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/javascript-b-dotnet/reports/latest)


### Runset **afj**

Runset Name: AFJ to AFJ

```tip
**Latest results: 18 out of 18 (100%)**


*Last run: Wed Mar 17 17:12:09 PDT 2021*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.03.05*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/javascript/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/javascript/reports/latest)

Jump back to the [interoperability summary](./README.md).

