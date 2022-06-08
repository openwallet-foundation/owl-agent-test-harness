#!/usr/bin/env bash

cd /etc/orb-cli

.build/orb-cli follower \
  --outbox-url=https://orb.domain2.com/services/orb/outbox \
  --actor=https://orb.domain2.com/services/orb \
  --to https://orb.domain1.com/services/orb \
  --tls-cacerts .build/keys/tls/ec-cacert.pem \
  --auth-token ADMIN_TOKEN \
  --action=Follow

agent_names=( "Acme" "Bob" "Faber" "Mallory" )

for AGENT_NAME in "${agent_names[@]}"; do
  .build/orb-cli did create \
    --domain https://orb.domain1.com \
    --did-anchor-origin https://orb.domain1.com \
    --publickey-file did-keys/create/publickeys.json \
    --sidetree-write-token ADMIN_TOKEN \
    --service-file .build/services/${AGENT_NAME}.json \
    --recoverykey-file .build/keys/recover/${AGENT_NAME}/public.pem \
    --updatekey-file .build/keys/update/${AGENT_NAME}/public.pem \
    --tls-cacerts .build/keys/tls/ec-cacert.pem \
    > .build/orb-dids/${AGENT_NAME}.json
done
