# AFJ to AF-.NET

## Summary of Tests


 This runset uses the current main branch of Aries Framework - JavaScript for all of the agents except for Bob (the Holder), which
 uses Aries Framework .NET. The runset executes all of the AIP 1.0 tests that are expected to be pass given the two state of the
 two frameworks involved. Tests involving revocation (not supported in Aries Framework - JavaScript) and proof proposals (not supported
 in Aries Framework .NET) are not executed.
 


|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) | Scope of Tests |
| :------------: | :----------: | :-------------: | :--------------: | -------------- |
| javascript | dotnet-master | javascript | javascript | AIP 1.0 except revocation and proof proposals |

```tip
**Latest results: 13 out of 13 (100%)**


*Last updated: Mon 8 Mar 2021 12:43:52 CET*
```

## Current Status of Tests

All but one of the tests being executed in this runset are passing. The failure is being investigated.

*Updated: 2021.03.05*

## Test Run Details
See the tests results grouped by the Aries RFCs executed [javascript-b-dotnet](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-dotnet/reports/latest/index.html?redirect=false#behaviors)

See the test runs history and drill into the details [javascript-b-dotnet](https://allure.vonx.io/allure-docker-service-ui/projects/javascript-b-dotnet/reports/latest)

Jump back to the [runset summary](./README.md).

