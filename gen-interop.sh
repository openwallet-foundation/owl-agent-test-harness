#! /bin/bash

# Config data
export outfile=docs/index.md

agent_type () { # file Agent Default_Value
    if grep -q $2 $1; then
        echo $(grep "$2" $1 | sed 's/.*: //')
    else
        echo $3
    fi
}

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
    export RUNSET_LINK=${RUNSET}
    export SUMMARY=$(grep "^#" $file | sed 's/^#[ ]*//'  | sed '/Current/,$d' | sed '/Summary/d' | sed 's/$/\\n/' | sed 's/^ //')
    export CURRENT_STATUS=$(grep "^#" $file | sed 's/^#[ ]*//'  | sed '/^End/,$d' | sed -n '/Current/,$p' | sed '1d' | sed 's/$/\\n/' | sed 's/^ //')
    export DEFAULT_AGENT=$(grep "DEFAULT_AGENT" $file | sed 's/.*: //' )
    export ACME=$(agent_type $file ACME ${DEFAULT_AGENT} )
    export BOB=$(agent_type $file BOB ${DEFAULT_AGENT} )
    export FABER=$(agent_type $file FABER ${DEFAULT_AGENT} )
    export MALLORY=$(agent_type $file MALLORY ${DEFAULT_AGENT} )
    export ALLURE_PROJECT=$(grep "REPORT_PROJECT" $1 | sed -n '1p' | sed 's/.*: //' | sed 's/ *$//' )
    export ALLURE_LINK=https://allure.vonx.io/allure-docker-service-ui/projects/${ALLURE_PROJECT}/reports/latest
    export TOTAL_CASES=$( curl --silent https://allure.vonx.io/api/allure-docker-service/projects/${ALLURE_PROJECT}/reports/latest/widgets/summary.json | grep "total" | sed 's/.*: //' | sed 's/[^0-9]*$//' )
    export PASSED=$( curl --silent https://allure.vonx.io/api/allure-docker-service/projects/${ALLURE_PROJECT}/reports/latest/widgets/summary.json | grep "passed" | sed 's/.*: //' | sed 's/[^0-9]*$//' )
    export FAILED=$( curl --silent https://allure.vonx.io/api/allure-docker-service/projects/${ALLURE_PROJECT}/reports/latest/widgets/summary.json | grep "failed" | sed 's/.*: //' | sed 's/[^0-9]*$//' )
    if [ ${TOTAL_CASES} -eq 0 ]; then
        export PERCENT=0
    else
        export PERCENT=$((PASSED*100/TOTAL_CASES))
    fi
}

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

|   #   | Runset Name     | Passed Tests |
| :---: | :-------------: | :-------------: |
EOF
}

# First write to file -- make sure to replace the old version
echo -e '# Aries Interoperability Testing Overview\n' >$outfile
aries_interop_header

count=1
for file in .github/workflows/test-harness-*; do
    collect_runset_data $file
    echo "| ${count} | [${RUNSET_NAME}](#${count}-$RUNSET_LINK) | **${PASSED} / ${TOTAL_CASES}** (${PERCENT}%) |" >>$outfile
    count=$(expr ${count} + 1)
done

echo "" >>$outfile
count=1
for file in .github/workflows/test-harness-*; do
    collect_runset_data $file
    echo -e "## ${count} ${RUNSET}\\n" >>$outfile
    echo -e Name: **${RUNSET_NAME}**\\n >>$outfile
    if [ "${SUMMARY}" == "" ]; then
        echo -e "No summary is available for this runset. Please add it to the file $file.\\n" >>$outfile
    else
        echo -e ${SUMMARY}\\n >>$outfile
    fi

    echo "|  ACME (Issuer) | Bob (Holder) | Faber (Verfier) | Mallory (Holder) |" >>$outfile
    echo "| :------------: | :----------: | :-------------: | :--------------: |" >>$outfile
    echo "| ${ACME} | ${BOB} | ${FABER} | ${MALLORY} |" >>$outfile
    echo -e "\\n**Latest results: ${PASSED} out of ${TOTAL_CASES} (${PERCENT}%)**\\n" >>$outfile
    if [ "${CURRENT_STATUS}" == "" ]; then
        echo -e "Test Status Notes: No summary is available for this runset. Please add it to the file $file.\\n" >>$outfile
    else
        echo -e "Test Status Notes: ${CURRENT_STATUS}\\n" >>$outfile
    fi
    echo -e "See the full test run results and history for the runset [${ALLURE_PROJECT}](${ALLURE_LINK})\\n" >>$outfile
    count=$(expr ${count} + 1)
done

echo "" >>$outfile
# cat $outfile