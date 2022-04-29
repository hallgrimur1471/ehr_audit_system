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

    create_ca()


def create_ca():
    ca_dir = Path(__file__).parent.absolute() / "ca"
    ca_dir.mkdir(exist_ok=True)

    create_ca_key("ca.key", ca_dir)
    create_ca_certificate("ca.crt", "ca.key", ca_dir)


def create_ca_key(key_filename, ca_dir):
    subprocess.run(
        f"openssl genrsa -out {key_filename} 2048", shell=True, check=True, cwd=ca_dir
    )

    logging.info(f"Created CA key '{ca_dir / key_filename}'")


def create_ca_certificate(cert_filename, key_filename, ca_dir):
    subprocess.run(
        f"openssl req -x509 -new -nodes -key {key_filename} -sha256 -days 1024 "
        + f"-out {cert_filename} "
        + '-subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=certificate-authority"',
        shell=True,
        check=True,
        cwd=ca_dir,
    )

    logging.info(f"Create CA certificate '{ca_dir / cert_filename}'")


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
    parser.description = "Creates a certificate authority key and certificate."
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
