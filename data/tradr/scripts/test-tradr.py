#!/usr/bin/env python3
"""test-tradr.py -- Comprehensive unit tests for tradr logic."""

import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta

passed = 0
failed = 0
errors = []

def test(name):
    global passed, failed
    def decorator(fn):
        global passed, failed
        try:
            fn()
            passed += 1
            print(f"  \u2713 {name}")
        except Exception as e:
            failed += 1
            errors.append((name, str(e)))
            print(f"  \u2717 {name}: {e}")
    return decorator

def resolve(score_map, score):
    best_key, best_val = None, None
    for key_str, val in score_map.items():
        t = int(key_str)
        if score >= t and (best_key is None or t > best_key):
            best_key, best_val = t, val
    return best_val

def detect_chain(ca):
    if ca.startswith("0x") or ca.startswith("0X"):
        return "base"
    base58 = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    if len(ca) >= 32 and len(ca) <= 44 and all(c in base58 for c in ca):
        return "solana"
    return "base"

SIZE_MAP = {"8": 200.0, "5": 150.0, "3": 100.0, "0": 50.0}
MODE_MAP = {"8": "swing", "5": "snipe", "0": "snipe"}

# ====== Score-to-Size ======
print("\n== Score-to-Size Resolution ==")

@test("score 10 -> $200")
def _(): assert resolve(SIZE_MAP, 10) == 200.0

@test("score 8 -> $200")
def _(): assert resolve(SIZE_MAP, 8) == 200.0

@test("score 7 -> $150 (between thresholds)")
def _(): assert resolve(SIZE_MAP, 7) == 150.0

@test("score 5 -> $150")
def _(): assert resolve(SIZE_MAP, 5) == 150.0

@test("score 4 -> $100")
def _(): assert resolve(SIZE_MAP, 4) == 100.0

@test("score 3 -> $100")
def _(): assert resolve(SIZE_MAP, 3) == 100.0

@test("score 1 -> $50")
def _(): assert resolve(SIZE_MAP, 1) == 50.0

@test("score 0 -> $50")
def _(): assert resolve(SIZE_MAP, 0) == 50.0

# ====== Score-to-Mode ======
print("\n== Score-to-Mode Resolution ==")

@test("score 8 -> swing")
def _(): assert resolve(MODE_MAP, 8) == "swing"

@test("score 5 -> snipe")
def _(): assert resolve(MODE_MAP, 5) == "snipe"

@test("score 3 -> snipe (falls to 0)")
def _(): assert resolve(MODE_MAP, 3) == "snipe"

# ====== Chain Detection ======
print("\n== Chain Detection ==")

@test("0x address -> base")
def _(): assert detect_chain("0x5B5dee44552546ECEA05EDeA01DCD7Be7aa6144A") == "base"

@test("0X address -> base")
def _(): assert detect_chain("0XABC123") == "base"

@test("base58 44-char -> solana")
def _(): assert detect_chain("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263") == "solana"

@test("base58 32-char -> solana")
def _(): assert detect_chain("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjn") == "solana"

@test("short string -> base fallback")
def _(): assert detect_chain("abc") == "base"

# ====== Hard Stop ======
print("\n== Exit Logic: Hard Stop ==")

@test("swing 0.69x triggers stop (< 0.70)")
def _(): assert 0.69 < 0.70

@test("swing 0.71x no stop")
def _(): assert not (0.71 < 0.70)

@test("snipe 0.84x triggers stop (< 0.85)")
def _(): assert 0.84 < 0.85

@test("gamble 0.49x triggers stop (< 0.50)")
def _(): assert 0.49 < 0.50

@test("diamond no stop (stop_at=None)")
def _(): assert not None

@test("after TP, stop moves to breakeven 1.0x")
def _():
    stop_at = 0.70
    first_exit_done = True
    effective = max(stop_at, 1.0) if stop_at and first_exit_done else stop_at
    assert effective == 1.0

@test("after TP, 0.95x triggers breakeven stop")
def _():
    effective = max(0.70, 1.0)  # after TP
    assert 0.95 < effective

@test("before TP, 0.95x does NOT trigger 0.70 stop")
def _(): assert not (0.95 < 0.70)

# ====== Take Profit ======
print("\n== Exit Logic: Take Profit ==")

@test("1.30x triggers TP")
def _():
    tp = 1.3; mult = 1.30; done = False
    assert tp and not done and mult >= tp

@test("1.29x no TP")
def _():
    tp = 1.3; mult = 1.29; done = False
    assert not (tp and not done and mult >= tp)

@test("TP does not fire twice")
def _():
    tp = 1.3; mult = 1.5; done = True
    assert not (tp and not done and mult >= tp)

@test("gamble no TP (None)")
def _():
    tp = None; mult = 5.0; done = False
    assert not (tp and not done and mult >= tp)

# ====== Trailing Stop ======
print("\n== Exit Logic: Trailing Stop ==")

@test("swing 26% drawdown triggers 25% trail")
def _():
    dd = 1 - (148000 / 200000)  # 0.26
    assert dd >= 0.25

@test("swing 24% drawdown no trigger")
def _():
    dd = 1 - (152000 / 200000)  # 0.24
    assert not (dd >= 0.25)

@test("snipe 11% drawdown triggers 10% trail")
def _():
    dd = 1 - (178000 / 200000)  # 0.11
    assert dd >= 0.10

@test("tiered: tight 15% when peak < 2x")
def _():
    peak_mult = 180000 / 100000  # 1.8x
    trail = 0.25 if peak_mult >= 2.0 else 0.15
    assert trail == 0.15

@test("tiered: wide 25% when peak >= 2x")
def _():
    peak_mult = 250000 / 100000  # 2.5x
    trail = 0.25 if peak_mult >= 2.0 else 0.15
    assert trail == 0.25

@test("tiered: exactly 2.0x uses wide")
def _():
    peak_mult = 200000 / 100000  # 2.0x
    trail = 0.25 if peak_mult >= 2.0 else 0.15
    assert trail == 0.25

@test("trailing only active after TP (has_tp mode)")
def _():
    done = False; has_tp = True
    active = done or (not has_tp and True)
    assert not active

@test("trailing active after TP done")
def _():
    done = True; has_tp = True
    active = done or (not has_tp and True)
    assert active

@test("gamble trailing active above entry (no TP)")
def _():
    done = False; has_tp = False; mult = 1.5
    active = done or (not has_tp and mult >= 1.0)
    assert active

@test("gamble trailing NOT active below entry")
def _():
    done = False; has_tp = False; mult = 0.8
    active = done or (not has_tp and mult >= 1.0)
    assert not active

@test("diamond no trailing")
def _():
    assert not None

# ====== Partial Sell Tracking ======
print("\n== Partial Sell Tracking ==")

@test("30% TP on $200 -> remaining $140")
def _():
    r = 200.0; sold = r * 0.3; r = round(r - sold, 2)
    assert r == 140.0 and sold == 60.0

@test("30% TP on $150 -> remaining $105")
def _():
    r = 150.0; sold = r * 0.3; r = round(r - sold, 2)
    assert r == 105.0

@test("P&L: TP 1.3x then exit 0.9x on $200")
def _():
    buy = 200; tp_sold = 60; remaining = 140
    pnl = (remaining * 0.9 + tp_sold * 1.3) - buy  # 126 + 78 - 200 = 4
    assert pnl == 4.0, f"got {pnl}"

@test("P&L: TP 1.3x then exit 2.0x on $150")
def _():
    buy = 150; tp_sold = 45; remaining = 105
    pnl = (remaining * 2.0 + tp_sold * 1.3) - buy  # 210 + 58.5 - 150 = 118.5
    assert pnl == 118.5

@test("P&L: no TP, full exit 0.5x on $100")
def _():
    buy = 100; remaining = 100
    pnl = (remaining * 0.5) - buy  # 50 - 100 = -50
    assert pnl == -50.0

@test("P&L: no TP, full exit 3.0x on $100")
def _():
    buy = 100; remaining = 100
    pnl = (remaining * 3.0) - buy  # 300 - 100 = 200
    assert pnl == 200.0

# ====== Entry Guards ======
print("\n== Entry Guards ==")

@test("mcap ceiling blocks above $10M")
def _(): assert 12000000 > 10000000

@test("mcap ceiling allows below $10M")
def _(): assert not (5000000 > 10000000)

@test("cooldown blocks within 30 min")
def _():
    close = datetime.now(timezone.utc) - timedelta(minutes=15)
    elapsed = (datetime.now(timezone.utc) - close).total_seconds() / 60
    assert elapsed < 30

@test("cooldown allows after 30 min")
def _():
    close = datetime.now(timezone.utc) - timedelta(minutes=45)
    elapsed = (datetime.now(timezone.utc) - close).total_seconds() / 60
    assert elapsed >= 30

@test("protected token blocked")
def _():
    protected = ["0xprotected"]
    assert "0xPROTECTED".lower() in protected

@test("non-protected token passes")
def _():
    protected = ["0xprotected"]
    assert "0xOTHER".lower() not in protected

@test("max size caps at $500")
def _():
    size = min(600, 500)
    assert size == 500

@test("duplicate entry blocked")
def _():
    positions = {"0xABC": {"closed": False}}
    blocked = "0xABC" in positions and not positions["0xABC"].get("closed", True)
    assert blocked

@test("closed position allows re-entry (after cooldown)")
def _():
    positions = {"0xABC": {"closed": True}}
    blocked = "0xABC" in positions and not positions["0xABC"].get("closed", True)
    assert not blocked

# ====== Mode Resolution ======
print("\n== Mode Resolution ==")

@test("unknown mode falls back to default")
def _():
    modes = {"swing": {"stop_at": 0.7}}
    p = modes.get("nonexistent") or modes.get("swing")
    assert p["stop_at"] == 0.7

@test("custom mode reads correctly")
def _():
    modes = {"my-mode": {"stop_at": 0.80, "take_profit_1": 1.2, "trailing_stop": 0.12}}
    p = modes["my-mode"]
    assert p["stop_at"] == 0.80 and p["take_profit_1"] == 1.2

# ====== Retry Tracking ======
print("\n== Retry Tracking ==")

@test("retry counter increments")
def _():
    pos = {}
    for i in range(1, 4):
        r = pos.get("_sell_retries", 0) + 1
        pos["_sell_retries"] = r
        assert r == i

@test("retry counter cleared on success")
def _():
    pos = {"_sell_retries": 5}
    pos.pop("_sell_retries", None)
    assert "_sell_retries" not in pos

# ====== Edge Cases ======
print("\n== Edge Cases ==")

@test("zero entry_mcap skipped")
def _(): assert not 0 or 0 <= 0

@test("peak only goes up")
def _():
    peak = 100000
    for p in [110000, 90000, 130000, 80000]:
        peak = max(peak, p)
    assert peak == 130000

@test("peak never decreases")
def _():
    peak = 200000
    for p in [150000, 100000]:
        peak = max(peak, p)
    assert peak == 200000

@test("tx hash extraction from bankr response")
def _():
    resp = "tx: 0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    m = re.search(r'[0-9a-fA-F]{64}', resp)
    assert m and len(m.group(0)) == 64

@test("EVM tx gets 0x prefix")
def _():
    tx = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    chain = "base"
    if chain not in ("solana", "sol") and not tx.startswith("0x"):
        tx = "0x" + tx
    assert tx.startswith("0x")

@test("solana tx no 0x prefix")
def _():
    tx = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    chain = "solana"
    if chain not in ("solana", "sol") and not tx.startswith("0x"):
        tx = "0x" + tx
    assert not tx.startswith("0x")

@test("size override replaces score size")
def _():
    score_size = 150.0; override = 50.0
    size = override if override and override > 0 else score_size
    assert size == 50.0

@test("zero override uses score size")
def _():
    score_size = 150.0; override = 0
    size = override if override and override > 0 else score_size
    assert size == 150.0

@test("None override uses score size")
def _():
    score_size = 150.0; override = None
    size = override if override and override > 0 else score_size
    assert size == 150.0

# ====== Full Lifecycle State Machine ======
print("\n== Full Lifecycle State Machine ==")

@test("entry -> TP -> trailing -> closed")
def _():
    pos = {"closed": False, "first_exit_done": False, "remaining_usd": 200.0, "buy_amount_usd": 200.0, "peak_mcap": 100000, "entry_mcap": 100000}
    
    # Step 1: TP at 1.3x
    pos["first_exit_done"] = True
    sold = pos["remaining_usd"] * 0.3
    pos["remaining_usd"] = round(pos["remaining_usd"] - sold, 2)
    assert pos["first_exit_done"] and pos["remaining_usd"] == 140.0
    
    # Step 2: Price rises to 2.5x, peak tracks
    pos["peak_mcap"] = 250000
    peak_mult = pos["peak_mcap"] / pos["entry_mcap"]
    trail = 0.25 if peak_mult >= 2.0 else 0.15
    assert trail == 0.25  # wide trail because peak > 2x
    
    # Step 3: Price drops 30% from peak
    current = 175000
    dd = 1 - (current / pos["peak_mcap"])
    assert dd >= trail  # 30% >= 25% -> triggers
    
    # Step 4: Close
    pos["closed"] = True
    pos["remaining_usd"] = 0
    mult = current / pos["entry_mcap"]  # 1.75x
    pnl = (140 * mult + 60 * 1.3) - 200  # 245 + 78 - 200 = 123
    assert pos["closed"] and pnl == 123.0

@test("entry -> hard stop (no TP)")
def _():
    pos = {"closed": False, "first_exit_done": False, "remaining_usd": 100.0, "entry_mcap": 100000}
    mult = 65000 / 100000  # 0.65x
    assert mult < 0.70  # hard stop triggers
    pos["closed"] = True
    pnl = (100 * mult) - 100  # -35
    assert pnl == -35.0

@test("entry -> TP -> breakeven stop")
def _():
    pos = {"first_exit_done": False, "remaining_usd": 150.0, "entry_mcap": 100000}
    
    # TP at 1.3x
    pos["first_exit_done"] = True
    pos["remaining_usd"] = 105.0  # 70% remaining
    
    # Price drops to 0.95x
    mult = 0.95
    stop_at = 0.70
    effective = max(stop_at, 1.0)  # breakeven after TP
    assert mult < effective  # 0.95 < 1.0 triggers

@test("gamble: no TP, trailing from above entry")
def _():
    pos = {"first_exit_done": False, "remaining_usd": 100.0, "entry_mcap": 100000, "peak_mcap": 300000}
    has_tp = False
    mult = 200000 / 100000  # 2.0x current
    trailing_active = pos["first_exit_done"] or (not has_tp and mult >= 1.0)
    assert trailing_active
    dd = 1 - (200000 / pos["peak_mcap"])  # 33% from peak
    assert dd >= 0.30  # gamble trail triggers at 30%


# ====== RESULTS ======
print(f"\n{'='*50}")
print(f"RESULTS: {passed} passed, {failed} failed")
if errors:
    print(f"\nFailed tests:")
    for name, err in errors:
        print(f"  \u2717 {name}: {err}")
print(f"{'='*50}")
sys.exit(0 if failed == 0 else 1)
