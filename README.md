[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

# Aries Agent Test Harness

This repository contains:

- A test framework, implemented using Behave, that can run RFC compliance tests across multiple Agents (with compatible backchannel adaptors)
- Sample backchannel adapters for ACA-PY and VCX Aries agents

The background for this test harness design is in the following Google doc:  https://docs.google.com/presentation/d/17iEhjs9xv3JRpcvXn6eu_12uEhOlwxyL_Tgt584wJmg/edit?usp=sharing

Note that this code is a Proof of Concept to illistrate this test harness approach, and to stimulate discussion.


## Aries Agent Backchannels

There are two sample backchannels in this repository, for the ACA-PY (https://github.com/hyperledger/aries-cloudagent-python) and VCX (https://github.com/hyperledger/indy-sdk/tree/master/vcx) Aries agents.

Both are built on a common set of base code (./aries-backchannels/aries_backchannel.py) that sets up the backchannel API listener and performs some basic request validation and dispatching.  The ACA-PY (./aries-backchannels/acapy_backchannel.py) and VCX (./aries-backchannels/vcx_backchannel.py) implementations extend this base to add support for their respective agents.


### Running the Backchannels using Docker

There is a single `manage` script that handles building and running the agents and test framework using Docker.

You must first start up a local set of Indy nodes - open up a bash shell and run the following commands:

```bash
git clone https://github.com/bcgov/vonnetwork.git
cd von-network
./manage build
./manage start --logs
```

Wait until the nodes are started and synchronized, you will see a message similar to the following:

```
webserver_1  | 2020-04-21 20:57:10,174|DEBUG|anchor.py|Finished resync
```

Open a separate bash shell and run the following:

```bash
git clone https://github.com/bcgov/aries-agent-test-harness.git
cd aries-agent-test-harness/docker
./manage build
./manage run
```

That's it!  Just sit back and enjoy the show, eventually you will see a test report showing how many of the tests passed and failed:

```
$ ./manage run
Starting Alice Agent ...
Starting Bob Agent ...
Starting Mallory Agent ...
Starting Victor Agent ...

waiting for Alice agent to start...
waiting for Bob agent to start...
waiting for Mallory agent to start
waiting for Victor agent to start......

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
    - Victor: Done
```

By default, the `Alice`, `Bob` and `Mallory` agents all run using aca-py.  (Another agent named `Victor` runs using VCX - `Victor` does not participate in any of the test scenarios, but shows how different agents can be implemented under a standard backchannel framework.)

To use a different agent for any of the test roles (`Alice`, `Bob` or `Mallory`) by specifying the agent type in an appropriate environment variable (`ALICE_AGENT`, `BOB_AGENT` or `MALLORY_AGENT`), for example:

```bash
BOB_AGENT=vcx-agent-backchannel ./manage run
```

... runs `Bob` using the VCX agent (`Alice` and `Mallory` run using the defauly agent, which is aca-py).


### Writing a new Backchannel for a new Agent

If you are writing a backchannel using Python, you're in luck!  Just use either the `aca-py` or `VCX` backchannels as a model.  They sub-class from a common base class, which implements the common backchannel features.

If you are implementing from scratch, you need to implement a backchannel which:

- implements the standard backchannel web service interface
- starts an agent instance, and forwards commands from the test harness to the agent
- provides a Docker script to build a Docker image for the backchannel (and agent)
- plugs into the common `./manage` script to allow the new backchannel/agent to be included in the standard test scenarios


#### 1. Standard Backchannel API

The test harness interacts with each backchannel using a standard set of web services, the url's are mapped here:

https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-backchannels/agent_backchannel.py#L190

... and you can see a full set of the expected parameters here:

https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-backchannels/agent_backchannel.py#L150

Additional protocols may be added in the future, but extending the list of parameters with additional `topics`.


#### 2. Backchannel/Agent Interaction

The test harness interacts with each published backchannel API using the following common functions:

https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-test-harness/agent_backchannel_client.py


#### 3. Docker Build Script

Each backchannel should provide a Docker script that builds a self-contained Docker image for the backchannel and agent.

Examples are provided for aca-py (`Dockerfile.acapy`) and VCX (`Dockerfile.vcx`).


#### 4. `./manage` Script Integration

The manage script builds an image for each backchannel:

https://github.com/bcgov/aries-agent-test-harness/blob/master/docker/manage#L119


... and the image is started using a standard set of parameters, for example for `Alice`:

```
docker run -d --rm --name alice_agent --expose 8020-8023 -p 8020-8023:8020-8023 -e "DOCKERHOST=${DOCKERHOST}" -e "LEDGER_URL=http://${DOCKERHOST}:9000" ${ALICE_AGENT} -p 8020 -i false >/dev/null  
```

Important things to note:

- each backchannel is provided a range of ports, which are mapped to localhost (aca-py and vcx each use 4 ports)
- environment variables provide the Docker host IP (`DOCKERHOST`) and a url to the ledger genesis transactions (`LEDGER_URL`)
- parameters are passed to the backchannel to specify the base port number (`-p port`) and to specify non-interactive mode (`-i false`)


### Running the Backchannels Locally (bare metal)

Note this is not recommended, however it may be desirable if you want to run outside of Docker containers.

To run each agent, install the appropriate pre-requisites (the VCX adapter requires a local install of indy-sdk and VCX) and then run as follows.

Setup - you need to run an Indy ledger and a ledger browser.  One way to run locally is to run the Indy ledger from the indy-sdk, and the browser from von-network.

In one shell, run the ledger (the nodes will be available on localhost):

```
git clone https://github.com/hyperledger/indy-sdk.git
cd indy-sdk
docker build -f ci/indy-pool.dockerfile -t indy_pool .
docker run -itd -p 9701-9708:9701-9708 indy_pool
```

(Note that you will need the indy-sdk to build the Indy and VCX libraries to run the VCX backchannel.)

... and in a second shell, run the ledger browser:

```
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

```
# install the pre-requisites:
cd aries-agent-test-harness/aries-backchannels
pip install -r requirements.txt
```

Note that this installs the aca-py and vcx python libraries from `ianco` forks of the gitub repositories.

```
cd aries-agent-test-harness/aries-backchannels
LEDGER_URL=http://localhost:9000 python acapy_backchannel.py -p 8020
```

`-p` specifies the backchannel port that the test harness will talk to.  The backchannel adaptor starts up an ACA-PY agent as a sub-process, and will use additional ports for communication between the adaptor and agent.  In general make sure there is a range of `10` free ports (i.e. in the example above reserve ports 8020 to 8029).

For VCX:

```
# install the pre-requisites:
cd aries-agent-test-harness/aries-backchannels
pip install -r requirements-vcx.txt
```

```
cd aries-agent-test-harness/aries-backchannels
LEDGER_URL=http://localhost:9000 python vcx_backchannel.py -p 8030
```

Note that you can run multiple instances of these agents.

Note also for VCX you need to install the Indy dependencies locally - libindy, libvcx, lubnulpay - and you also need to run a `dummy-cloud-agent` server.  You need to install these from `ianco`'s fork and branch of the indy-sdk:  https://github.com/ianco/indy-sdk/tree/vcx-aries-support

See the instructions in the indy-sdk for more details.

## Aries Test Framework

The test framework is implemented using Behave (https://behave.readthedocs.io/en/latest/index.html) and Python.

This test framework is in the "./aries-test-harness" folder.  The steps are implemented in Python and communicate to the agent backchannels using client functions in "./aries-test-harness/agent_backchannel_client.py"

To run the test harness:

```
# install the pre-requisites:
cd aries-agent-test-harness/aries-test-harness
pip install -r requirements.txt
```

```
cd aries-agent-test-harness/aries-test-harness
behave
```

The agents are configured in `behave.ini`.  

```
# -- FILE: behave.ini
[behave.userdata]
Alice = http://localhost:8020
Bob  = http://localhost:8070
```

If you want to run the tests using different agents, you can run:

```
behave -D Alice=http://localhost:8070 -D Bob=http://localhost:8020
```

This is the revers of the default configuration in `behave.ini`, and reverses the roles that the Alice and Bob agents will play in the test scenarios.

... or use any ports that you like!!!



