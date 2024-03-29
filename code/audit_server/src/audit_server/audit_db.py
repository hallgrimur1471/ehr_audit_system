import logging
import json
from pathlib import Path

from audit_server.audit_record import AuditRecord
from audit_server.database import DBEditor, DBReader

log = logging.getLogger("ehr_server.server")

DB_FILE = Path(__file__).absolute().parent.parent.parent / "audit_db.json"


def initialize():
    log.debug("Initializing audit database ...")

    # Create and initialize the database file if it doesn't already exist
    if not DB_FILE.exists():
        db_dir = DB_FILE.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        DB_FILE.touch()
        DB_FILE.write_text("[]\n")


def add_record(record: dict):
    with DBEditor(DB_FILE) as db:
        db.append(record)


def get_records():
    with DBReader(DB_FILE) as db:
        return db
