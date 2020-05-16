# Aries Backchannels

This folder contains the Aries backchannels that have been added to the Aries Agent Test Harness, each in their own folder. As noted in the main repo readme, backchannels receive requests from the test harness and convert those requests into instructions for the component under test (CUT). Within backchannel folders there may be more than one Dockerfile to build a different Test Agents sharing a single backchannel, perhaps for different versions of the CUT or different configurations.

## Writing a new Backchannel

If you are writing a backchannel using Python, you're in luck!  Just use either the `ACA-Py` or `VCX` backchannels as a model.  They sub-class from a common base class (in the `python` folder), which implements the common backchannel features. The Python implementation is data driven, using the txt file in the `data` folder.

If you are implementing from scratch, you need to implement a backchannel which:

- implements the standard backchannel web service interface (which is very simple) and all of the test step protocols (called topics), of which there are a fair number
- starts an instance of the component under test (CUT), and
- converts the requests from test harness into directives understood by the CUT

Once you have the backchannel, you need to define one or more docker files to create docker images of Test Agents to deploy in an AATH run. To do that, you must create a Dockerfile that builds a Docker image for the Test Agent (TA), including the backchannel, the CUT and anything else needed to operate the TA. The resulting docker image must be able to be launched by the common `./manage` bash script so the new TA can be included in the standard test scenarios.

### 1. Standard Backchannel API

The test harness interacts with each backchannel using a standard set of web services, the url's are mapped here:

https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-backchannels/python/agent_backchannel.py#L157

... and you can see a full set of the expected parameters here:

https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-backchannels/python/agent_backchannel.py#L153

Additional protocols will be added in the future by extending the list of parameters with additional `topics`.

A backchannel should be implemented to always return a `404` HTTP result for topics not handled by the backchannel, so that it is easy to separate errors in the CUT vs. test steps not yet implemented by the backchannel.

### 2. Backchannel/Agent Interaction

The test harness interacts with each published backchannel API using the following common functions:

https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-test-harness/agent_backchannel_client.py

### 3. Docker Build Script

Each backchannel should provide one or more Docker scripts that build a self-contained Docker image for the backchannel, the CUT and anything else needed to run the TA.

The following lists the requirements for building AATH compatible docker images:

- the Dockerfile for each Test Agent (TA) must be called `Dockerfile.<TA>`. For example `Dockerfile.acapy`, `Dockerfile.vcx`.
  - The `./manage` script uses the `<TA>` to validate command line arguments, to tag the agent, and for invoking docker build and run operations.
  - A backchannel may have multiple TA configurations and versions, each based on a different Dockerfile.
    - See the `acapy` backchannel where there the `Dockerfile.acapy` builds the latest released version of ACA-Py, where `Dockerfile.acapy-master` builds from the ACA-Py `master` branch.
  - TAs docker images are tagged with their `<TA>` name.
- The Dockerfiles must be located in a predefined location in this repo, currently in folders in the `aries-backchannels` folder.
  - The `./manage` script looks for the TA Dockerfiles in those folders.
- A TA docker image must include all of the processes needed to run the backchannel and the CUT. For example:
  - the VCX TA includes its backchannel, which embeds the VCX agent framework and the code to operate the VCX "dummy" agency.
  - the ACA-Py framework TA includes its backchannel and an appropriate release of ACA-Py.
- On startup, each TA has a range of ten public (to the docker network) ports available to it.
  - The lowest port number is passed to the TA on startup and is used by the test harness to send HTTP requests to the running TA.
  - The next nine higher ports are exposed across the docker network and can be used as needed by the TA.

Examples are provided for aca-py (`Dockerfile.acapy`) and VCX (`Dockerfile.vcx`).

### 4. `./manage` Script Integration

The `./manage` script builds an image for each backchannel using the following command:

```bash
      echo "Building ${agent}-agent-backchannel ..."
      docker build \
        ${args} \
        $(initDockerBuildArgs) \
        -t "${agent}-agent-backchannel" \
        -f "${BACKCHANNEL_FOLDER}/Dockerfile.${agent}" "aries-backchannels/"
```

where:

- `${agent}` is the name of the component under test (CUT)
- `$(initDockerBuildArgs)` picks up any HTTP_PROXY environment variables, and
- `${args}` are any extra arguments on the command line after standard options processing.
- Note that the docker build context is the aries-backchannel folder&mdash;the folder above the backchannel folders

Once built, the selected TAs for the run are started for the test roles (Acme, Bob and Mallory) using the following commands:

```bash
  echo "Starting Acme Agent ..."
  docker run -d --rm --name acme_agent --expose 9020-9029 -p 9020-9029:9020-9029 -e "DOCKERHOST=${DOCKERHOST}" -e "LEDGER_URL=http://${DOCKERHOST}:9000" ${ACME_AGENT} -p 9020 -i false >/dev/null  
  echo "Starting Bob Agent ..."
  docker run -d --rm --name bob_agent --expose 9030-9039 -p 9030-9039:9030-9039 -e "DOCKERHOST=${DOCKERHOST}" -e "LEDGER_URL=http://${DOCKERHOST}:9000" ${BOB_AGENT} -p 9030 -i false >/dev/null
  echo "Starting Mallory Agent ..."
  docker run -d --rm --name mallory_agent --expose 9040-9049 -p 9040-9049:9040-9049 -e "DOCKERHOST=${DOCKERHOST}" -e "LEDGER_URL=http://${DOCKERHOST}:9000" ${MALLORY_AGENT} -p 9040  -i false >/dev/null
```

Important things to note from the script snippet:

- each backchannel is provided a range of public ports (the `-expose` parameter), which are mapped to localhost
  - the backchannel must allocate the ports at runtime based on the `-p` parameter, and not hard code them in the container.
- the binding of the TA (e.g. `acapy` or `vcx`, etc.) is done earlier in the script by setting the `${ACME_AGENT}` etc. environment variables
- environment variables provide the Docker host IP (`DOCKERHOST`) and a url to the ledger genesis transactions (`LEDGER_URL`)
  - the variables are defaulted if not already set, with the `LEDGER_URL` assumed to be for a locally running instance of  `von-network`
- parameters passed to the backchannel specify the base port number (`-p port`) and to use non-interactive mode (`-i false`)

## The ACA-Py and Indy Influence

Many of the BDD feature steps (and hence, backchannel requests) in the initial test cases map very closely to the ACA-Py "admin" API used by a controller to control an instance of an ACA-Py agent. This makes sense because both the ACA-Py admin API and the AATH test cases were defined based on the Aries RFCs. However, we are aware the alignment between the two might be too close and welcome recommendations for making the backchannel API more agnostic, easier for other CUTs. Likewise, as the test suite becomes ledger- and verifiable credential format-agnostic, we anticipate abstracting away the Indy-isms that are in the current test cases, making them test parameters versus explicit steps.
