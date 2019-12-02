from behave import *
import json
from agent_backchannel_client import agent_backchannel_GET, agent_backchannel_POST, connection_status

# This step is defined in another feature file
# Given "Alice" and "Bob" have an existing connection

@when('"{issuer}" sends a credential offer')
def step_impl(context, issuer):
    pass

@when('"{receiver}" sends a credential request')
def step_impl(context, receiver):
    pass

@when('"{issuer}" issues a credential')
def step_impl(context, issuer):
    pass

@when('"{receiver}" receives and acknowledges the credential')
def step_impl(context, receiver):
    pass

@then('"{issuer}" has an acknowledged credential issue')
def step_impl(context, issuer):
    pass

@then('"{issuer}" has received a credential')
def step_impl(context, issuer):
    pass
