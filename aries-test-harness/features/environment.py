# -----------------------------------------------------------
# Behave environtment file used to hold test hooks to do
# Setup and Tear Downs at different levels
# For more info see:
# https://behave.readthedocs.io/en/latest/tutorial.html#environmental-controls
#  
# -----------------------------------------------------------

def before_scenario(context, scenario):
    print("before_scenario activated")
    # See if the @WillFail tag exists
    if 'WillFail' in context.tags :
        # if so get the @OutstandingBug.bug#.bugURL tag
        #sIssueInfo = context.tags
        sIssueInfo = [i for i in context.tags if 'OutstandingBug' in i] 
        sIssueInfo = sIssueInfo[0]
        # Parse out the Bug number and the URL based on the double . separator.
        lIssueInfo = sIssueInfo.split("..")
        sIssueNum = lIssueInfo[1]
        sIssueURL = lIssueInfo[2]

        # Tell the user the scenario will fail, the bug number, and the URL to the bug
        print ('Test ' + scenario.name + ' WILL FAIL due to an outstanding issue, ' + sIssueNum + ', not yet resolved.')
        print ('For more information see issue details at ' + sIssueURL)