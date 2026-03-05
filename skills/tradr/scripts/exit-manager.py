#!/usr/bin/env python3
"""exit-manager.py — Mode-aware autonomous position exit daemon for tradr.

Polls DexScreener for prices, reads each position's mode (snipe/swing/gamble/diamond/custom)
from positions.json, applies mode-specific exit rules via config.json, executes sells
via Bankr, verifies on-chain balances, and sends notifications.

No LLM required. No paid APIs. Runs as a systemd service.
"""

import json
import os
import sys
import time
import fcntl
import signal
import subprocess
import logging
import re
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

# ── Resolve skill dir (parent of scripts/) ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

# ── Load config ──
def load_config():
    config_path = os.path.join(SKILL_DIR, "config.json")
    if not os.path.exists(config_path):
        print(f"ERROR: config.json not found at {config_path}", file=sys.stderr)
        print("Run setup.sh first or copy config-template.json to config.json", file=sys.stderr)
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)

CONFIG = load_config()

# ── Paths from config ──
POSITIONS_FILE = os.path.expanduser(CONFIG.get("positions_file", "~/.openclaw/workspace/tradr/positions.json"))
TRADE_LOG = os.path.expanduser(CONFIG.get("trade_log", "~/.openclaw/workspace/tradr/trade-log.jsonl"))
LOG_FILE = os.path.expanduser(CONFIG.get("log_file", "~/.openclaw/workspace/tradr/tradr.log"))
BANKR_SH = os.path.expanduser(CONFIG.get("bankr_script", "~/.openclaw/skills/bankr/scripts/bankr.sh"))
LOCKFILE = CONFIG.get("lockfile", "/tmp/tradr-exit-manager.lock")

# ── Modes from config ──
MODES = CONFIG.get("modes", {})
DEFAULT_MODE = CONFIG.get("default_mode", "swing")

# ── Polling config ──
POLL_INTERVAL = CONFIG.get("poll_interval_seconds", 10)
DEXSCREENER_DELAY = CONFIG.get("dexscreener_delay", 1.5)
MAX_RETRIES = CONFIG.get("max_retries", 2)
RECONCILE_CYCLES = CONFIG.get("reconcile_every_cycles", 30)

# ── Wallet addresses ──
WALLETS = CONFIG.get("wallets", {})
SOL_WALLET = WALLETS.get("solana", os.environ.get("SOL_WALLET_ADDRESS", ""))
EVM_WALLET = WALLETS.get("evm", os.environ.get("EVM_WALLET_ADDRESS", ""))

# ── Notification config ──
NOTIFY_CFG = CONFIG.get("notifications", {})
NOTIFY_SCRIPT = NOTIFY_CFG.get("script")
NOTIFY_ENABLED = NOTIFY_CFG.get("enabled", True)

# ── Logging ──
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [TRADR-EXIT] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, mode="a"),
    ],
)
log = logging.getLogger("tradr-exit")
logging.Formatter.converter = time.gmtime

# ── Graceful shutdown ──
running = True

def handle_signal(signum, frame):
    global running
    log.info("Received signal %d, shutting down...", signum)
    running = False

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)


# ── HTTP helper ──
def fetch_json(url, retries=MAX_RETRIES):
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        except HTTPError as e:
            if e.code == 429 and attempt < retries:
                time.sleep(3 * (attempt + 1))
                continue
            log.warning("HTTP %d fetching %s", e.code, url)
            return None
        except (URLError, Exception) as e:
            if attempt < retries:
                time.sleep(2)
                continue
            log.warning("Failed to fetch %s: %s", url, e)
            return None
    return None


# ── DexScreener ──
def get_price(ca):
    data = fetch_json(f"https://api.dexscreener.com/latest/dex/tokens/{ca}")
    if not data or not data.get("pairs"):
        return None, None
    p = data["pairs"][0]
    price = float(p.get("priceUsd", 0) or 0)
    mcap = float(p.get("fdv", 0) or 0)
    return (price if price > 0 else None, mcap if mcap > 0 else None)


# ── On-chain verification ──
def verify_onchain_balance(ca, chain):
    try:
        if chain in ("solana", "sol"):
            return _check_solana_balance(ca)
        else:
            return _check_evm_balance(ca, chain)
    except Exception as e:
        log.warning("On-chain check failed for %s on %s: %s", ca, chain, e)
        return None

def _check_solana_balance(mint):
    if not SOL_WALLET:
        return None
    rpc_url = CONFIG.get("rpc_urls", {}).get("solana", "https://api.mainnet-beta.solana.com")
    payload = {
        "jsonrpc": "2.0", "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [SOL_WALLET, {"mint": mint}, {"encoding": "jsonParsed"}],
    }
    try:
        req = Request(rpc_url, data=json.dumps(payload).encode(),
                     headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        accounts = result.get("result", {}).get("value", [])
        total = 0.0
        for acc in accounts:
            info = acc.get("account", {}).get("data", {}).get("parsed", {}).get("info", {})
            token_amount = info.get("tokenAmount", {})
            total += float(token_amount.get("uiAmount", 0) or 0)
        return total
    except Exception as e:
        log.warning("Solana RPC error for %s: %s", mint, e)
        return None

def _check_evm_balance(ca, chain):
    if not EVM_WALLET:
        return None
    default_rpcs = {
        "base": "https://mainnet.base.org",
        "ethereum": "https://eth.llamarpc.com",
        "eth": "https://eth.llamarpc.com",
        "polygon": "https://polygon-rpc.com",
        "unichain": "https://mainnet.unichain.org",
    }
    custom_rpcs = CONFIG.get("rpc_urls", {})
    rpc_url = custom_rpcs.get(chain.lower(), default_rpcs.get(chain.lower(), default_rpcs["base"]))

    wallet_padded = EVM_WALLET.lower().replace("0x", "").zfill(64)
    call_data = "0x70a08231" + wallet_padded

    payload = {
        "jsonrpc": "2.0", "id": 1,
        "method": "eth_call",
        "params": [{"to": ca, "data": call_data}, "latest"],
    }
    try:
        req = Request(rpc_url, data=json.dumps(payload).encode(),
                     headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        hex_balance = result.get("result", "0x0")
        return int(hex_balance, 16)
    except Exception as e:
        log.warning("EVM RPC error for %s on %s: %s", ca, chain, e)
        return None


# ── Notifications ──
def notify(text, level="info", notify_type="info"):
    """Send notification. notify_type is one of: buy, sell, confluence, error, info."""
    if not NOTIFY_ENABLED:
        return
    log.info("[NOTIFY:%s:%s] %s", level, notify_type, text)
    if NOTIFY_SCRIPT:
        script = os.path.expanduser(NOTIFY_SCRIPT)
        if os.path.exists(script):
            try:
                subprocess.run([script, level, notify_type, text], capture_output=True, timeout=15)
            except Exception as e:
                log.warning("Notification script failed: %s", e)


# ── Bankr execution ──
def bankr_sell(prompt):
    log.info("Executing bankr: %s", prompt)
    try:
        env = os.environ.copy()
        env["BANKR_ALLOW_TRADE"] = "1"  # Bypass trade guard for mechanical pipeline
        env["BANKR_ALLOW_SELL"] = "1"   # Legacy sell override
        result = subprocess.run(
            [BANKR_SH, prompt],
            capture_output=True, text=True, timeout=330,
            env=env,
        )
        stdout = result.stdout.strip()
        if result.returncode == 0 and stdout:
            try:
                data = json.loads(stdout)
                return True, data.get("response", stdout)
            except json.JSONDecodeError:
                return True, stdout
        else:
            stderr = result.stderr.strip()
            return False, stderr or stdout or "bankr failed with no output"
    except subprocess.TimeoutExpired:
        return False, "bankr.sh timed out"
    except Exception as e:
        return False, str(e)


# ── Positions I/O ──
def load_positions():
    if not os.path.exists(POSITIONS_FILE):
        return {}
    try:
        with open(POSITIONS_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def save_positions(positions):
    os.makedirs(os.path.dirname(POSITIONS_FILE), exist_ok=True)
    tmp = POSITIONS_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(positions, f, indent=2)
    os.replace(tmp, POSITIONS_FILE)


# ── Trade log ──
def log_trade(token, ca, action, amount, chain, mode, reason, status, response):
    tx_hash = ""
    m = re.search(r'[0-9a-fA-F]{64}', response or "")
    if m:
        tx_hash = m.group(0)
        if chain not in ("solana", "sol") and not tx_hash.startswith("0x"):
            tx_hash = "0x" + tx_hash
    entry = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "token": token,
        "ca": ca,
        "chain": chain,
        "action": action,
        "amount": str(amount),
        "mode": mode,
        "reason": reason,
        "status": status,
        "tx": tx_hash,
        "response": (response or "")[:200],
    }
    os.makedirs(os.path.dirname(TRADE_LOG), exist_ok=True)
    with open(TRADE_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    log.info("Trade logged: %s %s — %s (%s) [mode=%s]", action, token, status, reason, mode)


# ── Get mode params for a position ──
def get_mode_params(pos):
    """Return exit params dict for the position's mode. Falls back to default_mode, then swing."""
    mode = pos.get("mode", DEFAULT_MODE)
    params = MODES.get(mode)
    if not params:
        log.warning("Unknown mode '%s', falling back to '%s'", mode, DEFAULT_MODE)
        params = MODES.get(DEFAULT_MODE, MODES.get("swing", {}))
    return mode, params


# ── Exit execution ──
def execute_partial_exit(positions, ca, pos, token, chain, entry_mcap, mcap, multiple):
    mode, params = get_mode_params(pos)
    tp_size = params.get("take_profit_1_size", 0.3)
    sell_pct = int(tp_size * 100)
    prompt = f"sell {sell_pct}% of my {ca}"
    if chain:
        prompt += f" on {chain}"

    log.info("%s: TAKE PROFIT at %.2fx — selling %d%% [mode=%s]", token, multiple, sell_pct, mode)
    notify(f"{token} hit {multiple:.1f}x — selling {sell_pct}% [mode={mode}]", "trade", "sell")

    success, response = bankr_sell(prompt)
    if success:
        pos["first_exit_done"] = True
        pos.pop("_sell_retries", None)

        # Track remaining position value
        buy_usd = pos.get("buy_amount_usd", 0)
        remaining = pos.get("remaining_usd", buy_usd)
        sold_usd = remaining * tp_size
        pos["remaining_usd"] = round(remaining - sold_usd, 2)

        log.info("%s: TP executed — sold $%.2f, remaining $%.2f — %s",
                 token, sold_usd, pos["remaining_usd"], (response or "")[:100])
        notify(
            f"Sold {sell_pct}% of {token} at {multiple:.1f}x "
            f"(Entry ${entry_mcap:,.0f} -> ${mcap:,.0f}) [{mode}] | "
            f"Sold ~${sold_usd:.2f}, remaining ~${pos['remaining_usd']:.2f}",
            "trade", "sell"
        )
        log_trade(token, ca, f"SELL_{sell_pct}PCT", round(sold_usd, 2),
                 chain, mode, f"TP1_{multiple:.2f}x", "completed", response)
        _verify_after_trade(ca, chain, token, "partial sell")
    else:
        retries = pos.get("_sell_retries", 0) + 1
        pos["_sell_retries"] = retries
        log.error("%s: TP FAILED (attempt %d) — %s", token, retries, response)
        if retries <= 3:
            notify(f"{token} TP sell FAILED (attempt {retries}): {response}", "error", "error")
        elif retries == 10:
            notify(f"{token} TP sell FAILED {retries} times — needs manual intervention: {response}", "error", "error")

    save_positions(positions)
    time.sleep(DEXSCREENER_DELAY)

def execute_full_exit(positions, ca, pos, token, chain, entry_mcap, mcap, multiple, peak_mcap, reason):
    mode, params = get_mode_params(pos)
    prompt = f"sell all of my {ca}"
    if chain:
        prompt += f" on {chain}"

    notify(f"{token} {reason} at {multiple:.1f}x — selling all [{mode}]", "trade", "sell")

    success, response = bankr_sell(prompt)
    if success:
        pos["closed"] = True
        pos.pop("_sell_retries", None)
        pos["close_ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        pos["close_reason"] = reason
        pos["close_mcap"] = mcap
        pos["close_multiple"] = round(multiple, 3)

        # P&L based on remaining position value (accounts for partial sells)
        remaining = pos.get("remaining_usd", pos.get("buy_amount_usd", 0))
        buy_usd = pos.get("buy_amount_usd", 0)
        # Estimated P&L: what we got from partial sells + final exit value - original buy
        # Partial sell value: (buy_usd - remaining) * avg_multiple_at_tp (approximate with TP mult)
        # Final exit value: remaining * multiple
        # Simplified: remaining * multiple + (buy_usd - remaining) * tp_mult - buy_usd
        # But we don't track the exact TP price, so approximate:
        # Total return = remaining * multiple (from final sell)
        #              + already-sold portion at whatever price (we can't perfectly reconstruct)
        # Best approximation: use remaining for the final piece
        final_value = remaining * multiple
        already_sold_value = buy_usd - remaining  # what was sold at TP (in original USD terms)
        tp_mult = params.get("take_profit_1")
        if tp_mult and already_sold_value > 0:
            already_sold_return = already_sold_value * tp_mult
        else:
            already_sold_return = already_sold_value  # fallback: assume sold at 1x

        est_pnl = (final_value + already_sold_return) - buy_usd
        pos["est_pnl_usd"] = round(est_pnl, 2)
        pos["remaining_usd"] = 0

        log.info("%s: CLOSED — %s at %.2fx (est P&L: $%.2f) [mode=%s]", token, reason, multiple, est_pnl, mode)
        peak_mult = peak_mcap / entry_mcap if entry_mcap > 0 else 0
        pnl_sign = "+" if est_pnl >= 0 else ""
        notify(
            f"{token} closed at {multiple:.2f}x ({reason}) [{mode}] | "
            f"Entry ${entry_mcap:,.0f} -> Peak ${peak_mcap:,.0f} ({peak_mult:.1f}x) -> Exit ${mcap:,.0f} | "
            f"P&L: {pnl_sign}${est_pnl:.2f}",
            "trade", "sell"
        )

        log_trade(token, ca, "SELL_ALL", round(remaining, 2), chain, mode, reason, "completed", response)
        _verify_after_trade(ca, chain, token, "full exit")
    else:
        retries = pos.get("_sell_retries", 0) + 1
        pos["_sell_retries"] = retries
        log.error("%s: EXIT FAILED (%s, attempt %d) — %s", token, reason, retries, response)
        if retries <= 3:
            notify(f"{token} exit FAILED ({reason}, attempt {retries}): {response}", "error", "error")
        elif retries == 10:
            notify(f"{token} exit FAILED {retries} times — needs manual intervention: {response}", "error", "error")

    save_positions(positions)
    time.sleep(DEXSCREENER_DELAY)

def _verify_after_trade(ca, chain, token, trade_type):
    time.sleep(5)
    balance = verify_onchain_balance(ca, chain)
    if balance is not None:
        if balance == 0:
            log.info("%s: on-chain verified — zero balance after %s", token, trade_type)
        else:
            log.info("%s: on-chain balance %s after %s", token, balance, trade_type)
    else:
        log.warning("%s: could not verify on-chain balance", token)


# ── Main loop ──
def check_positions():
    positions = load_positions()
    if not positions:
        return

    open_positions = {ca: pos for ca, pos in positions.items() if not pos.get("closed", True)}
    if not open_positions:
        return

    any_changes = False

    # Protected tokens — never sell (e.g. token gate holdings)
    protected = [t.lower() for t in CONFIG.get("pipeline", {}).get("protected_tokens", [])]

    for ca, pos in open_positions.items():
        if ca.lower() in protected:
            continue
        token = pos.get("token", "???")
        chain = pos.get("chain", "base")
        mode, params = get_mode_params(pos)

        price, mcap = get_price(ca)
        if not price or not mcap:
            log.warning("%s: no price data, skipping", token)
            continue

        entry_mcap = pos.get("entry_mcap", 0)
        if not entry_mcap or entry_mcap <= 0:
            log.warning("%s: no entry_mcap, skipping", token)
            continue

        # Update current + peak
        pos["current_mcap"] = mcap
        pos["current_price"] = price
        old_peak = pos.get("peak_mcap", 0)
        if mcap > old_peak:
            pos["peak_mcap"] = mcap
        any_changes = True

        multiple = mcap / entry_mcap
        peak_mcap = pos.get("peak_mcap", mcap)
        first_exit_done = pos.get("first_exit_done", False)


        # ── Hard stop (mode-specific) — stop_at is the actual multiplier ──
        # After TP, hard stop moves to breakeven (1.0x) to protect profits
        stop_at = params.get("stop_at")
        effective_stop = stop_at
        if stop_at and first_exit_done:
            effective_stop = max(stop_at, 1.0)  # at least breakeven after TP
        if effective_stop:
            if multiple < effective_stop:
                log.info("%s: HARD STOP at %.2fx (threshold %.2fx) [mode=%s]", token, multiple, stop_at, mode)
                execute_full_exit(positions, ca, pos, token, chain, entry_mcap, mcap,
                                multiple, peak_mcap, f"HARD_STOP_{multiple:.2f}x")
                continue

        # ── Take profit (mode-specific) ──
        tp_mult = params.get("take_profit_1")
        if tp_mult and not first_exit_done and multiple >= tp_mult:
            execute_partial_exit(positions, ca, pos, token, chain, entry_mcap, mcap, multiple)
            continue

        # ── Trailing stop (mode-specific, with optional tiered logic) ──
        # Fires after TP, OR if mode has no TP (e.g. gamble) once price exceeds entry
        trailing = params.get("trailing_stop")
        has_tp = bool(params.get("take_profit_1"))
        trailing_active = first_exit_done or (not has_tp and multiple >= 1.0)
        if trailing and trailing_active and peak_mcap > 0:
            trailing_tight = params.get("trailing_stop_tight")
            tight_below = params.get("trailing_stop_tight_below")

            if trailing_tight and tight_below and entry_mcap > 0:
                peak_mult = peak_mcap / entry_mcap
                if peak_mult >= tight_below:
                    trail_pct = trailing
                    trail_label = "wide"
                else:
                    trail_pct = trailing_tight
                    trail_label = "tight"
            else:
                trail_pct = trailing
                trail_label = "flat"

            drawdown = 1 - (mcap / peak_mcap)
            if drawdown >= trail_pct:
                peak_mult = peak_mcap / entry_mcap if entry_mcap > 0 else 0
                log.info("%s: TRAILING STOP (%s %.0f%%) — %.0f%% from peak [mode=%s]",
                         token, trail_label, trail_pct * 100, drawdown * 100, mode)
                execute_full_exit(positions, ca, pos, token, chain, entry_mcap, mcap,
                                multiple, peak_mcap,
                                f"TRAILING_{trail_label}_{drawdown:.0%}_from_{peak_mult:.1f}x_peak")
                continue

        # ── Diamond mode / no triggers: no mechanical exits ──
        # Log periodic status for debugging (every ~5 min = 30 cycles at 10s)
        status_key = f"_status_cycles_{ca}"
        if not hasattr(check_positions, '_counters'):
            check_positions._counters = {}
        check_positions._counters[status_key] = check_positions._counters.get(status_key, 0) + 1
        if check_positions._counters[status_key] % 30 == 0:
            peak_mult = peak_mcap / entry_mcap if entry_mcap > 0 else 0
            log.info("%s: status — %.2fx (peak %.2fx, mcap $%s) first_exit=%s trail_active=%s [%s]",
                     token, multiple, peak_mult, f"{mcap:,.0f}", first_exit_done, trailing_active, mode)

        time.sleep(DEXSCREENER_DELAY)

    if any_changes:
        save_positions(positions)


def reconcile_positions():
    positions = load_positions()
    open_pos = {ca: pos for ca, pos in positions.items() if not pos.get("closed", True)}
    if not open_pos:
        return

    mismatches = []
    for ca, pos in open_pos.items():
        token = pos.get("token", "???")
        chain = pos.get("chain", "base")
        balance = verify_onchain_balance(ca, chain)

        if balance is not None and balance == 0:
            mode = pos.get("mode", DEFAULT_MODE)
            mismatches.append(f"{token} ({ca[:8]}...): open but wallet empty [mode={mode}]")
            pos["closed"] = True
            pos["close_ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            pos["close_reason"] = "RECONCILED_EMPTY"
            pos["remaining_usd"] = 0
            log.warning("%s: auto-closed — on-chain balance is zero (possible external sell via Bankr or MEV)", token)
            log_trade(token, ca, "RECONCILED_CLOSE", 0, chain, mode,
                     "RECONCILED_EMPTY", "completed", "wallet empty — exit not initiated by exit-manager")

    if mismatches:
        save_positions(positions)
        notify("Position reconciliation: " + "; ".join(mismatches), "warning", "info")


def main():
    log.info("tradr exit-manager starting (poll: %ds, reconcile: every %d cycles)", POLL_INTERVAL, RECONCILE_CYCLES)
    log.info("Modes loaded: %s (default: %s)", list(MODES.keys()), DEFAULT_MODE)
    for mode_name, mode_params in MODES.items():
        stop = f"{mode_params['stop_at']}x" if mode_params.get("stop_at") else "none"
        tp = f"{mode_params['take_profit_1']}x" if mode_params.get("take_profit_1") else "none"
        trail = f"{mode_params['trailing_stop']*100:.0f}%" if mode_params.get("trailing_stop") else "none"
        log.info("  %s: stop=%s tp=%s trail=%s", mode_name, stop, tp, trail)
    log.info("Wallets: EVM=%s SOL=%s",
             (EVM_WALLET[:10] + "...") if EVM_WALLET else "N/A",
             (SOL_WALLET[:10] + "...") if SOL_WALLET else "N/A")

    cycle = 0
    while running:
        try:
            check_positions()
        except Exception as e:
            log.error("Error in check_positions: %s", e, exc_info=True)

        cycle += 1
        if cycle % RECONCILE_CYCLES == 0:
            try:
                reconcile_positions()
            except Exception as e:
                log.error("Error in reconcile: %s", e, exc_info=True)

        for _ in range(POLL_INTERVAL * 2):
            if not running:
                break
            time.sleep(0.5)

    log.info("tradr exit-manager stopped")


if __name__ == "__main__":
    lock_fp = open(LOCKFILE, "w")
    try:
        fcntl.flock(lock_fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("Another tradr exit-manager instance is running", file=sys.stderr)
        sys.exit(1)

    lock_fp.write(str(os.getpid()))
    lock_fp.flush()

    try:
        main()
    finally:
        fcntl.flock(lock_fp, fcntl.LOCK_UN)
        lock_fp.close()
        try:
            os.remove(LOCKFILE)
        except OSError:
            pass
