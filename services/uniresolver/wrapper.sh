#!/bin/bash

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"
COMMAND=${1}

SOV_NETWORK="${LEDGER_URL_CONFIG:-http://localhost:9000}"

startCommand() {
	mkdir -p .build/sov-pool-config
	rm -f .build/sov-pool-config/config.txt
	curl $SOV_NETWORK/genesis --output .build/sov-pool-config/config.txt

	docker-compose up -d
}

pushd ${SCRIPT_HOME} > /dev/null

case "${COMMAND}" in
	clean)
		docker-compose down --volumes
		rm -rf .build
		;;
	stop)
		docker-compose stop
		docker-compose logs > uniresolver.log
		docker-compose down --volumes
		;;
	start)
		startCommand
		;;
	logs)
		docker-compose logs -f -t
		;;
	*)
		echo "uniresolver: valid commands are 'clean', 'start', 'stop', 'logs'"
		;;
esac

popd > /dev/null # to caller
