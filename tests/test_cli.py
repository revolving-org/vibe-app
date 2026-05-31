import io
import os
import sys
import unittest
from pathlib import Path

from notes.cli import build_parser, main, run_with_store
from notes.store import NotesStore
from notes.models import Note


class TestCLIParser(unittest.TestCase):
    def setUp(self):
        self.parser = build_parser()

    def test_add_subcommand(self):
        args = self.parser.parse_args(["add", "My Title"])
        self.assertEqual(args.command, "add")
        self.assertEqual(args.title, "My Title")
        self.assertIsNone(args.body)

    def test_add_subcommand_with_body(self):
        args = self.parser.parse_args(["add", "Title", "-b", "Body text"])
        self.assertEqual(args.command, "add")
        self.assertEqual(args.title, "Title")
        self.assertEqual(args.body, "Body text")

    def test_list_subcommand(self):
        args = self.parser.parse_args(["list"])
        self.assertEqual(args.command, "list")

    def test_show_subcommand(self):
        args = self.parser.parse_args(["show", "abc123"])
        self.assertEqual(args.command, "show")
        self.assertEqual(args.id, "abc123")

    def test_delete_subcommand(self):
        args = self.parser.parse_args(["delete", "abc123"])
        self.assertEqual(args.command, "delete")
        self.assertEqual(args.id, "abc123")

    def test_search_subcommand(self):
        args = self.parser.parse_args(["search", "keyword"])
        self.assertEqual(args.command, "search")
        self.assertEqual(args.keyword, "keyword")

    def test_no_args_shows_help(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])


class TestCLIAdd(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self.filepath = Path(self.tmp) / "notes.json"
        self.store = NotesStore(filepath=self.filepath)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def _run(self, *args):
        """Run main with given args and custom store, capture stdout/stderr."""
        old_argv = sys.argv
        sys.argv = ["notes"] + list(args)
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            run_with_store(self.store)
            return sys.stdout.getvalue(), sys.stderr.getvalue()
        except SystemExit:
            return sys.stdout.getvalue(), sys.stderr.getvalue()
        finally:
            sys.argv = old_argv
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

    def test_add_note(self):
        out, err = self._run("add", "Hello", "-b", "World")
        notes = self.store.list_all()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "Hello")
        self.assertEqual(notes[0].body, "World")
        self.assertIn("Added note", out)

    def test_add_note_empty_title(self):
        out, err = self._run("add", "")
        self.assertIn("Title must not be empty", err)
        self.assertEqual(len(self.store.list_all()), 0)

    def test_add_note_whitespace_title(self):
        out, err = self._run("add", "   ")
        self.assertIn("Title must not be empty", err)


class TestCLIList(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self.filepath = Path(self.tmp) / "notes.json"
        self.store = NotesStore(filepath=self.filepath)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def _run(self, *args):
        old_argv = sys.argv
        sys.argv = ["notes"] + list(args)
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            from notes.cli import run_with_store
            run_with_store(self.store)
            return sys.stdout.getvalue(), sys.stderr.getvalue()
        except SystemExit:
            return sys.stdout.getvalue(), sys.stderr.getvalue()
        finally:
            sys.argv = old_argv
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

    def test_list_empty(self):
        out, err = self._run("list")
        self.assertIn("No notes", out)

    def test_list_with_notes(self):
        n1 = self.store.add(Note.from_input("First", "Body one"))
        n2 = self.store.add(Note.from_input("Second", "Body two"))
        out, err = self._run("list")
        self.assertIn("First", out)
        self.assertIn("Second", out)
        self.assertIn(n1.id, out)
        self.assertIn(n2.id, out)
        # Body should not appear in list output
        self.assertNotIn("Body one", out)
        # Newest first: n2 was added after n1, so n2 should appear before n1
        self.assertLess(out.index(n2.id), out.index(n1.id))


class TestCLIShow(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self.filepath = Path(self.tmp) / "notes.json"
        self.store = NotesStore(filepath=self.filepath)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp)

    def _run(self, *args):
        old_argv = sys.argv
        sys.argv = ["notes"] + list(args)
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            from notes.cli import run_with_store
            run_with_store(self.store)
            return sys.stdout.getvalue(), sys.stderr.getvalue()
        except SystemExit:
            return sys.stdout.getvalue(), sys.stderr.getvalue()
        finally:
            sys.argv = old_argv
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

    def test_show_existing_note(self):
        note = self.store.add(Note.from_input("My Title", "My body text"))
        out, err = self._run("show", note.id)
        self.assertIn("My Title", out)
        self.assertIn("My body text", out)
        self.assertIn(note.id, out)

    def test_show_nonexistent_note(self):
        out, err = self._run("show", "nonexistent")
        self.assertIn("not found", err)
