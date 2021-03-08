from behave import *
import json
from agent_backchannel_client import agent_backchannel_GET, agent_backchannel_POST, expected_agent_state
from time import sleep
import time


@when('"{holder}" proposes a credential to "{issuer}" with {credential_data}')
def step_impl(context, holder, issuer, credential_data):

    if "schema_dict" in context:
        for schema in context.schema_dict:
            try:
                credential_data_json_file = open('features/data/cred_data_' + schema.lower() + '.json')
                credential_data_json = json.load(credential_data_json_file)
            except FileNotFoundError:
                print(FileNotFoundError + ': features/data/cred_data_' + schema.lower() + '.json')

            if 'credential_data_dict' in context:
                context.credential_data_dict[schema] = credential_data_json[credential_data]['attributes']
            else:
                context.credential_data_dict = {schema: credential_data_json[credential_data]['attributes']}

            if "AIP20" in context.tags:
                if 'filters_dict' in context:
                    context.filters_dict[schema] = credential_data_json[credential_data]['filters']
                else:
                    context.filters_dict = {schema: credential_data_json[credential_data]['filters']}

    for schema in context.schema_dict:
        context.credential_data = context.credential_data_dict[schema]
        context.schema = context.schema_dict[schema]
        if "AIP20" in context.tags:
            context.filters = context.filters_dict[schema]
        context.execute_steps('''
                When  "''' + holder + '''" proposes a credential to "''' + issuer + '''"
            ''')
