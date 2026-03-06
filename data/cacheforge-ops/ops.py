#!/usr/bin/env python3
"""CacheForge Operations CLI — balance, top-up, upstream, keys, info."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

# ── Colour helpers ────────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"
MAGENTA = "\033[95m"


def c(text, *codes):
    """Wrap *text* with ANSI escape codes."""
    return "".join(codes) + str(text) + RESET


# ── Box-drawing helpers ───────────────────────────────────────────────────────

BOX_TL = "\u250c"  # ┌
BOX_TR = "\u2510"  # ┐
BOX_BL = "\u2514"  # └
BOX_BR = "\u2518"  # ┘
BOX_H = "\u2500"   # ─
BOX_V = "\u2502"   # │
BOX_ML = "\u251c"  # ├
BOX_MR = "\u2524"  # ┤

BLOCK_FULL = "\u2588"   # █
BLOCK_LIGHT = "\u2591"  # ░


def box_line(text, width=60):
    """Return a single box row with left-aligned *text*."""
    visible = len(strip_ansi(text))
    pad = max(width - visible - 2, 0)
    return f"{BOX_V} {text}{' ' * pad}{BOX_V}"


def box_top(width=60):
    return BOX_TL + BOX_H * (width) + BOX_TR


def box_bottom(width=60):
    return BOX_BL + BOX_H * (width) + BOX_BR


def box_sep(width=60):
    return BOX_ML + BOX_H * (width) + BOX_MR


def strip_ansi(s):
    """Remove ANSI escape sequences for length calculations."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", s)


def print_box(title, rows, width=60):
    """Print a titled box with *rows* (list of strings)."""
    print(box_top(width))
    header = c(f" {title}", BOLD, CYAN)
    print(box_line(header, width))
    print(box_sep(width))
    for row in rows:
        print(box_line(row, width))
    print(box_bottom(width))


def balance_bar(balance_usd, max_usd=50.0, bar_width=40):
    """Return a coloured bar representing the current balance."""
    ratio = max(0.0, min(1.0, balance_usd / max_usd)) if max_usd > 0 else 0
    filled = int(ratio * bar_width)
    empty = bar_width - filled
    if balance_usd > 5.0:
        clr = GREEN
    elif balance_usd > 1.0:
        clr = YELLOW
    else:
        clr = RED
    return c(BLOCK_FULL * filled, clr) + c(BLOCK_LIGHT * empty, DIM)


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def get_config():
    """Return (base_url, api_key) from environment."""
    base = os.environ.get("CACHEFORGE_BASE_URL", "https://app.anvil-ai.io").rstrip("/")
    key = os.environ.get("CACHEFORGE_API_KEY", "")
    if not key:
        print(c("ERROR: CACHEFORGE_API_KEY is not set.", BOLD, RED))
        print(f"  Export it first:  {c('export CACHEFORGE_API_KEY=cf_...', DIM)}")
        sys.exit(1)
    return base, key


def api_request(method, path, body=None):
    """Issue an HTTP request and return parsed JSON (or exit on error)."""
    base, key = get_config()
    url = f"{base}{path}"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        try:
            err_body = exc.read().decode()
            err_json = json.loads(err_body)
            detail = err_json.get("error", err_json.get("message", err_body))
        except Exception:
            detail = str(exc)
        print(c(f"API Error ({exc.code}): {detail}", BOLD, RED))
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(c(f"Connection Error: {exc.reason}", BOLD, RED))
        sys.exit(1)


# ── Subcommands ───────────────────────────────────────────────────────────────

def cmd_balance(_args):
    """Check balance and billing status."""
    data = api_request("GET", "/v1/account/billing")
    billing = data.get("billing", {})

    balance_micro = billing.get("creditBalanceMicrousd", 0)
    balance_usd = balance_micro / 1_000_000.0
    auto_topup_enabled = billing.get("autoTopupEnabled", False)
    auto_topup_threshold = billing.get("autoTopupThresholdCents", 0)
    auto_topup_amount = billing.get("autoTopupAmountCents", 0)
    has_payment_method = billing.get("defaultPaymentMethodSet", False)

    # Colour the balance figure
    if balance_usd > 5.0:
        bal_color = GREEN
    elif balance_usd > 1.0:
        bal_color = YELLOW
    else:
        bal_color = RED

    big_balance = c(f"${balance_usd:,.2f}", BOLD, bal_color)

    rows = [
        f"  Balance:  {big_balance}",
        f"  {balance_bar(balance_usd)}",
        "",
    ]

    # Auto top-up status
    if auto_topup_enabled:
        thr = auto_topup_threshold / 100.0
        amt = auto_topup_amount / 100.0
        rows.append(f"  Auto top-up:  {c('ON', BOLD, GREEN)}  "
                     f"(+${amt:.0f} when < ${thr:.0f})")
    else:
        rows.append(f"  Auto top-up:  {c('OFF', BOLD, DIM)}")

    # Payment method
    if has_payment_method:
        rows.append(f"  Payment:    {c('Card on file', WHITE)}")
    else:
        rows.append(f"  Payment:    {c('No card on file', DIM)}")

    print()
    print_box("CacheForge Balance", rows)
    print()


def cmd_topup(args):
    """Create a top-up payment link."""
    amount = args.amount
    data = api_request("POST", "/v1/account/billing/topup", {
        "amountUsd": amount,
        "method": args.method,
    })

    url = data.get("paymentUrl", "")
    rows = [
        f"  Amount:  {c(f'${amount}', BOLD, GREEN)}",
        f"  Method:  {c(args.method, WHITE)}",
        "",
        f"  {c('Payment link:', BOLD, CYAN)}",
        f"  {c(url, BOLD, WHITE)}",
        "",
        f"  {c('Open this URL to complete payment.', DIM)}",
    ]
    print()
    print_box("Top Up Credits", rows)
    print()


def cmd_auto_topup(args):
    """Enable or disable auto top-up."""
    if args.disable:
        body = {"enabled": False}
    elif args.enable:
        body = {
            "enabled": True,
            "thresholdCents": args.threshold,
            "amountCents": args.amount,
        }
    else:
        print(c("Specify --enable or --disable", BOLD, YELLOW))
        sys.exit(1)

    api_request("PATCH", "/v1/account/billing/auto-topup", body)

    if body["enabled"]:
        thr_usd = args.threshold / 100.0
        amt_usd = args.amount / 100.0
        status = (c("ENABLED", BOLD, GREEN) +
                  f"  (+${amt_usd:.0f} when balance < ${thr_usd:.0f})")
    else:
        status = c("DISABLED", BOLD, DIM)

    rows = [f"  Auto top-up:  {status}"]
    print()
    print_box("Auto Top-Up", rows)
    print()


def cmd_upstream(args):
    """View or set upstream provider config."""
    if args.set:
        body = {}
        if args.kind:
            body["kind"] = args.kind
        if args.base_url:
            body["baseUrl"] = args.base_url
        if args.api_key:
            body["apiKey"] = args.api_key
        api_request("POST", "/v1/account/upstream", body)
        print()
        rows = [
            f"  {c('Upstream updated successfully.', BOLD, GREEN)}",
        ]
        if args.kind:
            rows.append(f"  Kind:     {c(args.kind, WHITE)}")
        if args.base_url:
            rows.append(f"  Base URL: {c(args.base_url, WHITE)}")
        rows.append(f"  API Key:  {c('configured', DIM)}")
        print_box("Upstream Provider", rows)
        print()
    else:
        data = api_request("GET", "/v1/account/upstream")
        configured = data.get("configured", False)
        upstream = data.get("upstream", {})

        if not configured:
            rows = [f"  {c('Not configured', DIM)}"]
        else:
            kind = upstream.get("kind", "unknown")
            base_url = upstream.get("baseUrl", "—")
            rows = [
                f"  Kind:     {c(kind, BOLD, CYAN)}",
                f"  Base URL: {c(base_url, WHITE)}",
                f"  API Key:  {c('configured', GREEN)}",
            ]
        print()
        print_box("Upstream Provider", rows)
        print()


def cmd_keys(args):
    """List or create API keys."""
    if args.create:
        data = api_request("POST", "/v1/account/keys", {})
        key = data.get("apiKey", "")
        prefix = data.get("prefix", key[:12] + "..." if key else "")

        rows = [
            f"  {c('New API key created!', BOLD, GREEN)}",
            "",
            f"  {c(key, BOLD, WHITE)}",
            "",
            f"  {c('Save this key now — it will not be shown again.', BOLD, YELLOW)}",
        ]
        print()
        print_box("New API Key", rows)
        print()
    else:
        data = api_request("GET", "/v1/account/keys")
        keys = data.get("keys", [])

        if not keys:
            rows = [f"  {c('No API keys found.', DIM)}"]
        else:
            rows = []
            for i, k in enumerate(keys):
                prefix = k.get("prefix", k.get("id", "???"))
                created = k.get("createdAt", "")[:10] or "—"
                label = k.get("label", "")
                line = f"  {c(str(i + 1) + '.', DIM)} {c(prefix, CYAN)}"
                if label:
                    line += f"  {c(label, DIM)}"
                line += f"  {c(f'({created})', DIM)}"
                rows.append(line)

        print()
        print_box("API Keys", rows)
        print()


def cmd_info(_args):
    """Show tenant info."""
    data = api_request("GET", "/v1/account/info")
    tenant = data.get("tenant", {})

    name = tenant.get("name", "—")
    status = tenant.get("status", "—")
    upstream = tenant.get("upstreamConfigured", False)
    key_count = tenant.get("activeKeys", "?")
    tenant_id = tenant.get("id", "")

    # Status colour
    status_str = status
    if isinstance(status, str):
        if status.lower() in ("active", "enabled"):
            status_str = c(status, BOLD, GREEN)
        elif status.lower() in ("suspended", "disabled"):
            status_str = c(status, BOLD, RED)
        else:
            status_str = c(status, BOLD, YELLOW)

    rows = [
        f"  Tenant:    {c(name, BOLD, WHITE)}",
    ]
    if tenant_id:
        rows.append(f"  ID:        {c(tenant_id, DIM)}")
    rows.extend([
        f"  Status:    {status_str}",
        f"  Upstream:  {c('configured', GREEN) if upstream else c('not set', RED)}",
        f"  API Keys:  {c(str(key_count), WHITE)}",
    ])

    print()
    print_box("CacheForge Tenant", rows)
    print()


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CacheForge Operations CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Environment:\n"
            "  CACHEFORGE_BASE_URL  API base URL (default: https://app.anvil-ai.io)\n"
            "  CACHEFORGE_API_KEY   Your CacheForge API key (required)\n"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # balance
    sub.add_parser("balance", help="Check balance and billing status")

    # topup
    p_topup = sub.add_parser("topup", help="Create a top-up payment link")
    p_topup.add_argument("--amount", type=int, default=10,
                         help="Amount in USD (default: 10)")
    p_topup.add_argument("--method", choices=["stripe", "crypto"], default="stripe",
                         help="Payment method (default: stripe)")

    # auto-topup
    p_auto = sub.add_parser("auto-topup", help="Enable/disable auto top-up")
    auto_grp = p_auto.add_mutually_exclusive_group(required=True)
    auto_grp.add_argument("--enable", action="store_true",
                          help="Enable auto top-up")
    auto_grp.add_argument("--disable", action="store_true",
                          help="Disable auto top-up")
    p_auto.add_argument("--threshold", type=int, default=200,
                        help="Threshold in cents (default: 200)")
    p_auto.add_argument("--amount", type=int, default=1000,
                        help="Top-up amount in cents (default: 1000)")

    # upstream
    p_up = sub.add_parser("upstream", help="View or set upstream provider")
    p_up.add_argument("--set", action="store_true",
                      help="Set upstream (otherwise just view)")
    p_up.add_argument("--kind", type=str, default=None,
                      help="Provider kind (openrouter, openai, anthropic, custom)")
    p_up.add_argument("--base-url", type=str, default=None,
                      help="Upstream base URL")
    p_up.add_argument("--api-key", type=str, default=None,
                      help="Upstream API key")

    # keys
    p_keys = sub.add_parser("keys", help="List or create API keys")
    p_keys.add_argument("--create", action="store_true",
                        help="Create a new API key")

    # info
    sub.add_parser("info", help="Show tenant info")

    args = parser.parse_args()
    dispatch = {
        "balance": cmd_balance,
        "topup": cmd_topup,
        "auto-topup": cmd_auto_topup,
        "upstream": cmd_upstream,
        "keys": cmd_keys,
        "info": cmd_info,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
