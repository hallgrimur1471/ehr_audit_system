import logging

from flask import Flask, request, make_response

import audit_server.audit as audit
import audit_server.audit_db as audit_db

app = Flask(__name__)

log = app.logger


@app.route("/", methods=["GET"])
def hello():
    return "Welcome to the EHR Audit service\n"


@app.route("/log_action", methods=["POST"])
def log_action():
    log.debug("Logging new EHR action ...")
    patient = request.json["patient"]
    requested_by = request.json["requested_by"]
    action = request.json["action"]
    if "ehr_id" in request.json:
        ehr_id = request.json["ehr_id"]
    else:
        ehr_id = None

    audit.log(patient, requested_by, action, ehr_id=ehr_id)

    log_msg = f"EHR action {action} logged"
    if ehr_id:
        log_msg += f", ehr_id: '{ehr_id}'"
    log.info(log_msg)
    return "Action logged\n"


def run():
    audit_db.initialize()
    log.setLevel(logging.DEBUG)
    app.run(debug=True, port=5001)
