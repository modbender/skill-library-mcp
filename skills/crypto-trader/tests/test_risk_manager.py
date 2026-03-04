"""Tests for the Risk Manager module."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from risk_manager import RiskManager, RiskLimitExceeded


@pytest.fixture
def risk_config(tmp_path):
    """Create a temporary risk config file."""
    config = {
        "global_limits": {
            "max_position_size_pct": 25.0,
            "max_daily_loss_eur": 50.0,
            "max_drawdown_pct": 15.0,
            "max_order_size_eur": 100.0,
            "max_open_orders": 50,
            "min_cash_reserve_pct": 10.0,
            "emergency_stop_loss_pct": 20.0,
        },
        "strategy_overrides": {
            "grid_trading": {
                "max_order_size_eur": 50.0,
                "max_open_orders": 20,
            },
        },
        "stop_loss": {
            "enabled": True,
            "default_pct": 5.0,
            "trailing_enabled": True,
            "trailing_pct": 3.0,
        },
        "take_profit": {
            "enabled": True,
            "default_pct": 10.0,
            "partial_exit_enabled": True,
            "partial_exit_pct": 50.0,
            "partial_exit_trigger_pct": 5.0,
        },
    }
    config_path = tmp_path / "risk_limits.yaml"
    import yaml
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    return str(config_path)


@pytest.fixture
def risk_manager(risk_config, tmp_path):
    """Create a RiskManager with temporary state."""
    state_path = str(tmp_path / "risk-state.json")
    with patch.dict(os.environ, {"CRYPTO_RISK_STATE_PATH": state_path}):
        return RiskManager(config_path=risk_config)


class TestValidateOrder:
    def test_valid_order_passes(self, risk_manager):
        risk_manager.validate_order(
            strategy="grid_trading",
            exchange="binance",
            symbol="BTC/USDT",
            side="buy",
            amount=0.001,
            price=40000,
            portfolio_value_eur=1000,
            open_order_count=0,
        )

    def test_max_order_size_global(self, risk_manager):
        with pytest.raises(RiskLimitExceeded, match="max_order_size"):
            risk_manager.validate_order(
                strategy="dca",
                exchange="binance",
                symbol="BTC/USDT",
                side="buy",
                amount=1.0,
                price=200,
                portfolio_value_eur=10000,
                open_order_count=0,
            )

    def test_max_order_size_strategy_override(self, risk_manager):
        with pytest.raises(RiskLimitExceeded, match="max_order_size"):
            risk_manager.validate_order(
                strategy="grid_trading",
                exchange="binance",
                symbol="BTC/USDT",
                side="buy",
                amount=1.0,
                price=60,
                portfolio_value_eur=10000,
                open_order_count=0,
            )

    def test_max_open_orders(self, risk_manager):
        with pytest.raises(RiskLimitExceeded, match="max_open_orders"):
            risk_manager.validate_order(
                strategy="grid_trading",
                exchange="binance",
                symbol="BTC/USDT",
                side="buy",
                amount=0.001,
                price=40,
                portfolio_value_eur=1000,
                open_order_count=20,
            )

    def test_max_position_size(self, risk_manager):
        with pytest.raises(RiskLimitExceeded, match="max_position_size"):
            risk_manager.validate_order(
                strategy=None,
                exchange="binance",
                symbol="BTC/USDT",
                side="buy",
                amount=1.0,
                price=30,
                portfolio_value_eur=100,
                open_order_count=0,
            )

    def test_kill_switch_blocks_orders(self, risk_manager):
        risk_manager.activate_kill_switch("test")
        with pytest.raises(RiskLimitExceeded, match="kill_switch"):
            risk_manager.validate_order(
                strategy=None,
                exchange="binance",
                symbol="BTC/USDT",
                side="buy",
                amount=0.001,
                price=40,
                portfolio_value_eur=1000,
                open_order_count=0,
            )


class TestStopLoss:
    def test_stop_loss_triggers(self, risk_manager):
        assert risk_manager.check_stop_loss(entry_price=100, current_price=94) is True

    def test_stop_loss_does_not_trigger(self, risk_manager):
        assert risk_manager.check_stop_loss(entry_price=100, current_price=97) is False

    def test_trailing_stop_triggers(self, risk_manager):
        assert risk_manager.check_trailing_stop(highest_price=110, current_price=106) is True

    def test_trailing_stop_does_not_trigger(self, risk_manager):
        assert risk_manager.check_trailing_stop(highest_price=110, current_price=108) is False


class TestTakeProfit:
    def test_take_profit_triggers(self, risk_manager):
        assert risk_manager.check_take_profit(entry_price=100, current_price=111) is True

    def test_take_profit_does_not_trigger(self, risk_manager):
        assert risk_manager.check_take_profit(entry_price=100, current_price=108) is False

    def test_partial_take_profit(self, risk_manager):
        fraction = risk_manager.check_partial_take_profit(entry_price=100, current_price=106)
        assert fraction == 0.5


class TestKillSwitch:
    def test_activate_and_deactivate(self, risk_manager):
        assert risk_manager.is_killed is False
        risk_manager.activate_kill_switch("test")
        assert risk_manager.is_killed is True
        risk_manager.deactivate_kill_switch()
        assert risk_manager.is_killed is False


class TestStatus:
    def test_get_status_returns_dict(self, risk_manager):
        status = risk_manager.get_status()
        assert "daily_pnl_eur" in status
        assert "drawdown_pct" in status
        assert "kill_switch_active" in status
        assert "limits" in status


class TestRecordTrade:
    def test_record_trade_updates_pnl(self, risk_manager):
        risk_manager.record_trade({
            "symbol": "BTC/USDT",
            "side": "sell",
            "amount": 0.01,
            "price": 50000,
            "realized_pnl_eur": 15.0,
        })
        status = risk_manager.get_status()
        assert status["daily_pnl_eur"] == 15.0
        assert status["trades_today_count"] == 1
