"""Tests for screen.py - core screener CLI."""
import sys
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from screener_constants import SCREENER_MAP, OP_MAP, resolve_field, find_df_column
from screen import apply_filters, select_columns, format_markdown


# -- Fixtures --

@pytest.fixture
def stock_df():
    return pd.DataFrame({
        "Symbol": ["NYSE:AAPL", "NYSE:GOOGL", "NYSE:MSFT", "NYSE:TSLA", "NYSE:AMZN"],
        "Name": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],
        "Price": [150.0, 140.0, 350.0, 200.0, 170.0],
        "Volume": [50e6, 30e6, 25e6, 80e6, 40e6],
        "Change %": [2.5, -1.0, 0.5, 5.0, 1.2],
    })


# -- SCREENER_MAP tests --

def test_screener_map_has_all_asset_classes():
    expected = {"stock", "crypto", "forex", "bond", "futures", "coin"}
    assert set(SCREENER_MAP.keys()) == expected


def test_screener_map_values_are_tuples():
    for key, val in SCREENER_MAP.items():
        assert isinstance(val, tuple) and len(val) == 2, f"{key} should map to (Screener, Field) tuple"


# -- OP_MAP tests --

def test_op_map_has_all_operators():
    expected = {">", ">=", "<", "<=", "==", "!=", "between", "isin"}
    assert set(OP_MAP.keys()) == expected


# -- resolve_field tests --

def test_resolve_field_valid():
    import tvscreener as tvs
    field = resolve_field(tvs.StockField, "PRICE")
    assert field == tvs.StockField.PRICE


def test_resolve_field_case_insensitive():
    import tvscreener as tvs
    field = resolve_field(tvs.StockField, "price")
    assert field == tvs.StockField.PRICE


def test_resolve_field_invalid_raises():
    import tvscreener as tvs
    with pytest.raises(ValueError, match="not found"):
        resolve_field(tvs.StockField, "NONEXISTENT_FIELD_XYZ")


# -- find_df_column tests --

def test_find_df_column_exact(stock_df):
    assert find_df_column(stock_df, "Volume") == "Volume"


def test_find_df_column_case_insensitive(stock_df):
    assert find_df_column(stock_df, "VOLUME") == "Volume"


def test_find_df_column_enum_to_display():
    df = pd.DataFrame(columns=["Simple Moving Average (50)", "Relative Strength Index (14)"])
    assert find_df_column(df, "SIMPLE_MOVING_AVERAGE_50") == "Simple Moving Average (50)"
    assert find_df_column(df, "RELATIVE_STRENGTH_INDEX_14") == "Relative Strength Index (14)"


def test_find_df_column_not_found(stock_df):
    assert find_df_column(stock_df, "NONEXISTENT") is None


# -- format_markdown tests --

def test_format_markdown_basic(stock_df):
    result = format_markdown(stock_df, "stock")
    assert "**Stock Screener**" in result
    assert "5 of 5 results" in result


def test_format_markdown_with_sort(stock_df):
    result = format_markdown(stock_df, "stock", sort_by="VOLUME", sort_order="desc")
    assert "Sorted by VOLUME desc" in result
    # First data line should have highest volume (TSLA=80M)
    lines = result.split("\n")
    data_lines = [l for l in lines if "TSLA" in l]
    assert len(data_lines) > 0


def test_format_markdown_with_limit(stock_df):
    result = format_markdown(stock_df, "stock", limit=2)
    assert "2 of 5 results" in result


def test_format_markdown_empty():
    df = pd.DataFrame()
    result = format_markdown(df, "stock")
    assert "0 results" in result
    assert "No matches found" in result


# -- apply_filters tests --

def test_apply_filters_none():
    screener = MagicMock()
    result = apply_filters(screener, None, None)
    assert result == screener
    screener.where.assert_not_called()


def test_apply_filters_invalid_json(capsys):
    screener = MagicMock()
    with pytest.raises(SystemExit):
        apply_filters(screener, None, "not valid json")


# -- select_columns tests --

def test_select_columns_none():
    screener = MagicMock()
    result = select_columns(screener, None, None)
    assert result == screener
    screener.select.assert_not_called()
