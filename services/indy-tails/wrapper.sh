#!/bin/bash

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"
COMMAND=${1}

export COMPOSE_PROJECT_NAME=docker

# runTailsCommand <command>
runTailsCommand() {
	mkdir -p .build
	pushd .build > /dev/null

	if [[ ! -d "indy-tails-server" ]] ; then
		git clone https://github.com/bcgov/indy-tails-server.git > /dev/null
		pushd indy-tails-server > /dev/null
	else
		pushd indy-tails-server > /dev/null
		git pull > /dev/null
	fi

	./docker/manage "${1}"

	popd > /dev/null # to .build
	popd > /dev/null # to SCRIPT_HOME
}

checkStop() {
	if [[ -f ".build/indy-tails-server/docker/manage" ]]; then
		.build/indy-tails-server/docker/manage rm
	fi
}

pushd ${SCRIPT_HOME} > /dev/null

case "${COMMAND}" in
	clean)
		checkStop
		rm -rf .build
		;;
	start)
		runTailsCommand up
		;;
	stop)
		runTailsCommand down
		;;
	logs)
		runTailsCommand logs
		;;
	*)
		echo "indy-tails-server: valid commands are 'clean', 'start', 'stop', 'logs'"
		;;
esac

popd > /dev/null # to caller
