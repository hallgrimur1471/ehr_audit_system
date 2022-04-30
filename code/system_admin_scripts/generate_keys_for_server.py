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

    generate_tls_for_domain(args.SERVER_DOMAIN)


def generate_tls_for_domain(server_domain):
    key_dir = Path(__file__).parent.absolute() / "keys"
    ca_dir = Path(__file__).parent.parent.absolute() / "ca/keys"

    key_dir.mkdir(exist_ok=True)

    generate_tls_keys(server_domain, key_dir, ca_dir)


def generate_tls_keys(server_domain, key_dir, ca_dir):
    server_key_filename = f"{server_domain}_tls.key"
    server_csr_filename = f"{server_domain}_tls.csr"  # csr: certificate signing request
    server_cert_filename = f"{server_domain}_tls.crt"

    ca_key_path = ca_dir / "ca.key"
    ca_cert_path = ca_dir / "ca.crt"

    logging.info("Generating server TLS key ...")
    subprocess.run(
        f"openssl genrsa -out {server_key_filename} 2048",
        shell=True,
        check=True,
        cwd=key_dir,
    )

    logging.info("Creating a certificate signing request ...")
    subprocess.run(
        f"openssl req -new -key {server_key_filename} -out {server_csr_filename} "
        + f'-subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN={server_domain}"',
        shell=True,
        check=True,
        cwd=key_dir,
    )

    logging.info("Creating server certificate ...")
    subprocess.run(
        f"openssl x509 -req -in {server_csr_filename} -CA {ca_cert_path} "
        + f"-CAkey {ca_key_path} -CAcreateserial "
        + f"-out {server_cert_filename} -days 1024 -sha256",
        shell=True,
        check=True,
        cwd=key_dir,
    )

    # Now since server's certificate has been signed by the CA, the csr can be deleted
    subprocess.run(f"rm {server_csr_filename}", shell=True, check=True, cwd=key_dir)

    logging.info(
        "TLS key and cert generated. "
        + f"Private key: '{server_key_filename}', "
        + f"certificate: '{server_cert_filename}'"
    )


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.description = "Generate a TLS key and cert signed by a CA for a server"
    parser.add_argument(
        "SERVER_DOMAIN", type=str, help="Server to generate TLS key and cert for"
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
