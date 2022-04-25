import json

from flask import Flask, request, make_response

import ehr_server.ehr_db as ehr_db
import ehr_server.ehr as ehr
from ehr_server.ehr import EHR

app = Flask(__name__)


@app.route("/", methods=["GET"])
def hello_world():
    # request.method == "POST"
    return "<p>Hello, World!</p>"


@app.route("/create_record/<patient>", methods=["POST"])
def create_record(patient):
    app.logger.debug(f"Creating a new record for '{patient}' ...")

    if "description" not in request.json:
        return "Request must include description\n", 400

    description = request.json["description"]

    record = ehr.create_ehr(description)
    ehr_db.add_record(
        patient,
        record,
    )

    app.logger.debug(f"Created record '{patient}/{record.id}'")
    return f"Created record {record.id}\n"


@app.route("/delete_record/<patient>/<record_id>", methods=["POST"])
def delete_record(patient, record_id):
    app.logger.debug(f"Deleting record '{patient}/{record_id}' ...")

    ehr_db.delete_record(patient, record_id)

    return "Record deleted\n"


@app.route("/change_record/<patient>/<record_id>", methods=["POST"])
def change_record(patient, record_id):
    app.logger.debug(f"Changing record '{patient}/{record_id}'...")

    if "description" not in request.json:
        return "Request must include description\n", 400
    new_description = request.json["description"]

    ehr_db.change_record(patient, record_id, new_description)

    return "Record changed\n"


@app.route("/get_record/<patient>/<record_id>")
def get_record(patient, record_id):
    app.logger.debug(f"Getting record '{patient}/{record_id}'...")

    record = ehr_db.get_record(patient, record_id)

    return str(record) + "\n"


@app.route("/get_records/<patient>")
def get_records(patient):
    app.logger.debug(f"Getting records of '{patient}'...")

    records = ehr_db.get_records(patient)

    return str(records) + "\n"


def run():
    ehr_db.initialize()
    app.run(debug=True)
