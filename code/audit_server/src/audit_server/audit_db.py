import logging
import json
from pathlib import Path

from audit_server.audit_record import AuditRecord
import audit_server.database

log = logging.getLogger("ehr_server.server")

DB_FILE = Path("/home/david1471/ehr_audit_system/code/audit_server/audit_db.json")


def initialize():
    log.debug("Initializing audit database ...")

    # Create and initialize the database file if it doesn't already exist
    if not DB_FILE.exists():
        db_dir = DB_FILE.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        DB_FILE.touch()
        DB_FILE.write_text("[]\n")


def add_record(record: AuditRecord):
    with audit_server.database.DBEditor(DB_FILE) as db:
        db.append(json.loads(str(record)))
