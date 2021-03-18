# Aries Framework Go Interoperability

## Runsets with AF-Go

| Runset | ACME<br>(Issuer) | Bob<br>(Holder) | Faber<br>(Verfier) | Mallory<br>(Holder) | Scope | Results | 
| ------ | :--------------: | :-------------: | :----------------: | :-----------------: | ----- | :-----: | 
| [acapy-afgo](#runset-acapy-afgo) | acapy-main | afgo-master | acapy-main | acapy-main | pre-AIP 2.0 | [**0 / 5<br>0%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-afgo/reports/latest/index.html?redirect=false#behaviors) |
| [afgo](#runset-afgo) | afgo-master | afgo-master | afgo-master | afgo-master | pre-AIP 2.0 | [**3 / 5<br>60%**](https://allure.vonx.io/api/allure-docker-service/projects/afgo/reports/latest/index.html?redirect=false#behaviors) |

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


### Runset **afgo**

Runset Name: AF-Go to AF-Go

```tip
**Latest results: 3 out of 5 (60%)**


*Last run: Wed Mar 17 17:44:15 PDT 2021*
```

#### Current Runset Status

The tests that use an implicit invitation are not currently working. The issue is being investigated -- this feature may not be
supported in Aries Framework Go.

*Status Note Updated: 2021.03.05*

#### Runset Details

- Results grouped by [executed Aries RFCs executed](https://allure.vonx.io/api/allure-docker-service/projects/afgo/reports/latest/index.html?redirect=false#behaviors)
- Results by [history](https://allure.vonx.io/allure-docker-service-ui/projects/afgo/reports/latest)

Jump back to the [interoperability summary](./README.md).

