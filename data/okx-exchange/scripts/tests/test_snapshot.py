"""Unit tests for cmd_snapshot() in okx.py."""
import sys, os, json, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock


def _bal(equity=5000.0, avail_usdt=116.0):
    return {
        "code": "0",
        "data": [{"details": [
            {"ccy": "USDT", "eqUsd": str(avail_usdt), "availBal": str(avail_usdt)},
            {"ccy": "BTC",  "eqUsd": str(equity - avail_usdt), "availBal": "0.1"},
        ]}],
    }


def _pos(mark_px=66500.0, upl=0.75, realized=-0.03, liq_px=50000.0):
    return {
        "code": "0",
        "data": [{
            "instId": "BTC-USDT-SWAP",
            "posSide": "short",
            "pos": "0.1",
            "avgPx": str(67308.0),
            "markPx": str(mark_px),
            "upl": str(upl),
            "realizedPnl": str(realized),
            "liqPx": str(liq_px),
            "lever": "5",
        }],
    }


def _mock_client(bal=None, pos=None):
    m = MagicMock()
    m.balance.return_value = bal or _bal()
    m.positions.return_value = pos or _pos()
    return m


class TestCmdSnapshot(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import config
        config.SNAPSHOTS_PATH = os.path.join(self.tmp, "okx-monitor-snapshots.json")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _run(self, mock_client):
        import io
        with patch("okx_client.OKXClient", return_value=mock_client), \
             patch("sys.stdout", new_callable=io.StringIO) as out:
            import okx
            okx.cmd_snapshot([])
            return out.getvalue()

    def test_calls_balance_and_positions(self):
        mc = _mock_client()
        self._run(mc)
        mc.balance.assert_called_once()
        mc.positions.assert_called_once()

    def test_output_contains_equity(self):
        output = self._run(_mock_client(_bal(equity=5000.0)))
        self.assertIn("5,000.00", output)

    def test_output_contains_position(self):
        output = self._run(_mock_client(pos=_pos(mark_px=66500.0)))
        self.assertIn("BTC-USDT-SWAP", output)
        self.assertIn("66,500.0", output)

    def test_output_contains_initial_equity(self):
        output = self._run(_mock_client())
        self.assertIn("初始资金", output)

    def test_snapshot_file_written(self):
        import config
        self._run(_mock_client(_bal(equity=5000.0)))
        data = config.load_snapshots()
        self.assertEqual(len(data["snapshots"]), 1)
        self.assertAlmostEqual(data["snapshots"][0]["equity_usd"], 5000.0, places=0)

    def test_initial_equity_set_on_first_run(self):
        import config
        self._run(_mock_client(_bal(equity=5000.0)))
        data = config.load_snapshots()
        self.assertAlmostEqual(data["initial_equity"], 5000.0, places=0)

    def test_history_table_shown_after_two_runs(self):
        mc = _mock_client()
        self._run(mc)
        output = self._run(mc)
        self.assertIn("历史追踪", output)

    def test_no_history_table_on_first_run(self):
        output = self._run(_mock_client())
        self.assertNotIn("历史追踪", output)

    def test_unrealistic_liq_px_not_shown(self):
        # liq_px > mark_px * 50 → skip
        pos = _pos(mark_px=66500.0, liq_px=66500.0 * 60)
        output = self._run(_mock_client(pos=pos))
        self.assertNotIn("强平价", output)

    def test_realistic_liq_px_shown(self):
        pos = _pos(mark_px=66500.0, liq_px=50000.0)
        output = self._run(_mock_client(pos=pos))
        self.assertIn("强平价", output)

    def test_exits_on_balance_error(self):
        mc = _mock_client()
        mc.balance.return_value = {"code": "1", "msg": "Unauthorized"}
        with self.assertRaises(SystemExit):
            self._run(mc)

    def test_exits_on_positions_error(self):
        mc = _mock_client()
        mc.positions.return_value = {"code": "1", "msg": "Unauthorized"}
        with self.assertRaises(SystemExit):
            self._run(mc)

    def test_position_with_zero_sz_excluded(self):
        pos = _pos()
        pos["data"][0]["pos"] = "0"
        output = self._run(_mock_client(pos=pos))
        self.assertNotIn("BTC-USDT-SWAP", output.split("合约持仓")[-1])

    def test_equity_change_shown_on_second_run(self):
        import config
        # First run: equity 5000
        self._run(_mock_client(_bal(equity=5000.0)))
        # Second run: equity 5100
        import io
        mc2 = _mock_client(_bal(equity=5100.0))
        with patch("okx_client.OKXClient", return_value=mc2), \
             patch("sys.stdout", new_callable=io.StringIO) as out:
            import okx
            okx.cmd_snapshot([])
            output = out.getvalue()
        self.assertIn("+100.00", output)


if __name__ == "__main__":
    unittest.main()
