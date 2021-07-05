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
DNS.4 = orb2.domain1.com" >> "$tmp"

#create CA
openssl ecparam -name prime256v1 -genkey -noout -out .build/keys/tls/ec-cakey.pem
openssl req -new -x509 -key .build/keys/tls/ec-cakey.pem -subj "/C=CA/ST=ON/O=Example Internet CA Inc.:CA Sec/OU=CA Sec" -out .build/keys/tls/ec-cacert.pem

#create TLS creds
openssl ecparam -name prime256v1 -genkey -noout -out .build/keys/tls/ec-key.pem
openssl req -new -key .build/keys/tls/ec-key.pem -subj "/C=CA/ST=ON/O=Example Inc.:orb/OU=orb/CN=localhost" -out .build/keys/tls/ec-key.csr
openssl x509 -req -in .build/keys/tls/ec-key.csr -CA .build/keys/tls/ec-cacert.pem -CAkey .build/keys/tls/ec-cakey.pem -CAcreateserial -extfile "$tmp" -out .build/keys/tls/ec-pubCert.pem -days 365


# generate key pair for recover/updates
mkdir -p .build/keys/recover
mkdir -p .build/keys/update

openssl ecparam -name prime256v1 -genkey -noout -out .build/keys/recover/key.pem
openssl ec -in .build/keys/recover/key.pem -passout pass:123 -out .build/keys/recover/key_encrypted.pem -aes256
openssl ec -in .build/keys/recover/key.pem -pubout -out .build/keys/recover/public.pem

openssl ecparam -name prime256v1 -genkey -noout -out .build/keys/update/key.pem
openssl ec -in .build/keys/update/key.pem -passout pass:123 -out .build/keys/update/key_encrypted.pem -aes256
openssl ec -in .build/keys/update/key.pem -pubout -out .build/keys/update/public.pem

echo "done generating orb PKI"
