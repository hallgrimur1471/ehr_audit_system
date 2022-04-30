#!/usr/bin/env python3

import json
import logging
import argparse
import urllib.request
from urllib.request import Request
from urllib.error import HTTPError

AUDIT_SERVER_BASEURL = "http://audit_server:5001"


def main():
    args = parse_arguments()

    if args.verbose:
        configure_logger(logging.DEBUG)
    else:
        configure_logger(logging.INFO)

    query_usage(args.PATIENT)


def query_usage(patient):
    audit_server_get_request(f"/query_usage/{patient}")


def audit_server_get_request(url_path):
    request = Request(
        f"{AUDIT_SERVER_BASEURL}{url_path}",
        method="GET",
    )
    try:
        with urllib.request.urlopen(request) as resp:
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
    parser.add_argument("PATIENT", help=f"Name of patient")
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
# >>> f = open('mykey.pem','r')
# >>> key = RSA.import_key(f.read())
