# Retry Failed Test Scenarios

This feature introduces the ability to retry failed test scenarios in your test runs. It provides flexibility in managing the number of retry attempts for scenarios that fail during testing.

## Table of Contents
- [Introduction](#introduction)
- [Changes Made](#changes-made)
- [How to Run](#how-to-run)
  - [Using behave.ini](#1-using-behaveini)
  - [Using Environment Variable](#2-using-environment-variable)

## Introduction

This feature addresses the issue of retrying failed test scenarios. It implements a mechanism to automatically rerun failed scenarios to improve the stability of test results.

## Changes Made

The following changes have been made to implement the retry functionality:

- Added a `before_feature` hook in `\features\environment.py` to handle retrying failed scenarios.
- Passed the overriding variable `TEST_RETRY_ATTEMPTS_OVERRIDE` via `manage.py` to the Docker environment.

## How to Run

There are two ways to override the number of attempts for retrying failed scenarios:

### 1. Using `behave.ini`

Add the following variable to the `[behave.userdata]` section of the `behave.ini` file:

```ini
[behave.userdata]
test_retry_attempts = 2
```

### 2. Using Environment Variable

Pass the `TEST_RETRY_ATTEMPTS_OVERRIDE` variable as an environment variable while running tests or through deployment YAML files.

Example:
```bash
TEST_RETRY_ATTEMPTS_OVERRIDE=2 ./manage run -d acapy -b javascript -t @AcceptanceTest
```

### Feedback and Contributions
Your feedback and contributions are welcome! If you encounter any issues or have suggestions for improvement, please feel free to open an issue or submit a pull request.
