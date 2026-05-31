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


class TestNotesStoreGetAndDelete(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self.filepath = Path(self.tmp) / "notes.json"
        self.store = NotesStore(filepath=self.filepath)
        self.note = self.store.add(Note.from_input("Keep me", "Body here"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def test_get_existing_note(self):
        found = self.store.get(self.note.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Keep me")

    def test_get_nonexistent_note(self):
        found = self.store.get("nonexistent-id")
        self.assertIsNone(found)

    def test_delete_existing_note(self):
        result = self.store.delete(self.note.id)
        self.assertTrue(result)
        notes = self.store.list_all()
        self.assertEqual(len(notes), 0)

    def test_delete_nonexistent_note(self):
        result = self.store.delete("nonexistent-id")
        self.assertFalse(result)
        notes = self.store.list_all()
        self.assertEqual(len(notes), 1)

    def test_delete_only_removes_target(self):
        note2 = self.store.add(Note.from_input("Second"))
        self.store.delete(self.note.id)
        notes = self.store.list_all()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].id, note2.id)


class TestNotesStoreSearch(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self.filepath = Path(self.tmp) / "notes.json"
        self.store = NotesStore(filepath=self.filepath)
        self.store.add(Note.from_input("Hello World", "About Python"))
        self.store.add(Note.from_input("Shopping List", "Buy milk and eggs"))
        self.store.add(Note.from_input("Python Tips", "Use list comprehensions"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def test_search_finds_title_match(self):
        results = self.store.search("Hello")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Hello World")

    def test_search_finds_body_match(self):
        results = self.store.search("milk")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Shopping List")

    def test_search_case_insensitive(self):
        results = self.store.search("python")
        self.assertEqual(len(results), 2)

    def test_search_no_match(self):
        results = self.store.search("zzzzz")
        self.assertEqual(results, [])

    def test_search_empty_keyword(self):
        results = self.store.search("")
        self.assertEqual(results, [])


class TestNotesStoreCorruption(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self.filepath = Path(self.tmp) / "notes.json"
        self.store = NotesStore(filepath=self.filepath)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def test_corrupt_json_returns_empty_and_creates_backup(self):
        # Write invalid JSON
        self.filepath.write_text("this is not json{{{")
        notes = self.store.list_all()
        self.assertEqual(notes, [])
        backup = self.filepath.with_suffix(".json.bak")
        self.assertTrue(backup.exists())

    def test_recovery_then_add_works(self):
        self.filepath.write_text("garbage")
        self.store.list_all()  # triggers recovery
        self.store.add(Note.from_input("After recovery"))
        notes = self.store.list_all()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "After recovery")
