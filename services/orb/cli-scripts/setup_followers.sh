#!/usr/bin/env bash

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"

cd ${SCRIPT_HOME}/../

domain1=https://orb.domain1.com/services/orb
domain2=https://orb.domain2.com/services/orb

domain1External=https://localhost:48326/services/orb
domain2External=https://localhost:48426/services/orb

CURL_CA_BUNDLE=.build/keys/tls/ec-cacert.pem

followID=$(cat /proc/sys/kernel/random/uuid)

curl -d "{\
  \"@context\":\"https://www.w3.org/ns/activitystreams\",\
  \"id\":\"${domain2}/activities/${followID}\",\
  \"type\":\"Follow\",\
  \"actor\":\"${domain2}\",\
  \"to\":\"${domain1}\",\
  \"object\":\"${domain1}\"\
}" \
  -H "Content-Type: application/json" -H "Authorization: Bearer ADMIN_TOKEN" -X POST -k ${domain2External}/outbox

followID=$(cat /proc/sys/kernel/random/uuid)

curl -d "{\
  \"@context\":\"https://www.w3.org/ns/activitystreams\",\
  \"id\":\"${domain1}/activities/${followID}\",\
  \"type\":\"Follow\",\
  \"actor\":\"${domain1}\",\
  \"to\":\"${domain2}\",\
  \"object\":\"${domain2}\"\
}" \
  -H "Content-Type: application/json" -H "Authorization: Bearer ADMIN_TOKEN" -X POST -k ${domain1External}/outbox

inviteWitnessID=$(cat /proc/sys/kernel/random/uuid)

curl -d "{\
  \"@context\":[\"https://www.w3.org/ns/activitystreams\",\"https://trustbloc.github.io/did-method-orb/contexts/anchor/v1\"],\
  \"id\":\"${domain1}/activities/${inviteWitnessID}\",\
  \"type\":\"InviteWitness\",\
  \"actor\":\"${domain1}\",\
  \"to\":\"${domain2}\",\
  \"object\":\"${domain2}\"\
}" \
  -H "Content-Type: application/json" -H "Authorization: Bearer ADMIN_TOKEN" -X POST -k ${domain1External}/outbox


inviteWitnessID=$(cat /proc/sys/kernel/random/uuid)

curl -d "{\
  \"@context\":[\"https://www.w3.org/ns/activitystreams\",\"https://trustbloc.github.io/did-method-orb/contexts/anchor/v1\"],\
  \"id\":\"${domain2}/activities/${inviteWitnessID}\",\
  \"type\":\"InviteWitness\",\
  \"actor\":\"${domain2}\",\
  \"to\":\"${domain1}\",\
  \"object\":\"${domain1}\"\
}" \
  -H "Content-Type: application/json" -H "Authorization: Bearer ADMIN_TOKEN" -X POST -k ${domain2External}/outbox

echo
