import ssl
import json
import logging
import urllib.request
from pathlib import Path
from urllib.request import Request

log = logging.getLogger("ehr_server.server")

AUDIT_API_BASEURL = "https://audit_server:5001"


def log_record(patient, requested_by, action, ehr_id=None):
    url = AUDIT_API_BASEURL + "/log_action"
    request_data = {
        "patient": patient,
        "requested_by": requested_by,
        "action": action,
    }
    if ehr_id is not None:
        request_data["ehr_id"] = ehr_id

    audit_server_post_request(url, request_data)


def audit_server_post_request(url, request_data):
    code_dir = Path(__file__).absolute().parent.parent.parent.parent
    ca_dir = code_dir / "ca/keys"
    ca_cert = ca_dir / "ca.crt"

    ehr_server_dir = Path(__file__).absolute().parent.parent.parent
    client_cert = ehr_server_dir / "keys/ehr_server_tls.crt"
    client_key = ehr_server_dir / "keys/ehr_server_tls.key"
    client_key_password = None

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_cert)
    context.load_cert_chain(
        certfile=client_cert, keyfile=client_key, password=client_key_password
    )

    request = Request(
        url,
        data=json.dumps(request_data).encode("utf-8"),
        headers={"Content-type": "application/json"},
        method="POST",
    )

    log.debug("Notifying audit server about the EHR action ...")
    urllib.request.urlopen(request, context=context)
