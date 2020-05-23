# Backchannel Data Files

The data files in this folder can be used by the backchannel implementations as follows:

- The "local-genesis.txt" file is a genesis file that can be used for a locally running Indy sandbox.
  - If the Indy network used for testing is deployed some other way, such as via a local docker-based instance of [VON Network](https://github.com/bcgov/von-network) or a public Indy network with a VON Network-based ledger browser, the genesis file will likely be retrieved in some other way, such as via an HTTP request to a web service. Likewise, if a Sovrin ledger is being used for the testing, the genesis file can be pulled from github.

- The [backchannel_operations.csv] file is a list of operations that the test suite developers have defined in the test cases. The file can be loaded by backchannel to provide a list of the operations needed to be supported by the backchannel. This list is expanded as the number of tests cases evolves, and new operations are defined. The source of the data is this [Google Sheet of Test Operations](https://bit.ly/AriesTestHarnessScenarios). Test case developers periodically download a CSV of the Google Sheet and run it through a script to generate the CSV file in this folder.

An example of the use of the `backchannel_operations.cv` file can be found in the Python [agent backchannel](https://github.com/bcgov/aries-agent-test-harness/blob/958ff843b7ebc2ab392eee06b5d7c4ec27ba5dc3/aries-backchannels/python/agent_backchannel.py#L153) script.
