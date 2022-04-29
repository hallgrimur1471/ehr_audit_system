import logging

from flask import Flask, request, make_response

import ehr_server.ehr_db as ehr_db
import ehr_server.ehr as ehr
from ehr_server.ehr import EHR
import ehr_server.audit as audit

app = Flask(__name__)

log = app.logger


@app.route("/", methods=["GET"])
def hello():
    return "Welcome to the EHR REST service\n"


@app.route("/create_record/<patient>", methods=["POST"])
def create_record(patient):
    log.debug(f"Creating a new record for '{patient}' ...")

    if "description" not in request.json:
        return "Request must include description\n", 400

    if "requested_by" not in request.json:
        return (
            "Request must include information about "
            + "who is requesting this EHR action"
        ), 400

    description = request.json["description"]
    requested_by = request.json["requested_by"]

    record = ehr.create_ehr(description)
    ehr_db.add_record(
        patient,
        record,
    )

    audit.log_record(patient, requested_by, "CREATE", ehr_id=record.id)

    log.info(f"Created record '{patient}/{record.id}', requested by '{requested_by}'")
    return f"Created record {record.id}\n"


@app.route("/delete_record/<patient>/<record_id>", methods=["POST"])
def delete_record(patient, record_id):
    log.debug(f"Deleting record '{patient}/{record_id}' ...")

    if "requested_by" not in request.json:
        return (
            "Request must include information about "
            + "who is requesting this EHR action"
        ), 400

    requested_by = request.json["requested_by"]

    try:
        ehr_db.delete_record(patient, record_id)
    except RuntimeError:
        return "Failed to delete record, maybe it doesn't exist?\n", 500

    audit.log_record(patient, requested_by, "DELETE", ehr_id=record_id)

    log.info(f"Deleted record '{patient}/{record_id}")
    return "Record deleted\n"


@app.route("/change_record/<patient>/<record_id>", methods=["POST"])
def change_record(patient, record_id):
    log.debug(f"Changing record '{patient}/{record_id}' ...")

    if "description" not in request.json:
        return "Request must include description\n", 400

    if "requested_by" not in request.json:
        return (
            "Request must include information about "
            + "who is requesting this EHR action"
        ), 400

    new_description = request.json["description"]
    requested_by = request.json["requested_by"]

    try:
        ehr_db.change_record(patient, record_id, new_description)
    except RuntimeError:
        return "Failed to change record, maybe it doesn't exist?\n", 500

    audit.log_record(patient, requested_by, "CHANGE", ehr_id=record_id)

    log.info(f"Changed record '{patient}/{record_id}'")
    return "Record changed\n"


@app.route("/get_record/<patient>/<record_id>/<requested_by>")
def get_record(patient, record_id, requested_by):
    log.debug(f"Getting record '{patient}/{record_id}' ...")

    try:
        record = ehr_db.get_record(patient, record_id)
    except RuntimeError:
        return "Failed to get record, maybe it doesn't exist?\n", 500

    audit.log_record(patient, requested_by, "GET_RECORD", ehr_id=record_id)

    log.info(f"Fetched record '{patient}/{record_id}'")
    return str(record) + "\n"


@app.route("/get_records/<patient>/<requested_by>")
def get_records(patient, requested_by):
    log.debug(f"Getting records of '{patient}' ...")

    try:
        records = ehr_db.get_records(patient)
    except RuntimeError:
        return "Failed to get records, maybe this patient is not in our system?\n", 500

    audit.log_record(patient, requested_by, "GET_RECORDS")

    log.info(f"Fetched records of '{patient}'")
    return str(records) + "\n"


def run():
    ehr_db.initialize()
    log.setLevel(logging.DEBUG)
    app.run(debug=True)
