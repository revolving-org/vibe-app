import json
import unittest
from pathlib import Path

from notes.store import NotesStore
from notes.models import Note


class TestNotesStoreInit(unittest.TestCase):
    def test_default_filepath(self):
        store = NotesStore()
        self.assertEqual(store.filepath, Path.home() / ".notes.json")

    def test_custom_filepath(self):
        store = NotesStore(filepath=Path("/tmp/test_notes.json"))
        self.assertEqual(store.filepath, Path("/tmp/test_notes.json"))


class TestNotesStoreAddAndList(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self.filepath = Path(self.tmp) / "notes.json"
        self.store = NotesStore(filepath=self.filepath)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def test_list_all_empty_store(self):
        notes = self.store.list_all()
        self.assertEqual(notes, [])

    def test_add_and_list_all(self):
        note = Note.from_input("Hello", "World")
        self.store.add(note)
        notes = self.store.list_all()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "Hello")
        self.assertEqual(notes[0].body, "World")

    def test_add_multiple_notes(self):
        self.store.add(Note.from_input("First"))
        self.store.add(Note.from_input("Second"))
        self.store.add(Note.from_input("Third"))
        notes = self.store.list_all()
        self.assertEqual(len(notes), 3)

    def test_file_persists_between_store_instances(self):
        self.store.add(Note.from_input("Persist me"))
        store2 = NotesStore(filepath=self.filepath)
        notes = store2.list_all()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "Persist me")

    def test_file_contains_valid_json(self):
        self.store.add(Note.from_input("Hello", "World"))
        with open(self.filepath) as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Hello")
