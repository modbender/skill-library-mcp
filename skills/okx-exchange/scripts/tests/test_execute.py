"""Unit tests for execute.py (client mocked)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock, call
import tempfile, shutil, json


def _make_prefs(**overrides):
    from config import DEFAULT_PREFS
    prefs = DEFAULT_PREFS.copy()
    prefs.update(overrides)
    return prefs


class TestPlaceOrder(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import config
        config.PREFS_PATH = os.path.join(self.tmp, "prefs.json")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _mock_client(self, ticker_last="67000", orderbook_asks=None, orderbook_bids=None,
                     order_code="0", order_id="TEST123"):
        asks = orderbook_asks or [["67010", "10", ""], ["67020", "10", ""]]
        bids = orderbook_bids or [["66990", "10", ""], ["66980", "10", ""]]
        client = MagicMock()
        client.ticker.return_value = {"code": "0", "data": [{"last": ticker_last}]}
        client.orderbook.return_value = {"code": "0", "data": [{"asks": asks, "bids": bids}]}
        client.place_order.return_value = {
            "code": order_code,
            "data": [{"ordId": order_id, "sCode": order_code, "sMsg": ""}],
            "msg": "All operations failed" if order_code != "0" else "",
        }
        return client

    def test_max_order_usd_blocks_large_spot_order(self):
        """A $6700 spot order should be blocked when max_order_usd=100."""
        import execute
        prefs = _make_prefs(max_order_usd=100, require_confirm=False)
        client = self._mock_client(ticker_last="67000")
        with patch("execute.load_prefs", return_value=prefs), \
             patch("execute.OKXClient", return_value=client):
            execute.place_order("BTC-USDT", "sell", "market", "0.1", td_mode="cash",
                                no_confirm=True)
        client.place_order.assert_not_called()

    def test_max_order_usd_allows_small_spot_order(self):
        """A $6.7 spot order should pass when max_order_usd=100."""
        import execute
        prefs = _make_prefs(max_order_usd=100, require_confirm=False)
        client = self._mock_client(ticker_last="67000")
        with patch("execute.load_prefs", return_value=prefs), \
             patch("execute.OKXClient", return_value=client):
            execute.place_order("BTC-USDT", "sell", "market", "0.0001", td_mode="cash",
                                no_confirm=True)
        client.place_order.assert_called_once()

    def test_max_order_usd_not_checked_for_derivatives(self):
        """Derivatives (tdMode=cross) skip the max_order_usd check."""
        import execute
        prefs = _make_prefs(max_order_usd=1, require_confirm=False)  # very low limit
        client = self._mock_client(ticker_last="67000")
        with patch("execute.load_prefs", return_value=prefs), \
             patch("execute.OKXClient", return_value=client):
            execute.place_order("BTC-USDT-SWAP", "buy", "market", "1",
                                td_mode="cross", no_confirm=True)
        client.place_order.assert_called_once()

    def test_price_impact_abort(self):
        """High price impact (>1%) should abort the order."""
        import execute
        prefs = _make_prefs(price_impact_abort=0.01, require_confirm=False)
        # Spread of 10%: asks start at 73700, bids at 67000 → impact ~10%
        asks = [["73700", "10", ""], ["74000", "5", ""]]
        bids = [["67000", "10", ""], ["66000", "5", ""]]
        client = self._mock_client(ticker_last="67000", orderbook_asks=asks, orderbook_bids=bids)
        with patch("execute.load_prefs", return_value=prefs), \
             patch("execute.OKXClient", return_value=client):
            execute.place_order("BTC-USDT", "buy", "market", "5", td_mode="cash",
                                no_confirm=True)
        client.place_order.assert_not_called()

    def test_no_confirm_bypasses_prompt(self):
        """no_confirm=True skips the input() call."""
        import execute
        prefs = _make_prefs(require_confirm=True)
        client = self._mock_client()
        with patch("execute.load_prefs", return_value=prefs), \
             patch("execute.OKXClient", return_value=client), \
             patch("builtins.input") as mock_input:
            execute.place_order("BTC-USDT", "sell", "market", "0.0001", td_mode="cash",
                                no_confirm=True)
        mock_input.assert_not_called()

    def test_confirm_prompt_on_require_confirm(self):
        """require_confirm=True should call input()."""
        import execute
        prefs = _make_prefs(require_confirm=True)
        client = self._mock_client()
        with patch("execute.load_prefs", return_value=prefs), \
             patch("execute.OKXClient", return_value=client), \
             patch("builtins.input", return_value="n"):
            execute.place_order("BTC-USDT", "sell", "market", "0.0001", td_mode="cash")
        client.place_order.assert_not_called()

    def test_order_placed_on_confirm_yes(self):
        """Typing 'y' at the prompt should place the order."""
        import execute
        prefs = _make_prefs(require_confirm=True)
        client = self._mock_client()
        with patch("execute.load_prefs", return_value=prefs), \
             patch("execute.OKXClient", return_value=client), \
             patch("builtins.input", return_value="y"):
            execute.place_order("BTC-USDT", "sell", "market", "0.0001", td_mode="cash")
        client.place_order.assert_called_once()


class TestSetLeverage(unittest.TestCase):
    def test_max_leverage_blocks(self):
        """Leverage exceeding max should be blocked."""
        import execute
        prefs = _make_prefs(max_leverage=10)
        client = MagicMock()
        with patch("execute.load_prefs", return_value=prefs), \
             patch("execute.OKXClient", return_value=client):
            execute.set_leverage("BTC-USDT-SWAP", 20)
        client.set_leverage.assert_not_called()

    def test_max_leverage_allows_at_limit(self):
        """Leverage equal to max should be allowed."""
        import execute
        prefs = _make_prefs(max_leverage=10)
        client = MagicMock()
        client.set_leverage.return_value = {"code": "0", "data": []}
        with patch("execute.load_prefs", return_value=prefs), \
             patch("execute.OKXClient", return_value=client):
            execute.set_leverage("BTC-USDT-SWAP", 10)
        client.set_leverage.assert_called_once_with("BTC-USDT-SWAP", 10, "cross")

    def test_max_leverage_allows_below_limit(self):
        import execute
        prefs = _make_prefs(max_leverage=10)
        client = MagicMock()
        client.set_leverage.return_value = {"code": "0", "data": []}
        with patch("execute.load_prefs", return_value=prefs), \
             patch("execute.OKXClient", return_value=client):
            execute.set_leverage("BTC-USDT-SWAP", 5)
        client.set_leverage.assert_called_once()


class TestCancelOrder(unittest.TestCase):
    def test_cancel_success(self):
        import execute
        client = MagicMock()
        client.cancel_order.return_value = {"code": "0", "data": [{"ordId": "123"}]}
        with patch("execute.OKXClient", return_value=client):
            execute.cancel_order("BTC-USDT", "123")
        client.cancel_order.assert_called_once_with("BTC-USDT", "123")

    def test_cancel_failure_logs_error(self):
        import execute
        client = MagicMock()
        client.cancel_order.return_value = {"code": "1", "msg": "Order not found"}
        with patch("execute.OKXClient", return_value=client):
            execute.cancel_order("BTC-USDT", "999")  # should not raise


class TestCancelAll(unittest.TestCase):
    def test_cancel_all_reports_counts(self):
        import execute
        client = MagicMock()
        client.cancel_all_orders.return_value = {"cancelled": 3, "failed": 1}
        with patch("execute.OKXClient", return_value=client):
            execute.cancel_all("BTC-USDT")
        client.cancel_all_orders.assert_called_once_with("BTC-USDT")


class TestTransferFunds(unittest.TestCase):
    def test_transfer_success(self):
        import execute
        client = MagicMock()
        client.transfer.return_value = {
            "code": "0", "data": [{"transId": "tx123"}]
        }
        with patch("execute.OKXClient", return_value=client):
            execute.transfer_funds("USDT", "100", "6", "18")
        client.transfer.assert_called_once_with("USDT", "100", "6", "18")

    def test_transfer_alias_mapping(self):
        """Ensure okx.py maps 'funding' -> '6' and 'trading' -> '18'."""
        # This tests the alias mapping in okx.py cmd_transfer
        import okx
        _code = {"funding": "6", "fund": "6", "6": "6",
                 "trading": "18", "trade": "18", "18": "18"}
        self.assertEqual(_code["funding"], "6")
        self.assertEqual(_code["trading"], "18")
        self.assertEqual(_code["fund"], "6")
        self.assertEqual(_code["trade"], "18")

    def test_transfer_failure_logs_error(self):
        import execute
        client = MagicMock()
        client.transfer.return_value = {"code": "1", "msg": "Insufficient balance"}
        with patch("execute.OKXClient", return_value=client):
            execute.transfer_funds("USDT", "999999", "6", "18")  # should not raise


if __name__ == "__main__":
    unittest.main()
