import json


class DBEditor:
    def __init__(self, database_file):
        self.database_file = database_file
        self.db = None

    def __enter__(self):
        self.db = self.read_db()
        return self.db

    def __exit__(self, exc_type, exc_value, tb):
        self.update_db()

    def read_db(self):
        return json.loads(self.database_file.read_text())

    def update_db(self):
        self.database_file.write_text(json.dumps(self.db, indent=2) + "\n")


class DBReader(DBEditor):
    def __exit__(self, exc_type, exc_value, tb):
        pass
