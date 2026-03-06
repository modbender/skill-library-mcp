#!/usr/bin/env python3
"""
Manage LP Rebalancer controllers via hummingbot-api.

Usage:
    # Get LP Rebalancer config template
    python manage_controller.py template

    # Create LP Rebalancer config
    python manage_controller.py create-config my_lp_config --pool <pool_address> --pair SOL-USDC --amount 100

    # List all configs
    python manage_controller.py list-configs

    # Get config details
    python manage_controller.py describe-config my_lp_config

    # Deploy bot with controller
    python manage_controller.py deploy my_bot --configs my_lp_config

    # Get active bots status
    python manage_controller.py status

    # Stop a bot
    python manage_controller.py stop my_bot

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


def get_template(args):
    """Get LP Rebalancer config template."""
    result = api_request("GET", "/controllers/generic/lp_rebalancer/config/template")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("LP Rebalancer Config Template")
        print("-" * 50)
        for field, info in result.items():
            default = info.get("default", "")
            field_type = info.get("type", "")
            required = info.get("required", False)
            req_str = " (required)" if required else ""
            print(f"  {field}: {default} [{field_type}]{req_str}")


def create_config(args):
    """Create LP Rebalancer controller config."""
    config_data = {
        "id": args.config_name,
        "controller_name": "lp_rebalancer",
        "controller_type": "generic",
        "connector_name": args.connector,
        "network": args.network,
        "trading_pair": args.pair,
        "pool_address": args.pool,
        "total_amount_quote": str(args.amount),
        "side": args.side,
        "position_width_pct": str(args.width),
        "position_offset_pct": str(args.offset),
        "rebalance_seconds": args.rebalance_seconds,
        "rebalance_threshold_pct": str(args.rebalance_threshold),
        "strategy_type": args.strategy_type,
    }

    # Add price limits
    config_data["sell_price_max"] = args.sell_max
    config_data["sell_price_min"] = args.sell_min
    config_data["buy_price_max"] = args.buy_max
    config_data["buy_price_min"] = args.buy_min

    # POST /controllers/configs/{config_name} to create/update
    result = api_request("POST", f"/controllers/configs/{args.config_name}", config_data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"✓ Config '{args.config_name}' created")
        print(f"  Pool: {args.pool}")
        print(f"  Pair: {args.pair}")
        print(f"  Amount: {args.amount} (quote)")


def list_configs(args):
    """List all controller configs."""
    result = api_request("GET", "/controllers/configs/")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if not result:
            print("No configs found.")
            return

        print(f"Controller Configs ({len(result)}):")
        print("-" * 80)
        print(f"{'Name':<25} {'Controller':<20} {'Pair':<15} {'Amount'}")
        print("-" * 80)

        for cfg in result:
            name = cfg.get("id", "")[:23]
            controller = cfg.get("controller_name", "")[:18]
            pair = cfg.get("trading_pair", "")[:13]
            amount = cfg.get("total_amount_quote", "")
            print(f"{name:<25} {controller:<20} {pair:<15} {amount}")


def describe_config(args):
    """Get details of a specific config."""
    result = api_request("GET", f"/controllers/configs/{args.config_name}")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Config: {args.config_name}")
        print("-" * 50)
        for key, value in result.items():
            if not key.startswith("_"):
                print(f"  {key}: {value}")


def delete_config(args):
    """Delete a controller config."""
    result = api_request("DELETE", f"/controllers/configs/{args.config_name}")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"✓ Config '{args.config_name}' deleted")


def deploy_bot(args):
    """Deploy bot with controller configs using V2 deployment."""
    data = {
        "instance_name": args.bot_name,
        "controllers_config": args.configs,
        "credentials_profile": args.account,
        "image": args.image,
        "headless": args.headless,
    }

    if args.max_global_drawdown:
        data["max_global_drawdown_quote"] = args.max_global_drawdown
    if args.max_controller_drawdown:
        data["max_controller_drawdown_quote"] = args.max_controller_drawdown
    if args.script_config:
        data["script_config"] = args.script_config

    result = api_request("POST", "/bot-orchestration/deploy-v2-controllers", data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(f"✓ Bot deployed")
            print(f"  Name: {result.get('unique_instance_name', args.bot_name)}")
            print(f"  Controllers: {', '.join(args.configs)}")
            print(f"  Script Config: {result.get('script_config_generated', '')}")
        else:
            print(f"Deployment response: {result}")


def get_status(args):
    """Get active bots status."""
    result = api_request("GET", "/bot-orchestration/status")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        data = result.get("data", result)
        if not data:
            print("No active bots.")
            return

        print("Active Bots:")
        print("-" * 60)

        for bot_name, bot_data in data.items():
            status = bot_data.get("status", "unknown")
            print(f"\n{bot_name} ({status})")

            # Performance data if available
            perf = bot_data.get("performance", {})
            if perf:
                pnl = perf.get("unrealized_pnl_quote", 0)
                rpnl = perf.get("realized_pnl_quote", 0)
                volume = perf.get("volume_traded", 0)
                print(f"  Unrealized PnL: ${pnl:.2f}")
                print(f"  Realized PnL: ${rpnl:.2f}")
                print(f"  Volume: ${volume:.2f}")


def get_bot_status(args):
    """Get specific bot status."""
    result = api_request("GET", f"/bot-orchestration/{args.bot_name}/status")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        data = result.get("data", result)
        print(f"Bot: {args.bot_name}")
        print("-" * 50)
        print(f"  Status: {data.get('status', 'unknown')}")

        perf = data.get("performance", {})
        if perf:
            print(f"  Unrealized PnL: ${perf.get('unrealized_pnl_quote', 0):.2f}")
            print(f"  Realized PnL: ${perf.get('realized_pnl_quote', 0):.2f}")
            print(f"  Volume: ${perf.get('volume_traded', 0):.2f}")


def stop_bot(args):
    """Stop a bot."""
    data = {
        "bot_name": args.bot_name,
        "skip_order_cancellation": args.skip_cancel,
        "async_backend": True,
    }
    result = api_request("POST", "/bot-orchestration/stop-bot", data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        response = result.get("response", result)
        if response.get("success"):
            print(f"✓ Bot '{args.bot_name}' stopped")
        else:
            print(f"Response: {response}")


def stop_and_archive(args):
    """Stop and archive a bot."""
    endpoint = f"/bot-orchestration/stop-and-archive-bot/{args.bot_name}"
    params = []
    if args.skip_cancel:
        params.append("skip_order_cancellation=true")
    if args.s3_bucket:
        params.append(f"s3_bucket={args.s3_bucket}")
        params.append("archive_locally=false")
    else:
        params.append("archive_locally=true")

    if params:
        endpoint += "?" + "&".join(params)

    result = api_request("POST", endpoint)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("status") == "success":
            print(f"✓ Stop and archive initiated for '{args.bot_name}'")
            print(f"  {result.get('message', '')}")
        else:
            print(f"Response: {result}")


def main():
    parser = argparse.ArgumentParser(description="Manage LP Rebalancer controllers via hummingbot-api")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # template command
    template_parser = subparsers.add_parser("template", help="Get LP Rebalancer config template")
    template_parser.add_argument("--json", action="store_true", help="Output as JSON")
    template_parser.set_defaults(func=get_template)

    # create-config command
    create_parser = subparsers.add_parser("create-config", help="Create LP Rebalancer config")
    create_parser.add_argument("config_name", help="Config name")
    create_parser.add_argument("--pool", required=True, help="Pool address (from Meteora UI or list_meteora_pools.py)")
    create_parser.add_argument("--pair", required=True, help="Trading pair matching pool tokens (e.g., SOL-USDC, Percolator-SOL). Use exact token symbols from Gateway.")
    create_parser.add_argument("--connector", default="meteora/clmm", help="Connector name")
    create_parser.add_argument("--network", default="solana-mainnet-beta", help="Network")
    create_parser.add_argument("--amount", type=float, required=True, help="Total amount in QUOTE asset (2nd token in pair). E.g. for Percolator-SOL this is SOL. For SOL-USDC this is USDC.")
    create_parser.add_argument("--side", type=int, default=0, choices=[0, 1, 2], help="Side: 0=BOTH, 1=BUY (quote only), 2=SELL (base only)")
    create_parser.add_argument("--width", type=float, default=10.0, help="Position width in pct (e.g. 10 = 10%% of current price above and below)")
    create_parser.add_argument("--offset", type=float, default=0.1, help="Position offset in pct — how far center of range is from current price (default: 0.1%%)")
    create_parser.add_argument("--rebalance-seconds", type=int, default=300, help="Seconds out-of-range before rebalancing (default: 300)")
    create_parser.add_argument("--rebalance-threshold", type=float, default=1.0, help="Rebalance threshold in pct — minimum price movement to trigger rebalance (default: 1.0)")
    create_parser.add_argument("--sell-max", type=float, default=None, help="Max price for SELL orders (default: null = no limit)")
    create_parser.add_argument("--sell-min", type=float, default=None, help="Min price for SELL orders (default: null = no limit)")
    create_parser.add_argument("--buy-max", type=float, default=None, help="Max price for BUY orders (default: null = no limit)")
    create_parser.add_argument("--buy-min", type=float, default=None, help="Min price for BUY orders (default: null = no limit)")
    create_parser.add_argument("--strategy-type", type=int, default=0, choices=[0, 1, 2], help="Meteora liquidity shape: 0=Spot (uniform), 1=Curve (concentrated center), 2=Bid-Ask (edges)")
    create_parser.add_argument("--json", action="store_true", help="Output as JSON")
    create_parser.set_defaults(func=create_config)

    # list-configs command
    list_configs_parser = subparsers.add_parser("list-configs", help="List controller configs")
    list_configs_parser.add_argument("--json", action="store_true", help="Output as JSON")
    list_configs_parser.set_defaults(func=list_configs)

    # describe-config command
    describe_parser = subparsers.add_parser("describe-config", help="Get config details")
    describe_parser.add_argument("config_name", help="Config name")
    describe_parser.add_argument("--json", action="store_true", help="Output as JSON")
    describe_parser.set_defaults(func=describe_config)

    # delete-config command
    delete_parser = subparsers.add_parser("delete-config", help="Delete a config")
    delete_parser.add_argument("config_name", help="Config name")
    delete_parser.add_argument("--json", action="store_true", help="Output as JSON")
    delete_parser.set_defaults(func=delete_config)

    # deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy bot with controllers")
    deploy_parser.add_argument("bot_name", help="Bot name")
    deploy_parser.add_argument("--configs", nargs="+", required=True, help="Controller config names")
    deploy_parser.add_argument("--account", default="master_account", help="Account name (default: master_account)")
    deploy_parser.add_argument("--image", default="hummingbot/hummingbot:development", help="Docker image")
    deploy_parser.add_argument("--max-global-drawdown", type=float, help="Max global drawdown in quote")
    deploy_parser.add_argument("--max-controller-drawdown", type=float, help="Max controller drawdown in quote")
    deploy_parser.add_argument("--script-config", help="Script config name (auto-generated if not provided)")
    deploy_parser.add_argument("--headless", action="store_true", default=False, help="Run in headless mode")
    deploy_parser.add_argument("--json", action="store_true", help="Output as JSON")
    deploy_parser.set_defaults(func=deploy_bot)

    # status command
    status_parser = subparsers.add_parser("status", help="Get active bots status")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON")
    status_parser.set_defaults(func=get_status)

    # bot-status command
    bot_status_parser = subparsers.add_parser("bot-status", help="Get specific bot status")
    bot_status_parser.add_argument("bot_name", help="Bot name")
    bot_status_parser.add_argument("--json", action="store_true", help="Output as JSON")
    bot_status_parser.set_defaults(func=get_bot_status)

    # stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a bot")
    stop_parser.add_argument("bot_name", help="Bot name")
    stop_parser.add_argument("--skip-cancel", action="store_true", help="Skip order cancellation")
    stop_parser.add_argument("--json", action="store_true", help="Output as JSON")
    stop_parser.set_defaults(func=stop_bot)

    # stop-and-archive command
    archive_parser = subparsers.add_parser("stop-and-archive", help="Stop and archive a bot")
    archive_parser.add_argument("bot_name", help="Bot name")
    archive_parser.add_argument("--skip-cancel", action="store_true", help="Skip order cancellation")
    archive_parser.add_argument("--s3-bucket", help="S3 bucket for archiving (default: local archive)")
    archive_parser.add_argument("--json", action="store_true", help="Output as JSON")
    archive_parser.set_defaults(func=stop_and_archive)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
