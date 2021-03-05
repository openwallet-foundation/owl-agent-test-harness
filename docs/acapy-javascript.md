# ACA-PY and AF-JS

## Summary of Tests


 This runset uses the current main branch of ACA-Py for all of the agents except Bob (holder),
 which uses the master branch of Aries Framework JavaScript. The runset covers all of the AIP 1.0 tests
 except those that are known **not** to work with the Aries Framework JavaScript as the holder,
 notably those that involve revocation.
 


|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) | Scope of Tests |
| :------------: | :----------: | :-------------: | :--------------: | -------------- |
| acapy-master | javascript | acapy-master | acapy-master | AIP 1.0 except revocation |

```tip
**Latest results: 15 out of 30 (50%)**
```

## Current Status of Tests

Only about half of the tests are currently running. The issues seem to be related to the set of tags
of the test cases being run as a number of the revocation tests are running and shouldn't be. As well,
the tests with the holder proposing a proof are not running, as that feature is not supported in AFJ.

## Test Run Details
See the tests runs organized by Aries RFC [acapy-b-javascript behaviors](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-javascript/reports/latest/index.html?redirect=false#behaviors)

See the test runs history and drill into the details [acapy-b-javascript](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-javascript/reports/latest)

