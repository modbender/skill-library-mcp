"""Shared constants and helpers for TradingView screener scripts."""
import tvscreener as tvs

# Maps asset class string to (ScreenerClass, FieldEnum) tuple
SCREENER_MAP = {
    "stock": (tvs.StockScreener, tvs.StockField),
    "crypto": (tvs.CryptoScreener, tvs.CryptoField),
    "forex": (tvs.ForexScreener, tvs.ForexField),
    "bond": (tvs.BondScreener, tvs.BondField),
    "futures": (tvs.FuturesScreener, tvs.FuturesField),
    "coin": (tvs.CoinScreener, tvs.CoinField),
}

# Maps operator string to lambda applying the operation on a Field
OP_MAP = {
    ">": lambda f, v: f > v,
    ">=": lambda f, v: f >= v,
    "<": lambda f, v: f < v,
    "<=": lambda f, v: f <= v,
    "==": lambda f, v: f == v,
    "!=": lambda f, v: f != v,
    "between": lambda f, v: f.between(v[0], v[1]),
    "isin": lambda f, v: f.isin(v),
}


def resolve_field(field_enum, field_name):
    """Resolve a field name string to a Field enum instance.

    Args:
        field_enum: The Field enum class (e.g., StockField)
        field_name: String name of the field (case-insensitive)

    Returns:
        Field enum instance

    Raises:
        ValueError: If field name not found in enum
    """
    name_upper = field_name.strip().upper()
    try:
        return getattr(field_enum, name_upper)
    except AttributeError:
        # Try search as fallback
        results = field_enum.search(field_name)
        if results:
            return results[0]
        raise ValueError(
            f"Field '{field_name}' not found in {field_enum.__name__}. "
            f"Use {field_enum.__name__}.search('{field_name}') to discover fields."
        )


def _normalize(s):
    """Normalize a string for fuzzy column matching.

    Strips underscores, parens, percent signs, extra spaces, lowercases.
    E.g., 'SIMPLE_MOVING_AVERAGE_50' → 'simple moving average 50'
          'Simple Moving Average (50)' → 'simple moving average 50'
    """
    import re
    s = s.lower().replace("_", " ").replace("(", " ").replace(")", " ").replace("%", " ")
    return re.sub(r"\s+", " ", s).strip()


def find_df_column(df, name):
    """Find a DataFrame column by name (case-insensitive, normalized match).

    tvscreener returns display names (e.g., 'Volume') not enum names ('VOLUME').
    This helper matches user-provided names against actual DataFrame columns.
    """
    if name in df.columns:
        return name
    # Case-insensitive exact match
    lower_map = {c.lower(): c for c in df.columns}
    if name.lower() in lower_map:
        return lower_map[name.lower()]
    # Normalized match: strip underscores, parens, etc.
    name_norm = _normalize(name)
    for col in df.columns:
        if _normalize(col) == name_norm:
            return col
    # Partial containment match
    for col in df.columns:
        col_norm = _normalize(col)
        if name_norm in col_norm or col_norm in name_norm:
            return col
    return None
