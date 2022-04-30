import json
from base64 import b64encode
from pathlib import Path

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

from audit_server.audit_record import AuditRecord
import audit_server.audit_companies as audit_companies


def encrypt_record(record: AuditRecord, patient: str):
    patient_rsa_pubkey = get_rsa_pubkey(patient)

    audit_company = audit_companies.get_company_of(patient)
    audit_company_rsa_pubkey = get_rsa_pubkey(audit_company)

    entry = {}

    # Generate a random key for symmetric encryption
    ks = get_random_bytes(32)

    # Use symmetric encryption for the AuditRecord itself
    cipher = AES.new(ks, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(str(record).encode("utf-8"))
    entry["record_enc"] = {}
    entry["record_enc"]["ciphertext"] = b64encode(ciphertext).decode()
    entry["record_enc"]["tag"] = b64encode(tag).decode()

    # Encrypt the symmetric key with the patient's RSA key.
    # Patient's ID needs also to be encrypted so we do that here as well.
    # Note that RSA PKCS#1 OAEP used randomized encryption.
    cipher = PKCS1_OAEP.new(patient_rsa_pubkey)
    ciphertext = cipher.encrypt(
        json.dumps({"patient": patient, "ks": b64encode(ks).decode()}).encode()
    )
    entry["patient_and_key_enc"] = b64encode(ciphertext).decode()

    # The patient and symmetric key must be encrypted for audit company
    # access as well.
    cipher = PKCS1_OAEP.new(audit_company_rsa_pubkey)
    ciphertext = cipher.encrypt(
        json.dumps({"patient": patient, "ks": b64encode(ks).decode()}).encode()
    )
    entry["patient_and_key_enc_for_audit_company"] = b64encode(ciphertext).decode()

    return entry


def get_rsa_pubkey(entity):
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
