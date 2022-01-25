# Backchannel Data Files

The data files in this folder can be used by the backchannel implementations as follows:

- The "local-genesis.txt" file is a genesis file that can be used for a locally running Indy sandbox.
  - If the Indy network used for testing is deployed some other way, such as via a local docker-based instance of [VON Network](https://github.com/bcgov/von-network) or a public Indy network with a VON Network-based ledger browser, the genesis file will likely be retrieved in some other way, such as via an HTTP request to a web service. Likewise, if a Sovrin ledger is being used for the testing, the genesis file can be pulled from github.
