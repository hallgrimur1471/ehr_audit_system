import json
from datetime import datetime

import ehr_server.audit_db as audit_db
from ehr_server.time import TIME_FORMAT


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


def log(patient, requested_by, action, ehr_id=None):
    record = create_record(patient, requested_by, action, ehr_id=ehr_id)
    log_record(record)


def log_record(record: AuditRecord):
    audit_db.add_record(record)


def create_record(patient, requested_by, action, ehr_id=None):
    t = datetime.now()
    return AuditRecord(
        time=t, patient=patient, requested_by=requested_by, action=action, ehr_id=ehr_id
    )
