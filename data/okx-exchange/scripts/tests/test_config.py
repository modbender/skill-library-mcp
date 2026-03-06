"""Unit tests for config.py"""
import sys, os, json, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # Redirect MEMORY_DIR to a temp directory for all tests
        self._patcher = patch("config.MEMORY_DIR", self.tmp)
        self._patcher.start()
        # Also patch the path constants that were already bound at import time
        import config
        config.PREFS_PATH = os.path.join(self.tmp, "okx-trading-preferences.json")
        config.STATE_PATH = os.path.join(self.tmp, "okx-trading-state.json")
        config.JOURNAL_PATH = os.path.join(self.tmp, "okx-trading-journal.json")

    def tearDown(self):
        self._patcher.stop()
        shutil.rmtree(self.tmp)

    def test_load_prefs_returns_defaults_when_no_file(self):
        import config
        prefs = config.load_prefs()
        self.assertIn("max_order_usd", prefs)
        self.assertIn("stop_loss_pct", prefs)
        self.assertIn("watchlist", prefs)

    def test_save_and_load_prefs_roundtrip(self):
        import config
        prefs = config.load_prefs()
        prefs["max_order_usd"] = 999
        config.save_prefs(prefs)
        loaded = config.load_prefs()
        self.assertEqual(loaded["max_order_usd"], 999)

    def test_load_prefs_merges_defaults_for_missing_keys(self):
        import config
        # Write partial prefs (missing some keys)
        partial = {"max_order_usd": 50}
        with open(config.PREFS_PATH, "w") as f:
            json.dump(partial, f)
        prefs = config.load_prefs()
        # All default keys should still be present
        self.assertEqual(prefs["max_order_usd"], 50)
        self.assertIn("stop_loss_pct", prefs)
        self.assertIn("auto_trade", prefs)

    def test_load_state_returns_defaults(self):
        import config
        state = config.load_state()
        self.assertIn("daily_trades", state)
        self.assertEqual(state["daily_trades"], 0)

    def test_save_and_load_state_roundtrip(self):
        import config
        state = config.load_state()
        state["daily_trades"] = 5
        config.save_state(state)
        loaded = config.load_state()
        self.assertEqual(loaded["daily_trades"], 5)

    def test_log_trade_appends(self):
        import config
        config.log_trade({"inst_id": "BTC-USDT", "action": "buy"})
        config.log_trade({"inst_id": "ETH-USDT", "action": "sell"})
        with open(config.JOURNAL_PATH) as f:
            data = json.load(f)
        trades = data["trades"]  # journal is {"trades": [...]}
        self.assertEqual(len(trades), 2)
        self.assertEqual(trades[0]["inst_id"], "BTC-USDT")
        self.assertEqual(trades[1]["action"], "sell")

    def test_log_trade_appends_to_existing(self):
        import config
        config.log_trade({"inst_id": "BTC-USDT", "action": "buy"})
        config.log_trade({"inst_id": "ETH-USDT", "action": "sell"})
        config.log_trade({"inst_id": "SOL-USDT", "action": "buy"})
        with open(config.JOURNAL_PATH) as f:
            data = json.load(f)
        self.assertEqual(len(data["trades"]), 3)

    def test_grid_state_path(self):
        import config
        path = config.grid_state_path("BTC-USDT")
        self.assertIn("BTC-USDT", path)
        self.assertTrue(path.endswith(".json"))

    def test_default_prefs_types(self):
        import config
        prefs = config.DEFAULT_PREFS
        self.assertIsInstance(prefs["max_order_usd"], (int, float))
        self.assertIsInstance(prefs["require_confirm"], bool)
        self.assertIsInstance(prefs["watchlist"], list)
        self.assertIsInstance(prefs["strategies"], list)


class TestSnapshots(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import config
        config.SNAPSHOTS_PATH = os.path.join(self.tmp, "okx-monitor-snapshots.json")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_load_snapshots_returns_defaults_when_no_file(self):
        import config
        data = config.load_snapshots()
        self.assertIsNone(data["initial_equity"])
        self.assertEqual(data["snapshots"], [])

    def test_save_snapshot_sets_initial_equity_on_first_write(self):
        import config
        config.save_snapshot({"equity_usd": 1000.0, "ts_label": "01:00"})
        data = config.load_snapshots()
        self.assertEqual(data["initial_equity"], 1000.0)

    def test_save_snapshot_does_not_overwrite_initial_equity(self):
        import config
        config.save_snapshot({"equity_usd": 1000.0, "ts_label": "01:00"})
        config.save_snapshot({"equity_usd": 1200.0, "ts_label": "01:01"})
        data = config.load_snapshots()
        self.assertEqual(data["initial_equity"], 1000.0)  # unchanged

    def test_save_snapshot_appends_entries(self):
        import config
        config.save_snapshot({"equity_usd": 1000.0, "ts_label": "01:00"})
        config.save_snapshot({"equity_usd": 1010.0, "ts_label": "01:01"})
        data = config.load_snapshots()
        self.assertEqual(len(data["snapshots"]), 2)
        self.assertEqual(data["snapshots"][1]["equity_usd"], 1010.0)

    def test_save_snapshot_caps_at_48(self):
        import config
        for i in range(50):
            config.save_snapshot({"equity_usd": float(i), "ts_label": f"{i:02d}:00"})
        data = config.load_snapshots()
        self.assertEqual(len(data["snapshots"]), 48)
        # Oldest entries are dropped; last entry is the most recent
        self.assertEqual(data["snapshots"][-1]["equity_usd"], 49.0)

    def test_save_and_load_roundtrip(self):
        import config
        snap = {"equity_usd": 5000.0, "ts_label": "02:30",
                "avail_usdt": 116.5, "total_upl": 0.75}
        config.save_snapshot(snap)
        data = config.load_snapshots()
        self.assertEqual(data["snapshots"][0]["avail_usdt"], 116.5)
        self.assertEqual(data["snapshots"][0]["total_upl"], 0.75)


if __name__ == "__main__":
    unittest.main()
