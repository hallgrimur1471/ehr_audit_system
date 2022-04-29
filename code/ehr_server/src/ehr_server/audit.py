import json
import logging
import urllib.request
from urllib.request import Request

log = logging.getLogger("ehr_server.server")

AUDIT_API_BASEURL = "http://audit_server:5001"


def log_record(patient, requested_by, action, ehr_id=None):
    request_data = {
        "patient": patient,
        "requested_by": requested_by,
        "action": action,
    }
    if ehr_id is not None:
        request_data["ehr_id"] = ehr_id

    request = Request(
        AUDIT_API_BASEURL + "/log_action",
        data=json.dumps(request_data).encode("utf-8"),
        headers={"Content-type": "application/json"},
        method="POST",
    )

    log.debug("Notifying audit server about the EHR action ...")
    urllib.request.urlopen(request)
