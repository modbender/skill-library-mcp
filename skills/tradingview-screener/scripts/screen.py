"""TradingView market screener CLI. Fetches filtered data and outputs markdown."""
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from screener_constants import SCREENER_MAP, OP_MAP, resolve_field, find_df_column


def apply_filters(screener, field_enum, filters_json, timeframe=None):
    """Apply JSON filter specs to a screener via .where() chains."""
    if not filters_json:
        return screener
    try:
        filters = json.loads(filters_json) if isinstance(filters_json, str) else filters_json
    except json.JSONDecodeError as e:
        print(f"Error: Invalid filter JSON: {e}", file=sys.stderr)
        sys.exit(1)

    for f in filters:
        field = resolve_field(field_enum, f["field"])
        op = f.get("op", ">")
        value = f["value"]
        if op not in OP_MAP:
            print(f"Error: Unknown operator '{op}'", file=sys.stderr)
            sys.exit(1)
        if timeframe and timeframe not in ("1D", "1d") and hasattr(field, "with_interval"):
            try:
                field = field.with_interval(timeframe)
            except Exception:
                pass  # Not all fields support intervals
        screener.where(OP_MAP[op](field, value))
    return screener


def select_columns(screener, field_enum, columns_str, timeframe=None):
    """Select columns on a screener from comma-separated field names."""
    if not columns_str:
        return screener
    names = [c.strip() for c in columns_str.split(",") if c.strip()]
    fields = []
    for name in names:
        field = resolve_field(field_enum, name)
        if timeframe and timeframe not in ("1D", "1d") and hasattr(field, "with_interval"):
            try:
                field = field.with_interval(timeframe)
            except Exception:
                pass
        fields.append(field)
    if fields:
        screener.select(*fields)
    return screener


def format_markdown(df, asset_class, sort_by=None, sort_order="desc", limit=50):
    """Format DataFrame as markdown table with summary line."""
    if df.empty:
        return f"**{asset_class.title()} Screener** | 0 results\n\nNo matches found."

    if sort_by:
        col = find_df_column(df, sort_by)
        if col:
            ascending = sort_order.lower() == "asc"
            df = df.sort_values(by=col, ascending=ascending)

    total = len(df)
    df = df.head(limit)

    try:
        table = df.to_markdown(index=False)
    except ImportError:
        # Fallback if tabulate not installed
        table = df.to_string(index=False)

    sort_info = f"Sorted by {sort_by} {sort_order}" if sort_by else "Default order"
    summary = f"**{asset_class.title()} Screener** | {len(df)} of {total} results | {sort_info}"
    return f"{summary}\n\n{table}"


def main():
    parser = argparse.ArgumentParser(description="TradingView Market Screener")
    parser.add_argument("--asset-class", default="stock",
                        choices=list(SCREENER_MAP.keys()),
                        help="Asset class to screen")
    parser.add_argument("--filters", default=None,
                        help='JSON filter array, e.g. \'[{"field":"PRICE","op":">","value":50}]\'')
    parser.add_argument("--columns", default=None,
                        help="Comma-separated column names")
    parser.add_argument("--sort-by", default=None,
                        help="Column name to sort by")
    parser.add_argument("--sort-order", default="desc", choices=["asc", "desc"])
    parser.add_argument("--limit", type=int, default=50,
                        help="Max results to display")
    parser.add_argument("--timeframe", default=None,
                        help="Interval for technical fields (1,5,15,30,60,120,240,1D,1W,1M)")
    parser.add_argument("--market", default=None,
                        help="Market filter (e.g. america, europe)")
    args = parser.parse_args()

    try:
        screener_cls, field_enum = SCREENER_MAP[args.asset_class]
        screener = screener_cls()

        if args.market:
            screener.set_markets(args.market)

        apply_filters(screener, field_enum, args.filters, args.timeframe)
        select_columns(screener, field_enum, args.columns, args.timeframe)

        df = screener.get()

        output = format_markdown(df, args.asset_class, args.sort_by, args.sort_order, args.limit)
        print(output)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Screener failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
