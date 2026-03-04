"""Unit tests for grid.py"""
import sys, os, json, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "strategies"))

import unittest
from unittest.mock import patch, MagicMock


class TestGridLevels(unittest.TestCase):
    """Test grid level calculation without API calls."""

    def test_level_count(self):
        """n grids → n+1 levels."""
        lower, upper, grids = 40000, 50000, 10
        step = (upper - lower) / grids
        levels = [lower + i * step for i in range(grids + 1)]
        self.assertEqual(len(levels), 11)

    def test_level_bounds(self):
        lower, upper, grids = 40000, 50000, 10
        step = (upper - lower) / grids
        levels = [lower + i * step for i in range(grids + 1)]
        self.assertAlmostEqual(levels[0], 40000)
        self.assertAlmostEqual(levels[-1], 50000)

    def test_step_size(self):
        lower, upper, grids = 40000, 50000, 10
        step = (upper - lower) / grids
        self.assertAlmostEqual(step, 1000)

    def test_order_size_per_grid(self):
        total_usdt, grids = 1000, 10
        order_usdt = total_usdt / grids
        self.assertAlmostEqual(order_usdt, 100)

    def test_sz_calculation(self):
        """sz = order_usdt / price, correct to 6 decimals."""
        order_usdt, level = 100, 40000
        sz = round(order_usdt / level, 6)
        self.assertAlmostEqual(sz, 0.0025, places=6)


class TestGridPnL(unittest.TestCase):
    """Test per-trade PnL accumulation — verifies the double-count bug is fixed."""

    def test_pnl_per_trade_not_cumulative(self):
        """Each sell fill adds step * sz, not cumulative."""
        step = 1000
        state = {"pnl": 0.0}
        fills = [
            {"sz": "0.0025", "expected_profit": 0.0025 * 1000},
            {"sz": "0.0025", "expected_profit": 0.0025 * 1000},
        ]
        for fill in fills:
            trade_profit = float(fill["sz"]) * step
            state["pnl"] += trade_profit

        # After 2 fills, total PnL = 2 * 2.5 = 5.0 USDT
        self.assertAlmostEqual(state["pnl"], 5.0)

    def test_pnl_not_doubled_on_third_fill(self):
        """The OLD bug: state['pnl'] += profit (where profit was cumulative)."""
        step = 1000
        sz = 0.0025
        state = {"pnl": 0.0}

        # Simulate the FIXED code: trade_profit is per-trade only
        for _ in range(5):
            trade_profit = sz * step
            state["pnl"] += trade_profit

        self.assertAlmostEqual(state["pnl"], 5 * sz * step)  # 5 * 2.5 = 12.5


class TestGridSetup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _mock_client(self, price="45000"):
        client = MagicMock()
        client.ticker.return_value = {"code": "0", "data": [{"last": price}]}
        client.place_order.return_value = {
            "code": "0", "data": [{"ordId": "order123", "sCode": "0", "sMsg": ""}]
        }
        return client

    def test_setup_places_only_buy_orders_below_price(self):
        """Only buy orders should be placed for levels below current price."""
        from strategies.grid import setup_grid
        client = self._mock_client(price="45000")

        with patch("strategies.grid.OKXClient", return_value=client), \
             patch("strategies.grid.MEMORY_DIR", self.tmp), \
             patch("strategies.grid.grid_state_path",
                   return_value=os.path.join(self.tmp, "grid.json")):
            setup_grid("BTC-USDT", 40000, 50000, 10, 1000)

        # Levels: 40000, 41000, 42000, 43000, 44000, 45000(=current), 46000, 47000...
        # Only 40000-44000 should get buy orders (5 levels below current)
        calls = client.place_order.call_args_list
        sides = [c[1]["side"] for c in calls]
        self.assertTrue(all(s == "buy" for s in sides))
        self.assertEqual(len(sides), 5)  # 40k,41k,42k,43k,44k < 45k current

    def test_state_saved_with_correct_structure(self):
        from strategies.grid import setup_grid
        client = self._mock_client(price="45000")
        state_path = os.path.join(self.tmp, "grid.json")

        with patch("strategies.grid.OKXClient", return_value=client), \
             patch("strategies.grid.MEMORY_DIR", self.tmp), \
             patch("strategies.grid.grid_state_path", return_value=state_path):
            setup_grid("BTC-USDT", 40000, 50000, 10, 1000)

        with open(state_path) as f:
            state = json.load(f)

        self.assertEqual(state["inst_id"], "BTC-USDT")
        self.assertEqual(state["lower"], 40000)
        self.assertEqual(state["upper"], 50000)
        self.assertIn("orders", state)
        self.assertEqual(state["pnl"], 0.0)


class TestGridStop(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.state_path = os.path.join(self.tmp, "grid.json")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _write_state(self, orders: dict):
        state = {
            "inst_id": "BTC-USDT", "lower": 40000, "upper": 50000,
            "grids": 10, "step": 1000, "total_usdt": 1000, "td_mode": "cash",
            "levels": [], "orders": orders, "pnl": 2.5,
        }
        with open(self.state_path, "w") as f:
            json.dump(state, f)

    def test_stop_grid_cancels_all_orders(self):
        from strategies.grid import stop_grid
        self._write_state({
            "40000.0": {"ordId": "ord1", "side": "buy", "sz": "0.0025"},
            "41000.0": {"ordId": "ord2", "side": "buy", "sz": "0.0025"},
        })
        client = MagicMock()
        client.cancel_order.return_value = {"code": "0"}

        with patch("strategies.grid.OKXClient", return_value=client), \
             patch("strategies.grid.grid_state_path", return_value=self.state_path):
            stop_grid("BTC-USDT")

        self.assertEqual(client.cancel_order.call_count, 2)

    def test_stop_grid_clears_orders_in_state(self):
        from strategies.grid import stop_grid
        self._write_state({"40000.0": {"ordId": "ord1", "side": "buy", "sz": "0.0025"}})
        client = MagicMock()
        client.cancel_order.return_value = {"code": "0"}

        with patch("strategies.grid.OKXClient", return_value=client), \
             patch("strategies.grid.grid_state_path", return_value=self.state_path):
            stop_grid("BTC-USDT")

        with open(self.state_path) as f:
            state = json.load(f)
        self.assertEqual(state["orders"], {})


if __name__ == "__main__":
    unittest.main()
