# Aries Agent Test Harness Quick Start Guide

This guide quickly gets the Aca-py Agent BDD tests up and running. It utilizes separate docker containers for the Indy Ledger and Ledger Browser, the ACA-PY agents and backchannels, and the test harness itself. 

### Prerequisites
- Docker is installed and working on the host machine.
- git is install and working with a github account.

## Run the Ledger and Ledger Browser
In one shell...
```
git clone https://github.com/hyperledger/indy-sdk.git
git clone https://github.com/bcgov/von-network
cd von-network
./manage build
./manage start --logs
```

# Determine the Ledger Browser IP to use in the URL for the Aca-py Agent in the next section
in another shell...
Make sure there is a von_von network
```
docker network ls
```
Find the Gateway IP and record it. For example in this guide it is 172.18.0.1
```
docker network inspect von_von | grep Gateway
```

## Run an ACA-PY Agent and Backchannel (one container per agent)
In another shell...
```
git clone https://github.com/bcgov/aries-agent-test-harness.git
cd aries-agent-test-harness/aries-backchannels
docker build -t acapy-agent-backchannel .
docker run -it --name alice_agent --expose 8020-8023 -p 8020-8023:8020-8023 -e “LEDGER_URL=http://172.18.0.1:9000” acapy-agent-backchannel -p 8020
```
To run another ACA-PY Agent in another container, open another shell...
```
docker run -it --name bob_agent --expose 8030-8033 -p 8030-8033:8030-8033 -e “LEDGER_URL=http://172.18.0.1:9000” acapy-agent-backchannel -p 8030
```
Run another ACA-PY Agent in another container, open another shell...
```
docker run -it --name mallory_agent --expose 8040-8043 -p 8040-8043:8040-8043 -e “LEDGER_URL=http://172.18.0.1:9000” acapy-agent-backchannel -p 8040
```

More agents can be started by making sure the posts are exposed and assigned to the agent properly in the command. The next Agent in this sequence should get a port of 8050, the Agent Startup routine will have the agent listening for the backshannel on port 8050, listening to web_hooks on 8023, and have the agent admin on port 8052. The startup command would look like this:
```
docker run -it --name frank_agent --expose 8050-8053 -p 8050-8053:8050-8053 -e “LEDGER_URL=http://172.18.0.1:9000” acapy-agent-backchannel -p 8050
```

## Run the Aries Agent Tests
In another shell...
```
cd aries-test-harness
docker build -t aries-agent-tests .  
docker run -it --network="host" aries-agent-tests -k -D Alice=http://0.0.0.0:8020 -D Bob=http://0.0.0.0:8030 -D Mallory=http://0.0.0.0:8040
```
The above will run all tests for all features. 

Read Test Tags Below for in use and proposed test sceanrio tags

Using tags, one can just run Acceptance Tests...
```
docker run -it --network="host" aries-agent-tests -k --tags=AcceptanceTest -D Alice=http://0.0.0.0:8020 -D Bob=http://0.0.0.0:8030 -D Mallory=http://0.0.0.0:8040
```
or all Priority 1 Acceptance Tests...
```
docker run -it --network="host" aries-agent-tests -k --tags=@P1 --tags=@AcceptanceTest -D Alice=http://0.0.0.0:8020 -D Bob=http://0.0.0.0:8030 -D Mallory=http://0.0.0.0:8040
```
Or derived functional tests
```
docker run -it --network="host" aries-agent-tests -k --tags=DerivedFunctionalTest -D Alice=http://0.0.0.0:8020 -D Bob=http://0.0.0.0:8030 -D Mallory=http://0.0.0.0:8040
```
Or all the ExceptionTests...
```
docker run -it --network="host" aries-agent-tests -k --tags=ExceptionTest -D Alice=http://0.0.0.0:8020 -D Bob=http://0.0.0.0:8030 -D Mallory=http://0.0.0.0:8040
```

To read more on how one can control the execution of test sets based on tags see https://behave.readthedocs.io/en/latest/tutorial.html#controlling-things-with-tags

At the command line, anywhere after the image name of aries-agent-tests any of the regular behave arguments can be specified to control how behave behaves. https://behave.readthedocs.io/en/latest/behave.html


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

Proprosed Connecton Protocol Tags
- @MultiUseInvite - Test utilizes a multi-use invite. Not using this tag and the test expects the invite to be single use.
- @SingleTryOnException
- @RetryableOnException