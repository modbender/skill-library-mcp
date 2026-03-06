"""Unit tests for okx_learning.py"""
import sys, os, json, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from pathlib import Path
from unittest.mock import patch


def _patch_paths(tmp):
    """Return a dict of patches redirecting all learning file paths to tmp."""
    import okx_learning as L
    return {
        "LEARNING_MODEL_FILE": Path(tmp) / "model.json",
        "TRADE_JOURNAL_FILE":  Path(tmp) / "journal.json",
        "LESSONS_FILE":        Path(tmp) / "lessons.json",
        "PATTERNS_FILE":       Path(tmp) / "patterns.json",
        "MONITORING_LOG_FILE": Path(tmp) / "monitoring.json",
    }


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        import okx_learning as L
        self._orig = {k: getattr(L, k) for k in _patch_paths(self.tmp)}
        for k, v in _patch_paths(self.tmp).items():
            setattr(L, k, v)

    def tearDown(self):
        import okx_learning as L
        for k, v in self._orig.items():
            setattr(L, k, v)
        shutil.rmtree(self.tmp)


# ── generate_trade_id ────────────────────────────────────────────────────────

class TestGenerateTradeId(_Base):
    def test_deterministic(self):
        from okx_learning import generate_trade_id
        d = {"coin": "BTC", "timestamp": "2024-01-01", "entry_price": 50000}
        self.assertEqual(generate_trade_id(d), generate_trade_id(d))

    def test_length_12(self):
        from okx_learning import generate_trade_id
        id_ = generate_trade_id({"coin": "ETH"})
        self.assertEqual(len(id_), 12)

    def test_different_inputs_different_ids(self):
        from okx_learning import generate_trade_id
        a = generate_trade_id({"coin": "BTC", "entry_price": 50000})
        b = generate_trade_id({"coin": "ETH", "entry_price": 50000})
        self.assertNotEqual(a, b)


# ── compress_trade_journal ───────────────────────────────────────────────────

class TestCompressTradeJournal(_Base):
    def _journal(self, n):
        return {"trades": [
            {"timestamp": f"2024-01-{i:02d}T00:00:00", "pnl_pct": 1.0, "pnl_usdt": 1.0}
            for i in range(1, n + 1)
        ]}

    def test_no_compression_when_under_limit(self):
        from okx_learning import compress_trade_journal, MAX_TRADES_IN_MEMORY
        j = self._journal(10)
        result = compress_trade_journal(j)
        self.assertEqual(len(result["trades"]), 10)
        self.assertNotIn("compressed_stats", result)

    def test_compression_when_over_limit(self):
        from okx_learning import compress_trade_journal, MAX_TRADES_IN_MEMORY
        n = MAX_TRADES_IN_MEMORY + 5
        j = self._journal(n)
        result = compress_trade_journal(j)
        self.assertEqual(len(result["trades"]), MAX_TRADES_IN_MEMORY)
        self.assertIn("compressed_stats", result)

    def test_compressed_stats_contain_counts(self):
        from okx_learning import compress_trade_journal, MAX_TRADES_IN_MEMORY
        n = MAX_TRADES_IN_MEMORY + 10
        j = self._journal(n)
        result = compress_trade_journal(j)
        stats = result["compressed_stats"][0]
        self.assertEqual(stats["total_trades"], 10)
        self.assertIn("winning_trades", stats)
        self.assertIn("total_pnl_usdt", stats)


# ── extract_lesson ───────────────────────────────────────────────────────────

class TestExtractLesson(_Base):
    def test_large_loss_returns_lesson(self):
        from okx_learning import extract_lesson
        lesson = extract_lesson({"pnl_pct": -8, "coin": "BTC",
                                  "signal_type": "trend", "market_regime": "bear"})
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson["type"], "large_loss")
        self.assertIn("avoid_condition", lesson)

    def test_large_loss_severity_high_when_below_minus10(self):
        from okx_learning import extract_lesson
        lesson = extract_lesson({"pnl_pct": -12, "coin": "BTC",
                                  "signal_type": "trend", "market_regime": "bear"})
        self.assertEqual(lesson["severity"], "high")

    def test_large_win_returns_lesson(self):
        from okx_learning import extract_lesson
        lesson = extract_lesson({"pnl_pct": 15, "coin": "ETH",
                                  "signal_type": "trend", "market_regime": "bull"})
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson["type"], "large_win")
        self.assertIn("replicate_condition", lesson)

    def test_quick_win_returns_lesson(self):
        from okx_learning import extract_lesson
        lesson = extract_lesson({"pnl_pct": 6, "hold_time_hours": 0.5,
                                  "coin": "SOL", "signal_type": "trend", "market_regime": "bull"})
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson["type"], "quick_win")

    def test_good_stop_returns_lesson(self):
        from okx_learning import extract_lesson
        lesson = extract_lesson({"pnl_pct": -3.0, "coin": "BTC",
                                  "signal_type": "trend", "market_regime": "bear"})
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson["type"], "good_stop")

    def test_small_pnl_returns_none(self):
        from okx_learning import extract_lesson
        lesson = extract_lesson({"pnl_pct": 1.0, "coin": "BTC",
                                  "signal_type": "trend", "market_regime": "ranging"})
        self.assertIsNone(lesson)


# ── update_patterns ──────────────────────────────────────────────────────────

class TestUpdatePatterns(_Base):
    def test_creates_new_pattern(self):
        from okx_learning import update_patterns
        patterns = {}
        update_patterns(patterns, {"coin": "BTC", "signal_type": "trend",
                                    "market_regime": "bull", "pnl_pct": 5.0})
        self.assertEqual(len(patterns["patterns"]), 1)
        self.assertEqual(patterns["patterns"][0]["trades"], 1)

    def test_win_increments_correctly(self):
        from okx_learning import update_patterns
        patterns = {}
        update_patterns(patterns, {"coin": "BTC", "signal_type": "trend",
                                    "market_regime": "bull", "pnl_pct": 5.0})
        self.assertEqual(patterns["patterns"][0]["wins"], 1)
        self.assertEqual(patterns["patterns"][0]["losses"], 0)

    def test_loss_increments_correctly(self):
        from okx_learning import update_patterns
        patterns = {}
        update_patterns(patterns, {"coin": "BTC", "signal_type": "trend",
                                    "market_regime": "bull", "pnl_pct": -3.0})
        self.assertEqual(patterns["patterns"][0]["losses"], 1)

    def test_accumulates_on_same_key(self):
        from okx_learning import update_patterns
        patterns = {}
        trade = {"coin": "BTC", "signal_type": "trend", "market_regime": "bull"}
        update_patterns(patterns, {**trade, "pnl_pct": 5.0})
        update_patterns(patterns, {**trade, "pnl_pct": -2.0})
        self.assertEqual(len(patterns["patterns"]), 1)
        self.assertEqual(patterns["patterns"][0]["trades"], 2)

    def test_win_rate_calculated(self):
        from okx_learning import update_patterns
        patterns = {}
        trade = {"coin": "BTC", "signal_type": "trend", "market_regime": "bull"}
        update_patterns(patterns, {**trade, "pnl_pct": 5.0})
        update_patterns(patterns, {**trade, "pnl_pct": 5.0})
        update_patterns(patterns, {**trade, "pnl_pct": -2.0})
        self.assertAlmostEqual(patterns["patterns"][0]["win_rate"], 2/3)

    def test_pattern_marked_successful_after_enough_trades(self):
        from okx_learning import update_patterns, MIN_TRADES_FOR_PATTERN
        patterns = {}
        trade = {"coin": "BTC", "signal_type": "trend", "market_regime": "bull"}
        for _ in range(MIN_TRADES_FOR_PATTERN):
            update_patterns(patterns, {**trade, "pnl_pct": 5.0})  # 100% win rate
        self.assertEqual(patterns["patterns"][0]["pattern_type"], "successful")

    def test_pattern_marked_failed_after_enough_losses(self):
        from okx_learning import update_patterns, MIN_TRADES_FOR_PATTERN
        patterns = {}
        trade = {"coin": "BTC", "signal_type": "trend", "market_regime": "bull"}
        for _ in range(MIN_TRADES_FOR_PATTERN):
            update_patterns(patterns, {**trade, "pnl_pct": -3.0})  # 0% win rate
        self.assertEqual(patterns["patterns"][0]["pattern_type"], "failed")


# ── should_avoid_trade ───────────────────────────────────────────────────────

class TestShouldAvoidTrade(_Base):
    def test_returns_false_when_no_data(self):
        from okx_learning import should_avoid_trade
        avoid, reason = should_avoid_trade("BTC", "BUY", "bull")
        self.assertFalse(avoid)
        self.assertIsNone(reason)

    def test_avoids_when_matching_lesson(self):
        from okx_learning import save_json, LESSONS_FILE, should_avoid_trade
        lessons = {"lessons": [{
            "type": "large_loss",
            "lesson": "BTC 亏损",
            "avoid_condition": {"coin": "BTC", "signal": "BUY", "market_regime": "bear"}
        }]}
        save_json(LESSONS_FILE, lessons)
        avoid, reason = should_avoid_trade("BTC", "BUY", "bear")
        self.assertTrue(avoid)
        self.assertIn("避免", reason)

    def test_avoids_when_failed_pattern(self):
        from okx_learning import save_json, PATTERNS_FILE, should_avoid_trade
        patterns = {"patterns": [{
            "coin": "ETH", "signal": "SELL", "market_regime": "bull",
            "pattern_type": "failed", "win_rate": 0.2
        }]}
        save_json(PATTERNS_FILE, patterns)
        avoid, reason = should_avoid_trade("ETH", "SELL", "bull")
        self.assertTrue(avoid)

    def test_no_avoid_when_different_coin(self):
        from okx_learning import save_json, LESSONS_FILE, should_avoid_trade
        lessons = {"lessons": [{
            "type": "large_loss",
            "avoid_condition": {"coin": "BTC", "signal": "BUY", "market_regime": "bear"}
        }]}
        save_json(LESSONS_FILE, lessons)
        avoid, _ = should_avoid_trade("ETH", "BUY", "bear")
        self.assertFalse(avoid)


# ── identify_market_regime ───────────────────────────────────────────────────

class TestIdentifyMarketRegime(_Base):
    def test_empty_returns_unknown(self):
        from okx_learning import identify_market_regime
        self.assertEqual(identify_market_regime([]), "unknown")

    def test_all_sell_returns_strong_bear(self):
        from okx_learning import identify_market_regime
        data = [{"signal": "SELL"}] * 20
        self.assertEqual(identify_market_regime(data), "strong_bear")

    def test_all_buy_returns_strong_bull(self):
        from okx_learning import identify_market_regime
        data = [{"signal": "BUY"}] * 20
        self.assertEqual(identify_market_regime(data), "strong_bull")

    def test_mixed_returns_ranging(self):
        from okx_learning import identify_market_regime
        data = [{"signal": "BUY"}] * 10 + [{"signal": "SELL"}] * 10
        self.assertEqual(identify_market_regime(data), "ranging")


# ── get_adaptive_parameters ──────────────────────────────────────────────────

class TestGetAdaptiveParameters(_Base):
    def test_all_regimes_return_params(self):
        from okx_learning import get_adaptive_parameters
        for regime in ("strong_bull", "weak_bull", "ranging", "weak_bear", "strong_bear"):
            params = get_adaptive_parameters(regime)
            self.assertIn("position_size", params)
            self.assertIn("leverage", params)
            self.assertIn("stop_loss", params)

    def test_unknown_regime_falls_back_to_ranging(self):
        from okx_learning import get_adaptive_parameters
        params = get_adaptive_parameters("unknown_regime")
        ranging = get_adaptive_parameters("ranging")
        self.assertEqual(params, ranging)


# ── update_model_stats ───────────────────────────────────────────────────────

class TestUpdateModelStats(_Base):
    def _model(self):
        from okx_learning import _init_model
        return _init_model({})

    def test_win_increments(self):
        from okx_learning import update_model_stats
        model = self._model()
        update_model_stats(model, {"pnl_pct": 5.0, "pnl_usdt": 10.0, "coin": "BTC"})
        self.assertEqual(model["performance_stats"]["winning_trades"], 1)
        self.assertEqual(model["performance_stats"]["total_trades"], 1)

    def test_loss_increments(self):
        from okx_learning import update_model_stats
        model = self._model()
        update_model_stats(model, {"pnl_pct": -3.0, "pnl_usdt": -5.0, "coin": "BTC"})
        self.assertEqual(model["performance_stats"]["losing_trades"], 1)

    def test_win_rate_correct(self):
        from okx_learning import update_model_stats
        model = self._model()
        update_model_stats(model, {"pnl_pct": 5.0,  "pnl_usdt": 10.0, "coin": "BTC"})
        update_model_stats(model, {"pnl_pct": -3.0, "pnl_usdt": -5.0, "coin": "BTC"})
        self.assertAlmostEqual(model["performance_stats"]["win_rate"], 50.0)

    def test_coin_performance_tracked(self):
        from okx_learning import update_model_stats
        model = self._model()
        update_model_stats(model, {"pnl_pct": 5.0, "pnl_usdt": 10.0, "coin": "ETH"})
        self.assertIn("ETH", model["coin_performance"])
        self.assertEqual(model["coin_performance"]["ETH"]["wins"], 1)

    def test_large_loss_adds_lesson(self):
        from okx_learning import update_model_stats
        model = self._model()
        update_model_stats(model, {"pnl_pct": -8.0, "pnl_usdt": -20.0, "coin": "BTC"})
        self.assertTrue(any(l["type"] == "large_loss" for l in model["lessons_learned"]))


# ── record_trade ─────────────────────────────────────────────────────────────

class TestRecordTrade(_Base):
    def _trade(self, **kwargs):
        base = {"coin": "BTC", "signal_type": "trend", "market_regime": "bull",
                "pnl_pct": 5.0, "pnl_usdt": 10.0}
        return {**base, **kwargs}

    def test_appends_to_journal(self):
        from okx_learning import record_trade, TRADE_JOURNAL_FILE, load_json
        record_trade(self._trade())
        j = load_json(TRADE_JOURNAL_FILE)
        self.assertEqual(len(j["trades"]), 1)

    def test_assigns_trade_id(self):
        from okx_learning import record_trade, TRADE_JOURNAL_FILE, load_json
        record_trade(self._trade())
        j = load_json(TRADE_JOURNAL_FILE)
        self.assertIn("id", j["trades"][0])

    def test_updates_model_win_count(self):
        from okx_learning import record_trade
        model = record_trade(self._trade(pnl_pct=5.0, pnl_usdt=10.0))
        self.assertEqual(model["performance_stats"]["winning_trades"], 1)

    def test_large_loss_writes_lesson(self):
        from okx_learning import record_trade, LESSONS_FILE, load_json
        record_trade(self._trade(pnl_pct=-9.0, pnl_usdt=-20.0))
        lessons = load_json(LESSONS_FILE)
        self.assertTrue(any(l["type"] == "large_loss"
                            for l in lessons.get("lessons", [])))

    def test_updates_patterns_file(self):
        from okx_learning import record_trade, PATTERNS_FILE, load_json
        record_trade(self._trade())
        patterns = load_json(PATTERNS_FILE)
        self.assertEqual(len(patterns.get("patterns", [])), 1)

    def test_multiple_trades_accumulate(self):
        from okx_learning import record_trade, TRADE_JOURNAL_FILE, load_json
        record_trade(self._trade())
        record_trade(self._trade(pnl_pct=3.0, pnl_usdt=6.0))
        j = load_json(TRADE_JOURNAL_FILE)
        self.assertEqual(len(j["trades"]), 2)


# ── get_lessons_summary ───────────────────────────────────────────────────────

class TestGetLessonsSummary(_Base):
    def test_empty_returns_zero_total(self):
        from okx_learning import get_lessons_summary
        s = get_lessons_summary()
        self.assertEqual(s["total_lessons"], 0)

    def test_counts_lessons(self):
        from okx_learning import save_json, LESSONS_FILE, get_lessons_summary
        lessons = {"lessons": [
            {"type": "large_loss", "lesson": "BTC 亏", "action": "减仓",
             "avoid_condition": {"coin": "BTC", "signal": "BUY", "market_regime": "bear"}},
            {"type": "large_win", "lesson": "ETH 赚", "action": "加仓",
             "replicate_condition": {"coin": "ETH", "signal": "BUY", "market_regime": "bull"}},
        ]}
        save_json(LESSONS_FILE, lessons)
        s = get_lessons_summary()
        self.assertEqual(s["total_lessons"], 2)
        self.assertEqual(len(s["avoid_conditions"]), 1)
        self.assertEqual(len(s["replicate_conditions"]), 1)

    def test_successful_patterns_included(self):
        from okx_learning import save_json, PATTERNS_FILE, get_lessons_summary
        patterns = {"patterns": [
            {"coin": "BTC", "signal": "BUY", "market_regime": "bull",
             "pattern_type": "successful", "win_rate": 0.8,
             "total_pnl": 40.0, "trades": 10},
        ]}
        save_json(PATTERNS_FILE, patterns)
        s = get_lessons_summary()
        self.assertEqual(len(s["successful_patterns"]), 1)
        self.assertIn("win_rate", s["successful_patterns"][0])

    def test_failed_patterns_included(self):
        from okx_learning import save_json, PATTERNS_FILE, get_lessons_summary
        patterns = {"patterns": [
            {"coin": "ETH", "signal": "SELL", "market_regime": "bull",
             "pattern_type": "failed", "win_rate": 0.2,
             "total_pnl": -15.0, "trades": 5},
        ]}
        save_json(PATTERNS_FILE, patterns)
        s = get_lessons_summary()
        self.assertEqual(len(s["failed_patterns"]), 1)


# ── get_optimal_conditions ────────────────────────────────────────────────────

class TestGetOptimalConditions(_Base):
    def test_returns_empty_when_no_data(self):
        from okx_learning import get_optimal_conditions
        self.assertEqual(get_optimal_conditions("BTC", "BUY", "bull"), [])

    def test_returns_replicate_suggestion(self):
        from okx_learning import save_json, LESSONS_FILE, get_optimal_conditions
        lessons = {"lessons": [{"type": "large_win", "lesson": "ETH 大赚",
            "action": "加仓",
            "replicate_condition": {"coin": "ETH", "signal": "BUY", "market_regime": "bull"}}
        ]}
        save_json(LESSONS_FILE, lessons)
        result = get_optimal_conditions("ETH", "BUY", "bull")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "replicate")

    def test_returns_successful_pattern_suggestion(self):
        from okx_learning import save_json, PATTERNS_FILE, get_optimal_conditions
        patterns = {"patterns": [
            {"coin": "BTC", "signal": "BUY", "market_regime": "bull",
             "pattern_type": "successful", "win_rate": 0.75,
             "total_pnl": 30.0, "trades": 8},
        ]}
        save_json(PATTERNS_FILE, patterns)
        result = get_optimal_conditions("BTC", "BUY", "bull")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "successful_pattern")

    def test_no_match_on_different_coin(self):
        from okx_learning import save_json, PATTERNS_FILE, get_optimal_conditions
        patterns = {"patterns": [
            {"coin": "BTC", "signal": "BUY", "market_regime": "bull",
             "pattern_type": "successful", "win_rate": 0.8,
             "total_pnl": 20.0, "trades": 5},
        ]}
        save_json(PATTERNS_FILE, patterns)
        self.assertEqual(get_optimal_conditions("ETH", "BUY", "bull"), [])


# ── cleanup_old_data ──────────────────────────────────────────────────────────

class TestCleanupOldData(_Base):
    def test_removes_old_trades(self):
        from okx_learning import save_json, TRADE_JOURNAL_FILE, load_json, cleanup_old_data
        # Write a trade with a date far in the past
        old_journal = {"trades": [
            {"timestamp": "2000-01-01T00:00:00", "pnl_pct": 1.0},
            {"timestamp": "2000-01-02T00:00:00", "pnl_pct": 2.0},
        ]}
        save_json(TRADE_JOURNAL_FILE, old_journal)
        result = cleanup_old_data()
        j = load_json(TRADE_JOURNAL_FILE)
        self.assertEqual(len(j["trades"]), 0)
        self.assertIn("清理了", result)

    def test_keeps_recent_trades(self):
        from datetime import datetime
        from okx_learning import save_json, TRADE_JOURNAL_FILE, load_json, cleanup_old_data
        recent = datetime.now().isoformat()
        journal = {"trades": [{"timestamp": recent, "pnl_pct": 1.0}]}
        save_json(TRADE_JOURNAL_FILE, journal)
        cleanup_old_data()
        j = load_json(TRADE_JOURNAL_FILE)
        self.assertEqual(len(j["trades"]), 1)

    def test_no_cleanup_message_when_nothing_to_remove(self):
        from okx_learning import cleanup_old_data
        result = cleanup_old_data()
        self.assertEqual(result, "无需清理")


if __name__ == "__main__":
    unittest.main()
