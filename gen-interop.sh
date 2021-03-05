#! /bin/bash

usage () {

cat << EOF
Usage: gen-interop.sh [--help]

Generates the Aries Interop tests documentation pages based on the workflows defined in the
repo. The workflows are in the .github/workflows folder and must be named "test-harness-<name>.yml".

The generator iterates over each workflow file, extracts data from it -- either live
data or from comments, grabs data from the last run of the workflow and puts the data
into generated markdown files in the /docs folder.

Basic process:
  Generate the header for the summary page (README.md)
  Iterate through the workflow files -- the runsets
      Extract data from the workflow file and Allure results
      Print a summary row about the test runs and history
  Iterate through the workflow files -- the runsets (again)
      Extract data from the workflow file and Allure results (again)
      Print a details file about about the current runset (<runset>.md)

To add information about a workflow, insert comments into the YAML with identifiers RUNSET_NAME,
Scope, Summary, and Current.

To exclude a workflow, add a comment "# SKIP", and the process will not include the workflow 
EOF

exit

}

if [ "$1" == "--help" ]; then
    usage
fi

# Helper function to override the default agent type -- if there is an override
agent_type () { # file Agent Default_Value
    if grep -q $2 $1; then
        echo $(grep "$2" $1 | sed 's/.*: //')
    else
        echo $3
    fi
}

# Collect all the data about each runset
collect_runset_data () {
    file=$1
    export RUNSET=$(echo $file | sed "s/.*ness-//" | sed "s/.yml//")
    export RUNSET_NAME=""
    export RUNSET_NAME=$(grep RUNSET_NAME $file |  sed 's/^.*: //' | sed 's/["]//g')
    if [ "${RUNSET_NAME}" == "" ]; then
        export RUNSET_NAME=${RUNSET}
    fi
    export SCOPE=$(grep "# Scope" $file |  sed 's/^.*: //' | sed 's/["]//g')
    # Optional -- to skip a runset from inclusion in the results.
    export SKIP=$(grep "# SKIP" $file )
    export RUNSET_LINK=${RUNSET}
    export SUMMARY=$(grep "^#" $file | sed 's/^#[ ]*//'  | sed '/Current/,$d' | sed '1,/Summary/d' | sed 's/$/\\n/' | sed 's/^ //')
    export CURRENT_STATUS=$(grep "^#" $file | sed 's/^#[ ]*//'  | sed '/^End/,$d' | sed -n '/Current/,$p' | sed '1d' | sed 's/^ //')
    export DEFAULT_AGENT=$(grep "DEFAULT_AGENT" $file | sed 's/.*: //' )
    export ACME=$(agent_type $file ACME ${DEFAULT_AGENT} )
    export BOB=$(agent_type $file BOB ${DEFAULT_AGENT} )
    export FABER=$(agent_type $file FABER ${DEFAULT_AGENT} )
    export MALLORY=$(agent_type $file MALLORY ${DEFAULT_AGENT} )
    export ALLURE_PROJECT=$(grep "REPORT_PROJECT" $1 | sed -n '1p' | sed 's/.*: //' | sed 's/ *$//' )
    export ALLURE_LINK="https://allure.vonx.io/allure-docker-service-ui/projects/${ALLURE_PROJECT}/reports/latest"
    export ALLURE_BEHAVIORS_LINK="https://allure.vonx.io/api/allure-docker-service/projects/${ALLURE_PROJECT}/reports/latest/index.html?redirect=false#behaviors"
    export TOTAL_CASES=$( curl --silent https://allure.vonx.io/api/allure-docker-service/projects/${ALLURE_PROJECT}/reports/latest/widgets/summary.json | grep "total" | sed 's/.*: //' | sed 's/[^0-9]*$//' )
    export PASSED=$( curl --silent https://allure.vonx.io/api/allure-docker-service/projects/${ALLURE_PROJECT}/reports/latest/widgets/summary.json | grep "passed" | sed 's/.*: //' | sed 's/[^0-9]*$//' )
    export FAILED=$( curl --silent https://allure.vonx.io/api/allure-docker-service/projects/${ALLURE_PROJECT}/reports/latest/widgets/summary.json | grep "failed" | sed 's/.*: //' | sed 's/[^0-9]*$//' )
    if [ ${TOTAL_CASES} -eq 0 ]; then
        export PERCENT=0
    else
        export PERCENT=$((PASSED*100/TOTAL_CASES))
    fi
}

# The summary page header -- markdown format
aries_interop_header () {

    cat << EOF >>$outfile

This web site shows the current status of Aries Interoperability.

The latest interoperability test results are provided below. Each item is for a test runset, a combination
of Aries agents and frameworks running a subset of the overall tests in the repository. The subset of tests
run represent the set of tests expected to be supported by the combination of components being tested.

The following test agents are currently included in the runsets:

- [Aries Cloud Agent Python](https://github.com/hyperledger/aries-cloudagent-python) (ACA-Py)
- [Aries Framework .NET](https://github.com/hyperledger/aries-framework-dotnet) (AF-.NET)
- [Aries Framework - JavaScript](https://github.com/hyperledger/aries-framework-javascript) (AF-JS)
- [Aries Framework Go](https://github.com/hyperledger/aries-framework-go) (AF-Go)

Want to add your Aries component to this page? You need to add a runset to the
[Aries Agent Test Harness](https://github.com/hyperledger/aries-agent-test-harness).

## Summary

|   #   | Runset Name     | Scope | Results |
| :---- | :-------------- | ----- | ------: |
EOF
}

# First write the summary file -- make sure to replace the old version with a ">" and ">>" for the rest
outfile=docs/README.md
# Title of the page
# Note -- may want to put Jekyll frontmatter at the top of the page
echo -e '# Aries Interoperability Testing Overview\n' >$outfile

aries_interop_header

count=1
for file in .github/workflows/test-harness-*; do
# Collect the data per workflow and then dump it into the table
    collect_runset_data $file
    if [ "${SKIP}" != "" ]; then
        continue # Skip this workflow from the published results
    fi
    echo "| ${count} | [${RUNSET_NAME}](./${RUNSET}.md) | ${SCOPE} | **${PASSED} / ${TOTAL_CASES}** (${PERCENT}%) |" >>$outfile
    count=$(expr ${count} + 1)
done

# Finished with the table -- add in the footer and done with the summary file
echo -e "\\n*Results last updated: $(date | sed 's/  / /g')*" >>$outfile
echo "" >>$outfile

# Loop again over the workflow files and generate a file per workflow of details
count=1
for file in .github/workflows/test-harness-*; do
# Collect the data -- again. No worries -- it won't take long.
    collect_runset_data $file
    if [ "${SKIP}" != "" ]; then
        continue # Skip this workflow from the published results
    fi
# New output file -- the test details -- overwrite the old version
    outfile=docs/${RUNSET}.md

# First write eache detail file -- make sure to replace the old version with a ">" and ">>" for the rest
    echo -e "# ${RUNSET_NAME}\\n" >$outfile
    echo -e "## Summary of Tests\\n" >>$outfile
    
# Print the summary text from the workflow file -- or a default message
    if [ "${SUMMARY}" == "" ]; then
        echo -e "\`\`\`warning\\nNo summary is available for this runset. Please update: $file.\\n\`\`\`\\n" >>$outfile
    else
        echo -e ${SUMMARY}\\n >>$outfile
    fi

# Print a table of details
    echo "|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) | Scope of Tests |" >>$outfile
    echo "| :------------: | :----------: | :-------------: | :--------------: | -------------- |" >>$outfile
    echo "| ${ACME} | ${BOB} | ${FABER} | ${MALLORY} | ${SCOPE} |" >>$outfile
# Print the highlighted test results
    echo -e "\\n\`\`\`tip\\n**Latest results: ${PASSED} out of ${TOTAL_CASES} (${PERCENT}%)**\\n" >>$outfile
    echo -e "\\n*Last updated: $(date | sed 's/  / /g')*\\n\`\`\`\\n" >>$outfile
    echo -e "## Current Status of Tests" >>$outfile
# Print the status text from the workflow file -- or a default message
    if [ "${CURRENT_STATUS}" == "" ]; then
        echo -e "\`\`\`warning\\nNo test status note is available for this runset. Please update: $file.\\n\`\`\`\\n" >>$outfile
    else
        echo -e "${CURRENT_STATUS}\\n" >>$outfile
    fi
# Links to the allure results
    echo -e "## Test Run Details" >>$outfile
    echo -e "See the tests results organized by Aries RFCs executed [${ALLURE_PROJECT}](${ALLURE_BEHAVIORS_LINK})\\n" >>$outfile
    echo -e "See the test runs history and drill into the details [${ALLURE_PROJECT}](${ALLURE_LINK})\\n" >>$outfile
    count=$(expr ${count} + 1)

# Link to the summary page
    echo "Jump back to the [runset summary](./README.md)." >>$outfile
# And we're done for this file
    echo "" >>$outfile
done
