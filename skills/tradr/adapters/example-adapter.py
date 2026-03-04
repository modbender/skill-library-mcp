#!/usr/bin/env python3
"""example-adapter.py — Sample signal adapter for tradr.

A signal adapter watches a signal source and feeds trades into tradr.
This example demonstrates the interface. Replace the signal source with yours.

Usage:
    python3 example-adapter.py

The adapter contract is simple:
    1. Watch your signal source (any method: websocket, polling, file, webhook)
    2. When you detect a trade signal, call tradr-enter.py with:
       - ca: contract address (required)
       - score: confidence score 0-10 (maps to position sizing via config)
       - chain: solana/base/ethereum/polygon/unichain (auto-detected if omitted)
       - token: human-readable name (optional, for logs)

That's it. tradr handles sizing, entry guards, execution, position tracking,
exit management, and notifications.
"""

import json
import os
import subprocess
import sys
import time

# ── Configuration ──────────────────────────────────────────────
# Point these at your tradr installation
TRADR_DIR = os.path.expanduser("~/.openclaw/workspace/tradr")
TRADR_ENTER = os.path.join(TRADR_DIR, "scripts", "tradr-enter.py")

# Your signal source config (replace with your own)
POLL_INTERVAL = 30  # seconds between checks


# ── Signal Source (replace this) ───────────────────────────────

def get_signals():
    """Poll your signal source and return a list of signals.

    Each signal is a dict with:
        ca       (str, required): Contract address
        score    (int, required): Confidence score 0-10
                                  Maps to position size via tradr config:
                                    score >= 8  → $200 (or your config value)
                                    score >= 5  → $150
                                    score >= 3  → $100
                                    score >= 0  → $50
        chain    (str, optional): solana/base/ethereum/polygon/unichain
                                  Auto-detected from CA format if omitted
        token    (str, optional): Human-readable name/ticker

    Return an empty list if no signals.
    """
    # ── EXAMPLE: Replace this with your actual signal source ──
    #
    # Ideas for signal sources:
    #   - Twitter/X API: watch KOL accounts for token mentions
    #   - On-chain: monitor whale wallets for new buys
    #   - Telegram: parse alpha group messages for CAs
    #   - DEX: watch for unusual volume spikes
    #   - Aggregator: combine multiple sources with scoring
    #
    # Example static signal (remove this):
    # return [{
    #     "ca": "0x1234567890abcdef1234567890abcdef12345678",
    #     "score": 5,
    #     "chain": "base",
    #     "token": "EXAMPLE",
    # }]

    return []


# ── Feed signals to tradr ──────────────────────────────────────

def feed_signal(signal):
    """Pass a signal to tradr-enter.py and return the result."""
    ca = signal["ca"]
    score = signal.get("score", 0)
    chain = signal.get("chain")
    token = signal.get("token")

    cmd = ["python3", TRADR_ENTER, ca, "--score", str(score)]
    if chain:
        cmd += ["--chain", chain]
    if token:
        cmd += ["--token", token]

    print(f"[ADAPTER] Feeding signal: {token or ca[:12]} | score={score} | chain={chain or 'auto'}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=360)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get("success"):
                trade = data["trade"]
                print(f"[ADAPTER] ✓ Entry executed: ${trade['size_usd']:.2f} | mode={trade['mode']} | mcap={trade['entry_mcap']:,.0f}")
            else:
                print(f"[ADAPTER] ✗ Rejected: {data.get('error', 'unknown')}")
            return data
        else:
            err = result.stderr.strip() or result.stdout.strip()
            print(f"[ADAPTER] ✗ Failed: {err[:200]}")
            return {"success": False, "error": err}
    except subprocess.TimeoutExpired:
        print(f"[ADAPTER] ✗ Timeout waiting for tradr-enter.py")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        print(f"[ADAPTER] ✗ Error: {e}")
        return {"success": False, "error": str(e)}


# ── Main loop ──────────────────────────────────────────────────

def main():
    print(f"[ADAPTER] Starting signal adapter")
    print(f"[ADAPTER] tradr entry: {TRADR_ENTER}")
    print(f"[ADAPTER] Poll interval: {POLL_INTERVAL}s")
    print()

    if not os.path.exists(TRADR_ENTER):
        print(f"[ADAPTER] ERROR: tradr-enter.py not found at {TRADR_ENTER}")
        print(f"[ADAPTER] Run tradr setup.sh first")
        sys.exit(1)

    while True:
        try:
            signals = get_signals()
            for signal in signals:
                if not signal.get("ca"):
                    continue
                feed_signal(signal)
                time.sleep(1)  # small delay between signals
        except KeyboardInterrupt:
            print("\n[ADAPTER] Stopped")
            break
        except Exception as e:
            print(f"[ADAPTER] Error: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
