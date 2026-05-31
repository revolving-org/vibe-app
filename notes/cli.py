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


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    store = NotesStore()

    if args.command == "list":
        pass
    elif args.command == "add":
        pass
    elif args.command == "show":
        pass
    elif args.command == "delete":
        pass
    elif args.command == "search":
        pass


if __name__ == "__main__":
    main()
