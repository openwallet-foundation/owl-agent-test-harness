#!/usr/bin/env bash

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"

cd ${SCRIPT_HOME}/../

DID_RESULT=$(.build/orb-cli did create \
  --domain https://orb.domain1.com \
  --did-anchor-origin https://orb.domain1.com/services/orb \
  --publickey-file did-keys/create/publickeys.json \
  --sidetree-write-token ADMIN_TOKEN \
  --service-file ${SERVICE_FILE} \
  --recoverykey-file .build/keys/recover/${AGENT_NAME}/public.pem \
  --updatekey-file .build/keys/update/${AGENT_NAME}/public.pem \
  --tls-cacerts .build/keys/tls/ec-cacert.pem \
  )

echo $DID_RESULT
