import json
from datetime import datetime

import audit_server.audit_db as audit_db
from audit_server.audit_record import AuditRecord


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
