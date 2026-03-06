"""Unit tests for okx_ws_client.py and OKXClient WS/REST transparent switching."""
import sys, os, json, threading, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock, call
from collections import deque


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_feed():
    """Create a fresh OKXWebSocketFeed without starting the WS thread."""
    from okx_ws_client import OKXWebSocketFeed
    return OKXWebSocketFeed()


def _ticker_msg(inst_id: str, last: str = "67000") -> str:
    return json.dumps({
        "arg": {"channel": "tickers", "instId": inst_id},
        "data": [{"instId": inst_id, "last": last, "vol24h": "100"}],
    })


def _candle_msg(inst_id: str, bar: str = "1H", ts: str = "1700000000000",
                o="100", h="110", lo="90", c="105", vol="1000") -> str:
    return json.dumps({
        "arg": {"channel": f"candle{bar}", "instId": inst_id},
        "data": [[ts, o, h, lo, c, vol, "0", "0", "1"]],
    })


# ── Cache operations ──────────────────────────────────────────────────────────

class TestOKXWebSocketFeedCache(unittest.TestCase):

    def test_ticker_empty_initially(self):
        feed = _make_feed()
        self.assertIsNone(feed.get_ticker("BTC-USDT-SWAP"))

    def test_ticker_stored_after_update(self):
        feed = _make_feed()
        feed._update_ticker("BTC-USDT-SWAP", {"instId": "BTC-USDT-SWAP", "last": "67000"})
        result = feed.get_ticker("BTC-USDT-SWAP")
        self.assertIsNotNone(result)
        self.assertEqual(result["last"], "67000")

    def test_ticker_overwritten_on_update(self):
        feed = _make_feed()
        feed._update_ticker("BTC-USDT-SWAP", {"last": "67000"})
        feed._update_ticker("BTC-USDT-SWAP", {"last": "68000"})
        self.assertEqual(feed.get_ticker("BTC-USDT-SWAP")["last"], "68000")

    def test_ticker_isolated_per_inst(self):
        feed = _make_feed()
        feed._update_ticker("BTC-USDT-SWAP", {"last": "67000"})
        feed._update_ticker("ETH-USDT-SWAP", {"last": "2200"})
        self.assertEqual(feed.get_ticker("BTC-USDT-SWAP")["last"], "67000")
        self.assertEqual(feed.get_ticker("ETH-USDT-SWAP")["last"], "2200")

    def test_candles_empty_initially(self):
        feed = _make_feed()
        self.assertIsNone(feed.get_candles("BTC-USDT-SWAP", "1H"))

    def test_candle_stored_after_update(self):
        feed = _make_feed()
        feed._update_candle("BTC-USDT-SWAP", "1H", ["1700000000000", "100", "110", "90", "105", "1000"])
        result = feed.get_candles("BTC-USDT-SWAP", "1H")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][4], "105")  # close price

    def test_candle_new_timestamp_prepended(self):
        feed = _make_feed()
        feed._update_candle("BTC-USDT-SWAP", "1H", ["1000", "100", "110", "90", "105", "1000"])
        feed._update_candle("BTC-USDT-SWAP", "1H", ["2000", "106", "115", "100", "112", "900"])
        result = feed.get_candles("BTC-USDT-SWAP", "1H")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], "2000")   # newest first

    def test_candle_same_timestamp_updates_inplace(self):
        feed = _make_feed()
        feed._update_candle("BTC-USDT-SWAP", "1H", ["1000", "100", "110", "90", "105", "1000"])
        feed._update_candle("BTC-USDT-SWAP", "1H", ["1000", "100", "115", "90", "112", "1200"])
        result = feed.get_candles("BTC-USDT-SWAP", "1H")
        self.assertEqual(len(result), 1)          # not duplicated
        self.assertEqual(result[0][4], "112")     # updated close

    def test_candle_max_300_rows(self):
        feed = _make_feed()
        for i in range(350):
            feed._update_candle("BTC-USDT-SWAP", "1H", [str(i), "100", "110", "90", "105", "1000"])
        result = feed.get_candles("BTC-USDT-SWAP", "1H")
        self.assertLessEqual(len(result), 300)

    def test_candle_isolated_by_bar(self):
        feed = _make_feed()
        feed._update_candle("BTC-USDT-SWAP", "1H", ["1000", "100", "110", "90", "105", "1000"])
        feed._update_candle("BTC-USDT-SWAP", "4H", ["2000", "200", "220", "180", "210", "5000"])
        r1h = feed.get_candles("BTC-USDT-SWAP", "1H")
        r4h = feed.get_candles("BTC-USDT-SWAP", "4H")
        self.assertEqual(r1h[0][1], "100")
        self.assertEqual(r4h[0][1], "200")


# ── Message parsing ───────────────────────────────────────────────────────────

class TestOKXWebSocketFeedMessages(unittest.TestCase):

    def test_ticker_message_updates_cache(self):
        feed = _make_feed()
        feed._on_message(None, _ticker_msg("BTC-USDT-SWAP", "67500"))
        self.assertEqual(feed.get_ticker("BTC-USDT-SWAP")["last"], "67500")

    def test_candle_message_updates_cache(self):
        feed = _make_feed()
        feed._on_message(None, _candle_msg("SOL-USDT-SWAP", "1H", "1000", c="85"))
        result = feed.get_candles("SOL-USDT-SWAP", "1H")
        self.assertIsNotNone(result)
        self.assertEqual(result[0][4], "85")

    def test_pong_ignored(self):
        feed = _make_feed()
        feed._on_message(None, "pong")   # must not raise
        self.assertIsNone(feed.get_ticker("BTC-USDT-SWAP"))

    def test_invalid_json_ignored(self):
        feed = _make_feed()
        feed._on_message(None, "not-json{{{")   # must not raise

    def test_subscribe_event_ignored_gracefully(self):
        feed = _make_feed()
        msg = json.dumps({"event": "subscribe", "arg": {"channel": "tickers"}})
        feed._on_message(None, msg)   # must not raise

    def test_error_event_logged_gracefully(self):
        feed = _make_feed()
        msg = json.dumps({"event": "error", "code": "60012", "msg": "Invalid request"})
        feed._on_message(None, msg)   # must not raise

    def test_unknown_channel_ignored(self):
        feed = _make_feed()
        msg = json.dumps({"arg": {"channel": "funding-rate", "instId": "BTC-USDT-SWAP"},
                          "data": [{"fundingRate": "0.0001"}]})
        feed._on_message(None, msg)   # must not raise


# ── Subscription management ───────────────────────────────────────────────────

class TestOKXWebSocketFeedSubscriptions(unittest.TestCase):

    def test_subscribe_tickers_adds_to_list(self):
        feed = _make_feed()
        feed.subscribe_tickers(["BTC-USDT-SWAP", "ETH-USDT-SWAP"])
        channels = [s["channel"] for s in feed._subscriptions]
        self.assertEqual(channels.count("tickers"), 2)

    def test_subscribe_tickers_no_duplicate(self):
        feed = _make_feed()
        feed.subscribe_tickers(["BTC-USDT-SWAP"])
        feed.subscribe_tickers(["BTC-USDT-SWAP"])
        self.assertEqual(len(feed._subscriptions), 1)

    def test_subscribe_candles_correct_channel_name(self):
        feed = _make_feed()
        feed._simulated = False  # candle channel is disabled in simulated mode
        feed.subscribe_candles(["BTC-USDT-SWAP"], "4H")
        self.assertEqual(feed._subscriptions[0]["channel"], "candle4H")

    def test_subscribe_candles_no_duplicate(self):
        feed = _make_feed()
        feed._simulated = False
        feed.subscribe_candles(["BTC-USDT-SWAP"], "1H")
        feed.subscribe_candles(["BTC-USDT-SWAP"], "1H")
        self.assertEqual(len(feed._subscriptions), 1)

    def test_mixed_subscriptions_stored_separately(self):
        feed = _make_feed()
        feed._simulated = False
        feed.subscribe_tickers(["BTC-USDT-SWAP"])
        feed.subscribe_candles(["BTC-USDT-SWAP"], "1H")
        self.assertEqual(len(feed._subscriptions), 2)

    def test_subscribe_sends_to_ws_when_connected(self):
        feed = _make_feed()
        feed._connected.set()
        feed._ws = MagicMock()
        feed.subscribe_tickers(["BTC-USDT-SWAP"])
        feed._ws.send.assert_called_once()
        payload = json.loads(feed._ws.send.call_args[0][0])
        self.assertEqual(payload["op"], "subscribe")


# ── get_feed() singleton ──────────────────────────────────────────────────────

class TestGetFeed(unittest.TestCase):

    def test_returns_none_when_ows_disabled(self):
        import okx_ws_client
        with patch.dict(os.environ, {"OKX_WS": "0"}):
            # Force re-evaluation by patching the module env check
            with patch("okx_ws_client.os.getenv", return_value="0"):
                result = okx_ws_client.get_feed()
        self.assertIsNone(result)

    def test_returns_feed_when_enabled(self):
        import okx_ws_client
        mock_feed = MagicMock()
        mock_feed.start = MagicMock()
        with patch("okx_ws_client.os.getenv", return_value="1"), \
             patch("okx_ws_client.OKXWebSocketFeed", return_value=mock_feed), \
             patch.object(okx_ws_client, "_feed", None):
            result = okx_ws_client.get_feed()
        self.assertIsNotNone(result)

    def test_simulated_uses_sim_url(self):
        with patch.dict(os.environ, {"OKX_SIMULATED": "1"}):
            feed = _make_feed()
        from okx_ws_client import _WS_PUBLIC_SIM
        self.assertEqual(feed._url(), _WS_PUBLIC_SIM)

    def test_live_uses_live_url(self):
        with patch.dict(os.environ, {"OKX_SIMULATED": "0"}):
            feed = _make_feed()
        from okx_ws_client import _WS_PUBLIC
        self.assertEqual(feed._url(), _WS_PUBLIC)


# ── OKXClient transparent WS/REST switching ──────────────────────────────────

class TestOKXClientWSIntegration(unittest.TestCase):

    def _rest_ticker_response(self, inst_id: str, last: str) -> dict:
        return {"code": "0", "data": [{"instId": inst_id, "last": last}]}

    def _rest_candles_response(self, rows: list) -> dict:
        return {"code": "0", "data": rows}

    def test_ticker_uses_ws_cache_when_available(self):
        mock_feed = MagicMock()
        mock_feed.get_ticker.return_value = {"instId": "BTC-USDT-SWAP", "last": "99999"}
        with patch("okx_client.get_feed", return_value=mock_feed), \
             patch("okx_client._load_env"), \
             patch("okx_client._sync_time"):
            from okx_client import OKXClient
            client = OKXClient()
            with patch.object(client, "get") as mock_get:
                result = client.ticker("BTC-USDT-SWAP")
        mock_get.assert_not_called()          # REST not called
        self.assertEqual(result["data"][0]["last"], "99999")

    def test_ticker_falls_back_to_rest_when_cache_empty(self):
        mock_feed = MagicMock()
        mock_feed.get_ticker.return_value = None   # cache miss
        with patch("okx_client.get_feed", return_value=mock_feed), \
             patch("okx_client._load_env"), \
             patch("okx_client._sync_time"):
            from okx_client import OKXClient
            client = OKXClient()
            with patch.object(client, "get", return_value=self._rest_ticker_response("BTC-USDT-SWAP", "67000")) as mock_get:
                result = client.ticker("BTC-USDT-SWAP")
        mock_get.assert_called_once()         # REST fallback used
        self.assertEqual(result["data"][0]["last"], "67000")

    def test_ticker_uses_rest_when_ws_disabled(self):
        with patch("okx_client.get_feed", return_value=None), \
             patch("okx_client._load_env"), \
             patch("okx_client._sync_time"):
            from okx_client import OKXClient
            client = OKXClient()
            with patch.object(client, "get", return_value=self._rest_ticker_response("BTC-USDT-SWAP", "67000")) as mock_get:
                result = client.ticker("BTC-USDT-SWAP")
        mock_get.assert_called_once()
        self.assertEqual(result["data"][0]["last"], "67000")

    def test_candles_uses_ws_cache_when_sufficient(self):
        rows = [[str(i), "100", "110", "90", "105", "1000"] for i in range(100)]
        mock_feed = MagicMock()
        mock_feed.get_candles.return_value = rows
        with patch("okx_client.get_feed", return_value=mock_feed), \
             patch("okx_client._load_env"), \
             patch("okx_client._sync_time"):
            from okx_client import OKXClient
            client = OKXClient()
            with patch.object(client, "get") as mock_get:
                result = client.candles("BTC-USDT-SWAP", "1H", 50)
        mock_get.assert_not_called()
        self.assertEqual(len(result["data"]), 50)

    def test_candles_falls_back_to_rest_when_cache_insufficient(self):
        rows = [[str(i), "100", "110", "90", "105", "1000"] for i in range(10)]  # only 10
        mock_feed = MagicMock()
        mock_feed.get_candles.return_value = rows
        with patch("okx_client.get_feed", return_value=mock_feed), \
             patch("okx_client._load_env"), \
             patch("okx_client._sync_time"):
            from okx_client import OKXClient
            client = OKXClient()
            with patch.object(client, "get", return_value=self._rest_candles_response(rows)) as mock_get:
                result = client.candles("BTC-USDT-SWAP", "1H", 100)  # need 100
        mock_get.assert_called_once()         # not enough cached → REST

    def test_candles_uses_rest_when_ws_disabled(self):
        rows = [[str(i), "100", "110", "90", "105", "1000"] for i in range(100)]
        with patch("okx_client.get_feed", return_value=None), \
             patch("okx_client._load_env"), \
             patch("okx_client._sync_time"):
            from okx_client import OKXClient
            client = OKXClient()
            with patch.object(client, "get", return_value=self._rest_candles_response(rows)) as mock_get:
                result = client.candles("BTC-USDT-SWAP", "1H", 100)
        mock_get.assert_called_once()


# ── Thread safety ─────────────────────────────────────────────────────────────

class TestOKXWebSocketFeedThreadSafety(unittest.TestCase):

    def test_concurrent_ticker_writes_do_not_corrupt(self):
        feed = _make_feed()
        errors = []

        def writer(inst_id, price):
            try:
                for _ in range(200):
                    feed._update_ticker(inst_id, {"last": str(price)})
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(f"COIN{i}-USDT-SWAP", i * 1000))
                   for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        for i in range(5):
            t = feed.get_ticker(f"COIN{i}-USDT-SWAP")
            self.assertIsNotNone(t)

    def test_concurrent_candle_writes_do_not_corrupt(self):
        feed = _make_feed()
        errors = []

        def writer(ts_offset):
            try:
                for i in range(100):
                    feed._update_candle("BTC-USDT-SWAP", "1H",
                                        [str(ts_offset + i), "100", "110", "90", "105", "1000"])
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(i * 10000,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        result = feed.get_candles("BTC-USDT-SWAP", "1H")
        self.assertIsNotNone(result)

    def test_concurrent_read_write_do_not_deadlock(self):
        feed = _make_feed()
        stop = threading.Event()

        def writer():
            i = 0
            while not stop.is_set():
                feed._update_ticker("BTC-USDT-SWAP", {"last": str(i)})
                i += 1

        def reader():
            count = 0
            while not stop.is_set() and count < 500:
                feed.get_ticker("BTC-USDT-SWAP")
                count += 1

        wt = threading.Thread(target=writer)
        rt = threading.Thread(target=reader)
        wt.start()
        rt.start()
        rt.join(timeout=3)
        stop.set()
        wt.join(timeout=1)
        self.assertFalse(rt.is_alive(), "Reader thread hung — possible deadlock")


if __name__ == "__main__":
    unittest.main()
