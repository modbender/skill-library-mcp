"""Unit tests for position_risk() and check_liquidation_risk()."""
import sys, os
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


def _risk_response(positions: list) -> dict:
    """Build a mock /api/v5/account/position-risk response."""
    return {"code": "0", "data": [{"posData": positions}]}


# ── OKXClient.position_risk() ──────────────────────────────────────────────────

class TestPositionRiskAPI(unittest.TestCase):

    def test_position_risk_no_params(self):
        client = _client()
        ok = _risk_response([])
        with patch.object(client, "get", return_value=ok) as m:
            client.position_risk()
            m.assert_called_once_with("/api/v5/account/position-risk", {})

    def test_position_risk_with_inst_type(self):
        client = _client()
        ok = _risk_response([])
        with patch.object(client, "get", return_value=ok) as m:
            client.position_risk("SWAP")
            m.assert_called_once_with("/api/v5/account/position-risk", {"instType": "SWAP"})

    def test_position_risk_returns_response(self):
        client = _client()
        pos = {"instId": "BTC-USDT-SWAP", "liqPx": "40000", "markPx": "50000"}
        ok = _risk_response([pos])
        with patch.object(client, "get", return_value=ok):
            result = client.position_risk()
        self.assertEqual(result["code"], "0")
        self.assertEqual(result["data"][0]["posData"][0]["instId"], "BTC-USDT-SWAP")


# ── check_liquidation_risk() ───────────────────────────────────────────────────

class TestCheckLiquidationRisk(unittest.TestCase):

    def _run(self, positions: list, threshold: float = 10.0):
        import monitor
        mock_client = MagicMock()
        mock_client.position_risk.return_value = _risk_response(positions)
        with patch("monitor.OKXClient", return_value=mock_client):
            return monitor.check_liquidation_risk(threshold)

    def test_no_positions_returns_empty(self):
        result = self._run([])
        self.assertEqual(result, [])

    def test_position_safe_distance_no_alert(self):
        # mark=50000, liq=40000 → distance = 20% (> 10% threshold)
        result = self._run([{
            "instId": "BTC-USDT-SWAP", "posSide": "long",
            "markPx": "50000", "liqPx": "40000",
        }])
        self.assertEqual(result, [])

    def test_position_near_liquidation_triggers_alert(self):
        # mark=50000, liq=46000 → distance = 8% (< 10% threshold)
        result = self._run([{
            "instId": "BTC-USDT-SWAP", "posSide": "long",
            "markPx": "50000", "liqPx": "46000",
        }])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["inst_id"], "BTC-USDT-SWAP")
        self.assertAlmostEqual(result[0]["distance_pct"], 8.0, places=1)

    def test_custom_threshold_respected(self):
        # mark=50000, liq=47000 → distance = 6%
        result_strict = self._run([{
            "instId": "BTC-USDT-SWAP", "posSide": "long",
            "markPx": "50000", "liqPx": "47000",
        }], threshold=5.0)  # 6% > 5% → no alert
        self.assertEqual(result_strict, [])

        result_loose = self._run([{
            "instId": "BTC-USDT-SWAP", "posSide": "long",
            "markPx": "50000", "liqPx": "47000",
        }], threshold=10.0)  # 6% < 10% → alert
        self.assertEqual(len(result_loose), 1)

    def test_missing_liq_px_skipped(self):
        result = self._run([{
            "instId": "BTC-USDT-SWAP", "posSide": "long",
            "markPx": "50000", "liqPx": "",
        }])
        self.assertEqual(result, [])

    def test_zero_liq_px_skipped(self):
        """liqPx='0' means no liquidation risk (e.g., no leverage)."""
        result = self._run([{
            "instId": "BTC-USDT-SWAP", "posSide": "long",
            "markPx": "50000", "liqPx": "0",
        }])
        self.assertEqual(result, [])

    def test_invalid_float_skipped(self):
        result = self._run([{
            "instId": "BTC-USDT-SWAP", "posSide": "long",
            "markPx": "NaN", "liqPx": "40000",
        }])
        self.assertEqual(result, [])

    def test_multiple_positions_independent_alerts(self):
        positions = [
            {"instId": "BTC-USDT-SWAP", "posSide": "long", "markPx": "50000", "liqPx": "46000"},  # 8% → alert
            {"instId": "ETH-USDT-SWAP", "posSide": "long", "markPx": "3000", "liqPx": "2500"},    # 16.7% → safe
        ]
        result = self._run(positions)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["inst_id"], "BTC-USDT-SWAP")

    def test_api_error_returns_early(self):
        import monitor
        mock_client = MagicMock()
        mock_client.position_risk.return_value = {"code": "50001", "msg": "Service unavailable"}
        with patch("monitor.OKXClient", return_value=mock_client):
            # Should not raise; returns None (logs error and returns)
            monitor.check_liquidation_risk()

    def test_short_position_distance_computed_correctly(self):
        """For a short position, liqPx > markPx; distance still uses abs()."""
        # short: mark=50000, liq=53000 → distance = 6% → alert at 10% threshold
        result = self._run([{
            "instId": "BTC-USDT-SWAP", "posSide": "short",
            "markPx": "50000", "liqPx": "53000",
        }])
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0]["distance_pct"], 6.0, places=1)


# ── check_stop_loss_take_profit() ─────────────────────────────────────────────

class TestCheckStopLossTakeProfit(unittest.TestCase):

    def _prefs(self, **kw):
        from config import DEFAULT_PREFS
        return {**DEFAULT_PREFS, **kw}

    def _pos(self, inst_id="BTC-USDT-SWAP", side="long", upl_ratio=0.0, sz="0.01"):
        return {"instId": inst_id, "posSide": side,
                "uplRatio": str(upl_ratio / 100), "pos": sz}

    def _run(self, positions, prefs=None, auto_trade=False, daily_trades=0):
        import monitor
        from datetime import datetime
        mock_client = MagicMock()
        mock_client.positions.return_value = {"code": "0", "data": positions}
        mock_client.place_order.return_value = {
            "code": "0", "data": [{"ordId": "ord123"}]
        }
        p = prefs or self._prefs(auto_trade=auto_trade)
        # Use today's date so the daily-reset branch is NOT triggered
        today = datetime.utcnow().strftime("%Y-%m-%d")
        state = {"daily_trades": daily_trades, "last_reset": today}
        with patch("monitor.OKXClient", return_value=mock_client), \
             patch("monitor.load_prefs", return_value=p), \
             patch("monitor.load_state", return_value=state), \
             patch("monitor.save_state"), \
             patch("monitor.log_trade"), \
             patch("monitor.record_trade"), \
             patch("monitor._ws_warmup"):
            monitor.check_stop_loss_take_profit()
        return mock_client, state

    def test_no_positions_no_action(self):
        client, _ = self._run([])
        client.place_order.assert_not_called()

    def test_api_error_returns_early(self):
        import monitor
        mock_client = MagicMock()
        mock_client.positions.return_value = {"code": "50001", "msg": "Error"}
        with patch("monitor.OKXClient", return_value=mock_client), \
             patch("monitor.load_prefs", return_value=self._prefs()), \
             patch("monitor.load_state", return_value={"daily_trades": 0}), \
             patch("monitor.save_state"), \
             patch("monitor._ws_warmup"):
            monitor.check_stop_loss_take_profit()
        mock_client.place_order.assert_not_called()

    def test_sl_triggered_logs_stop_loss(self):
        # stop_loss_pct=5.0 → upl_ratio=-6% triggers SL
        client, _ = self._run([self._pos(upl_ratio=-6.0)],
                              prefs=self._prefs(stop_loss_pct=5.0, auto_trade=False))
        client.place_order.assert_not_called()  # auto_trade=False

    def test_tp_triggered_logs_take_profit(self):
        # take_profit_pct=10.0 → upl_ratio=12% triggers TP
        client, _ = self._run([self._pos(upl_ratio=12.0)],
                              prefs=self._prefs(take_profit_pct=10.0, auto_trade=False))
        client.place_order.assert_not_called()  # auto_trade=False

    def test_within_threshold_no_action(self):
        # upl_ratio=-2% < stop_loss 5% → no trigger
        client, _ = self._run([self._pos(upl_ratio=-2.0)])
        client.place_order.assert_not_called()

    def test_auto_trade_true_places_order_on_sl(self):
        client, state = self._run(
            [self._pos(upl_ratio=-6.0)],
            prefs=self._prefs(stop_loss_pct=5.0, auto_trade=True, max_daily_trades=10),
        )
        client.place_order.assert_called_once()
        self.assertEqual(state["daily_trades"], 1)

    def test_auto_trade_true_places_order_on_tp(self):
        client, state = self._run(
            [self._pos(upl_ratio=12.0)],
            prefs=self._prefs(take_profit_pct=10.0, auto_trade=True, max_daily_trades=10),
        )
        client.place_order.assert_called_once()
        self.assertEqual(state["daily_trades"], 1)

    def test_daily_limit_prevents_order(self):
        # daily_trades already at max
        client, _ = self._run(
            [self._pos(upl_ratio=-6.0)],
            prefs=self._prefs(stop_loss_pct=5.0, auto_trade=True, max_daily_trades=3),
            daily_trades=3,
        )
        client.place_order.assert_not_called()

    def test_short_position_close_side_is_buy(self):
        client, _ = self._run(
            [self._pos(side="short", upl_ratio=-6.0)],
            prefs=self._prefs(stop_loss_pct=5.0, auto_trade=True, max_daily_trades=10),
        )
        call_kwargs = client.place_order.call_args[1]
        self.assertEqual(call_kwargs["side"], "buy")

    def test_long_position_close_side_is_sell(self):
        client, _ = self._run(
            [self._pos(side="long", upl_ratio=-6.0)],
            prefs=self._prefs(stop_loss_pct=5.0, auto_trade=True, max_daily_trades=10),
        )
        call_kwargs = client.place_order.call_args[1]
        self.assertEqual(call_kwargs["side"], "sell")


# ── scan_opportunities() ──────────────────────────────────────────────────────

class TestScanOpportunities(unittest.TestCase):

    def _prefs(self, **kw):
        from config import DEFAULT_PREFS
        return {**DEFAULT_PREFS, "watchlist": ["BTC-USDT-SWAP"], **kw}

    def _trend(self, signal="hold", price=66000.0, regime="bull"):
        return {"signal": signal, "current_price": price,
                "rsi": 50, "macd_histogram": 0.1, "market_regime": regime}

    def _run(self, signal="hold", auto_trade=False, daily_trades=0,
             should_avoid=False, strategies=None):
        import monitor
        from datetime import datetime
        today = datetime.utcnow().strftime("%Y-%m-%d")
        prefs = self._prefs(auto_trade=auto_trade,
                            strategies=strategies or ["trend"])
        state = {"daily_trades": daily_trades, "last_reset": today,
                 "last_scan": ""}
        mock_analyze = MagicMock(return_value=self._trend(signal))
        mock_place = MagicMock()
        with patch("monitor.load_prefs", return_value=prefs), \
             patch("monitor.load_state", return_value=state), \
             patch("monitor.save_state"), \
             patch("monitor.log_trade"), \
             patch("monitor.record_trade"), \
             patch("monitor.should_avoid_trade", return_value=(should_avoid, "reason")), \
             patch("monitor._ws_warmup"), \
             patch("strategies.trend.analyze", mock_analyze), \
             patch("execute.place_order", mock_place):
            monitor.scan_opportunities()
        return mock_place, state

    def test_hold_signal_no_order(self):
        place, _ = self._run(signal="hold", auto_trade=True)
        place.assert_not_called()

    def test_buy_signal_auto_trade_places_order(self):
        place, _ = self._run(signal="buy", auto_trade=True)
        place.assert_called_once()
        args = place.call_args[0]
        self.assertEqual(args[1], "buy")

    def test_sell_signal_auto_trade_places_order(self):
        place, _ = self._run(signal="sell", auto_trade=True)
        place.assert_called_once()
        args = place.call_args[0]
        self.assertEqual(args[1], "sell")

    def test_buy_signal_auto_trade_false_no_order(self):
        place, _ = self._run(signal="buy", auto_trade=False)
        place.assert_not_called()

    def test_daily_limit_prevents_order(self):
        place, _ = self._run(signal="buy", auto_trade=True, daily_trades=10)
        place.assert_not_called()

    def test_learning_avoid_prevents_order(self):
        place, _ = self._run(signal="buy", auto_trade=True, should_avoid=True)
        place.assert_not_called()

    def test_daily_trades_incremented(self):
        _, state = self._run(signal="buy", auto_trade=True, daily_trades=0)
        self.assertEqual(state["daily_trades"], 1)

    def test_last_scan_updated(self):
        _, state = self._run()
        self.assertNotEqual(state["last_scan"], "")

    def test_buy_tp_above_entry_sl_below(self):
        """For a BUY signal: TP > entry price, SL < entry price."""
        import monitor
        from datetime import datetime
        price = 66000.0
        today = datetime.utcnow().strftime("%Y-%m-%d")
        prefs = self._prefs(auto_trade=True, take_profit_pct=10.0,
                            stop_loss_pct=5.0, default_sz="0.01")
        state = {"daily_trades": 0, "last_reset": today, "last_scan": ""}
        captured = {}
        def fake_place(inst_id, side, ord_type, sz, td_mode, **kw):
            captured.update(kw)
        with patch("monitor.load_prefs", return_value=prefs), \
             patch("monitor.load_state", return_value=state), \
             patch("monitor.save_state"), \
             patch("monitor.log_trade"), patch("monitor.record_trade"), \
             patch("monitor.should_avoid_trade", return_value=(False, "")), \
             patch("monitor._ws_warmup"), \
             patch("strategies.trend.analyze",
                   return_value=self._trend("buy", price)), \
             patch("execute.place_order", side_effect=fake_place):
            monitor.scan_opportunities()
        self.assertGreater(float(captured["tp"]), price)
        self.assertLess(float(captured["sl"]), price)

    def test_sell_tp_below_entry_sl_above(self):
        """For a SELL signal: TP < entry price, SL > entry price."""
        import monitor
        from datetime import datetime
        price = 66000.0
        today = datetime.utcnow().strftime("%Y-%m-%d")
        prefs = self._prefs(auto_trade=True, take_profit_pct=10.0,
                            stop_loss_pct=5.0, default_sz="0.01")
        state = {"daily_trades": 0, "last_reset": today, "last_scan": ""}
        captured = {}
        def fake_place(inst_id, side, ord_type, sz, td_mode, **kw):
            captured.update(kw)
        with patch("monitor.load_prefs", return_value=prefs), \
             patch("monitor.load_state", return_value=state), \
             patch("monitor.save_state"), \
             patch("monitor.log_trade"), patch("monitor.record_trade"), \
             patch("monitor.should_avoid_trade", return_value=(False, "")), \
             patch("monitor._ws_warmup"), \
             patch("strategies.trend.analyze",
                   return_value=self._trend("sell", price)), \
             patch("execute.place_order", side_effect=fake_place):
            monitor.scan_opportunities()
        self.assertLess(float(captured["tp"]), price)
        self.assertGreater(float(captured["sl"]), price)


if __name__ == "__main__":
    unittest.main()
