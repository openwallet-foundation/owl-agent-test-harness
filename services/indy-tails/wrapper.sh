#!/bin/bash

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"
COMMAND=${1}

export COMPOSE_PROJECT_NAME=docker

pushd ${SCRIPT_HOME} > /dev/null

# ========================================================================================================
# Check Docker Compose
# --------------------------------------------------------------------------------------------------------

# Default to deprecated V1 'docker-compose'.
dockerCompose="docker-compose --log-level ERROR"

# Prefer 'docker compose' V2 if available
if [[ $(docker compose version 2> /dev/null) == 'Docker Compose'* ]]; then
  dockerCompose="docker --log-level error compose"
fi
echo "Using: ${dockerCompose}"

case "${COMMAND}" in
	clean)
		${dockerCompose} down --volumes
		rm -rf .build
		;;
	start)
		${dockerCompose} up -d
		;;
	stop)
		${dockerCompose} down
		;;
	logs)
		${dockerCompose} logs
		;;
	*)
		echo "indy-tails-server: valid commands are 'clean', 'start', 'stop', 'logs'"
		;;
esac

popd > /dev/null # to caller
