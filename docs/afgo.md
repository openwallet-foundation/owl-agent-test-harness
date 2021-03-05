# AF-Go to AF-Go Passing Tests

## Summary of Tests


 This runset uses the current main branch of Aries Framework Go for all of the agents. The runset runs some of the tests in the suite
 that are expected to pass given the current state of Aries Framework Go support for 2 DID exchange.
 


|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) | Scope of Tests |
| :------------: | :----------: | :-------------: | :--------------: | -------------- |
| afgo-master | afgo-master | afgo-master | afgo-master | AP 2.0 RFC0023 Only |

```tip
**Latest results: 3 out of 5 (60%)**
```

## Current Status of Tests

The tests that use an implicit invitation are not currently working. The issue is being investigated -- this feature may not be
supported in Aries Framework Go.

## Test Run Details
See the tests runs organized by Aries RFC [afgo behaviors](https://allure.vonx.io/api/allure-docker-service/projects/afgo/reports/latest/index.html?redirect=false#behaviors)

See the test runs history and drill into the details [afgo](https://allure.vonx.io/allure-docker-service-ui/projects/afgo/reports/latest)

