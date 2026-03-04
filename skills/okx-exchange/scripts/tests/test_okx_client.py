"""Unit tests for okx_client.py (all HTTP calls mocked)"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock
import requests

from errors import NetworkError, APIError


def _make_response(data: dict, status: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.ok = (status < 400)
    mock.status_code = status
    mock.json.return_value = data
    return mock


class TestSign(unittest.TestCase):
    def test_sign_returns_base64_string(self):
        from okx_client import _sign
        result = _sign("2024-01-01T00:00:00.000Z", "GET", "/api/v5/account/balance", "", "secret")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 10)

    def test_sign_deterministic(self):
        from okx_client import _sign
        s1 = _sign("ts", "GET", "/path", "", "secret")
        s2 = _sign("ts", "GET", "/path", "", "secret")
        self.assertEqual(s1, s2)

    def test_sign_different_for_different_inputs(self):
        from okx_client import _sign
        s1 = _sign("ts", "GET", "/path1", "", "secret")
        s2 = _sign("ts", "GET", "/path2", "", "secret")
        self.assertNotEqual(s1, s2)

    def test_sign_different_for_different_secrets(self):
        from okx_client import _sign
        s1 = _sign("ts", "GET", "/path", "", "secret1")
        s2 = _sign("ts", "GET", "/path", "", "secret2")
        self.assertNotEqual(s1, s2)


class TestTimestamp(unittest.TestCase):
    def test_timestamp_format(self):
        from okx_client import _timestamp
        ts = _timestamp()
        self.assertRegex(ts, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z")


class TestOKXClientRequest(unittest.TestCase):
    def _client(self):
        with patch("okx_client._sync_time"):
            from okx_client import OKXClient
            with patch.dict(os.environ, {
                "OKX_API_KEY": "key", "OKX_SECRET_KEY": "secret",
                "OKX_PASSPHRASE": "pass", "OKX_SIMULATED": "1"
            }):
                return OKXClient()

    def test_get_builds_query_string(self):
        client = self._client()
        ok_resp = _make_response({"code": "0", "data": []})
        with patch("requests.get", return_value=ok_resp) as mock_get:
            client.get("/api/v5/market/ticker", {"instId": "BTC-USDT"})
            url = mock_get.call_args[0][0]
            self.assertIn("instId=BTC-USDT", url)

    def test_post_sends_json_body(self):
        client = self._client()
        ok_resp = _make_response({"code": "0", "data": []})
        with patch("requests.post", return_value=ok_resp) as mock_post:
            client.post("/api/v5/trade/order", {"instId": "BTC-USDT"})
            body = mock_post.call_args[1]["data"]
            parsed = json.loads(body)
            self.assertEqual(parsed["instId"], "BTC-USDT")

    def test_simulated_header_set(self):
        client = self._client()
        ok_resp = _make_response({"code": "0", "data": []})
        with patch("requests.get", return_value=ok_resp) as mock_get:
            client.get("/api/v5/account/balance")
            headers = mock_get.call_args[1]["headers"]
            self.assertEqual(headers["x-simulated-trading"], "1")

    def test_retry_on_connection_error(self):
        client = self._client()
        ok_resp = _make_response({"code": "0", "data": []})
        with patch("requests.get", side_effect=[
            requests.exceptions.ConnectionError("conn"),
            ok_resp,
        ]) as mock_get:
            with patch("time.sleep"):
                result = client.get("/api/v5/account/balance")
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(result["code"], "0")

    def test_raises_network_error_after_3_retries(self):
        client = self._client()
        with patch("requests.get", side_effect=requests.exceptions.Timeout("timeout")):
            with patch("time.sleep"):
                with self.assertRaises(NetworkError):
                    client.get("/api/v5/account/balance")

    def test_raises_api_error_on_http_error(self):
        client = self._client()
        err_resp = _make_response({"code": "50111", "msg": "Invalid API key"}, status=401)
        with patch("requests.get", return_value=err_resp):
            with self.assertRaises(APIError) as ctx:
                client.get("/api/v5/account/balance")
            self.assertEqual(ctx.exception.status, 401)

    def test_get_no_params(self):
        client = self._client()
        ok_resp = _make_response({"code": "0", "data": []})
        with patch("requests.get", return_value=ok_resp) as mock_get:
            client.get("/api/v5/account/config")
            url = mock_get.call_args[0][0]
            self.assertNotIn("?", url)

    def test_cancel_all_orders_counts_correctly(self):
        client = self._client()
        pending_resp = _make_response({"code": "0", "data": [
            {"ordId": "1"}, {"ordId": "2"}, {"ordId": "3"},
        ]})
        cancel_ok = _make_response({"code": "0", "data": [{"ordId": "x"}]})
        cancel_fail = _make_response({"code": "1", "data": [{"sCode": "51400", "sMsg": "Already cancelled"}]})

        with patch.object(client, "pending_orders", return_value=pending_resp.json()):
            with patch.object(client, "cancel_order", side_effect=[
                cancel_ok.json(), cancel_ok.json(), cancel_fail.json()
            ]):
                result = client.cancel_all_orders("BTC-USDT")

        self.assertEqual(result["cancelled"], 2)
        self.assertEqual(result["failed"], 1)


class TestOKXClientMethods(unittest.TestCase):
    def _client(self):
        with patch("okx_client._sync_time"):
            from okx_client import OKXClient
            with patch.dict(os.environ, {
                "OKX_API_KEY": "key", "OKX_SECRET_KEY": "secret",
                "OKX_PASSPHRASE": "pass", "OKX_SIMULATED": "1"
            }):
                return OKXClient()

    def _mock_get(self, data):
        return patch.object(self._client().__class__, "get",
                            return_value={"code": "0", "data": data})

    def test_ticker_passes_inst_id(self):
        client = self._client()
        ok = {"code": "0", "data": [{"last": "50000"}]}
        with patch.object(client, "get", return_value=ok) as m:
            client.ticker("BTC-USDT")
            m.assert_called_once_with("/api/v5/market/ticker", {"instId": "BTC-USDT"})

    def test_candles_default_params(self):
        client = self._client()
        ok = {"code": "0", "data": []}
        with patch.object(client, "get", return_value=ok) as m:
            client.candles("BTC-USDT")
            _, kwargs = m.call_args
            params = m.call_args[0][1]
            self.assertEqual(params["bar"], "1H")
            self.assertEqual(params["limit"], 100)

    def test_place_order_body(self):
        client = self._client()
        ok = {"code": "0", "data": [{"ordId": "123", "sCode": "0", "sMsg": ""}]}
        with patch.object(client, "post", return_value=ok) as m:
            client.place_order("BTC-USDT", "cash", "buy", "market", "0.01")
            body = m.call_args[0][1]
            self.assertEqual(body["instId"], "BTC-USDT")
            self.assertEqual(body["side"], "buy")
            self.assertNotIn("reduceOnly", body)  # not set

    def test_place_order_with_tp_sl(self):
        """TP/SL now uses attachAlgoOrds array format (OKX API v5 requirement)."""
        client = self._client()
        ok = {"code": "0", "data": [{"ordId": "123", "sCode": "0", "sMsg": ""}]}
        with patch.object(client, "post", return_value=ok) as m:
            client.place_order("BTC-USDT-SWAP", "cross", "buy", "market", "1",
                               tp_trigger_px="55000", sl_trigger_px="45000")
            body = m.call_args[0][1]
            self.assertIn("attachAlgoOrds", body)
            algo = body["attachAlgoOrds"][0]
            self.assertEqual(algo["tpTriggerPx"], "55000")
            self.assertEqual(algo["slTriggerPx"], "45000")
            self.assertEqual(algo["tpOrdPx"], "-1")
            self.assertEqual(algo["slOrdPx"], "-1")
            self.assertEqual(algo["tpTriggerPxType"], "last")
            self.assertEqual(algo["slTriggerPxType"], "last")

    def test_place_order_reduce_only(self):
        client = self._client()
        ok = {"code": "0", "data": [{"ordId": "123", "sCode": "0", "sMsg": ""}]}
        with patch.object(client, "post", return_value=ok) as m:
            client.place_order("BTC-USDT-SWAP", "cross", "sell", "market", "1",
                               reduce_only=True)
            body = m.call_args[0][1]
            self.assertEqual(body["reduceOnly"], "true")

    def test_set_leverage_body(self):
        client = self._client()
        ok = {"code": "0", "data": []}
        with patch.object(client, "post", return_value=ok) as m:
            client.set_leverage("BTC-USDT-SWAP", 10, "cross")
            body = m.call_args[0][1]
            self.assertEqual(body["lever"], "10")
            self.assertEqual(body["mgnMode"], "cross")

    def test_transfer_body(self):
        client = self._client()
        ok = {"code": "0", "data": [{"transId": "abc"}]}
        with patch.object(client, "post", return_value=ok) as m:
            client.transfer("USDT", "100", "6", "18")
            body = m.call_args[0][1]
            self.assertEqual(body["ccy"], "USDT")
            self.assertEqual(body["amt"], "100")
            self.assertEqual(body["from"], "6")
            self.assertEqual(body["to"], "18")

    def test_balance_with_ccy(self):
        client = self._client()
        ok = {"code": "0", "data": []}
        with patch.object(client, "get", return_value=ok) as m:
            client.balance("USDT")
            params = m.call_args[0][1]
            self.assertEqual(params["ccy"], "USDT")

    def test_balance_no_ccy(self):
        client = self._client()
        ok = {"code": "0", "data": []}
        with patch.object(client, "get", return_value=ok) as m:
            client.balance()
            params = m.call_args[0][1]
            self.assertEqual(params, {})


if __name__ == "__main__":
    unittest.main()
