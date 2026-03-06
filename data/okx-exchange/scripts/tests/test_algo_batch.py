"""Unit tests for algo orders and batch orders."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock


def _client():
    with patch("okx_client._sync_time"), patch("okx_client._load_env"):
        from okx_client import OKXClient
        with patch.dict(os.environ, {
            "OKX_API_KEY": "key", "OKX_SECRET_KEY": "secret",
            "OKX_PASSPHRASE": "pass", "OKX_SIMULATED": "1",
        }):
            return OKXClient()


# ── place_algo_order() ────────────────────────────────────────────────────────

class TestPlaceAlgoOrder(unittest.TestCase):

    def test_oco_body_has_tp_and_sl(self):
        client = _client()
        ok = {"code": "0", "data": [{"algoId": "algo123", "sCode": "0"}]}
        with patch.object(client, "post", return_value=ok) as m:
            client.place_algo_order(
                inst_id="BTC-USDT-SWAP", td_mode="cross", side="sell",
                ord_type="oco", sz="1",
                tp_trigger_px="55000", sl_trigger_px="45000",
            )
            body = m.call_args[0][1]
        self.assertEqual(body["ordType"], "oco")
        self.assertEqual(body["tpTriggerPx"], "55000")
        self.assertEqual(body["slTriggerPx"], "45000")
        self.assertEqual(body["tpOrdPx"], "-1")   # market execution
        self.assertEqual(body["slOrdPx"], "-1")
        self.assertEqual(body["tpTriggerPxType"], "last")
        self.assertEqual(body["slTriggerPxType"], "last")

    def test_conditional_body_sl_only(self):
        client = _client()
        ok = {"code": "0", "data": [{"algoId": "algo456", "sCode": "0"}]}
        with patch.object(client, "post", return_value=ok) as m:
            client.place_algo_order(
                inst_id="BTC-USDT-SWAP", td_mode="cross", side="sell",
                ord_type="conditional", sz="1", sl_trigger_px="45000",
            )
            body = m.call_args[0][1]
        self.assertEqual(body["ordType"], "conditional")
        self.assertIn("slTriggerPx", body)
        self.assertNotIn("tpTriggerPx", body)

    def test_conditional_body_tp_only(self):
        client = _client()
        ok = {"code": "0", "data": [{"algoId": "algo789", "sCode": "0"}]}
        with patch.object(client, "post", return_value=ok) as m:
            client.place_algo_order(
                inst_id="BTC-USDT-SWAP", td_mode="cross", side="sell",
                ord_type="conditional", sz="1", tp_trigger_px="55000",
            )
            body = m.call_args[0][1]
        self.assertIn("tpTriggerPx", body)
        self.assertNotIn("slTriggerPx", body)

    def test_custom_ord_px_used_when_provided(self):
        client = _client()
        ok = {"code": "0", "data": [{"algoId": "x", "sCode": "0"}]}
        with patch.object(client, "post", return_value=ok) as m:
            client.place_algo_order(
                inst_id="BTC-USDT-SWAP", td_mode="cross", side="sell",
                ord_type="conditional", sz="1",
                sl_trigger_px="45000", sl_ord_px="44500",
            )
            body = m.call_args[0][1]
        self.assertEqual(body["slOrdPx"], "44500")

    def test_reduce_only_flag(self):
        client = _client()
        ok = {"code": "0", "data": [{"algoId": "x", "sCode": "0"}]}
        with patch.object(client, "post", return_value=ok) as m:
            client.place_algo_order(
                inst_id="BTC-USDT-SWAP", td_mode="cross", side="sell",
                ord_type="conditional", sz="1", sl_trigger_px="45000",
                reduce_only=True,
            )
            body = m.call_args[0][1]
        self.assertEqual(body["reduceOnly"], "true")

    def test_pos_side_included_when_set(self):
        client = _client()
        ok = {"code": "0", "data": [{"algoId": "x", "sCode": "0"}]}
        with patch.object(client, "post", return_value=ok) as m:
            client.place_algo_order(
                inst_id="BTC-USDT-SWAP", td_mode="cross", side="sell",
                ord_type="oco", sz="1",
                tp_trigger_px="55000", sl_trigger_px="45000",
                pos_side="long",
            )
            body = m.call_args[0][1]
        self.assertEqual(body["posSide"], "long")

    def test_posts_to_correct_endpoint(self):
        client = _client()
        ok = {"code": "0", "data": [{"algoId": "x", "sCode": "0"}]}
        with patch.object(client, "post", return_value=ok) as m:
            client.place_algo_order("BTC-USDT-SWAP", "cross", "sell", "oco", "1",
                                    tp_trigger_px="55000", sl_trigger_px="45000")
            endpoint = m.call_args[0][0]
        self.assertEqual(endpoint, "/api/v5/trade/order-algo")


# ── cancel_algo_order() ───────────────────────────────────────────────────────

class TestCancelAlgoOrder(unittest.TestCase):

    def test_cancel_posts_list_payload(self):
        client = _client()
        ok = {"code": "0", "data": [{"algoId": "algo123", "sCode": "0"}]}
        with patch.object(client, "post", return_value=ok) as m:
            client.cancel_algo_order("BTC-USDT-SWAP", "algo123")
            endpoint, body = m.call_args[0]
        self.assertEqual(endpoint, "/api/v5/trade/cancel-algos")
        self.assertIsInstance(body, list)
        self.assertEqual(body[0]["instId"], "BTC-USDT-SWAP")
        self.assertEqual(body[0]["algoId"], "algo123")


# ── pending_algo_orders() ─────────────────────────────────────────────────────

class TestPendingAlgoOrders(unittest.TestCase):

    def test_no_params_empty_dict(self):
        client = _client()
        ok = {"code": "0", "data": []}
        with patch.object(client, "get", return_value=ok) as m:
            client.pending_algo_orders()
            params = m.call_args[0][1]
        self.assertEqual(params, {})

    def test_with_inst_id(self):
        client = _client()
        ok = {"code": "0", "data": []}
        with patch.object(client, "get", return_value=ok) as m:
            client.pending_algo_orders(inst_id="BTC-USDT-SWAP")
            params = m.call_args[0][1]
        self.assertEqual(params["instId"], "BTC-USDT-SWAP")

    def test_with_ord_type(self):
        client = _client()
        ok = {"code": "0", "data": []}
        with patch.object(client, "get", return_value=ok) as m:
            client.pending_algo_orders(ord_type="oco")
            params = m.call_args[0][1]
        self.assertEqual(params["ordType"], "oco")

    def test_posts_to_correct_endpoint(self):
        client = _client()
        ok = {"code": "0", "data": []}
        with patch.object(client, "get", return_value=ok) as m:
            client.pending_algo_orders()
            endpoint = m.call_args[0][0]
        self.assertEqual(endpoint, "/api/v5/trade/orders-algo-pending")


# ── batch_orders() ────────────────────────────────────────────────────────────

class TestBatchOrders(unittest.TestCase):

    def _sample_orders(self, n: int = 3) -> list:
        return [
            {"instId": f"COIN{i}-USDT-SWAP", "tdMode": "cross",
             "side": "buy", "ordType": "market", "sz": "1"}
            for i in range(n)
        ]

    def test_batch_posts_list(self):
        client = _client()
        ok = {"code": "0", "data": [{"ordId": str(i), "sCode": "0"} for i in range(3)]}
        with patch.object(client, "post", return_value=ok) as m:
            orders = self._sample_orders(3)
            client.batch_orders(orders)
            endpoint, body = m.call_args[0]
        self.assertEqual(endpoint, "/api/v5/trade/batch-orders")
        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 3)

    def test_batch_preserves_order_fields(self):
        client = _client()
        ok = {"code": "0", "data": [{"ordId": "1", "sCode": "0"}]}
        with patch.object(client, "post", return_value=ok) as m:
            orders = [{"instId": "BTC-USDT-SWAP", "tdMode": "cross",
                       "side": "sell", "ordType": "limit", "sz": "0.5", "px": "60000"}]
            client.batch_orders(orders)
            body = m.call_args[0][1]
        self.assertEqual(body[0]["px"], "60000")
        self.assertEqual(body[0]["ordType"], "limit")

    def test_batch_returns_response(self):
        client = _client()
        ok = {"code": "0", "data": [
            {"ordId": "1", "sCode": "0"},
            {"ordId": "", "sCode": "51008", "sMsg": "Insufficient balance"},
        ]}
        with patch.object(client, "post", return_value=ok):
            result = client.batch_orders(self._sample_orders(2))
        self.assertEqual(result["code"], "0")
        self.assertEqual(len(result["data"]), 2)

    def test_empty_batch_still_posts(self):
        client = _client()
        ok = {"code": "0", "data": []}
        with patch.object(client, "post", return_value=ok) as m:
            client.batch_orders([])
        m.assert_called_once()


# ── cmd_algo() integration ────────────────────────────────────────────────────

class TestCmdAlgo(unittest.TestCase):

    def _mock_client(self, algo_orders=None):
        mock = MagicMock()
        mock.pending_algo_orders.return_value = {
            "code": "0",
            "data": algo_orders or [],
        }
        mock.place_algo_order.return_value = {
            "code": "0", "data": [{"algoId": "algo999", "sCode": "0"}],
        }
        mock.cancel_algo_order.return_value = {
            "code": "0", "data": [{"algoId": "algo999", "sCode": "0"}],
        }
        return mock

    def test_list_no_orders(self):
        import okx
        with patch("okx_client.OKXClient", return_value=self._mock_client()):
            okx.cmd_algo(["list"])  # should not raise

    def test_list_with_orders(self):
        import okx
        orders = [{"algoId": "a1", "instId": "BTC-USDT-SWAP",
                   "ordType": "oco", "side": "sell", "sz": "1",
                   "tpTriggerPx": "55000", "slTriggerPx": "45000"}]
        with patch("okx_client.OKXClient", return_value=self._mock_client(orders)):
            okx.cmd_algo(["list"])  # should not raise

    def test_oco_missing_tp_exits(self):
        import okx
        with patch("okx_client.OKXClient", return_value=self._mock_client()):
            with self.assertRaises(SystemExit):
                okx.cmd_algo(["oco", "BTC-USDT-SWAP", "1", "--sl", "45000"])

    def test_oco_missing_sl_exits(self):
        import okx
        with patch("okx_client.OKXClient", return_value=self._mock_client()):
            with self.assertRaises(SystemExit):
                okx.cmd_algo(["oco", "BTC-USDT-SWAP", "1", "--tp", "55000"])

    def test_stop_missing_sl_exits(self):
        import okx
        with patch("okx_client.OKXClient", return_value=self._mock_client()):
            with self.assertRaises(SystemExit):
                okx.cmd_algo(["stop", "BTC-USDT-SWAP", "1"])

    def test_oco_no_confirm_places_order(self):
        import okx
        mock = self._mock_client()
        with patch("okx_client.OKXClient", return_value=mock):
            okx.cmd_algo(["oco", "BTC-USDT-SWAP", "1",
                          "--tp", "55000", "--sl", "45000", "--no-confirm"])
        mock.place_algo_order.assert_called_once()
        _, kwargs = mock.place_algo_order.call_args
        self.assertEqual(mock.place_algo_order.call_args[1].get("ord_type") or
                         mock.place_algo_order.call_args[0][3], "oco")

    def test_cancel_requires_algo_id(self):
        import okx
        with patch("okx_client.OKXClient", return_value=self._mock_client()):
            with self.assertRaises(SystemExit):
                okx.cmd_algo(["cancel", "BTC-USDT-SWAP"])  # missing algo_id

    def test_cancel_calls_client(self):
        import okx
        mock = self._mock_client()
        with patch("okx_client.OKXClient", return_value=mock):
            okx.cmd_algo(["cancel", "BTC-USDT-SWAP", "algo999"])
        mock.cancel_algo_order.assert_called_once_with("BTC-USDT-SWAP", "algo999")

    def test_unknown_sub_exits(self):
        import okx
        with patch("okx_client.OKXClient", return_value=self._mock_client()):
            with self.assertRaises(SystemExit):
                okx.cmd_algo(["invalid"])


if __name__ == "__main__":
    unittest.main()
