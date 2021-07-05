#!/bin/bash

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"
COMMAND=${1}

startCommand() {
	docker-compose -f compose-1.yml up -d
	sleep 15
	docker-compose -f compose-2.yml up -d
	sleep 10
	docker-compose -f compose-3.yml up -d
}

generateKeys() {
	mkdir -p .build/keys/tls
	docker run -i --rm \
		-v ${SCRIPT_HOME}:/opt/workspace/orb \
		--entrypoint "/opt/workspace/orb/key-generation/generate_orb_keys.sh" \
		--user "$(id -u):$(id -g)" \
		frapsoft/openssl
}

setupCLI() {
	mkdir -p .build
	pushd .build > /dev/null

	if [[ ! -f orb-cli ]]; then
		curl -sL https://github.com/trustbloc/orb/releases/download/v0.1.1/orb-cli-linux-amd64.tar.gz | tar -x -z -O -f - > orb-cli
		chmod +x orb-cli
	fi

	popd > /dev/null
}

waitForReady() {
	sleep 15
}

setupFollowers() {
	($SCRIPT_HOME/cli-scripts/setup_followers.sh)
}

createDID() {
	RESULT=$(docker run -it --rm \
		--name "create-did" \
		-v "${SCRIPT_HOME}:/etc/orb-cli" \
		--network "aath_network" \
		--entrypoint "/etc/orb-cli/cli-scripts/create_did.sh" \
		"ubuntu:latest" \
	)

	mkdir -p $SCRIPT_HOME/../../aries-backchannels/afgo/.build/afgo-master.data
	echo $RESULT > $SCRIPT_HOME/../../aries-backchannels/afgo/.build/afgo-master.data/orb-did.json

	echo $RESULT
}

pushd ${SCRIPT_HOME} > /dev/null

case "${COMMAND}" in
	clean)
		docker-compose -f compose-1.yml -f compose-2.yml -f compose-3.yml down --volumes
		rm -rf .build
		;;
	stop)
		docker-compose -f compose-1.yml -f compose-2.yml -f compose-3.yml stop
		docker-compose -f compose-1.yml -f compose-2.yml -f compose-3.yml logs > orb.log
		docker-compose -f compose-1.yml -f compose-2.yml -f compose-3.yml down --volumes
		;;
	start)
		generateKeys
		setupCLI
		startCommand
		waitForReady
		setupFollowers
		sleep 5
		createDID
		;;
	logs)
		docker-compose -f compose-1.yml -f compose-2.yml -f compose-3.yml logs -f -t
		;;
	create)
		echo $(createDID)
		;;
	*)
		echo "orb: valid commands are 'clean' 'start' 'stop' 'logs'"
		;;
esac

popd > /dev/null # to caller
