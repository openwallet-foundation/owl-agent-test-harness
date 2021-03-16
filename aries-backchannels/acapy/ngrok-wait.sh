#!/bin/bash

# based on code developed by Sovrin:  https://github.com/hyperledger/aries-acapy-plugin-toolbox

if [[ ! "${NGROK_NAME}" = "" ]]; then
    echo "using ngrok end point [$NGROK_NAME]"

    NGROK_ENDPOINT=null
    while [ -z "$NGROK_ENDPOINT" ] || [ "$NGROK_ENDPOINT" = "null" ]
    do
        echo "Fetching end point from ngrok service"
        NGROK_ENDPOINT=$(curl --silent $NGROK_NAME:4040/api/tunnels | ./jq -r '.tunnels[] | select(.proto=="https") | .public_url')

        if [ -z "$NGROK_ENDPOINT" ] || [ "$NGROK_ENDPOINT" = "null" ]; then
            echo "ngrok not ready, sleeping 5 seconds...."
            sleep 5
        fi
    done

    export AGENT_PUBLIC_ENDPOINT=$NGROK_ENDPOINT
    echo "fetched end point [$AGENT_PUBLIC_ENDPOINT]"
fi

echo "Starting aca-py agent ..."

python acapy/acapy_backchannel.py "$@"
