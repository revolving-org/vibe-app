import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Note:
    id: str
    title: str
    body: str
    created_at: str
    updated_at: str

    @classmethod
    def from_input(cls, title: str, body: str = "") -> "Note":
        title = title.strip()
        if not title:
            raise ValueError("Title must not be empty.")
        body = body.strip()
        now = datetime.now(timezone.utc).isoformat()
        note_id = uuid.uuid4().hex
        return cls(
            id=note_id,
            title=title,
            body=body,
            created_at=now,
            updated_at=now,
        )
