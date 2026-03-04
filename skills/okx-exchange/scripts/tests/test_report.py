"""Unit tests for report.py — performance report generation."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import tempfile
import shutil
from datetime import datetime, timezone, timedelta
from unittest.mock import patch


def _make_trade(ts: str, inst_id: str, pnl_pct: float, action: str = "stop_loss") -> dict:
    """Helper to build a monitor-journal trade entry."""
    return {"ts": ts, "inst_id": inst_id, "action": action, "upl_pct": pnl_pct}


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _days_ago(n: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=n)).strftime("%Y-%m-%dT%H:%M:%S")


class TestReportStats(unittest.TestCase):

    def test_empty_trades(self):
        import report
        s = report._stats([])
        self.assertEqual(s["count"], 0)
        self.assertEqual(s["wins"], 0)
        self.assertEqual(s["win_rate"], 0.0)
        self.assertEqual(s["total_pnl"], 0.0)

    def test_all_wins(self):
        import report
        trades = [{"pnl_pct": p} for p in [1.0, 2.0, 3.0]]
        s = report._stats(trades)
        self.assertEqual(s["wins"], 3)
        self.assertEqual(s["losses"], 0)
        self.assertAlmostEqual(s["win_rate"], 100.0)
        self.assertAlmostEqual(s["total_pnl"], 6.0)

    def test_all_losses(self):
        import report
        trades = [{"pnl_pct": p} for p in [-1.0, -2.0]]
        s = report._stats(trades)
        self.assertEqual(s["wins"], 0)
        self.assertEqual(s["losses"], 2)
        self.assertAlmostEqual(s["win_rate"], 0.0)

    def test_mixed_win_loss(self):
        import report
        trades = [{"pnl_pct": 5.0}, {"pnl_pct": -2.0}, {"pnl_pct": 3.0}]
        s = report._stats(trades)
        self.assertEqual(s["wins"], 2)
        self.assertEqual(s["losses"], 1)
        self.assertAlmostEqual(s["win_rate"], 2 / 3 * 100, places=1)
        self.assertAlmostEqual(s["best"], 5.0)
        self.assertAlmostEqual(s["worst"], -2.0)

    def test_none_pnl_ignored(self):
        """pnl_pct=None should not cause TypeError (regression test)."""
        import report
        trades = [{"pnl_pct": None}, {"pnl_pct": 3.0}, {"pnl_pct": 0}]
        s = report._stats(trades)
        self.assertEqual(s["wins"], 1)

    def test_zero_pnl_excluded(self):
        """pnl_pct=0 is excluded (no closed P&L)."""
        import report
        trades = [{"pnl_pct": 0}, {"pnl_pct": 2.0}]
        s = report._stats(trades)
        self.assertEqual(s["wins"], 1)


class TestReportCoinBreakdown(unittest.TestCase):

    def test_coin_extracted_from_inst_id(self):
        import report
        trades = [
            {"inst_id": "BTC-USDT-SWAP", "pnl_pct": 5.0},
            {"inst_id": "BTC-USDT-SWAP", "pnl_pct": -2.0},
            {"inst_id": "ETH-USDT-SWAP", "pnl_pct": 3.0},
        ]
        coins = report._coin_breakdown(trades)
        self.assertIn("BTC", coins)
        self.assertIn("ETH", coins)
        self.assertAlmostEqual(coins["BTC"]["total_pnl"], 3.0)
        self.assertAlmostEqual(coins["ETH"]["total_pnl"], 3.0)

    def test_sorted_by_total_pnl_descending(self):
        import report
        trades = [
            {"inst_id": "BTC-USDT-SWAP", "pnl_pct": 1.0},
            {"inst_id": "ETH-USDT-SWAP", "pnl_pct": 10.0},
            {"inst_id": "SOL-USDT-SWAP", "pnl_pct": 5.0},
        ]
        coins = report._coin_breakdown(trades)
        keys = list(coins.keys())
        self.assertEqual(keys[0], "ETH")
        self.assertEqual(keys[1], "SOL")

    def test_none_pnl_excluded_in_breakdown(self):
        """Regression: None pnl_pct should not cause TypeError."""
        import report
        trades = [
            {"inst_id": "BTC-USDT-SWAP", "pnl_pct": None},
            {"inst_id": "BTC-USDT-SWAP", "pnl_pct": 5.0},
        ]
        coins = report._coin_breakdown(trades)
        self.assertIn("BTC", coins)
        self.assertEqual(coins["BTC"]["trades"], 1)


class TestReportPeriodFilter(unittest.TestCase):

    def test_daily_includes_today(self):
        import report
        trades = [
            {"ts": _today(), "pnl_pct": 1.0},
            {"ts": _days_ago(2), "pnl_pct": 2.0},
        ]
        result = report._period_trades(trades, 1)
        self.assertEqual(len(result), 1)

    def test_weekly_includes_last_7_days(self):
        import report
        trades = [
            {"ts": _today(), "pnl_pct": 1.0},
            {"ts": _days_ago(5), "pnl_pct": 2.0},
            {"ts": _days_ago(10), "pnl_pct": 3.0},
        ]
        result = report._period_trades(trades, 7)
        self.assertEqual(len(result), 2)

    def test_all_includes_everything(self):
        import report
        trades = [
            {"ts": _today(), "pnl_pct": 1.0},
            {"ts": _days_ago(365), "pnl_pct": 2.0},
        ]
        result = report._period_trades(trades, 9999)
        self.assertEqual(len(result), 2)


class TestReportGenerate(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _write_journal(self, trades: list, filename: str) -> str:
        path = os.path.join(self.tmp, filename)
        with open(path, "w") as f:
            json.dump({"trades": trades}, f)
        return path

    def test_generate_report_daily_no_trades(self):
        import report
        journal = self._write_journal([], "journal.json")
        learning = self._write_journal([], "learning.json")
        with patch.object(report, "JOURNAL_PATH", ""), \
             patch.object(report, "LEARNING_JOURNAL", ""):
            text = report.generate_report("daily")
        self.assertIn("暂无交易记录", text)

    def test_generate_report_contains_header(self):
        import report
        with patch.object(report, "JOURNAL_PATH", ""), \
             patch.object(report, "LEARNING_JOURNAL", ""):
            text = report.generate_report("weekly")
        self.assertIn("OKX 交易绩效报告", text)
        self.assertIn("本周", text)

    def test_generate_report_all_label(self):
        import report
        with patch.object(report, "JOURNAL_PATH", ""), \
             patch.object(report, "LEARNING_JOURNAL", ""):
            text = report.generate_report("all")
        self.assertIn("全部", text)

    def test_generate_report_with_trades(self):
        import report
        journal_path = self._write_journal([
            {"ts": _today(), "inst_id": "BTC-USDT-SWAP", "action": "take_profit", "upl_pct": 5.5},
            {"ts": _today(), "inst_id": "ETH-USDT-SWAP", "action": "stop_loss", "upl_pct": -2.1},
        ], "journal.json")
        with patch.object(report, "JOURNAL_PATH", journal_path), \
             patch.object(report, "LEARNING_JOURNAL", ""):
            text = report.generate_report("daily")
        self.assertIn("BTC", text)
        self.assertNotIn("暂无交易记录", text)


if __name__ == "__main__":
    unittest.main()
