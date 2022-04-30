import json
from datetime import datetime

import audit_server.audit_db as audit_db
from audit_server.audit_record import AuditRecord


def log(patient, requested_by, action, ehr_id=None):
    record = create_record(patient, requested_by, action, ehr_id=ehr_id)
    log_record(record)


def log_record(record: AuditRecord):
    audit_db.add_record(record)


def get_ehr_actions(requester, patient):
    if not is_authorized_for_ehrs(requester, patient):
        raise RuntimeError(
            f"'{requester}' is not authorized to get EHR actions of '{patient}'\n"
        )
    return audit_db.get_records(patient)


def is_authorized_for_ehrs(requester, patient):
    # patient's should be able to request EHR actions belonging to them
    if requester == patient:
        return True

    # USC should be able to query information about its patients
    usc_patients = {"alice", "bob", "eve"}
    if requester == "usc" and patient in usc_patients:
        return True

    # UCLA should be able to query information about its patients
    ucla_patients = {"carol", "david"}
    if requester == "ucla" and patient in ucla_patients:
        return True

    return False


def create_record(patient, requested_by, action, ehr_id=None):
    t = datetime.now()
    return AuditRecord(
        time=t, patient=patient, requested_by=requested_by, action=action, ehr_id=ehr_id
    )
