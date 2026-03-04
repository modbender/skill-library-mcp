"""Tests for signal_types.py and signal_engine.py."""
import sys
import os
import pytest
import pandas as pd
import tempfile
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from signal_types import (
    apply_crossover, apply_threshold, apply_expression, apply_range,
    apply_computed_signals, validate_expression, SIGNAL_TYPE_MAP,
)
from signal_engine import load_signal, list_signals


# -- Fixtures --

@pytest.fixture
def crossover_df():
    return pd.DataFrame({
        "Name": ["A", "B", "C", "D"],
        "SMA50": [100, 200, 150, 80],
        "SMA200": [95, 210, 148, 85],
        "Price": [105, 195, 155, 78],
    })


@pytest.fixture
def indicator_df():
    return pd.DataFrame({
        "Name": ["A", "B", "C", "D", "E"],
        "RSI": [25, 45, 70, 15, 55],
        "Price": [100, 200, 300, 50, 150],
        "Volume": [1e6, 5e6, 2e6, 8e6, 3e6],
        "AvgVolume": [0.5e6, 4e6, 3e6, 2e6, 3e6],
        "Change": [2.0, -1.0, 0.5, 5.0, 1.2],
    })


# -- Signal type tests --

def test_crossover_up(crossover_df):
    config = {"fast": "SMA50", "slow": "SMA200", "direction": "up"}
    result = apply_crossover(crossover_df, config)
    assert len(result) == 2  # A (100>95) and C (150>148)
    assert list(result["Name"]) == ["A", "C"]


def test_crossover_down(crossover_df):
    config = {"fast": "SMA50", "slow": "SMA200", "direction": "down"}
    result = apply_crossover(crossover_df, config)
    assert len(result) == 2  # B (200<210) and D (80<85)
    assert list(result["Name"]) == ["B", "D"]


def test_crossover_both(crossover_df):
    config = {"fast": "SMA50", "slow": "SMA200", "direction": "both"}
    result = apply_crossover(crossover_df, config)
    assert len(result) == 4  # All have different values


def test_crossover_missing_column(crossover_df):
    config = {"fast": "NONEXISTENT", "slow": "SMA200", "direction": "up"}
    result = apply_crossover(crossover_df, config)
    assert len(result) == len(crossover_df)  # Returns unchanged


def test_threshold_less_than(indicator_df):
    config = {"field": "RSI", "op": "<", "value": 30}
    result = apply_threshold(indicator_df, config)
    assert len(result) == 2  # A (25) and D (15)


def test_threshold_greater_than(indicator_df):
    config = {"field": "RSI", "op": ">", "value": 50}
    result = apply_threshold(indicator_df, config)
    assert len(result) == 2  # C (70) and E (55)


def test_threshold_missing_field(indicator_df):
    config = {"field": "MISSING", "op": ">", "value": 0}
    result = apply_threshold(indicator_df, config)
    assert len(result) == len(indicator_df)


def test_threshold_invalid_op(indicator_df):
    config = {"field": "RSI", "op": "~=", "value": 30}
    with pytest.raises(ValueError, match="Unknown threshold operator"):
        apply_threshold(indicator_df, config)


def test_expression_valid(indicator_df):
    config = {"expr": "Volume > AvgVolume * 2"}
    result = apply_expression(indicator_df, config)
    assert len(result) == 1  # D (8M > 2M*2=4M); A is equal, not greater


def test_expression_invalid_returns_original(indicator_df):
    config = {"expr": "NONEXISTENT > 0"}
    result = apply_expression(indicator_df, config)
    assert len(result) == len(indicator_df)  # Returns unchanged on error


def test_validate_expression_blocked():
    with pytest.raises(ValueError, match="blocked keywords"):
        validate_expression("import os")


def test_validate_expression_valid():
    validate_expression("PRICE > 50")
    validate_expression("VOLUME > AVERAGE_VOLUME * 2")


def test_range_filter(indicator_df):
    config = {"field": "RSI", "min": 20, "max": 50}
    result = apply_range(indicator_df, config)
    assert len(result) == 2  # A (25) and B (45)


def test_range_missing_field(indicator_df):
    config = {"field": "MISSING", "min": 0, "max": 100}
    result = apply_range(indicator_df, config)
    assert len(result) == len(indicator_df)


# -- Dispatcher tests --

def test_signal_type_map_has_all_types():
    assert set(SIGNAL_TYPE_MAP.keys()) == {"crossover", "threshold", "expression", "range"}


def test_apply_computed_signals_chain(indicator_df):
    computed = [
        {"type": "threshold", "field": "RSI", "op": "<", "value": 60},
        {"type": "threshold", "field": "Change", "op": ">", "value": 0},
    ]
    result = apply_computed_signals(indicator_df, computed)
    # RSI<60: A(25), B(45), D(15), E(55) -> Change>0: A(2), D(5), E(1.2)
    assert len(result) == 3


def test_apply_computed_signals_empty(indicator_df):
    result = apply_computed_signals(indicator_df, [])
    assert len(result) == len(indicator_df)


def test_apply_computed_signals_unknown_type(indicator_df):
    with pytest.raises(ValueError, match="Unknown signal type"):
        apply_computed_signals(indicator_df, [{"type": "unknown"}])


# -- YAML loading tests --

def test_load_signal_valid():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({"name": "test", "asset_class": "stock", "filters": []}, f)
        f.flush()
        config = load_signal(f.name)
        assert config["name"] == "test"
        assert config["asset_class"] == "stock"
    os.unlink(f.name)


def test_load_signal_missing_file():
    with pytest.raises(FileNotFoundError):
        load_signal("/nonexistent/path/signal.yaml")


def test_load_signal_invalid_config():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({"invalid": "config"}, f)
        f.flush()
        with pytest.raises(ValueError, match="missing"):
            load_signal(f.name)
    os.unlink(f.name)


def test_load_signal_by_name():
    """Test loading signal by name from default signals dir."""
    config = load_signal("golden-cross")
    assert config["name"] == "golden-cross"
    assert config["asset_class"] == "stock"


def test_list_signals(capsys):
    list_signals()
    output = capsys.readouterr().out
    assert "golden-cross" in output
    assert "oversold-bounce" in output
    assert "volume-breakout" in output
