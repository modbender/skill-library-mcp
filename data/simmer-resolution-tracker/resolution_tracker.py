#!/usr/bin/env python3
"""Simmer Resolution Tracker and Auto-Redeemer.

Monitors Simmer positions for resolutions, logs outcomes to trade journal,
posts Discord alerts, and auto-redeems winning positions on-chain.

Run every 5 minutes via cron, or manually.

Required env vars:
    SIMMER_API_KEY       — your Simmer API key
    WALLET_PRIVATE_KEY   — Polymarket wallet private key (for redemptions)

Optional:
    DISCORD_WEBHOOK      — Discord webhook URL for win/loss alerts
    POLY_MODE            — set to "sim" to skip on-chain redemptions
    DATA_DIR             — override data directory (default: ./data/live)
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Load .env if present (development convenience) ────────────────────────────
def _load_env():
    for candidate in [".env", os.path.expanduser("~/.env")]:
        if os.path.exists(candidate):
            with open(candidate) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
            break

_load_env()

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY      = os.environ.get("SIMMER_API_KEY", "")
WEBHOOK_URL  = os.environ.get("DISCORD_WEBHOOK", "")
IS_SIM       = os.environ.get("POLY_MODE", "live").lower() == "sim"
API_BASE     = "https://api.simmer.markets"
SKILL_SLUG   = "simmer-resolution-tracker"

# Data directory — defaults to ./data/live (or ./data/sim in sim mode)
_default_data = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sim" if IS_SIM else "live")
DATA_DIR     = os.environ.get("DATA_DIR", _default_data)

JOURNAL_PATH      = os.path.join(DATA_DIR, "trade_journal.jsonl")
RESOLVED_PATH     = os.path.join(DATA_DIR, "resolved_trades.jsonl")
RESOLVED_IDS_PATH = os.path.join(DATA_DIR, "resolved_markets.json")
REDEEMED_IDS_PATH = os.path.join(DATA_DIR, "redeemed_markets.json")

MAX_REDEEMS_PER_RUN  = 6
TIME_BUDGET_SECONDS  = 120

# ── Simmer SDK (for redemptions) ──────────────────────────────────────────────
_client = None

def get_client():
    global _client
    if _client is None:
        from simmer_sdk import SimmerClient
        _client = SimmerClient(
            api_key=API_KEY,
            venue="polymarket",
        )
    return _client

# ── API helpers ───────────────────────────────────────────────────────────────

def api_request(path, method="GET", data=None):
    url = f"{API_BASE}{path}"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, headers=headers, method=method, data=body)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  API error {e.code}: {e.read().decode()[:120]}")
        return None
    except Exception as e:
        print(f"  API error: {e}")
        return None


def post_webhook(content):
    """Post a message to Discord via webhook URL (pure Python, no curl)."""
    if not WEBHOOK_URL:
        return
    try:
        body = json.dumps({"content": content[:2000]}).encode()
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"  ⚠️  Webhook error: {e}")

# ── Position fetching ─────────────────────────────────────────────────────────

def get_resolved_positions():
    data = api_request("/api/sdk/positions?status=resolved")
    if not data:
        return []
    positions = data.get("positions", [])
    counts    = data.get("position_counts", {})
    if positions:
        print(f"  📦 {len(positions)} resolved positions "
              f"(active={counts.get('active',0)}, resolved={counts.get('resolved',0)})")
    return positions


def get_all_positions():
    data = api_request("/api/sdk/positions?status=all")
    return data.get("positions", []) if data else []

# ── Redemption ────────────────────────────────────────────────────────────────

def redeem_position(market_id, side):
    """Redeem a winning position via Simmer SDK.

    Returns: (status, error)
      status: True (redeemed), False (failed), "already" (already done)
    """
    try:
        client = get_client()
        result = client.redeem(market_id=market_id, side=side)
        if not result:
            return False, "No result from SDK"

        if result.get("already_redeemed"):
            return "already", None

        tx_hash = result.get("tx_hash", "") or ""
        success = result.get("success", False)

        if success and tx_hash:
            print(f"    ✅ Redeemed (tx: {tx_hash[:20]}...)")
            return True, None
        elif success and not tx_hash:
            # SDK says success but no tx_hash — treat as unconfirmed, retry next run
            print(f"    ⚠️  Success but no tx_hash — will retry next run")
            return False, "success_no_tx_hash"
        else:
            error = result.get("error", "SDK redeem failed")
            return False, error

    except Exception as e:
        print(f"    ❌ Redeem exception: {e}")
        return False, str(e)

# ── Journal helpers ───────────────────────────────────────────────────────────

def load_journal():
    trades = []
    try:
        for line in Path(JOURNAL_PATH).read_text().strip().splitlines():
            try:
                trades.append(json.loads(line))
            except Exception:
                pass
    except FileNotFoundError:
        pass
    return trades


def save_journal(trades):
    tmp = JOURNAL_PATH + ".tmp"
    Path(tmp).parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, "w") as f:
        for t in trades:
            f.write(json.dumps(t) + "\n")
    os.replace(tmp, JOURNAL_PATH)


def append_resolved(trade):
    Path(RESOLVED_PATH).parent.mkdir(parents=True, exist_ok=True)
    mid = trade.get("market_id", "")
    # Dedup check
    if mid and Path(RESOLVED_PATH).exists():
        with open(RESOLVED_PATH) as f:
            for line in f:
                try:
                    if json.loads(line).get("market_id") == mid:
                        return
                except Exception:
                    pass
    with open(RESOLVED_PATH, "a") as f:
        f.write(json.dumps(trade) + "\n")


def load_id_set(path):
    try:
        return set(json.loads(Path(path).read_text()))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_id_set(ids, path, cap=500):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(list(ids)[-cap:], f)

# ── Cooldown tracking ─────────────────────────────────────────────────────────

_COOLDOWN_PATH = None

def record_trade_outcome(strategy, won):
    """Update consecutive-loss counter for cooldown detection."""
    global _COOLDOWN_PATH
    if _COOLDOWN_PATH is None:
        _COOLDOWN_PATH = os.path.join(DATA_DIR, "cooldown_state.json")
    try:
        state = {}
        if Path(_COOLDOWN_PATH).exists():
            state = json.loads(Path(_COOLDOWN_PATH).read_text())
        s = state.setdefault(strategy, {"consecutive_losses": 0, "skip_count": 0})
        if won:
            s["consecutive_losses"] = 0
        else:
            s["consecutive_losses"] = s.get("consecutive_losses", 0) + 1
        with open(_COOLDOWN_PATH, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"  ⚠️  Cooldown update error: {e}")

# ── Budget guard ──────────────────────────────────────────────────────────────

def _budget_ok(start_time, redeem_count):
    if redeem_count >= MAX_REDEEMS_PER_RUN:
        return False
    if time.monotonic() - start_time > TIME_BUDGET_SECONDS:
        return False
    return True

# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    _start = time.monotonic()
    now    = datetime.now(timezone.utc)
    print(f"\n🔍 Simmer Resolution Tracker — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   Mode: {'SIM (no on-chain redemptions)' if IS_SIM else 'LIVE'}")

    resolved_positions = get_resolved_positions()
    if not resolved_positions:
        print("  No resolved positions")
        return

    already_reported = load_id_set(RESOLVED_IDS_PATH)
    redeemed_ids     = load_id_set(REDEEMED_IDS_PATH)
    journal          = load_journal()

    # Build market_id → journal indices lookup
    market_index = {}
    for i, t in enumerate(journal):
        mid = t.get("market_id", "")
        if mid:
            market_index.setdefault(mid, []).append(i)

    new_count      = 0
    redeemed_count = 0
    total_redeemed = 0.0
    journal_dirty  = False

    for pos in resolved_positions:
        market_id = pos.get("market_id", "")
        if market_id in already_reported:
            continue

        question    = pos.get("question", "Unknown")
        cost_basis  = pos.get("cost_basis", 0) or 0
        pnl_api     = pos.get("pnl", 0) or 0
        shares_yes  = pos.get("shares_yes", 0) or 0
        shares_no   = pos.get("shares_no", 0) or 0
        api_outcome = pos.get("outcome")  # "yes" | "no" | None

        # Determine which side we held
        if shares_yes > shares_no:
            side = "yes"
        elif shares_no > shares_yes:
            side = "no"
        else:
            side = "unknown"

        # Win/loss for our position
        if api_outcome == "yes":
            won = (side == "yes")
        elif api_outcome == "no":
            won = (side == "no")
        else:
            won = pnl_api > 0  # fallback

        # Match journal entries and compute per-trade PnL
        indices     = market_index.get(market_id, [])
        strategies  = set()
        total_cost  = sum(abs(journal[i].get("cost", 0) or 0) for i in indices) or 1.0
        total_trade_pnl = 0.0

        for idx in indices:
            t          = journal[idx]
            trade_side = t.get("side", "").lower()
            strategies.add(t.get("strategy", "unknown"))

            if t.get("resolved"):
                continue
            if "sell" in trade_side:
                t["resolved"] = True
                t["resolved_at"] = now.isoformat()
                journal_dirty = True
                continue

            # Per-trade outcome
            if api_outcome is not None:
                trade_won = (trade_side == "yes" and api_outcome == "yes") or \
                            (trade_side == "no"  and api_outcome == "no")
            else:
                trade_won = won

            trade_shares = abs(t.get("shares", 0) or 0)
            trade_cost   = abs(t.get("cost",   0) or 0)

            if trade_shares > 0:
                trade_pnl = (trade_shares - trade_cost) if trade_won else -trade_cost
            else:
                # No shares (e.g. SIM ghost) — proportion from API PnL
                trade_pnl = pnl_api * (trade_cost / total_cost) if total_cost > 0 else pnl_api

            total_trade_pnl += trade_pnl

            t.update({
                "resolved":    True,
                "won":         trade_won,
                "outcome":     "win" if trade_won else "loss",
                "pnl":         round(trade_pnl, 4),
                "resolved_at": now.isoformat(),
            })
            journal_dirty = True

        strategy = ", ".join(sorted(strategies)) if strategies else "unknown"

        # Update cooldown state for each strategy
        for strat in strategies:
            strat_indices = [i for i in indices if journal[i].get("strategy") == strat]
            strat_won = any(journal[i].get("won") for i in strat_indices) if strat_indices else won
            record_trade_outcome(strat, strat_won)

        # Persist resolution record
        display_pnl = total_trade_pnl if indices else pnl_api
        append_resolved({
            "market_id":  market_id,
            "question":   question,
            "side":       side,
            "won":        won,
            "pnl":        round(display_pnl, 4),
            "cost_basis": round(cost_basis, 4),
            "strategy":   strategy,
            "outcome":    "win" if won else "loss",
            "resolved_at": now.isoformat(),
        })

        emoji   = "💰" if won else "❌"
        pnl_str = f"${display_pnl:+.2f}"
        print(f"  {emoji} {question[:60]} | {strategy} | {pnl_str}")

        post_webhook(
            f"{emoji} **{strategy}** | {side.upper()} | {question[:60]}\n"
            f"{pnl_str} | {'WIN 🎉' if won else 'LOSS'}"
        )

        # Auto-redeem (LIVE only)
        if IS_SIM:
            redeemed_ids.add(market_id)
        elif pos.get("redeemable") and market_id not in redeemed_ids and _budget_ok(_start, redeemed_count):
            print(f"    💰 Attempting redemption...")
            redeemable_side = pos.get("redeemable_side") or side
            status, error = redeem_position(market_id, redeemable_side)
            if status == "already":
                redeemed_ids.add(market_id)
            elif status:
                redeemed_ids.add(market_id)
                redeemed_count += 1
                total_redeemed += pos.get("current_value", 0)
                post_webhook(f"💰 **Auto-Redeemed** | {question[:50]}... | +${pos.get('current_value',0):.2f}")
            else:
                print(f"    ⚠️  Redemption failed: {error}")

        already_reported.add(market_id)
        new_count += 1

    if journal_dirty:
        save_journal(journal)

    save_id_set(already_reported, RESOLVED_IDS_PATH)
    save_id_set(redeemed_ids, REDEEMED_IDS_PATH)

    if new_count:
        print(f"\n  📊 {new_count} new resolution(s) processed")
    else:
        print("  ✅ No new resolutions")

    # Sweep for any older redeemable positions not yet claimed (LIVE only)
    if not IS_SIM:
        all_pos    = get_all_positions()
        redeemable = [p for p in all_pos
                      if p.get("redeemable") and p.get("market_id") not in redeemed_ids]
        redeemable.sort(key=lambda p: p.get("current_value", 0), reverse=True)

        skipped = 0
        for p in redeemable:
            if not _budget_ok(_start, redeemed_count):
                skipped += 1
                continue
            mid   = p.get("market_id", "")
            q     = p.get("question", "Unknown")[:50]
            value = p.get("current_value", 0)
            rside = p.get("redeemable_side", "yes")
            print(f"  💰 Redeeming: {q}... | ${value:.2f}")
            status, error = redeem_position(mid, rside)
            if status in (True, "already"):
                redeemed_ids.add(mid)
                if status is True:
                    redeemed_count += 1
                    total_redeemed += value
            else:
                print(f"    ⚠️  Failed: {error}")

        save_id_set(redeemed_ids, REDEEMED_IDS_PATH)
        if skipped:
            print(f"  ⏳ {skipped} redemption(s) deferred to next run (budget limit)")

    if redeemed_count:
        print(f"  💰 {redeemed_count} position(s) redeemed | Total: ${total_redeemed:.2f}")


if __name__ == "__main__":
    run()
