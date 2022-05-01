#!/usr/bin/env python3

import json
import logging
import argparse
import urllib.request
from urllib.request import Request
from urllib.error import HTTPError

EHR_SERVER_BASEURL = "http://ehr_server:5000"


def main():
    args = parse_arguments()

    if args.verbose:
        configure_logger(logging.DEBUG)
    else:
        configure_logger(logging.INFO)

    do_ehr_action(
        args.PATIENT_ID,
        args.DOCTOR_ID,
        args.ACTION,
        ehr_id=args.ehr_id,
        description=args.description,
    )


def do_ehr_action(patient, doctor, action, ehr_id=None, description=None):
    if action == "CREATE":
        ehr_server_post_request(
            doctor, f"/create_record/{patient}", description=description
        )
    elif action == "DELETE":
        ehr_server_post_request(doctor, f"/delete_record/{patient}/{ehr_id}")
    elif action == "CHANGE":
        ehr_server_post_request(
            doctor, f"/change_record/{patient}/{ehr_id}", description=description
        )
    elif action == "GET_RECORD":
        ehr_server_get_request(f"/get_record/{patient}/{ehr_id}/{doctor}")
    elif action == "GET_RECORDS":
        ehr_server_get_request(f"/get_records/{patient}/{doctor}")


def ehr_server_post_request(doctor, url_path, description=None):
    request_data = {"requested_by": doctor}
    if description is not None:
        request_data["description"] = description
    request = Request(
        f"{EHR_SERVER_BASEURL}{url_path}",
        data=json.dumps(request_data).encode("utf-8"),
        headers={"Content-type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as resp:
            response_text = resp.read().decode()
            logging.info(response_text.rstrip())
    except HTTPError as err:
        logging.error(
            f"Action failed, ehr_server responded with: {err.read().decode().rstrip()}"
        )


def ehr_server_get_request(url_path):
    request = Request(
        f"{EHR_SERVER_BASEURL}{url_path}",
        method="GET",
    )
    try:
        with urllib.request.urlopen(request) as resp:
            response_text = resp.read().decode()
            print(response_text.rstrip())
    except HTTPError as err:
        logging.error(
            f"Action failed, ehr_server responded with: {err.read().decode().rstrip()}"
        )


def parse_arguments():
    parser = argparse.ArgumentParser()
    valid_actions = ["CREATE", "DELETE", "CHANGE", "GET_RECORD", "GET_RECORDS"]
    parser.description = "Do EHR operations"
    parser.add_argument("ACTION", help=f"One of {valid_actions}")
    parser.add_argument("PATIENT_ID", help="The name of the patient the EHR belongs to")
    parser.add_argument(
        "DOCTOR_ID", help="The name of the doctor that's doing the operation"
    )
    parser.add_argument(
        "--description",
        help="Put EHR contents here, "
        + "applies to the actions CREATE and CHANGE. "
        + "Example: 'The patient visited "
        + "with symptoms X and Y which was remediated by Z'",
    )
    parser.add_argument(
        "--ehr-id",
        help="ID of EHR, applies to the actions DELETE, CHANGE and GET_RECORD. Example: 'f764b7595b74a1d02d3af9f8a2642b8f'",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enables printing of debug statements",
    )
    arguments = parser.parse_args()

    # Validate arguments
    if arguments.ACTION not in valid_actions:
        raise ValueError(f"ACTION must be one of {valid_actions}")
    if arguments.ACTION == "CREATE" and arguments.description is None:
        raise ValueError(
            f"CREATE action must include a description, see --description flag"
        )
    if arguments.ACTION == "CHANGE" and arguments.description is None:
        raise ValueError(
            f"CHANGE action must include a new description, see --description flag"
        )
    if (
        arguments.ACTION in ["DELETE", "CHANGE", "GET_RECORD"]
        and arguments.ehr_id is None
    ):
        raise ValueError(
            f"{arguments.ACTION} action must include an EHR ID, see --ehr-id flag"
        )

    return arguments


def configure_logger(log_level):
    logging.basicConfig(
        format="[%(asctime)s.%(msecs)03d %(levelname)s]: %(message)s",
        datefmt="%H:%M:%S",
        level=log_level,
    )


if __name__ == "__main__":
    main()
