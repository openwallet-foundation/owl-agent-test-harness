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

export DOCKERHOST=$(docker run --rm --net=host eclipse/che-ip)

generateAgentServices() {
	pushd ${SCRIPT_HOME} > /dev/null

	mkdir -p .build/services

	sed "s/AGENT_URL/${DOCKERHOST}/g" did-services/services.template | tee > .build/services.template

	sed "s/AGENT_PORT/9021/g" .build/services.template | tee > .build/services/Acme.json
	sed "s/AGENT_PORT/9031/g" .build/services.template | tee > .build/services/Bob.json
	sed "s/AGENT_PORT/9041/g" .build/services.template | tee > .build/services/Faber.json
	sed "s/AGENT_PORT/9051/g" .build/services.template | tee > .build/services/Mallory.json

	popd > /dev/null # to caller
}

createDID() {
	pushd ${SCRIPT_HOME} > /dev/null

	mkdir -p .build/orb-dids

	agent_names=( "Acme" "Bob" "Faber" "Mallory" )

	for AGENT_NAME in "${agent_names[@]}"; do

		RESULT=$(docker run -it --rm \
			--name "create-did" \
			-v "${SCRIPT_HOME}:/etc/orb-cli" \
			-e "SERVICE_FILE=.build/services/${AGENT_NAME}.json" \
			-e "AGENT_NAME=${AGENT_NAME}" \
			--network "aath_network" \
			--entrypoint "/etc/orb-cli/cli-scripts/create_did.sh" \
			"ubuntu:latest" \
		)

		echo $RESULT > .build/orb-dids/${AGENT_NAME}.json
		echo $RESULT\n
	done

	mkdir -p $SCRIPT_HOME/../../aries-backchannels/afgo/.build/afgo-master.data
	mkdir -p $SCRIPT_HOME/../../aries-backchannels/afgo/.build/afgo-interop.data

	cp -r .build/orb-dids ../../aries-backchannels/afgo/.build/afgo-master.data/
	cp -r .build/orb-dids ../../aries-backchannels/afgo/.build/afgo-interop.data/

	cp -r did-keys/priv ../../aries-backchannels/afgo/.build/afgo-master.data/
	cp -r did-keys/priv ../../aries-backchannels/afgo/.build/afgo-interop.data/


	popd > /dev/null # to caller
}

stopService() {
	arg=$1

	docker-compose -f compose-1.yml -f compose-2.yml -f compose-3.yml stop

	if [[ $arg = "with-logs" ]]; then
		if [[ -n "$(docker-compose -f compose-1.yml -f compose-2.yml -f compose-3.yml -p aath ps -q)" ]]; then
			echo writing logs...
			docker-compose -f compose-1.yml -f compose-2.yml -f compose-3.yml logs > orb.log
		fi
	fi

	docker-compose -f compose-1.yml -f compose-2.yml -f compose-3.yml down --volumes
}

pushd ${SCRIPT_HOME} > /dev/null

case "${COMMAND}" in
	clean)
		docker-compose -f compose-1.yml -f compose-2.yml -f compose-3.yml down --volumes
		rm -rf .build
		;;
	stop)
		stopService with-logs
		;;
	start)
		stopService
		generateKeys
		setupCLI
		startCommand
		waitForReady
		setupFollowers
		generateAgentServices
		sleep 5
		createDID
		;;
	logs)
		docker-compose -f compose-1.yml -f compose-2.yml -f compose-3.yml logs -f -t
		;;
	create)
		generateAgentServices
		echo $(createDID)
		;;
	*)
		echo "orb: valid commands are 'clean' 'start' 'stop' 'logs'"
		;;
esac

popd > /dev/null # to caller
