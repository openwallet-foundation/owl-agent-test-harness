# Mobile Agent (Manual) Testing

Aries Agent Test Harness includes the "mobile" Test Agent that supports the manual testing of some mobile agents.
The mobile Test Agent doesn't control the mobile app directly but rather prompts the user to interact with
the wallet app on their phone to scan a QR code to establish a connection, respond to a credential offer, etc.

Before executing a test run, you have to build the Test Agents you are going to use. For example, the following builds the "mobile" and "acapy-main" Test Agents:

```bash
./manage build -a mobile -a acapy-main
```

Remember to build any other Test Agents you are going to run with the mobile tests.

There are several options to the `./manage run` script that must be used when testing a mobile wallet:

- use the `-n` option tells the `./manage` script to start ngrok services for each agent (issuer, verifier) to provide the mobile app an Internet accessible endpoint for each of those agents
- use the `-b mobile` option to use the mobile Test Agent for the `Bob` role (the only one that makes sense for a mobile app)
- use the `-t @MobileTest` option to run only the tests that have been tagged as "working" with the mobile test agent
  - as new test scenarios are found to (or made to) work with the mobile Test Agent, the `@MobileTest` tag should be added to those test scenarios
  - currently, only AIP 1.0 tests using the Indy ledger work with the mobile Test Agent

Another requirement for using the mobile Test Agent is that you have to use an Indy ledger that is publicly accessible, does not have a
Transaction Author Agreement (TAA), and is "known" by the mobile wallet app you are testing. That generally means you must use the "BCovrin
Test" network. Also needed is a public Indy tails file for running revocation tests.

Before you run the tests, you have to have a mobile wallet to test (here are [some instructions for getting a mobile wallet app](https://vonx.io/getwallet)),
and if necessary, you must use the wallet app settings to use the "BCovrin Test" ledger.

Put together, that gives us the following command to test a mobile wallet with Aries Cloud Agent Python (main branch) running in all other roles.

```bash
LEDGER_URL_CONFIG=http://test.bcovrin.vonx.io TAILS_SERVER_URL_CONFIG=https://tails.vonx.io ./manage run -d acapy-main -b mobile -n -t @MobileTest
```

Want to test your mobile app with Aries Framework .NET? Make sure to build the `dotnet` Test Agent, and then run this command:

```bash
LEDGER_URL_CONFIG=http://test.bcovrin.vonx.io TAILS_SERVER_URL_CONFIG=https://tails.vonx.io ./manage run -d dotnet -b mobile -n -t @MobileTest
```

The mobile agent is in "proof-of-concept" status and some tests are not 100% reliable with all mobile agents. If things don't work, take a look at the
logs (in the `./logs` folder) to try to understand what went wrong.

You can try to run other test scenarios by adjusting the tags (`-t` options) you select when running tests, per [these instructions](./README.md#test-tags).
If you do find other test scenarios that work with the mobile Test Agent, please add an issue or PR to add the "@MobileTest" tag to the test scenario.

While this gives us one way to test mobile agent interoperability, it would be **really** nice to be able to run the mobile wallets without human intervention
so that we can include mobile wallets in the continuous integration testing. Those working on the Aries Agent Test Harness haven't looked into how that
could be done, so if you have any ideas, please let us know.

Another thing that would be nice to have supported is capturing the mobile wallet (brand and version) and test run results in a way that we could add the test run
to the https://aries-interop.info page. Do you have any ideas for that? Let us know!
