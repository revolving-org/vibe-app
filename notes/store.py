import json
import os
import sys
from pathlib import Path

from notes.models import Note


class NotesStore:
    def __init__(self, filepath: Path | None = None):
        if filepath is None:
            filepath = Path.home() / ".notes.json"
        self.filepath = filepath

    def _load(self) -> list[Note]:
        if not self.filepath.exists():
            return []
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
            notes = []
            for item in data:
                try:
                    notes.append(Note.from_dict(item))
                except (KeyError, TypeError):
                    continue
            return notes
        except json.JSONDecodeError:
            self._handle_corruption()
            return []

    def _handle_corruption(self):
        backup = self.filepath.with_suffix(".json.bak")
        try:
            self.filepath.rename(backup)
        except OSError:
            pass
        print(
            f"Warning: Corrupt notes file. Backed up to {backup}",
            file=sys.stderr,
        )

    def _save(self, notes: list[Note]):
        data = [note.to_dict() for note in notes]
        tmp = self.filepath.with_suffix(".json.tmp")
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(tmp, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, self.filepath)
        finally:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass

    def get(self, note_id: str) -> Note | None:
        notes = self._load()
        for note in notes:
            if note.id == note_id:
                return note
        return None

    def delete(self, note_id: str) -> bool:
        notes = self._load()
        new_notes = [n for n in notes if n.id != note_id]
        if len(new_notes) == len(notes):
            return False
        self._save(new_notes)
        return True

    def add(self, note: Note) -> Note:
        notes = self._load()
        notes.append(note)
        self._save(notes)
        return note

    def list_all(self) -> list[Note]:
        return self._load()
