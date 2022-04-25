import logging
import json
from pathlib import Path

from ehr_server.audit import AuditRecord
from ehr_server.database import DBEditor

log = logging.getLogger("ehr_server.server")

DB_FILE = Path("/home/david1471/ehr_audit_system/code/server/audit_db.json")


def initialize():
    log.debug("Initializing audit database ...")

    # Create and initialize the database file if it doesn't already exist
    if not DB_FILE.exists():
        db_dir = DB_FILE.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        DB_FILE.touch()
        DB_FILE.write_text("[]\n")


def add_record(record: AuditRecord):
    with DBEditor(DB_FILE) as db:
        db.append(json.loads(str(record)))
