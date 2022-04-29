import json
from datetime import datetime

from audit_server.time import TIME_FORMAT


class AuditRecord:
    def __init__(
        self,
        time: datetime,
        patient: str,
        requested_by: str,
        action: str,
        ehr_id: str = None,
    ):
        self.time = time
        self.patient = patient
        self.requested_by = requested_by
        self.action = action
        self.ehr_id = ehr_id

    def __repr__(self):
        d = {
            "time": self.time.strftime(TIME_FORMAT),
            "patient": self.patient,
            "requested_by": self.requested_by,
            "action": self.action,
        }
        if self.ehr_id is not None:
            d["ehr_id"] = self.ehr_id

        return json.dumps(d, indent=2)
