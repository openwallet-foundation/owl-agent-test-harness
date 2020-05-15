## Running Locally (Bare Metal) - NOT RECOMMENDED

Note this is **not** recommended, however it may be desirable if you want to run outside of Docker containers. While this repo is in early iteration, we can only provide limited support in using this. These instructions cover what was done in initially setting up the ACA-Py and VCX backchannels before they were standardized. As such, they are included for historical purposes only, and may or may not still be accurate.

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

Open additional shells to run the agents.

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

Note also for VCX you need to install the Indy dependencies locally - libindy, libvcx, libnulpay - and you also need to run a `dummy-cloud-agent` server.  You need to install these from `ianco`'s fork and branch of the indy-sdk:  https://github.com/ianco/indy-sdk/tree/vcx-aries-support

See the instructions in the indy-sdk for more details.
