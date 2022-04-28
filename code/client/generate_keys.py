#!/usr/bin/env python3

import logging
import argparse
from pathlib import Path

from Crypto.PublicKey import RSA


def main():
    args = parse_arguments()

    if args.verbose:
        configure_logger(logging.DEBUG)
    else:
        configure_logger(logging.INFO)

    generate_keys()


def generate_keys():
    generate_encryption_decryption_keys()
    generate_sign_verify_keys()


def generate_encryption_decryption_keys():
    generate_rsa_keys(2048, "sign.pem", "verify.pem")


def generate_sign_verify_keys():
    generate_rsa_keys(2048, "encrypt.pem", "decrypt.pem")


def generate_rsa_keys(size_bits, private_key_filename, public_key_filename):
    keypair = RSA.generate(size_bits)

    # Export private key
    with open(private_key_filename, "wb") as f:
        f.write(keypair.export_key(format="PEM"))

    # Export public key
    with open(public_key_filename, "wb") as f:
        f.write(keypair.public_key().export_key(format="PEM"))

    logging.info(
        f"RSA keypair generated. Private key: '{private_key_filename}', "
        + f"public key: '{public_key_filename}'"
    )


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.description = (
        "Generate two sets of RSA public and private keys, "
        + "one set for signing and verification, "
        + "the other set of encryption an decryption."
    )
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
