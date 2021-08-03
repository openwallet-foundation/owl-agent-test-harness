#!/bin/bash

set -o pipefail

ANSII_GREEN='\u001b[32m'
ANSII_RESET='\x1b[0m'

# Handle ctrl-C to exit the application
trap_ctrlC() {
    if [ -n "$NGROK_PID" ]; then
        kill "$NGROK_PID"
    fi
    exit 1
}
trap trap_ctrlC SIGINT SIGTERM

provision() {
  echo
  echo "***************************   PROVISIONING    ************************"

  # AATH requires to be run agains a VON Network
  NETWORK="von"
  TXN_FILE="von.txn"

  echo
  echo "*********Env Variables**********"
  printenv
  echo

  # Handle run mode environment variables
  run_mode="$RUN_MODE"
  docker_host="host.docker.internal"
  if [ ! -z "$DOCKERHOST" ] ; then 
    docker_host="$DOCKERHOST"
  fi
  external_host="localhost"
  if [ "$run_mode" == "docker" ] ; then
    external_host=docker_host
  fi

  # Get the genesis file for the ledger
  echo
  echo "Getting Genesis Transactions"
  echo

  echo "Ledger URL: $LEDGER_URL"
  ledger_url="$LEDGER_URL"
  if [ ! -z "$GENESIS_FILE" ] ; then
    echo "Received Genesis file"
    echo $GENESIS_FILE > /etc/verity/verity-application/von.txn
  elif [ ! -z "$GENESIS_URL" ] ; then
    echo "Retrieving genesis txns from genesis url: ${GENESIS_URL}"
    curl $GENESIS_URL > /etc/verity/verity-application/von.txn
  elif [ ! -z "$LEDGER_URL" ] ; then 
    echo "Retrieving genesis txns from ${ledger_url}/genesis"
    curl ${ledger_url}/genesis > /etc/verity/verity-application/von.txn
  else
    TXN_FILE="local-genesis.txn"
  fi
  
  echo
  echo "*******GENESIS TRANSACTIONS********"
  cat /etc/verity/verity-application/von.txn
  echo

  # Generate a random seed
  VERITY_SEED=$(date +%s | md5sum | base64 | head -c 32)

  export TXN_FILE
  DATE=$(date +%F)
  export TAA_ACCEPTANCE=$DATE
  export TAA_HASH="N/A"
  export TAA_VERSION="N/A"

  # Create DID/Verkey based on the provided VERITY_SEED 
  printf "wallet create test key=test\nwallet open test key=test\ndid new seed=%s" "${VERITY_SEED}" | indy-cli | tee /tmp/indy_cli_output.txt
  echo

  # Register Verity DID/Verkey on the ledger via VON-Network Registration endpoint
  ledger_url="http://${external_host}:9000"
  if [ ! -z "$LEDGER_URL" ] ; then 
    ledger_url="$LEDGER_URL"
  fi

  DID=`grep verkey /tmp/indy_cli_output.txt |awk '{print $2}'`
  VERKEY=`grep verkey /tmp/indy_cli_output.txt |awk '{print $7}'`

  echo "Writing did and verkey to ${ledger_url}/register"
  echo "Posting {\"alias\":\"verity\",\"did\":$DID,\"verkey\":$VERKEY, \"role\":\"ENDORSER\"} to ${ledger_url}/register"
  curl -d "{\"alias\":\"verity\",\"did\":$DID,\"verkey\":$VERKEY, \"role\":\"ENDORSER\"}" -X POST ${ledger_url}/register

  # Write out TAA configruation to the file
  echo "verity.lib-indy.ledger.transaction_author_agreement.agreements = {\"${TAA_VERSION}\" = { digest = \${?TAA_HASH}, mechanism = on_file, time-of-acceptance = \${?TAA_ACCEPTANCE}}}" > /etc/verity/verity-application/taa.conf

  # Generate random logo
  ROBO_HASH=$(date +%s | md5sum | base64 | head -c 8)
  export LOGO_URL="http://robohash.org/${ROBO_HASH}"
}

start_ngrok() {
  ngrok http ${AGENT_PORT} >> /dev/null &
  NGROK_PID=$!
  until curl -m 1 -q http://127.0.0.1:4040/api/tunnels 2> /dev/null | jq -M -r -e '.tunnels[0].public_url' > /dev/null 2>&1
  do
    echo -n "."
    sleep 1
  done
}

print_config() {
  echo "******************        VERITY PARAMETERS         ******************"
  echo "VERITY_SEED=$VERITY_SEED"
  echo "NETWORK=$NETWORK"
  echo "TXN_FILE=${TXN_FILE}"
  echo "**********************************************************************"
  echo
}

print_license() {
  echo
  echo "***********************        LICENSE         ***********************"
  echo "Verity application is available under the Business Source License"
  printf "${ANSII_GREEN}https://github.com/evernym/verity/blob/master/LICENSE.txt${ANSII_RESET}\n"
  echo "Please contact Evernym if you have any questions regarding Verity licensing"
  echo "**********************************************************************"
  echo
}

start_verity() {

  print_license

  provision

  print_config

  echo "**********************       VERITY STARTUP         ******************"
  # If public URL for docker Host is not specified start Ngrok tunnel to obtain public Verity Application endpoint
  echo -n Starting ngrok..
  start_ngrok
  export HOST_ADDRESS=$(curl -m 1 -s http://127.0.0.1:4040/api/tunnels 2> /dev/null | jq -M -r '.tunnels[0].public_url')

  export HOST_DOMAIN=`echo $HOST_ADDRESS |  cut -d'/' -f3`

  echo
  printf "Verity Endpoint is: ${ANSII_GREEN}${HOST_ADDRESS}${ANSII_RESET}"
  echo

  # Start Verity Application
  /usr/bin/java -cp /etc/verity/verity-application:.m2/repository/org/fusesource/leveldbjni/leveldbjni-all/1.8/leveldbjni-all-1.8.jar:./verity-assembly-0.4.0-SNAPSHOT.jar \
  com.evernym.verity.Main &

  echo
  echo -n "Waiting for Verity to start listening"
  until curl 127.0.0.1:${AGENT_PORT}/agency > /dev/null 2>&1
  do
      echo -n "."
      sleep 1
  done
  echo

  # Bootstrap Verity Application with seed
  if [ -z "$BOOTSTRAP" ]; then
    echo "Bootstrapping Verity"
    echo
    echo "Verity Setup"
    curl -f -H "Content-Type: application/json" -X POST http://127.0.0.1:${AGENT_PORT}/agency/internal/setup/key \
    -d "{\"seed\":\"$VERITY_SEED\"}" || exit 1
    echo; echo
    echo "Verity Endpoint Setup"
    curl -f -X POST http://127.0.0.1:${AGENT_PORT}/agency/internal/setup/endpoint || exit 1
    echo; echo
    echo "Verity Bootstrapping complete."
  fi

  echo "Verity application started."
  echo "**********************************************************************"
  echo
}

start_verity

