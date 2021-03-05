#! /bin/bash

# Generates the Aries Interop tests documentation pages.
# Basic process:
#   Generate the header for the summary page
#   Iterate through the workflow files -- the runsets
#       Extract data from the workflow file and Allure results
#       Print a summary row about the test runs and history
#   Iterate through the workflow files -- the runsets (again)
#       Extract data from the workflow file and Allure results (again)
#       Print a details file about about the current runset


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
        export RUNSET_LINK=${RUNSET}
    else
        export RUNSET_LINK=$(echo "$RUNSET_NAME" | tr '[:upper:]' '[:lower:]' | tr -d '[:punct:]' | tr '[:blank:]' '-')
    fi
    # Temporary -- until I can figure out how to convert arbitary strings into GitHub links
    export SCOPE=$(grep "# Scope" $file |  sed 's/^.*: //' | sed 's/["]//g')
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

- [Aries Cloud Agent Python](https://github.com/hyperledger/aries-cloudagent-python)
- [Aries Framework .NET](https://github.com/hyperledger/aries-framework-dotnet)
- [Aries Framework - JavaScript](https://github.com/hyperledger/aries-framework-javascript)
- [Aries Framework Go](https://github.com/hyperledger/aries-framework-go)

Want to add your Aries component to this page? You need to add a runset to the
[Aries Agent Test Harness](https://github.com/hyperledger/aries-agent-test-harness).

## Summary

Results last updated: $(date | sed 's/  / /g')

|   #   | Runset Name     | Scope | Passed Tests |
| :---- | :-------------- | ----- | -----------: |
EOF
}

# First write to file -- make sure to replace the old version
outfile=docs/README.md
echo -e '# Aries Interoperability Testing Overview\n' >$outfile
aries_interop_header

count=1
for file in .github/workflows/test-harness-*; do
    collect_runset_data $file
    echo "| ${count} | [${RUNSET_NAME}](./${RUNSET}.md) | ${SCOPE} | **${PASSED} / ${TOTAL_CASES}** (${PERCENT}%) |" >>$outfile
    count=$(expr ${count} + 1)
done

echo "" >>$outfile

count=1
for file in .github/workflows/test-harness-*; do
    collect_runset_data $file
    # New output file -- the test details -- overwrite the old version
    outfile=docs/${RUNSET}.md
    echo -e "# ${RUNSET_NAME}\\n" >$outfile
    echo -e "## Summary of Tests\\n" >>$outfile
    
    if [ "${SUMMARY}" == "" ]; then
        echo -e "\`\`\`warning\\nNo summary is available for this runset. Please update: $file.\\n\`\`\`\\n" >>$outfile
    else
        echo -e ${SUMMARY}\\n >>$outfile
    fi

    echo "|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) | Scope of Tests |" >>$outfile
    echo "| :------------: | :----------: | :-------------: | :--------------: | -------------- |" >>$outfile
    echo "| ${ACME} | ${BOB} | ${FABER} | ${MALLORY} | ${SCOPE} |" >>$outfile
    echo -e "\\n\`\`\`tip\\n**Latest results: ${PASSED} out of ${TOTAL_CASES} (${PERCENT}%)**\\n\`\`\`\\n" >>$outfile
    echo -e "## Current Status of Tests" >>$outfile
    if [ "${CURRENT_STATUS}" == "" ]; then
        echo -e "\`\`\`warning\\nNo test status note is available for this runset. Please update: $file.\\n\`\`\`\\n" >>$outfile
    else
        echo -e "${CURRENT_STATUS}\\n" >>$outfile
    fi
    echo -e "## Test Run Details" >>$outfile
    echo -e "See the tests runs organized by Aries RFC [${ALLURE_PROJECT} behaviors](${ALLURE_BEHAVIORS_LINK})\\n" >>$outfile
    echo -e "See the test runs history and drill into the details [${ALLURE_PROJECT}](${ALLURE_LINK})\\n" >>$outfile
    count=$(expr ${count} + 1)
done

echo "Jump back to the [runset summary](./README.md)." >>$outfile

echo "" >>$outfile
# cat $outfile