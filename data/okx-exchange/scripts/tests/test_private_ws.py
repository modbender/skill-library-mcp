"""Unit tests for OKXPrivateWebSocketFeed."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import threading
from unittest.mock import patch, MagicMock


def _make_private_feed(**kwargs):
    from okx_ws_client import OKXPrivateWebSocketFeed
    return OKXPrivateWebSocketFeed(
        api_key=kwargs.get("api_key", "key"),
        secret=kwargs.get("secret", "secret"),
        passphrase=kwargs.get("passphrase", "pass"),
        simulated=kwargs.get("simulated", False),
    )


# ── Login payload ──────────────────────────────────────────────────────────────

class TestPrivateWSLoginPayload(unittest.TestCase):

    def test_login_payload_structure(self):
        feed = _make_private_feed()
        payload = feed._login_payload()
        self.assertEqual(payload["op"], "login")
        self.assertEqual(len(payload["args"]), 1)
        arg = payload["args"][0]
        self.assertEqual(arg["apiKey"], "key")
        self.assertEqual(arg["passphrase"], "pass")
        self.assertIn("timestamp", arg)
        self.assertIn("sign", arg)

    def test_login_timestamp_is_unix_seconds(self):
        """OKX private WS requires Unix seconds (not milliseconds)."""
        import time
        feed = _make_private_feed()
        payload = feed._login_payload()
        ts = int(payload["args"][0]["timestamp"])
        now = int(time.time())
        self.assertAlmostEqual(ts, now, delta=5)

    def test_login_sign_is_base64(self):
        import base64
        feed = _make_private_feed()
        payload = feed._login_payload()
        sign = payload["args"][0]["sign"]
        # Should decode without error
        decoded = base64.b64decode(sign)
        self.assertEqual(len(decoded), 32)  # SHA-256 = 32 bytes

    def test_login_sign_uses_get_path(self):
        """Sign must be HMAC-SHA256 of ts+"GET"+"/users/self/verify"."""
        import hmac, hashlib, base64, time
        feed = _make_private_feed(secret="test_secret")
        payload = feed._login_payload()
        ts = payload["args"][0]["timestamp"]
        msg = ts + "GET" + "/users/self/verify"
        expected = base64.b64encode(
            hmac.new("test_secret".encode(), msg.encode(), hashlib.sha256).digest()
        ).decode()
        self.assertEqual(payload["args"][0]["sign"], expected)


# ── URL selection ──────────────────────────────────────────────────────────────

class TestPrivateWSUrl(unittest.TestCase):

    def test_live_uses_live_url(self):
        from okx_ws_client import _WS_PRIVATE
        feed = _make_private_feed(simulated=False)
        self.assertEqual(feed._url(), _WS_PRIVATE)

    def test_simulated_uses_sim_url(self):
        from okx_ws_client import _WS_PRIVATE_SIM
        feed = _make_private_feed(simulated=True)
        self.assertEqual(feed._url(), _WS_PRIVATE_SIM)


# ── Message handling ───────────────────────────────────────────────────────────

class TestPrivateWSMessages(unittest.TestCase):

    def _login_success_msg(self) -> str:
        return json.dumps({"event": "login", "code": "0", "msg": ""})

    def _login_fail_msg(self) -> str:
        return json.dumps({"event": "login", "code": "60009", "msg": "Login failed"})

    def _account_msg(self, details: list) -> str:
        return json.dumps({
            "arg": {"channel": "account"},
            "data": [{"details": details}],
        })

    def _position_msg(self, positions: list) -> str:
        return json.dumps({
            "arg": {"channel": "positions"},
            "data": positions,
        })

    def _order_msg(self, orders: list) -> str:
        return json.dumps({
            "arg": {"channel": "orders"},
            "data": orders,
        })

    def test_login_success_sets_logged_in_event(self):
        feed = _make_private_feed()
        mock_ws = MagicMock()
        feed._ws = mock_ws
        feed._on_message(None, self._login_success_msg())
        self.assertTrue(feed._logged_in.is_set())

    def test_login_success_subscribes_to_channels(self):
        feed = _make_private_feed()
        mock_ws = MagicMock()
        feed._ws = mock_ws
        feed._on_message(None, self._login_success_msg())
        mock_ws.send.assert_called_once()
        payload = json.loads(mock_ws.send.call_args[0][0])
        channels = [a["channel"] for a in payload["args"]]
        self.assertIn("account", channels)
        self.assertIn("positions", channels)
        self.assertIn("orders", channels)

    def test_login_failure_does_not_set_logged_in(self):
        feed = _make_private_feed()
        feed._on_message(None, self._login_fail_msg())
        self.assertFalse(feed._logged_in.is_set())

    def test_account_update_stores_by_ccy(self):
        feed = _make_private_feed()
        msg = self._account_msg([
            {"ccy": "USDT", "cashBal": "1000"},
            {"ccy": "BTC", "cashBal": "0.5"},
        ])
        feed._on_message(None, msg)
        account = feed.get_account()
        self.assertIn("USDT", account)
        self.assertIn("BTC", account)
        self.assertEqual(account["USDT"]["cashBal"], "1000")

    def test_account_update_overwrites_existing_ccy(self):
        feed = _make_private_feed()
        feed._on_message(None, self._account_msg([{"ccy": "USDT", "cashBal": "1000"}]))
        feed._on_message(None, self._account_msg([{"ccy": "USDT", "cashBal": "2000"}]))
        self.assertEqual(feed.get_account()["USDT"]["cashBal"], "2000")

    def test_position_update_stores_by_inst_and_side(self):
        feed = _make_private_feed()
        msg = self._position_msg([
            {"instId": "BTC-USDT-SWAP", "posSide": "long", "pos": "1", "uplRatio": "0.05"},
        ])
        feed._on_message(None, msg)
        positions = feed.get_positions()
        self.assertIn("BTC-USDT-SWAP:long", positions)

    def test_position_with_zero_pos_removes_entry(self):
        """A position update with pos='0' means the position is closed."""
        feed = _make_private_feed()
        feed._on_message(None, self._position_msg([
            {"instId": "BTC-USDT-SWAP", "posSide": "long", "pos": "1"},
        ]))
        feed._on_message(None, self._position_msg([
            {"instId": "BTC-USDT-SWAP", "posSide": "long", "pos": "0"},
        ]))
        self.assertNotIn("BTC-USDT-SWAP:long", feed.get_positions())

    def test_order_update_stores_by_ord_id(self):
        feed = _make_private_feed()
        feed._on_message(None, self._order_msg([
            {"ordId": "123", "instId": "BTC-USDT-SWAP", "state": "filled"},
        ]))
        orders = feed.get_orders()
        self.assertIn("123", orders)
        self.assertEqual(orders["123"]["state"], "filled")

    def test_order_cache_capped_at_50(self):
        feed = _make_private_feed()
        for i in range(60):
            feed._update_order({"ordId": str(i), "state": "filled"})
        self.assertLessEqual(len(feed.get_orders()), 50)

    def test_pong_ignored(self):
        feed = _make_private_feed()
        feed._on_message(None, "pong")  # must not raise

    def test_invalid_json_ignored(self):
        feed = _make_private_feed()
        feed._on_message(None, "not-json{{{{")  # must not raise

    def test_on_close_clears_logged_in(self):
        feed = _make_private_feed()
        feed._logged_in.set()
        feed._on_close(None, None, None)
        self.assertFalse(feed._logged_in.is_set())


# ── get_private_feed() singleton ──────────────────────────────────────────────

class TestGetPrivateFeed(unittest.TestCase):

    def test_returns_none_when_ws_disabled(self):
        import okx_ws_client
        with patch("okx_ws_client.os.getenv", return_value="0"):
            result = okx_ws_client.get_private_feed()
        self.assertIsNone(result)

    def test_returns_none_when_no_api_key(self):
        import okx_ws_client
        with patch.dict(os.environ, {"OKX_WS": "1", "OKX_API_KEY": ""}), \
             patch("okx_ws_client.os.getenv", side_effect=lambda k, d="": "1" if k == "OKX_WS" else ""), \
             patch.object(okx_ws_client, "_private_feed", None):
            result = okx_ws_client.get_private_feed()
        self.assertIsNone(result)


# ── OKXClient private WS integration ──────────────────────────────────────────

class TestOKXClientPrivateFeedIntegration(unittest.TestCase):

    def _client(self):
        with patch("okx_client._sync_time"), patch("okx_client._load_env"):
            from okx_client import OKXClient
            with patch.dict(os.environ, {
                "OKX_API_KEY": "key", "OKX_SECRET_KEY": "secret",
                "OKX_PASSPHRASE": "pass", "OKX_SIMULATED": "1",
            }):
                return OKXClient()

    def test_balance_uses_private_feed_cache(self):
        mock_pfeed = MagicMock()
        mock_pfeed.get_account.return_value = {"USDT": {"ccy": "USDT", "cashBal": "5000"}}
        with patch("okx_client.get_private_feed", return_value=mock_pfeed):
            client = self._client()
            with patch.object(client, "get") as mock_get:
                result = client.balance()
        mock_get.assert_not_called()
        self.assertEqual(result["code"], "0")
        self.assertEqual(result["data"][0]["details"][0]["ccy"], "USDT")

    def test_balance_filters_by_ccy(self):
        mock_pfeed = MagicMock()
        mock_pfeed.get_account.return_value = {
            "USDT": {"ccy": "USDT", "cashBal": "5000"},
            "BTC": {"ccy": "BTC", "cashBal": "0.5"},
        }
        with patch("okx_client.get_private_feed", return_value=mock_pfeed):
            client = self._client()
            result = client.balance("USDT")
        details = result["data"][0]["details"]
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0]["ccy"], "USDT")

    def test_balance_falls_back_to_rest_when_cache_empty(self):
        mock_pfeed = MagicMock()
        mock_pfeed.get_account.return_value = {}  # empty cache
        with patch("okx_client.get_private_feed", return_value=mock_pfeed):
            client = self._client()
            rest_response = {"code": "0", "data": [{"details": []}]}
            with patch.object(client, "get", return_value=rest_response) as mock_get:
                result = client.balance()
        mock_get.assert_called_once()

    def test_positions_uses_private_feed_cache(self):
        mock_pfeed = MagicMock()
        mock_pfeed.get_positions.return_value = {
            "BTC-USDT-SWAP:long": {"instId": "BTC-USDT-SWAP", "posSide": "long", "pos": "1"},
        }
        with patch("okx_client.get_private_feed", return_value=mock_pfeed):
            client = self._client()
            with patch.object(client, "get") as mock_get:
                result = client.positions()
        mock_get.assert_not_called()
        self.assertEqual(len(result["data"]), 1)

    def test_positions_filters_by_inst_id(self):
        mock_pfeed = MagicMock()
        mock_pfeed.get_positions.return_value = {
            "BTC-USDT-SWAP:long": {"instId": "BTC-USDT-SWAP", "posSide": "long"},
            "ETH-USDT-SWAP:long": {"instId": "ETH-USDT-SWAP", "posSide": "long"},
        }
        with patch("okx_client.get_private_feed", return_value=mock_pfeed):
            client = self._client()
            result = client.positions(inst_id="BTC-USDT-SWAP")
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["instId"], "BTC-USDT-SWAP")

    def test_positions_falls_back_to_rest_when_cache_empty(self):
        mock_pfeed = MagicMock()
        mock_pfeed.get_positions.return_value = {}
        with patch("okx_client.get_private_feed", return_value=mock_pfeed):
            client = self._client()
            rest_response = {"code": "0", "data": []}
            with patch.object(client, "get", return_value=rest_response) as mock_get:
                result = client.positions()
        mock_get.assert_called_once()


# ── Thread safety ──────────────────────────────────────────────────────────────

class TestPrivateWSThreadSafety(unittest.TestCase):

    def test_concurrent_account_updates_no_corruption(self):
        feed = _make_private_feed()
        errors = []

        def updater(ccy, bal):
            try:
                for _ in range(200):
                    feed._update_account({"details": [{"ccy": ccy, "cashBal": str(bal)}]})
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=updater, args=(f"CCY{i}", i * 1000))
            for i in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        for i in range(5):
            self.assertIn(f"CCY{i}", feed.get_account())

    def test_concurrent_position_updates_no_corruption(self):
        feed = _make_private_feed()
        errors = []

        def updater(n):
            try:
                for i in range(100):
                    feed._update_position({
                        "instId": f"COIN{n}-USDT-SWAP",
                        "posSide": "long",
                        "pos": str(i % 5),
                    })
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=updater, args=(i,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
