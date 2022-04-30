import json
import logging
from pathlib import Path

from flask import Flask, request
import werkzeug.serving
import ssl
from ssl import TLSVersion
import OpenSSL

import audit_server.audit as audit
import audit_server.audit_db as audit_db

# This class is copied from:
# https://gist.github.com/nebulak/6d865ddd768fb905a562d6026cdd508a
class PeerCertWSGIRequestHandler(werkzeug.serving.WSGIRequestHandler):
    def make_environ(self):
        environ = super(PeerCertWSGIRequestHandler, self).make_environ()
        x509_binary = self.connection.getpeercert(True)
        x509 = OpenSSL.crypto.load_certificate(
            OpenSSL.crypto.FILETYPE_ASN1, x509_binary
        )
        environ["peercert"] = x509
        return environ


app = Flask(__name__)

# NOTE: This method of finding the keys directory breaks if the package
#       is installed not in edtiable mode (because in that case
#       __file__ might reside in a packaged zip file).
code_dir = Path(__file__).absolute().parent.parent.parent.parent
key_dir = code_dir / "audit_server/keys"
ca_dir = code_dir / "ca/keys"

server_key = key_dir / "audit_server_tls.key"
server_key_password = None
server_cert = key_dir / "audit_server_tls.crt"

ca_cert = ca_dir / "ca.crt"

# Configure TLS for client authentication
ssl_context = ssl.create_default_context(
    purpose=ssl.Purpose.CLIENT_AUTH, cafile=ca_cert
)

# Load server TLS key and certificate
ssl_context.load_cert_chain(
    certfile=server_cert, keyfile=server_key, password=server_key_password
)

# Configure TLS to require client certificate signed by CA
ssl_context.verify_mode = ssl.CERT_REQUIRED

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

    user = request.environ["peercert"].get_subject().commonName

    log.debug(f"User is '{user}'")
    return user


def run():
    audit_db.initialize()
    log.setLevel(logging.DEBUG)
    app.run(
        debug=True,
        port=5001,
        ssl_context=ssl_context,
        request_handler=PeerCertWSGIRequestHandler,
    )
