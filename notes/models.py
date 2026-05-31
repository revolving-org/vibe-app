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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Note":
        return cls(
            id=d["id"],
            title=d["title"],
            body=d["body"],
            created_at=d["created_at"],
            updated_at=d["updated_at"],
        )

    def matches(self, keyword: str) -> bool:
        if not keyword:
            return False
        kw = keyword.lower()
        return kw in self.title.lower() or kw in self.body.lower()
