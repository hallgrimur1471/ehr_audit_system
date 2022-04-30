from http import server
import json
from base64 import b64encode
from pathlib import Path

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

from audit_server.audit_record import AuditRecord
import audit_server.audit_companies as audit_companies


def encrypt_record(record: AuditRecord, patient: str):
    # The encrypted record should look similar to this:
    # {
    #     "patient_enc": {
    #         "ciphertext": "...",
    #         "ciphertext_tag": "...",
    #         "key_enc": "...", // encrypted with audit_server's public key
    #         "key_enc_signature": "..." // signed by audit_server
    #     },
    #     "ehr_action_enc": {
    #         "ciphertext": "...",
    #         "ciphertext_tag": "...",
    #         "for_patient": {
    #             "key_enc": "...", // encrypted with patient's public key
    #             "key_enc_signature": "..." // signed by audit_server
    #         },
    #         "for_audit_company": {
    #             "key_enc": "...", // encrypted with audit company's public key
    #             "key_enc_signature": "..." // signed by audit_server
    #         }
    #     }
    # }
    db_entry = {
        "patient_enc": get_patient_enc(patient),
        "ehr_action_enc": get_ehr_action_enc(record, patient),
    }
    return db_entry


def get_patient_enc(patient):
    patient_enc = {}

    # Generate a random key for symmetric encryption
    ks = get_random_bytes(32)

    # Encrypt patient using symmetric encryption
    cipher = AES.new(ks, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(patient.encode())
    patient_enc["ciphertext"] = b64encode(ciphertext).decode()
    patient_enc["ciphertext_tag"] = b64encode(tag).decode()

    # Encrypt the symmetric key using server's RSA encryption public key
    server_rsa_pubkey_for_encryption = get_server_rsa_pubkey_for_encryption()
    cipher = PKCS1_OAEP.new(server_rsa_pubkey_for_encryption)
    key_enc = cipher.encrypt(ks)
    patient_enc["key_enc"] = b64encode(key_enc).decode()

    # Sign key_enc to protect against tampering with key_enc
    server_rsa_pubkey_for_signing = get_server_rsa_pubkey_for_signing()
    hash = SHA256.new(key_enc)
    key_enc_signature = pss.new(server_rsa_pubkey_for_signing).sign(hash)
    patient_enc["key_enc_signature"] = b64encode(key_enc_signature).decode()

    return patient_enc


def get_ehr_action_enc(record, patient):
    ehr_action_enc = {}

    # Generate a random key for symmetric encryption
    ks = get_random_bytes(32)

    # Encrypt record using symmetric encryption
    cipher = AES.new(ks, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(str(record).encode())
    ehr_action_enc["ciphertext"] = b64encode(ciphertext).decode()
    ehr_action_enc["ciphertext_tag"] = b64encode(tag).decode()

    # Encrypt the symmetric key using patient's RSA encryption public key
    patient_rsa_pubkey_for_encryption = get_rsa_encryption_pubkey(patient)
    cipher = PKCS1_OAEP.new(patient_rsa_pubkey_for_encryption)
    key_enc = cipher.encrypt(ks)
    ehr_action_enc["for_patient"] = {}
    ehr_action_enc["for_patient"]["key_enc"] = b64encode(key_enc).decode()

    # Sign key_enc to protect against tampering with key_enc
    server_rsa_pubkey_for_signing = get_server_rsa_pubkey_for_signing()
    hash = SHA256.new(key_enc)
    key_enc_signature = pss.new(server_rsa_pubkey_for_signing).sign(hash)
    ehr_action_enc["for_patient"]["key_enc_signature"] = b64encode(
        key_enc_signature
    ).decode()

    # Encrypt the symmetric key using audit company's RSA encryption public key
    audit_company = audit_companies.get_company_of(patient)
    patient_rsa_pubkey_for_encryption = get_rsa_encryption_pubkey(audit_company)
    cipher = PKCS1_OAEP.new(patient_rsa_pubkey_for_encryption)
    key_enc = cipher.encrypt(ks)
    ehr_action_enc["for_audit_company"] = {}
    ehr_action_enc["for_audit_company"]["key_enc"] = b64encode(key_enc).decode()

    # Sign key_enc to protect against tampering with key_enc
    server_rsa_pubkey_for_signing = get_server_rsa_pubkey_for_signing()
    hash = SHA256.new(key_enc)
    key_enc_signature = pss.new(server_rsa_pubkey_for_signing).sign(hash)
    ehr_action_enc["for_audit_company"]["key_enc_signature"] = b64encode(
        key_enc_signature
    ).decode()

    return ehr_action_enc


def get_rsa_encryption_pubkey(entity):
    audit_server_dir = Path(__file__).absolute().parent.parent.parent
    pubkey_dir = audit_server_dir / "keys/known_pubkeys"
    sub_dirs = [dir_.name for dir_ in pubkey_dir.iterdir() if dir_.is_dir()]

    if entity not in sub_dirs:
        raise RuntimeError(f"Could not find pubkey directory for '{entity}'")

    pubkey_path = pubkey_dir / f"{entity}/rsa_encrypt.pem"
    if not pubkey_path.exists():
        raise RuntimeError(f"Could not find the pubkey '{pubkey_path.name}'")

    pubkey = RSA.import_key(pubkey_path.read_bytes())

    return pubkey


def get_server_rsa_pubkey_for_encryption():
    pubkey_path = get_server_keys_dir() / "rsa_encrypt.pem"
    pubkey = RSA.import_key(pubkey_path.read_bytes())
    return pubkey


def get_server_rsa_pubkey_for_signing():
    pubkey_path = get_server_keys_dir() / "rsa_sign.pem"
    pubkey = RSA.import_key(pubkey_path.read_bytes())
    return pubkey


def get_server_keys_dir():
    audit_server_dir = Path(__file__).absolute().parent.parent.parent
    return audit_server_dir / "keys/server_keys"
