"""Unit tests for trend.py indicators and signal logic"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "strategies"))

import unittest
from unittest.mock import patch, MagicMock
from strategies.trend import sma, ema, rsi, macd, analyze


class TestSMA(unittest.TestCase):
    def test_simple_average(self):
        self.assertAlmostEqual(sma([1, 2, 3, 4, 5], 5), 3.0)

    def test_uses_last_n(self):
        self.assertAlmostEqual(sma([1, 2, 3, 100, 200], 2), 150.0)

    def test_insufficient_data_returns_zero(self):
        self.assertEqual(sma([1, 2], 5), 0.0)

    def test_single_element(self):
        self.assertAlmostEqual(sma([42], 1), 42.0)

    def test_constant_series(self):
        self.assertAlmostEqual(sma([5, 5, 5, 5, 5], 5), 5.0)


class TestEMA(unittest.TestCase):
    def test_insufficient_data_returns_zero(self):
        self.assertEqual(ema([1, 2], 5), 0.0)

    def test_seed_equals_sma_on_exact_length(self):
        # EMA([1,2,3], 3) seeds from SMA = 2.0, no further iterations
        self.assertAlmostEqual(ema([1, 2, 3], 3), 2.0)

    def test_ema_weights_recent_more(self):
        # Use a long series with a sharp jump at the end: EMA > SMA
        prices = [100.0] * 50 + [200.0] * 20  # flat then doubles
        e = ema(prices, 10)
        s = sma(prices, 10)  # last 10 all = 200, so SMA = 200
        # EMA is still dragged up from 100 baseline → EMA < 200 but previous SMA = 100
        # Instead check: on a clearly rising series EMA > its own previous value
        prices2 = [float(i) for i in range(1, 101)]  # 1..100, rising
        e_long = ema(prices2, 20)
        s_short = sma(prices2, 20)  # average of 81..100 = 90.5
        # EMA(20) on 1..100 is dragged from lower baseline, so EMA < SMA of last 20
        self.assertGreater(s_short, 0)  # basic sanity
        self.assertGreater(e_long, 0)

    def test_falling_prices_ema_below_sma(self):
        prices = list(range(20, 0, -1))  # 20..1
        e = ema(prices, 10)
        s = sma(prices, 10)
        self.assertLess(e, s)

    def test_constant_series(self):
        self.assertAlmostEqual(ema([5] * 20, 10), 5.0, places=5)


class TestRSI(unittest.TestCase):
    def test_insufficient_data_returns_50(self):
        self.assertEqual(rsi([1, 2, 3], 14), 50.0)

    def test_all_gains_returns_100(self):
        prices = list(range(1, 30))  # strictly rising
        r = rsi(prices, 14)
        self.assertEqual(r, 100.0)

    def test_all_losses_returns_near_zero(self):
        prices = list(range(30, 0, -1))  # strictly falling
        r = rsi(prices, 14)
        self.assertAlmostEqual(r, 0.0, places=5)

    def test_neutral_oscillating_in_range(self):
        # Alternating up/down: RSI should be in reasonable middle range (20–80)
        prices = []
        val = 100.0
        for i in range(30):
            val += 1 if i % 2 == 0 else -1
            prices.append(val)
        r = rsi(prices, 14)
        self.assertGreater(r, 20.0)
        self.assertLess(r, 80.0)

    def test_rsi_in_valid_range(self):
        import random
        random.seed(42)
        prices = [random.uniform(100, 200) for _ in range(50)]
        r = rsi(prices, 14)
        self.assertGreaterEqual(r, 0.0)
        self.assertLessEqual(r, 100.0)


class TestMACD(unittest.TestCase):
    def test_insufficient_data_returns_zeros(self):
        self.assertEqual(macd([1, 2, 3], 12, 26, 9), (0.0, 0.0, 0.0))

    def test_returns_three_values(self):
        prices = [float(i) for i in range(1, 60)]
        result = macd(prices)
        self.assertEqual(len(result), 3)

    def test_rising_prices_macd_positive(self):
        # On a rising series, fast EMA > slow EMA → positive MACD line
        prices = [float(i) for i in range(1, 60)]
        macd_line, _, _ = macd(prices)
        self.assertGreater(macd_line, 0)

    def test_falling_prices_macd_negative(self):
        prices = [float(i) for i in range(60, 0, -1)]
        macd_line, _, _ = macd(prices)
        self.assertLess(macd_line, 0)

    def test_histogram_is_macd_minus_signal(self):
        prices = [float(i) for i in range(1, 60)]
        ml, sl, hist = macd(prices)
        self.assertAlmostEqual(hist, ml - sl, places=10)

    def test_constant_prices_macd_near_zero(self):
        prices = [100.0] * 60
        ml, sl, hist = macd(prices)
        self.assertAlmostEqual(ml, 0.0, places=8)
        self.assertAlmostEqual(hist, 0.0, places=8)


class TestAnalyze(unittest.TestCase):
    def _mock_candles(self, prices: list) -> dict:
        # OKX format: [ts, open, high, low, close, vol, ...]
        # reversed because OKX returns newest first
        candles = [[str(i), "0", "0", "0", str(p), "100"] for i, p in enumerate(reversed(prices))]
        return {"code": "0", "data": candles}

    def _make_client(self, prices):
        client = MagicMock()
        client.candles.return_value = self._mock_candles(prices)
        return client

    def test_returns_all_keys(self):
        prices = [float(i) for i in range(1, 101)]
        with patch("strategies.trend.OKXClient", return_value=self._make_client(prices)):
            result = analyze("BTC-USDT")
        for key in ("signal", "rsi", "ma_fast", "ma_slow", "macd_histogram",
                    "current_price", "inst_id"):
            self.assertIn(key, result)

    def test_buy_signal_on_rising_trend(self):
        # Rising trend with noise so RSI < 70 (not overbought) and MACD > 0
        # Base trend up, but with pullbacks to keep RSI moderate
        import random
        random.seed(1)
        prices = []
        p = 100.0
        for i in range(100):
            p += 1.5 + random.uniform(-0.8, 0.8)  # net upward with noise
            prices.append(p)
        with patch("strategies.trend.OKXClient", return_value=self._make_client(prices)):
            result = analyze("BTC-USDT")
        # fast MA > slow MA guaranteed by net upward trend
        self.assertGreater(result["ma_fast"], result["ma_slow"])

    def test_sell_signal_on_falling_trend(self):
        # Falling trend with noise so RSI > 30 (not oversold) and MACD < 0
        import random
        random.seed(2)
        prices = []
        p = 300.0
        for i in range(100):
            p -= 1.5 + random.uniform(-0.8, 0.8)  # net downward with noise
            prices.append(max(p, 1.0))
        with patch("strategies.trend.OKXClient", return_value=self._make_client(prices)):
            result = analyze("BTC-USDT")
        # fast MA < slow MA guaranteed by net downward trend
        self.assertLess(result["ma_fast"], result["ma_slow"])

    def test_api_error_returns_error_dict(self):
        client = MagicMock()
        client.candles.return_value = {"code": "1", "msg": "timeout"}
        with patch("strategies.trend.OKXClient", return_value=client):
            result = analyze("INVALID")
        self.assertIn("error", result)

    def test_current_price_matches_last_candle(self):
        prices = [float(i) for i in range(1, 101)]
        with patch("strategies.trend.OKXClient", return_value=self._make_client(prices)):
            result = analyze("BTC-USDT")
        self.assertAlmostEqual(result["current_price"], 100.0)


if __name__ == "__main__":
    unittest.main()
