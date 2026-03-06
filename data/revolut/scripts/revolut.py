#!/usr/bin/env python3
from __future__ import annotations

"""Revolut web automation (Playwright).

Commands:
- login: QR-code login and save storage state
- logout: delete saved storage state
- accounts: fetch wallet accounts via Revolut Web API
- transactions: fetch latest transactions via Revolut Web API
"""

import sys

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

import argparse
import json
import os
import re
import shutil
import time
import random
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Any


# Allow `--help` without requiring Playwright.
if "-h" in sys.argv or "--help" in sys.argv:
    sync_playwright = None  # type: ignore
    PlaywrightTimeout = Exception  # type: ignore
else:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except Exception:
        sync_playwright = None  # type: ignore
        PlaywrightTimeout = Exception  # type: ignore


def _find_workspace_root() -> Path:
    """Walk up from script location to find workspace root (parent of 'skills/')."""
    env = os.environ.get("OPENCLAW_WORKSPACE")
    if env:
        return Path(env).expanduser().resolve()
    
    # Use $PWD (preserves symlinks) instead of Path.cwd() (resolves them).
    pwd_env = os.environ.get("PWD")
    cwd = Path(pwd_env) if pwd_env else Path.cwd()
    d = cwd
    for _ in range(6):
        if (d / "skills").is_dir() and d != d.parent:
            return d
        parent = d.parent
        if parent == d:
            break
        d = parent

    d = Path(__file__).resolve().parent
    for _ in range(6):
        if (d / "skills").is_dir() and d != d.parent:
            return d
        d = d.parent
    return Path.cwd()


WORKSPACE_DIR = _find_workspace_root()

# Ephemeral outputs (OCR markdown + default JSON output dir) go to /tmp by default.
# Override with OPENCLAW_TMP if you want a different temp root.
_TMP_ROOT = Path(os.environ.get("OPENCLAW_TMP") or "/tmp").expanduser().resolve()
TMP_DIR = _TMP_ROOT / "openclaw" / "revolut"

CONFIG_DIR = WORKSPACE_DIR / "revolut"
CONFIG_FILE = CONFIG_DIR / "config.json"


# ---- config ----

def _load_config() -> dict:
    """Load config.json from workspace/revolut/config.json."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _resolve_user(explicit_user: str | None) -> tuple[str | None, dict]:
    """Resolve the active user and return (user_name, user_config).

    Rules:
    - If only one user in config: auto-select (no --user needed).
    - If multiple users: --user is required.
    - If no config/users: return (None, {}) for backward compat.
    """
    cfg = _load_config()
    users = cfg.get("users", {})

    if explicit_user:
        if explicit_user not in users:
            raise SystemExit(f"ERROR: user '{explicit_user}' not found in config. Available: {', '.join(users.keys())}")
        return explicit_user, users[explicit_user]

    if len(users) == 1:
        name = next(iter(users))
        return name, users[name]

    if len(users) > 1:
        raise SystemExit(f"ERROR: multiple users in config — use --user to select one: {', '.join(users.keys())}")

    return None, {}


# ---- path safety ----

def _safe_output_path(raw: str) -> Path:
    """Resolve *raw* and verify it lives under WORKSPACE_DIR or /tmp."""
    p = Path(raw).expanduser().resolve()
    ws = str(WORKSPACE_DIR)
    tmp = str(Path("/tmp").resolve())
    if not (str(p).startswith(ws + "/") or str(p) == ws
            or str(p).startswith(tmp + "/") or str(p) == tmp):
        raise SystemExit(f"ERROR: output path must be under workspace ({ws}) or /tmp, got: {p}")
    return p


def _profile_dir_from_args(args) -> Path:
    # Stable persistent profile alongside the state file.
    state = _state_file_from_args(args)
    base = state.parent
    name = f".pw-{state.stem}-profile"
    return (base / name).expanduser().resolve()


def _load_storage_state(path: Path) -> dict | None:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _apply_storage_state_to_context(context, payload: dict) -> None:
    """Best-effort import of Playwright storage_state into a persistent context.

    Persistent contexts can't be created *from* storage_state directly.
    But we can:
    - add cookies
    - add an init script that restores localStorage per-origin

    This is good enough to avoid repeated step-up auth in many cases.
    """
    if not isinstance(payload, dict):
        return

    cookies = payload.get("cookies")
    if isinstance(cookies, list) and cookies:
        try:
            context.add_cookies(cookies)
        except Exception:
            pass

    origins = payload.get("origins")
    if not isinstance(origins, list) or not origins:
        return

    mapping = {}
    for o in origins:
        if not isinstance(o, dict):
            continue
        origin = o.get("origin")
        ls = o.get("localStorage")
        if not isinstance(origin, str) or not isinstance(ls, list):
            continue
        kv = {}
        for item in ls:
            if isinstance(item, dict) and isinstance(item.get("name"), str):
                kv[item["name"]] = str(item.get("value") or "")
        if kv:
            mapping[origin] = kv

    if not mapping:
        return

    # Restore localStorage for matching origin on each document.
    script = """
(() => {
  try {
    const m = %s;
    const origin = window.location.origin;
    const kv = m[origin];
    if (kv) {
      for (const [k, v] of Object.entries(kv)) {
        try { window.localStorage.setItem(k, v); } catch (e) {}
      }
    }
  } catch (e) {}
})();
""" % json.dumps(mapping)

    try:
        context.add_init_script(script)
    except Exception:
        pass


def _profile_is_empty(profile_dir: Path) -> bool:
    try:
        if not profile_dir.exists():
            return True
        # Chromium profile dirs have lots of files; if empty, consider it uninitialized.
        return not any(profile_dir.iterdir())
    except Exception:
        return True


def _launch_persistent_context(p, args, headless: bool):
    state_file = _state_file_from_args(args)
    profile_dir = _profile_dir_from_args(args)
    _ensure_dir(profile_dir)

    context = p.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir),
        headless=headless,
        viewport={"width": 1280, "height": 800},
        user_agent=DEFAULT_UA,
    )

    # If profile is empty but we have a legacy state file, import it once.
    if _profile_is_empty(profile_dir) and state_file.exists():
        payload = _load_storage_state(state_file)
        if payload:
            _apply_storage_state_to_context(context, payload)

    return context

REVOLUT_BASE_URL = "https://app.revolut.com"
REVOLUT_HOME_URL = f"{REVOLUT_BASE_URL}/home"
REVOLUT_START_URL = f"{REVOLUT_BASE_URL}/start"
INVEST_HOME_URL = "https://invest.revolut.com/portfolio/overview/all"

# A reasonably "real" UA helps a bit with bot checks.
DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
)


# ------------------------- shared utils -------------------------

def _now_iso_local() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, payload: Any) -> None:
    _ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _parse_iso_date(s: str) -> str:
    return datetime.strptime(s, "%Y-%m-%d").date().isoformat()

def _date_to_ms_bounds_utc(d: str) -> tuple[int, int]:
    dt0 = datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    start_ms = int(dt0.timestamp() * 1000)
    end_ms = int((dt0.replace(hour=23, minute=59, second=59, microsecond=999000)).timestamp() * 1000)
    return start_ms, end_ms

def _raw_tx_timestamp_ms(tx: dict) -> int | None:
    for key in ("completedAt", "startedDate"):
        if key not in tx:
            continue
        v = tx.get(key)
        if isinstance(v, (int, float)):
            ms = int(v)
        elif isinstance(v, str):
            try:
                ms = int(float(v.strip()))
            except Exception:
                continue
        else:
            continue
        if ms < 1_000_000_000_000:
            ms *= 1000
        return ms
    return None

def _raw_tx_dedupe_key(tx: dict) -> tuple:
    for key in ("id", "transactionId", "transferId", "reference", "externalId"):
        v = tx.get(key)
        if v is not None and str(v).strip():
            return ("id", key, str(v))
    amt_obj = tx.get("amount") or tx.get("money") or tx.get("balanceChange")
    amt_val = _extract_amount(amt_obj)
    ccy = _extract_currency(amt_obj) or ((tx.get("currency") or "").strip().upper() if isinstance(tx.get("currency"), str) else "")
    desc = (tx.get("description") or tx.get("title") or (tx.get("merchant") or {}).get("name") or "")
    return ("fuzzy", _raw_tx_timestamp_ms(tx), amt_val, ccy, desc)

def _extract_tx_items(payload: Any) -> list[dict]:
    if isinstance(payload, list):
        return [t for t in payload if isinstance(t, dict)]
    if isinstance(payload, dict):
        for key in ("transactions", "data", "items"):
            v = payload.get(key)
            if isinstance(v, list):
                return [t for t in v if isinstance(t, dict)]
        return [payload]
    return []


def _slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "other"


def _require_playwright() -> None:
    if sync_playwright is None:
        print("ERROR: playwright not installed. Run: pipx install playwright && playwright install chromium", file=sys.stderr)
        raise SystemExit(1)


# ------------------------- Revolut web (Playwright) -------------------------

def _safe_filename_component(s: str) -> str:
    """Sanitize a string for safe use in filenames (no path traversal)."""
    s = re.sub(r'[^\w\-.]', '_', s.strip())
    s = s.strip('._')
    if not s or s in ('.', '..'):
        raise SystemExit(f"ERROR: invalid user name: {s!r}")
    return s


def _state_file_from_args(args) -> Path:
    user_name = getattr(args, "_user_name", None) or getattr(args, "user", None)
    if user_name:
        safe = _safe_filename_component(user_name)
        return CONFIG_DIR / f"state_{safe}.json"
    return CONFIG_DIR / "state.json"


def _looks_like_pin_screen(text: str) -> bool:
    t = (text or "").lower()
    return "enter passcode" in t or "forgot your passcode" in t or "enter pin" in t


def _fetch_via_interception(page, url_pattern: str, timeout_ms: int = 30000) -> dict | None:
    """Capture JSON response matching url_pattern by reloading/navigating."""
    captured = []
    
    def handle_response(response):
        if url_pattern in response.url and response.status == 200:
            try:
                captured.append(response.json())
            except: pass
            
    page.on("response", handle_response)
    
    # Trigger data load
    try:
        # Reloading usually triggers the main fetch
        page.reload(wait_until="networkidle", timeout=timeout_ms)
    except:
        pass
        
    if captured:
        return captured[0] # Return first match
    return None


def _extract_amount(value) -> float | None:
    if value is None: return None
    
    # If direct number, check heuristic?
    # Usually Revolut web API returns objects. If it returns a flat number, it might be units or cents.
    # But let's handle the dict case first which is the common one.
    
    if isinstance(value, dict):
        # Case 1: value + precision (e.g. {value: 1234, precision: 2} -> 12.34)
        if isinstance(value.get("value"), (int, float)) and isinstance(value.get("precision"), int):
            return float(value["value"]) / (10 ** int(value["precision"]))
            
        # Case 2: amount (usually cents) + currency
        # "amount" might be int (1234) or str ("1234").
        raw_amt = value.get("amount")
        if raw_amt is not None:
            try:
                amt = float(raw_amt)
            except:
                return None
                
            # Check for currency indicator to confirm it's a money object
            has_currency = False
            for k in ("currency", "ccy", "currencyCode"):
                if isinstance(value.get(k), str):
                    has_currency = True
                    break
            
            # Heuristic: If it has currency and looks like an integer, treat as cents.
            # Revolut Web API almost always sends cents as integers (or strings of integers).
            if has_currency:
                # If it's an integer (1000.0 or 1000), divide by 100.
                if amt.is_integer():
                    return amt / 100.0
                # If it's a float with decimals (10.50), it's likely already units.
                return amt
                
            return amt

    # Fallback for direct numbers or strings
    if isinstance(value, int):
        # Revolut API typically sends amounts in minor units (cents) as integers.
        # e.g. 100 -> 1.00, 378899 -> 3788.99
        return float(value) / 100.0
        
    if isinstance(value, float):
        # If it's a float, it's ambiguous.
        # But usually raw JSON has ints for cents.
        # If json.load parsed it as float, it had a decimal point?
        # If it had decimal point, assume units.
        return value
        
    if isinstance(value, str):
        try: return float(value.replace(" ", "").replace(",", "."))
        except: return None

    return None


def _extract_currency(value) -> str | None:
    if isinstance(value, dict):
        for k in ("currency", "ccy"):
            v = value.get(k)
            if isinstance(v, str) and v.strip(): return v.strip().upper()
    return None


def _to_date_iso(value) -> str | None:
    if value is None: return None
    if isinstance(value, (int, float)):
        ts = float(value)
        if ts > 1e12: ts = ts / 1000.0
        try: return datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
        except: return None
    return None


def canonicalize_revolut_accounts(payload) -> list[dict]:
    wallets: list[dict] = []
    if isinstance(payload, list):
        wallets = [w for w in payload if isinstance(w, dict)]
    elif isinstance(payload, dict):
        for key in ("wallets", "data", "items", "PERSONAL"): # Added PERSONAL/POCKETS handling
            v = payload.get(key)
            if isinstance(v, list):
                wallets = [w for w in v if isinstance(w, dict)]
                break
        else:
            wallets = [payload]

    out: list[dict] = []
    
    # Handle nested pockets (PERSONAL -> pockets)
    expanded_wallets = []
    for w in wallets:
        if "pockets" in w and isinstance(w["pockets"], list):
            expanded_wallets.extend(w["pockets"])
        else:
            expanded_wallets.append(w)
            
    for w in expanded_wallets:
        wid = w.get("id") or w.get("walletId") or w.get("uuid")
        wid_s = str(wid) if wid is not None else ""

        ccy = (w.get("currency") or w.get("ccy") or "").strip().upper() or _extract_currency(w.get("balance")) or ""
        name = (
            w.get("name")
            or w.get("displayName")
            or w.get("title")
            or (f"Revolut Wallet ({ccy})" if ccy else "Revolut Wallet")
        )

        iban = None
        for k in ("iban", "ibanFormatted"):
            if isinstance(w.get(k), str) and w.get(k).strip():
                iban = w.get(k).strip()
                break

        # Note: balance can be numeric 0 which is falsy, so we must not use `or` chaining here.
        bal_src = None
        if "balance" in w:
            bal_src = w.get("balance")
        elif "balances" in w:
            bal_src = w.get("balances")
        elif "amount" in w:
            bal_src = w.get("amount")
        bal_amt = _extract_amount(bal_src)

        acct: dict = {
            "id": wid_s or (ccy or name),
            "type": "checking",
            "name": str(name),
            "currency": ccy or "EUR",
        }

        if iban:
            acct["iban"] = iban

        balances: dict = {}
        if bal_amt is not None:
            balances["booked"] = {"amount": bal_amt, "currency": acct["currency"]}
            balances["available"] = {"amount": bal_amt, "currency": acct["currency"]}
        if balances:
            acct["balances"] = balances

        out.append(acct)

    out.sort(key=lambda a: ((a.get("currency") or ""), (a.get("name") or "")))
    return out


def _canonical_category_from_revolut_type(type_str: str) -> str:
    t = (type_str or "").strip().lower()
    if "card" in t: return "card_payment"
    if "transfer" in t: return "transfer"
    if "exchange" in t or "fx" in t: return "exchange"
    return _slug(type_str)


    # Filter by account ID if provided
    if account_id:
        filtered = []
        for t in out:
            # We need to access the raw transaction structure to check account.id?
            # canonicalize_revolut_transactions takes raw payload and returns simplified dicts.
            # But wait, simplified dict doesn't keep account.id!
            # We need to filter *during* canonicalization or *before*.
            pass 
            
        # Let's adjust canonicalize_revolut_transactions to accept filter_account_id
        # OR: canonicalize_revolut_transactions could return the account ID in the simplified dict?
        # Current simplified dict:
        # { status, bookingDate, amount: {amount, currency}, category, description }
        # It doesn't have account ID.
        
        # We should filter raw_txs BEFORE canonicalization.
        pass

def canonicalize_revolut_transactions(payload, filter_account_id: str | None = None) -> list[dict]:
    txs: list[dict] = []
    if isinstance(payload, list):
        txs = [t for t in payload if isinstance(t, dict)]
    elif isinstance(payload, dict):
        for key in ("transactions", "data", "items"):
            v = payload.get(key)
            if isinstance(v, list):
                txs = [t for t in v if isinstance(t, dict)]
                break
        else:
            txs = [payload]

    out: list[dict] = []
    for t in txs:
        # Filter by account.id if requested
        if filter_account_id:
            # Check t["account"]["id"]
            acc = t.get("account") or {}
            if acc.get("id") != filter_account_id:
                # Also check pocketId just in case
                if acc.get("pocketId") != filter_account_id:
                    continue

        state = (t.get("state") or t.get("status") or "").upper()
        if state in ("COMPLETED", "BOOKED", "DONE"):
            status = "booked"
        elif state in ("DECLINED", "FAILED", "REJECTED", "CANCELLED"):
            status = "rejected"
        else:
            status = "pending"

        d = (_to_date_iso(t.get("completedAt")) or _to_date_iso(t.get("startedDate")))
        if not d: continue

        amt_obj = t.get("amount") or t.get("money") or t.get("balanceChange")
        amt = _extract_amount(amt_obj)
        ccy = ((t.get("currency") or "").strip().upper() or "EUR")
        if amt is None: continue

        desc = (t.get("description") or t.get("title") or (t.get("merchant") or {}).get("name") or "")
        reason = t.get("reason")
        
        tx: dict = {
            "status": status,
            "bookingDate": d,
            "valueDate": d,
            "amount": {"amount": float(amt), "currency": ccy},
            "category": {"code": _canonical_category_from_revolut_type(t.get("type") or "")},
            "description": desc or None
        }
        if reason:
            tx["rejectionReason"] = _slug(str(reason)).replace("_", " ").capitalize() # "insufficient_balance" -> "Insufficient balance"
        out.append(tx)
    return out


def canonicalize_revolut_portfolio(payload, tickers_by_ref: dict[str, dict] | None = None) -> dict:
    """Return banker-style portfolio positions.

    If tickers_by_ref is provided, we enrich positions with:
      - marketValue
      - performance.absolute
      - performance.percent
    """
    positions: list[dict] = []

    # If payload is list, find GIA/STOCK portfolio
    if isinstance(payload, list):
        for p in payload:
            if isinstance(p, dict) and (p.get("accountType") == "GIA" or "holdings" in p):
                payload = p
                break
        else:
            if payload:
                payload = payload[0]

    holdings = payload.get("holdings", []) if isinstance(payload, dict) else []
    if not isinstance(holdings, list):
        holdings = []

    for h in holdings:
        if not isinstance(h, dict):
            continue
        htype = h.get("assetType")
        if htype == "CASH":
            continue

        symbol = h.get("symbol")
        name = h.get("name")
        ref = h.get("ref") or h.get("id")

        isin = (h.get("assetInfo") or {}).get("isin")

        qty_obj = h.get("balance") or {}
        try:
            qf = float(qty_obj.get("quantity") or 0)
            qty = int(qf) if qf.is_integer() else qf
        except Exception:
            qty = 0

        avg_obj = h.get("averagePrice")
        avg_amt = _extract_amount(avg_obj)
        cur = _extract_currency(avg_obj)

        # Current price from tickers endpoint
        last_price = None
        if tickers_by_ref and isinstance(ref, str) and ref in tickers_by_ref:
            t = tickers_by_ref.get(ref) or {}
            # prefer lastPrecise if present
            lp = t.get("lastPrecise")
            if isinstance(lp, str):
                try:
                    last_price = float(lp)
                except Exception:
                    last_price = None
            if last_price is None:
                last_price = _extract_amount({"amount": t.get("last"), "currency": t.get("currency")})

        price_amt = last_price if last_price is not None else avg_amt

        pos: dict = {
            "name": name,
            "isin": isin or symbol,
            "quantity": qty,
            # For banker UI, "price" is interpreted as current price.
            "price": {"amount": price_amt, "currency": (cur or (tickers_by_ref.get(ref, {}).get('currency') if tickers_by_ref and ref else None))},
            # keep avg price for reference
            "averagePrice": {"amount": avg_amt, "currency": cur},
            "ref": ref,
        }

        # Enrichment if we have ticker + avg
        if last_price is not None and avg_amt is not None and cur:
            mv = qty * float(last_price)
            pl = (float(last_price) - float(avg_amt)) * qty
            pct = None
            try:
                if avg_amt and float(avg_amt) != 0:
                    pct = ((float(last_price) / float(avg_amt)) - 1.0) * 100.0
            except Exception:
                pct = None

            pos["marketValue"] = {"amount": mv, "currency": cur}
            pos["performance"] = {
                "absolute": {"amount": pl, "currency": cur},
                "percent": pct,
            }

        positions.append(pos)

    return {"positions": positions}

def canonicalize_revolut_invest_tx(payload, name_map: dict | None = None) -> list[dict]:
    """Canonicalize Revolut Invest trade history into banker 'depot transactions' shape.

    Args:
        payload: Raw transaction data from Revolut API
        name_map: Optional dict mapping ref/symbol to stock name (e.g. {"TSLA": "Tesla"})
    """
    # Payload shapes vary. We accept:
    # - {"items": [...]} (older)
    # - {"orders": [...]} or similar
    # - a raw list
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = payload.get("items") or payload.get("orders") or payload.get("data") or []
    else:
        items = []

    out: list[dict] = []
    name_map = name_map or {}

    for t in items:
        if not isinstance(t, dict):
            continue
        if t.get("state") != "COMPLETED":
            continue

        # We focus on TRADE (buy/sell securities)
        if t.get("type") != "TRADE":
            continue

        symbol = t.get("symbol")
        ref = t.get("ref") or t.get("instrumentRef") or t.get("baseInstrumentRef")
        # Try to get name from transaction, then from name_map by ref or symbol
        name = t.get("name") or (t.get("instrument") or {}).get("name") if isinstance(t.get("instrument"), dict) else None
        if not name and name_map:
            name = name_map.get(ref) or name_map.get(symbol)
        side = t.get("side")  # BUY/SELL

        d = _to_date_iso(t.get("completedAt"))

        qty = None
        try:
            qf = float(t.get("executedQuantity") or 0)
            qty = int(qf) if qf.is_integer() else qf
        except Exception:
            qty = None

        price_obj = t.get("executedPrice")
        price_amt = _extract_amount(price_obj)
        price_cur = _extract_currency(price_obj)

        total_obj = t.get("total") or t.get("net")
        total_amt = _extract_amount(total_obj)
        total_cur = _extract_currency(total_obj)

        # Banker UI expects:
        # bookingDate, kind, security{isin,name}, quantity, unit, price{amount,currency}, venue, status
        tx: dict = {
            "bookingDate": d,
            "status": "booked",
            "kind": side.lower() if isinstance(side, str) and side else "trade",
            "security": {
                # We don't always have true ISIN; use ref if available, else ticker.
                "isin": ref or symbol,
                "name": name or symbol,
            },
            "quantity": qty,
            # unit is implicit for equities; omit to keep canonical JSON clean
            "price": {"amount": price_amt, "currency": price_cur},
            "venue": "REVOLUT",
            "amount": {"amount": total_amt, "currency": total_cur},
            "description": f"{side} {symbol}" if side and symbol else None,
        }

        # Also keep a convenient fallback field (some older code paths look at tx['isin']).
        tx["isin"] = (ref or symbol)

        out.append(tx)

    return out


def _resolve_account_selector(accounts: list[dict], selector: str) -> dict:
    q = (selector or "").strip().lower()
    if not q: return accounts[0] if accounts else {}
    for a in accounts:
        if (a.get("id") or "").lower() == q: return a
        if a.get("currency","").lower() == q: return a
    return accounts[0] if accounts else {}


def _handle_pin_screen(page, pin: str | None = None):
    """Enter pin if screen detected.

    Pin is read from user config in config.json (or passed explicitly).
    """
    if not pin:
        return False
    try:
        if _looks_like_pin_screen(page.inner_text("body")):
            print("[revolut] Pin screen detected. Entering PIN...", file=sys.stderr)
            inputs = page.locator('input[aria-label^="Code input"], input[aria-label^="Codeinput"], input[inputmode="numeric"], input[type="password"]')
            if inputs.count() > 0:
                first = inputs.first
                first.click()
                time.sleep(0.5)
                
                for digit in pin:
                    page.keyboard.type(digit)
                    time.sleep(random.uniform(0.1, 0.3))
                
                print("[revolut] PIN entered. Waiting...", file=sys.stderr)
                time.sleep(3)
                return True
    except Exception as e:
        print(f"[revolut] Error handling pin: {e}", file=sys.stderr)
    return False

_LAST_AUTH_EXPIRED = False


class RevolutAuthExpired(Exception):
    pass


def _capture_qr_screenshot(page) -> Path | None:
    """Try to screenshot just the QR code element, falling back to a cropped page screenshot."""
    qr_path = TMP_DIR / "revolut_qr.png"
    _ensure_dir(qr_path.parent)

    # Strategy 1: Find the QR canvas/svg/img element and screenshot it directly
    for selector in [
        'canvas',                          # QR often rendered as <canvas>
        'svg[viewBox]',                    # or as <svg>
        '[data-testid*="qr"]',            # data-testid with "qr"
        'img[src*="qr"]',                 # <img> with qr in src
        '[class*="qr" i]',                # class containing "qr"
        '[class*="QR"]',                  # class containing "QR"
    ]:
        try:
            loc = page.locator(selector)
            if loc.count() > 0:
                el = loc.first
                bbox = el.bounding_box()
                if bbox and bbox["width"] > 50 and bbox["height"] > 50:
                    el.screenshot(path=str(qr_path))
                    print(f"[revolut] QR screenshot saved: {qr_path}", file=sys.stderr)
                    return qr_path
        except Exception:
            continue

    # Strategy 2: Full page screenshot (still useful for manual scanning)
    try:
        page.screenshot(path=str(qr_path))
        print(f"[revolut] Full page screenshot saved (QR element not isolated): {qr_path}", file=sys.stderr)
        return qr_path
    except Exception as e:
        print(f"[revolut] Failed to capture QR screenshot: {e}", file=sys.stderr)
        return None


def _try_extract_qr_url(page) -> str | None:
    # Try DOM attributes first
    try:
        loc = page.locator('[aria-label*="revolut.com/app/challenges/qr/"], [href*="revolut.com/app/challenges/qr/"]')
        if loc.count() > 0:
            el = loc.first
            url = el.get_attribute("aria-label") or el.get_attribute("href")
            if url and "revolut.com/app/challenges/qr/" in url:
                return url
    except:  # noqa: E722
        pass

    # Fallback: search HTML
    try:
        html = page.content() or ""
        # some pages escape slashes
        html = html.replace("\\/", "/")
        m = re.search(r"https://revolut\\.com/app/challenges/qr/[^\"\s<]+", html)
        if m:
            return m.group(0)
    except:  # noqa: E722
        pass

    return None


def _handle_auth_challenge(page, success_url_pattern="**/home**", auth_timeout_ms: int = 600_000, pin: str | None = None):
    global _LAST_AUTH_EXPIRED
    _LAST_AUTH_EXPIRED = False
    """Handle PIN and/or QR code challenge if they appear.

    Revolut can require:
    - Pin entry
    - QR-based login approval
    - (sometimes) just waiting for an SSO redirect
    """

    # Dismiss cookie banner first (might block UI)
    try:
        try:
            page.get_by_role("button", name="Allow all cookies").click(timeout=1000)
        except Exception:
            try:
                page.locator('button.styled__CookieConsentButton-bylcZS:has-text("Allow all cookies")').first.click(timeout=1000)
            except Exception:
                try:
                    page.locator('button:has-text("Allow all cookies"), button:has-text("Accept all cookies"), button:has-text("Accept all")').first.click(timeout=1000)
                except Exception:
                    pass
    except:  # noqa: E722
        pass

    # 1) Pin
    if _handle_pin_screen(page, pin=pin):
        time.sleep(1)

    # If we're already where we need to be, we're done.
    try:
        page.wait_for_url(success_url_pattern, timeout=2000)
        return True
    except:  # noqa: E722
        pass

    # Sometimes we are already on the right screen but Playwright URL-pattern matching can miss fast redirects.
    try:
        cur = page.url or ""
        if ("/trade/" in cur and "trade" in (success_url_pattern or "")) or ("/activity/transactions" in cur):
            return True
    except Exception:
        pass

    # 2) QR / approval
    try:
        login_url = _try_extract_qr_url(page)
        if login_url:
            print("[revolut] Auth challenge detected (QR).", file=sys.stderr)

            # Capture QR code as image for scanning from another device
            qr_path = _capture_qr_screenshot(page)

            print(f"IMPORTANT: Approve in Revolut app via this link: {login_url}")
            if qr_path:
                print(f"QR_IMAGE:{qr_path}")
            print(f"[revolut] Approve in Revolut app via: {login_url}", file=sys.stderr)
            try:
                sys.stdout.flush()
            except Exception:
                pass
        else:
            # If we're already inside the Invest app (trade/activity/etc.), don't flag this as an auth challenge.
            # Only treat it as suspicious when we're on SSO/pin flows.
            try:
                cur = page.url or ""
                if "invest.revolut.com" in cur and "sso.revolut.com" not in cur:
                    return True
            except Exception:
                pass

            # Still useful to capture what we're seeing
            try:
                shot = TMP_DIR / "revolut_auth_debug.png"
                page.screenshot(path=str(shot))
                print(f"[revolut] Auth challenge suspected but QR URL not detected. Screenshot: {shot}", file=sys.stderr)
                print(f"[revolut] Current URL: {page.url}", file=sys.stderr)
            except:  # noqa: E722
                pass

        # Wait for successful redirect (user approves in Revolut app).
        # We poll so we can detect "QR code expired".
        deadline = time.time() + (auth_timeout_ms / 1000.0)
        while time.time() < deadline:
            # Dismiss cookie banner (can appear after redirect)
            try:
                page.get_by_role("button", name="Allow all cookies").click(timeout=200)
            except Exception:
                pass

            try:
                body = (page.inner_text("body") or "").lower()
                if "qr code expired" in body:
                    raise RevolutAuthExpired("QR code expired")
            except RevolutAuthExpired:
                raise
            except:  # noqa: E722
                pass

            try:
                page.wait_for_url(success_url_pattern, timeout=1000)
                print("[revolut] Login confirmed.", file=sys.stderr)
                return True
            except PlaywrightTimeout:
                pass


            # Fast path: check current URL (handles quick redirects that we might miss).
            try:
                cur = page.url or ""
                if ("/trade/" in cur and "trade" in (success_url_pattern or "")) or ("/activity/transactions" in cur):
                    print("[revolut] Login confirmed.", file=sys.stderr)
                    return True
            except Exception:
                pass
            except:  # noqa: E722
                # likely target closed
                break

            time.sleep(0.5)

        print("[revolut] Timed out waiting for auth.", file=sys.stderr)
        return False

    except RevolutAuthExpired:
        _LAST_AUTH_EXPIRED = True
        print("[revolut] QR code expired.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[revolut] Error while handling auth: {e}", file=sys.stderr)
        return False


def cmd_login(args) -> int:
    _require_playwright()
    state_file = _state_file_from_args(args)
    _ensure_dir(state_file.parent)

    with sync_playwright() as p:  # type: ignore[misc]
        # Persistent profile keeps Revolut session stable across commands.
        context = _launch_persistent_context(p, args, headless=False)
        page = context.new_page()

        try:
            page.goto(REVOLUT_HOME_URL, wait_until="domcontentloaded", timeout=30000)
        except Exception:
            pass

        ok = _handle_auth_challenge(page, success_url_pattern="**/home**", pin=getattr(args, "_pin", None))
        if not ok:
            if _LAST_AUTH_EXPIRED:
                print("QR code expired, please try again", file=sys.stderr)
            else:
                print("[revolut] Auth not completed.", file=sys.stderr)
            try:
                context.close()
            except Exception:
                pass
            return 3

        time.sleep(2)
        try:
            context.storage_state(path=str(state_file))
            print(f"[revolut] Login successful. State saved to: {state_file}", file=sys.stderr)
        except Exception as e:
            print(f"[revolut] WARNING: could not save storage state: {e}", file=sys.stderr)

        try:
            context.close()
        except Exception:
            pass

    return 0


def cmd_logout(args) -> int:
    state_file = _state_file_from_args(args)
    profile_dir = _profile_dir_from_args(args)

    try:
        if state_file.exists():
            state_file.unlink()
            print(f"[revolut] Deleted state: {state_file}", file=sys.stderr)
    except Exception as e:
        print(f"[revolut] Failed to delete state: {e}", file=sys.stderr)

    try:
        if profile_dir.exists():
            shutil.rmtree(profile_dir)
            print(f"[revolut] Deleted profile dir: {profile_dir}", file=sys.stderr)
    except Exception as e:
        print(f"[revolut] Failed to delete profile dir: {e}", file=sys.stderr)

    return 0


def cmd_accounts(args) -> int:
    _require_playwright()
    state_file = _state_file_from_args(args)
    profile_dir = _profile_dir_from_args(args)
    if (not state_file.exists()) and (not profile_dir.exists()):
        print(f"[revolut] ERROR: No session found. Run: revolut.py login", file=sys.stderr)
        return 2

    debug = bool(getattr(args, "debug", False))
    headless = not bool(getattr(args, "visible", False))

    with sync_playwright() as p:  # type: ignore[misc]
        context = _launch_persistent_context(p, args, headless=headless)
        page = context.new_page()

        # Check for pin/QR if redirected to login
        try:
            page.goto(REVOLUT_HOME_URL, wait_until="domcontentloaded", timeout=15000)
            ok = _handle_auth_challenge(page, success_url_pattern="**/home**", pin=getattr(args, "_pin", None))
            if not ok:
                if _LAST_AUTH_EXPIRED:
                    print("QR code expired, please try again", file=sys.stderr)
                else:
                    print("[revolut] Auth not completed.", file=sys.stderr)
                context.close()
                return 3
            time.sleep(2)
        except Exception:
            pass

        # Prefer JS fetch (more reliable than interception)
        headers = _get_api_headers(page)
        raw = _fetch_via_api_call(page, "/api/retail/wallets", headers)

        # Fallback to interception if needed
        if raw is None:
            raw = _fetch_via_interception(page, "/api/retail/wallets")

        if not raw:
            print("[revolut] Failed to fetch accounts data. Session invalid or CF blocked.", file=sys.stderr)
            if debug:
                try:
                    page.screenshot(path=str(state_file.parent / "revolut_debug_fetch.png"))
                except Exception:
                    pass
            context.close()
            return 3

        if debug:
            _write_json(state_file.parent / "revolut_raw_accounts.json", raw)

        accounts = canonicalize_revolut_accounts(raw)

        # Always include Invest depot summary as a synthetic "depot" account.
        # (Oliver preference: no flag; accounts should always show depot.)
        portfolio_id = getattr(args, "portfolio_id", None)
        depot_account_id = getattr(args, "depot_account", "revolut_gia")

        # We need to enter Invest context to access its APIs.
        try:
            page.goto(INVEST_HOME_URL, wait_until="domcontentloaded", timeout=15000)
            ok = _handle_auth_challenge(page, success_url_pattern="**/trade/**", pin=getattr(args, "_pin", None))
            if not ok:
                if _LAST_AUTH_EXPIRED:
                    print("QR code expired, please try again", file=sys.stderr)
                else:
                    print("[revolut] Auth not completed.", file=sys.stderr)
                context.close()
                return 3
            time.sleep(1)

            invest_headers = _get_api_headers(page)

            # Determine portfolio id if not provided.
            pid = portfolio_id
            if not pid:
                raw_list = _fetch_via_api_call(page, "/api/retail/trading-access/portfolios", invest_headers)
                if isinstance(raw_list, list):
                    for p0 in raw_list:
                        if isinstance(p0, dict) and p0.get("state") == "ACTIVE" and p0.get("accountType") == "GIA":
                            pid = p0.get("id")
                            break

            depot_currency = "USD"
            depot_value = None
            depot_pl = None
            depot_pct = None

            if pid and isinstance(pid, str):
                raw_pf = _fetch_via_api_call(page, f"/api/retail/trading-access/portfolios/{pid}", invest_headers)
                tickers_by_ref = {}
                holdings = raw_pf.get("holdings", []) if isinstance(raw_pf, dict) else []
                refs = []
                if isinstance(holdings, list):
                    for h in holdings:
                        if isinstance(h, dict) and h.get("assetType") != "CASH":
                            r = h.get("ref") or h.get("id")
                            if isinstance(r, str) and r:
                                refs.append(r)
                refs = sorted(set(refs))
                if refs:
                    tickers = _fetch_via_api_call(page, "/api/retail/instruments/tickers", invest_headers, method="POST", body=refs)
                    if isinstance(tickers, list):
                        for t in tickers:
                            if isinstance(t, dict) and isinstance(t.get("ref"), str):
                                tickers_by_ref[t["ref"]] = t

                canon_pf = canonicalize_revolut_portfolio(raw_pf, tickers_by_ref=tickers_by_ref)
                positions = canon_pf.get("positions", [])

                # Compute totals
                total_mv = 0.0
                total_pl = 0.0
                total_cost = 0.0
                for pos in positions:
                    if not isinstance(pos, dict):
                        continue
                    mv = pos.get("marketValue") if isinstance(pos.get("marketValue"), dict) else None
                    perf = pos.get("performance") if isinstance(pos.get("performance"), dict) else None
                    avg = pos.get("averagePrice") if isinstance(pos.get("averagePrice"), dict) else None
                    qty = pos.get("quantity")
                    try:
                        q = float(qty) if qty is not None else 0.0
                    except Exception:
                        q = 0.0
                    if isinstance(mv, dict) and mv.get("amount") is not None:
                        try:
                            total_mv += float(mv.get("amount"))
                        except Exception:
                            pass
                        depot_currency = mv.get("currency") or depot_currency
                    if isinstance(perf, dict):
                        abs_ = perf.get("absolute") if isinstance(perf.get("absolute"), dict) else None
                        if isinstance(abs_, dict) and abs_.get("amount") is not None:
                            try:
                                total_pl += float(abs_.get("amount"))
                            except Exception:
                                pass
                    if isinstance(avg, dict) and avg.get("amount") is not None:
                        try:
                            total_cost += float(avg.get("amount")) * q
                        except Exception:
                            pass

                depot_value = total_mv
                depot_pl = total_pl
                if total_cost:
                    depot_pct = (total_pl / total_cost) * 100.0

            depot_acct = {
                "id": depot_account_id,
                "type": "depot",
                "name": "Revolut Invest (GIA)",
                "currency": depot_currency,
            }
            if depot_value is not None or depot_pl is not None:
                depot_acct["securities"] = {
                    "value": {"amount": depot_value, "currency": depot_currency},
                    "profitLoss": {"amount": depot_pl, "currency": depot_currency, "percent": depot_pct},
                }

            # Replace existing synthetic depot entry if present
            accounts = [a for a in accounts if a.get("id") != depot_account_id]
            accounts.append(depot_acct)

        except Exception as e:
            print(f"[revolut] Failed to include depot: {e}", file=sys.stderr)

        wrapper: dict[str, Any] = {
            "institution": "revolut",
            "fetchedAt": _now_iso_local(),
            "accounts": accounts,
        }

        out_path = getattr(args, "out", None)
        if out_path:
            _safe_output_path(out_path).write_text(
                json.dumps(wrapper, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"[revolut] Wrote JSON: {out_path}", file=sys.stderr)
        else:
            print(json.dumps(wrapper, ensure_ascii=False, indent=2))
        context.close()
        return 0


def _get_api_headers(page, trigger_reload: bool = False) -> dict:
    """Capture headers from background requests to reuse authentication tokens.

    Revolut's JS client sends important headers (x-device-id, x-browser-application, x-client-version, ...)
    that are not automatically added by the browser. We sniff them from real in-app requests.

    If trigger_reload=True, we reload once to force the app to emit background /api/retail requests.
    """
    captured = []

    def on_request(request):
        if "/api/retail" in request.url and not captured:
            h = request.headers
            if "x-device-id" in h:
                captured.append(h)

    page.on("request", on_request)

    # Cookie banner can block the app from making API calls.
    try:
        try:
            page.get_by_role("button", name="Allow all cookies").click(timeout=1000)
        except Exception:
            try:
                page.locator('button.styled__CookieConsentButton-bylcZS:has-text("Allow all cookies")').first.click(timeout=1000)
            except Exception:
                try:
                    page.locator('button:has-text("Allow all cookies"), button:has-text("Accept all cookies"), button:has-text("Accept all")').first.click(timeout=1000)
                except Exception:
                    pass
    except Exception:
        pass

    if trigger_reload:
        try:
            page.reload(wait_until="domcontentloaded", timeout=15000)
        except Exception:
            pass

    # Wait up to 5s for a request (usually Home loads them immediately)
    for _ in range(50):
        if captured:
            break
        try:
            page.wait_for_timeout(100)
        except:  # noqa: E722
            break

    if captured:
        orig = captured[0]
        out = {}
        keys = ["x-device-id", "x-browser-application", "x-client-version", "x-timezone", "device-id"]
        for k in keys:
            if k in orig:
                out[k] = orig[k]
        return out
    return {}

def _fetch_via_api_call(page, url: str, extra_headers: dict = {}, method: str = "GET", body: Any = None) -> Any:
    """Execute fetch() inside the page context to get data directly."""
    headers_json = json.dumps(extra_headers)
    method_json = json.dumps(method)
    body_json = json.dumps(body)

    try:
        print(f"[revolut] Fetching via JS: {method} {url}", file=sys.stderr)
        result = page.evaluate(
            f"""
            async () => {{
                try {{
                    const extra = {headers_json};
                    const method = {method_json};
                    const body = {body_json};

                    const headers = {{
                        'Accept': 'application/json, text/plain, */*',
                        ...extra
                    }};

                    const opts = {{ method, headers, credentials: 'include' }};
                    if (body !== null && body !== undefined) {{
                        headers['Content-Type'] = 'application/json';
                        opts.body = JSON.stringify(body);
                    }}

                    const res = await fetch("{url}", opts);
                    if (!res.ok) return {{ error: String(res.status) + " " + (res.statusText || "") }};
                    return await res.json();
                }} catch (e) {{
                    return {{ error: e.toString() }};
                }}
            }}
            """
        )

        if isinstance(result, dict) and "error" in result:
            print(f"[revolut] JS fetch error: {result['error']}", file=sys.stderr)
            return None
        return result
    except Exception as e:
        print(f"[revolut] API fetch failed: {e}", file=sys.stderr)
        return None

def cmd_transactions(args) -> int:
    _require_playwright()
    state_file = _state_file_from_args(args)
    profile_dir = _profile_dir_from_args(args)
    if (not state_file.exists()) and (not profile_dir.exists()):
        print(f"[revolut] ERROR: No session found. Run: revolut.py login", file=sys.stderr)
        return 2

    debug = bool(getattr(args, "debug", False))
    headless = not bool(getattr(args, "visible", False))
    # Revolut wallet endpoint can become flaky with very large counts. Keep it fixed.
    count = 50
    account_id = getattr(args, "account", None)
    date_from = getattr(args, "date_from", None)
    date_until = getattr(args, "date_until", None)

    if (date_from and not date_until) or (date_until and not date_from):
        print("[revolut] ERROR: --from and --until must be provided together.", file=sys.stderr)
        return 2

    paging_enabled = bool(date_from and date_until)
    from_ms = None
    until_ms = None
    from_date = None
    until_date = None
    if paging_enabled:
        try:
            _parse_iso_date(date_from)
            _parse_iso_date(date_until)
        except ValueError:
            print("[revolut] ERROR: Dates must be in YYYY-MM-DD format.", file=sys.stderr)
            return 2
        from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
        until_date = datetime.strptime(date_until, "%Y-%m-%d").date()
        if from_date > until_date:
            print("[revolut] ERROR: --from must be on or before --until.", file=sys.stderr)
            return 2
        from_ms, _ = _date_to_ms_bounds_utc(date_from)
        _, until_ms = _date_to_ms_bounds_utc(date_until)

    with sync_playwright() as p:  # type: ignore[misc]
        context = _launch_persistent_context(p, args, headless=headless)
        page = context.new_page()

        try:
            page.goto(REVOLUT_HOME_URL, wait_until="domcontentloaded", timeout=30000)
            _handle_auth_challenge(page, success_url_pattern="**/home**", pin=getattr(args, "_pin", None))
            time.sleep(1)
        except Exception:
            pass

        # Construct API URL
        # Default: last transactions (mixed)
        # If account provided: use internalPocketId
        base_url = f"/api/retail/user/current/transactions/last?count={count}"
        internal_pocket_qs = ""
        if account_id:
            # We assume the user passed the UUID. If they passed a name/currency, we can't easily resolve it without fetching accounts first.
            # But usually we pass UUIDs.
            # However, if it's a UUID, we append internalPocketId.
            # If it's not a UUID (like "USD"), we might fail. 
            # Ideally we should resolve it, but let's assume UUID for now or try to fetch regardless.
            if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', account_id, re.I):
                internal_pocket_qs = f"&internalPocketId={account_id}"
                base_url += internal_pocket_qs
            else:
                print(f"[revolut] Warning: Account ID '{account_id}' does not look like a UUID. API might ignore it or fail.", file=sys.stderr)

        # Capture headers from environment. Trigger a reload to ensure we sniff x-device-id etc.
        api_headers = _get_api_headers(page, trigger_reload=True)

        all_raw_items: list[dict] = []
        seen_keys: set[tuple] = set()

        if paging_enabled:
            cur_to_ms = int(until_ms)
            page_idx = 0
            while True:
                page_idx += 1
                url = f"/api/retail/user/current/transactions/last?to={cur_to_ms}&count={count}{internal_pocket_qs}"
                raw_txs = _fetch_via_api_call(page, url, api_headers)

                # Fallback to interception if JS fetch returns null (e.g. CORS or strict CSP, though usually fine on same origin)
                if raw_txs is None:
                    print("[revolut] JS fetch returned null. Trying interception fallback...", file=sys.stderr)
                    raw_txs = _fetch_via_interception(page, "/api/retail/user/current/transactions/last")

                if raw_txs is None or (isinstance(raw_txs, dict) and raw_txs.get("error")):
                    print("[revolut] Failed to fetch transactions.", file=sys.stderr)
                    context.close()
                    return 3

                if debug:
                    _write_json(state_file.parent / f"revolut_raw_transactions_p{page_idx}.json", raw_txs)

                items = _extract_tx_items(raw_txs)
                print(f"[revolut] Paging transactions: page={page_idx} to={cur_to_ms} items={len(items)}", file=sys.stderr)

                if not items:
                    break

                oldest_ms = None
                for item in items:
                    key = _raw_tx_dedupe_key(item)
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)
                    all_raw_items.append(item)

                    ts_ms = _raw_tx_timestamp_ms(item)
                    if ts_ms is not None and (oldest_ms is None or ts_ms < oldest_ms):
                        oldest_ms = ts_ms

                if oldest_ms is None:
                    break

                if oldest_ms <= from_ms:
                    break

                next_to = int(oldest_ms) - 1
                if next_to >= cur_to_ms:
                    break
                cur_to_ms = next_to
        else:
            # Use JS fetch instead of interception for reliability and param support
            raw_txs = _fetch_via_api_call(page, base_url, api_headers)

            # Fallback to interception if JS fetch returns null (e.g. CORS or strict CSP, though usually fine on same origin)
            if raw_txs is None:
                print("[revolut] JS fetch returned null. Trying interception fallback...", file=sys.stderr)
                raw_txs = _fetch_via_interception(page, "/api/retail/user/current/transactions/last")

            if raw_txs is None or (isinstance(raw_txs, dict) and raw_txs.get("error")):
                print("[revolut] Failed to fetch transactions.", file=sys.stderr)
                context.close()
                return 3

            if debug:
                _write_json(state_file.parent / "revolut_raw_transactions.json", raw_txs)

            all_raw_items = _extract_tx_items(raw_txs)

        txs = canonicalize_revolut_transactions(all_raw_items, filter_account_id=account_id)
        if paging_enabled and from_date and until_date:
            filtered = []
            for tx in txs:
                bd = tx.get("bookingDate")
                if not isinstance(bd, str):
                    continue
                try:
                    d = datetime.strptime(bd, "%Y-%m-%d").date()
                except Exception:
                    continue
                if from_date <= d <= until_date:
                    filtered.append(tx)
            txs = filtered
        
        wrapper: dict[str, Any] = {
            "institution": "revolut",
            "fetchedAt": _now_iso_local(),
            "transactions": txs,
        }

        if paging_enabled:
            wrapper["range"] = {"from": date_from, "until": date_until}
        
        if account_id:
            wrapper["account"] = {"id": account_id}

        out_path = getattr(args, "out", None)
        if out_path:
            _safe_output_path(out_path).write_text(
                json.dumps(wrapper, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"[revolut] Wrote JSON: {out_path}", file=sys.stderr)
        else:
            print(json.dumps(wrapper, ensure_ascii=False, indent=2))
        context.close()
        return 0


def cmd_portfolio(args) -> int:
    _require_playwright()
    state_file = _state_file_from_args(args)
    profile_dir = _profile_dir_from_args(args)
    if (not state_file.exists()) and (not profile_dir.exists()):
        print(f"[revolut] ERROR: No session found. Run: revolut.py login", file=sys.stderr)
        return 2

    debug = bool(getattr(args, "debug", False))
    headless = not bool(getattr(args, "visible", False))
    portfolio_id = getattr(args, "id", None)
    account_id = getattr(args, "account", None)

    with sync_playwright() as p:
        context = _launch_persistent_context(p, args, headless=headless)
        page = context.new_page()

        try:
            page.goto(INVEST_HOME_URL, wait_until="domcontentloaded", timeout=15000)
            ok = _handle_auth_challenge(page, success_url_pattern="**/portfolio**", pin=getattr(args, "_pin", None))
            if not ok:
                if _LAST_AUTH_EXPIRED:
                    print("QR code expired, please try again", file=sys.stderr)
                else:
                    print("[revolut] Auth not completed.", file=sys.stderr)
                context.close()
                return 3
            time.sleep(2)
            # Cookie banner sometimes blocks UI / network requests on invest.revolut.com
            try:
                try:
                    page.get_by_role("button", name="Allow all cookies").click(timeout=1500)
                except Exception:
                    try:
                        page.locator('button.styled__CookieConsentButton-bylcZS:has-text("Allow all cookies")').first.click(timeout=1500)
                    except Exception:
                        page.locator('button:has-text("Allow all cookies"), button:has-text("Accept all cookies"), button:has-text("Accept all")').first.click(timeout=1500)
            except Exception:
                pass
        except:  # noqa: E722
            pass

        headers = _get_api_headers(page)

        # If caller provided a portfolio id, fetch that directly.
        raw = None
        if portfolio_id:
            raw = _fetch_via_api_call(page, f"/api/retail/trading-access/portfolios/{portfolio_id}", headers)

        # Otherwise try list + pick first ACTIVE/GIA id.
        if not raw:
            raw_list = _fetch_via_api_call(page, "/api/retail/trading-access/portfolios", headers)
            if isinstance(raw_list, list) and raw_list:
                picked = None
                for p0 in raw_list:
                    if isinstance(p0, dict) and p0.get("state") == "ACTIVE" and p0.get("accountType") == "GIA":
                        picked = p0
                        break
                if picked is None:
                    picked = raw_list[0]
                pid = picked.get("id") if isinstance(picked, dict) else None
                if pid:
                    raw = _fetch_via_api_call(page, f"/api/retail/trading-access/portfolios/{pid}", headers)
                else:
                    raw = picked
            else:
                # Fallback: interception
                raw = _fetch_via_interception(page, "/api/retail/trading-access/portfolios")

        if not raw:
            print("[revolut] Failed to fetch portfolio.", file=sys.stderr)
            context.close()
            return 3

        if debug:
            _write_json(state_file.parent / "revolut_raw_portfolio.json", raw)

        # Enrich holdings with current prices to compute value + performance
        tickers_by_ref = {}
        try:
            holdings = raw.get("holdings", []) if isinstance(raw, dict) else []
            refs = []
            if isinstance(holdings, list):
                for h in holdings:
                    if isinstance(h, dict) and (h.get("assetType") != "CASH"):
                        r = h.get("ref") or h.get("id")
                        if isinstance(r, str) and r:
                            refs.append(r)
            # De-dupe refs
            refs = sorted(set(refs))
            if refs:
                tickers = _fetch_via_api_call(page, "/api/retail/instruments/tickers", headers, method="POST", body=refs)
                if isinstance(tickers, list):
                    for t in tickers:
                        if isinstance(t, dict) and isinstance(t.get("ref"), str):
                            tickers_by_ref[t["ref"]] = t
        except Exception:
            pass

        canon = canonicalize_revolut_portfolio(raw, tickers_by_ref=tickers_by_ref)
        wrapper = {
            "institution": "revolut",
            "fetchedAt": _now_iso_local(),
            "kind": "portfolio",
            "account": {"id": account_id} if account_id else None,
            **canon,
        }
        # Remove null account if not provided
        if wrapper.get("account") is None:
            wrapper.pop("account")

        out_path = getattr(args, "out", None)
        if out_path:
            _safe_output_path(out_path).write_text(
                json.dumps(wrapper, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"[revolut] Wrote JSON: {out_path}", file=sys.stderr)
        else:
            print(json.dumps(wrapper, ensure_ascii=False, indent=2))
        context.close()
        return 0

def cmd_invest_scan(args) -> int:
    """Load Invest dashboard and print all /api/retail request URLs observed.

    Useful to discover endpoints for portfolio valuation/performance.
    """
    _require_playwright()
    state_file = _state_file_from_args(args)
    profile_dir = _profile_dir_from_args(args)
    if (not state_file.exists()) and (not profile_dir.exists()):
        print(f"[revolut] ERROR: No session found. Run: revolut.py login", file=sys.stderr)
        return 2

    headless = not bool(getattr(args, "visible", False))

    with sync_playwright() as p:  # type: ignore[misc]
        context = _launch_persistent_context(p, args, headless=headless)
        page = context.new_page()

        urls: set[str] = set()

        def on_request(req):
            try:
                u = req.url
                if "/api/retail" in u:
                    urls.add(u)
            except Exception:
                pass

        page.on("request", on_request)

        try:
            page.goto(INVEST_HOME_URL, wait_until="domcontentloaded", timeout=15000)
            ok = _handle_auth_challenge(page, success_url_pattern="**/portfolio**", pin=getattr(args, "_pin", None))
            if not ok:
                if _LAST_AUTH_EXPIRED:
                    print("QR code expired, please try again", file=sys.stderr)
                else:
                    print("[revolut] Auth not completed.", file=sys.stderr)
                context.close()
                return 3

            # Cookie banner sometimes blocks UI / network requests
            try:
                try:
                    page.get_by_role("button", name="Allow all cookies").click(timeout=1500)
                except Exception:
                    try:
                        page.locator('button.styled__CookieConsentButton-bylcZS:has-text("Allow all cookies")').first.click(timeout=1500)
                    except Exception:
                        page.locator('button:has-text("Allow all cookies"), button:has-text("Accept all cookies"), button:has-text("Accept all")').first.click(timeout=1500)
            except Exception:
                pass

            # Trigger more network activity
            try:
                page.reload(wait_until="networkidle", timeout=30000)
            except Exception:
                pass
            time.sleep(2)

        except Exception as e:
            print(f"[revolut] invest-scan failed: {e}", file=sys.stderr)
            context.close()
            return 3

        payload = {"observed": len(urls), "urls": sorted(urls)}

        out_path = getattr(args, "out", None)
        if out_path:
            _safe_output_path(out_path).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"[revolut] Wrote JSON: {out_path}", file=sys.stderr)
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        context.close()
        return 0


def cmd_invest_transactions(args) -> int:
    _require_playwright()
    state_file = _state_file_from_args(args)
    profile_dir = _profile_dir_from_args(args)
    if (not state_file.exists()) and (not profile_dir.exists()):
        print(f"[revolut] ERROR: No session found. Run: revolut.py login", file=sys.stderr)
        return 2

    debug = bool(getattr(args, "debug", False))
    headless = not bool(getattr(args, "visible", False))

    # Match George/ELBA UX: explicit date bounds (YYYY-MM-DD).
    date_from = getattr(args, "date_from", None)
    date_until = getattr(args, "date_until", None)
    if not date_from or not date_until:
        print("[revolut] ERROR: Missing required arguments: --from, --until", file=sys.stderr)
        return 2

    # Validate ISO dates
    import datetime
    try:
        datetime.datetime.strptime(date_from, "%Y-%m-%d")
        datetime.datetime.strptime(date_until, "%Y-%m-%d")
    except ValueError:
        print("[revolut] ERROR: Dates must be in YYYY-MM-DD format.", file=sys.stderr)
        return 2

    # Revolut seems to enforce a relatively small server-side limit. Keep this fixed.
    limit = 100

    with sync_playwright() as p:
        context = _launch_persistent_context(p, args, headless=headless)
        page = context.new_page()
        
        try:
            page.goto(INVEST_HOME_URL, wait_until="domcontentloaded", timeout=15000)
            # We consider ourselves authenticated once we're in the actual Invest trading UI.
            ok = _handle_auth_challenge(page, success_url_pattern="**/trade/**", pin=getattr(args, "_pin", None))
            if not ok:
                if _LAST_AUTH_EXPIRED:
                    print("QR code expired, please try again", file=sys.stderr)
                else:
                    print("[revolut] Auth not completed.", file=sys.stderr)
                context.close()
                return 3
            time.sleep(2)
        except:  # noqa: E722
            pass
        
        # Capture auth headers from the initial Invest app load (it emits /api/retail calls that
        # include x-device-id, x-browser-application, x-client-version, etc.).
        headers = _get_api_headers(page, trigger_reload=True)

        # Navigate to the transactions activity page so the request origin/referrer matches
        # what the web client uses.
        try:
            page.goto("https://invest.revolut.com/activity/transactions", wait_until="domcontentloaded", timeout=15000)
            time.sleep(1)
            try:
                try:
                    page.get_by_role("button", name="Allow all cookies").click(timeout=1500)
                except Exception:
                    try:
                        page.locator('button.styled__CookieConsentButton-bylcZS:has-text("Allow all cookies")').first.click(timeout=1500)
                    except Exception:
                        page.locator('button:has-text("Allow all cookies"), button:has-text("Accept all cookies"), button:has-text("Accept all")').first.click(timeout=1500)
            except Exception:
                pass
        except Exception:
            pass

        # Optional name enrichment (best-effort; may fail when Revolut changes endpoints)
        name_map: dict[str, str] = {}

        # Correct trade history endpoint observed in the web client:
        # https://invest.revolut.com/api/retail/trading/transactions?limit=100&accountType=GIA&to=<ms>&from=<ms>
        import datetime

        def _date_to_ms_bounds_utc(d: str):
            dt0 = datetime.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
            start_ms = int(dt0.timestamp() * 1000)
            end_ms = int((dt0.replace(hour=23, minute=59, second=59, microsecond=999000)).timestamp() * 1000)
            return start_ms, end_ms

        from_ms, _ = _date_to_ms_bounds_utc(date_from)
        _, to_ms = _date_to_ms_bounds_utc(date_until)

        def _parse_dt_ms(v):
            if v is None:
                return None
            if isinstance(v, (int, float)):
                return int(v)
            if isinstance(v, str):
                s = v.strip()
                if s.endswith("Z"):
                    s = s[:-1] + "+00:00"
                try:
                    dt = datetime.datetime.fromisoformat(s)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=datetime.timezone.utc)
                    return int(dt.timestamp() * 1000)
                except Exception:
                    return None
            return None

        def _extract_items(payload):
            if isinstance(payload, list):
                return payload
            if isinstance(payload, dict):
                return payload.get("items") or payload.get("orders") or payload.get("data") or []
            return []

        def _min_item_ms(items: list):
            fields = ["completedAt", "createdAt", "executedAt", "updatedAt", "timestamp", "time"]
            mmin = None
            for it in items:
                if not isinstance(it, dict):
                    continue
                for f in fields:
                    if f in it:
                        ms = _parse_dt_ms(it.get(f))
                        if ms is None:
                            continue
                        if mmin is None or ms < mmin:
                            mmin = ms
                        break
            return mmin

        cur_to_ms = to_ms
        all_txs: list[dict] = []
        seen: set[tuple] = set()

        page_idx = 0
        while True:
            page_idx += 1
            url = f"/api/retail/trading/transactions?limit={limit}&accountType=GIA&to={cur_to_ms}&from={from_ms}"
            raw = _fetch_via_api_call(page, url, headers)

            # Fallbacks (endpoint variations)
            if isinstance(raw, dict) and raw.get("error"):
                raw = _fetch_via_api_call(page, f"/api/retail/trading/transactions?limit={limit}&accountType=GIA&to={cur_to_ms}", headers)
            if isinstance(raw, dict) and raw.get("error"):
                raw = _fetch_via_api_call(page, f"/api/retail/trading/transactions?limit={limit}&accountType=GIA", headers)

            if raw is None or (isinstance(raw, dict) and raw.get("error")):
                print("[revolut] Failed to fetch invest transactions.", file=sys.stderr)
                context.close()
                return 3

            if debug:
                _write_json(state_file.parent / f"revolut_raw_invest_tx_p{page_idx}.json", raw)

            txs = canonicalize_revolut_invest_tx(raw, name_map=name_map)
            # de-dupe overlapping pages
            for tx in txs:
                key = (
                    tx.get("bookingDate"),
                    tx.get("kind"),
                    (tx.get("security") or {}).get("isin"),
                    tx.get("quantity"),
                    (tx.get("price") or {}).get("amount"),
                    (tx.get("price") or {}).get("currency"),
                    (tx.get("amount") or {}).get("amount"),
                    (tx.get("amount") or {}).get("currency"),
                )
                if key in seen:
                    continue
                seen.add(key)
                all_txs.append(tx)

            items = _extract_items(raw)
            if not isinstance(items, list) or not items:
                break

            min_ms = _min_item_ms(items)
            if min_ms is None:
                break

            # paginate further into the past
            next_to = int(min_ms) - 1
            if next_to <= from_ms:
                break
            if next_to >= cur_to_ms:
                break
            cur_to_ms = next_to

            # stop early if fewer than limit returned
            if len(items) < limit:
                break

        wrapper = {
            "institution": "revolut",
            "fetchedAt": _now_iso_local(),
            "range": {"from": date_from, "until": date_until},
            "transactions": all_txs,
        }


        out_path = getattr(args, "out", None)
        if out_path:
            _safe_output_path(out_path).write_text(
                json.dumps(wrapper, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"[revolut] Wrote JSON: {out_path}", file=sys.stderr)
        else:
            print(json.dumps(wrapper, ensure_ascii=False, indent=2))
        context.close()
        return 0


# ------------------------- CLI -------------------------




def main() -> int:
    parser = argparse.ArgumentParser(
        description="Revolut CLI (web automation)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global flags
    parser.add_argument("--visible", action="store_true", help="Show browser window")
    parser.add_argument("--debug", action="store_true", help="Save raw Revolut payloads")
    parser.add_argument("--out", default=None, help="Write JSON output to file (must be under workspace or /tmp)")
    parser.add_argument("--user", default=None, help="User profile name (uses revolut_state_{user}.json)")

    sub = parser.add_subparsers(dest="command", required=True)

    p_login = sub.add_parser("login", help="Login via QR code and save storage state")
    p_login.set_defaults(func=cmd_login)

    p_logout = sub.add_parser("logout", help="Delete storage state")
    p_logout.set_defaults(func=cmd_logout)

    p_acc = sub.add_parser("accounts", help="Fetch accounts (wallets + Invest depot) from Revolut Web")
    p_acc.add_argument("--json", action="store_true", help="(kept for parity)")
    p_acc.add_argument("--portfolio-id", default=None, help="Optional portfolio id (if you want to force a specific Invest portfolio)")
    p_acc.add_argument("--depot-account", default="revolut_gia", help="Account id to use for the synthetic depot entry (default: revolut_gia)")
    p_acc.set_defaults(func=cmd_accounts)

    p_tx = sub.add_parser("transactions", help="Fetch wallet transactions from Revolut Web")
    p_tx.add_argument("--account", default=None, help="Account selector")
    p_tx.add_argument("--from", dest="date_from", default=None, help="Start date (YYYY-MM-DD)")
    p_tx.add_argument("--until", dest="date_until", default=None, help="End date (YYYY-MM-DD)")
    p_tx.set_defaults(func=cmd_transactions)

    p_pf = sub.add_parser("portfolio", help="Fetch Revolut Invest (stocks) portfolio holdings")
    p_pf.add_argument("--id", default=None, help="Portfolio id (optional; auto-pick if omitted)")
    p_pf.add_argument("--account", default=None, help="Optional account id label for output")
    p_pf.set_defaults(func=cmd_portfolio)

    p_itx = sub.add_parser("invest-transactions", help="Fetch Revolut Invest (stocks) transactions")
    p_itx.add_argument("--from", dest="date_from", required=True, help="Start date (YYYY-MM-DD)")
    p_itx.add_argument("--until", dest="date_until", required=True, help="End date (YYYY-MM-DD)")
    p_itx.set_defaults(func=cmd_invest_transactions)

    p_iscan = sub.add_parser("invest-scan", help="Debug: list observed Revolut Invest /api/retail endpoints")
    p_iscan.set_defaults(func=cmd_invest_scan)

    args = parser.parse_args()

    # Resolve user early — attaches pin to args for all commands
    user_name, user_cfg = _resolve_user(args.user)
    args._user_name = user_name
    args._pin = user_cfg.get("pin")

    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
