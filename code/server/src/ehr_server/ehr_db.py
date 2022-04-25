import logging
from typing import List
from pathlib import Path
import json
from datetime import datetime

from ehr_server.ehr import EHR

log = logging.getLogger("ehr_server.server")

DB_FILE = Path("/home/david1471/ehr_audit_system/code/server/ehr_db.json")


class DBEditor:
    def __init__(self):
        self.db = None

    def __enter__(self):
        self.db = self.read_db()
        return self.db

    def __exit__(self, exc_type, exc_value, tb):
        self.update_db()

    def read_db(self):
        return json.loads(DB_FILE.read_text())

    def update_db(self):
        DB_FILE.write_text(json.dumps(self.db, indent=2) + "\n")


def initialize():
    log.debug("Initializing EHR database ...")

    # Create and initialize the database file if it doesn't already exist
    if not DB_FILE.exists():
        db_dir = DB_FILE.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        DB_FILE.touch()
        DB_FILE.write_text("{}\n")


def add_record(patient: str, record: EHR):
    with DBEditor() as db:
        if patient not in db:
            db[patient] = {}

        if record.id in db[patient]:
            raise RuntimeError(
                "Cannot add record, there already exists a record with the same id"
            )

        db[patient][record.id] = json.loads(str(record))


def delete_record(patient: str, record_id: str):
    with DBEditor() as db:
        check_if_record_exists(patient, record_id, db)

        del db[patient][record_id]


def change_record(patient: str, record_id: str, new_description: str):
    with DBEditor() as db:
        check_if_record_exists(patient, record_id, db)

        db[patient][record_id]["description"] = new_description


def get_record(patient: str, record_id: str) -> EHR:
    with DBEditor() as db:
        check_if_record_exists(patient, record_id, db)

        return dict_2_ehr(db[patient][record_id])


def get_records(patient: str) -> List[EHR]:
    with DBEditor() as db:
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
    dt = datetime.strptime(d["created"], "%Y-%m-%d %H:%M:%S")
    return EHR(id=d["id"], created=dt, description=d["description"])
