"""Unit tests for arbitrage.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "strategies"))

import unittest
from unittest.mock import patch, MagicMock
from errors import ArbHedgeFailedError


def _make_client(spot_px="67000", swap_px="67200", funding="0.0001"):
    client = MagicMock()
    client.ticker.side_effect = lambda inst_id: {
        "code": "0",
        "data": [{"last": spot_px if "SWAP" not in inst_id else swap_px}],
    }
    client.funding_rate.return_value = {
        "code": "0",
        "data": [{"fundingRate": funding}],
    }
    return client


class TestBasis(unittest.TestCase):
    def test_basis_calculation(self):
        from strategies.arbitrage import basis
        client = _make_client(spot_px="67000", swap_px="67200")
        with patch("strategies.arbitrage.OKXClient", return_value=client):
            result = basis("BTC-USDT", "BTC-USDT-SWAP")

        self.assertAlmostEqual(result["basis"], 200.0)
        self.assertAlmostEqual(result["basis_pct"], round(200 / 67000 * 100, 4))

    def test_signal_open_when_basis_above_threshold(self):
        from strategies.arbitrage import basis
        # basis_pct = 200/67000*100 ≈ 0.299% > 0.1 → "open"
        client = _make_client(spot_px="67000", swap_px="67200")
        with patch("strategies.arbitrage.OKXClient", return_value=client):
            result = basis("BTC-USDT", "BTC-USDT-SWAP")
        self.assertEqual(result["signal"], "open")

    def test_signal_close_when_basis_below_threshold(self):
        from strategies.arbitrage import basis
        # basis_pct = 10/67000*100 ≈ 0.015% < 0.02 → "close"
        client = _make_client(spot_px="67000", swap_px="67010")
        with patch("strategies.arbitrage.OKXClient", return_value=client):
            result = basis("BTC-USDT", "BTC-USDT-SWAP")
        self.assertEqual(result["signal"], "close")

    def test_signal_wait_in_between(self):
        from strategies.arbitrage import basis
        # basis_pct = 50/67000*100 ≈ 0.075% → between 0.02 and 0.1 → "wait"
        client = _make_client(spot_px="67000", swap_px="67050")
        with patch("strategies.arbitrage.OKXClient", return_value=client):
            result = basis("BTC-USDT", "BTC-USDT-SWAP")
        self.assertEqual(result["signal"], "wait")

    def test_annual_funding_calculation(self):
        from strategies.arbitrage import basis
        # funding_rate=0.0001 → 0.0001 * 3 * 365 * 100 = 10.95%/yr
        client = _make_client(funding="0.0001")
        with patch("strategies.arbitrage.OKXClient", return_value=client):
            result = basis("BTC-USDT", "BTC-USDT-SWAP")
        self.assertAlmostEqual(result["annual_funding_pct"], 10.95, places=1)

    def test_api_error_returns_error_dict(self):
        from strategies.arbitrage import basis
        client = MagicMock()
        client.ticker.return_value = {"code": "1", "msg": "timeout"}
        with patch("strategies.arbitrage.OKXClient", return_value=client):
            result = basis("BTC-USDT", "BTC-USDT-SWAP")
        self.assertIn("error", result)

    def test_negative_basis_when_spot_above_swap(self):
        from strategies.arbitrage import basis
        client = _make_client(spot_px="67200", swap_px="67000")
        with patch("strategies.arbitrage.OKXClient", return_value=client):
            result = basis("BTC-USDT", "BTC-USDT-SWAP")
        self.assertLess(result["basis"], 0)
        self.assertLess(result["basis_pct"], 0)


class TestOpenArb(unittest.TestCase):
    def test_hedge_failure_raises_arb_error(self):
        """If swap short fails after spot buy succeeds, raise ArbHedgeFailedError."""
        from strategies.arbitrage import open_arb
        client = MagicMock()
        client.ticker.side_effect = lambda inst_id: {
            "code": "0",
            "data": [{"last": "67000" if "SWAP" not in inst_id else "67200"}]
        }
        client.funding_rate.return_value = {
            "code": "0", "data": [{"fundingRate": "0.0001"}]
        }
        # Spot buy succeeds, swap short fails
        client.place_order.side_effect = [
            {"code": "0", "data": [{"ordId": "spot123"}]},  # spot buy OK
            {"code": "1", "msg": "Insufficient margin"},     # swap short FAIL
        ]

        with patch("strategies.arbitrage.OKXClient", return_value=client), \
             patch("builtins.input", return_value="y"):
            with self.assertRaises(ArbHedgeFailedError) as ctx:
                open_arb("BTC-USDT", "BTC-USDT-SWAP", 100, min_basis_pct=0.0)

        self.assertIn("swap-short", str(ctx.exception))

    def test_no_trade_when_basis_below_threshold(self):
        """No order placed if basis < min_basis_pct."""
        from strategies.arbitrage import open_arb
        client = _make_client(spot_px="67000", swap_px="67010")  # basis ≈ 0.015%

        with patch("strategies.arbitrage.OKXClient", return_value=client):
            open_arb("BTC-USDT", "BTC-USDT-SWAP", 100, min_basis_pct=0.1)

        client.place_order.assert_not_called()

    def test_cancel_at_prompt_skips_order(self):
        """User typing 'n' at confirm prompt should skip order placement."""
        from strategies.arbitrage import open_arb
        client = _make_client(spot_px="67000", swap_px="67300")

        with patch("strategies.arbitrage.OKXClient", return_value=client), \
             patch("builtins.input", return_value="n"):
            open_arb("BTC-USDT", "BTC-USDT-SWAP", 100, min_basis_pct=0.0)

        client.place_order.assert_not_called()


class TestScan(unittest.TestCase):
    def test_scan_handles_api_errors_gracefully(self):
        """scan() should not raise even if some pairs fail."""
        from strategies.arbitrage import scan
        client = MagicMock()
        client.ticker.return_value = {"code": "1", "msg": "timeout"}
        client.funding_rate.return_value = {"code": "1"}

        with patch("strategies.arbitrage.OKXClient", return_value=client):
            scan([("BTC-USDT", "BTC-USDT-SWAP")])  # should not raise

    def test_scan_processes_all_pairs(self):
        """scan() should call ticker for each pair."""
        from strategies.arbitrage import scan
        client = _make_client()

        with patch("strategies.arbitrage.OKXClient", return_value=client):
            scan([
                ("BTC-USDT", "BTC-USDT-SWAP"),
                ("ETH-USDT", "ETH-USDT-SWAP"),
            ])

        # 2 tickers per pair (spot + swap) × 2 pairs = 4 calls
        self.assertEqual(client.ticker.call_count, 4)


if __name__ == "__main__":
    unittest.main()
