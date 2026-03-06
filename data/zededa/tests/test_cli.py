#!/usr/bin/env python3
"""Unit tests for scripts/zededa.py — CLI entrypoint."""

import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.zededa import main, _load_body, _out


class TestLoadBody(unittest.TestCase):
    """JSON body loading from --body and --body-file."""

    def test_body_string(self):
        args = MagicMock()
        args.body = '{"name": "test"}'
        args.body_file = None
        result = _load_body(args)
        self.assertEqual(result, {"name": "test"})

    def test_body_file(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"key": "value"}, f)
            f.flush()
            args = MagicMock()
            args.body = None
            args.body_file = f.name
            result = _load_body(args)
            self.assertEqual(result, {"key": "value"})
        os.unlink(f.name)

    def test_neither(self):
        args = MagicMock()
        args.body = None
        args.body_file = None
        result = _load_body(args)
        self.assertIsNone(result)


class TestOut(unittest.TestCase):
    """Pretty-print JSON output."""

    @patch("builtins.print")
    def test_out_prints_json(self, mock_print):
        _out({"status": "ok"})
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        parsed = json.loads(output)
        self.assertEqual(parsed["status"], "ok")


class TestCLIHelp(unittest.TestCase):
    """CLI argument parsing."""

    def test_help_exits_cleanly(self):
        with patch("sys.argv", ["zededa", "--help"]):
            with self.assertRaises(SystemExit) as ctx:
                main()
            self.assertEqual(ctx.exception.code, 0)

    def test_node_help(self):
        with patch("sys.argv", ["zededa", "node", "--help"]):
            with self.assertRaises(SystemExit) as ctx:
                main()
            self.assertEqual(ctx.exception.code, 0)

    def test_app_help(self):
        with patch("sys.argv", ["zededa", "app", "--help"]):
            with self.assertRaises(SystemExit) as ctx:
                main()
            self.assertEqual(ctx.exception.code, 0)

    def test_no_service_shows_error(self):
        with patch("sys.argv", ["zededa"]):
            with self.assertRaises(SystemExit) as ctx:
                main()
            self.assertNotEqual(ctx.exception.code, 0)


class TestCLIDispatch(unittest.TestCase):
    """CLI dispatches to correct service method."""

    @patch("scripts.zededa.NodeService")
    @patch("scripts.zededa.ZededaClient")
    def test_node_list_devices(self, MockClient, MockNode):
        mock_svc = MagicMock()
        mock_svc.query_edge_nodes.return_value = {"list": []}
        MockNode.return_value = mock_svc

        with patch("sys.argv", ["zededa", "node", "list-devices"]):
            with patch("builtins.print"):
                main()
        mock_svc.query_edge_nodes.assert_called_once()

    @patch("scripts.zededa.UserService")
    @patch("scripts.zededa.ZededaClient")
    def test_user_whoami(self, MockClient, MockUser):
        mock_svc = MagicMock()
        mock_svc.get_user_self.return_value = {"name": "me"}
        MockUser.return_value = mock_svc

        with patch("sys.argv", ["zededa", "user", "whoami"]):
            with patch("builtins.print"):
                main()
        mock_svc.get_user_self.assert_called_once()


if __name__ == "__main__":
    unittest.main()
