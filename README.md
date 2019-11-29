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
cd aries-agent-test-harness/aries-backchannels
LEDGER_URL=http://localhost:9000 python acapy_backchannel.py -p 8020
```

`-p` specifies the backchannel port that the test harness will talk to.  The backchannel adaptor starts up an ACA-PY agent as a sub-process, and will use additional ports for communication between the adaptor and agent.  In general make sure there is a range of `10` free ports (i.e. in the example above reserve ports 8020 to 8029).

For VCX:

```
cd aries-agent-test-harness/aries-backchannels
LEDGER_URL=http://localhost:9000 python vcx_backchannel.py -p 8030
```

Note that you can run multiple instances of these agents.

Note also for VCX you need to install the Indy dependencies locally - libindy, libvcx, lubnulpay - and you also need to run a `dummy-cloud-agent` server.  See the instructions in the indy-sdk for more details.

## Aries Test Framework

The test framework is implemented using Behave (https://behave.readthedocs.io/en/latest/index.html) and Python.

This test framework is in the "./aries-test-harness" folder.  The steps are implemented in Python and communicate to the agent backchannels using client functions in "./aries-test-harness/agent_backchannel_client.py"

To run the test harness:

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



