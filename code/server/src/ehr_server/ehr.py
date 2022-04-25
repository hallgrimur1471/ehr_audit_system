import os
import json
from datetime import datetime


class EHR:
    def __init__(self, id: str, created: datetime, description: str):
        self.id = id
        self.created = created
        self.description = description

    def __repr__(self) -> str:
        return json.dumps(
            {
                "id": self.id,
                "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
                "description": self.description,
            },
            indent=2,
        )


def create_ehr(description: str) -> EHR:
    return EHR(id=generate_id(), created=datetime.now(), description=description)


def generate_id():
    return os.urandom(16).hex()
