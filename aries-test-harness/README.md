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
Acme = http://localhost:8020
Bob  = http://localhost:8070
```
