"""Unit tests for live/demo trading mode toggle (okx.py cmd_mode)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import tempfile
import shutil
from unittest.mock import patch


class TestModeToggle(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._orig_prefs = None
        import config as cfg
        self._orig_prefs_path = cfg.PREFS_PATH
        cfg.PREFS_PATH = os.path.join(self.tmp, "prefs.json")

    def tearDown(self):
        import config as cfg
        cfg.PREFS_PATH = self._orig_prefs_path
        shutil.rmtree(self.tmp)

    def _prefs_file(self):
        import config as cfg
        return cfg.PREFS_PATH

    def _write_prefs(self, prefs: dict):
        with open(self._prefs_file(), "w") as f:
            json.dump(prefs, f)

    def _read_prefs(self) -> dict:
        with open(self._prefs_file()) as f:
            return json.load(f)

    def test_default_mode_is_demo(self):
        from config import load_prefs
        prefs = load_prefs()
        self.assertEqual(prefs.get("mode", "demo"), "demo")

    def test_mode_switch_to_demo(self):
        from config import load_prefs, save_prefs
        prefs = load_prefs()
        prefs["mode"] = "live"
        save_prefs(prefs)
        self.assertEqual(load_prefs()["mode"], "live")
        prefs["mode"] = "demo"
        save_prefs(prefs)
        self.assertEqual(load_prefs()["mode"], "demo")

    def test_mode_switch_to_live_requires_yes_confirm(self):
        from config import load_prefs, save_prefs
        import okx
        prefs = load_prefs()
        prefs["mode"] = "demo"
        save_prefs(prefs)

        with patch("builtins.input", return_value="yes"):
            okx.cmd_mode(["live"])
        self.assertEqual(load_prefs()["mode"], "live")

    def test_mode_switch_to_live_cancelled_on_non_yes(self):
        from config import load_prefs, save_prefs
        import okx
        prefs = load_prefs()
        prefs["mode"] = "demo"
        save_prefs(prefs)

        with patch("builtins.input", return_value="no"):
            okx.cmd_mode(["live"])
        self.assertEqual(load_prefs()["mode"], "demo")

    def test_mode_no_args_shows_current(self):
        from config import load_prefs, save_prefs
        import okx
        prefs = load_prefs()
        prefs["mode"] = "demo"
        save_prefs(prefs)
        # Should not raise; just logs current mode
        okx.cmd_mode([])

    def test_okx_client_uses_live_credentials_in_live_mode(self):
        from config import load_prefs, save_prefs
        prefs = load_prefs()
        prefs["mode"] = "live"
        save_prefs(prefs)

        with patch("okx_client._sync_time"), \
             patch.dict(os.environ, {
                 "OKX_API_KEY_LIVE": "live_key",
                 "OKX_SECRET_KEY_LIVE": "live_secret",
                 "OKX_PASSPHRASE_LIVE": "live_pass",
             }):
            from okx_client import OKXClient
            client = OKXClient()
        self.assertEqual(client.api_key, "live_key")
        self.assertFalse(client.simulated)

    def test_okx_client_uses_demo_credentials_in_demo_mode(self):
        from config import load_prefs, save_prefs
        prefs = load_prefs()
        prefs["mode"] = "demo"
        save_prefs(prefs)

        with patch("okx_client._sync_time"), \
             patch.dict(os.environ, {
                 "OKX_API_KEY": "demo_key",
                 "OKX_SECRET_KEY": "demo_secret",
                 "OKX_PASSPHRASE": "demo_pass",
                 "OKX_SIMULATED": "1",
             }):
            from okx_client import OKXClient
            client = OKXClient()
        self.assertEqual(client.api_key, "demo_key")
        self.assertTrue(client.simulated)

    def test_mode_invalid_value_exits(self):
        import okx
        with self.assertRaises(SystemExit):
            okx.cmd_mode(["paper"])


# ── cmd_prefs ─────────────────────────────────────────────────────────────────

class TestCmdPrefs(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import config as cfg
        self._orig = cfg.PREFS_PATH
        cfg.PREFS_PATH = os.path.join(self.tmp, "prefs.json")

    def tearDown(self):
        import config as cfg
        cfg.PREFS_PATH = self._orig
        shutil.rmtree(self.tmp)

    def _set(self, key, value):
        import okx
        okx.cmd_prefs(["set", key, value])

    def test_set_int_key(self):
        self._set("max_order_usd", "200")
        from config import load_prefs
        self.assertEqual(load_prefs()["max_order_usd"], 200)
        self.assertIsInstance(load_prefs()["max_order_usd"], int)

    def test_set_float_key(self):
        self._set("stop_loss_pct", "7.5")
        from config import load_prefs
        self.assertAlmostEqual(load_prefs()["stop_loss_pct"], 7.5)
        self.assertIsInstance(load_prefs()["stop_loss_pct"], float)

    def test_set_bool_key_true(self):
        self._set("auto_trade", "true")
        from config import load_prefs
        self.assertTrue(load_prefs()["auto_trade"])

    def test_set_bool_key_false(self):
        self._set("auto_trade", "false")
        from config import load_prefs
        self.assertFalse(load_prefs()["auto_trade"])

    def test_set_bool_key_yes(self):
        self._set("require_confirm", "yes")
        from config import load_prefs
        self.assertTrue(load_prefs()["require_confirm"])

    def test_set_list_key(self):
        self._set("watchlist", "BTC-USDT-SWAP,ETH-USDT-SWAP,SOL-USDT-SWAP")
        from config import load_prefs
        self.assertEqual(load_prefs()["watchlist"],
                         ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP"])

    def test_set_string_key(self):
        self._set("default_sz", "0.05")
        from config import load_prefs
        self.assertEqual(load_prefs()["default_sz"], "0.05")
        self.assertIsInstance(load_prefs()["default_sz"], str)

    def test_unknown_key_exits(self):
        import okx
        with self.assertRaises(SystemExit):
            okx.cmd_prefs(["set", "nonexistent_key", "value"])

    def test_set_missing_value_exits(self):
        import okx
        with self.assertRaises(SystemExit):
            okx.cmd_prefs(["set", "max_order_usd"])


if __name__ == "__main__":
    unittest.main()
