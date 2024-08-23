# Introduction to Aries Interoperability

This website reports on the interoperability between different Hyperledger Aries agents. Interoperability includes how seamlessly the agents work together, and how well each agent adheres to community-agreed standards such as Aries Interop Profile (AIP) 1.0 and AIP 2.0.

## Why is interoperability important?

As Digital Trust ecosystems evolve they will naturally require many technologies to coexist and cooperate. Worldwide projects will get larger and will start to overlap. Also, stakeholders and users will not care about incompatibilities; they will simply wish to take advantage of Digital Trust benefits. Interoperability ultimately means more than just Aries agents working with each other, as it covers worldwide standards and paves the way for broader compatibility.

For all these reasons interoperability is incredibly important if Hyperledger Aries is to continue to flourish.

## What are Hyperledger Aries agents and frameworks?

Aries agents are the pieces of software that provide Digital Trust services such as issuing and receiving verifiable credentials and verifying presentations of verifiable credentials. Many Aries agents are built on Aries Frameworks, common components that make it easier to create agents -- developers need only add the business logic on top of a framework to make their agent. Agents can be written in different programming languages, and designed for different devices or for use in the cloud.

What unites Aries agents are the standards and protocols they aim to adhere to, and the underlying technologies (cryptography, DIDs and DID utility ledgers and verifiable credentials).

The Aries frameworks and agents currently tested for interoperability with AATH are:

- [Aries Cloud Agent Python (ACA-Py)](https://github.com/hyperledger/aries-cloudagent-python)
- [Credo-TS (Credo)](https://github.com/openwallet-foundation/credo-ts)
- [Aries VCX](https://github.com/hyperledger/aries-vcx)

The Aries frameworks and agents formerly tested for interoperability with AATH are:

- [Aries Framework .NET](https://github.com/hyperledger/aries-framework-dotnet)
- [Aries Framework Go](https://github.com/hyperledger/aries-framework-go)
- [Findy Agent](https://findy-network.github.io/)

## How is interoperability assessed?

### The Aries Agent Test Harness

Aries Agent Test Harness (AATH) is open-source software that runs a series of Aries interoperability tests and delivers the test results data to this website.

AATH uses a [Behavior Driven-Development](https://en.wikipedia.org/wiki/Behavior-driven_development) (BDD) framework to run tests that are designed to exercise the community-designed Aries Protocols, as defined in the [Aries RFC](https://hyperledger.github.io/aries-rfcs/latest/) specifications.

The tests are executed by starting up four Test Agents (“Acme” is an issuer, “Bob” a holder/prover, “Faber” a verifier and Mallory, a sometimes malicious holder/prover), and having the test harness send instructions to the Test Agents to execute the steps of the BDD tests. Each Test Agent is a container that contains the “component under test” (an Aries agent or framework), along with a web server that communicates (using HTTP) with the test harness to receive instructions and report status, and translates and passes on those instructions to the “component under test” using whatever method works for that component. This is pictured in the diagram below, and is covered in more detail in the [AATH Architecture](https://github.com/hyperledger/aries-agent-test-harness#architecture) section of the repo’s README.

![AATH Architecture](assets/aath-arch/aath-arch.png)

### Runsets

A runset is a named set of tests (e.g. “all AIP 1.0 tests”) and test agents (e.g. “ACA-Py and Aries Framework JavaScript”) that are run on a periodic basis via GitHub Actions — for example, every day. The results of each run of a runset are recorded to a test results repository for analysis and summarized on this site. In general, the order of the Test Agent names indicate the roles played, with the first playing all roles except Bob (the holder/prover). However, exact details of what Test Agents play what roles can be found in the runset details page.

The set of tests run (the scope) per runset vary by the combined state of the agents involved in a test. For example:

- Some agents implement Aries Interop Profile (AIP) 1.0, others 2.0 and others, both.
- Some agents have implemented more features than others, and therefore support more tests,
- Some agents are unable to support particular tests because of practical limitations of the device they run on (e.g. mobile) or the ease with which that test can be conducted.

For these reasons it’s not possible to say that, for example, an 80% pass result is “good” or 50% is “bad”. The numbers need to be understood in context.

The scope and exceptions columns in the summary and the summary statement found on each runset detail page on this website, document the scope and expectations of runset.

Each runset detail page also provides narrative on the current status of the runset — for example, why some tests of a runset are failing, what issues have been opened and where to address the issue.

### Failing Tests

Tests can fail for many reasons, and much of the work of maintaining the tests and runsets is staying on top of the failures.  The following are some notes about failing tests and what to do about them:

- Most failures happen when new runsets are added. For example, a new Test Agent is added to the repository and it doesn’t play well with the existing Test Agents.
- Since most runsets pull the latest main branch code for each Test Agent for each run of the set, errors may be introduced as a result of code added to a Test Agent. Thus, the AATH is an example of a new form of “CI”, Continuous _Interoperability_.
- With each failure, an evaluation is needed about the cause of the error:
  - Is the test that is incorrectly interpreting the RFC?
  - Is the RFC itself wrong?
  - Is one of the agents/frameworks involved in the testing implementing the RFC incorrectly?
  - Is the driver (called the Backchannel) that is controlling the agent/framework have a bug?
- Each failure should result in a GitHub issue being opened in the appropriate repo and the runset narrative updated to note the failure and the issue. Once solved, the runset narrative should be updated to remove the reference to the issue.

#### Investigating Failing Tests

The Allure reports accessible from this site provide a lot of information about failing tests and are a good place to start in figuring out what is happening. Here's how to follow the links to get to the test failure details:

1. On the main page, pick a Test Agent whose tests you want to drill into by clicking the name of the Test Agent from the main page summary table (first column), taking you to the Test Agent page.
2. On the Test Agent page, find a runset with at least some failures, and click on the runset name from the Test Agent summary table (first column), taking you to the section of the Test Agent page about that runset.
3. Within the runset details section, check the "Current Runset Status" summary to see if there is any reason for the failures there, and then drill into the test results by clicking the link entitled "Results by executed Aries RFCs." Clicking that link takes you from the Aries Interop Info site into the Allure test results, and lots (and lots) of details about test runs.
4. The page you will arrive upon will show the handful of RFCs scenarios executed during the test runs (with titles like "RFC 0036 Aries agent issue credential"), and for each a count of the status for tests cases within each scenario (e.g. passed, failed, broken and so on).
5. Expand a scenario with one or more failing tests and then click on the one of the failed tests (with an ugly red "X" beside the test case) to see the details (stack trace) of the error on the right part of the page.
6. From here you can look at a variety of things about the failing test:
   1. Review the test failure "Overview" to see the specific test step that failed and related failed assertion stack trace.
   2. Scroll down to the sequence of steps in the test, to see how far along the test got before the failure.
   3. Click on the "History" tab to see if it has always failed, or if this is a new issue.
   4. If it has passed in earlier runs, drill into the passing test to see if you can learn anything from that.
   5. Dive into the weeds...look at the stack trace, find the associated code, and see if you can figure out what happened. Find anything?  Report it via an issue, or even better, submit a Pull Request to fix the issue. Remember to consider all of the possible places an error could occur (above).

In addition to drilling into a specific test scenario (aka "stories")/case (aka "behavior")/step, you can look at the recent runset history (last 20 runs). On the left side menu, click on "Overview", and then take a look at the big "history" graph in the top right, showing how the runset execution has varied over time. Ideally, it's all green, but since you started from a runset that had failures, it won't be. Pretty much every part of the overview page is a drill down link into more and more detailed information about the runset, a specific run of the runset, a specific test case and so on. Lots to look at!

## What is Aries Interop Profile?

Aries Interop Profile (AIP) is a set of concepts and protocols that every Aries agent that wants to be interoperable should implement. Specific Aries agents may implement additional capabilities and protocols, but for interoperability, they must implement those defined in an AIP.

AIP currently has two versions:

- [AIP 1.0](https://github.com/hyperledger/aries-rfcs/tree/master/concepts/0302-aries-interop-profile#aries-interop-profile-version-10), finalized in January 2020, defines how Aries agents communicate with each other using a single type of verifiable credential
- [AIP 2.0](https://github.com/hyperledger/aries-rfcs/pull/579), is expected to be finalized in March 2021, builds on AIP 1.0 including how Aries agents can exchange several types of verifiable credentials, including W3C standard verifiable credentials.

AIP versions go through a rigorous community process of discussion and refinement before being agreed upon. During that process, the RFCs that go into each AIP are debated and the specific version of each included RFC is locked down. AIPs are available for anyone to review (and potentially contribute to) in the [Aries RFC repo](https://github.com/hyperledger/aries-rfcs).

## How can I contribute?

For developers improving an Aries agent or framework, each runset's page has a link to a detailed report in Allure. This allows the specific tests and results to be explored in detail.

If you are a stakeholder interested in improving the results for an agent, this website (and the Allure links, described above) should have enough material for your teams to take action.

Finally, if you want your Aries agent to be added to this website, or wish to expand the tests covered for your agent, your developers can reference the extensive information in the [Aries Agent Test Harness repo](https://github.com/hyperledger/aries-agent-test-harness) on GitHub.

In addition an API reference for backchannels can be found [here](http://aries-interop.info/api.html)
