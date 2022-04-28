#!/usr/bin/env python3

import os
import math
import json
import random
import logging
import argparse
from pathlib import Path


def main():
    args = parse_arguments()

    if args.verbose:
        configure_logger(logging.DEBUG)
    else:
        configure_logger(logging.INFO)

    generate_keys(args.USER)


def generate_keys(user):
    pass


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.description = (
        "Generate Two sets of RSA public and private keys, "
        + "one set for signing and verification, "
        + "the other set of encryption an decryption."
    )
    parser.add_argument(
        "USER_ID", help="The name of the user for whom the keys will be generated."
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
