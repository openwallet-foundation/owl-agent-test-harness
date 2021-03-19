# Mobile Agent (Manual) Testing

There is a backchannel that supports manual testing of mobile agents - the backchannel doesn't control the mobile app directly but rather prompts the user to interact on their phone (scan QR code to establish a connection, respond to a credential offer, etc.).

There are two options that must be used when testing a mobile agent:

* `-n` option tells the `./manage` script to start ngrok services for each agent (issuer, verifier) to allow the mobile app to connect
* `-b mobile` will use the mobile backchannel for the `Bob` role (the only one that makes sense for a mobile app)

5 tests currently support mobile - these are tagged with `@MobileTest`, so for example all mobile tests can be run with one of the following commands:

```bash
LEDGER_URL_CONFIG=http://test.bcovrin.vonx.io TAILS_SERVER_URL_CONFIG=https://tails.vonx.io ./manage run -d acapy-main -b mobile -n -t @MobileTest
```

Or:

```bash
LEDGER_URL_CONFIG=http://test.bcovrin.vonx.io TAILS_SERVER_URL_CONFIG=https://tails.vonx.io ./manage run -d dotnet-master -b mobile -n -t @MobileTest
```

The first example will use the aca-py agent for all enterprise roles (issuer, verifier) and the second example will use the dotnet agent.

Note that this backchannel is in POC status and some tests are not 100% reliable with all mobile agents.
