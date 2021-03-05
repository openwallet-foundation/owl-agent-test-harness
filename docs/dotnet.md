# AF-.NET to AF-.NET Passing Tests

## Summary of Tests


 This runset uses the current main branch of Aries Framework .NET for all of the agents. The runset runs all of the tests in the suite
 that are expected to pass given the current state of Aries Framework .NET's support for AIP 1. Tests related to revocation (Indy HIPE 0011)
 and holders initiating present proof protocols using a "proposal" message are not included.
 


|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) | Scope of Tests |
| :------------: | :----------: | :-------------: | :--------------: | -------------- |
| dotnet-master | dotnet-master | dotnet-master | dotnet-master | AIP 1.0 except revocation and proof proposals |

```tip
**Latest results: 13 out of 13 (100%)**
```

## Current Status of Tests

All of the tests being executed in this runset are passing.

## Test Run Details
See the tests runs organized by Aries RFC [dotnet behaviors](https://allure.vonx.io/api/allure-docker-service/projects/dotnet/reports/latest/index.html?redirect=false#behaviors)

See the test runs history and drill into the details [dotnet](https://allure.vonx.io/allure-docker-service-ui/projects/dotnet/reports/latest)

