#!/usr/bin/env python3

import logging
import argparse
import subprocess
from pathlib import Path

from Crypto.PublicKey import RSA


def main():
    args = parse_arguments()

    if args.verbose:
        configure_logger(logging.DEBUG)
    else:
        configure_logger(logging.INFO)

    generate_keys(args.USER_ID)


def generate_keys(user_id):
    key_dir = Path(__file__).parent.absolute() / f"keys/{user_id}"
    ca_dir = Path(__file__).parent.parent.absolute() / "ca/keys"

    key_dir.mkdir(exist_ok=True, parents=True)

    generate_tls_keys(user_id, key_dir, ca_dir)
    generate_encryption_decryption_keys(user_id, key_dir)


def generate_tls_keys(user_id, key_dir, ca_dir):
    user_key_filename = f"tls.key"
    user_csr_filename = f"tls.csr"  # csr: certificate signing request
    user_cert_filename = f"tls.crt"
    user_domain = user_id

    ca_key_path = ca_dir / "ca.key"
    ca_cert_path = ca_dir / "ca.crt"

    logging.info("Generating user TLS key ...")
    subprocess.run(
        f"openssl genrsa -out {user_key_filename} 2048",
        shell=True,
        check=True,
        cwd=key_dir,
    )

    logging.info("Creating a certificate signing request ...")
    subprocess.run(
        f"openssl req -new -key {user_key_filename} -out {user_csr_filename} "
        + f'-subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN={user_domain}"',
        shell=True,
        check=True,
        cwd=key_dir,
    )

    logging.info("Creating user certificate ...")
    subprocess.run(
        f"openssl x509 -req -in {user_csr_filename} -CA {ca_cert_path} "
        + f"-CAkey {ca_key_path} -CAcreateserial "
        + f"-out {user_cert_filename} -days 1024 -sha256",
        shell=True,
        check=True,
        cwd=key_dir,
    )

    # Now since user's certificate has been signed by the CA, the csr can be deleted
    subprocess.run(f"rm {user_csr_filename}", shell=True, check=True, cwd=key_dir)

    logging.info(
        "TLS key and cert generated. "
        + f"Private key: '{user_key_filename}', "
        + f"certificate: '{user_cert_filename}'"
    )


def generate_encryption_decryption_keys(user_id, key_dir):
    private_key_filename = f"rsa_decrypt.pem"
    public_key_filename = f"rsa_encrypt.pem"
    generate_rsa_keys(2048, private_key_filename, public_key_filename, key_dir)


def generate_rsa_keys(size_bits, private_key_filename, public_key_filename, key_dir):
    keypair = RSA.generate(size_bits)

    # Export private key
    with open(key_dir / private_key_filename, "wb") as f:
        f.write(keypair.export_key(format="PEM"))

    # Export public key
    with open(key_dir / public_key_filename, "wb") as f:
        f.write(keypair.public_key().export_key(format="PEM"))

    logging.info(
        f"RSA keypair generated. Private key: '{private_key_filename}', "
        + f"public key: '{public_key_filename}'"
    )


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.description = (
        "Generate RSA keypair for a user "
        + "along with a TLS key and cert signed by a CA"
    )
    parser.add_argument("USER_ID", type=str, help="User to generate keys for")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enables printing of debug statements",
    )
    arguments = parser.parse_args()
    return arguments


def configure_logger(log_level):
    logging.basicConfig(
        format="[%(asctime)s.%(msecs)03d %(levelname)s]: %(message)s",
        datefmt="%H:%M:%S",
        level=log_level,
    )


if __name__ == "__main__":
    main()
