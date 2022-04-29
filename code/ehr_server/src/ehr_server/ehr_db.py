import logging
from typing import List
from pathlib import Path
import json
from datetime import datetime

from ehr_server.ehr import EHR
from ehr_server.database import DBEditor
from ehr_server.time import TIME_FORMAT

log = logging.getLogger("ehr_server.server")

DB_FILE = Path("/home/david1471/ehr_audit_system/code/ehr_server/ehr_db.json")


def initialize():
    log.debug("Initializing EHR database ...")

    # Create and initialize the database file if it doesn't already exist
    if not DB_FILE.exists():
        db_dir = DB_FILE.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        DB_FILE.touch()
        DB_FILE.write_text("{}\n")


def add_record(patient: str, record: EHR):
    with DBEditor(DB_FILE) as db:
        if patient not in db:
            db[patient] = {}

        if record.id in db[patient]:
            raise RuntimeError(
                "Cannot add record, there already exists a record with the same id"
            )

        db[patient][record.id] = json.loads(str(record))


def delete_record(patient: str, record_id: str):
    with DBEditor(DB_FILE) as db:
        check_if_record_exists(patient, record_id, db)

        del db[patient][record_id]


def change_record(patient: str, record_id: str, new_description: str):
    with DBEditor(DB_FILE) as db:
        check_if_record_exists(patient, record_id, db)

        db[patient][record_id]["description"] = new_description


def get_record(patient: str, record_id: str) -> EHR:
    with DBEditor(DB_FILE) as db:
        check_if_record_exists(patient, record_id, db)

        return dict_2_ehr(db[patient][record_id])


def get_records(patient: str) -> List[EHR]:
    with DBEditor(DB_FILE) as db:
        check_if_patient_exists(patient, db)

        return [dict_2_ehr(r) for _, r in db[patient].items()]


def check_if_record_exists(patient, record_id, db):
    check_if_patient_exists(patient, db)

    if record_id not in db[patient]:
        raise RuntimeError("Record not in database")


def check_if_patient_exists(patient, db):
    if patient not in db:
        raise RuntimeError("Patient not in database")


def dict_2_ehr(d):
    dt = datetime.strptime(d["created"], TIME_FORMAT)
    return EHR(id=d["id"], created=dt, description=d["description"])
