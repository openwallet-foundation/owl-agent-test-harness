# Remote Agent Testing in OATH

OWL Agent Test Harness is a powerful tool for running verifiable credential and decentralized identity interoperability tests. It supports a variety of agent configurations, including running agents locally that are test harness managed, or remotely, unmanaged by the test harness. This guide covers the **remote** option, allowing you to execute interoperability tests with agents running on remote servers in development, test, staging, or production environments, communicating with other remote agents or test harness managed agents.

## Prerequisites

Before using the `remote` option, make sure you have:

- A running remote instance of an agent you want to connect to and test with.
- The agent(s) controller has implemented the test api (backchannel api) for the protocols desired to be tested.
- OATH is cloned and set up locally or on a machine with network access to your remote agent(s).
- The remote agent(s) are configured with the same ledgers or tails server that OATH is configured with.
- Valid configuration URLs for remote agents, including public endpoints to the test api in the agent controller.

## Command Structure

When running the test harness with remote agents, the basic command structure for setting remote agents is as follows:

```bash
./manage run -a remote --aep <acme_endpoint> -b remote --bep <bob_endpoint> -f remote --fep <faber_endpoint> -m remote --mep <mallory_endpoint> 
```

For any of the agent flags, `-a`, `-b`, `-f`, `-m`, if the agent is set to `remote` then the test harness will look for the long option of `--aep`, `--bep`, `--fep`, and `-mep` for the endpoint of that particular remote agent. 

#### Long Options for Remote Endpoints

- --aep: ACME agent’s remote endpoint URL (e.g., http://remote-acme.com).
- --bep: BOB agent’s remote endpoint URL.
- --fep: FABER agent’s remote endpoint URL.
- --mep: MALLORY agent’s remote endpoint URL.

#### Example Command
```bash
LEDGER_URL_CONFIG=http://test.bcovrin.vonx.io \
TAILS_SERVER_URL_CONFIG=https://tails.vonx.io \
./manage run \
  -a remote --aep http://remote-acme.com \
  -b acapy-main -f acapy-main -m acapy-main \
  -t @T002-RFC0160
```
This example command will test a remote agent in the role if Acme, an issuer/verifier in conjuction with test harness managed acapy agents playing the other roles of Bob, Faber, and Mallory.

Any combination of remote and test harness managed agents is testable, including all remote if one is so inclined.

#### Local Example

To verify and see the remote implementation in the test harness working locally, you will need to run one of the test harness agents outside of the OATH docker network. Then use that agent as a remote agent. 

Build the local agents:
```bash
./manage build -a acapy-main
```

Run a remote agent locally:
```bash
docker run -dt --name "fred_agent" --expose "9030-9039" -p "9030-9039:9030-9039" -v  <location_of_test_harness>/aries-backchannels/acapy/.build/acapy-main.data:/data-mount:z --env-file=aries-backchannels/acapy/acapy-main.env -e AGENT_NAME=Fred -e LEDGER_URL=http://test.bcovrin.vonx.io -e TAILS_SERVER_URL=https://tails.vonx.io -e DOCKERHOST=host.docker.internal -e CONTAINER_NAME=fred_agent "acapy-main-agent-backchannel" -p "9031" -i false
```

Run the tests:
```bash
LEDGER_URL_CONFIG=http://test.bcovrin.vonx.io TAILS_SERVER_URL_CONFIG=https://tails.vonx.io ./manage run -a acapy-main -b remote --bep http://0.0.0.0:9031 -f acapy-main -m acapy-main -t @T002-RFC0160
```

#### Handling Errors

If you encounter any issues while using the remote option, check the following:

- Endpoint URLs and Ports: Ensure the URLs and ports specified are correct and accessible from your local machine or environment the test harness is running in.
- Agent Configuration: Make sure the agents on the remote server are properly configured and running.
- Logs: Check the remote agents log in conjuction with the other agents logs for hints on what could be causing the errors. 

## Conclusion

The remote option in the Test Harness allows you to test verifiable credential interactions with agents running in remote environments. This flexibility essentially allows you to verify that your agent(s) can successfully interop with other agents for the implemented protocols. 

For any extra troubleshooting please consult with the [OWL maintainers on Discord](https://discord.com/channels/1022962884864643214/1214965981470924911).