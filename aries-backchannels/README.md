# Aries Backchannels

This folder contains the Aries backchannels that have been added to the Aries Agent Test Harness. As noted in the readme, backchannels receive requests from the test harness and convert those requests into instructions for the component under test (CUT).

> To Do: Reorganize to put each backchannel into a separate folder.

## Writing a new Backchannel

If you are writing a backchannel using Python, you're in luck!  Just use either the `ACA-Py` or `VCX` backchannels as a model.  They sub-class from a common base class, which implements the common backchannel features.

If you are implementing from scratch, you need to implement a backchannel which:

- implements the standard backchannel web service interface
- starts an instance of the component under test (CUT), and forwards commands from the test harness to the CUT

Once you have the backchannel, you need to define one or more docker files to create docker images of Test Agents to deploy in an AATH run. To do that, you must create:

- a Dockerfile that builds a Docker image for the Test Agent (TA), including the backchannel, the CUT and anything else needed to operate the TA
- the resulting docker image must be able to be launched by the common `./manage` bacsh script so the new TA can be included in the standard test scenarios

### 1. Standard Backchannel API

The test harness interacts with each backchannel using a standard set of web services, the url's are mapped here:

https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-backchannels/agent_backchannel.py#L157

... and you can see a full set of the expected parameters here:

https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-backchannels/agent_backchannel.py#L153

Additional protocols will be added in the future by extending the list of parameters with additional `topics`.

### 2. Backchannel/Agent Interaction

The test harness interacts with each published backchannel API using the following common functions:

https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-test-harness/agent_backchannel_client.py

### 3. Docker Build Script

Each backchannel should provide one or more Docker scripts that build a self-contained Docker image for the backchannel, the CUT and anything else needed to run the TA.

The following lists the requirements for building AATH compatible docker images:

- the Dockerfile for each Test Agent (TA) must be called `Dockerfile.<TA>`. For example `Dockerfile.acapy`, `Dockerfile.vcx`.
  - The `./manage` script uses the `<TA>` to validate command line arguments and for performing docker build and run operations.
  - A component may have multiple TA configurations and versions, each based on a different Dockerfile. Examples of that might be `Dockerfile.acapy-ws` (websockets setup) and `Dockerfile.acapy-0.5.1` (release 0.5.1 of ACA-Py).
  - TAs docker images are tagged and run based on their `<TA>` name.
- The Dockerfiles must be located in a predefined location in this repo, currently the `aries-backchannels` folder.
  - The `./manage` script looks for the scripts in that location.
- The TA docker image must include all of the processes needed to run the backchannel and the CUT. For example:
  - the VCX TA includes code to operate a VCX agency and its backchannel, which embeds the VCX agent framework.
  - the ACA-Py framework TA includes its backchannel and a release of ACA-Py.
- On startup, each TA has a range of four public (to the docker network) ports available to it.
  - The lowest port number is passed to the TA on startup and is used by the test harness to send HTTP requests to the running TA.
  - The next three higher ports are exposed across the docker network and can be used as needed by the TA.

Examples are provided for aca-py (`Dockerfile.acapy`) and VCX (`Dockerfile.vcx`).

### 4. `./manage` Script Integration

The manage script builds an image for each backchannel using the following command:

```bash
      docker build \
        ${args} \
        $(initDockerBuildArgs) \
        -t "${agent}-agent-backchannel" \
        -f "../aries-backchannels/Dockerfile.${agent}" "../aries-backchannels/"
```

where:

- `${agent}` is the name of the component under test (CUT)
- `$(initDockerBuildArgs)` picks up any HTTP_PROXY environment variables, and
- `${args}` are any extra arguments on the command line after standard options processing.

Once built, the selected TAs for the run are started for the test roles (Acme, Bob and Mallory) using the following commands:

```bash
  echo "Starting Acme Agent ..."
  docker run -d --rm --name acme_agent --expose 9020-9023 -p 9020-9023:9020-9023 -e "DOCKERHOST=${DOCKERHOST}" -e "LEDGER_URL=http://${DOCKERHOST}:9000" ${ACME_AGENT} -p 9020 -i false >/dev/null  
  echo "Starting Bob Agent ..."
  docker run -d --rm --name bob_agent --expose 9030-9033 -p 9030-9033:9030-9033 -e "DOCKERHOST=${DOCKERHOST}" -e "LEDGER_URL=http://${DOCKERHOST}:9000" ${BOB_AGENT} -p 9030 -i false >/dev/null
  echo "Starting Mallory Agent ..."
  docker run -d --rm --name mallory_agent --expose 9040-9043 -p 9040-9043:9040-9043 -e "DOCKERHOST=${DOCKERHOST}" -e "LEDGER_URL=http://${DOCKERHOST}:9000" ${MALLORY_AGENT} -p 9040  -i false >/dev/null
```

Important things to note from the script snippet:

- each backchannel is provided a range of public ports (the `-expose` parameter), which are mapped to localhost
- the binding of the TA (e.g. `acapy` or `vcx`, etc.) is done earlier in the script by setting the `${ACME_AGENT}` etc. environment variables
- environment variables provide the Docker host IP (`DOCKERHOST`) and a url to the ledger genesis transactions (`LEDGER_URL`)
  - the variables are defaulted if not already set, with the `LEDGER_URL` assumed to be for a locally running instance of  `von-network`
- parameters passed to the backchannel specify the base port number (`-p port`) and to use non-interactive mode (`-i false`)

## The ACA-Py and Indy Influence

Many of the BDD feature steps (and hence, backchannel requests) in the initial test cases map very closely to the ACA-Py "admin" API used by a controller to control an instance of an ACAP-Py agent. This makes sense because both the ACA-Py admin API and the AATH test cases were defined based on the Aries RFCs. However, we are aware the alignment between the two might be too close and welcome recommendations for making the backchannel API more agnostic, easier for other CUTs. Likewise, as the test suite becomes ledger- and verifiable credential format-agnostic, we anticipate abstracting away the Indy-isms that are in the current test cases, making them test parameters versus explicit steps.
