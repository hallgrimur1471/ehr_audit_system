#!/usr/bin/env python3

import ssl
import logging
import argparse
from pathlib import Path
import urllib.request
from urllib.request import Request
from urllib.error import HTTPError

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

    audit_server_get_request(f"/query_usage/{patient}", user_cert_file, user_key_file)


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
            response_text = resp.read().decode()
            print(response_text.rstrip())
    except HTTPError as err:
        logging.error(
            "Failed to create record, audit_server responded with HTTP returncode "
            + f"{err.code} and the message: {err.read().decode().rstrip()}"
        )


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


if __name__ == "__main__":
    main()
# >>> f = open('mykey.pem','r')
# >>> key = RSA.import_key(f.read())
