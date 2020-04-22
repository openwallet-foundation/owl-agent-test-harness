# Aries Agent Test Harness Quick Start Guide

This guide quickly gets the Aca-py Agent BDD tests up and running. It utilizes separate docker containers for the Indy Ledger and Ledger Browser, the ACA-PY agents and backchannels, and the test harness itself. 

## Prerequisites

- Docker is installed and working on the host machine.
- git is install and working with a github account.

## Run the Ledger and Ledger Browser

In one shell...

``` bash
git clone https://github.com/bcgov/von-network
cd von-network
./manage build
./manage start --logs
```

## Run the Aries Agent Tests

In another shell...

``` bash
git clone https://github.com/bcgov/aries-agent-test-harness.git
cd aries-agent-test-harness/docker
./manage build
./manage run
```

The above will run all tests for all features. 

Read Test Tags Below for in use and proposed test scenario tags

Using tags, one can just run Acceptance Tests...

``` bash
./manage run --tags=AcceptanceTest
```

or all Priority 1 Acceptance Tests...

``` bash
./manage run --tags=@P1 --tags=@AcceptanceTest
```

or derived functional tests

``` bash
./manage run --tags=DerivedFunctionalTest
```

or all the ExceptionTests...

``` bash
./manage run --tags=ExceptionTest
```

To read more on how one can control the execution of test sets based on tags see [https://behave.readthedocs.io/en/latest/tutorial.html#controlling-things-with-tags](https://behave.readthedocs.io/en/latest/tutorial.html#controlling-things-with-tags)

At the command line, any of the regular behave arguments can be specified to control how behave behaves. [https://behave.readthedocs.io/en/latest/behave.html]
(https://behave.readthedocs.io/en/latest/behave.html)

## Test Tags

The test harness has utilized tags in the feature files to be able to narrow down a test set to be executed. The general tags currently utilized are as follows:

- @AcceptanceTest - Tests based on requirements specifically stated in the RFC
- @DerivedFunctionalTest - Tests derived on requirements but not specifically stated in the RFC.
- @P1 - Test Priority
- @P2 - Test Priority
- @P3 - Test Priority
- @P4 - Test Priority
- @NegativeTest - Test that attempts to break the software. ie. change workflow order, use invalid data, etc.
- @ExceptionTest - Tests that are based on requirements that suggest exception cases.
- @SmokeTest - Tests that can be used as a builds smoke or sanity tests.
- @NeedsReview - Tests that have not been reviewed or approved.
- @ReviewedApproved - obvious
- @wip - Tests that are a work in progress and incomplete
- @Done - Finished tests that are expected to Pass if executed against an Agent.
- @AIP10 - Aries Interop Profile version the tests are written for
- @T01-API10-RFC0160 - Test Unique Identifier

Proposed Connection Protocol Tags

- @MultiUseInvite - Test utilizes a multi-use invite. Not using this tag and the test expects the invite to be single use.
- @SingleTryOnException
- @RetryableOnException
