#!/bin/bash

# based on code developed by Sovrin:  https://github.com/hyperledger/aries-acapy-plugin-toolbox

if [[ ! "${NGROK_NAME}" = "" ]]; then
    echo "using ngrok end point [$NGROK_NAME]"

    NGROK_ENDPOINT=null
    while [ -z "$NGROK_ENDPOINT" ] || [ "$NGROK_ENDPOINT" = "null" ]
    do
        echo "Fetching end point from ngrok service"
        NGROK_ENDPOINT=$(curl -s $NGROK_NAME:4040/api/tunnels/command_line | grep -o "https:\/\/.*\.ngrok\.io")

        if [ -z "$NGROK_ENDPOINT" ] || [ "$NGROK_ENDPOINT" = "null" ]; then
            echo "ngrok not ready, sleeping 5 seconds...."
            sleep 5
        fi
    done

    export AGENT_PUBLIC_ENDPOINT=$NGROK_ENDPOINT
    echo "fetched end point [$AGENT_PUBLIC_ENDPOINT]"
fi

echo "Starting AFJ agent ..."

yarn ts-node src/index.ts "$@"
