import argparse
import sys
from pathlib import Path

from notes.store import NotesStore
from notes.models import Note


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="notes", description="A personal notes CLI tool.")
    sub = parser.add_subparsers(dest="command", required=True)

    add_parser = sub.add_parser("add", help="Add a new note")
    add_parser.add_argument("title", help="Note title")
    add_parser.add_argument("-b", "--body", default=None, help="Note body (optional)")

    sub.add_parser("list", help="List all notes")

    show_parser = sub.add_parser("show", help="Show a note by ID")
    show_parser.add_argument("id", help="Note ID")

    delete_parser = sub.add_parser("delete", help="Delete a note by ID")
    delete_parser.add_argument("id", help="Note ID")

    search_parser = sub.add_parser("search", help="Search notes by keyword")
    search_parser.add_argument("keyword", help="Search keyword")

    return parser


def _handle_add(store: NotesStore, args):
    import os
    import tempfile
    import subprocess

    body = args.body
    if body is None:
        editor = os.environ.get("EDITOR")
        if editor:
            tmpfile = tempfile.NamedTemporaryFile(mode="w+", suffix=".md", delete=False)
            try:
                tmpfile.close()
                subprocess.run([editor, tmpfile.name], check=False)
                with open(tmpfile.name, "r") as f:
                    body = f.read().strip()
            finally:
                try:
                    os.unlink(tmpfile.name)
                except OSError:
                    pass
        else:
            # Fallback: read from stdin
            body = sys.stdin.read().strip()

    try:
        note = Note.from_input(args.title, body or "")
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    try:
        store.add(note)
    except OSError as e:
        print(f"Error writing notes file: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Added note {note.id}: {note.title}")


def _handle_list(store: NotesStore):
    try:
        notes = store.list_all()
    except OSError as e:
        print(f"Error reading notes file: {e}", file=sys.stderr)
        sys.exit(2)
    if not notes:
        print("No notes.")
        return
    for note in reversed(notes):
        print(f"  [{note.id}]  {note.title}")


def main():
    store = NotesStore()
    run_with_store(store)


def run_with_store(store: NotesStore):
    """Entry point that accepts a pre-configured store. Useful for testing."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "add":
        _handle_add(store, args)
    elif args.command == "list":
        _handle_list(store)
    elif args.command == "show":
        _handle_show(store, args)
    elif args.command == "delete":
        _handle_delete(store, args)
    elif args.command == "search":
        _handle_search(store, args)


def _handle_show(store: NotesStore, args):
    try:
        note = store.get(args.id)
    except OSError as e:
        print(f"Error reading notes file: {e}", file=sys.stderr)
        sys.exit(2)
    if note is None:
        print(f"Note '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)
    print(f"  ID:        {note.id}")
    print(f"  Title:     {note.title}")
    print(f"  Created:   {note.created_at}")
    print(f"  Updated:   {note.updated_at}")
    print()
    print(f"  {note.body}")


def _handle_delete(store: NotesStore, args):
    try:
        note = store.get(args.id)
    except OSError as e:
        print(f"Error reading notes file: {e}", file=sys.stderr)
        sys.exit(2)
    if note is None:
        print(f"Note '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)
    try:
        store.delete(args.id)
    except OSError as e:
        print(f"Error writing notes file: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Deleted note '{note.title}'.")


def _handle_search(store: NotesStore, args):
    try:
        results = store.search(args.keyword)
    except OSError as e:
        print(f"Error reading notes file: {e}", file=sys.stderr)
        sys.exit(2)
    if not results:
        print(f"No matches for '{args.keyword}'.")
        return
    for note in reversed(results):
        print(f"  [{note.id}]  {note.title}")


if __name__ == "__main__":
    main()
