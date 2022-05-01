#!/usr/bin/env bash

# NOTE: this script is just a shortcut to regenerate some data
#       consider doing things manually instead.

python3 generate_keys_for_server.py audit_server
for user in alice bob carol david eve usc ucla; do
    python3 generate_keys_for_user.py $user;
    cp keys/audit_server/rsa_verify.pem keys/${user}/audit_server_rsa_verify.pem
done

# Move audit_server keys
rsync -avP keys/audit_server/ ../audit_server/keys/server_keys
rm -rf keys/audit_server

# Add client pubkeys to audit_server
for user in alice bob carol david eve usc ucla; do
    cp keys/${user}/rsa_encrypt.pem ../audit_server/keys/known_pubkeys/${user}/
done
rm -rf ../audit_client/keys


mv keys ../audit_client/keys
rm ../audit_server/audit_db.json
rm ../ehr_server/ehr_db.json

echo "{}" > ../ehr_server/ehr_db.json
echo "[]" > ../audit_server/audit_db.json

(cd ../doctor_client; ./ehr.py CREATE alice mark --description "Visit 1")
(cd ../doctor_client; ./ehr.py CREATE alice mark --description "Visit 2")
(cd ../doctor_client; ./ehr.py CREATE alice mark --description "Visit 3")
(cd ../doctor_client; ./ehr.py CREATE bob john --description "Visit 1")
(cd ../doctor_client; ./ehr.py CREATE bob john --description "Visit 2")