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

    description = request.json["description"]

    record = ehr.create_ehr(description)
    ehr_db.add_record(
        patient,
        record,
    )

    audit.log_record(patient, "unknown", "CREATE", ehr_id=record.id)

    log.info(f"Created record '{patient}/{record.id}'")
    return f"Created record {record.id}\n"


@app.route("/delete_record/<patient>/<record_id>", methods=["POST"])
def delete_record(patient, record_id):
    log.debug(f"Deleting record '{patient}/{record_id}' ...")

    ehr_db.delete_record(patient, record_id)

    audit.log_record(patient, "unknown", "DELETE", ehr_id=record_id)

    log.info(f"Deleted record '{patient}/{record_id}")
    return "Record deleted\n"


@app.route("/change_record/<patient>/<record_id>", methods=["POST"])
def change_record(patient, record_id):
    log.debug(f"Changing record '{patient}/{record_id}' ...")

    if "description" not in request.json:
        return "Request must include description\n", 400
    new_description = request.json["description"]

    ehr_db.change_record(patient, record_id, new_description)

    audit.log_record(patient, "unknown", "CHANGE", ehr_id=record_id)

    log.info(f"Changed record '{patient}/{record_id}'")
    return "Record changed\n"


@app.route("/get_record/<patient>/<record_id>")
def get_record(patient, record_id):
    log.debug(f"Getting record '{patient}/{record_id}' ...")

    record = ehr_db.get_record(patient, record_id)

    audit.log_record(patient, "unknown", "GET_RECORD", ehr_id=record_id)

    log.info(f"Fetched record '{patient}/{record_id}'")
    return str(record) + "\n"


@app.route("/get_records/<patient>")
def get_records(patient):
    log.debug(f"Getting records of '{patient}' ...")

    records = ehr_db.get_records(patient)

    audit.log_record(patient, "unknown", "GET_RECORDS")

    log.info(f"Fetched records of '{patient}'")
    return str(records) + "\n"


def run():
    ehr_db.initialize()
    log.setLevel(logging.DEBUG)
    app.run(debug=True)
