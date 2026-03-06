"""Unit tests for account.py (client mocked)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO


def _balance_data(balances: dict) -> dict:
    """Build a mock balance response."""
    details = [
        {"ccy": ccy, "availBal": str(amt), "frozenBal": "0", "usdVal": str(amt)}
        for ccy, amt in balances.items()
    ]
    total_eq = sum(balances.values())
    return {
        "code": "0",
        "data": [{"totalEq": str(total_eq), "details": details}]
    }


class TestGetBalance(unittest.TestCase):
    def test_specific_currency(self):
        import account
        client = MagicMock()
        client.balance.return_value = _balance_data({"USDT": 1000.0})

        with patch("account.OKXClient", return_value=client):
            account.get_balance("USDT")

        client.balance.assert_called_once_with("USDT")

    def test_all_currencies(self):
        import account
        client = MagicMock()
        client.balance.return_value = _balance_data({
            "USDT": 1000.0, "BTC": 0.5, "ETH": 2.0
        })

        with patch("account.OKXClient", return_value=client):
            account.get_balance("")

        client.balance.assert_called_once_with("")

    def test_api_error_handled(self):
        import account
        client = MagicMock()
        client.balance.return_value = {"code": "1", "msg": "timeout"}

        with patch("account.OKXClient", return_value=client):
            account.get_balance("")  # should not raise


class TestGetPositions(unittest.TestCase):
    def test_no_positions(self):
        import account
        client = MagicMock()
        client.positions.return_value = {"code": "0", "data": []}

        with patch("account.OKXClient", return_value=client):
            account.get_positions("")  # should not raise

    def test_with_positions(self):
        import account
        client = MagicMock()
        client.positions.return_value = {"code": "0", "data": [
            {
                "instId": "BTC-USDT-SWAP",
                "posSide": "long",
                "pos": "1",
                "avgPx": "67000",
                "markPx": "67500",
                "upl": "5",
                "uplRatio": "0.0746",
                "lever": "5",
            }
        ]}

        with patch("account.OKXClient", return_value=client):
            account.get_positions("")  # should not raise

    def test_positions_filtered_by_inst_id(self):
        import account
        client = MagicMock()
        client.positions.return_value = {"code": "0", "data": []}

        with patch("account.OKXClient", return_value=client):
            # get_positions(inst_type, inst_id) — pass "" as inst_type
            account.get_positions("", "BTC-USDT-SWAP")

        client.positions.assert_called_once_with("", "BTC-USDT-SWAP")


class TestGetPendingOrders(unittest.TestCase):
    def test_no_pending_orders(self):
        import account
        client = MagicMock()
        client.pending_orders.return_value = {"code": "0", "data": []}

        with patch("account.OKXClient", return_value=client):
            account.get_pending_orders("")

    def test_with_pending_orders(self):
        import account
        client = MagicMock()
        client.pending_orders.return_value = {"code": "0", "data": [
            {
                "instId": "BTC-USDT",
                "ordId": "12345",
                "side": "buy",
                "ordType": "limit",
                "sz": "0.01",
                "px": "65000",
                "state": "live",
                "cTime": "1700000000000",
            }
        ]}

        with patch("account.OKXClient", return_value=client):
            account.get_pending_orders("")


class TestGetOrderHistory(unittest.TestCase):
    def test_order_history_spot(self):
        import account
        client = MagicMock()
        client.order_history.return_value = {"code": "0", "data": [
            {
                "instId": "BTC-USDT",
                "ordId": "111",
                "side": "sell",
                "ordType": "market",
                "sz": "0.001",
                "avgPx": "67000",
                "accFillSz": "0.001",
                "state": "filled",
                "uTime": "1700000000000",
                "pnl": "0",
            }
        ]}

        with patch("account.OKXClient", return_value=client):
            account.get_order_history("SPOT", "", 10)

        client.order_history.assert_called_once_with("SPOT", "", 10)

    def test_order_history_swap(self):
        import account
        client = MagicMock()
        client.order_history.return_value = {"code": "0", "data": []}

        with patch("account.OKXClient", return_value=client):
            account.get_order_history("SWAP", "BTC-USDT-SWAP", 20)

        client.order_history.assert_called_once_with("SWAP", "BTC-USDT-SWAP", 20)


class TestPortfolioSummary(unittest.TestCase):
    def test_portfolio_summary(self):
        import account
        client = MagicMock()
        client.balance.return_value = _balance_data({
            "USDT": 1000.0, "BTC": 0.5,
        })
        client.positions.return_value = {"code": "0", "data": []}
        client.pending_orders.return_value = {"code": "0", "data": []}

        with patch("account.OKXClient", return_value=client):
            account.portfolio_summary()  # should not raise

    def test_portfolio_summary_with_positions(self):
        import account
        client = MagicMock()
        client.balance.return_value = _balance_data({"USDT": 500.0})
        client.positions.return_value = {"code": "0", "data": [
            {
                "instId": "BTC-USDT-SWAP",
                "posSide": "long",
                "pos": "1",
                "avgPx": "67000",
                "markPx": "67500",
                "upl": "5",
                "uplRatio": "0.0746",
                "lever": "5",
            }
        ]}
        client.pending_orders.return_value = {"code": "0", "data": []}

        with patch("account.OKXClient", return_value=client):
            account.portfolio_summary()


if __name__ == "__main__":
    unittest.main()
