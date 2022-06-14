#!/bin/bash

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"
COMMAND=${1}

# If multi-step composition becomes necessary again, set ALL_COMPOSES to a string of command-line parameters for
# all of the docker-compose files, like this:
# ALL_COMPOSES=" -f compose-1.yml -f compose-2.yml -f compose-3.yml "
ALL_COMPOSES=" "

startCommand() {
	# docker-compose -f compose-1.yml up -d
	# sleep 15
	# docker-compose -f compose-2.yml up -d
	# sleep 10
	# docker-compose -f compose-3.yml up -d
	docker-compose up -d
}

generateKeys() {
	mkdir -p .build/keys/tls
	docker run ${USE_TTY} --rm \
		-v ${SCRIPT_HOME}:/opt/workspace/orb \
		--entrypoint "/opt/workspace/orb/key-generation/generate_orb_keys.sh" \
		--user "$(id -u):$(id -g)" \
		frapsoft/openssl
}

setupCLI() {
	mkdir -p .build
	pushd .build > /dev/null

	if [[ ! -f orb-cli ]]; then
		# curl -sL https://github.com/trustbloc/orb/releases/download/v1.0.0-rc.1/orb-cli-linux-amd64.tar.gz | tar -x -z -O -f - > orb-cli

		if [[ ! -f orb-cli-linux-amd64.tar.gz ]]; then
			if [[ ! -f orb-cli.zip ]]; then
				wget https://nightly.link/trustbloc/orb/actions/artifacts/260114064.zip -O orb-cli.zip
			fi

			unzip -n orb-cli.zip orb-cli-linux-amd64.tar.gz
		fi

		tar -xzf orb-cli-linux-amd64.tar.gz

		mv orb-cli-linux-amd64 orb-cli

		chmod +x orb-cli
	fi

	popd > /dev/null
}

waitForReady() {
	sleep 15
}

# getDockerHost; for details refer to https://github.com/bcgov/DITP-DevOps/tree/main/code/snippets#getdockerhost
. /dev/stdin <<<"$(cat <(curl -s --raw https://raw.githubusercontent.com/bcgov/DITP-DevOps/main/code/snippets/getDockerHost))" 
export DOCKERHOST=$(getDockerHost)

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

	docker run ${USE_TTY} --rm \
		--name "create-did" \
		-v "${SCRIPT_HOME}:/etc/orb-cli" \
		--user "$(id -u):$(id -g)" \
		-e "SERVICE_FILE=.build/services/${AGENT_NAME}.json" \
		-e "AGENT_NAME=${AGENT_NAME}" \
		--network "aath_network" \
		--entrypoint "/etc/orb-cli/cli-scripts/create_did.sh" \
		"ubuntu:20.04"

	mkdir -p $SCRIPT_HOME/../../aries-backchannels/afgo/.build/afgo-master.data
	mkdir -p $SCRIPT_HOME/../../aries-backchannels/afgo/.build/afgo-interop.data

	cp -r .build/orb-dids ../../aries-backchannels/afgo/.build/afgo-master.data
	cp -r .build/orb-dids ../../aries-backchannels/afgo/.build/afgo-interop.data

	cp -r did-keys/priv ../../aries-backchannels/afgo/.build/afgo-master.data
	cp -r did-keys/priv ../../aries-backchannels/afgo/.build/afgo-interop.data


	popd > /dev/null # to caller
}

stopService() {
	arg=$1

	docker-compose ${ALL_COMPOSES} stop

	if [[ $arg = "with-logs" ]]; then
		if [[ -n "$(docker-compose ${ALL_COMPOSES} -p aath ps -q)" ]]; then
			echo writing logs...
			docker-compose ${ALL_COMPOSES} logs > orb.log
		fi
	fi

	docker-compose ${ALL_COMPOSES} down --volumes
}

pushd ${SCRIPT_HOME} > /dev/null

case "${COMMAND}" in
	clean)
		docker-compose ${ALL_COMPOSES} down --volumes
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
		generateAgentServices
		sleep 5
		createDID
		;;
	logs)
		docker-compose ${ALL_COMPOSES} logs -f -t
		;;
	create)
		setupCLI
		generateAgentServices
		echo $(createDID)
		;;
	*)
		echo "orb: valid commands are 'clean' 'start' 'stop' 'logs'"
		;;
esac

popd > /dev/null # to caller
