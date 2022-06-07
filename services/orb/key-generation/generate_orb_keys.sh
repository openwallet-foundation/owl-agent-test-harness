#!/bin/sh
#
# Copyright SecureKey Technologies Inc. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

set -e

echo "Generating orb Test PKI"

cd /opt/workspace/orb
mkdir -p .build/keys/tls
cd .build

tmp=$(mktemp)
echo "subjectKeyIdentifier=hash
authorityKeyIdentifier = keyid,issuer
extendedKeyUsage = serverAuth
keyUsage = Digital Signature, Key Encipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = localhost
DNS.2 = orb.domain1.com
DNS.3 = orb.domain2.com
DNS.4 = orb2.domain1.com
DNS.5 = orb.file-server.com
DNS.6 = orb.kms" >> "$tmp"

export RANDFILE=./.rnd

#create CA
openssl ecparam -name prime256v1 -genkey -noout -out keys/tls/ec-cakey.pem
openssl req -new -x509 -key keys/tls/ec-cakey.pem -subj "/C=CA/ST=ON/O=Example Internet CA Inc.:CA Sec/OU=CA Sec" -out keys/tls/ec-cacert.pem

#create TLS creds
openssl ecparam -name prime256v1 -genkey -noout -out keys/tls/ec-key.pem
openssl req -new -key keys/tls/ec-key.pem -subj "/C=CA/ST=ON/O=Example Inc.:orb/OU=orb/CN=localhost" -out keys/tls/ec-key.csr
openssl x509 -req -in keys/tls/ec-key.csr -CA keys/tls/ec-cacert.pem -CAkey keys/tls/ec-cakey.pem -CAcreateserial -extfile "$tmp" -out keys/tls/ec-pubCert.pem -days 365


# generate keys for recover/updates
mkdir -p keys/recover
mkdir -p keys/update

mkdir -p keys/kms
openssl rand 32 | base64 | sed 's/+/-/g; s/\//_/g' > keys/kms/secret-lock.key

export agent_names="Acme Bob Faber Mallory"

for AGENT_NAME in $agent_names; do
	mkdir -p keys/recover/${AGENT_NAME}
	mkdir -p keys/update/${AGENT_NAME}

	openssl ecparam -name prime256v1 -genkey -noout -out keys/recover/${AGENT_NAME}/key.pem
	openssl ec -in keys/recover/${AGENT_NAME}/key.pem -passout pass:123 -out keys/recover/${AGENT_NAME}/key_encrypted.pem -aes256
	openssl ec -in keys/recover/${AGENT_NAME}/key.pem -pubout -out keys/recover/${AGENT_NAME}/public.pem

	openssl ecparam -name prime256v1 -genkey -noout -out keys/update/${AGENT_NAME}/key.pem
	openssl ec -in keys/update/${AGENT_NAME}/key.pem -passout pass:123 -out keys/update/${AGENT_NAME}/key_encrypted.pem -aes256
	openssl ec -in keys/update/${AGENT_NAME}/key.pem -pubout -out keys/update/${AGENT_NAME}/public.pem
done

echo "done generating orb PKI"
