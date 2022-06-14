#!/bin/bash

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"
COMMAND=${1}

export COMPOSE_PROJECT_NAME=docker

pushd ${SCRIPT_HOME} > /dev/null

case "${COMMAND}" in
	clean)
		docker-compose down --volumes
		rm -rf .build
		;;
	start)
		docker-compose up -d
		;;
	stop)
		docker-compose down
		;;
	logs)
		docker-compose logs
		;;
	*)
		echo "indy-tails-server: valid commands are 'clean', 'start', 'stop', 'logs'"
		;;
esac

popd > /dev/null # to caller
