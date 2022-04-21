# Aries Agent Test Harness: Smashing Complexity in Interoperability Testing<!-- omit in toc -->

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

The Aries Agent Test Harness (AATH) is a [BDD](https://en.wikipedia.org/wiki/Behavior-driven_development)-based test execution engine and set of tests for evaluating the interoperability of Aries Agents and Agent Frameworks. The tests are agnostic to the components under test but rather are designed based on the [Aries RFCs](https://github.com/hyperledger/aries) and the interaction protocols documented there. The AATH enables the creation of an interop lab much like the [labs](https://www.iol.unh.edu/) used by the telcos when introducing new hardware into the markets&mdash;routers, switchers and the like. Aries agent and agent framework builders can easily incorporate these tests into the their CI/CD pipelines to ensure that interoperability is core to the development process.

Want to see the Aries Agent Test Harness in action? Give it a try using a git, docker and bash enabled system. Once you are in a bash shell, run the following commands to execute a set of RFC tests using the [Aries Cloud Agent - Python](https://github.com/hyperledger/aries-cloudagent-python):

```bash
git clone https://github.com/hyperledger/aries-agent-test-harness
cd aries-agent-test-harness
./manage build -a acapy -a dotnet
./manage run -d acapy -b dotnet -t @AcceptanceTest -t ~@wip

```

The commands take a while to run (you know...building modern apps always means downloading half the internet...), so while you wait, here's what's happening:

- The AATH `./manage build` command builds Test Agent docker images for the ACA-Py and .NET agent frameworks and the test harness.
- The AATH `./manage run` command executes a set of tests (those tagged "AcceptanceTest" but not tagged "@wip") with the ACA-Py test agent playing most of the roles&mdash;Acme, Faber and Mallory, while the .NET test agent plays the role of Bob.

It's that last part makes the AATH powerful. On every run, different AATH-enabled components can be assigned any role (Acme, Bob, Faber, Mallory). For some initial pain (AATH-enabling a component), interoperability testing becomes routine, and we can make hit our goal: to make interoperability boring.

Interesting to you? Read on for more about the architecture, how to build tests, how to AATH-enable the Aries agents and agent frameworks that you are building and how you can run these tests on a continuous basis. For a brief set of slides covering the process and goals, check [this](https://docs.google.com/presentation/d/1tNttxlHE8iwyOr7LDOZ6VrCwh8AuINfzuI2Gl0WEld0/edit?usp=sharing) out.

We'd love to have help in building out a full Aries interoperability lab.

## Contents<!-- omit in toc -->

- [Architecture](#architecture)
- [Aries Agent Test Harness Terminology](#aries-agent-test-harness-terminology)
- [Test Script Guidelines](#test-script-guidelines)
- [Aries Agent Backchannels](#aries-agent-backchannels)
  - [Implemented Backchannels](#implemented-backchannels)
- [The `manage` bash script](#the-manage-bash-script)
- [Using AATH Agents as Services](#using-aath-agents-as-services)
  - [Use Cases](#use-cases)
    - [Debugging within AATH](#debugging-within-aath)
    - [Aries Mobile Test Harness](#aries-mobile-test-harness)
- [Extra Backchannel-Specific Parameters](#extra-backchannel-specific-parameters)
- [Custom Configurations for Agents](#custom-configurations-for-agents)
  - [Use Cases](#use-cases-1)
    - [Aries Mobile Test Harness](#aries-mobile-test-harness-1)
- [Test Tags](#test-tags)
  - [Running Tagged Tests](#running-tagged-tests)
  - [Test Coverage](#test-coverage)
  - [Test Reporting](#test-reporting)
- [Adding Runsets](#adding-runsets)

## Architecture

The following diagram provides an overview of the architecture of the AATH.

![Aries Agent Test Harness Architecture](docs/assets/aath-arch/aath-arch.png)

- All of the executable elements run in "Test Agent" docker containers.
- The components-under-test (e.g. Acme, Bob and Mallory) are externally identical, enabling the selection of the components to be tested a runtime decision.
  - An identical HTTP interface exists between the test harness and each test docker container.
  - A "backchannel" within each test container handles the commands from the test harness, converting them into actions understood by the agent or agent framework.
    - This is the hard part&mdash;creating a backchannel for each agents/agent frameworks
- The general roles of the test participants are:
  - Acme: an enterprise issuer/verifier
  - Bob: a holder/prover
  - Faber: another enterprise issuer/verifier
  - Mallory: a malicious holder/prover
  - Other roles could be added, perhaps Carol (another holder/prover) and Device (an IOT device).
- The test harness is the Python [behave](https://behave.readthedocs.io/en/latest/) engine, with the "features" (as they are called in BDD-speak) written in [Gherkin](https://behave.readthedocs.io/en/latest/gherkin.html#gherkin-feature-testing-language) and the feature steps in Python.
- Dockerfiles are used to package the backchannel and the component under test (an agent or agent framework) into a single container image with a pre-defined set of port mappings.
  - One of the ports is for the test-harness-to-backchannel interface, while the rest can be used as needed by the component under test and it's backchannel.
- At test execution time, command line parameters enable the selection of any of the docker images to be used to play any of the test case roles. Further, a flexible test case tagging mechanism enables command line (or configuration file) selection of the tests cases to be run.
  - Since the components being tested will have different capabilities (e.g., issuer, prover, verifier), they may only be selected to play certain roles. For example, a mobile wallet app might only play the roles of Bob and Mallory, and never be selected to play the role of Acme.
  - Likewise, only some tests will be selected for execution based on the interoperable capabilities of the components being tested, for example, a component might only support AIP 2.0.
- A bash script (`./manage`) processes the command line options and orchestrates the docker image building and test case running.
- The `./manage` script also supports running the services needed by the tests, such as a [von-network](https://github.com/bcgov/von-network) Indy instance, an [Indy tails service](https://github.com/bcgov/indy-tails-server), a universal resolver and a `did:orb` instance.
  - Environment variables can also be used to configure a test run to use public services, such as the BCovrin test Indy instance. You'll find examples of using environment variables to use those services in various documentation files in this repo.
- A special Test Agent called `mobile` can be used in the `Bob` role to test mobile wallet apps on phones. See [this document](./MOBILE_AGENT_TESTING.md) for details.

## Aries Agent Test Harness Terminology

There are a couple of layers of abstraction involved in the test harness architecture, and it's worth formalizing some terminology to make it easier to communicate about what's what when we are are running tests.

- **Test Harness**: An engine that executes the selected tests and collects the results.
- **Backchannel**: A piece of integration software that receives HTTP requests from the Test Harness and interacts with the agent or agent framework under test to execute the requests. A backchannel is needed for each agent or agent framework. The same backchannel will likely work for multiple agent and agent framework versions and/or configurations.
- **Components under Test (CUTs)**: external Aries agents or agent frameworks being tested.
  - The CUT might be an agent framework like aries-framework-dotnet or aries-cloudagent-python. In those cases, the backchannel is a controller that directly operates an instance of the agent framework.
  - The CUT might be a full agent; a combination of an agent framework instance and a controller. In those cases, the backchannel must be able to operate the controller, which in turn controls the agent framework. For example, a mobile agent has a user interface (a controller), perhaps with some automation rules. Its' AATH backchannel will interact with the controller, not the agent framework directly.
  - There may be multiple CUTs that operate with a single backchannel. For example, different configurations of an agent framework or different versions.
- **Test Agent (TA)**: The combined instance of a CUT and a backchannel, instantiated as a single docker image.

## Test Script Guidelines

AATH test scripts are written in the [Gherkin](https://behave.readthedocs.io/en/latest/gherkin.html#gherkin-feature-testing-language) language, using the python [behave](https://behave.readthedocs.io/en/latest/) framework. Guidelines for writing test scripts are located [here](./TEST_DEV_GUIDE.md).

## Aries Agent Backchannels

Backchannels are the challenging part of the AATH. In order to participate in the interoperability testing, each CUT builder must create and maintain a backchannel that converts requests from the test harness into commands for the component under test. In some cases, that's relatively easy, such as with [Aries Cloud Agent - Python](https://github.com/hyperledger/aries-cloudagent-python). An ACA-Py controller uses an HTTP interface to control an ACA-Py instance, so the ACA-Py backchannel is "just another" ACA-Py controller. In other cases, it may be more difficult, calling for the component under test to be embedded into a web service.

We have created a proof-of-concept Test Agent to support manual testing with mobile agents, described [here](./MOBILE_AGENT_TESTING.md).

A further complication is that as tests are added to the test suite, the backchannel interface expands, requiring that backchannel maintainers extend their implementation to be able to run the new tests. Note that the test engine doesn't stop if the backchannel steps are not implemented, however, such tests will be marked as `fail`ing on test runs, usually with an HTTP `404` error.

### Implemented Backchannels

Backchannels can be found in the [`aries-backchannels`](aries-backchannels) folder of this repo. For more information on building a backchannel, see the documentation in the [`aries-backchannels` README](aries-backchannels/README.md), and look at the code of the existing backchannels. To get help in building a backchannel for a component you want tested, please use GitHub issues and/or ask questions on the [Hyperledger Chat](https://chat.hyperledger.org) `#aries-agent-test-harness` channel (free Linux Foundation account required).

Three backchannels have been implemented, for the [ACA-PY](https://github.com/hyperledger/aries-cloudagent-python), [AriesVCX](https://github.com/hyperledger/aries-vcx), [.NET](https://github.com/hyperledger/aries-framework-dotnet) and [JavaScript](https://github.com/hyperledger/aries-framework-javascript.git) Aries agent frameworks. The ACA-Py is built on a common Python base (./aries-backchannels/python/aries_backchannel.py) that sets up the backchannel API listener and performs some basic request validation and dispatching. On the other hand AriesVCX is build on their preferred language (Rust). The ACA-PY (./aries-backchannels/acapy/acapy_backchannel.py) and AriesVCX (./aries-backchannels/aries-vcx) implementations are good example to extend the base to add support for their respective agent frameworks.

There is also a backchannel to support (manual) testing with [mobile](./aries-backcgannels/mobile) agents. This backchannel doesn't control the mobile agent directly, rather it will prompt the tester to manually accept connection requests, credential offers etc. Use of the mobile backchannel is described [here](./MOBILE_AGENT_TESTING.md).

## The `manage` bash script

The AATH `./manage` script in the repo root folder is used to manage running builds of TA images and initiate test runs. Running the script with no arguments or just `help` to see the script's usage information. The following summarizes the key concepts.

`./manage` is a bash script, so you must be in a bash compatible shell to run the AATH. You must also have an operational docker installation and git installed. Pretty normal stuff for Aries Agent development. As well, the current AATH requires access to a running Indy network. A locally running instance of [VON-Network](https://github.com/bcgov/von-network) is one option, but you can also pass in environment variables for the LEDGER_URL, GENESIS_URL or GENESIS_FILE to use a remote network. For example `LEDGER_URL_CONFIG=http://test.bcovrin.vonx.io`

Before running tests, you must build the TA and harness docker images. Use `./manage build -a <TA>` to build the docker images for a TA, and the test harness itself. You may specify multiple `-a` parameters to build multiple TAs at the same time. Leaving off the `-a` option builds docker images for all of the TAs found in the repo. It takes a long time to run...

There are two options for testing [ACA-PY](https://github.com/hyperledger/aries-cloudagent-python) - you can build and run `acapy`, which builds the backchannel based on the latest released code, or you can build and run `acapy-main`, which builds the backchannel based on the latest version of the `main` branch. (Note that to build the backchannel based on a different repo/branch, edit [this file](https://github.com/hyperledger/aries-agent-test-harness/blob/main/aries-backchannels/acapy/requirements-main.txt) to specify the repo/branch you want to test, and then build/run `acapy-main`.)

To run the tests, use the `./manage run...` sub-command. the `run` command requires defining what TAs will be used for Acme (`-a <TA>`), Bob (`-b <TA>`) and Mallory (`-m <TA>`). To default all the agents to use a single component, use `-d <TA>`. Parameters are processed in order, so you can use `-d` to default the agents to one, and then use `-b` to use a different TA for Bob.

There are two ways to control the behave test engine's selection of test cases to run. First, you can specify one or more `-t <tag>` options to select the tests associated with specific tags. See the guidance on using tags with behave [here](https://behave.readthedocs.io/en/stable/behave.html#tag-expression). Note that each `-t` option is passed to behave as a `--tags <tag>` parameter, enabling control of the ANDs and ORs handling of tags. Specifically, each separate `-t` option is ANDed with the rest of the `-t` options. To OR tags, use a single `-t` option with commas (`,`) between the tags. For example, specify the options `-t @t1,@t2 -t @f1` means to use "tests tagged with `(t1 or t2) AND f1`." To get a full list of possible tags to use in this run command, use the `./manage tags` command.

> Note that the `<tag>` arguments passed in on the command line **cannot** have a space, even if you double-quote the tag or escape the space. This is because the args are going through multiple layers shells (the script, calling docker, calling a script in the docker instance that in turn calls behave...). In all that argument passing, the wrappers around the args get lost. That should be OK in most cases, but if it is a problem, we have the `-i` option as follows...

To enable full control over behave's behaviour (if you will...), the `-i <ini file>` option can be used to pass a behave "ini" format file into the test harness container. The ini file enables full control over the behave engine, add handles the shortcoming of not being able to pass tags arguments with spaces in them. See the behave configuration file options [here](https://behave.readthedocs.io/en/stable/behave.html#configuration-files). Note that the file name can be whatever you want. When it lands in the test harness container, it will be called `behave.ini`. There is a default ini file located in `aries-agent-test-harness/aries-test-harness/behave.ini`. This ini file is picked up and used by the test harness without the -i option. To run the tests with a custom behave ini file, follow this example,

```bash
./manage run -d acapy -t @AcceptanceTest -t ~@wip -i aries-test-harness/MyNewBehaveConfig.ini
```

For a full inventory of tests available to run, use the `./manage tests`. Note that tests in the list tagged @wip are works in progress and should generally not be run.

## Using AATH Agents as Services
You may have the need to utilize the agents and their controller/backchannels separately from running interop tests with them. This can be for debugging AATH test code, or for something outside of AATH, like Aries Mobile Test Harness (AMTH) tests. To assist in this requirement the manage script can start 1-n agents of any aries framework that exists in AATH. This is done as follows:

```
./manage start -a acapy-main
```
The command above will only start Acme as ACA-py. No other agents (Bob, Faber, etc.) will be started. 
```
LEDGER_URL_CONFIG=http://test.bcovrin.vonx.io TAILS_SERVER_URL_CONFIG=https://tails.vonx.io AGENT_CONFIG_FILE=/aries-backchannels/acapy/auto_issuer_config.yaml ./manage start -a afgo-interop -b acapy-main -n
```
The second command above, will start Acme as AFGO, and Bob as ACA-py, utilizing an external Ledger and Tails Server, with a custom configuration to start ACA-py with. It will also start ngrok which is usually needed for mobile testing in AMTH. 

To stop any agents started in this manner just run `./manage stop`.

### Use Cases
#### Debugging within AATH
When running test code in a debugger, you may not always want or need all the agents running when doing your debugging. Your test may only utilize Acme and Bob, and have no need for Faber and Mallory. This feature will allow you to start only the agents needed in your test you are debugging. The following example will run ACA-py as Acme and Bob with no other agents running. 
```
./manage start -a acapy-main -b acapy-main
```
#### Aries Mobile Test Harness
Aries Mobile Test Harness (AMTH) is a testing stack used to test mobile Aries wallets. To do this end to end, mobile tests need issuers, verifiers, and maybe mediators. Instead of AMTH managing a set of controllers and agents, AMTH can point to an Issuer or Verifier controller/agent URL. AMTH can take advantage of the work done across aries frameworks and backchannels to assign AATH agents as issuers or verifiers in testing aries wallets. For example, the BC Wallet tests in AMTH are utilizing ACA-py agents in AATH as an issuer and verifier. This is done by executing the following.
From within aries-agent-test-harness
```
./manage start -a acapy-main -b acapy-main
```
From within aries-mobile-test-harness
```
LEDGER_URL_CONFIG=http://test.bcovrin.vonx.io REGION=us-west-1 ./manage run -d SauceLabs -u <device-cloud-username> -k <device-cloud-access-key> -p iOS -a AriesBifold-114.ipa -i http://0.0.0.0:9020 -v http://0.0.0.0:9030 -t @bc_wallet -t @T001-Connect
```
The URLs for issuer and verifier are pointers to the backchannel controllers for Acme and Bob in AATH, so that these test take advantage of the work done there. 

## Extra Backchannel-Specific Parameters

You can pass backchannel-specific parameters as follows:

```bash
BACKCHANNEL_EXTRA_acapy_main="{\"wallet-type\":\"askar\"}" ./manage run -d acapy-main -t @AcceptanceTest -t ~@wip
```

The environment variable name is of the format `-<agent_name>`, where `<agent_name>` is the name of the agent (e.g. `acapy-main`) with hyphens replaced with underscores (i.e. `acapy_main`).

The contents of the environment variable are backchannel-specific. For aca-py it is a JSON structure containing parameters to use for agent startup.

The above example runs all the tests using the `askar` wallet type (vs `indy`, which is the default).

## Custom Configurations for Agents
  Alternatively to the Extra Backchannel-Specific Parameters above, you can also pass a configuration file through to your agent when it starts (only works if your agent is started by your backchannel). The AATH tests have a predefined set of options needed for the test flow to function properly so, adding this configuration to AATH test execution may have side effects causing the interop tests to fail. However, this is helpful when using the agents as services outside of AATH tests like with Mobile Wallet tests in Aries Mobile Test Harness, where the agents usually will benefit from having auto options turned on. You can pass through your config file using the environment variable AGENT_CONFIG_FILE as follows:
  ```
  LEDGER_URL_CONFIG=http://test.bcovrin.vonx.io TAILS_SERVER_URL_CONFIG=https://tails.vonx.io AGENT_CONFIG_FILE=/aries-backchannels/acapy/auto_issuer_config.yaml ./manage start -b acapy-main -n
  ```
The config file should live in the `aries-backchannels/<agent>` folder so it gets copied into the agent container automatically. Currently only the acapy backchannel supports this custom configuration in this manner. 

### Use Cases
#### Aries Mobile Test Harness
When using AATH agents as a service for AMTH, these agent services will need to be started with differet or extra parameters on the agents than AATH starts them with by default. Mobile test issuers and verifiers may need the auto parameters turned on, like `--auto-accept-requests`, `--auto-respond-credential-proposal`, etc. The only way to do this when using the AATH agents is through using this configuration file handling. There is an existing file in `aries-backchannels/acapy` called auto_isser_config.yaml that is there to support this requirement for the BC wallet. This works in BC Wallet as follows;
From within aries-agent-test-harness
```
LEDGER_URL_CONFIG=http://test.bcovrin.vonx.io TAILS_SERVER_URL_CONFIG=https://tails.vonx.io AGENT_CONFIG_FILE=/aries-backchannels/acapy/auto_issuer_config.yaml ./manage start -a acapy-main -b acapy-main -n
```
From within aries-mobile-test-harness
```
LEDGER_URL_CONFIG=http://test.bcovrin.vonx.io REGION=us-west-1 ./manage run -d SauceLabs -u <device-cloud-username> -k <device-cloud-access-key> -p iOS -a AriesBifold-114.ipa -i http://0.0.0.0:9020 -v http://0.0.0.0:9030 -t @bc_wallet -t @T001-Connect
```

## Test Tags

The test harness has utilized tags in the BDD feature files to be able to narrow down a test set to be executed at runtime. The general AATH tags currently utilized are as follows:

- @AcceptanceTest - Tests based on requirements specifically stated in the RFC.
- @DerivedFunctionalTest - Tests derived on requirements but not specifically stated in the RFC.
- @P1, @P2, @P3, @P4 - Test Priority.
- @NegativeTest - Test that attempts to break the software. ie. change workflow order, use invalid data, etc.
- @ExceptionTest - Tests that are based on requirements that suggest exception cases.
- @SmokeTest - Tests that can be used as a builds smoke or sanity tests.
- @NeedsReview - Tests that have not been reviewed or approved.
- @ReviewedApproved - Tests that have been reviewed and approved.
- @wip - Tests that are a work in progress and incomplete.
- @Done - Finished tests that are expected to Pass if executed against a Test Agent.
- @AIP10, @AIP20 - The Aries Interop Profile version for which the tests are written.
- @MobileTest - The test (likely) works when using the "mobile" Test Agent.
- @T01-AIP10-RFC0160 - Unique Test Identifiers.

Proposed Connection Protocol Tags

- @MultiUseInvite - Test utilizes a multi-use invite. Not using this tag and the test expects the invite to be single use.
- @SingleTryOnException
- @RetryableOnException

To get a list of all the tags in the current test suite, run the command: `./manage tags`

To get a list of the tests (scenarios) and the associated tags, run the command: `./manage tests`

### Running Tagged Tests

Using tags, one can just run Acceptance Tests...

```bash
./manage run -d acapy -t @AcceptanceTest
```

or all Priority 1 Acceptance Tests, but not the ones flagged Work In Progress...

```bash
./manage run -d acapy -t @P1 -t @AcceptanceTest -t ~@wip
```

or derived functional tests

```bash
./manage run -d acapy -t @DerivedFunctionalTest
```

or all the ExceptionTests...

```bash
./manage run -t @ExceptionTest
```

Using AND, OR in Test Execution Tags
Stringing tags together in one `-t` with commas as separators is equivalent to an `OR`. The separate `-t` options is equivalent to an `AND`.

```bash
./manage run -d acapy-main -t @RFC0453,@RFC0454 -t ~@wip -t ~@CredFormat_JSON-LD
```

So the command above will run tests from RFC0453 or RFC0454, without the wip tag, and without the CredFormat_JSON-LD tag.

To read more on how one can control the execution of test sets based on tags see the [behave documentation](https://behave.readthedocs.io/en/stable/tutorial.html#controlling-things-with-tags)

The option `-i <inifile>` can be used to pass a file in the `behave.ini` format into behave. With that, any behave configuration settings can be specified to control how behave behaves. See the behave documentation about the `behave.ini` configuration file [here](https://behave.readthedocs.io/en/stable/behave.html#configuration-files).

### Test Coverage

To read about what protocols and features from Aries Interop Profile 1.0, see the [Test Coverage Matrix](./TEST-COVERAGE.md).

### Test Reporting

For information on enhanced test reporting with the Aries Agent Test Harness, see [Advanced Test Reporting](./TEST_REPORTING.md).

## Adding Runsets

Runsets are GHA based workflows that automate the execution of your interop tests and reporting of the results.

These workflows are contained in the .github/workflows folder and must be named `test-harness-<name>.yml`.  Refer to the existing files for examples on how to create one specific to your use case.  In most cases you will be able to copy an existing file and change a few parameters.

Test execution is controlled by the [`test-harness-runner`](./.github/workflows/test-runner.yml).  This workflow will dynamically pick up and run any workflow conforming to the `test-harness-*.yml` naming convention.  Specific test harnesses can be excluded by adding their file name pattern to the `ignore_files_starts_with` list separated by a `,`.  The test harnesses are run by the **Run Test Harness** job which uses a throttled matrix strategy.  The number of concurrent test harness runs can be controlled by setting the `max-parallel` parameter to an appropriate number.
