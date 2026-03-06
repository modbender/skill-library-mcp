#!/usr/bin/env python3
"""
PolyClaw API Bridge — CLI interface for Wells TG Bot integration.
Called via SSH from Wells TG Bot to interact with portfolio_tracker + trade systems.

Usage:
    python3 polyclaw_api.py portfolio          # JSON: all open positions with live prices
    python3 polyclaw_api.py summary            # Text summary
    python3 polyclaw_api.py balance            # CLOB + wallet balance
    python3 polyclaw_api.py risk               # Current risk rules
    python3 polyclaw_api.py risk_check <usd> <slug> <channel>  # Pre-trade risk check
    python3 polyclaw_api.py swap auto          # Swap all non-USDC.e to USDC.e
    python3 polyclaw_api.py swap status        # Show token balances
"""
import json
import sys
import os
import traceback
from pathlib import Path
from datetime import datetime, timezone

# Ensure .env is loaded
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from portfolio_tracker import PortfolioTracker

GAMMA_API = "https://gamma-api.polymarket.com"


def cmd_portfolio():
    """Return all positions from on-chain Data API (SSoT) + local cost basis."""
    from portfolio_live import print_portfolio
    print_portfolio()


def cmd_summary():
    """Text summary of portfolio."""
    pt = PortfolioTracker()
    print(pt.summary())
    print()
    for slug, pos in pt.get_open_positions().items():
        print("  " + pos["question"][:50])
        print("    %s %.1f @ $%.3f | $%.2f | %s" % (
            pos["side"], pos["tokens"], pos["avg_price"], pos["total_cost"], pos["channel"]))



DATA_API = "https://data-api.polymarket.com"
WALLET_ADDR = "0x2aacf919270Ae303fD3FE8e27D96CBA250936B9F"


CLOB_API = "https://clob.polymarket.com"


def _fetch_data_api_positions() -> dict:
    """Fetch all active positions from Polymarket Data API.
    Returns {slug: live_data}. Note: same slug may appear with multiple outcomes (YES+NO).
    In that case, we return the position with the higher currentValue.
    """
    import urllib.request
    live = {}
    try:
        url = f"{DATA_API}/positions?user={WALLET_ADDR}&limit=500"
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            batch = json.loads(resp.read())
        for item in batch:
            slug = item.get("slug", "")
            if not slug:
                continue
            # If duplicate slug, keep whichever has higher value
            if slug not in live or float(item.get("currentValue", 0)) > float(live[slug].get("currentValue", 0)):
                live[slug] = item
    except Exception as e:
        print(f"[data_api] warning: {e}", file=sys.stderr)
    return live


def _fetch_data_api_total_value() -> float:
    """Fetch canonical total position value from Data API /value endpoint."""
    import urllib.request
    try:
        url = f"{DATA_API}/value?user={WALLET_ADDR}"
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        if data and isinstance(data, list):
            return float(data[0].get("value", 0))
    except Exception as e:
        print(f"[data_api/value] warning: {e}", file=sys.stderr)
    return 0.0


def cmd_positions_json():
    """Return open positions as JSON with live prices for Wells TG Bot integration."""
    pt = PortfolioTracker()
    open_pos = pt.get_open_positions()

    # Fetch live data from Polymarket Data API
    live = _fetch_data_api_positions()

    positions = []
    total_cost = 0
    total_value = 0

    for slug, pos in open_pos.items():
        side = pos.get('side', 'YES').upper()
        tokens = float(pos.get('tokens', 0))
        avg_price = float(pos.get('avg_price', 0))
        cost = float(pos.get('total_cost', 0))

        # Use Data API live data if available
        lp = live.get(slug)
        if lp:
            cur_price = float(lp.get('curPrice', 0))
            current_value = float(lp.get('currentValue', 0))
            pnl = float(lp.get('cashPnl', 0))
            pnl_pct = float(lp.get('percentPnl', 0))
            end_date = lp.get('endDate', pos.get('end_date', ''))
        else:
            cur_price = None
            current_value = None
            pnl = None
            pnl_pct = None
            end_date = pos.get('end_date', '')

        total_cost += cost
        if current_value is not None:
            total_value += current_value

        positions.append({
            'slug': slug,
            'question': pos.get('question', lp.get('title', '') if lp else ''),
            'side': side,
            'tokens': tokens,
            'avg_price': avg_price,
            'total_cost': cost,
            'cur_price': cur_price,
            'current_value': current_value,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'channel': pos.get('channel', ''),
            'status': pos.get('status', 'open'),
            'end_date': end_date,
        })

    # Separate active (in Data API) vs settled (not in Data API)
    live_cost = sum(float(p["total_cost"]) for p in positions if p["pnl"] is not None)
    settled_cost = sum(float(p["total_cost"]) for p in positions if p["pnl"] is None)
    live_count = sum(1 for p in positions if p["pnl"] is not None)
    settled_count = sum(1 for p in positions if p["pnl"] is None)

    # Canonical total position value from Data API /value endpoint (SSoT)
    canonical_value = _fetch_data_api_total_value()
    live_pnl = round(total_value - live_cost, 2) if live_cost > 0 else None
    live_pnl_pct = round(live_pnl / live_cost * 100, 1) if live_cost > 0 and live_pnl is not None else None

    stats = pt.summary_dict() if hasattr(pt, "summary_dict") else {}
    print(json.dumps({
        "positions": positions,
        "count": len(positions),
        "total_cost": round(total_cost, 2),
        "total_value": round(total_value, 2),
        "canonical_value": round(canonical_value, 2),
        "live_cost": round(live_cost, 2),
        "live_count": live_count,
        "settled_cost": round(settled_cost, 2),
        "settled_count": settled_count,
        "total_pnl": live_pnl,
        "total_pnl_pct": live_pnl_pct,
        "stats": stats,
    }, indent=2))

def cmd_balance():
    """Get CLOB balance + wallet token balances."""
    from py_clob_client.client import ClobClient
    from py_clob_client.clob_types import BalanceAllowanceParams
    from web3 import Web3

    host = "https://clob.polymarket.com"
    chain_id = 137
    pk = os.environ.get("POLYCLAW_PRIVATE_KEY", "")

    wallet_addr = "0x2aacf919270Ae303fD3FE8e27D96CBA250936B9F"
    clob = ClobClient(host, key=pk, chain_id=chain_id, signature_type=0, funder=wallet_addr)
    creds = clob.create_or_derive_api_creds()
    clob.set_api_creds(creds)
    params = BalanceAllowanceParams(asset_type="COLLATERAL", signature_type=0)
    bal = clob.get_balance_allowance(params)
    clob_balance = float(bal.get("balance", 0)) / 1e6 if bal else 0

    # Wallet balances
    rpc_url = os.environ.get("CHAINSTACK_NODE", "https://polygon-rpc.com")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    wallet = w3.eth.account.from_key(pk).address

    tokens = {
        "USDC.e": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        "USDC": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
    }

    erc20_abi = [{"constant": True, "inputs": [{"name": "", "type": "address"}],
                  "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
                  "type": "function"},
                 {"constant": True, "inputs": [], "name": "decimals",
                  "outputs": [{"name": "", "type": "uint8"}], "type": "function"}]

    wallet_balances = {}
    for name, addr in tokens.items():
        try:
            contract = w3.eth.contract(address=Web3.to_checksum_address(addr), abi=erc20_abi)
            raw = contract.functions.balanceOf(Web3.to_checksum_address(wallet)).call()
            decimals = contract.functions.decimals().call()
            wallet_balances[name] = raw / (10 ** decimals)
        except Exception:
            wallet_balances[name] = 0

    pol_balance = w3.eth.get_balance(Web3.to_checksum_address(wallet)) / 1e18

    print(json.dumps({
        "clob_balance": round(clob_balance, 2),
        "wallet": wallet_balances,
        "pol": round(pol_balance, 4),
        "wallet_address": wallet,
    }, indent=2))


def cmd_risk():
    """Show current risk rules."""
    pt = PortfolioTracker()
    print(json.dumps(pt.data.get("risk_rules", {}), indent=2))


def cmd_risk_check(amount_str, slug, channel):
    """Pre-trade risk check."""
    pt = PortfolioTracker()
    amount = float(amount_str)

    # Get CLOB balance for reserve check
    try:
        from py_clob_client.client import ClobClient
        pk = os.environ.get("POLYCLAW_PRIVATE_KEY", "")
        wallet_addr = "0x2aacf919270Ae303fD3FE8e27D96CBA250936B9F"
        clob = ClobClient("https://clob.polymarket.com", key=pk, chain_id=137,
                           signature_type=0, funder=wallet_addr)
        creds = clob.create_or_derive_api_creds()
        clob.set_api_creds(creds)
        bal = clob.get_balance_allowance()
        clob_balance = float(bal.get("balance", 0)) / 1e6
    except Exception:
        clob_balance = 999  # Fallback: don't block on balance check failure

    ok, reason = pt.check_risk(amount, slug, channel, clob_balance)
    print(json.dumps({"ok": ok, "reason": reason, "clob_balance": round(clob_balance, 2)}))


def cmd_intel(themes_arg: str = ""):
    """Fetch geo-political + market news relevant to open positions."""
    sys.path.insert(0, str(Path(__file__).parent))
    from polyclaw_intel import fetch_intel
    themes = [t.strip() for t in themes_arg.split(",") if t.strip()] if themes_arg else None
    data = fetch_intel(focus_themes=themes)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_swap(action):
    """Delegate to swap.py."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "swap.py"), action],
        capture_output=True, text=True, timeout=120,
        env={**os.environ},
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)



def cmd_backfill_tokens():
    """Backfill missing token_ids in portfolio tracker from Gamma API."""
    import urllib.request
    pt = PortfolioTracker()
    positions = pt.data.get("positions", {})
    updated = 0
    failed = 0

    for slug, pos in positions.items():
        if pos.get("token_id"):
            continue  # Already has token_id, skip

        side = pos.get("side", "YES").upper()
        try:
            url = f"https://gamma-api.polymarket.com/markets?slug={slug}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
            if not data:
                failed += 1
                continue
            m = data[0]
            token_ids = json.loads(m.get("clobTokenIds", '["",""]'))
            yes_token = token_ids[0] if len(token_ids) > 0 else ""
            no_token = token_ids[1] if len(token_ids) > 1 else ""
            token_id = yes_token if side == "YES" else no_token
            market_id = str(m.get("id", ""))

            if token_id:
                pos["token_id"] = token_id
                if not pos.get("market_id"):
                    pos["market_id"] = market_id
                if not pos.get("end_date"):
                    pos["end_date"] = m.get("endDate", "")
                updated += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1

    if updated > 0:
        pt._save()

    print(json.dumps({
        "updated": updated,
        "failed": failed,
        "skipped": sum(1 for p in positions.values() if p.get("token_id")),
        "total": len(positions),
    }))


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 polyclaw_api.py <command> [args]")
        print("Commands: portfolio, summary, balance, risk, risk_check, swap")
        sys.exit(1)

    cmd = sys.argv[1]

    try:
        if cmd == "portfolio":
            cmd_portfolio()
        elif cmd == "summary":
            cmd_summary()
        elif cmd == "positions_json":
            cmd_positions_json()
        elif cmd == "balance":
            cmd_balance()
        elif cmd == "risk":
            cmd_risk()
        elif cmd == "risk_check":
            if len(sys.argv) < 5:
                print(json.dumps({"ok": False, "reason": "Usage: risk_check <amount> <slug> <channel>"}))
                sys.exit(1)
            cmd_risk_check(sys.argv[2], sys.argv[3], sys.argv[4])
        elif cmd == "intel":
            themes_arg = sys.argv[2] if len(sys.argv) > 2 else ""
            cmd_intel(themes_arg)
        elif cmd == "swap":
            action = sys.argv[2] if len(sys.argv) > 2 else "status"
            cmd_swap(action)
        elif cmd == "backfill_tokens":
            cmd_backfill_tokens()
        else:
            print(json.dumps({"error": f"Unknown command: {cmd}"}))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e), "traceback": traceback.format_exc()}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
