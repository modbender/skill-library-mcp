#!/usr/bin/env python3
"""tradr-enter.py -- Trade entry execution engine.

Accepts a contract address (CA) + score, determines position size and exit mode,
executes buy via Bankr, writes position to positions.json, and logs the trade.

No signal generation -- purely execution.

Usage:
    tradr-enter.py <ca> [--score N] [--chain CHAIN] [--mode MODE] [--token NAME]
"""

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
import logging
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

# -- Resolve skill dir (parent of scripts/) --
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

# -- Logging (basic stderr until config loaded) --
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ENTER] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger("tradr-enter")
logging.Formatter.converter = time.gmtime


# -- Config --
def load_config():
    config_path = os.path.join(SKILL_DIR, "config.json")
    if not os.path.exists(config_path):
        log.error("config.json not found at %s", config_path)
        log.error("Run setup.sh first or copy config-template.json to config.json")
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


# -- HTTP helper --
def fetch_json(url, retries=2):
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


# -- DexScreener --
def get_price(ca):
    """Returns (price_usd, market_cap) or (None, None)."""
    data = fetch_json(f"https://api.dexscreener.com/latest/dex/tokens/{ca}")
    if not data or not data.get("pairs"):
        return None, None
    p = data["pairs"][0]
    price = float(p.get("priceUsd", 0) or 0)
    mcap = float(p.get("fdv", 0) or 0)
    return (price if price > 0 else None, mcap if mcap > 0 else None)


# -- Chain detection --
def detect_chain(ca):
    if ca.startswith("0x") or ca.startswith("0X"):
        return "base"
    base58_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    if len(ca) >= 32 and len(ca) <= 44 and all(c in base58_chars for c in ca):
        return "solana"
    return "base"


# -- Token gate --
def check_token_gate(config):
    """Check if wallet holds minimum required tokens. Returns (ok, error_msg)."""
    gate = config.get("token_gate", {})
    if not gate.get("enabled", False):
        return True, None

    token_addr = gate.get("token")
    min_balance = gate.get("min_balance", 0)
    gate_chain = gate.get("chain", "base")
    symbol = gate.get("symbol", "TOKEN")

    if not token_addr or min_balance <= 0:
        return True, None

    wallet = config.get("wallets", {}).get("evm" if gate_chain != "solana" else "solana")
    if not wallet:
        log.warning("Token gate: no wallet configured for chain %s", gate_chain)
        return False, f"No wallet configured for {gate_chain}"

    if gate_chain == "solana":
        return _check_spl_balance(config, wallet, token_addr, min_balance, symbol)
    else:
        return _check_erc20_balance(config, wallet, token_addr, min_balance, symbol, gate_chain)


def _check_erc20_balance(config, wallet, token_addr, min_balance, symbol, chain):
    """Check ERC-20 balance via RPC balanceOf call."""
    rpc_url = config.get("rpc_urls", {}).get(chain)
    if not rpc_url:
        log.warning("Token gate: no RPC URL for chain %s", chain)
        return False, f"No RPC URL for {chain}"

    # balanceOf(address) selector = 0x70a08231
    padded_wallet = wallet.lower().replace("0x", "").zfill(64)
    calldata = "0x70a08231" + padded_wallet

    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_call",
        "params": [{"to": token_addr, "data": calldata}, "latest"]
    }).encode()

    try:
        req = Request(rpc_url, data=payload, headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "tradr/1.0",
        })
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        result = data.get("result", "0x0")
        balance_raw = int(result, 16)
        # Assume 18 decimals (standard ERC-20)
        decimals = gate_cfg_decimals = config.get("token_gate", {}).get("decimals", 18)
        balance = balance_raw / (10 ** decimals)

        if balance >= min_balance:
            log.info("Token gate passed: %.0f %s (min: %.0f)", balance, symbol, min_balance)
            return True, None
        else:
            msg = f"Token gate: wallet holds {balance:,.0f} {symbol}, need {min_balance:,.0f}"
            log.warning(msg)
            return False, msg
    except Exception as e:
        log.warning("Token gate RPC check failed: %s", e)
        return False, f"Token gate check failed: {e}"


def _check_spl_balance(config, wallet, token_mint, min_balance, symbol):
    """Check SPL token balance via Solana RPC."""
    rpc_url = config.get("rpc_urls", {}).get("solana", "https://api.mainnet-beta.solana.com")

    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet,
            {"mint": token_mint},
            {"encoding": "jsonParsed"}
        ]
    }).encode()

    try:
        req = Request(rpc_url, data=payload, headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "tradr/1.0",
        })
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        accounts = data.get("result", {}).get("value", [])
        total = 0.0
        for acct in accounts:
            info = acct.get("account", {}).get("data", {}).get("parsed", {}).get("info", {})
            token_amount = info.get("tokenAmount", {})
            total += float(token_amount.get("uiAmount", 0) or 0)

        if total >= min_balance:
            log.info("Token gate passed: %.0f %s (min: %.0f)", total, symbol, min_balance)
            return True, None
        else:
            msg = f"Token gate: wallet holds {total:,.0f} {symbol}, need {min_balance:,.0f}"
            log.warning(msg)
            return False, msg
    except Exception as e:
        log.warning("Token gate SPL check failed: %s", e)
        return False, f"Token gate check failed: {e}"


# -- Score-based lookups (threshold matching) --
def resolve_from_score_map(score_map, score):
    best_key = None
    best_val = None
    for key_str, val in score_map.items():
        threshold = int(key_str)
        if score >= threshold:
            if best_key is None or threshold > best_key:
                best_key = threshold
                best_val = val
    return best_val


# -- Positions I/O --
def load_positions(positions_file):
    if not os.path.exists(positions_file):
        return {}
    try:
        with open(positions_file) as f:
            return json.load(f)
    except Exception:
        return {}


def save_positions(positions, positions_file):
    os.makedirs(os.path.dirname(positions_file), exist_ok=True)
    tmp = positions_file + ".tmp"
    with open(tmp, "w") as f:
        json.dump(positions, f, indent=2)
    os.replace(tmp, positions_file)


# -- Trade log --
def log_trade(trade_log_file, entry):
    os.makedirs(os.path.dirname(trade_log_file), exist_ok=True)
    with open(trade_log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


# -- Notifications --
def notify(config, text, level="info", notify_type="info"):
    """Send notification. notify_type is one of: buy, sell, confluence, error, info."""
    notify_cfg = config.get("notifications", {})
    if not notify_cfg.get("enabled", True):
        return
    log.info("[NOTIFY:%s:%s] %s", level, notify_type, text)
    script = notify_cfg.get("script")
    if script:
        script = os.path.expanduser(script)
        if os.path.exists(script):
            try:
                subprocess.run([script, level, notify_type, text], capture_output=True, timeout=15)
            except Exception as e:
                log.warning("Notification script failed: %s", e)


# -- Bankr execution --
def bankr_buy(bankr_script, prompt):
    log.info("Executing bankr: %s", prompt)
    try:
        env = os.environ.copy()
        env["BANKR_ALLOW_TRADE"] = "1"  # Bypass trade guard for mechanical pipeline
        result = subprocess.run(
            [bankr_script, prompt],
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
    except FileNotFoundError:
        return False, f"bankr.sh not found at {bankr_script}"
    except Exception as e:
        return False, str(e)


# -- Main entry logic --
def execute_entry(ca, score, chain, mode, token_name, config, size_override=None):
    positions_file = os.path.expanduser(config.get("positions_file",
        "~/.openclaw/workspace/signals/positions.json"))
    trade_log_file = os.path.expanduser(config.get("trade_log",
        "~/.openclaw/workspace/trade-log.jsonl"))
    bankr_script = os.path.expanduser(config.get("bankr_script",
        "~/.openclaw/skills/bankr/scripts/bankr.sh"))
    max_size = config.get("max_position_size_usd", 200)
    mcap_ceiling = config.get("mcap_ceiling_usd", 0)
    cooldown_min = config.get("cooldown_minutes", 0)
    modes = config.get("modes", {})
    default_mode = config.get("default_mode", "swing")

    # -- Guard: token gate --
    gate_ok, gate_err = check_token_gate(config)
    if not gate_ok:
        return {"success": False, "error": gate_err}

    # -- Guard: protected tokens (never trade these, e.g. token gate holdings) --
    protected = [t.lower() for t in config.get("pipeline", {}).get("protected_tokens", [])]
    if ca.lower() in protected:
        return {"success": False, "error": f"Token {ca} is protected — cannot trade"}

    # -- Resolve chain --
    if not chain:
        chain = detect_chain(ca)
    chain = chain.lower()

    # -- Resolve mode from score --
    if not mode:
        score_to_mode = config.get("score_to_mode", {})
        mode = resolve_from_score_map(score_to_mode, score)
        if not mode:
            mode = default_mode
    mode = mode.lower()

    # Validate mode exists
    if mode not in modes:
        return {"success": False, "error": f"Unknown mode '{mode}'. Available: {list(modes.keys())}"}

    # -- Resolve position size from score --
    score_to_size = config.get("score_to_size", {})
    size_usd = resolve_from_score_map(score_to_size, score)
    if size_usd is None:
        size_usd = 2.50

    # Allow caller to override size (e.g., reduced size for 2-trader entries)
    if size_override is not None and size_override > 0:
        log.info("Size override: $%.2f (was $%.2f from score)", size_override, size_usd)
        size_usd = size_override



    # -- Guard: max position size --
    if size_usd > max_size:
        log.warning("Size $%.2f exceeds max $%.2f, capping", size_usd, max_size)
        size_usd = max_size

    # -- Acquire entry lock (prevents duplicate buys for same CA) --
    lock_dir = os.path.expanduser(config.get("lock_dir", "~/.openclaw/workspace/signals/locks"))
    os.makedirs(lock_dir, exist_ok=True)
    lock_path = os.path.join(lock_dir, f"entry-{ca}.lock")
    lock_fd = None
    try:
        lock_fd = open(lock_path, "w")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(f"{os.getpid()} {datetime.now(timezone.utc).isoformat()}\n")
        lock_fd.flush()
        log.info("Acquired entry lock for %s", ca[:12])
    except (BlockingIOError, OSError):
        if lock_fd:
            lock_fd.close()
        return {"success": False, "error": f"Entry already in progress for {ca} (locked by another process)"}

    try:
        return _execute_entry_locked(
            ca, score, chain, mode, token_name, config,
            positions_file, trade_log_file, bankr_script,
            max_size, mcap_ceiling, cooldown_min, modes, default_mode,
            size_usd,
        )
    finally:
        if lock_fd:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                lock_fd.close()
                os.unlink(lock_path)
            except OSError:
                pass


def _execute_entry_locked(
    ca, score, chain, mode, token_name, config,
    positions_file, trade_log_file, bankr_script,
    max_size, mcap_ceiling, cooldown_min, modes, default_mode,
    size_usd,
):
    # -- Guard: already in position --
    positions = load_positions(positions_file)
    if ca in positions and not positions[ca].get("closed", True):
        return {"success": False, "error": f"Already in position for {ca}"}

    # -- Guard: cooldown (recently closed same token) --
    if cooldown_min > 0 and ca in positions and positions[ca].get("closed", False):
        close_ts = positions[ca].get("close_ts", "")
        if close_ts:
            try:
                close_dt = datetime.fromisoformat(close_ts.replace("Z", "+00:00"))
                elapsed = (datetime.now(timezone.utc) - close_dt).total_seconds() / 60
                if elapsed < cooldown_min:
                    remaining = int(cooldown_min - elapsed)
                    return {"success": False,
                            "error": f"Cooldown active for {ca} — closed {int(elapsed)}m ago, {remaining}m remaining"}
            except Exception:
                pass

    # -- Fetch current price/mcap --
    log.info("Fetching price for %s...", ca)
    price, mcap = get_price(ca)
    if not price or not mcap:
        return {"success": False, "error": f"Could not fetch price/mcap for {ca} from DexScreener"}

    # -- Guard: mcap ceiling --
    if mcap_ceiling > 0 and mcap > mcap_ceiling:
        return {"success": False,
                "error": f"Mcap ${mcap:,.0f} exceeds ceiling ${mcap_ceiling:,.0f}"}

    # -- Execute buy via Bankr --
    buy_prompt = f"buy {size_usd} dollars of {ca}"
    if chain:
        buy_prompt += f" on {chain}"

    log.info("Entering %s | mode=%s | size=$%.2f | score=%d | chain=%s | mcap=$%s",
             token_name or ca[:12], mode, size_usd, score, chain, f"{mcap:,.0f}")

    success, response = bankr_buy(bankr_script, buy_prompt)

    if not success:
        log.error("Buy FAILED for %s: %s", ca, response)
        log_trade(trade_log_file, {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "token": token_name or ca[:12],
            "ca": ca,
            "chain": chain,
            "action": "BUY",
            "amount": str(size_usd),
            "mode": mode,
            "score": score,
            "reason": "ENTRY",
            "status": "failed",
            "tx": "",
            "response": (response or "")[:200],
        })
        notify(config, f"BUY FAILED for {token_name or ca[:12]}: {response}", "error", "buy")
        return {"success": False, "error": f"Bankr buy failed: {response}"}

    # -- Extract tx hash if present --
    tx_hash = ""
    m = re.search(r'[0-9a-fA-F]{64}', response or "")
    if m:
        tx_hash = m.group(0)
        if chain not in ("solana", "sol") and not tx_hash.startswith("0x"):
            tx_hash = "0x" + tx_hash

    # -- Write position to positions.json --
    now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    position = {
        "token": token_name or ca[:12],
        "chain": chain,
        "buy_ts": now_ts,
        "entry_mcap": mcap,
        "entry_price": price,
        "buy_amount_usd": size_usd,
        "remaining_usd": size_usd,
        "mode": mode,
        "score": score,
        "current_mcap": mcap,
        "current_price": price,
        "peak_mcap": mcap,
        "first_exit_done": False,
        "closed": False,
        "close_ts": None,
        "close_reason": None,
        "close_mcap": None,
        "close_multiple": None,
        "est_pnl_usd": None,
        "tx_hash": tx_hash,
    }

    positions[ca] = position
    save_positions(positions, positions_file)
    log.info("Position written for %s", token_name or ca[:12])

    # -- Log trade --
    log_trade(trade_log_file, {
        "ts": now_ts,
        "token": token_name or ca[:12],
        "ca": ca,
        "chain": chain,
        "action": "BUY",
        "amount": str(size_usd),
        "mode": mode,
        "score": score,
        "reason": "ENTRY",
        "status": "completed",
        "tx": tx_hash,
        "response": (response or "")[:200],
    })

    # -- Notify --
    mode_params = modes[mode]
    stop_val = f"{mode_params['stop_at']}x" if mode_params.get("stop_at") else "none"
    tp_val = f"{mode_params['take_profit_1']}x" if mode_params.get("take_profit_1") else "none"
    trail_val = f"{mode_params['trailing_stop']*100:.0f}%" if mode_params.get("trailing_stop") else "none"

    notify(config,
        f"BUY {token_name or ca[:12]} | ${size_usd:.2f} | mode={mode} | "
        f"score={score} | mcap=${mcap:,.0f} | chain={chain} | "
        f"stop={stop_val} tp={tp_val} trail={trail_val}",
        "trade", "buy")

    # -- Return result --
    result = {
        "success": True,
        "trade": {
            "ca": ca,
            "token": token_name or ca[:12],
            "chain": chain,
            "mode": mode,
            "score": score,
            "size_usd": size_usd,
            "entry_price": price,
            "entry_mcap": mcap,
            "tx_hash": tx_hash,
            "timestamp": now_ts,
        },
        "mode_params": {
            "stop_at": mode_params.get("stop_at"),
            "take_profit_1": mode_params.get("take_profit_1"),
            "trailing_stop": mode_params.get("trailing_stop"),
        },
    }
    return result


def main():
    parser = argparse.ArgumentParser(
        description="tradr entry -- execute a trade by CA + score",
        usage="tradr-enter.py <ca> [--score N] [--chain CHAIN] [--mode MODE] [--token NAME]",
    )
    parser.add_argument("ca", help="Contract address to buy")
    parser.add_argument("--score", type=int, default=0, help="Signal score (0-10, default: 0)")
    parser.add_argument("--chain", type=str, default=None,
                        help="Chain (solana/base/ethereum/polygon/unichain). Auto-detected if omitted.")
    parser.add_argument("--mode", type=str, default=None,
                        help="Exit mode (snipe/swing/gamble/diamond/custom). Auto-selected from score if omitted.")
    parser.add_argument("--token", type=str, default=None,
                        help="Token name/ticker label (optional)")
    parser.add_argument("--size", type=float, default=None,
                        help="Override trade size in USD (bypasses score_to_size)")

    args = parser.parse_args()

    if not args.ca or not args.ca.strip():
        print(json.dumps({"success": False, "error": "Contract address is required"}))
        sys.exit(1)

    ca = args.ca.strip()
    size_override = args.size
    config = load_config()

    log_file = os.path.expanduser(config.get("log_file", "~/.openclaw/workspace/signals/tradr.log"))
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(log_file, mode="a")
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [ENTER] %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ"))
    log.addHandler(file_handler)

    result = execute_entry(
        ca=ca,
        score=args.score,
        chain=args.chain,
        mode=args.mode,
        token_name=args.token,
        config=config,
        size_override=size_override,
    )

    print(json.dumps(result, indent=2))

    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
