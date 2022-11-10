#!/bin/bash

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"
COMMAND=${1}

SOV_NETWORK="${LEDGER_URL_CONFIG:-http://localhost:9000}"

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

startCommand() {
	mkdir -p .build/sov-pool-config
	rm -f .build/sov-pool-config/config.txt
	curl $SOV_NETWORK/genesis --output .build/sov-pool-config/config.txt

	${dockerCompose} up -d
}

pushd ${SCRIPT_HOME} > /dev/null

case "${COMMAND}" in
	clean)
		${dockerCompose} down --volumes
		rm -rf .build
		;;
	stop)
		${dockerCompose} stop
		${dockerCompose} logs > uniresolver.log
		${dockerCompose} down --volumes
		;;
	start)
		startCommand
		;;
	logs)
		${dockerCompose} logs -f -t
		;;
	*)
		echo "uniresolver: valid commands are 'clean', 'start', 'stop', 'logs'"
		;;
esac

popd > /dev/null # to caller
