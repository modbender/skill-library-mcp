#!/usr/bin/env python3
"""CacheForge terminal dashboard -- usage, savings, and performance metrics.

Stdlib-only (no external deps). Renders rich ASCII dashboards with Unicode
box drawing, block-element bar charts, sparklines, and ANSI colours.
"""

import argparse
import json
import os
import shutil
import sys
import urllib.error
import urllib.request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = os.environ.get("CACHEFORGE_BASE_URL", "https://app.anvil-ai.io").rstrip("/")
API_KEY = os.environ.get("CACHEFORGE_API_KEY", "")

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
WHITE = "\033[37m"


def color(text: str, color_code: str) -> str:
    """Wrap *text* in an ANSI colour escape sequence."""
    return f"{color_code}{text}{RESET}"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_tokens(n: int) -> str:
    """Human-friendly token count: 1.3M, 847K, 198."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def format_usd(amount) -> str:
    """Format a numeric value as $X.XX. Handles micro-USD, cents, or dollars."""
    try:
        v = float(amount)
    except (TypeError, ValueError):
        return "$0.00"
    # Heuristic: if the API passes micro-USD or cents, normalise.
    if abs(v) >= 10_000:
        # Likely micro-USD
        v = v / 1_000_000
    elif abs(v) >= 100:
        # Likely cents
        v = v / 100
    return f"${v:,.2f}"


def bar(value: float, max_val: float, width: int = 30) -> str:
    """Render a horizontal bar chart: filled blocks + empty blocks."""
    if max_val <= 0:
        filled = 0
    else:
        filled = int(round((value / max_val) * width))
        filled = max(0, min(filled, width))
    empty = width - filled
    return color("\u2588" * filled, GREEN) + color("\u2591" * empty, WHITE)


def pct_bar(pct: float, width: int = 30) -> str:
    """Render a percentage bar (0-100)."""
    return bar(pct, 100, width)


def spark(values: list) -> str:
    """Render a sparkline string for a list of numeric values."""
    ticks = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"
    if not values:
        return ""
    lo = min(values)
    hi = max(values)
    rng = hi - lo if hi != lo else 1
    return "".join(ticks[min(int((v - lo) / rng * 7), 7)] for v in values)


# ---------------------------------------------------------------------------
# Terminal width
# ---------------------------------------------------------------------------

def term_width(default: int = 60) -> int:
    """Return usable terminal width, clamped to a sane minimum."""
    try:
        cols = shutil.get_terminal_size((default, 24)).columns
    except Exception:
        cols = default
    return max(cols, 40)


# ---------------------------------------------------------------------------
# Box-drawing helpers
# ---------------------------------------------------------------------------

def box_top(w: int) -> str:
    return "\u250c" + "\u2500" * (w - 2) + "\u2510"


def box_mid(w: int) -> str:
    return "\u251c" + "\u2500" * (w - 2) + "\u2524"


def box_bot(w: int) -> str:
    return "\u2514" + "\u2500" * (w - 2) + "\u2518"


def box_row(text: str, w: int) -> str:
    """Pad *text* into a box row, accounting for ANSI escape widths."""
    visible_len = len(_strip_ansi(text))
    pad = max(w - 2 - visible_len, 0)
    return "\u2502 " + text + " " * pad + " \u2502" if visible_len + 2 < w else "\u2502" + text[: w - 2] + "\u2502"


def box_empty(w: int) -> str:
    return box_row("", w)


def _strip_ansi(s: str) -> str:
    """Remove ANSI escape codes for length calculations."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", s)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _api_get(path: str, params: dict | None = None) -> dict:
    """Perform an authenticated GET against the CacheForge API."""
    if not API_KEY:
        print(color("Error: CACHEFORGE_API_KEY is not set.", RED), file=sys.stderr)
        sys.exit(1)

    url = f"{BASE_URL}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url = f"{url}?{qs}"

    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode() if exc.fp else ""
        print(color(f"API error {exc.code}: {body}", RED), file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(color(f"Connection error: {exc.reason}", RED), file=sys.stderr)
        sys.exit(1)


def fetch_billing() -> dict:
    """Returns the 'billing' sub-object from GET /v1/account/billing."""
    data = _api_get("/v1/account/billing")
    return data.get("billing", {})


def fetch_usage(days: int = 7) -> dict:
    """Returns the 'summary' sub-object from GET /v1/account/usage."""
    data = _api_get("/v1/account/usage", {"days": str(days)})
    return data.get("summary", {})


def fetch_breakdown(group_by: str = "model", window: str = "7d") -> dict:
    """Returns the full response from GET /v1/account/usage/breakdown."""
    return _api_get("/v1/account/usage/breakdown", {"groupBy": group_by, "window": window})


def fetch_info() -> dict:
    """Returns the 'tenant' sub-object from GET /v1/account/info."""
    data = _api_get("/v1/account/info")
    return data.get("tenant", {})


# ---------------------------------------------------------------------------
# Safe dict access
# ---------------------------------------------------------------------------

def _g(d: dict, *keys, default=0):
    """Nested dict get with a default."""
    cur = d
    for k in keys:
        if isinstance(cur, dict):
            cur = cur.get(k, default)
        else:
            return default
    return cur


# ---------------------------------------------------------------------------
# Parse window string -> days int
# ---------------------------------------------------------------------------

def _window_to_days(window: str) -> int:
    """Convert '7d', '30d', '1d' etc. to integer days."""
    w = window.strip().lower()
    if w.endswith("d"):
        try:
            return int(w[:-1])
        except ValueError:
            pass
    try:
        return int(w)
    except ValueError:
        return 7


# ---------------------------------------------------------------------------
# Subcommand: dashboard
# ---------------------------------------------------------------------------

def cmd_dashboard(args: argparse.Namespace) -> None:
    """Full terminal dashboard combining billing + usage + breakdown."""
    days = _window_to_days(args.window)

    # Fetch all data (already unwrapped by fetch_* helpers)
    info = fetch_info()
    billing = fetch_billing()
    usage = fetch_usage(days)
    breakdown_data = fetch_breakdown("model", args.window)

    w = min(term_width(), 80)

    workspace = info.get("name", "CacheForge")

    balance_micro = billing.get("creditBalanceMicrousd", 0)
    balance_usd = balance_micro / 1_000_000.0
    status = info.get("status", "active")
    auto_topup = billing.get("autoTopupEnabled", False)
    topup_label = color("on", GREEN) if auto_topup else color("off", YELLOW)

    requests_count = usage.get("totalRequests", 0)
    prompt_tokens = usage.get("promptTokens", 0)
    output_tokens = usage.get("outputTokens", 0)
    tokens_saved = usage.get("estimatedOptimizerSavedPromptTokens", 0)
    upstream_cost = usage.get("upstreamCostUsd", 0)
    cost_avoided = usage.get("estimatedOptimizerCostAvoidedUsd", 0)

    tokens_sent = prompt_tokens + output_tokens
    total_tokens = tokens_sent + tokens_saved
    token_reduction_pct = (tokens_saved / total_tokens * 100) if total_tokens > 0 else 0.0
    cache_hit_pct = usage.get("cacheHitRatePct", 0.0)
    total_cost = upstream_cost + cost_avoided if cost_avoided else upstream_cost
    cost_savings_pct = (cost_avoided / total_cost * 100) if total_cost > 0 else 0.0

    # Build output
    lines: list[str] = []
    lines.append(box_top(w))

    # Header
    title = f"  {color(BOLD, CYAN)}CacheForge{RESET} {color('--', WHITE)} {workspace}"
    lines.append(box_row(title, w))
    bal_line = (
        f"  Balance: {color(f'${balance_usd:,.2f}', GREEN)}"
        f"  {color(chr(0x25CF), GREEN)} {status}"
        f"  {color(chr(0x25CF), WHITE)} Auto Top-up {topup_label}"
    )
    lines.append(box_row(bal_line, w))

    lines.append(box_mid(w))

    # Summary header
    lines.append(box_row(color(f"  {days}-Day Summary", CYAN), w))
    lines.append(box_row("  " + "\u2500" * (w - 6), w))

    # Two-column stats
    def stat_pair(l_label, l_val, r_label, r_val):
        left = f"  {l_label:<16s}{l_val:>10s}"
        right = f"{r_label:<18s}{r_val:>10s}"
        return box_row(left + "  " + right, w)

    lines.append(stat_pair(
        "Requests:", f"{requests_count:,}",
        "Upstream Cost:", format_usd(upstream_cost),
    ))
    lines.append(stat_pair(
        "Tokens Sent:", format_tokens(tokens_sent),
        "Cost Avoided:", color(format_usd(cost_avoided), GREEN),
    ))

    net_savings_str = f"{cost_savings_pct:.1f}%"
    lines.append(stat_pair(
        "Tokens Saved:", color(format_tokens(tokens_saved), GREEN),
        "Net Savings:", color(net_savings_str, GREEN),
    ))

    lines.append(box_empty(w))

    # Bar charts
    bar_w = max(w - 40, 10)

    tr_line = f"  Token Reduction {pct_bar(token_reduction_pct, bar_w)}  {token_reduction_pct:5.1f}%"
    lines.append(box_row(tr_line, w))

    ch_line = f"  Cache Hit Rate  {pct_bar(cache_hit_pct, bar_w)}  {cache_hit_pct:5.1f}%"
    lines.append(box_row(ch_line, w))

    cs_line = f"  Cost Savings    {pct_bar(cost_savings_pct, bar_w)}  {cost_savings_pct:5.1f}%"
    lines.append(box_row(cs_line, w))

    lines.append(box_empty(w))

    # Top models breakdown
    groups = breakdown_data.get("breakdown", [])
    if isinstance(groups, list) and groups:
        lines.append(box_row(color("  Top Models (tokens)", CYAN), w))
        sorted_groups = sorted(groups, key=lambda g: _g(g, "observedTotalTokens", default=0), reverse=True)[:5]
        max_tokens = max(_g(g, "observedTotalTokens", default=0) for g in sorted_groups) if sorted_groups else 1
        model_bar_w = max(w - 40, 10)
        for g in sorted_groups:
            name = g.get("group", "unknown")
            if isinstance(name, dict):
                name = str(name)
            toks = _g(g, "observedTotalTokens", default=0)
            name_str = f"  {str(name)[:20]:<20s}"
            bar_str = bar(toks, max_tokens, model_bar_w)
            tok_str = format_tokens(toks)
            lines.append(box_row(f"{name_str}{bar_str}  {tok_str:>6s}", w))

    lines.append(box_bot(w))

    print("\n".join(lines))


# ---------------------------------------------------------------------------
# Subcommand: usage
# ---------------------------------------------------------------------------

def cmd_usage(args: argparse.Namespace) -> None:
    """Show usage summary for the given window."""
    days = _window_to_days(args.window)
    usage = fetch_usage(days)

    w = min(term_width(), 70)

    requests_count = usage.get("totalRequests", 0)
    prompt_tokens = usage.get("promptTokens", 0)
    output_tokens = usage.get("outputTokens", 0)
    tokens_saved = usage.get("estimatedOptimizerSavedPromptTokens", 0)
    upstream_cost = usage.get("upstreamCostUsd", 0)
    cost_avoided = usage.get("estimatedOptimizerCostAvoidedUsd", 0)

    tokens_sent = prompt_tokens + output_tokens
    total_tokens = tokens_sent + tokens_saved
    token_reduction_pct = (tokens_saved / total_tokens * 100) if total_tokens > 0 else 0.0

    print()
    print(color(f"  CacheForge Usage ({days}d)", CYAN + BOLD))
    print("  " + "\u2500" * (w - 4))
    print(f"  {'Requests:':<20s}{requests_count:>12,}")
    print(f"  {'Tokens Sent:':<20s}{format_tokens(tokens_sent):>12s}")
    print(f"  {'Tokens Saved:':<20s}{color(format_tokens(tokens_saved), GREEN):>12s}")
    print(f"  {'Token Reduction:':<20s}{color(f'{token_reduction_pct:.1f}%', GREEN):>12s}")
    print()
    print(f"  {'Upstream Cost:':<20s}{format_usd(upstream_cost):>12s}")
    print(f"  {'Cost Avoided:':<20s}{color(format_usd(cost_avoided), GREEN):>12s}")
    print()


# ---------------------------------------------------------------------------
# Subcommand: breakdown
# ---------------------------------------------------------------------------

def cmd_breakdown(args: argparse.Namespace) -> None:
    """Show breakdown table by model/provider/key."""
    data = fetch_breakdown(args.by, args.window)

    w = min(term_width(), 80)
    groups = data.get("breakdown", [])
    if not isinstance(groups, list) or not groups:
        print(color("  No breakdown data available.", YELLOW))
        return

    sorted_groups = sorted(groups, key=lambda g: _g(g, "observedTotalTokens", default=0), reverse=True)
    max_tokens = max(_g(g, "observedTotalTokens", default=0) for g in sorted_groups) if sorted_groups else 1
    bar_w = max(w - 50, 10)

    print()
    print(color(f"  Breakdown by {args.by} ({args.window})", CYAN + BOLD))
    print("  " + "\u2500" * (w - 4))
    print(f"  {'Name':<22s}{'Requests':>10s}  {'Tokens':>8s}  {'Bar':<{bar_w}s}")
    print("  " + "\u2500" * (w - 4))

    for g in sorted_groups:
        name = g.get("group", "unknown")
        if isinstance(name, dict):
            name = str(name)
        name = str(name)[:20]
        reqs = _g(g, "requests", default=0)
        toks = _g(g, "observedTotalTokens", default=0)
        b = bar(toks, max_tokens, bar_w)
        print(f"  {name:<22s}{reqs:>10,}  {format_tokens(toks):>8s}  {b}")

    print()


# ---------------------------------------------------------------------------
# Subcommand: savings
# ---------------------------------------------------------------------------

def cmd_savings(args: argparse.Namespace) -> None:
    """Savings-focused view showing before/after comparison."""
    days = _window_to_days(args.window)
    usage = fetch_usage(days)

    w = min(term_width(), 70)

    prompt_tokens = usage.get("promptTokens", 0)
    output_tokens = usage.get("outputTokens", 0)
    tokens_saved = usage.get("estimatedOptimizerSavedPromptTokens", 0)
    upstream_cost = usage.get("upstreamCostUsd", 0)
    cost_avoided = usage.get("estimatedOptimizerCostAvoidedUsd", 0)

    tokens_sent = prompt_tokens + output_tokens
    total_tokens = tokens_sent + tokens_saved
    total_cost = upstream_cost + cost_avoided if cost_avoided else upstream_cost

    token_reduction_pct = (tokens_saved / total_tokens * 100) if total_tokens > 0 else 0.0
    cost_savings_pct = (cost_avoided / total_cost * 100) if total_cost > 0 else 0.0

    bar_w = max(w - 30, 10)

    print()
    print(color(f"  CacheForge Savings Report ({days}d)", CYAN + BOLD))
    print("  " + "\u2500" * (w - 4))
    print()

    print(color("  Tokens", CYAN))
    print(f"    Without CacheForge:  {format_tokens(total_tokens):>10s}")
    print(f"    With CacheForge:     {color(format_tokens(tokens_sent), GREEN):>10s}")
    print(f"    Tokens Saved:        {color(format_tokens(tokens_saved), GREEN):>10s}")
    print(f"    Reduction:           {pct_bar(token_reduction_pct, bar_w)}  {color(f'{token_reduction_pct:.1f}%', GREEN)}")
    print()

    print(color("  Cost", CYAN))
    print(f"    Without CacheForge:  {format_usd(total_cost):>10s}")
    print(f"    With CacheForge:     {color(format_usd(upstream_cost), GREEN):>10s}")
    print(f"    Cost Avoided:        {color(format_usd(cost_avoided), GREEN):>10s}")
    print(f"    Savings:             {pct_bar(cost_savings_pct, bar_w)}  {color(f'{cost_savings_pct:.1f}%', GREEN)}")
    print()

    if total_tokens > 0:
        print(color("  Summary", CYAN))
        print(f"    You saved {color(format_tokens(tokens_saved), GREEN)} tokens "
              f"and {color(format_usd(cost_avoided), GREEN)} "
              f"over the last {days} days.")
        print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cacheforge-stats",
        description="CacheForge terminal dashboard -- usage, savings, and performance metrics.",
    )
    sub = parser.add_subparsers(dest="command")

    # dashboard (default)
    p_dash = sub.add_parser("dashboard", help="Full terminal dashboard")
    p_dash.add_argument("--window", default="7d", help="Time window (e.g. 7d, 30d)")

    # usage
    p_usage = sub.add_parser("usage", help="Usage summary")
    p_usage.add_argument("--window", default="7d", help="Time window (e.g. 7d, 30d)")

    # breakdown
    p_bd = sub.add_parser("breakdown", help="Breakdown by model/provider/key")
    p_bd.add_argument("--by", default="model", choices=["model", "provider", "key"],
                       help="Group by dimension")
    p_bd.add_argument("--window", default="7d", help="Time window (e.g. 7d, 30d)")

    # savings
    p_sav = sub.add_parser("savings", help="Savings-focused view")
    p_sav.add_argument("--window", default="7d", help="Time window (e.g. 7d, 30d)")

    args = parser.parse_args()

    # Default to dashboard when no subcommand given
    if args.command is None:
        args.command = "dashboard"
        if not hasattr(args, "window"):
            args.window = "7d"

    dispatch = {
        "dashboard": cmd_dashboard,
        "usage": cmd_usage,
        "breakdown": cmd_breakdown,
        "savings": cmd_savings,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
