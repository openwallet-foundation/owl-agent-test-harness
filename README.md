[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

# Aries Agent Test Harness<!-- omit in toc -->

This repository contains:

- A test framework, implemented using Behave, that can run RFC compliance tests across multiple Agents (with compatible backchannel adaptors)
- Backchannel adapters for the ACA-PY and VCX Aries agent frameworks.

The background for this test harness design is in the following Google doc:  https://docs.google.com/presentation/d/17iEhjs9xv3JRpcvXn6eu_12uEhOlwxyL_Tgt584wJmg/edit?usp=sharing

Note that this code is in active development.

## Contents<!-- omit in toc -->

- [Aries Agent Backchannels](#aries-agent-backchannels)
- [Running the Backchannels using Docker](#running-the-backchannels-using-docker)
- [Test Tags](#test-tags)
  - [Running Tagged Tests](#running-tagged-tests)
- [Writing a new Backchannel for a new Agent](#writing-a-new-backchannel-for-a-new-agent)
  - [1. Standard Backchannel API](#1-standard-backchannel-api)
  - [2. Backchannel/Agent Interaction](#2-backchannelagent-interaction)
  - [3. Docker Build Script](#3-docker-build-script)
  - [4. `./manage` Script Integration](#4-manage-script-integration)
- [Behave in the Aries Test Framework](#behave-in-the-aries-test-framework)
- [Running Locally (Bare Metal) - NOT RECOMMENDED](#running-locally-bare-metal---not-recommended)

## Aries Agent Backchannels

There are two backchannels in this repository, for the ACA-PY (https://github.com/hyperledger/aries-cloudagent-python) and VCX (https://github.com/hyperledger/indy-sdk/tree/master/vcx) Aries agents.

Both are built on a common base (./aries-backchannels/aries_backchannel.py) that sets up the backchannel API listener and performs some basic request validation and dispatching.  The ACA-PY (./aries-backchannels/acapy_backchannel.py) and VCX (./aries-backchannels/vcx_backchannel.py) implementations extend this base to add support for their respective agent
frameworks.

## Running the Backchannels using Docker

Prerequisites for running the test harness are:

- a terminal app running the `bash` shell
- Docker, installed and working
- git installed and working with github

There is a single `manage` script that handles building and running the agents and test framework using Docker.

You must first start up a local set of Indy nodes - open up a bash shell and run the following commands:

```bash
git clone https://github.com/bcgov/von-network.git
cd von-network
./manage build
./manage start --logs
```

Wait until the nodes are started and synchronized, you will see a message similar to the following:

```bash
webserver_1  | 2020-04-21 20:57:10,174|DEBUG|anchor.py|Finished resync
```

Now, open a separate bash shell to run the test harness and backchannel(s).  Run the following:

```bash
git clone https://github.com/bcgov/aries-agent-test-harness.git
cd aries-agent-test-harness/docker
./manage build
./manage run -d acapy
```

That's it!  Just sit back and enjoy the show, eventually you will see a test report showing how many of the tests passed and failed:

```bash
$ ./manage run
Starting Alice Agent ...
Starting Bob Agent ...
Starting Mallory Agent ...

waiting for Alice agent to start...
waiting for Bob agent to start...
waiting for Mallory agent to start

...

Failing scenarios:
  features/0160-connection.feature:3  establish a connection between two agents OLD
  features/0160-connection.feature:39  Connection established between two agents and inviter gets a preceding message -- @1.1 
  features/0160-connection.feature:40  Connection established between two agents and inviter gets a preceding message -- @1.2 
  features/0160-connection.feature:59  Inviter Sends invitation for one agent second agent tries during first share phase
  features/0160-connection.feature:72  Inviter Sends invitation for multiple agents
  features/0160-connection.feature:86  Establish a connection between two agents who already have a connection initiated from invitee

1 feature passed, 1 failed, 0 skipped
4 scenarios passed, 6 failed, 0 skipped
45 steps passed, 5 failed, 15 skipped, 1 undefined
Took 0m22.558s

You can implement step definitions for undefined steps with these snippets:

@when(u'"Alice" accepts the connection request')
def step_impl(context):
    raise NotImplementedError(u'STEP: When "Alice" accepts the connection request')


Cleanup:
  - Shutting down agents ...
    - Alice: Done
    - Bob: Done
    - Mallory: Done
```

For the run above, the `Alice`, `Bob` and `Mallory` agents are all running with the ACA-Py backchannels and agent frameworks. Use the "-a" (for Alice), "-b" (for Bob) and "-m" (for Mallory) to mix and match the agents. Run `./manage help` to see the command usage information.

For example:

```bash
./manage run -a acapy -b vcx -m acapy
```

... runs `Bob` using the VCX agent framework, while `Alice` and `Mallory` run the ACA-PY agent framework.

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

### Running Tagged Tests

Using tags, one can just run Acceptance Tests...

``` bash
./manage run -d acapy -t @AcceptanceTest
```

or all Priority 1 Acceptance Tests...

``` bash
./manage run -d acapy -t @P1 -t @AcceptanceTest
```

or derived functional tests

``` bash
./manage run -d acapy -t @DerivedFunctionalTest
```

or all the ExceptionTests...

``` bash
./manage run -t @ExceptionTest
```

To read more on how one can control the execution of test sets based on tags see [https://behave.readthedocs.io/en/latest/tutorial.html#controlling-things-with-tags](https://behave.readthedocs.io/en/latest/tutorial.html#controlling-things-with-tags)

At the command line, any of the regular behave arguments can be specified to control how behave behaves. [https://behave.readthedocs.io/en/latest/behave.html]
(https://behave.readthedocs.io/en/latest/behave.html)

## Writing a new Backchannel for a new Agent

If you are writing a backchannel using Python, you're in luck!  Just use either the `ACA-Py` or `VCX` backchannels as a model.  They sub-class from a common base class, which implements the common backchannel features.

If you are implementing from scratch, you need to implement a backchannel which:

- implements the standard backchannel web service interface
- starts an agent instance, and forwards commands from the test harness to the agent
- provides a Docker script to build a Docker image for the backchannel (and agent)
- plugs into the common `./manage` script to allow the new backchannel/agent to be included in the standard test scenarios

### 1. Standard Backchannel API

The test harness interacts with each backchannel using a standard set of web services, the url's are mapped here:

https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-backchannels/agent_backchannel.py#L190

... and you can see a full set of the expected parameters here:

https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-backchannels/agent_backchannel.py#L150

Additional protocols may be added in the future, by extending the list of parameters with additional `topics`.

### 2. Backchannel/Agent Interaction

The test harness interacts with each published backchannel API using the following common functions:

https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-test-harness/agent_backchannel_client.py

### 3. Docker Build Script

Each backchannel should provide a Docker script that builds a self-contained Docker image for the backchannel and agent.

Examples are provided for aca-py (`Dockerfile.acapy`) and VCX (`Dockerfile.vcx`).

### 4. `./manage` Script Integration

The manage script builds an image for each backchannel:

https://github.com/bcgov/aries-agent-test-harness/blob/master/docker/manage#L120


... and the image is started using a standard set of parameters, for example for `Alice`:

```
docker run -d --rm --name alice_agent --expose 8020-8023 -p 8020-8023:8020-8023 -e "DOCKERHOST=${DOCKERHOST}" -e "LEDGER_URL=http://${DOCKERHOST}:9000" ${ALICE_AGENT} -p 8020 -i false >/dev/null  
```

Important things to note:

- each backchannel is provided a range of ports, which are mapped to localhost (aca-py and vcx each use 4 ports)
- environment variables provide the Docker host IP (`DOCKERHOST`) and a url to the ledger genesis transactions (`LEDGER_URL`)
- parameters are passed to the backchannel to specify the base port number (`-p port`) and to specify non-interactive mode (`-i false`)

## Behave in the Aries Test Framework

The test framework is implemented using Behave (https://behave.readthedocs.io/en/latest/index.html) and Python.

This test framework is in the "./aries-test-harness" folder.  The steps are implemented in Python and communicate to the agent backchannels using client functions in "./aries-test-harness/agent_backchannel_client.py"

To run the test harness:

```bash
# install the pre-requisites:
cd aries-agent-test-harness/aries-test-harness
pip install -r requirements.txt
```

```bash
cd aries-agent-test-harness/aries-test-harness
behave
```

The agents are configured in `behave.ini`.  

```bash
# -- FILE: behave.ini
[behave.userdata]
Alice = http://localhost:8020
Bob  = http://localhost:8070
```

## Running Locally (Bare Metal) - NOT RECOMMENDED

Note this is **not** recommended, however it may be desirable if you want to run outside of Docker containers. While this repo is in early iteration, we can only provide limited support in using this.

> We would **FAR** prefer help in being able in documenting the use of a debugger with the docker containers vs. documentation on running the test harness on bare-metal.

To run each agent, install the appropriate pre-requisites (the VCX adapter requires a local install of indy-sdk and VCX) and then run as follows.

Setup - you need to run an Indy ledger and a ledger browser.  One way to run locally is to run the Indy ledger from the indy-sdk, and the browser from von-network.

In one shell, run the ledger (the nodes will be available on localhost):

```bash
git clone https://github.com/hyperledger/indy-sdk.git
cd indy-sdk
docker build -f ci/indy-pool.dockerfile -t indy_pool .
docker run -itd -p 9701-9708:9701-9708 indy_pool
```

(Note that you will need the indy-sdk to build the Indy and VCX libraries to run the VCX backchannel.)

... and in a second shell, run the ledger browser:

```bash
git clone https://github.com/bcgov/von-network.git
cd von-network
# run a python virtual environment
virtualenv venv
source ./venv/bin/activate
# install the pre-requisites and then run the ledger browser
pip install -r server/requirements.txt
GENESIS_FILE=<your path>/aries-agent-test-harness/aries-backchannels/local-genesis.txt REGISTER_NEW_DIDS=true PORT=9000 python -m server.server
```

You will open additional shells to run the agents.

For ACA-PY:

```bash
# install the pre-requisites:
cd aries-agent-test-harness/aries-backchannels
pip install -r requirements.txt
```

Note that this installs the aca-py and vcx python libraries from `ianco` forks of the gitub repositories.

```bash
cd aries-agent-test-harness/aries-backchannels
LEDGER_URL=http://localhost:9000 python acapy_backchannel.py -p 8020
```

`-p` specifies the backchannel port that the test harness will talk to.  The backchannel adaptor starts up an ACA-PY agent as a sub-process, and will use additional ports for communication between the adaptor and agent.  In general make sure there is a range of `10` free ports (i.e. in the example above reserve ports 8020 to 8029).

For VCX:

``` bash
# install the pre-requisites:
cd aries-agent-test-harness/aries-backchannels
pip install -r requirements-vcx.txt
```

``` bash
cd aries-agent-test-harness/aries-backchannels
LEDGER_URL=http://localhost:9000 python vcx_backchannel.py -p 8030
```

Note that you can run multiple instances of these agents.

Note also for VCX you need to install the Indy dependencies locally - libindy, libvcx, lubnulpay - and you also need to run a `dummy-cloud-agent` server.  You need to install these from `ianco`'s fork and branch of the indy-sdk:  https://github.com/ianco/indy-sdk/tree/vcx-aries-support

See the instructions in the indy-sdk for more details.
