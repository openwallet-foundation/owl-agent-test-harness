#!/bin/bash

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"
COMMAND=${1}

export COMPOSE_PROJECT_NAME=von

# runVonCommand <command>
runVonCommand() {
	mkdir -p .build
	pushd .build > /dev/null

	if [[ ! -d "von-network" ]] ; then
		git clone https://github.com/bcgov/von-network.git > /dev/null
		pushd von-network > /dev/null
	else
		pushd von-network > /dev/null
		git pull > /dev/null
	fi

	./manage "${1}"

	popd > /dev/null # to .build
	popd > /dev/null # to SCRIPT_HOME
}

checkStop() {
	if [[ -f ".build/von-network/manage" ]]; then
		.build/von-network/manage down
	fi
}

pushd ${SCRIPT_HOME} > /dev/null

case "${COMMAND}" in
	clean)
		checkStop
		rm -rf .build
		;;
	start)
		runVonCommand up
		;;
	stop)
		runVonCommand down
		;;
	logs)
		runVonCommand logs
		;;
	*)
		echo "von-network: valid commands are 'clean', 'start', 'stop', 'logs'"
		;;
esac

popd > /dev/null # to caller
