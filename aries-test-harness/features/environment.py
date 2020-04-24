# -----------------------------------------------------------
# Behave environtment file used to hold test hooks to do
# Setup and Tear Downs at different levels
# For more info see:
# https://behave.readthedocs.io/en/latest/tutorial.html#environmental-controls
#  
# -----------------------------------------------------------

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
        print ('NOTE: Test ' + scenario.name + ' WILL FAIL due to an outstanding issue, ' + s_issue_num + ', not yet resolved.')
        print ('For more information see issue details at ' + s_issue_url)

    # Check if the @MultiUseInvite tag exists
    if 'MultiUseInvite' in context.tags :
        
        print ('NOTE: Test ' + scenario.name + ' WILL FAIL if your Agent Under Test is not started with or does not support Multi Use Invites.')
