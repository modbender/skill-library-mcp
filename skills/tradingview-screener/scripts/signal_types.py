"""Signal type implementations for computed post-filter signals.

Each function takes a DataFrame + config dict, returns filtered DataFrame.
4 signal types: crossover, threshold, expression, range.
"""
import re
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from screener_constants import find_df_column


# Whitelist for expression validation: column ops, basic math, comparisons
EXPR_ALLOWED_PATTERN = re.compile(
    r"^[A-Za-z0-9_\s\.\+\-\*\/\>\<\=\!\(\)\,\%]+$"
)
EXPR_BLOCKED_KEYWORDS = {"import", "exec", "eval", "__", "open", "os", "sys", "lambda"}


def validate_expression(expr):
    """Validate expression string against whitelist rules.

    Allows: column names, basic operators (+,-,*,/,>,<,>=,<=,==,!=,and,or,not),
    numeric literals, .mean(), .std(), .sum(), .min(), .max()
    """
    if not EXPR_ALLOWED_PATTERN.match(expr):
        raise ValueError(f"Expression contains disallowed characters: {expr}")
    words = set(re.findall(r"[a-zA-Z_]\w*", expr.lower()))
    blocked = words & EXPR_BLOCKED_KEYWORDS
    if blocked:
        raise ValueError(f"Expression contains blocked keywords: {blocked}")


def apply_crossover(df, config):
    """Detect when fast field is above/below slow field.

    Config keys: fast (column), slow (column), direction (up|down|both)
    """
    fast = find_df_column(df, config["fast"])
    slow = find_df_column(df, config["slow"])
    direction = config.get("direction", "up")

    if not fast or not slow:
        print(f"Warning: Crossover columns not found in DataFrame. "
              f"Available: {list(df.columns)}", file=sys.stderr)
        return df

    if direction == "up":
        mask = df[fast] > df[slow]
    elif direction == "down":
        mask = df[fast] < df[slow]
    else:  # both
        mask = df[fast] != df[slow]

    return df[mask].copy()


def apply_threshold(df, config):
    """Filter rows where field crosses a threshold value.

    Config keys: field (column), op (comparison), value (number)
    """
    col = find_df_column(df, config["field"])
    op = config.get("op", ">")
    value = config["value"]

    if not col:
        print(f"Warning: Threshold field '{config['field']}' not in DataFrame. "
              f"Available: {list(df.columns)}", file=sys.stderr)
        return df

    ops = {
        ">": lambda: df[col] > value,
        ">=": lambda: df[col] >= value,
        "<": lambda: df[col] < value,
        "<=": lambda: df[col] <= value,
        "==": lambda: df[col] == value,
        "!=": lambda: df[col] != value,
    }
    if op not in ops:
        raise ValueError(f"Unknown threshold operator: {op}")

    return df[ops[op]()].copy()


def apply_expression(df, config):
    """Evaluate a pandas expression on the DataFrame.

    Config keys: expr (pandas eval string)
    Uses df.eval() which is sandboxed to DataFrame operations.
    Resolves enum-style field names to actual DataFrame column names.
    """
    expr = config["expr"]
    validate_expression(expr)
    # Resolve field names in expression to actual DataFrame column names
    resolved_expr = _resolve_expr_columns(df, expr)
    try:
        mask = df.eval(resolved_expr)
        return df[mask].copy()
    except Exception as e:
        print(f"Warning: Expression '{resolved_expr}' failed: {e}", file=sys.stderr)
        return df


def _resolve_expr_columns(df, expr):
    """Replace enum-style field names in expression with actual DataFrame column names."""
    # Find all potential column references (uppercase words with underscores)
    # Sort by length descending to avoid partial replacements
    # e.g., AVERAGE_VOLUME_30_DAY must be replaced before VOLUME
    tokens = sorted(set(re.findall(r"[A-Z][A-Z0-9_]+", expr)), key=len, reverse=True)
    for token in tokens:
        col = find_df_column(df, token)
        if col and col != token:
            # Use word-boundary replacement to avoid partial matches
            expr = re.sub(r"\b" + re.escape(token) + r"\b", f"`{col}`", expr)
    return expr


def apply_range(df, config):
    """Filter rows where field is between min and max (inclusive).

    Config keys: field (column), min (number), max (number)
    """
    col = find_df_column(df, config["field"])
    min_val = config["min"]
    max_val = config["max"]

    if not col:
        print(f"Warning: Range field '{config['field']}' not in DataFrame. "
              f"Available: {list(df.columns)}", file=sys.stderr)
        return df

    mask = (df[col] >= min_val) & (df[col] <= max_val)
    return df[mask].copy()


# Dispatcher mapping signal type string to handler function
SIGNAL_TYPE_MAP = {
    "crossover": apply_crossover,
    "threshold": apply_threshold,
    "expression": apply_expression,
    "range": apply_range,
}


def apply_computed_signals(df, computed_list):
    """Apply a list of computed signal configs to a DataFrame (AND chain).

    Args:
        df: Input DataFrame from tvscreener
        computed_list: List of signal config dicts, each with 'type' key

    Returns:
        Filtered DataFrame after all signals applied
    """
    if not computed_list:
        return df

    total_before = len(df)
    for signal in computed_list:
        sig_type = signal.get("type")
        if sig_type not in SIGNAL_TYPE_MAP:
            raise ValueError(
                f"Unknown signal type '{sig_type}'. "
                f"Available: {list(SIGNAL_TYPE_MAP.keys())}"
            )
        handler = SIGNAL_TYPE_MAP[sig_type]
        df = handler(df, signal)

    print(f"Signals: {total_before} → {len(df)} rows after filtering", file=sys.stderr)
    return df
