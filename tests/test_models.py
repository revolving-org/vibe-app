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
        self.assertTrue(len(note.id) > 0)
        # UUID4 hex is 32 chars
        self.assertEqual(len(note.id), 32)

    def test_generates_unique_ids(self):
        a = Note.from_input("A")
        b = Note.from_input("B")
        self.assertNotEqual(a.id, b.id)

    def test_sets_created_at_and_updated_at(self):
        note = Note.from_input("Hello")
        self.assertTrue(len(note.created_at) > 0)
        self.assertTrue(len(note.updated_at) > 0)

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
