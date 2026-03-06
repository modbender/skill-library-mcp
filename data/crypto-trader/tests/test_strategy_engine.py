"""Tests for the Strategy Engine module."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from strategy_engine import BaseStrategy, StrategyEngine


class MockStrategy(BaseStrategy):
    name = "mock"
    display_name = "Mock Strategy"

    def evaluate(self):
        return [{"symbol": "BTC/USDT", "side": "buy", "amount": 0.001, "reason": "test"}]


class TestStrategyEngine:
    @pytest.fixture
    def engine(self, tmp_path):
        state_path = str(tmp_path / "strategies.json")
        with patch.dict(os.environ, {"CRYPTO_STRATEGY_STATE_PATH": state_path}):
            exchange_mgr = MagicMock()
            exchange_mgr.available_exchanges = ["binance"]
            risk_mgr = MagicMock()
            engine = StrategyEngine(exchange_mgr, risk_mgr)
            engine.register_strategy(MockStrategy)
            return engine

    def test_register_strategy(self, engine):
        assert "mock" in engine.get_available_strategies()

    def test_start_strategy(self, engine):
        result = engine.start_strategy("mock", {"symbol": "ETH/USDT"})
        assert result["status"] == "ok"
        assert result["strategy_name"] == "mock"
        assert "strategy_id" in result

    def test_start_unknown_strategy(self, engine):
        result = engine.start_strategy("nonexistent")
        assert result["status"] == "error"

    def test_stop_strategy(self, engine):
        start = engine.start_strategy("mock")
        sid = start["strategy_id"]
        stop = engine.stop_strategy(sid)
        assert stop["status"] == "ok"

    def test_stop_nonexistent_strategy(self, engine):
        result = engine.stop_strategy("fake_id")
        assert result["status"] == "error"

    def test_list_strategies(self, engine):
        engine.start_strategy("mock")
        strategies = engine.list_strategies()
        assert len(strategies) == 1
        assert strategies[0]["name"] == "mock"

    def test_evaluate_all(self, engine):
        engine.start_strategy("mock")
        signals = engine.evaluate_all()
        assert len(signals) >= 1
        assert signals[0]["symbol"] == "BTC/USDT"

    def test_stop_all(self, engine):
        engine.start_strategy("mock")
        engine.start_strategy("mock")
        results = engine.stop_all()
        assert len(results) == 2
        assert engine.list_strategies() == []
