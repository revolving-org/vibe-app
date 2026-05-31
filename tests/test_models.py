import unittest
from notes.models import Note


class TestNoteFromInput(unittest.TestCase):
    def test_creates_note_with_title_and_body(self):
        note = Note.from_input("Hello", "World")
        self.assertEqual(note.title, "Hello")
        self.assertEqual(note.body, "World")

    def test_creates_note_with_empty_body(self):
        note = Note.from_input("Hello")
        self.assertEqual(note.title, "Hello")
        self.assertEqual(note.body, "")

    def test_generates_id(self):
        note = Note.from_input("Hello")
        self.assertEqual(len(note.id), 32)  # UUID4 hex

    def test_generates_unique_ids(self):
        a = Note.from_input("A")
        b = Note.from_input("B")
        self.assertNotEqual(a.id, b.id)

    def test_sets_created_at_and_updated_at(self):
        note = Note.from_input("Hello")
        # ISO8601 with timezone
        self.assertIn("+", note.created_at)
        self.assertIn("+", note.updated_at)

    def test_created_at_equals_updated_at_for_new_note(self):
        note = Note.from_input("Hello")
        self.assertEqual(note.created_at, note.updated_at)

    def test_raises_valueerror_on_empty_title(self):
        with self.assertRaises(ValueError):
            Note.from_input("")

    def test_raises_valueerror_on_whitespace_title(self):
        with self.assertRaises(ValueError):
            Note.from_input("   ")

    def test_strips_title_and_body_whitespace(self):
        note = Note.from_input("  Hello  ", "  World  ")
        self.assertEqual(note.title, "Hello")
        self.assertEqual(note.body, "World")


class TestNoteMatches(unittest.TestCase):
    def setUp(self):
        self.note = Note(
            id="abc123",
            title="Hello World",
            body="This is a test note about Python",
            created_at="2026-01-01T00:00:00+00:00",
            updated_at="2026-01-01T00:00:00+00:00",
        )

    def test_matches_title_exact(self):
        self.assertTrue(self.note.matches("Hello World"))

    def test_matches_title_substring(self):
        self.assertTrue(self.note.matches("Hello"))

    def test_matches_title_case_insensitive(self):
        self.assertTrue(self.note.matches("hello"))

    def test_matches_body(self):
        self.assertTrue(self.note.matches("Python"))

    def test_matches_body_case_insensitive(self):
        self.assertTrue(self.note.matches("python"))

    def test_no_match(self):
        self.assertFalse(self.note.matches("zzzzz"))

    def test_matches_empty_keyword_returns_false(self):
        self.assertFalse(self.note.matches(""))


class TestNoteSerialization(unittest.TestCase):
    def setUp(self):
        self.note = Note(
            id="abc123",
            title="Hello",
            body="World",
            created_at="2026-01-01T00:00:00+00:00",
            updated_at="2026-01-01T00:00:00+00:00",
        )

    def test_to_dict(self):
        d = self.note.to_dict()
        self.assertEqual(d["id"], "abc123")
        self.assertEqual(d["title"], "Hello")
        self.assertEqual(d["body"], "World")
        self.assertEqual(d["created_at"], "2026-01-01T00:00:00+00:00")
        self.assertEqual(d["updated_at"], "2026-01-01T00:00:00+00:00")

    def test_from_dict(self):
        d = {
            "id": "xyz789",
            "title": "Test",
            "body": "Body here",
            "created_at": "2026-06-01T12:00:00+00:00",
            "updated_at": "2026-06-01T12:00:00+00:00",
        }
        note = Note.from_dict(d)
        self.assertEqual(note.id, "xyz789")
        self.assertEqual(note.title, "Test")
        self.assertEqual(note.body, "Body here")
        self.assertEqual(note.created_at, "2026-06-01T12:00:00+00:00")
        self.assertEqual(note.updated_at, "2026-06-01T12:00:00+00:00")

    def test_roundtrip(self):
        d = self.note.to_dict()
        note2 = Note.from_dict(d)
        self.assertEqual(self.note, note2)
