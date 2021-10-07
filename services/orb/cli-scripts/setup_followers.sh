#!/usr/bin/env bash

random_string() {
  base64 /dev/urandom | tr -d '/+' | head -c 32
}

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"

cd ${SCRIPT_HOME}/../

domain1=https://orb.domain1.com/services/orb
domain2=https://orb.domain2.com/services/orb

domain1External=https://localhost:48326/services/orb
domain2External=https://localhost:48426/services/orb

CURL_CA_BUNDLE=.build/keys/tls/ec-cacert.pem

curl -d "$(cat <<EOF
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/activityanchors/v1"
  ],
  "id": "https://orb.domain1.com/services/orb/activities/77bdd005-bbb6-223d-b889-58bc1de84985",
  "type": "Create",
  "actor": "https://orb.domain1.com/services/orb",
  "to": [
    "https://orb.domain1.com/services/orb/followers",
    "https://www.w3.org/ns/activitystreams#Public"
  ],
  "published": "2021-03-31T09:30:10Z",
  "object": {
    "@context": [
      "https://www.w3.org/ns/activitystreams",
      "https://w3id.org/activityanchors/v1"
    ],
    "id": "https://orb.domain1.com/transactions/uEiB0I06Yr-dJj7Xa8fNqwteKzDOUZPlQcDuMAZiS-YK5Cw",
    "type": "AnchorCredentialReference",
    "target": {
      "type": "ContentAddressedStorage",
      "id": "https://orb.domain1.com/cas/uEiB0I06Yr-dJj7Xa8fNqwteKzDOUZPlQcDuMAZiS-YK5Cw",
      "cid": "hl:uEiB0I06Yr-dJj7Xa8fNqwteKzDOUZPlQcDuMAZiS-YK5Cw:uoQ-BeEtodHRwczovL29yYi5kb21haW4xLmNvbS9jYXMvdUVpQjBJMDZZci1kSmo3WGE4Zk5xd3RlS3pET1VaUGxRY0R1TUFaaVMtWUs1Q3c"
    }
  }
}
EOF
)" -H "Content-Type: application/json" -H "Authorization: Bearer ADMIN_TOKEN" -X POST -k ${domain1External}/outbox

followID=$(random_string)

curl -d "$(cat <<EOF
{
  "@context":"https://www.w3.org/ns/activitystreams",
  "id":"${domain2}/activities/${followID}",
  "type":"Follow",
  "actor":"${domain2}",
  "to":"${domain1}",
  "object":"${domain1}"
}
EOF
)" \
  -H "Content-Type: application/json" -H "Authorization: Bearer ADMIN_TOKEN" -X POST -k ${domain2External}/outbox

followID=$(random_string)


curl -d "$(cat <<EOF
{
  "@context":"https://www.w3.org/ns/activitystreams",
  "id":"${domain1}/activities/${followID}",
  "type":"Follow",
  "actor":"${domain1}",
  "to":"${domain2}",
  "object":"${domain2}"
}
EOF
)" \
  -H "Content-Type: application/json" -H "Authorization: Bearer ADMIN_TOKEN" -X POST -k ${domain1External}/outbox

inviteWitnessID=$(random_string)


curl -d "$(cat <<EOF
{
  "@context":["https://www.w3.org/ns/activitystreams","https://w3id.org/activityanchors/v1"],
  "id":"${domain1}/activities/${inviteWitnessID}",
  "type":"Invite",
  "actor":"${domain1}",
  "to":"${domain2}",
  "object":"https://w3id.org/activityanchors#AnchorWitness",
  "target":"${domain2}"
}
EOF
)" \
  -H "Content-Type: application/json" -H "Authorization: Bearer ADMIN_TOKEN" -X POST -k ${domain1External}/outbox

inviteWitnessID=$(random_string)

curl -d "$(cat <<EOF
{
  "@context":["https://www.w3.org/ns/activitystreams","https://w3id.org/activityanchors/v1"],
  "id":"${domain2}/activities/${inviteWitnessID}",
  "type":"Invite",
  "actor":"${domain2}",
  "to":"${domain1}",
  "object":"https://w3id.org/activityanchors#AnchorWitness",
  "target":"${domain1}"
}
EOF
)" \
  -H "Content-Type: application/json" -H "Authorization: Bearer ADMIN_TOKEN" -X POST -k ${domain2External}/outbox

echo
