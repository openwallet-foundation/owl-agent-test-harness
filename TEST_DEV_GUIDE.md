# Test Development Guidelines<!-- omit in toc -->

## Contents<!-- omit in toc -->

- [Writing Tests in Gherkin](#writing-tests-in-gherkin)
- [Using Tags](#using-tags)
- [Defining Backchannel Commands](#defining-backchannel-commands)
- [Implementing Test Steps](#implementing-test-steps)
- [Implementing the Backchannel](#implementing-the-backchannel)

## Writing Tests in Gherkin

The Aries Agent Test Harness utilizes a behavioural driven approach to testing. The Python toolset [Behave](https://behave.readthedocs.io/en/latest/index.html) is used to actualize this approach. [Gherkin] is the language syntax used to define test preconditions and context, actions and events, and expected results and outcomes. 

The first step in developing a suite of tests for the Aries Interop Protocols is to write plain english Gherkin definitions, before any code is written. The priority is to do "happy path" type tests first, leaving the exception & negative testing till there are multiple suites across protocols of happy path acceptance tests. Write one main scenario then get peers and others firmiliar with the RFC to review the test. This is important because the structure and language of this initial test may guide the rest of the tests in the suite. 

Intitial writing of the Gherkin tests themselves can be done in a [.feature file](https://behave.readthedocs.io/en/latest/tutorial.html?highlight=feature%20file#features) or in the [GitHub issue](https://github.com/bcgov/aries-agent-test-harness/issues) detailing the test development work to be accomplished. If no GitHub issue exists, for the test development work, create one. 

To keep test definitions immune to code changes or nomenclatures in code, it is best to express the RFC in high level terms from the user level (Acme and Bob for instance), that can be interpreted by the business instead of revealing implementation details. For example, `When Acme requests a connection with Bob` instead of `When Acme sends a connection-request to Bob`.  Sometimes this may be cumbersome, so just make it as high level as makes sense.  A full example from the connection protocol might look something like this;
```
Scenario Outline: establish a connection between two agents
Given we have "2" agents
| name | role |
| Acme | inviter |
| Bob | invitee |
When "Acme" generates a connection invitation
And "Bob" receives the connection invitation
And "Bob" sends a connection request to "Acme"
And "Acme" receives the connection request
And "Acme" sends a connection response to "Bob"
And "Bob" receives the connection response
And "Bob" sends <message> to "Acme"
Then "Acme" and "Bob" have a connection

Examples:
| message |
| trustping |
| ack |
```

Utilize [Data Tables](https://www.baeldung.com/cucumber-data-tables) and [Examples](https://behave.readthedocs.io/en/latest/gherkin.html#scenario-outlines) in the Gherkin definition where possible. 

## Using Tags

The test harness has utilized [tags](https://behave.readthedocs.io/en/latest/tutorial.html?highlight=tags#controlling-things-with-tags) in the feature files to be able to narrow down a test set to be executed. The general tags currently utilized are as follows:

- @AcceptanceTest - Tests based on requirements specifically stated in the RFC. These are tests that will run to verify confirmance of the implemented protocol in the Agents.
- @DerivedFunctionalTest - Tests derived on requirements but not specifically stated in the RFC.
- @P1 - Test Priority
- @P2 - Test Priority
- @P3 - Test Priority
- @P4 - Test Priority
- @NegativeTest - Test that attempts to break the software. ie. change workflow order, use invalid data, etc.
- @ExceptionTest - Tests that are based on requirements that suggest exception cases.
- @NegativeTest - Tests specifically designed to try and break the software
- @SmokeTest - Tests that can be used as a builds smoke or sanity tests.
- @NeedsReview - Tests that have not been reviewed or approved.
- @ReviewedApproved - obvious
- @wip - Tests that are a work in progress and incomplete
- @Done - Finished tests that are expected to Pass if executed against an Agent.
- @AIP10 - Aries Interop Profile version the tests are written for
- @T01-API10-RFC0160 - Test Unique Identifier - Please use T for the test cases number, the API version number the test is written for, and the RFC number for the Protocol under test. 
- @WillFail - Tests completed but because of an outstanding bug, they are expected to fail. The test harness looks for this to report on the next tag  
- @OutstandingBug..###..url - When using @WillFail, this tag much also be used. It is comprised of 3 components, OutstandingBug, the bug number, and the bug url. These must be separated by double periods.

### Defining Protocol Suite Specific Tags
There will be cases where there will be a need for Protocol specific tags. This will usually reveal itself when there are optional implementations or where implementations can diverge into 2 or more options. Tests will need to be tagged with the least common option, where no tag means the other option. For example in the connection protocol there are specific tests that exercise the behaviour of the protocol under a Multi Use Invite and a Single Use Invite. The tag @MultiUseInvite is used to differentiate the two, and by default it is expected that MultiUseInvite is the least common option.

Currently Existing Connection Protocol Tags
- @MultiUseInvite - Test utilizes a multi-use invite. Not using this tag and the test expects the invite to be single use.
- @SingleTryOnException
- @RetryableOnException

Defining specific tags should be discussed with the Aries Protocol test community. 

## Defining Backchannel Commands

While defining tests it will become evident that your backchannel, the interface between the tests and your Agent, will need to support certain commands. These are to be defined in the [aries-agent-test-harness/aries-backchannels/backchannel_operations.csv](https://github.com/bcgov/aries-agent-test-harness/blob/master/aries-backchannels/backchannel_operations.csv)

Note that this CSV file is currently generated from a google sheet, located [here](https://bit.ly/AriesTestHarnessScenarios).

## Implementing Test Steps

Follow standard best practices for implementing test steps in Behave. Write the test steps as if your backchannel is already implemented, then implement your backchannel to make the test work. 

Note that the current backchannels (aca-py and vcx) will throw a "NotImplementedException" for any steps that are not implemented in the backchannel, and will include information from the above-mentioned CSV file.

## Implementing the Backchannel

See [Writing a new Backchannel for a new Agent](https://github.com/bcgov/aries-agent-test-harness#writing-a-new-backchannel-for-a-new-agent)

