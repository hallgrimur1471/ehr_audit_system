#!/usr/bin/env python3

import sys
import ssl
import json
import logging
import argparse
from pathlib import Path
from base64 import b64decode
import urllib.request
from urllib.request import Request
from urllib.error import HTTPError

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import OpenSSL.crypto

AUDIT_SERVER_BASEURL = "https://audit_server:5001"


def main():
    args = parse_arguments()

    if args.verbose:
        configure_logger(logging.DEBUG)
    else:
        configure_logger(logging.INFO)

    query_usage(args.PATIENT, Path(args.USER_KEY_DIR))


def query_usage(patient: str, user_key_dir: Path):
    user_cert_file = user_key_dir / "tls.crt"
    user_key_file = user_key_dir / "tls.key"

    encrypted_records_str = audit_server_get_request(
        f"/query_usage/{patient}", user_cert_file, user_key_file
    )

    encrypted_records = json.loads(encrypted_records_str)
    is_audit_company = is_audit_company_cert_file(user_cert_file)
    records = decrypt_records(encrypted_records, is_audit_company, user_key_dir)
    print(json.dumps(records, indent=2))


def audit_server_get_request(url_path, client_cert, client_key):
    code_dir = Path(__file__).absolute().parent.parent
    ca_dir = code_dir / "ca/keys"
    ca_cert = ca_dir / "ca.crt"

    client_key_password = None

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_cert)
    context.load_cert_chain(
        certfile=client_cert, keyfile=client_key, password=client_key_password
    )

    request = Request(f"{AUDIT_SERVER_BASEURL}{url_path}", method="GET")
    try:
        with urllib.request.urlopen(request, context=context) as resp:
            encrypted_records_str = resp.read().decode()
    except HTTPError as err:
        logging.error(
            "Failed to get records, audit_server responded with HTTP returncode "
            + f"{err.code} and the message: {err.read().decode().rstrip()}"
        )
        sys.exit(1)

    return encrypted_records_str


def decrypt_records(encrypted_records, is_audit_company, user_key_dir):
    return [
        decrypt_record(record, is_audit_company, user_key_dir)
        for record in encrypted_records
    ]


def decrypt_record(encrypted_record, is_audit_company, user_key_dir):
    # encrypted_record looks similar to this:
    #
    #   {
    #     "ciphertext": "...",
    #     "ciphertext_tag": "...",
    #     "ciphertext_nonce": "...",
    #     "for_patient": {
    #       "key_enc": "...",
    #       "key_enc_signature": "..."
    #     },
    #     "for_audit_company": {
    #       "key_enc": "...",
    #       "key_enc_signature": "..."
    #     }
    #   }

    if is_audit_company:
        dict_key = "for_audit_company"
    else:
        dict_key = "for_patient"

    key_enc = b64decode(encrypted_record[dict_key]["key_enc"])
    key_enc_signature = b64decode(encrypted_record[dict_key]["key_enc_signature"])

    server_rsa_key_for_verifying = get_key("audit_server_rsa_verify.pem", user_key_dir)

    # Verify key_enc_signature
    hash = SHA256.new(key_enc)
    signature = key_enc_signature
    verifier = pss.new(server_rsa_key_for_verifying)
    try:
        verifier.verify(hash, signature)
    except (ValueError, TypeError):
        notify_relevent_authorities_of_record_tampering()
        raise RuntimeError(
            "It was detected that a record has been tampered with, "
            + "relevant authorities have been notified"
        )

    # Decrypt key_enc
    user_rsa_key_for_decrypting = get_key("rsa_decrypt.pem", user_key_dir)

    # Decrypt and verify ciphertext
    cipher = PKCS1_OAEP.new(user_rsa_key_for_decrypting)
    ks = cipher.decrypt(key_enc)

    try:
        nonce = b64decode(encrypted_record["ciphertext_nonce"])
        cipher = AES.new(ks, AES.MODE_GCM, nonce=nonce)
        ciphertext = b64decode(encrypted_record["ciphertext"])
        tag = b64decode(encrypted_record["ciphertext_tag"])
        record_str = cipher.decrypt_and_verify(ciphertext, tag).decode()
    except (ValueError, KeyError):
        notify_relevent_authorities_of_record_tampering()
        raise RuntimeError(
            "It was detected that record has been tampered with, "
            + "relevant authorities have been notified"
        )

    record = json.loads(record_str)
    return record


def is_audit_company_cert_file(cert_file):
    cert = OpenSSL.crypto.load_certificate(
        OpenSSL.crypto.FILETYPE_PEM, cert_file.read_bytes()
    )
    client_id = cert.get_subject().commonName

    audit_companies = {"usc", "ucla"}
    return client_id in audit_companies


def get_key(filename, user_key_dir):
    key_path = user_key_dir / filename
    key = RSA.import_key(key_path.read_bytes())
    return key


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.description = "Query EHR usage for patient"
    parser.add_argument("PATIENT", help=f"Patient to fetch EHR usage about")
    parser.add_argument(
        "USER_KEY_DIR",
        help=f"A directory with the keys user should have received from a system admin.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enables printing of debug statements",
    )
    arguments = parser.parse_args()

    # Validate key directory and its contents
    key_dir = Path(arguments.USER_KEY_DIR)
    if not key_dir.exists():
        raise ValueError(f"USER_KEY_DIR '{key_dir}' does not exist.")
    if not key_dir.is_dir():
        raise ValueError(f"USER_KEY_DIR '{key_dir}' is not a directory.")
    files = [file_.name for file_ in key_dir.iterdir()]
    required_files = ["tls.key", "tls.crt", "rsa_encrypt.pem", "rsa_decrypt.pem"]
    for required_file in required_files:
        if required_file not in files:
            raise ValueError(f"USER_KEY_DIR must include the file '{required_file}'")

    return arguments


def configure_logger(log_level):
    logging.basicConfig(
        format="[%(asctime)s.%(msecs)03d %(levelname)s]: %(message)s",
        datefmt="%H:%M:%S",
        level=log_level,
    )


def notify_relevent_authorities_of_record_tampering():
    # Not implemented in this project
    pass


if __name__ == "__main__":
    main()
