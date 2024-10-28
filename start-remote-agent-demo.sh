#!/bin/bash
# set -x

. /dev/stdin <<<"$(cat <(curl -s --raw https://raw.githubusercontent.com/bcgov/DITP-DevOps/main/code/snippets/getDockerHost))"
export DOCKERHOST=$(getDockerHost)
SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"

  # generate acapy plugin config file, writing $DOCKERHOST into URLs
pushd ${SCRIPT_HOME}/aries-backchannels/acapy/ > /dev/null

mkdir -p .build/acapy-main.data
mkdir -p .build/acapy.data

sed "s/REPLACE_WITH_DOCKERHOST/${DOCKERHOST}/g" plugin-config.template | tee > .build/plugin-config.yml

rm -f .build/acapy-main.data/plugin-config.yml .build/acapy.data/plugin-config.yml
cp .build/plugin-config.yml .build/acapy-main.data/plugin-config.yml
mv .build/plugin-config.yml .build/acapy.data/plugin-config.yml

popd > /dev/null

docker run -dt --name "fred_agent" --expose "9030-9039" -p "9030-9039:9030-9039" -v $PWD/aries-backchannels/acapy/.build/acapy-main.data:/data-mount:z --env-file=aries-backchannels/acapy/acapy-main.env -e AGENT_NAME=Fred -e LEDGER_URL=http://test.bcovrin.vonx.io -e TAILS_SERVER_URL=https://tails.vonx.io -e DOCKERHOST=$DOCKERHOST -e CONTAINER_NAME=fred_agent "acapy-main-agent-backchannel" -p "9031" -i false