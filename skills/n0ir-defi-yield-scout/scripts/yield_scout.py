#!/usr/bin/env python3
"""DeFi Yield Scout — USDC yield farming scanner for Base & Arbitrum.

Uses DeFiLlama's free API. Stdlib only (no pip installs).
"""

import argparse
import json
import math
import os
import ssl
import sys
import tempfile
import time
import urllib.request

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

POOLS_URL = "https://yields.llama.fi/pools"
CHART_URL = "https://yields.llama.fi/chart/{pool_id}"

CACHE_PATH = os.path.join(tempfile.gettempdir(), "yield_scout_pools.json")
CACHE_TTL = 900  # 15 minutes

CHAINS = {"base": "Base", "arbitrum": "Arbitrum"}

USDC_ADDRESSES = {
    "Base": ["0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"],
    "Arbitrum": [
        "0xaf88d065e77c8cc2239327c5edb3a432268e5831",
        "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8",
    ],
}

WHITELISTED_PROTOCOLS = {
    "morpho-v1",
    "euler-v2",
    "lazy-summer-protocol",
    "silo-v2",
    "moonwell-lending",
    "compound-v3",
    "aave-v3",
    "harvest-finance",
    "40-acres",
    "wasabi-protocol",
    "yo-protocol",
}

# Breakeven cost assumptions (fraction of amount)
COST_SAME_CHAIN = 0.01
COST_CROSS_CHAIN = 0.03

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

_ssl_ctx = None


def _get_ssl_ctx():
    global _ssl_ctx
    if _ssl_ctx is None:
        _ssl_ctx = ssl.create_default_context()
    return _ssl_ctx


def fetch_json(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "yield-scout/1.0"})
    with urllib.request.urlopen(req, context=_get_ssl_ctx(), timeout=timeout) as resp:
        return json.loads(resp.read().decode())


# ---------------------------------------------------------------------------
# Pool cache
# ---------------------------------------------------------------------------


def load_pools(force=False):
    if not force and os.path.exists(CACHE_PATH):
        age = time.time() - os.path.getmtime(CACHE_PATH)
        if age < CACHE_TTL:
            with open(CACHE_PATH, "r") as f:
                return json.load(f)

    print("Fetching pool data from DeFiLlama (this may take a moment)...", file=sys.stderr)
    data = fetch_json(POOLS_URL, timeout=120)
    pools = data.get("data", data) if isinstance(data, dict) else data

    with open(CACHE_PATH, "w") as f:
        json.dump(pools, f)

    return pools


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def is_usdc_pool(pool):
    """Check if pool is a USDC pool on a whitelisted chain + protocol."""
    chain = pool.get("chain", "")
    if chain not in CHAINS.values():
        return False

    project = pool.get("project", "")
    if project not in WHITELISTED_PROTOCOLS:
        return False

    # Must be stablecoin
    if not pool.get("stablecoin", False):
        return False

    # Check symbol contains USDC
    symbol = (pool.get("symbol") or "").upper()
    if "USDC" not in symbol:
        return False

    # Prefer single-exposure pools (no multi-asset LP)
    exposure = pool.get("exposure", "single")
    if exposure == "multi":
        return False

    return True


def filter_pools(pools, chain=None, protocol=None, min_tvl=0):
    results = []
    for p in pools:
        if not is_usdc_pool(p):
            continue
        if chain and p.get("chain", "").lower() != chain.lower():
            continue
        if protocol and p.get("project", "") != protocol:
            continue
        tvl = p.get("tvlUsd", 0) or 0
        if tvl < min_tvl:
            continue
        results.append(p)

    results.sort(key=lambda x: x.get("apy", 0) or 0, reverse=True)
    return results


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def fmt_usd(val):
    if val is None:
        return "N/A"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1_000_000_000:
        return f"{sign}${abs_val / 1_000_000_000:.1f}B"
    if abs_val >= 1_000_000:
        return f"{sign}${abs_val / 1_000_000:.1f}M"
    if abs_val >= 1_000:
        return f"{sign}${abs_val / 1_000:.1f}K"
    return f"{sign}${abs_val:.0f}"


def fmt_pct(val):
    if val is None:
        return "N/A"
    return f"{val:.2f}%"


def risk_score(pool):
    tvl = pool.get("tvlUsd", 0) or 0
    il_risk = pool.get("ilRisk", "no")
    pred = pool.get("predictions", {}) or {}
    pred_class = pred.get("predictedClass", "")

    if tvl < 500_000 or il_risk == "yes":
        return "HIGH"
    if tvl < 5_000_000 or pred_class in ("Down", ""):
        return "MED"
    return "LOW"


def short_id(pool_id):
    if pool_id and len(pool_id) > 12:
        return pool_id[:12] + "..."
    return pool_id or ""


def sparkline(values):
    if not values:
        return ""
    bars = " \u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"
    lo = min(values)
    hi = max(values)
    rng = hi - lo if hi != lo else 1
    return "".join(bars[min(int((v - lo) / rng * 7) + 1, 8)] for v in values)


# ---------------------------------------------------------------------------
# Subcommand: scan
# ---------------------------------------------------------------------------


def cmd_scan(args):
    pools = load_pools()
    filtered = filter_pools(
        pools,
        chain=args.chain,
        protocol=args.protocol,
        min_tvl=args.min_tvl,
    )

    top = args.top or 20
    filtered = filtered[:top]

    if not filtered:
        print("No USDC pools found matching your filters.")
        return

    if args.json:
        out = []
        for p in filtered:
            out.append({
                "pool": p.get("pool"),
                "project": p.get("project"),
                "chain": p.get("chain"),
                "symbol": p.get("symbol"),
                "apy": p.get("apy"),
                "apyBase": p.get("apyBase"),
                "apyReward": p.get("apyReward"),
                "tvlUsd": p.get("tvlUsd"),
                "risk": risk_score(p),
            })
        print(json.dumps(out, indent=2))
        return

    chains_label = args.chain or "Base + Arbitrum"
    print(f"\nDeFi Yield Scout \u2014 USDC Opportunities ({chains_label})")
    print("\u2501" * 100)
    hdr = f" {'#':>2}  {'Protocol':<20} {'Chain':<10} {'Pool':<24} {'APY':>7}  {'TVL':>9}  {'Risk':<5}  Pool ID"
    print(hdr)
    print("\u2501" * 100)

    for i, p in enumerate(filtered, 1):
        row = (
            f" {i:>2}  "
            f"{p.get('project', ''):<20} "
            f"{p.get('chain', ''):<10} "
            f"{(p.get('symbol') or '')[:24]:<24} "
            f"{fmt_pct(p.get('apy')):>7}  "
            f"{fmt_usd(p.get('tvlUsd')):>9}  "
            f"{risk_score(p):<5}  "
            f"{short_id(p.get('pool'))}"
        )
        print(row)

    print(f"\n{len(filtered)} pools shown. Use pool IDs with 'breakeven' or 'history' commands.")


# ---------------------------------------------------------------------------
# Subcommand: breakeven
# ---------------------------------------------------------------------------


def find_pool_by_id(pools, pool_id):
    pool_id = pool_id.rstrip(".")  # handle truncated IDs from scan output
    for p in pools:
        pid = p.get("pool", "")
        if pid == pool_id or pid.startswith(pool_id):
            return p
    return None


def cmd_breakeven(args):
    pools = load_pools()
    pool_a = find_pool_by_id(pools, args.from_pool)
    pool_b = find_pool_by_id(pools, args.to_pool)

    if not pool_a:
        print(f"Error: could not find pool '{args.from_pool}'", file=sys.stderr)
        sys.exit(1)
    if not pool_b:
        print(f"Error: could not find pool '{args.to_pool}'", file=sys.stderr)
        sys.exit(1)

    apy_a = pool_a.get("apy", 0) or 0
    apy_b = pool_b.get("apy", 0) or 0
    amount = args.amount or 10_000

    chain_a = pool_a.get("chain", "")
    chain_b = pool_b.get("chain", "")
    same_chain = chain_a.lower() == chain_b.lower()
    cost_rate = COST_SAME_CHAIN if same_chain else COST_CROSS_CHAIN
    cost = amount * cost_rate

    net_gain_pct = apy_b - apy_a  # percentage points
    daily_gain = (net_gain_pct / 100) * amount / 365

    if daily_gain <= 0:
        breakeven_days = float("inf")
        verdict = "NO-GO"
    else:
        breakeven_days = cost / daily_gain
        if breakeven_days <= 30:
            verdict = "GO"
        elif breakeven_days <= 90:
            verdict = "MAYBE"
        else:
            verdict = "NO-GO"

    if args.json:
        print(json.dumps({
            "from": {
                "pool": pool_a.get("pool"),
                "project": pool_a.get("project"),
                "chain": chain_a,
                "symbol": pool_a.get("symbol"),
                "apy": apy_a,
            },
            "to": {
                "pool": pool_b.get("pool"),
                "project": pool_b.get("project"),
                "chain": chain_b,
                "symbol": pool_b.get("symbol"),
                "apy": apy_b,
            },
            "amount": amount,
            "costRate": cost_rate,
            "estimatedCost": cost,
            "netGainPct": net_gain_pct,
            "dailyGain": daily_gain,
            "breakeven_days": None if math.isinf(breakeven_days) else round(breakeven_days, 1),
            "verdict": verdict,
        }, indent=2))
        return

    move_type = "same-chain" if same_chain else "cross-chain"
    print(f"\nDeFi Yield Scout \u2014 Breakeven Analysis")
    print("\u2501" * 70)
    print(f"  FROM: {pool_a.get('project')} / {pool_a.get('symbol')} ({chain_a})")
    print(f"        APY: {fmt_pct(apy_a)}")
    print(f"  TO:   {pool_b.get('project')} / {pool_b.get('symbol')} ({chain_b})")
    print(f"        APY: {fmt_pct(apy_b)}")
    print("\u2501" * 70)
    print(f"  Amount:          {fmt_usd(amount)}")
    print(f"  Move type:       {move_type}")
    print(f"  Est. cost:       {fmt_usd(cost)} ({cost_rate * 100:.0f}% of amount)")
    print(f"  Net APY gain:    {'+' if net_gain_pct >= 0 else ''}{net_gain_pct:.2f} pp")
    print(f"  Daily gain:      {fmt_usd(daily_gain)}/day")
    if math.isinf(breakeven_days):
        print(f"  Breakeven:       NEVER (target APY is not higher)")
    else:
        print(f"  Breakeven:       {breakeven_days:.0f} days")
    print("\u2501" * 70)
    tag = {"GO": "\u2705 GO", "MAYBE": "\u26a0\ufe0f  MAYBE", "NO-GO": "\u274c NO-GO"}
    print(f"  Verdict:         {tag[verdict]}")
    print()


# ---------------------------------------------------------------------------
# Subcommand: history
# ---------------------------------------------------------------------------


def cmd_history(args):
    pool_id = args.pool
    url = CHART_URL.format(pool_id=pool_id)

    print(f"Fetching 30-day history for {pool_id[:16]}...", file=sys.stderr)
    data = fetch_json(url)
    points = data.get("data", data) if isinstance(data, dict) else data

    if not points:
        print("No historical data found for this pool.", file=sys.stderr)
        sys.exit(1)

    # Take last 30 entries
    recent = points[-30:]
    apys = [p.get("apy", 0) or 0 for p in recent]
    tvls = [p.get("tvlUsd", 0) or 0 for p in recent]
    dates = [p.get("timestamp", "")[:10] for p in recent]

    avg_apy = sum(apys) / len(apys) if apys else 0
    min_apy = min(apys) if apys else 0
    max_apy = max(apys) if apys else 0

    # Stability score: based on coefficient of variation
    if avg_apy > 0 and len(apys) > 1:
        variance = sum((a - avg_apy) ** 2 for a in apys) / len(apys)
        std_dev = math.sqrt(variance)
        cv = std_dev / avg_apy
        if cv < 0.1:
            stability = "STABLE"
        elif cv < 0.3:
            stability = "MODERATE"
        else:
            stability = "VOLATILE"
    else:
        std_dev = 0
        cv = 0
        stability = "N/A"

    # TVL trend
    if len(tvls) >= 2:
        tvl_start = tvls[0] if tvls[0] else 1
        tvl_change = (tvls[-1] - tvls[0]) / tvl_start * 100
        if tvl_change > 5:
            tvl_trend = f"UP (+{tvl_change:.1f}%)"
        elif tvl_change < -5:
            tvl_trend = f"DOWN ({tvl_change:.1f}%)"
        else:
            tvl_trend = f"FLAT ({tvl_change:+.1f}%)"
    else:
        tvl_trend = "N/A"

    if args.json:
        print(json.dumps({
            "pool": pool_id,
            "days": len(recent),
            "current_apy": apys[-1] if apys else None,
            "avg_apy": round(avg_apy, 4),
            "min_apy": round(min_apy, 4),
            "max_apy": round(max_apy, 4),
            "std_dev": round(std_dev, 4),
            "stability": stability,
            "tvl_current": tvls[-1] if tvls else None,
            "tvl_trend": tvl_trend,
            "sparkline": sparkline(apys),
            "data": [{"date": d, "apy": a, "tvl": t} for d, a, t in zip(dates, apys, tvls)],
        }, indent=2))
        return

    print(f"\nDeFi Yield Scout \u2014 30-Day APY History")
    print("\u2501" * 60)
    print(f"  Pool:          {pool_id}")
    print(f"  Period:        {dates[0] if dates else '?'} \u2192 {dates[-1] if dates else '?'}")
    print(f"  Current APY:   {fmt_pct(apys[-1] if apys else 0)}")
    print(f"  Average APY:   {fmt_pct(avg_apy)}")
    print(f"  Min APY:       {fmt_pct(min_apy)}")
    print(f"  Max APY:       {fmt_pct(max_apy)}")
    print(f"  Std Dev:       {std_dev:.4f}")
    print(f"  Stability:     {stability}")
    print(f"  TVL Current:   {fmt_usd(tvls[-1] if tvls else 0)}")
    print(f"  TVL Trend:     {tvl_trend}")
    print("\u2501" * 60)
    print(f"  APY Trend:     {sparkline(apys)}")
    print()


# ---------------------------------------------------------------------------
# Subcommand: protocols
# ---------------------------------------------------------------------------

PROTOCOL_INFO = {
    "morpho-v1": {
        "name": "Morpho",
        "chains": ["Base", "Arbitrum"],
        "vault_standard": "ERC-4626",
        "audits": "Spearbit, Trail of Bits, Cantina",
        "risk_notes": "Non-custodial, immutable markets. Curated vaults add a layer of risk management.",
    },
    "euler-v2": {
        "name": "Euler v2",
        "chains": ["Base", "Arbitrum"],
        "vault_standard": "ERC-4626",
        "audits": "Spearbit, Certora, Trail of Bits",
        "risk_notes": "Modular vault system. v2 is a full rewrite after v1 exploit. Formal verification.",
    },
    "lazy-summer-protocol": {
        "name": "Lazy Summer",
        "chains": ["Base"],
        "vault_standard": "ERC-4626",
        "audits": "Community audited",
        "risk_notes": "Yield aggregator on Base. Allocates across underlying protocols.",
    },
    "silo-v2": {
        "name": "Silo v2",
        "chains": ["Base", "Arbitrum"],
        "vault_standard": "Custom (isolated markets)",
        "audits": "ABDK, Quantstamp",
        "risk_notes": "Isolated lending markets — risk is contained per pair.",
    },
    "moonwell-lending": {
        "name": "Moonwell",
        "chains": ["Base"],
        "vault_standard": "cToken (Compound-style)",
        "audits": "Halborn, Code4rena",
        "risk_notes": "Fork of Compound/Moonbeam. Governance-managed parameters.",
    },
    "compound-v3": {
        "name": "Compound v3",
        "chains": ["Base", "Arbitrum"],
        "vault_standard": "Comet (single-asset)",
        "audits": "OpenZeppelin, Trail of Bits, ChainSecurity",
        "risk_notes": "Battle-tested. Single-borrowable-asset model. COMP rewards may fluctuate.",
    },
    "aave-v3": {
        "name": "Aave v3",
        "chains": ["Base", "Arbitrum"],
        "vault_standard": "aToken (rebasing)",
        "audits": "SigmaPrime, Trail of Bits, Certora",
        "risk_notes": "Largest DeFi lending protocol. E-mode, isolation mode for risk segmentation.",
    },
    "harvest-finance": {
        "name": "Harvest Finance",
        "chains": ["Base", "Arbitrum"],
        "vault_standard": "Custom (fToken)",
        "audits": "Haechi, PeckShield",
        "risk_notes": "Yield aggregator. Auto-compounds. Strategy risk depends on underlying.",
    },
    "40-acres": {
        "name": "40 Acres",
        "chains": ["Base"],
        "vault_standard": "ERC-4626",
        "audits": "Community audited",
        "risk_notes": "Newer protocol. Lower TVL — higher smart contract risk.",
    },
    "wasabi-protocol": {
        "name": "Wasabi",
        "chains": ["Arbitrum"],
        "vault_standard": "Custom",
        "audits": "Community audited",
        "risk_notes": "Options/perps protocol. Yield from options premiums.",
    },
    "yo-protocol": {
        "name": "Yo Protocol",
        "chains": ["Base"],
        "vault_standard": "Custom",
        "audits": "Community audited",
        "risk_notes": "Newer protocol. Lower TVL — verify before large deposits.",
    },
}


def cmd_protocols(args):
    if args.json:
        print(json.dumps(PROTOCOL_INFO, indent=2))
        return

    print(f"\nDeFi Yield Scout \u2014 Whitelisted Protocols")
    print("\u2501" * 100)
    hdr = f"  {'Protocol':<22} {'Chains':<20} {'Vault Standard':<26} {'Audits':<30}"
    print(hdr)
    print("\u2501" * 100)

    for slug in sorted(PROTOCOL_INFO):
        info = PROTOCOL_INFO[slug]
        chains = ", ".join(info["chains"])
        print(
            f"  {info['name']:<22} "
            f"{chains:<20} "
            f"{info['vault_standard']:<26} "
            f"{info['audits']:<30}"
        )

    print(f"\n{len(PROTOCOL_INFO)} protocols. See references/protocols.md for detailed risk notes.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        prog="yield_scout",
        description="DeFi Yield Scout \u2014 USDC yield farming scanner for Base & Arbitrum",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # scan
    p_scan = sub.add_parser("scan", help="Ranked table of top USDC yields")
    p_scan.add_argument("--chain", choices=["Base", "Arbitrum", "base", "arbitrum"])
    p_scan.add_argument("--protocol", help="Filter by protocol slug")
    p_scan.add_argument("--min-tvl", type=float, default=0, help="Minimum TVL in USD")
    p_scan.add_argument("--top", type=int, default=20, help="Number of results")
    p_scan.add_argument("--json", action="store_true", help="JSON output")

    # breakeven
    p_be = sub.add_parser("breakeven", help="Compare two vaults — breakeven analysis")
    p_be.add_argument("--from-pool", required=True, help="Source pool UUID")
    p_be.add_argument("--to-pool", required=True, help="Target pool UUID")
    p_be.add_argument("--amount", type=float, default=10_000, help="Amount in USD (default 10000)")
    p_be.add_argument("--json", action="store_true", help="JSON output")

    # history
    p_hist = sub.add_parser("history", help="30-day APY trend for a pool")
    p_hist.add_argument("--pool", required=True, help="Pool UUID")
    p_hist.add_argument("--json", action="store_true", help="JSON output")

    # protocols
    p_proto = sub.add_parser("protocols", help="Overview of whitelisted protocols")
    p_proto.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "breakeven":
        cmd_breakeven(args)
    elif args.command == "history":
        cmd_history(args)
    elif args.command == "protocols":
        cmd_protocols(args)


if __name__ == "__main__":
    main()
