import json
from datetime import datetime

import audit_server.audit_companies as audit_companies
import audit_server.audit_db as audit_db
import audit_server.crypto as crypto
from audit_server.audit_record import AuditRecord


def log(patient, requested_by, action, ehr_id=None):
    record = create_record(patient, requested_by, action, ehr_id=ehr_id)
    record_enc = crypto.encrypt_record(record, patient)
    log_record(record_enc)


def log_record(record: dict):
    audit_db.add_record(record)


def get_ehr_actions(requester, patient):
    if not is_authorized_for_ehrs(requester, patient):
        raise RuntimeError(
            f"'{requester}' is not authorized to get EHR actions of '{patient}'\n"
        )
    return audit_db.get_records(patient)


def is_authorized_for_ehrs(requester, patient):
    # Patient should be able to request EHR actions belonging to them
    if requester == patient:
        return True

    # Audit companies should be able to query information about their patients
    if (
        requester in audit_companies.get_companies()
        and patient in audit_companies.get_patients(requester)
    ):
        return True

    return False


def create_record(patient, requested_by, action, ehr_id=None) -> AuditRecord:
    t = datetime.now()
    return AuditRecord(
        time=t, patient=patient, requested_by=requested_by, action=action, ehr_id=ehr_id
    )
