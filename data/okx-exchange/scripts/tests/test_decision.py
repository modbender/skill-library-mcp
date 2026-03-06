"""Unit tests for okx_decision.py — DecisionEngine"""
import sys, os, json, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock


def _engine(tmp, lessons=None, patterns=None, journal=None, model=None):
    """Build a DecisionEngine with in-memory data, no real file I/O."""
    from okx_decision import DecisionEngine
    engine = DecisionEngine.__new__(DecisionEngine)
    engine.lessons       = lessons  or {}
    engine.patterns      = patterns or {}
    engine.journal       = journal  or {}
    engine.model         = model    or {"optimal_parameters": {
        "stop_loss_pct": 3.0, "take_profit_pct": 15.0,
        "position_size_usdt": 50, "leverage": 3,
    }, "performance_stats": {"win_rate": 50.0}}
    engine.monitoring    = {}
    engine.decision_log  = {}
    return engine


# ── check_avoid_conditions ───────────────────────────────────────────────────

class TestCheckAvoidConditions(unittest.TestCase):

    def test_no_avoid_when_empty(self):
        engine = _engine(None)
        avoid, reason = engine.check_avoid_conditions("BTC", "BUY", "bull")
        self.assertFalse(avoid)
        self.assertEqual(reason, "")

    def test_avoids_on_matching_lesson(self):
        lessons = {"lessons": [{
            "type": "large_loss",
            "lesson": "BTC 大亏",
            "avoid_condition": {"coin": "BTC", "signal": "BUY", "market_regime": "bear"}
        }]}
        engine = _engine(None, lessons=lessons)
        avoid, reason = engine.check_avoid_conditions("BTC", "BUY", "bear")
        self.assertTrue(avoid)
        self.assertIn("BTC 大亏", reason)

    def test_avoids_on_failed_pattern(self):
        patterns = {"patterns": [{
            "coin": "ETH", "signal": "SELL", "market_regime": "bull",
            "pattern_type": "failed", "win_rate": 0.15
        }]}
        engine = _engine(None, patterns=patterns)
        avoid, reason = engine.check_avoid_conditions("ETH", "SELL", "bull")
        self.assertTrue(avoid)

    def test_no_avoid_on_different_regime(self):
        lessons = {"lessons": [{
            "avoid_condition": {"coin": "BTC", "signal": "BUY", "market_regime": "bear"}
        }]}
        engine = _engine(None, lessons=lessons)
        avoid, _ = engine.check_avoid_conditions("BTC", "BUY", "bull")
        self.assertFalse(avoid)


# ── check_success_patterns ───────────────────────────────────────────────────

class TestCheckSuccessPatterns(unittest.TestCase):

    def test_returns_empty_when_none(self):
        engine = _engine(None)
        self.assertEqual(engine.check_success_patterns("BTC", "BUY", "bull"), [])

    def test_returns_successful_pattern(self):
        patterns = {"patterns": [{
            "coin": "BTC", "signal": "BUY", "market_regime": "bull",
            "pattern_type": "successful", "win_rate": 0.75,
            "total_pnl": 30.0, "trades": 10
        }]}
        engine = _engine(None, patterns=patterns)
        result = engine.check_success_patterns("BTC", "BUY", "bull")
        self.assertEqual(len(result), 1)
        self.assertIn("win_rate", result[0])

    def test_does_not_return_failed_pattern(self):
        patterns = {"patterns": [{
            "coin": "BTC", "signal": "BUY", "market_regime": "bull",
            "pattern_type": "failed", "win_rate": 0.2
        }]}
        engine = _engine(None, patterns=patterns)
        result = engine.check_success_patterns("BTC", "BUY", "bull")
        self.assertEqual(result, [])

    def test_returns_replicate_lesson(self):
        lessons = {"lessons": [{
            "type": "large_win",
            "lesson": "BTC 大赚",
            "action": "加仓",
            "replicate_condition": {"coin": "BTC", "signal": "BUY", "market_regime": "bull"}
        }]}
        engine = _engine(None, lessons=lessons)
        result = engine.check_success_patterns("BTC", "BUY", "bull")
        self.assertEqual(len(result), 1)
        self.assertIn("lesson", result[0])


# ── generate_decision ────────────────────────────────────────────────────────

class TestGenerateDecision(unittest.TestCase):

    def test_returns_avoid_when_lesson_matches(self):
        lessons = {"lessons": [{
            "type": "large_loss",
            "lesson": "bad trade",
            "avoid_condition": {"coin": "BTC", "signal": "BUY", "market_regime": "bear"}
        }]}
        engine = _engine(None, lessons=lessons)
        decision = engine.generate_decision("BTC", "BUY", "bear", 66000)
        self.assertEqual(decision["decision"], "avoid")
        self.assertIsNotNone(decision["avoid_warning"])

    def test_strong_bull_buy_signal_returns_buy(self):
        engine = _engine(None)
        decision = engine.generate_decision("BTC", "BUY", "strong_bull", 66000, rsi=50)
        self.assertEqual(decision["decision"], "buy")

    def test_strong_bear_sell_signal_returns_sell(self):
        engine = _engine(None)
        decision = engine.generate_decision("BTC", "SELL", "strong_bear", 66000, rsi=50)
        self.assertEqual(decision["decision"], "sell")

    def test_oversold_rsi_returns_buy(self):
        # ranging applies *0.5 penalty → confidence 0.15 < 0.3 threshold → wait
        # use "bull" which has no penalty so RSI confidence 0.3 meets threshold
        engine = _engine(None)
        decision = engine.generate_decision("BTC", "BUY", "bull", 66000, rsi=25)
        self.assertEqual(decision["decision"], "buy")

    def test_overbought_rsi_returns_sell(self):
        # same reason: use "bear" to avoid the ranging 0.5 penalty
        engine = _engine(None)
        decision = engine.generate_decision("BTC", "SELL", "bear", 66000, rsi=75)
        self.assertEqual(decision["decision"], "sell")

    def test_low_confidence_returns_wait(self):
        engine = _engine(None)
        # ranging + no strong signal + rsi=50 → confidence too low
        decision = engine.generate_decision("BTC", "BUY", "ranging", 66000, rsi=50)
        self.assertEqual(decision["decision"], "wait")

    def test_decision_has_required_keys(self):
        engine = _engine(None)
        d = engine.generate_decision("BTC", "BUY", "strong_bull", 66000)
        for key in ("decision", "confidence", "reasons", "coin", "signal", "market_regime"):
            self.assertIn(key, d)

    def test_confidence_capped_at_1(self):
        patterns = {"patterns": [{
            "coin": "BTC", "signal": "BUY", "market_regime": "strong_bull",
            "pattern_type": "successful", "win_rate": 0.9,
            "total_pnl": 100.0, "trades": 20
        }] * 5}
        engine = _engine(None, patterns=patterns)
        d = engine.generate_decision("BTC", "BUY", "strong_bull", 66000, rsi=25)
        self.assertLessEqual(d["confidence"], 1.0)

    def test_buy_decision_includes_parameters(self):
        engine = _engine(None)
        d = engine.generate_decision("BTC", "BUY", "strong_bull", 66000)
        self.assertIn("position_usdt", d["parameters"])
        self.assertIn("stop_loss_pct", d["parameters"])


# ── log_decision ─────────────────────────────────────────────────────────────

class TestLogDecision(unittest.TestCase):

    def test_appends_decision(self):
        engine = _engine(None)
        with patch.object(engine, "decision_log", {}), \
             patch("okx_decision.save_json"):
            engine.log_decision({"decision": "buy", "coin": "BTC"})
            self.assertEqual(len(engine.decision_log["decisions"]), 1)

    def test_caps_at_500(self):
        engine = _engine(None)
        engine.decision_log = {"decisions": [{"d": i} for i in range(500)]}
        with patch("okx_decision.save_json"):
            engine.log_decision({"decision": "sell"})
        self.assertEqual(len(engine.decision_log["decisions"]), 500)
        self.assertEqual(engine.decision_log["decisions"][-1]["decision"], "sell")


# ── get_decision_summary ─────────────────────────────────────────────────────

class TestGetDecisionSummary(unittest.TestCase):

    def test_returns_last_n(self):
        engine = _engine(None)
        engine.decision_log = {"decisions": [
            {"timestamp": "2024-01-01T00:00:00", "coin": f"COIN{i}",
             "decision": "buy", "confidence": 0.8, "reasons": []}
            for i in range(20)
        ]}
        result = engine.get_decision_summary(5)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[-1]["coin"], "COIN19")

    def test_empty_log_returns_empty(self):
        engine = _engine(None)
        self.assertEqual(engine.get_decision_summary(), [])

    def test_summary_contains_required_fields(self):
        engine = _engine(None)
        engine.decision_log = {"decisions": [{
            "timestamp": "2024-01-01T00:00:00", "coin": "BTC",
            "decision": "buy", "confidence": 0.7, "reasons": ["RSI 超卖"]
        }]}
        result = engine.get_decision_summary(1)
        self.assertIn("coin", result[0])
        self.assertIn("decision", result[0])
        self.assertIn("confidence", result[0])


# ── simulate_scenario ────────────────────────────────────────────────────────

class TestSimulateScenario(unittest.TestCase):

    def test_insufficient_data_when_no_trades(self):
        engine = _engine(None, journal={})
        result = engine.simulate_scenario("BTC", "long", 66000, 100, 3, 0.03, 0.15)
        self.assertEqual(result["status"], "insufficient_data")

    def test_simulated_when_trades_exist(self):
        journal = {"trades": [
            {"coin": "BTC-USDT-SWAP", "direction": "long",
             "pnl_pct": 5.0, "pnl_usdt": 10.0}
            for _ in range(5)
        ]}
        engine = _engine(None, journal=journal)
        result = engine.simulate_scenario("BTC-USDT-SWAP", "long", 66000, 100, 3, 0.03, 0.15)
        self.assertEqual(result["status"], "simulated")
        self.assertIn("scenarios", result)
        self.assertIn("expected_value_usdt", result)

    def test_scenarios_have_three_cases(self):
        journal = {"trades": [
            {"coin": "BTC", "direction": "long", "pnl_pct": 3.0, "pnl_usdt": 5.0}
        ]}
        engine = _engine(None, journal=journal)
        result = engine.simulate_scenario("BTC", "long", 66000, 100, 3, 0.03, 0.15)
        if result["status"] == "simulated":
            for case in ("bull_case", "base_case", "bear_case"):
                self.assertIn(case, result["scenarios"])


if __name__ == "__main__":
    unittest.main()
