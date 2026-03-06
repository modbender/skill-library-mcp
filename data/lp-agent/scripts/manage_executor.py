#!/usr/bin/env python3
"""
Manage LP executors via hummingbot-api.

Usage:
    # Create LP executor
    python manage_executor.py create --pool <pool_address> --pair SOL-USDC --quote-amount 100 --lower 180 --upper 185

    # Get executor status
    python manage_executor.py get <executor_id>

    # List all executors
    python manage_executor.py list [--type lp_executor]

    # Get executor logs
    python manage_executor.py logs <executor_id> [--limit 50]

    # Stop executor
    python manage_executor.py stop <executor_id> [--keep-position]

    # Get executor summary
    python manage_executor.py summary

    # Get held positions summary
    python manage_executor.py positions

    # Get executor config schema
    python manage_executor.py config lp_executor

Environment:
    HUMMINGBOT_API_URL - API base URL (default: http://localhost:8000)
    API_USER - API username (default: admin)
    API_PASS - API password (default: admin)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import base64
from datetime import datetime


def load_env():
    """Load environment from .env files."""
    for path in ["hummingbot-api/.env", os.path.expanduser("~/.hummingbot/.env"), ".env"]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
            break


def get_api_config():
    """Get API configuration from environment."""
    load_env()
    return {
        "url": os.environ.get("HUMMINGBOT_API_URL", "http://localhost:8000"),
        "user": os.environ.get("API_USER", "admin"),
        "password": os.environ.get("API_PASS", "admin"),
    }


def api_request(method: str, endpoint: str, data=None) -> dict:
    """Make authenticated API request."""
    config = get_api_config()
    url = f"{config['url']}{endpoint}"

    # Basic auth
    credentials = base64.b64encode(f"{config['user']}:{config['password']}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"Error: HTTP {e.code} - {e.reason}", file=sys.stderr)
        if error_body:
            try:
                print(json.dumps(json.loads(error_body), indent=2), file=sys.stderr)
            except json.JSONDecodeError:
                print(error_body, file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Cannot connect to API at {config['url']}: {e.reason}", file=sys.stderr)
        sys.exit(1)


def create_executor(args):
    """Create a new LP executor."""
    # LP executor uses 'market' object for connector/pair
    executor_config = {
        "type": "lp_executor",
        "market": {
            "connector_name": args.connector,
            "trading_pair": args.pair,
        },
        "pool_address": args.pool,
        "lower_price": args.lower,
        "upper_price": args.upper,
        "base_amount": args.base_amount,
        "quote_amount": args.quote_amount,
        "side": args.side,
    }

    # Add optional parameters
    if args.auto_close_above is not None:
        executor_config["auto_close_above_range_seconds"] = args.auto_close_above
    if args.auto_close_below is not None:
        executor_config["auto_close_below_range_seconds"] = args.auto_close_below
    if args.strategy_type is not None:
        executor_config["extra_params"] = {"strategyType": args.strategy_type}

    request_data = {
        "executor_config": executor_config,
        "account_name": args.account,
    }

    result = api_request("POST", "/executors/", request_data)
    print(json.dumps(result, indent=2))


def get_executor(args):
    """Get executor status."""
    result = api_request("GET", f"/executors/{args.executor_id}")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Executor: {result.get('executor_id', args.executor_id)}")
        print("-" * 50)
        print(f"  Type: {result.get('executor_type', result.get('type', ''))}")
        print(f"  Status: {result.get('status', '')}")
        print(f"  Trading Pair: {result.get('trading_pair', '')}")
        print(f"  Connector: {result.get('connector_name', '')}")

        custom_info = result.get("custom_info", {})
        if custom_info:
            state = custom_info.get("state", "")
            if state:
                print(f"  State: {state}")
            position_address = custom_info.get("position_address", "")
            if position_address:
                print(f"  Position: {position_address[:20]}...")

        pnl = result.get("net_pnl_quote", result.get("pnl", 0))
        print(f"  PnL: ${pnl:.4f}" if pnl else "  PnL: $0.00")


def list_executors(args):
    """List all executors."""
    # Use POST /executors/search with filter
    filter_request = {
        "limit": args.limit,
    }

    if args.type:
        filter_request["executor_types"] = [args.type]
    if args.status:
        filter_request["status"] = args.status

    result = api_request("POST", "/executors/search", filter_request)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        executors = result.get("data", [])
        pagination = result.get("pagination", {})

        if not executors:
            print("No executors found.")
            return

        print(f"Executors ({pagination.get('total_count', len(executors))} total):")
        print("-" * 110)
        print(f"{'ID':<46} {'Type':<15} {'Status':<12} {'Pair':<15} {'PnL':<10}")
        print("-" * 110)

        for ex in executors:
            ex_id = ex.get("executor_id", "")
            ex_type = ex.get("executor_type", ex.get("type", ""))[:13]
            status = ex.get("status", "")[:10]
            pair = ex.get("trading_pair", "")[:13]
            pnl = ex.get("net_pnl_quote", ex.get("pnl", 0))
            pnl_str = f"${pnl:.2f}" if pnl else "$0.00"
            print(f"{ex_id:<46} {ex_type:<15} {status:<12} {pair:<15} {pnl_str:<10}")


def get_logs(args):
    """Get executor logs."""
    params = [f"limit={args.limit}"]
    if args.level:
        params.append(f"level={args.level}")

    endpoint = f"/executors/{args.executor_id}/logs?{'&'.join(params)}"
    result = api_request("GET", endpoint)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        logs = result.get("logs", [])
        total = result.get("total_count", len(logs))
        print(f"Logs for {args.executor_id} ({total} total, showing {len(logs)}):")
        print("-" * 80)

        for log in logs:
            ts = log.get("timestamp", "")
            level = log.get("level", "INFO")
            msg = log.get("message", str(log))
            print(f"[{ts}] {level}: {msg}")


def stop_executor(args):
    """Stop an executor."""
    data = {"keep_position": args.keep_position}
    result = api_request("POST", f"/executors/{args.executor_id}/stop", data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(f"✓ Executor {args.executor_id} stopped")
            if args.keep_position:
                print("  Position kept on-chain")
            else:
                print("  Position closed")
        else:
            print(f"Response: {result}")


def get_summary(args):
    """Get summary of all executors."""
    result = api_request("GET", "/executors/summary")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Executor Summary")
        print("-" * 40)
        print(f"  Active: {result.get('total_active', 0)}")
        print(f"  Total PnL: ${result.get('total_pnl_quote', 0):.2f}")
        print(f"  Total Volume: ${result.get('total_volume_quote', 0):.2f}")

        by_type = result.get("by_type", {})
        if by_type:
            print("\n  By Type:")
            for t, count in by_type.items():
                print(f"    {t}: {count}")

        by_status = result.get("by_status", {})
        if by_status:
            print("\n  By Status:")
            for s, count in by_status.items():
                print(f"    {s}: {count}")


def get_positions_summary(args):
    """Get summary of held positions from executors stopped with keep_position=True."""
    result = api_request("GET", "/executors/positions/summary")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Positions Summary")
        print("-" * 60)
        print(f"  Total Positions: {result.get('total_positions', 0)}")
        print(f"  Total Realized PnL: ${result.get('total_realized_pnl', 0):.4f}")

        unrealized = result.get('total_unrealized_pnl')
        if unrealized is not None:
            print(f"  Total Unrealized PnL: ${unrealized:.4f}")

        positions = result.get("positions", [])
        if positions:
            print("\n  Positions:")
            print("-" * 60)
            for pos in positions:
                pair = pos.get("trading_pair", "")
                connector = pos.get("connector_name", "")
                net_base = pos.get("net_amount_base", 0)
                realized = pos.get("realized_pnl_quote", 0)
                unrealized = pos.get("unrealized_pnl_quote")
                side = pos.get("position_side", "")

                print(f"    {pair} ({connector})")
                print(f"      Side: {side}, Net Base: {net_base:.6f}")
                print(f"      Realized PnL: ${realized:.4f}", end="")
                if unrealized is not None:
                    print(f", Unrealized: ${unrealized:.4f}")
                else:
                    print()


def get_config_schema(args):
    """Get configuration schema for an executor type."""
    result = api_request("GET", f"/executors/types/{args.executor_type}/config")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Config Schema: {result.get('executor_type', args.executor_type)}")
        print(f"Config Class: {result.get('config_class', '')}")
        print("-" * 60)

        fields = result.get("fields", [])
        if fields:
            print("\nFields:")
            for field in fields:
                name = field.get("name", "")
                ftype = field.get("type", "")
                required = "required" if field.get("required") else "optional"
                default = field.get("default")
                desc = field.get("description", "")

                print(f"  {name} ({ftype}, {required})")
                if default is not None:
                    print(f"    Default: {default}")
                if desc:
                    print(f"    {desc[:60]}...")

        nested = result.get("nested_types", {})
        if nested and not args.brief:
            print("\nNested Types:")
            for type_name, type_info in nested.items():
                print(f"  {type_name}: {type_info.get('description', '')[:50]}")


def main():
    parser = argparse.ArgumentParser(description="Manage LP executors via hummingbot-api")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create command
    create_parser = subparsers.add_parser("create", help="Create LP executor")
    create_parser.add_argument("--pool", required=True, help="Pool address")
    create_parser.add_argument("--pair", required=True, help="Trading pair (e.g., SOL-USDC)")
    create_parser.add_argument("--connector", default="meteora/clmm", help="Connector name (default: meteora/clmm)")
    create_parser.add_argument("--lower", type=float, required=True, help="Lower price bound")
    create_parser.add_argument("--upper", type=float, required=True, help="Upper price bound")
    create_parser.add_argument("--base-amount", type=float, default=0, help="Base token amount (default: 0)")
    create_parser.add_argument("--quote-amount", type=float, default=0, help="Quote token amount")
    create_parser.add_argument("--side", type=int, default=1, choices=[0, 1, 2], help="Side: 0=BOTH, 1=BUY, 2=SELL (default: 1)")
    create_parser.add_argument("--auto-close-above", type=int, help="Auto-close seconds when price above range")
    create_parser.add_argument("--auto-close-below", type=int, help="Auto-close seconds when price below range")
    create_parser.add_argument("--strategy-type", type=int, choices=[0, 1, 2], help="Meteora strategy: 0=Spot, 1=Curve, 2=Bid-Ask")
    create_parser.add_argument("--account", default="master_account", help="Account name (default: master_account)")
    create_parser.set_defaults(func=create_executor)

    # get command
    get_parser = subparsers.add_parser("get", help="Get executor status")
    get_parser.add_argument("executor_id", help="Executor ID")
    get_parser.add_argument("--json", action="store_true", help="Output as JSON")
    get_parser.set_defaults(func=get_executor)

    # list command
    list_parser = subparsers.add_parser("list", help="List executors")
    list_parser.add_argument("--type", help="Filter by executor type (e.g., lp_executor)")
    list_parser.add_argument("--status", help="Filter by status (e.g., RUNNING, TERMINATED)")
    list_parser.add_argument("--limit", type=int, default=50, help="Max results (default: 50)")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    list_parser.set_defaults(func=list_executors)

    # logs command
    logs_parser = subparsers.add_parser("logs", help="Get executor logs")
    logs_parser.add_argument("executor_id", help="Executor ID")
    logs_parser.add_argument("--limit", type=int, default=50, help="Number of log entries (default: 50)")
    logs_parser.add_argument("--level", choices=["ERROR", "WARNING", "INFO", "DEBUG"], help="Filter by log level")
    logs_parser.add_argument("--json", action="store_true", help="Output as JSON")
    logs_parser.set_defaults(func=get_logs)

    # stop command
    stop_parser = subparsers.add_parser("stop", help="Stop executor")
    stop_parser.add_argument("executor_id", help="Executor ID")
    stop_parser.add_argument("--keep-position", action="store_true", help="Keep position on-chain (don't close)")
    stop_parser.add_argument("--json", action="store_true", help="Output as JSON")
    stop_parser.set_defaults(func=stop_executor)

    # summary command
    summary_parser = subparsers.add_parser("summary", help="Get executor summary")
    summary_parser.add_argument("--json", action="store_true", help="Output as JSON")
    summary_parser.set_defaults(func=get_summary)

    # positions command
    positions_parser = subparsers.add_parser("positions", help="Get held positions summary")
    positions_parser.add_argument("--json", action="store_true", help="Output as JSON")
    positions_parser.set_defaults(func=get_positions_summary)

    # config command
    config_parser = subparsers.add_parser("config", help="Get executor config schema")
    config_parser.add_argument("executor_type", help="Executor type: position_executor, grid_executor, dca_executor, arbitrage_executor, twap_executor, xemm_executor, order_executor")
    config_parser.add_argument("--json", action="store_true", help="Output as JSON")
    config_parser.add_argument("--brief", action="store_true", help="Show brief output (skip nested types)")
    config_parser.set_defaults(func=get_config_schema)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
