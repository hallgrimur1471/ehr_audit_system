import json
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


@app.route("/query_usage/<patient>", methods=["GET"])
def query_usage(patient):
    try:
        requester = get_user_id_from_requester_tls_certificate()
        try:
            usage = json.dumps(audit.get_ehr_actions(requester, patient), indent=2)
        except RuntimeError as err:
            # RuntimeError is likely requester not authorized, so we send 403
            return str(err), 403
    except RuntimeError as err:
        return str(err), 500
    return usage


def get_user_id_from_requester_tls_certificate():
    log.debug("Determining user based on their TLS certificate ...")

    user = "bob"

    log.debug(f"User is '{user}'")
    return user


def run():
    audit_db.initialize()
    log.setLevel(logging.DEBUG)
    app.run(debug=True, port=5001)
