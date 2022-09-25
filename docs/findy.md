# Findy Agent Interoperability

## Runsets with Findy

| Runset | ACME<br>(Issuer) | Bob<br>(Holder) | Faber<br>(Verifier) | Mallory<br>(Holder) | Scope | Results | 
| ------ | :--------------: | :-------------: | :----------------: | :-----------------: | ----- | :-----: | 
| [acapy-findy](#runset-acapy-findy) | acapy-main<br>1.0.0-rc0 | findy<br>0.30.33 | acapy-main<br>1.0.0-rc0 | acapy-main<br>1.0.0-rc0 | AIP 1.0 | [**17 / 17<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-findy/reports/latest/index.html?redirect=false#behaviors) |
| [afj-findy](#runset-afj-findy) | javascript<br>0.2.5-alpha.1 | findy<br>0.30.33 | javascript<br>0.2.5-alpha.1 | javascript<br>0.2.5-alpha.1 | AIP 1.0 | [**17 / 17<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-findy/reports/latest/index.html?redirect=false#behaviors) |
| [dotnet-findy](#runset-dotnet-findy) | dotnet<br> | findy<br>0.30.33 | dotnet<br> | dotnet<br> | AIP 1.0 | [**2 / 10<br>20%**](https://allure.vonx.io/api/allure-docker-service/projects/dotnet-b-findy/reports/latest/index.html?redirect=false#behaviors) |
| [findy-acapy](#runset-findy-acapy) | findy<br>0.30.33 | acapy-main<br>1.0.0-rc0 | findy<br>0.30.33 | findy<br>0.30.33 | AIP 1.0 | [**17 / 17<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-acapy/reports/latest/index.html?redirect=false#behaviors) |
| [findy-dotnet](#runset-findy-dotnet) | findy<br>0.30.33 | dotnet<br> | findy<br>0.30.33 | findy<br>0.30.33 | AIP 1.0 | [**12 / 12<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-dotnet/reports/latest/index.html?redirect=false#behaviors) |
| [findy-javascript-dotnet](#runset-findy-javascript-dotnet) | findy<br>0.30.33 | javascript<br>0.2.5-alpha.1 | dotnet<br> | findy<br>0.30.33 | AIP 1.0 | [**17 / 17<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-javascript-f-dotnet/reports/latest/index.html?redirect=false#behaviors) |
| [findy-javascript](#runset-findy-javascript) | findy<br>0.30.33 | javascript<br>0.2.5-alpha.1 | findy<br>0.30.33 | findy<br>0.30.33 | AIP 1.0 | [**17 / 17<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-javascript/reports/latest/index.html?redirect=false#behaviors) |
| [findy](#runset-findy) | findy<br>0.30.33 | findy<br>0.30.33 | findy<br>0.30.33 | findy<br>0.30.33 | AIP 1.0 | [**17 / 17<br>100%**](https://allure.vonx.io/api/allure-docker-service/projects/findy/reports/latest/index.html?redirect=false#behaviors) |

## Runset Notes

### Runset **acapy-findy**

Runset Name: ACA-PY to findy

```tip
**Latest results: 17 out of 17 (100%)**


*Last run: Sun Sep 25 01:19:15 UTC 2022*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.09.14*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/acapy-b-findy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/acapy-b-findy/reports/latest)


### Runset **afj-findy**

Runset Name: AFJ to findy

```tip
**Latest results: 17 out of 17 (100%)**


*Last run: Sun Sep 25 01:57:41 UTC 2022*
```

#### Current Runset Status

All of the tests being executed in this runset are failing. There is an issue with afj sending the connection
response, and throws an error processing inbound message.

*Status Note Updated: 2021.09.28*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/javascript-b-findy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/javascript-b-findy/reports/latest)


### Runset **dotnet-findy**

Runset Name: dotnet to findy

```tip
**Latest results: 2 out of 10 (20%)**


*Last run: Sun Sep 25 02:20:11 UTC 2022*
```

#### Current Runset Status

Two connection tests are passing out of Nineteen total. There are multiple issues in Issue Credential and Proof
with dotnet as the issuer and findy as the holder. Removed a large portion of Proof tests since jobs were getting cancelled.
These will be added back when tests or agents are fixed and stability has returned.

*Status Note Updated: 2022.01.28*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/dotnet-b-findy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/dotnet-b-findy/reports/latest)


### Runset **findy-acapy**

Runset Name: findy to ACA-PY

```tip
**Latest results: 17 out of 17 (100%)**


*Last run: Sun Sep 25 02:43:56 UTC 2022*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.09.14*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-acapy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/findy-b-acapy/reports/latest)


### Runset **findy-dotnet**

Runset Name: findy to dotnet

```tip
**Latest results: 12 out of 12 (100%)**


*Last run: Sun Sep 25 02:36:34 UTC 2022*
```

#### Current Runset Status

All test scenarios are passing. 

*Status Note Updated: 2021.10.15*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-dotnet/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/findy-b-dotnet/reports/latest)


### Runset **findy-javascript-dotnet**

Runset Name: findy to AFJ to AF-.NET

```tip
**Latest results: 17 out of 17 (100%)**


*Last run: Sun Sep 25 03:01:30 UTC 2022*
```

#### Current Runset Status

All of the tests being executed in this runset are passing. 

*Status Note Updated: 2021.10.15*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-javascript-f-dotnet/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/findy-b-javascript-f-dotnet/reports/latest)


### Runset **findy-javascript**

Runset Name: findy to AFJ

```tip
**Latest results: 17 out of 17 (100%)**


*Last run: Sun Sep 25 02:53:40 UTC 2022*
```

#### Current Runset Status

All of the tests being executed in this runset are passing. 

*Status Note Updated: 2021.10.15*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/findy-b-javascript/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/findy-b-javascript/reports/latest)


### Runset **findy**

Runset Name: findy to findy

```tip
**Latest results: 17 out of 17 (100%)**


*Last run: Sun Sep 25 02:51:19 UTC 2022*
```

#### Current Runset Status

All of the tests being executed in this runset are passing.

*Status Note Updated: 2021.09.14*

#### Runset Details

- [Results by executed Aries RFCs](https://allure.vonx.io/api/allure-docker-service/projects/findy/reports/latest/index.html?redirect=false#behaviors)
- [Test execution history](https://allure.vonx.io/allure-docker-service-ui/projects/findy/reports/latest)

Jump back to the [interoperability summary](./README.md).

