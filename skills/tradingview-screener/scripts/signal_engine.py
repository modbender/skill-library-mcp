"""YAML-driven signal engine. Loads signal configs, runs screener, applies computed signals."""
import argparse
import json
import sys
import os
from pathlib import Path

import yaml

sys.path.insert(0, os.path.dirname(__file__))
from screener_constants import SCREENER_MAP, OP_MAP, resolve_field, find_df_column
from signal_types import apply_computed_signals

# Default signals directory relative to skill root
SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SIGNALS_DIR = SKILL_ROOT / "state" / "signals"


def load_signal(signal_path):
    """Load and validate a YAML signal config file."""
    path = Path(signal_path)
    if not path.exists():
        # Try as name in default signals dir
        path = DEFAULT_SIGNALS_DIR / f"{signal_path}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Signal config not found: {signal_path}")

    with open(path) as f:
        config = yaml.safe_load(f)

    if not config or "name" not in config or "asset_class" not in config:
        raise ValueError(f"Invalid signal config: missing 'name' or 'asset_class' in {path}")
    return config


def list_signals(signals_dir=None):
    """List available signal configs as markdown table."""
    sig_dir = Path(signals_dir) if signals_dir else DEFAULT_SIGNALS_DIR
    if not sig_dir.exists():
        print("No signals directory found.")
        return

    yamls = sorted(sig_dir.glob("*.yaml"))
    if not yamls:
        print("No signal configs found.")
        return

    print("| Signal | Description | Asset | Types |")
    print("|--------|-------------|-------|-------|")
    for yf in yamls:
        try:
            with open(yf) as f:
                cfg = yaml.safe_load(f)
            name = cfg.get("name", yf.stem)
            desc = cfg.get("description", "")[:60]
            asset = cfg.get("asset_class", "?")
            types = ", ".join(c.get("type", "?") for c in cfg.get("computed", []))
            print(f"| {name} | {desc} | {asset} | {types} |")
        except Exception as e:
            print(f"| {yf.stem} | Error: {e} | ? | ? |")


def build_and_run(config):
    """Build screener from config, fetch data, apply computed signals, output markdown."""
    asset_class = config["asset_class"]
    if asset_class not in SCREENER_MAP:
        raise ValueError(f"Unknown asset class: {asset_class}. Options: {list(SCREENER_MAP.keys())}")

    screener_cls, field_enum = SCREENER_MAP[asset_class]
    screener = screener_cls()

    # Only apply with_interval for non-daily timeframes (daily is default)
    timeframe = config.get("timeframe")
    use_interval = timeframe and timeframe not in ("1D", "1d")

    # Apply API pre-filters
    for f in config.get("filters", []):
        field = resolve_field(field_enum, f["field"])
        op = f.get("op", ">")
        value = f["value"]
        if op not in OP_MAP:
            raise ValueError(f"Unknown operator: {op}")
        if use_interval and hasattr(field, "with_interval"):
            try:
                field = field.with_interval(timeframe)
            except Exception:
                pass
        screener.where(OP_MAP[op](field, value))

    # Select columns
    columns = config.get("columns", [])
    if columns:
        fields = []
        for name in columns:
            fld = resolve_field(field_enum, name)
            if use_interval and hasattr(fld, "with_interval"):
                try:
                    fld = fld.with_interval(timeframe)
                except Exception:
                    pass
            fields.append(fld)
        screener.select(*fields)

    # Fetch data
    df = screener.get()
    total_rows = len(df)

    # Apply computed signals (post-filter)
    computed = config.get("computed", [])
    df = apply_computed_signals(df, computed)

    # Sort
    sort_by = config.get("sort_by")
    if sort_by:
        col = find_df_column(df, sort_by)
        if col:
            ascending = config.get("sort_order", "desc").lower() == "asc"
            df = df.sort_values(by=col, ascending=ascending)

    # Limit
    limit = config.get("limit", 50)
    df = df.head(limit)

    # Format output
    sig_name = config.get("name", "Signal")
    sig_desc = config.get("description", "")
    header = f"**{sig_name}** — {sig_desc}" if sig_desc else f"**{sig_name}**"
    types_used = ", ".join(c.get("type", "?") for c in computed) if computed else "none"
    summary = f"{header}\n{len(df)} matches from {total_rows} rows | Signals: {types_used}"

    try:
        table = df.to_markdown(index=False)
    except ImportError:
        table = df.to_string(index=False)

    print(f"{summary}\n\n{table}")


def main():
    parser = argparse.ArgumentParser(description="TradingView Signal Engine")
    parser.add_argument("--signal", default=None,
                        help="Signal name (from state/signals/) or path to YAML file")
    parser.add_argument("--list", action="store_true",
                        help="List available signal configs")
    parser.add_argument("--signals-dir", default=None,
                        help="Override signals directory path")
    args = parser.parse_args()

    if args.list:
        list_signals(args.signals_dir)
        return

    if not args.signal:
        parser.print_help()
        sys.exit(1)

    try:
        config = load_signal(args.signal)
        build_and_run(config)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Signal engine failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
