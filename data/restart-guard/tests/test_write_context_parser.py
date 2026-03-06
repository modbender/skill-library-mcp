import os
import tempfile
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in os.sys.path:
    os.sys.path.insert(0, SCRIPT_DIR)

import write_context  # noqa: E402


class WriteContextParserTests(unittest.TestCase):
    def test_yaml_lists_and_scalars(self):
        raw = """
paths:
  openclaw_bin: ""
guardian:
  diagnostics:
    - "openclaw doctor --non-interactive"
    - "openclaw logs --tail 30"
safety:
  backup_config: true
notification:
  channels: []
"""
        cfg = write_context.load_yaml_text(raw)
        self.assertIsInstance(cfg, dict)
        self.assertEqual(cfg["paths"]["openclaw_bin"], "")
        self.assertIsInstance(cfg["guardian"]["diagnostics"], list)
        self.assertEqual(len(cfg["guardian"]["diagnostics"]), 2)
        self.assertEqual(cfg["notification"]["channels"], [])
        self.assertIs(cfg["safety"]["backup_config"], True)

    def test_load_config_from_file(self):
        raw = """
notification:
  channels:
    - telegram
    - feishu
guardian:
  health_success_streak: 2
"""
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "restart-guard.yaml")
            with open(path, "w", encoding="utf-8") as f:
                f.write(raw)
            cfg = write_context.load_config(path)
        self.assertEqual(cfg["guardian"]["health_success_streak"], 2)
        self.assertEqual(cfg["notification"]["channels"], ["telegram", "feishu"])

    def test_frontmatter_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "context.md")
            frontmatter = {
                "restart_id": "rg-test",
                "notify_mode": "origin",
                "channel_selection": {"channel": "webui", "target": ""},
                "state_timestamps": {"context_saved_at": "2026-02-27T10:00:00+08:00"},
                "verify": [{"command": "openclaw health --json", "expect": "ok"}],
            }
            body = "# Restart Context\n\nhello"
            write_context.write_markdown_frontmatter(path, frontmatter, body)
            loaded, loaded_body = write_context.parse_markdown_frontmatter(path)
            self.assertEqual(loaded["restart_id"], "rg-test")
            self.assertEqual(loaded["channel_selection"]["channel"], "webui")
            self.assertEqual(loaded["verify"][0]["expect"], "ok")
            self.assertIn("Restart Context", loaded_body)


if __name__ == "__main__":
    unittest.main()
