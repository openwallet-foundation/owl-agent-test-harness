# -----------------------------------------------------------
# Behave environtment file used to hold test hooks to do
# Setup and Tear Downs at different levels
# For more info see:
# https://behave.readthedocs.io/en/latest/tutorial.html#environmental-controls
#  
# -----------------------------------------------------------
import json

def before_scenario(context, scenario):
    
    # Check if the @WillFail tag exists
    if 'WillFail' in context.tags :
        
        # if so get the @OutstandingBug..bug#..bugURL tag
        s_issue_info = [i for i in context.tags if 'OutstandingBug' in i] 
        s_issue_info = s_issue_info[0]
        
        # Parse out the Bug number and the URL based on the double . separator.
        l_issue_info = s_issue_info.split("..")
        s_issue_num = l_issue_info[1]
        s_issue_url = l_issue_info[2]

        # Tell the user the scenario will fail, the bug number, and the URL to the bug
        print ('NOTE: Test \"' + scenario.name + '\" WILL FAIL due to an outstanding issue, ' + s_issue_num + ', not yet resolved.')
        print ('For more information see issue details at ' + s_issue_url)

    # Check if the @MultiUseInvite tag exists
    if 'MultiUseInvite' in context.tags :
        
        print ('NOTE: Test \"' + scenario.name + '\" WILL FAIL if your Agent Under Test is not started with or does not support Multi Use Invites.')

    # Check for Present Froof Feature to be able to handle the loading of schemas and credential definitions before the scenarios.
    if 'present proof' in context.feature.name:
            # get the tag with "Schema_".
            for tag in context.tags:
                if 'Schema_' in tag:
                    # Get and assign the scehma to the context
                    try:
                        schema_json_file = open('features/data/' + tag.lower() + '.json')
                        schema_json = json.load(schema_json_file)
                        context.schema = schema_json["schema"]

                        # Get and assign the credential definition info to the context
                        context.support_revocation = schema_json["cred_def_support_revocation"]

                        #context.credential_definition = 
                    except FileNotFoundError:
                        print('FileNotFoundError: features/data/' + tag.lower + '.json')
                    
                    




