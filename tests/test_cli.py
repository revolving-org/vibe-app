import io
import sys
import unittest
from pathlib import Path

from notes.cli import build_parser


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
