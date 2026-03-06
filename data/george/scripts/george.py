#!/usr/bin/env python3
"""
George Banking Automation - Erste Bank/Sparkasse Austria

Modular script for:
- Listing accounts
- Downloading PDF statements (with booking receipts)
- Downloading data exports (CAMT53/MT940)
- Downloading transaction exports (CSV/JSON/OFX/XLSX)

Requires phone approval via George app during login.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

import argparse
import json
import os
import re
import time
import uuid
from datetime import datetime, date, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, quote


def _set_strict_umask() -> None:
    """Best-effort hardening: ensure files/dirs are private by default.

    This mainly protects persisted Playwright session state (cookies/storage) and token.json
    from other local users on the same machine.
    """
    try:
        os.umask(0o077)
    except Exception:
        pass


def _chmod(path: Path, mode: int) -> None:
    try:
        os.chmod(path, mode)
    except Exception:
        return


def _harden_tree(root: Path) -> None:
    """Best-effort recursive permission hardening (dirs 700, files 600)."""
    try:
        if not root.exists():
            return
        for dirpath, dirnames, filenames in os.walk(root):
            _chmod(Path(dirpath), 0o700)
            for fn in filenames:
                p = Path(dirpath) / fn
                try:
                    if p.is_symlink():
                        continue
                except Exception:
                    pass
                _chmod(p, 0o600)
    except Exception:
        return


_set_strict_umask()


def _find_workspace_root() -> Path:
    """Walk up from script location to find workspace root (parent of 'skills/')."""
    env = os.environ.get("OPENCLAW_WORKSPACE")
    if env:
        return Path(env).resolve()
    
    # Prefer CWD if it looks like a workspace (handles symlinks correctly)
    cwd = Path.cwd()
    if (cwd / "skills").is_dir():
        return cwd

    d = Path(__file__).resolve().parent
    for _ in range(6):
        if (d / "skills").is_dir() and d != d.parent:
            return d
        d = d.parent
    return Path.cwd()


# Data-carrier uploads are XML-based financial formats only.
_ALLOWED_UPLOAD_EXTENSIONS = {".xml", ".camt", ".camt053", ".pain", ".pain001", ".mt940"}

def _validate_upload_file(file_path: Path) -> None:
    """Validate a data-carrier file before upload.

    Checks:
    1. Path traversal protection (resolve to real path, reject symlinks outside cwd)
    2. File extension allowlist
    3. Content sniff (must look like XML, not arbitrary binary)
    """
    # Path traversal protection: resolve to absolute, reject if it escapes
    # the current working directory or home directory.
    resolved = file_path.resolve()
    home = Path.home().resolve()
    cwd = Path.cwd().resolve()
    if not (str(resolved).startswith(str(cwd)) or str(resolved).startswith(str(home))):
        raise ValueError(
            f"Path traversal blocked: '{file_path}' resolves to '{resolved}' "
            f"which is outside the home directory."
        )

    if not resolved.is_file():
        raise ValueError(f"File not found: '{file_path}'")

    # Extension check
    suffix = file_path.suffix.lower()
    if suffix not in _ALLOWED_UPLOAD_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{suffix}'. "
            f"Data-carrier uploads accept only XML-based formats: "
            f"{', '.join(sorted(_ALLOWED_UPLOAD_EXTENSIONS))}"
        )

    # Content sniff: first non-whitespace bytes must look like XML (<?xml or <Document etc.)
    try:
        with open(resolved, "rb") as f:
            head = f.read(1024)
        stripped = head.lstrip()
        if not (stripped.startswith(b"<?xml") or stripped.startswith(b"<") and b">" in stripped[:200]):
            raise ValueError(
                f"File '{file_path.name}' does not appear to be XML. "
                f"First bytes: {stripped[:40]!r}"
            )
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Cannot read file '{file_path}': {e}") from e


def _safe_download_filename(suggested: str) -> str:
    """Sanitise a Playwright suggested_filename to prevent path traversal.

    Strips directory components (including '..') and falls back to a
    safe default if the result is empty or suspicious.
    """
    # Take only the final component (basename) — removes any directory part.
    name = Path(suggested).name if suggested else ""
    # Extra guard: reject hidden files and empty names.
    if not name or name.startswith("."):
        name = "download.bin"
    return name


# Fast path: allow `--help` without requiring Playwright.
if "-h" in sys.argv or "--help" in sys.argv:
    sync_playwright = None  # type: ignore[assignment]
    PlaywrightTimeout = Exception  # type: ignore[assignment]
else:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        print("ERROR: playwright not installed. Run: pipx install playwright && playwright install chromium")
        sys.exit(1)

def _default_state_dir() -> Path:
    # Keep George state in the workspace.
    # Always: workspace/george
    return _find_workspace_root() / "george"


def _default_output_dir() -> Path:
    # Ephemeral outputs (exports, PDFs, canonical JSON) go to /tmp by default.
    # Override with OPENCLAW_TMP if you want a different temp root.
    tmp_root = Path(os.environ.get("OPENCLAW_TMP") or "/tmp").expanduser().resolve()
    return tmp_root / "openclaw" / "george"


# Runtime state dir (always workspace/george)
STATE_DIR: Path = _default_state_dir()
DEFAULT_OUTPUT_DIR: Path = _default_output_dir()

DEBUG_DIR: Path = STATE_DIR / "debug"

DEFAULT_LOGIN_TIMEOUT = 180  # seconds (George app approval window is ~3 minutes)

# User id override for this run (set from CLI --user-id)
USER_ID_OVERRIDE: str | None = None

def _get_profile_dir(user_id: str) -> Path:
    """Return profile directory for a specific user."""
    safe_uid = re.sub(r"[^a-z0-9\._-]", "", user_id.lower())
    return STATE_DIR / f".pw-profile-{safe_uid}"

def _get_token_cache_file(user_id: str) -> Path:
    return _get_profile_dir(user_id) / "token.json"

# George URLs
BASE_URL = "https://george.sparkasse.at"
LOGIN_URL = f"{BASE_URL}/index.html#/login"
DASHBOARD_URL = f"{BASE_URL}/index.html#/overview"


def _is_login_flow_url(url: str) -> bool:
    """Return True if URL looks like any login/SSO/OAuth page."""
    u = (url or "").lower()
    return (
        "login.sparkasse.at" in u
        or "/sts/oauth/authorize" in u
        or "#/login" in u
        or u.endswith("/login")
        or "/login" in u
    )


def _is_george_app_url(url: str) -> bool:
    u = (url or "").lower()
    return "george.sparkasse.at" in u


def _extract_token_expires_in_seconds(url: str | None) -> int | None:
    """Return expires_in seconds if the URL fragment includes an OAuth token response."""
    if not url:
        return None
    try:
        parts = urlsplit(url)
        frag = parts.fragment or ""
        if "access_token=" not in frag and "id_token=" not in frag:
            return None
        qs = dict(parse_qsl(frag, keep_blank_values=True))
        ei = qs.get("expires_in")
        return int(ei) if ei and ei.isdigit() else None
    except Exception:
        return None


def _safe_filename_component(value: str | None, default: str = "value") -> str:
    """Sanitize a user-controlled string for safe use in filenames.

    Prevents path traversal by stripping path separators and limiting characters.
    """
    s = str(value or "").strip()
    if not s:
        return default

    # Remove path separators (both POSIX and Windows)
    s = s.replace("/", "_").replace("\\", "_")
    try:
        sep = os.sep
        if sep:
            s = s.replace(sep, "_")
        alt = os.altsep
        if alt:
            s = s.replace(alt, "_")
    except Exception:
        pass

    # Keep only safe characters
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s)
    s = s.strip("._-")
    if not s:
        s = default
    return s[:80]


def _safe_url_for_logs(url: str | None) -> str:
    """Redact sensitive info from URLs before logging.

    George sometimes returns OAuth tokens in the URL fragment, e.g.
    `index.html#access_token=...&expires_in=...&state=/overview...`.
    Never log those tokens.
    """
    if not url:
        return "<empty>"

    try:
        parts = urlsplit(url)
        frag = parts.fragment or ""
        if "access_token=" in frag or "id_token=" in frag or "refresh_token=" in frag:
            qs = dict(parse_qsl(frag, keep_blank_values=True))
            state = qs.get("state")
            expires_in = qs.get("expires_in")
            # Keep only non-sensitive debugging info
            safe_frag_bits = []
            if state:
                safe_frag_bits.append(f"state={state}")
            if expires_in:
                safe_frag_bits.append(f"expires_in={expires_in}")
            safe_frag = "&".join(safe_frag_bits) if safe_frag_bits else "<redacted>"
            return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, safe_frag))

        # Otherwise keep the URL as-is
        return url
    except Exception:
        # Last resort: coarse redaction
        return "<redacted-url>"


def _apply_state_dir() -> None:
    """Recompute derived paths from the fixed workspace state dir."""
    global STATE_DIR, DEFAULT_OUTPUT_DIR

    STATE_DIR = _default_state_dir()
    DEFAULT_OUTPUT_DIR = _default_output_dir()

    global DEBUG_DIR
    DEBUG_DIR = STATE_DIR / "debug"

    # Ensure the state dir exists and is private.
    _ensure_dir(STATE_DIR)

    # No .env loading — use GEORGE_USER_ID env var or --user-id flag



def _now_iso_local() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
    _chmod(p, 0o700)


DEBUG_ENABLED: bool = False


def _write_debug_json(prefix: str, payload) -> Path | None:
    # Write bank-native payload to a timestamped JSON file for debugging.
    if not DEBUG_ENABLED:
        return None
    _ensure_dir(DEBUG_DIR)
    ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    out = DEBUG_DIR / f"{ts}-{prefix}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    _chmod(out, 0o600)
    return out


def _load_token_cache(user_id: str) -> dict | None:
    try:
        p = _get_token_cache_file(user_id)
        if not p.exists():
            return None
        return json.loads(p.read_text())
    except Exception:
        return None


def _save_token_cache(user_id: str, access_token: str, source: str = "auth_header", expires_at: str | None = None) -> None:
    try:
        p = _get_token_cache_file(user_id)
        _ensure_dir(p.parent)
        data = {
            "accessToken": access_token,
            "obtainedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "expiresAt": expires_at,
            "source": source,
        }
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        _chmod(p, 0o600)
        _chmod(p.parent, 0o700)
    except Exception:
        return


def _extract_bearer_token(auth_header: str) -> str | None:
    if not auth_header:
        return None
    m = re.match(r"(?i)bearer\s+(.+)$", auth_header.strip())
    if not m:
        return None
    return m.group(1).strip()


def _eu_amount(amount: float | None) -> str:
    if amount is None:
        return "N/A"
    s = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def _canonical_account_type_george(raw_type: str | None) -> str:
    t = (raw_type or "").lower()
    return {
        "currentaccount": "checking",
        "current": "checking",
        "giro": "checking",
        "saving": "savings",
        "savings": "savings",
        "loan": "debt",
        "credit": "debt",
        "kredit": "debt",
        "creditcard": "creditcard",
    }.get(t, t or "other")


def canonicalize_accounts_george(payload, normalized: list[dict], raw_path: Path | None = None) -> dict:
    # Build canonical accounts wrapper for George.
    raw_accounts: list[dict] = []
    if isinstance(payload, list):
        raw_accounts = [x for x in payload if isinstance(x, dict)]
    elif isinstance(payload, dict):
        for key in ("items", "accounts", "collection", "data", "content", "accountList"):
            v = payload.get(key)
            if isinstance(v, list):
                raw_accounts = [x for x in v if isinstance(x, dict)]
                break

    by_id: dict[str, dict] = {}
    for acc in raw_accounts:
        acc_id = _extract_first(acc, ["id", "accountId", "uid", "uuid"])
        if acc_id is not None:
            by_id[str(acc_id)] = acc

    out_accounts = []
    for a in normalized:
        acc_id = str(a.get("id") or "")

        # Filter out non-account products we don't want in canonical output (e.g. insurance, security placeholder).
        raw_type = str(a.get("type") or "").lower()
        canon_type = _canonical_account_type_george(a.get("type"))
        if raw_type == "insurance" or canon_type == "insurance":
            continue
        # George exposes a "security" pseudo-account (UUID) that is not a depot and has no transactions.
        # We model real depots separately via /my/securities as type="depot".
        if raw_type == "security" or canon_type == "security":
            continue

        raw = by_id.get(acc_id) or {}

        bal_amt, bal_ccy = _extract_money_from_account(
            raw,
            ["balance", "accountBalance", "amount", "currentBalance", "value"],
            ["currency", "ccy"],
        )
        avail_amt, avail_ccy = _extract_money_from_account(
            raw,
            ["disposable", "disposableAmount", "available", "availableAmount", "disposableBalance"],
            ["currency", "ccy"],
        )
        if avail_ccy is None:
            avail_ccy = bal_ccy

        currency = (a.get("currency") or bal_ccy or avail_ccy or "EUR").strip()

        balances: dict = {}
        if bal_amt is not None:
            balances["booked"] = {"amount": bal_amt, "currency": currency}
        if avail_amt is not None:
            balances["available"] = {"amount": avail_amt, "currency": currency}

        acct = {
            "id": acc_id,
            "type": canon_type,
            "name": a.get("name") or a.get("alias") or a.get("description") or "N/A",
            "currency": currency,
        }
        # Omit "balances": null/empty from JSON
        if balances:
            acct["balances"] = balances

        # Omit "iban": null from JSON
        if a.get("iban"):
            acct["iban"] = a.get("iban")

        # Extra metadata (currently used for credit cards)
        if isinstance(a.get("number"), str) and str(a.get("number")).strip():
            acct["number"] = str(a.get("number")).strip()

        if acct.get("type") == "creditcard":
            # Prefer values embedded in the proxy accounts payload: raw['card']
            card = raw.get("card") if isinstance(raw.get("card"), dict) else None
            if card:
                num = card.get("number")
                if not acct.get("number") and isinstance(num, str) and num.strip():
                    acct["number"] = num.strip()

                bal_amt2 = _extract_amount(card.get("balance"))
                bal_ccy2 = _extract_currency(card.get("balance")) or acct.get("currency")
                if bal_amt2 is not None:
                    if "balances" not in acct:
                        acct["balances"] = {}
                    acct["balances"]["booked"] = {"amount": bal_amt2, "currency": bal_ccy2}

                lim_amt = _extract_amount(card.get("limit"))
                lim_ccy = _extract_currency(card.get("limit")) or bal_ccy2 or acct.get("currency")
                if lim_amt is not None:
                    acct["limit"] = {"amount": lim_amt, "currency": lim_ccy}
            else:
                # Fallback: values from /my/cards merge (if present)
                bal = a.get("balance") if isinstance(a.get("balance"), dict) else None
                if isinstance(bal, dict) and bal.get("amount") is not None:
                    if "balances" not in acct:
                        acct["balances"] = {}
                    acct["balances"]["booked"] = {"amount": bal.get("amount"), "currency": bal.get("currency") or acct.get("currency")}
                lim = a.get("limit") if isinstance(a.get("limit"), dict) else None
                if isinstance(lim, dict) and lim.get("amount") is not None:
                    acct["limit"] = {"amount": lim.get("amount"), "currency": lim.get("currency") or acct.get("currency")}

        if acct.get("type") == "depot":
            settlement = a.get("settlementAccount")
            if isinstance(settlement, dict):
                iban = settlement.get("iban")
                if isinstance(iban, str) and iban.strip():
                    acct["settlementAccount"] = {"iban": iban.strip()}
                    cur = settlement.get("currency")
                    if isinstance(cur, str) and cur.strip():
                        acct["settlementAccount"]["currency"] = cur.strip()

            securities = a.get("securities")
            if isinstance(securities, dict) and securities:
                acct["securities"] = securities

        out_accounts.append(acct)

    return {
        "institution": "george",
        "fetchedAt": _now_iso_local(),
        "rawPath": str(raw_path) if raw_path else None,
        "accounts": out_accounts,
    }

def _login_timeout(args) -> int:
    return getattr(args, "login_timeout", DEFAULT_LOGIN_TIMEOUT)

def load_config() -> dict:
    """DEPRECATED: George no longer uses a local config.json/accounts cache.

    Kept only for backward-compatibility with old code paths.
    """
    return {}


def save_config(config: dict) -> None:
    """DEPRECATED: George no longer writes a local config.json/accounts cache."""
    return


_ACCOUNT_TYPE_PREFIX = {
    "currentaccount": "current",
    "currentaccount": "current",
    "saving": "saving",
    "loan": "loan",
    "credit": "credit",
    "kredit": "credit",
    "creditcard": "cc",
}


def _slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "account"


def _suggest_account_key(acc: dict, existing: set[str]) -> str:
    """Create a stable, human-usable account key for config.json.

    Prefer a name-based key (for readability) with a short suffix for uniqueness.
    """
    name = _slug(acc.get("name") or "")

    # Keep keys reasonably short
    name = name[:24]

    iban = (acc.get("iban") or "")
    iban_clean = re.sub(r"\s+", "", iban)
    suffix = iban_clean[-4:] if len(iban_clean) >= 4 else str(acc.get("id") or "")[-6:]
    suffix = suffix or "0000"

    base = f"{name}-{suffix}".lower()

    # If that base already exists, fall back to type-based base.
    if base in existing:
        acc_type = (acc.get("type") or "account").lower()
        prefix = _ACCOUNT_TYPE_PREFIX.get(acc_type, acc_type)
        base = f"{prefix}-{suffix}".lower()

    key = base
    i = 2
    while key in existing:
        key = f"{base}-{i}".lower()
        i += 1
    return key


def merge_accounts_into_config(config: dict, fetched_accounts: list[dict]) -> tuple[dict, list[str]]:
    """Merge fetched accounts into config['accounts'] (list).

    Returns (updated_config, changed_ids)
    """
    existing: list[dict]
    accs = config.get("accounts")
    if accs is None:
        existing = []
    elif isinstance(accs, dict):
        existing = list(accs.values())
    else:
        existing = list(accs)

    # Index by (type,id)
    by_tid: dict[tuple[str, str], int] = {}
    for idx, a in enumerate(existing):
        t = (a.get("type") or "").lower()
        i = str(a.get("id") or "")
        if t and i:
            by_tid[(t, i)] = idx

    changed: list[str] = []

    for acc in fetched_accounts:
        t = (acc.get("type") or "").lower()
        i = str(acc.get("id") or "")
        if not (t and i):
            continue

        pos = by_tid.get((t, i))
        if pos is not None:
            existing[pos] = {**existing[pos], **acc}
            changed.append(i)
        else:
            existing.append(acc)
            by_tid[(t, i)] = len(existing) - 1
            changed.append(i)

    # Stable-ish sort: type then name
    existing.sort(key=lambda a: ((a.get("type") or ""), (a.get("name") or "")))

    config["accounts"] = existing
    return config, changed


# Load configuration (lazy loaded later to allow help to run without config)
CONFIG = None


def _sanitize_id(value: str, label: str = "id") -> str:
    """Sanitize an ID parameter to prevent injection via URL or API paths.

    Allows alphanumeric, hyphens, underscores, dots, and spaces (for IBANs).
    Rejects anything that could be used for path traversal or injection.
    """
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValueError(f"Empty {label}")
    if not re.match(r"^[a-zA-Z0-9\s\-_.]+$", cleaned):
        raise ValueError(f"Invalid characters in {label}: {cleaned!r}")
    if ".." in cleaned or "/" in cleaned or "\\" in cleaned:
        raise ValueError(f"Suspicious {label}: {cleaned!r}")
    return cleaned


def get_account(account_key: str) -> dict:
    """Resolve an account by flexible query.

    Matches by:
    - exact id
    - exact IBAN (spaces ignored)
    - substring match on name
    - substring match on type
    - substring match on IBAN

    If ambiguous, raises with candidates.
    """
    q = _sanitize_id(account_key, "account key")
    # Config-less mode: caller must provide the internal account id.
    return {"id": q, "name": q, "iban": None, "type": "unknown"}

    def iban_norm(s: str | None) -> str:
        return re.sub(r"\s+", "", (s or "")).lower()

    # 1) Exact ID match
    for acc in accounts:
        if (acc.get("id") or "").lower() == q:
            return acc

    # 2) Exact IBAN match
    for acc in accounts:
        if acc.get("iban") and iban_norm(acc.get("iban")) == iban_norm(q):
            return acc

    # 3) Fuzzy matches
    matches: list[dict] = []
    for acc in accounts:
        name = (acc.get("name") or "").lower()
        typ = (acc.get("type") or "").lower()
        if q and (q in name or q in typ or (acc.get("iban") and q in iban_norm(acc.get("iban")))):
            matches.append(acc)

    if len(matches) == 1:
        return matches[0]

    if not matches:
        raise ValueError(f"Unknown account: {account_key}. Run 'accounts' to list known accounts (and fetch if empty).")

    # Ambiguous
    lines = [f"Ambiguous account selector '{account_key}'. Matches:"]
    for acc in matches:
        lines.append(f"- {acc.get('name')} ({acc.get('type')}) id={acc.get('id')}")
    raise ValueError("\n".join(lines))


def wait_for_login_approval(page, timeout_seconds: int = 300) -> bool:
    """Wait for user to approve login on phone.

    Important: do NOT scan the entire HTML for generic phrases (they may exist in hidden UI).
    Only react to **visible** error/dismissal messages.
    """
    print(f"[login] Waiting up to {timeout_seconds}s for phone approval...", flush=True)
    start = time.time()
    last_reported = -1

    dismissed_locator = page.locator("text=The login request was dismissed")
    login_failed_locator = page.locator("text=Login failed")
    login_failed_de_locator = page.locator("text=Anmeldung fehlgeschlagen")

    while time.time() - start < timeout_seconds:
        current_url = page.url

        # Success: redirected back into George app (NOT into the IdP/OAuth page)
        if _is_george_app_url(current_url) and not _is_login_flow_url(current_url):
            # Avoid leading newline + make URL logging robust (some terminals wrap weirdly).
            print(f"[login] Approved! Redirected to: {_safe_url_for_logs(current_url)}", flush=True)

            # Optional: provide a human-friendly "expires at" hint (token expiry, not necessarily cookie session expiry).
            ei = _extract_token_expires_in_seconds(current_url)
            if ei:
                expires_at = datetime.now() + timedelta(seconds=ei)
                print(f"[login] Logged in successfully. Token expires at ~{expires_at:%Y-%m-%d %H:%M:%S}", flush=True)

            return True

        # Do not navigate away here.
        # When George is in the middle of the OAuth/approval flow, extra navigations
        # can restart the redirect chain and make approval look like it "did nothing".

        # Dismissed (user rejected)
        try:
            if dismissed_locator.first.is_visible(timeout=200):
                print("\n[login] ❌ LOGIN DISMISSED - user rejected. Start over.", flush=True)
                return False
        except Exception:
            pass

        # Explicit failure message (visible)
        try:
            if login_failed_locator.first.is_visible(timeout=200) or login_failed_de_locator.first.is_visible(timeout=200):
                print("\n[login] Login failed", flush=True)
                return False
        except Exception:
            pass

        # Progress reporting every 10 seconds
        elapsed = int(time.time() - start)
        interval = elapsed // 10
        if interval > last_reported:
            last_reported = interval
            remaining = timeout_seconds - elapsed
            print(f"[login] Still waiting... {remaining}s remaining (url={_safe_url_for_logs(page.url)})", flush=True)

        time.sleep(1)

    print("\n[login] Script timeout waiting for approval", flush=True)
    return False


def extract_verification_code(page) -> str:
    """Extract verification code from login page."""
    try:
        # Wait for the verification code section to appear
        page.wait_for_selector('text=/Verification code/i', timeout=15000)
        time.sleep(1)  # Give it a moment to fully render
        
        all_text = page.inner_text('body')

        # Look for *the* canonical line: "Verification code: XXXX"
        match = re.search(r'\bVerification code:\s*([A-Z0-9]{4})\b', all_text)
        if match:
            return match.group(1)
        
        # Fallback: scan for a line that exactly matches the format
        for line in all_text.split('\n'):
            m = re.match(r'^Verification code:\s*([A-Z0-9]{4})\s*$', line.strip())
            if m:
                return m.group(1)

        return ""
                    
    except PlaywrightTimeout:
        print("[login] Timeout waiting for verification code element", flush=True)
    except Exception as e:
        print(f"[login] Could not extract verification code: {e}", flush=True)
    return ""


def dismiss_modals(page):
    """Dismiss any modal overlays."""
    try:
        for selector in [
            'button:has-text("Dismiss")',
            'button:has-text("Close")',
            'button:has-text("OK")',
            'button[aria-label="Close"]',
        ]:
            btn = page.query_selector(selector)
            if btn and btn.is_visible():
                print(f"[modal] Dismissing via {selector}", flush=True)
                btn.click()
                time.sleep(0.5)
    except Exception:
        pass


def login(page, timeout_seconds: int = 300) -> bool:
    """Perform George login with phone approval."""
    print("[login] Checking session...", flush=True)
    
    # Try dashboard first to see if session is valid.
    # NOTE: Going to about:blank first improves reliability for some SPA sessions.
    try:
        page.goto("about:blank")
        page.goto(DASHBOARD_URL, wait_until="domcontentloaded", timeout=15000)

        # Fast-path decision:
        # - If the session is expired, George usually redirects to the IdP within a second or two.
        # - If the session is valid, the overview tiles appear.
        tiles_visible = False
        t0 = time.time()
        while time.time() - t0 < 4.0:
            if _is_login_flow_url(page.url):
                break
            try:
                page.wait_for_selector(".g-card-overview-title", timeout=500)
                tiles_visible = True
                break
            except Exception:
                time.sleep(0.2)

        if tiles_visible and _is_george_app_url(page.url) and not _is_login_flow_url(page.url):
            # Extra guard: if the George login form is visible, session is NOT valid.
            login_form_visible = False
            try:
                login_form_visible = page.get_by_role(
                    "button", name=re.compile(r"start login", re.I)
                ).is_visible(timeout=800)
            except Exception:
                login_form_visible = False

            if not login_form_visible:
                print("[login] Session still valid!", flush=True)
                return True
    except Exception:
        pass

    print("[login] Session invalid/expired. Navigating to login...", flush=True)

    # Per observed behavior: always start from the overview and let George redirect
    # into the appropriate login/SSO flow.
    page.goto("about:blank")
    page.goto(DASHBOARD_URL, wait_until="domcontentloaded")

    # Wait for the George login form to appear. If it doesn't show up (e.g. we got
    # stuck at the IdP authorize page), fall back to the explicit /#/login route.
    try:
        # Keep this short: we want to type user_id ASAP.
        page.wait_for_selector('input[aria-label*="User"], input[placeholder*="User"], input', timeout=4000)
    except Exception:
        page.goto("about:blank")
        page.goto(LOGIN_URL, wait_until="domcontentloaded")
        page.wait_for_selector('input', timeout=4000)

    time.sleep(0.2)

    if _is_george_app_url(page.url) and not _is_login_flow_url(page.url):
        print("[login] Already logged in (redirected)!", flush=True)
        return True
    
    print(f"[login] Entering user ID...", flush=True)
    
    try:
        user_id = _resolve_user_id(argparse.Namespace(user_id=USER_ID_OVERRIDE))
    except Exception as e:
        print(f"[login] ERROR: {e}")
        return False

    try:
        page.get_by_role("textbox", name=re.compile(r"user number|username", re.I)).fill(user_id)
    except Exception:
        try:
            page.get_by_role("textbox").first.fill(user_id)
        except Exception:
            page.fill('input', user_id)
    
    time.sleep(1)
    print("[login] Clicking 'Start login'...", flush=True)
    
    try:
        page.get_by_role("button", name="Start login").click()
    except Exception:
        btn = page.query_selector('button:has-text("Start login")')
        if btn:
            btn.click()
        else:
            print("[login] ERROR: Could not find login button", flush=True)
            return False
    
    # George renders the verification code asynchronously.
    # Waiting a bit here makes extraction much more reliable.
    time.sleep(5)
    code = extract_verification_code(page)

    if code:
        print(f"[login] Verification code: {code}", flush=True)
    else:
        print("[login] ⚠️ Could not extract code - CHECK BROWSER WINDOW", flush=True)
    
    # NOTE: No macOS-specific notifications. Code is printed to stdout for the caller
    # (Moltbot session) to forward via Telegram.
    return wait_for_login_approval(page, timeout_seconds=timeout_seconds)


def _format_iban(iban: str) -> str:
    clean = re.sub(r"\s+", "", iban).strip()
    # Group in blocks of 4 for readability.
    return " ".join(clean[i : i + 4] for i in range(0, len(clean), 4))


def _short_iban(iban: str | None) -> str:
    if not iban:
        return "IBAN N/A"
    clean = re.sub(r"\s+", "", iban).strip()
    if len(clean) <= 8:
        return clean
    return f"{clean[:4]}...{clean[-4:]}"


def _first_iban_in_text(text: str) -> str | None:
    # Standard Austrian IBAN is 20 chars: AT + 18 digits.
    # Note: don't use a word-boundary here; George sometimes concatenates strings like "...KGAT31...".
    m = re.search(r"AT\d{2}(?:\s*\d{4}){4}", text)
    if m:
        return _format_iban(m.group(0))

    # Fallback: permissive, still anchored on AT + digits.
    m2 = re.search(r"AT\d{2}[0-9\s]{16,30}", text)
    if m2:
        return _format_iban(m2.group(0))

    return None


def capture_bearer_auth_header(context, page, timeout_s: int = 10) -> str | None:
    """Capture Bearer Authorization header from any George API request.

    Note: we listen on the *browser context* (not only the page) because George may
    issue requests from background frames / service worker-like contexts.
    """
    auth_header = {"value": None}

    def _on_request(request) -> None:
        if auth_header["value"]:
            return
        try:
            url = request.url or ""
            # George uses multiple backends; tokens are sent to both netbanking and proxy/g APIs.
            if not (
                url.startswith("https://api.sparkasse.at/rest/netbanking/")
                or url.startswith("https://api.sparkasse.at/proxy/g/api/")
                or url.startswith("https://api.sparkasse.at/sec-trading/")
            ):
                return
            headers = request.headers or {}
            auth = headers.get("authorization") or headers.get("Authorization")
            if auth and auth.lower().startswith("bearer "):
                auth_header["value"] = auth
        except Exception:
            return

    context.on("request", _on_request)
    try:
        # Force a fresh app bootstrap to trigger API calls.
        try:
            page.goto("about:blank")
        except Exception:
            pass

        # Add a cache-buster (before #) to reduce SW/cache short-circuiting.
        bust_url = f"https://george.sparkasse.at/index.html?nocache={int(time.time())}#/overview"
        page.goto(bust_url, wait_until="networkidle")

        start = time.time()
        reloaded = False
        while time.time() - start < timeout_s:
            if auth_header["value"]:
                return auth_header["value"]

            # One best-effort reload mid-way to coax the SPA into firing requests.
            if not reloaded and (time.time() - start) > max(1.0, timeout_s / 3):
                reloaded = True
                try:
                    page.reload(wait_until="networkidle")
                except Exception:
                    pass

            time.sleep(0.2)
    finally:
        try:
            context.off("request", _on_request)
        except Exception:
            pass

    return auth_header["value"]


def fetch_my_accounts(context, auth_header: str) -> dict:
    """Fetch accounts for the current user.

    George uses multiple backends; we've observed that the SPA calls:
      https://api.sparkasse.at/proxy/g/api/my/accounts
    which can include credit-card accounts.

    We keep a fallback to the older REST endpoint.
    """
    urls = [
        "https://api.sparkasse.at/proxy/g/api/my/accounts",
        "https://api.sparkasse.at/rest/netbanking/my/accounts",
    ]

    last_err: Exception | None = None
    for url in urls:
        try:
            resp = context.request.get(url, headers={"Authorization": auth_header}, timeout=30000)
        except Exception as e:
            last_err = e
            continue

        if resp and resp.ok:
            return resp.json()

        # keep trying fallbacks
        last_err = RuntimeError(f"[accounts] API request failed (status={resp.status if resp else 'N/A'}) for {url}")

    raise RuntimeError(f"[accounts] API request failed: {last_err}")


def fetch_my_cards(context, auth_header: str) -> dict:
    """Fetch all cards (debit + credit) for the current user.

    Note: This endpoint returns *plastic cards* plus some credit-card metadata.
    For credit cards, it includes a `creditCardShadowAccountId` that can be
    combined with the card `id` to form the George credit-card "account" id:

        <shadowAccountId>-<cardId>

    This matches the dashboard route: /creditcard/<shadow>-<cardId>
    """
    url = "https://api.sparkasse.at/rest/netbanking/my/cards"
    try:
        resp = context.request.get(url, headers={"Authorization": auth_header}, timeout=30000)
    except Exception as e:
        raise RuntimeError(f"[cards] API request failed: {e}") from e

    if not resp or not resp.ok:
        status = resp.status if resp else "N/A"
        raise RuntimeError(f"[cards] API request failed (status={status})")

    return resp.json()


def fetch_my_securities(context, auth_header: str) -> dict:
    """Fetch securities (depot) accounts list."""
    url = "https://api.sparkasse.at/rest/netbanking/my/securities"
    headers = {
        "Authorization": auth_header,
        "Accept": "application/vnd.at.sitsolutions.services.sec.account.representation.securities.account.list.v3+json",
        "Accept-Language": "en",
    }
    try:
        resp = context.request.get(url, headers=headers, timeout=30000)
    except Exception as e:
        raise RuntimeError(f"[securities] API request failed: {e}") from e

    if not resp or not resp.ok:
        status = resp.status if resp else "N/A"
        raise RuntimeError(f"[securities] API request failed (status={status})")

    return resp.json()


def fetch_my_securities_account(context, auth_header: str, account_id: str) -> dict:
    """Fetch securities (depot) account details, including holdings.

    Security: account_id is user-provided via CLI flags. Treat it as untrusted and
    ensure it cannot influence the request path (e.g. via "/" or ".." segments).
    """
    safe_id = _sanitize_id(account_id, "securities account id")
    safe_id_enc = quote(safe_id, safe="")
    url = f"https://api.sparkasse.at/rest/netbanking/my/securities/{safe_id_enc}"
    headers = {
        "Authorization": auth_header,
        "Accept": "application/vnd.at.sitsolutions.services.sec.account.representation.securities.account.v3+json",
        "Accept-Language": "en",
    }
    try:
        resp = context.request.get(url, headers=headers, timeout=30000)
    except Exception as e:
        raise RuntimeError(f"[securities] API request failed: {e}") from e

    if not resp or not resp.ok:
        status = resp.status if resp else "N/A"
        raise RuntimeError(f"[securities] API request failed (status={status})")

    return resp.json()


def normalize_creditcard_accounts_from_cards(payload) -> list[dict]:
    """Convert /my/cards payload into synthetic George 'creditcard' accounts.

    George exposes credit-card transactions under an account id of the form:
      <creditCardShadowAccountId>-<cardId>

    We store those as accounts so `george.py transactions --account <name>` works.
    """
    if not isinstance(payload, dict):
        return []

    cards = payload.get("cards")
    if not isinstance(cards, list):
        return []

    out: list[dict] = []
    for card in cards:
        if not isinstance(card, dict):
            continue

        # Only credit cards have this mapping.
        shadow = card.get("creditCardShadowAccountId")
        card_id = card.get("id")
        if not (isinstance(shadow, str) and shadow.strip() and isinstance(card_id, str) and card_id.strip()):
            continue

        cc_account_id = f"{shadow.strip()}-{card_id.strip()}"
        name = card.get("productI18N") or card.get("product") or "Credit Card"

        entry = {
            "id": cc_account_id,
            "type": "creditcard",
            "name": str(name),
            "iban": None,
        }

        # Card number (masked) for display (e.g. 530200XXXXXX1006)
        num = card.get("number")
        if isinstance(num, str) and num.strip():
            entry["number"] = num.strip()

        def money_obj(m):
            if not isinstance(m, dict):
                return None
            v = m.get("value")
            prec = m.get("precision")
            cur = m.get("currency")
            if isinstance(v, (int, float)) and isinstance(prec, int) and isinstance(cur, str) and cur.strip():
                return {"amount": float(v) / (10 ** prec), "currency": cur.strip()}
            return None

        # Carry balance + limit (and currency hint)
        bal = money_obj(card.get("balance"))
        if bal:
            entry["balance"] = bal
            entry["currency"] = bal.get("currency")

        limit = money_obj(card.get("limit"))
        if limit:
            entry["limit"] = limit
            if "currency" not in entry and limit.get("currency"):
                entry["currency"] = limit.get("currency")

        out.append(entry)

    return out


def _securities_accounts_list(payload) -> list[dict]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("securitiesAccounts", "items", "accounts", "collection", "data", "content"):
            v = payload.get(key)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
        return [payload] if payload else []
    return []


def _find_securities_account(payload, account_id: str) -> dict | None:
    if not account_id:
        return None
    for acc in _securities_accounts_list(payload):
        acc_id = acc.get("id") or acc.get("accountId") or acc.get("uid") or acc.get("uuid")
        if acc_id is not None and str(acc_id) == str(account_id):
            return acc
    return None


def _collect_titles_from_securities_account(account: dict) -> list[dict]:
    titles: list[dict] = []
    sub = account.get("subSecAccounts")
    if isinstance(sub, list):
        for sub_acc in sub:
            if not isinstance(sub_acc, dict):
                continue
            t = sub_acc.get("titles")
            if isinstance(t, list):
                titles.extend([x for x in t if isinstance(x, dict)])
    return titles


def normalize_depot_accounts_from_securities(payload) -> list[dict]:
    accounts = _securities_accounts_list(payload)
    out: list[dict] = []
    for acc in accounts:
        acc_id = _extract_first(acc, ["id", "accountId", "uid", "uuid"])
        name = _extract_first(acc, ["description", "name", "productI18N", "productName"])
        accountno = _extract_first(acc, ["accountno", "accountNo", "accountNumber"])
        settlement = acc.get("settlementAccount") if isinstance(acc.get("settlementAccount"), dict) else None

        titles = _collect_titles_from_securities_account(acc)
        securities_summary = _sum_securities_titles(titles) if titles else {}

        entry = {
            "id": str(acc_id) if acc_id is not None else "",
            "type": "depot",
            "name": str(name) if name is not None else "Depot",
            "iban": str(accountno) if isinstance(accountno, (str, int)) else None,
            "currency": "EUR",
        }
        if settlement and isinstance(settlement.get("iban"), str) and settlement.get("iban").strip():
            entry["settlementAccount"] = {"iban": settlement.get("iban").strip()}
            if isinstance(settlement.get("currency"), str) and settlement.get("currency").strip():
                entry["settlementAccount"]["currency"] = settlement.get("currency").strip()

        if securities_summary:
            entry["securities"] = securities_summary

        out.append(entry)

    return out


def _extract_first(d: dict, keys: list[str]) -> object | None:
    for k in keys:
        if k in d and d.get(k) is not None:
            return d.get(k)
    return None


def _extract_amount(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip().replace(".", "").replace(",", ".")
        try:
            return float(s)
        except Exception:
            return None
    if isinstance(value, dict):
        # Common George money object: { value: 18245, precision: 2, currency: 'EUR' }
        if "value" in value and isinstance(value.get("value"), (int, float)):
            prec = value.get("precision")
            if isinstance(prec, int) and prec >= 0:
                return float(value.get("value")) / (10 ** prec)

        for k in ("value", "amount", "balance", "disposable", "available"):
            if k in value:
                out = _extract_amount(value.get(k))
                if out is not None:
                    return out
        for k in ("valueInCents", "amountInCents", "cents", "amountCents", "valueCents"):
            if k in value and isinstance(value.get(k), (int, float)):
                return float(value.get(k)) / 100.0
    return None


def _extract_currency(value) -> str | None:
    if isinstance(value, dict):
        for k in ("currency", "ccy"):
            v = value.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
    return None


def _extract_money(value) -> tuple[float | None, str | None]:
    amount = _extract_amount(value)
    currency = _extract_currency(value)
    if isinstance(currency, str):
        currency = currency.strip()
    return amount, currency


def _sum_securities_titles(titles: list[dict]) -> dict:
    total_value = 0.0
    total_perf = 0.0
    value_ccy = None
    perf_ccy = None

    weighted_pct_sum = 0.0
    weighted_pct_weight = 0.0

    for title in titles:
        if not isinstance(title, dict):
            continue

        mv_amt, mv_ccy = _extract_money(title.get("marketValue"))
        if mv_amt is not None and mv_ccy:
            if value_ccy is None:
                value_ccy = mv_ccy
            if mv_ccy == value_ccy:
                total_value += mv_amt

        perf_amt, perf_ccy_val = _extract_money(title.get("performance"))
        if perf_amt is not None and perf_ccy_val:
            if perf_ccy is None:
                perf_ccy = perf_ccy_val
            if perf_ccy_val == perf_ccy:
                total_perf += perf_amt

        pct = title.get("performancePercent")
        if pct is None:
            pct = title.get("performancePercentInclFees") or title.get("performancePercentExclFees")
        if isinstance(pct, (int, float)) and mv_amt is not None and mv_amt != 0:
            weighted_pct_sum += float(pct) * abs(mv_amt)
            weighted_pct_weight += abs(mv_amt)

    out: dict = {}
    if value_ccy is None:
        value_ccy = perf_ccy
    if total_value or (value_ccy is not None and total_value == 0.0):
        out["value"] = {"amount": total_value, "currency": value_ccy or "EUR"}
    if total_perf or (perf_ccy is not None and total_perf == 0.0):
        profit = {"amount": total_perf, "currency": perf_ccy or value_ccy or "EUR"}
        if weighted_pct_weight > 0:
            profit["percent"] = weighted_pct_sum / weighted_pct_weight
        out["profitLoss"] = profit

    return out


def normalize_accounts_from_api(payload) -> list[dict]:
    if payload is None:
        return []

    accounts = None
    if isinstance(payload, list):
        accounts = payload
    elif isinstance(payload, dict):
        for key in ("items", "accounts", "collection", "data", "content", "accountList"):
            v = payload.get(key)
            if isinstance(v, list):
                accounts = v
                break
        else:
            accounts = [payload]
    else:
        return []

    normalized: list[dict] = []
    for acc in accounts:
        if not isinstance(acc, dict):
            continue
        acc_id = _extract_first(acc, ["id", "accountId", "uid", "uuid"])
        acc_type = _extract_first(acc, ["type", "accountType", "productType", "accountCategory"])
        name = _extract_first(acc, ["name", "alias", "productName", "description", "accountLabel", "accountName"])
        iban = _extract_first(acc, ["iban", "ibanNumber", "ibanFormatted"])
        currency = _extract_first(acc, ["currency", "ccy"])

        # /proxy/g/api/my/accounts includes embedded `card` objects.
        # Treat CREDIT cards as synthetic creditcard accounts (skip non-credit cards).
        card = acc.get("card") if isinstance(acc.get("card"), dict) else None
        card_number: str | None = None
        if card:
            card_type = (card.get("type") or "").lower()
            flags = acc.get("flags") if isinstance(acc.get("flags"), list) else []
            is_cc = (card_type == "credit") or ("CC" in flags)
            if not is_cc:
                continue

            acc_type = "creditcard"
            name = card.get("productI18N") or card.get("product") or name
            num = card.get("number")
            if isinstance(num, str) and num.strip():
                card_number = num.strip()

            # Prefer currency from card balance/limit if present.
            if currency is None and isinstance(card.get("balance"), dict):
                cur = card.get("balance", {}).get("currency")
                if isinstance(cur, str) and cur.strip():
                    currency = cur.strip()
            if currency is None and isinstance(card.get("limit"), dict):
                cur = card.get("limit", {}).get("currency")
                if isinstance(cur, str) and cur.strip():
                    currency = cur.strip()

        # George /my/accounts shape nests IBAN in accountno.iban
        if iban is None:
            accountno = acc.get("accountno") or acc.get("accountNo") or acc.get("accountNumber")
            if isinstance(accountno, dict):
                iban = accountno.get("iban") or accountno.get("IBAN")

        if isinstance(iban, dict):
            iban = _extract_first(iban, ["iban", "ibanNumber", "value"])

        entry = {
            "id": str(acc_id) if acc_id is not None else "",
            "type": (str(acc_type) if acc_type is not None else "").lower(),
            "name": str(name) if name is not None else "",
            "iban": str(iban) if iban is not None else None,
        }

        if card_number:
            entry["number"] = card_number

        if currency:
            entry["currency"] = str(currency)

        desc = _extract_first(acc, ["description"])
        alias = _extract_first(acc, ["alias"])
        if desc:
            entry["description"] = str(desc)
        if alias:
            entry["alias"] = str(alias)

        normalized.append(entry)

    return normalized


def _extract_money_from_account(acc: dict, value_keys: list[str], currency_keys: list[str]) -> tuple[float | None, str | None]:
    raw = _extract_first(acc, value_keys)
    amount = _extract_amount(raw)
    currency = _extract_currency(raw) or _extract_first(acc, currency_keys)
    if isinstance(currency, str):
        currency = currency.strip()
    return amount, currency


def try_extract_iban_from_account_page(page, acc_type: str, acc_id: str) -> str | None:
    """Try to extract IBAN by visiting the account detail page.

    This is slower than scraping the overview but tends to be more reliable.
    """
    try:
        page.goto("about:blank")
        page.goto(f"{BASE_URL}/index.html#/{acc_type}/{acc_id}", wait_until="domcontentloaded", timeout=15000)
        # Give SPA some time to render details.
        time.sleep(2)
        dismiss_modals(page)
        body = page.inner_text("body")
        return _first_iban_in_text(body)
    except Exception:
        return None


def list_accounts_from_page(page) -> list[dict]:
    """Fetch account list from George dashboard."""
    print("[accounts] Fetching accounts from dashboard...", flush=True)
    # Avoid networkidle (SPA + long-polling). domcontentloaded is more reliable here.
    page.goto(DASHBOARD_URL, wait_until="domcontentloaded")
    ensure_list_layout(page)

    # Wait for account list + lazy loading
    try:
        page.wait_for_selector(".g-card-overview-title", timeout=30000)
        time.sleep(3)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
    except Exception:
        pass

    dismiss_modals(page)

    accounts = []

    # Parse account links from the overview (including loans)
    links = page.query_selector_all('a[href*="/currentAccount/"], a[href*="/saving/"], a[href*="/loan/"], a[href*="/credit/"], a[href*="/kredit/"], a[href*="/creditcard/"]')

    for link in links:
        try:
            href = link.get_attribute('href') or ""

            match = re.search(r'/(currentAccount|saving|loan|credit|kredit|creditcard)/([A-F0-9-]+)', href)
            if not match:
                continue

            acc_type = match.group(1)
            acc_id = match.group(2)

            # The IBAN is usually NOT inside the <a> text; it's nearby within the card.
            # Grab a larger text blob by walking up the DOM.
            card_text = ""
            try:
                card_text = link.evaluate(
                    """
                    (el) => {
                      let cur = el;
                      for (let i = 0; i < 10 && cur; i++) {
                        const t = (cur.innerText || '').trim();
                        if (t && t.length > 20) return t;
                        cur = cur.parentElement;
                      }
                      return (el.parentElement?.innerText || '').trim();
                    }
                    """
                )
            except Exception:
                card_text = (link.inner_text() or "")

            # Name: first line of the card text
            name = (card_text.split("\n")[0] if card_text else "").strip() or (link.inner_text() or "").split("\n")[0].strip()

            # IBAN: matches both spaced and non-spaced formats
            iban = _first_iban_in_text(card_text)

            accounts.append({
                "name": name,
                "iban": iban,
                "id": acc_id,
                "type": acc_type,
            })
        except Exception:
            continue

    # Deduplicate by ID
    seen = set()
    unique = []
    for acc in accounts:
        if acc["id"] not in seen:
            seen.add(acc["id"])
            unique.append(acc)

    return unique


def ensure_list_layout(page) -> None:
    """Ensure the dashboard is in list layout (not tiles).

    List layout is more consistent for scraping (IBAN next to available amount).
    """
    try:
        btn = page.locator('[data-cy="dashboard-view-mode-toggle-list-button"]')
        if btn.count() > 0:
            # If aria-pressed isn't true, click it.
            pressed = (btn.first.get_attribute("aria-pressed") or "").lower() == "true"
            if not pressed:
                btn.first.click(force=True)
                time.sleep(1)
    except Exception:
        pass


def list_account_balances_from_overview(page) -> list[dict]:
    """Return accounts with (balance, available) as shown on the George overview page."""
    # Avoid networkidle (SPA + long-polling). domcontentloaded is more reliable here.
    page.goto(DASHBOARD_URL, wait_until="domcontentloaded")
    ensure_list_layout(page)
    
    # Wait for skeletons to load
    print("[accounts] Waiting for account list to load...", flush=True)
    try:
        # Wait for at least one account title to appear
        page.wait_for_selector(".g-card-overview-title", timeout=30000)
        # Give it a bit more time for all to settle
        time.sleep(5)

        # Scroll to bottom to trigger lazy loading
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        print("[accounts] Scrolled to bottom, waiting 5s...", flush=True)
        time.sleep(5)

        # Try again after scroll (sometimes overview populates late)
        page.wait_for_selector(".g-card-overview-title", timeout=20000)
    except Exception:
        print("[accounts] Warning: Timeout waiting for account list", flush=True)

    dismiss_modals(page)
    
    # Account cards typically have a heading (h3) with account name and nearby balance text.
    # Include currentAccount, saving, loan/credit accounts, and credit cards
    cards = page.query_selector_all('h3:has(a[href*="/currentAccount/"]), h3:has(a[href*="/saving/"]), h3:has(a[href*="/loan/"]), h3:has(a[href*="/credit/"]), h3:has(a[href*="/kredit/"]), h3:has(a[href*="/creditcard/"])')

    results: list[dict] = []

    def parse_amount(s: str) -> float:
        return float(s.replace('.', '').replace(',', '.'))

    for h3 in cards:
        try:
            name = (h3.inner_text() or "").strip()
            link = h3.query_selector('a')
            href = link.get_attribute('href') if link else ""
            m = re.search(r'/(currentAccount|saving|loan|credit|kredit|creditcard)/([A-F0-9-]+)', href or "")
            if not m:
                continue
            acc_type, acc_id = m.group(1), m.group(2)
            
            # Debug: print card info
            # print(f"[debug] Checking card: {name} ({acc_type}/{acc_id})", flush=True)

            # Grab surrounding card text: climb ancestors until we see currency/amount patterns
            card_text = ""
            try:
                card_text = h3.evaluate(
                    """
                    (el) => {
                      const want = /(amount|betrag|stand|eur|usd|chf|gbp|€|minus|[0-9]{1,3}(\\.[0-9]{3})*,[0-9]{2})/i;
                      let cur = el;
                      for (let i = 0; i < 10 && cur; i++) {
                        const t = (cur.innerText || '').trim();
                        if (t && t.length > 20 && want.test(t)) {
                          return t;
                        }
                        cur = cur.parentElement;
                      }
                      // fallback: parent text
                      return (el.parentElement?.innerText || '').trim();
                    }
                    """
                )
            except Exception:
                card_text = (h3.inner_text() or "").strip()
            
            # Debug: print card info if needed
            # print(f"[debug] Card: {name} | Text: {card_text!r}", flush=True)

            # BALANCE: prefer the "Amount:" line if present
            balance = None
            currency = None

            # Accept currency codes or symbols
            ccy_pat = r'(EUR|USD|CHF|GBP|€|\$)'

            # Matches e.g. "Amount: 852,53 EUR" or German variants
            # Note: The "Amount:" line often has raw numbers like 155470,53 (no dots),
            # while the UI display has 155.470,53. We match both.
            amount_match = re.search(
                rf'(Amount|Betrag|Stand)\s*:?\s*(Minus\s+)?([0-9.]+,\s*[0-9]{{2}})\s*{ccy_pat}',
                card_text,
                re.IGNORECASE,
            )
            if amount_match:
                sign = -1 if amount_match.group(2) else 1
                balance = sign * parse_amount(amount_match.group(3))
                currency = amount_match.group(4)
            else:
                # Fallback: first currency amount on the card
                any_match = re.search(rf'(Minus\s+)?([0-9.]+,\s*[0-9]{{2}})\s*{ccy_pat}', card_text)
                if any_match:
                    sign = -1 if any_match.group(1) else 1
                    balance = sign * parse_amount(any_match.group(2))
                    currency = any_match.group(3)

            # Normalize currency symbols
            if currency == '€':
                currency = 'EUR'
            if currency == '$':
                currency = 'USD'

            # AVAILABLE: e.g. "434,65 EUR available" or "€ 434,65 available" or "verfügbar"
            available = None
            available_currency = None
            # Try pattern: "amount CCY available" or "CCY amount available"
            avail_match = re.search(
                rf'([0-9]{{1,3}}(?:\.[0-9]{{3}})*,[0-9]{{2}})\s*{ccy_pat}\s*(available|verf\u00fcgbar)',
                card_text,
                re.IGNORECASE,
            )
            if not avail_match:
                # Try: "€ 434,65 available"
                avail_match = re.search(
                    rf'{ccy_pat}\s*([0-9]{{1,3}}(?:\.[0-9]{{3}})*,[0-9]{{2}})\s*(available|verf\u00fcgbar)',
                    card_text,
                    re.IGNORECASE,
                )
            if avail_match:
                # Groups depend on which pattern matched
                g1, g2 = avail_match.group(1), avail_match.group(2)
                # Figure out which is amount vs currency
                if re.match(r'[0-9]', g1):
                    available = parse_amount(g1)
                    available_currency = g2
                else:
                    available_currency = g1
                    available = parse_amount(g2)
                if available_currency == '€':
                    available_currency = 'EUR'
                if available_currency == '$':
                    available_currency = 'USD'
            else:
                # Debug if the card mentions available/verfügbar but regex didn't match
                if re.search(r'(available|verf)', card_text, re.IGNORECASE):
                    snippet = re.sub(r'\s+', ' ', card_text).strip()[:220]
                    print(f"[balances] WARN could not parse AVAILABLE for '{name}'. Snippet: {snippet}", flush=True)

            # Debug snippet if we failed to parse
            if balance is None:
                snippet = re.sub(r'\s+', ' ', card_text).strip()[:180]
                print(f"[balances] WARN could not parse balance for '{name}'. Snippet: {snippet}", flush=True)

            results.append({
                "name": name,
                "type": acc_type,
                "id": acc_id,
                "balance": balance,
                "currency": currency,
                "available": available,
                "available_currency": available_currency,
            })
        except Exception:
            continue

    # Deduplicate by id
    seen = set()
    out = []
    for r in results:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        out.append(r)
    return out


def download_statements_pdf(page, account: dict, statement_ids: list[int], 
                            include_receipts: bool = True, download_dir: Path = None) -> list[Path]:
    """Download PDF statements for an account."""
    acc_type = account["type"]
    acc_id = account["id"]
    acc_name = account["name"]
    
    url = f"https://george.sparkasse.at/index.html#/{acc_type}/{acc_id}/statements"
    print(f"[statements] Downloading statements {statement_ids} for {acc_name}...", flush=True)
    
    page.goto(url, wait_until="networkidle")
    time.sleep(2)
    dismiss_modals(page)
    time.sleep(1)
    
    # Enter multi-select mode
    try:
        page.get_by_role("button", name="Download multiple").click()
        time.sleep(1)
    except Exception:
        print("[statements] Could not find 'Download multiple' button", flush=True)
        return []
    
    # Select statements
    for stmt_id in statement_ids:
        try:
            page.get_by_role("checkbox", name=f"Statement - {stmt_id}").check()
            time.sleep(0.3)
        except Exception:
            print(f"[statements] WARNING: Could not find statement {stmt_id}", flush=True)
    
    # Click Download
    print("[statements] Opening download dialog...", flush=True)
    try:
        page.get_by_role("button", name="Download").first.click()
    except Exception:
        btn = page.query_selector('button:has-text("Download"):not([disabled])')
        if btn:
            btn.click()
    time.sleep(2)
    
    # Check "incl. booking receipts"
    if include_receipts:
        print("[statements] Checking 'incl. booking receipts'...", flush=True)
        try:
            page.get_by_text("booking receipts").click()
            time.sleep(0.5)
        except Exception as e:
            print(f"[statements] Could not check receipts: {e}", flush=True)
    
    # Click Download in dialog
    print("[statements] Starting download...", flush=True)
    try:
        with page.expect_download(timeout=120000) as download_info:
            modal_download = page.locator('.g-modal button:has-text("Download")')
            if modal_download.count() > 0:
                modal_download.first.click(force=True)
            else:
                page.get_by_role("button", name="Download").last.click(force=True)
        
        download = download_info.value
        safe_name = _safe_download_filename(download.suggested_filename)
        print(f"[statements] Downloaded: {safe_name}", flush=True)
        
        if download_dir:
            dest = download_dir / safe_name
            download.save_as(dest)
            print(f"[statements] Saved: {dest}", flush=True)
            return [dest]
    except Exception as e:
        print(f"[statements] Download failed: {e}", flush=True)
    
    return []


EXPORT_TYPES = ["camt53", "mt940"]
DEFAULT_EXPORT_TYPE = "camt53"
EXPORT_TYPE_LABELS = {
    "camt53": "CAMT53",
    "mt940": "MT940",
}

DATACARRIER_UPLOAD_URL = "https://george.sparkasse.at/index.html#/datacarrier/upload"
DATACARRIER_SIGN_API_TEMPLATE = "https://api.sparkasse.at/rest/netbanking/my/orders/datacarriers/{datacarrier_id}/sign/"
DATACARRIER_FILES_API_URL = "https://api.sparkasse.at/rest/netbanking/my/orders/datacarrier-files"


def download_data_exports(page, export_type: str, download_dir: Path = None) -> list[Path]:
    """Download data exports (CAMT53/MT940) for all available accounts."""
    export_type = export_type.lower()
    if export_type not in EXPORT_TYPES:
        print(f"[export] Invalid type '{export_type}'. Supported: {', '.join(EXPORT_TYPES)}", flush=True)
        return []

    label = EXPORT_TYPE_LABELS[export_type]
    print(f"[export] Downloading {label} data exports (all accounts)...", flush=True)

    page.goto("https://george.sparkasse.at/index.html#/datacarrier/download", wait_until="networkidle")
    time.sleep(2)
    dismiss_modals(page)

    downloaded = []
    rows = page.query_selector_all(f'tr:has-text("{label}")')
    if not rows:
        print(f"[export] No {label} exports found", flush=True)
        return []

    for row in rows:
        download_btn = row.query_selector("button")
        if not download_btn:
            continue
        try:
            with page.expect_download(timeout=30000) as download_info:
                download_btn.click()
            dl = download_info.value
            if download_dir:
                safe_name = _safe_download_filename(dl.suggested_filename)
                dest = download_dir / safe_name
                dl.save_as(dest)
                print(f"[export] Saved: {safe_name}", flush=True)
                downloaded.append(dest)
            time.sleep(1)
        except Exception as e:
            print(f"[export] Download failed: {e}", flush=True)

    return downloaded


def _click_first_visible_button(page, selectors: list[str]) -> bool:
    for selector in selectors:
        try:
            btn = page.query_selector(selector)
            if btn and btn.is_visible():
                btn.click()
                return True
        except Exception:
            continue
    return False


def _try_select_datacarrier_type(page, file_type: str) -> None:
    if not file_type:
        return

    # Try native <select> first
    try:
        select_el = page.locator("select")
        if select_el.count() > 0:
            select_el.first.select_option(label=file_type)
            time.sleep(0.5)
            return
    except Exception:
        pass

    # Try combobox/option roles
    try:
        combo = page.get_by_role("combobox").first
        if combo and combo.is_visible():
            combo.click()
            time.sleep(0.3)
            option = page.get_by_role("option", name=re.compile(re.escape(file_type), re.I))
            if option.count() > 0:
                option.first.click()
                time.sleep(0.3)
                return
    except Exception:
        pass

    # Fallback: clickable labels/buttons with the type text
    try:
        btn = page.locator(f'button:has-text("{file_type}")')
        if btn.count() > 0 and btn.first.is_visible():
            btn.first.click()
            time.sleep(0.3)
            return
    except Exception:
        pass


def upload_datacarrier_file(page, file_path: Path, file_type: str | None = None) -> dict | None:
    print(f"[datacarrier-upload] Opening upload page...", flush=True)
    page.goto(DATACARRIER_UPLOAD_URL, wait_until="domcontentloaded")
    time.sleep(2)
    dismiss_modals(page)

    if file_type:
        print(f"[datacarrier-upload] Selecting type: {file_type}", flush=True)
        _try_select_datacarrier_type(page, file_type)

    def _is_datacarrier_response(resp) -> bool:
        try:
            return resp.request.method == "POST" and "/datacarrier-files" in (resp.url or "")
        except Exception:
            return False

    upload_buttons = [
        'button:has-text("Upload")',
        'button:has-text("Send")',
        'button:has-text("Submit")',
        'button:has-text("Import")',
        'button:has-text("Start")',
        'button:has-text("Weiter")',
        'button:has-text("Senden")',
        'button[type="submit"]',
    ]

    # Find the file input
    try:
        file_input = page.locator('input[type="file"]')
        file_input.wait_for(timeout=30000)
    except Exception as e:
        print(f"[datacarrier-upload] ERROR: Could not find file input: {e}", flush=True)
        return None

    response = None
    try:
        with page.expect_response(_is_datacarrier_response, timeout=120000) as resp_info:
            file_input.set_input_files(str(file_path))
            clicked = _click_first_visible_button(page, upload_buttons)
            if not clicked:
                # Some UIs auto-upload after file selection
                pass
        response = resp_info.value
    except PlaywrightTimeout:
        print("[datacarrier-upload] ERROR: Timed out waiting for upload response", flush=True)
        return None

    try:
        return response.json()
    except Exception:
        try:
            text = response.text()
            return {"raw": text}
        except Exception:
            return {"raw": "<unparseable response>"}


def _extract_sign_state(payload: dict | None) -> tuple[str | None, str | None]:
    if not isinstance(payload, dict):
        return None, None
    sign_id = payload.get("signId") or payload.get("id")
    sign_info = payload.get("signInfo")
    state = None
    if isinstance(sign_info, dict):
        state = sign_info.get("state")
    return sign_id, state


def _extract_sign_id_from_url(url: str | None) -> str | None:
    if not url:
        return None
    try:
        path = urlsplit(url).path or ""
        parts = [p for p in path.split("/") if p]
        if not parts:
            return None
        # .../datacarriers/<id>/sign/<signId>
        if parts[-1] and parts[-1].lower() != "sign":
            return parts[-1]
    except Exception:
        return None
    return None


def _build_datacarrier_files_list_url() -> str:
    return f"{DATACARRIER_FILES_API_URL}?page=0&size=100"


def _extract_datacarrier_file_state(payload, file_id: str | int | None) -> tuple[str | None, dict | None]:
    if file_id is None:
        return None, None

    items = []
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        for key in ("items", "data", "datacarrierFiles", "files", "content"):
            v = payload.get(key)
            if isinstance(v, list):
                items = v
                break
        else:
            items = [payload]

    file_id_s = str(file_id)
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id") or item.get("fileId") or item.get("uuid")
        if item_id is not None and str(item_id) == file_id_s:
            state = item.get("state") or item.get("status")
            return state, item
    return None, None


def _click_confirmation_button(page) -> bool:
    try:
        locator = page.get_by_role("button", name=re.compile(r"(sign|confirm|weiter|best.?tigen)", re.I))
        count = locator.count()
        for idx in range(count):
            btn = locator.nth(idx)
            try:
                if btn.is_visible():
                    btn.click()
                    return True
            except Exception:
                continue
    except Exception:
        return False
    return False


def _parse_ddmmyyyy(s: str) -> date:
    return datetime.strptime(s, "%d.%m.%Y").date()


def _normalize_date_range(date_from: str | None, date_to: str | None) -> tuple[str | None, str]:
    """Return (date_from, date_to) as strings in DD.MM.YYYY.

    - date_to defaults to today
    - if date_to is in the future, clamp to today
    """
    today = date.today()

    df = _parse_ddmmyyyy(date_from) if date_from else None
    dt = _parse_ddmmyyyy(date_to) if date_to else today

    if dt > today:
        dt = today

    if df and df > dt:
        raise ValueError(f"date_from {df} is after date_to {dt}")

    df_s = df.strftime("%d.%m.%Y") if df else None
    dt_s = dt.strftime("%d.%m.%Y")
    return df_s, dt_s


# Supported transaction export formats (unified UX)
TRANSACTION_EXPORT_FORMATS = ["csv", "json"]
DEFAULT_TRANSACTION_FORMAT = "json"

def download_transactions(page, account: dict, date_from: str = None, date_to: str = None,
                          download_dir: Path = None, fmt: str = "csv") -> list[Path]:
    """Download transactions for an account in the specified format.
    
    Args:
        page: Playwright page object
        account: Account dict with type, id, name, iban
        date_from: Start date (DD.MM.YYYY)
        date_to: End date (DD.MM.YYYY)
        download_dir: Directory to save downloaded file
        fmt: Export format (csv, json, ofx, xlsx)
    
    Returns:
        List of downloaded file paths
    """
    acc_type = account["type"]
    acc_id = account["id"]
    acc_name = account["name"]
    fmt = fmt.lower()
    
    if fmt not in TRANSACTION_EXPORT_FORMATS:
        print(f"[transactions] Invalid format '{fmt}'. Supported: {', '.join(TRANSACTION_EXPORT_FORMATS)}", flush=True)
        return []
    
    url = f"https://george.sparkasse.at/index.html#/{acc_type}/{acc_id}"
    print(f"[transactions] Downloading {fmt.upper()} transactions for {acc_name}...", flush=True)
    
    page.goto(url, wait_until="networkidle")
    time.sleep(2)
    dismiss_modals(page)
    
    # Look for export/download button in transaction history
    # George has a "Print Overview" or export option
    try:
        # Try to find export button
        export_btn = page.query_selector('button:has-text("Export")')
        if not export_btn:
            export_btn = page.query_selector('button:has-text("Download")')
        if not export_btn:
            # Look for three-dot menu
            more_btn = page.query_selector('button:has-text("More")')
            if more_btn:
                more_btn.click()
                time.sleep(1)
                export_btn = page.query_selector('button:has-text("Export")')
        
        if export_btn:
            export_btn.click()
            time.sleep(2)
            
            # Select the requested format
            format_label = TRANSACTION_FORMAT_LABELS.get(fmt, fmt.upper())
            format_option = page.query_selector(f'text={format_label}')
            if not format_option and fmt == "xlsx":
                # Try alternate labels for Excel
                format_option = page.query_selector('text=XLSX') or page.query_selector('text=Excel')
            if format_option:
                format_option.click()
                time.sleep(1)
            elif fmt != "csv":
                # If specific format not found and it's not CSV, warn user
                print(f"[transactions] Warning: Could not find {fmt.upper()} option, attempting default download", flush=True)
            
            # Click final download
            with page.expect_download(timeout=60000) as download_info:
                dl_btn = page.query_selector('button:has-text("Download")')
                if dl_btn:
                    dl_btn.click(force=True)
            
            dl = download_info.value
            if download_dir:
                # Normalize filename to include account + date range (and clamp future end-date to today)
                iban = (account.get("iban") or "").replace(" ", "")
                if not iban:
                    iban = account.get("id")

                df, dt = _normalize_date_range(date_from, date_to)
                df_iso = _parse_ddmmyyyy(df).isoformat() if df else f"{date.today().year}-01-01"
                dt_iso = _parse_ddmmyyyy(dt).isoformat()

                dest = download_dir / f"{iban}_{df_iso}_{dt_iso}.{fmt}"
                dl.save_as(dest)
                print(f"[transactions] Saved: {dest}", flush=True)
                return [dest]
        else:
            print("[transactions] Could not find export button - trying History page", flush=True)
            
            # Navigate to history page
            history_url = f"https://george.sparkasse.at/index.html#/{acc_type}/{acc_id}/history"
            page.goto(history_url, wait_until="networkidle")
            time.sleep(2)
            
            # TODO: Implement date filtering and export from history
            print("[transactions] History-based export not yet implemented", flush=True)
            
    except Exception as e:
        print(f"[transactions] Export failed: {e}", flush=True)
    
    return []


# Legacy alias for backward compatibility
def download_csv_transactions(page, account: dict, date_from: str = None, date_to: str = None,
                              download_dir: Path = None) -> list[Path]:
    """Download transaction CSV for an account. (Legacy - use download_transactions instead)"""
    return download_transactions(page, account, date_from, date_to, download_dir, fmt="csv")


# =============================================================================
# CLI Commands
# =============================================================================

def cmd_login(args):
    """Perform standalone login."""
    try:
        user_id = _resolve_user_id(args)
    except Exception as e:
        print(f"[login] ERROR: {e}")
        return 1

    profile_dir = _get_profile_dir(user_id)
    _ensure_dir(profile_dir)
    print(f"[login] User: {user_id}", flush=True)

    global USER_ID_OVERRIDE
    USER_ID_OVERRIDE = user_id

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=not args.visible,
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()
        try:
            if login(page, timeout_seconds=_login_timeout(args)):
                # Best-effort: harden Playwright profile permissions after login.
                _harden_tree(profile_dir)
                print(f"[login] Success! Session saved to {profile_dir.name}", flush=True)
                return 0
            return 1
        finally:
            context.close()


def cmd_logout(args):
    """Clear session/profile for the selected user."""
    try:
        user_id = _resolve_user_id(args)
    except Exception as e:
        print(f"[logout] ERROR: {e}")
        return 1

    profile_dir = _get_profile_dir(user_id)
    if profile_dir.exists():
        import shutil
        try:
            shutil.rmtree(profile_dir)
            print(f"[logout] Removed profile for {user_id} at {profile_dir.name}", flush=True)
            return 0
        except Exception as e:
            print(f"[logout] Error removing profile: {e}", flush=True)
            return 1

    print(f"[logout] No session found for {user_id}.", flush=True)
    return 0


def _resolve_user_id(args) -> str:
    """Resolve the George user id.

    Precedence:
    1) --user-id (explicit)
    2) GEORGE_USER_ID from environment

    """
    if getattr(args, "user_id", None):
        return str(args.user_id).strip()

    env_uid = os.environ.get("GEORGE_USER_ID")
    if env_uid and env_uid.strip():
        return env_uid.strip()

    raise ValueError(
        "No user id configured. Provide one of:\n"
        "- --user-id <your-user-number-or-username>\n"
        "- set GEORGE_USER_ID env var"
    )


def cmd_setup(args):
    """Setup George user ID and ensure playwright is installed."""

    print("[setup] George Banking Setup")
    print()
    
    # Get user ID from args or env
    user_id = args.user_id or os.environ.get("GEORGE_USER_ID", "")
    
    if not user_id:
        print("[setup] ERROR: User ID required")
        print("[setup] Provide via --user-id flag or GEORGE_USER_ID env var")
        return 1
    
    # Create config directory
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create config.json
    config = {
        "user_id": user_id,
        "accounts": []
    }
    
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

    print(f"[setup] ✓ Config saved to {CONFIG_PATH}")
    print(f"[setup] To discover accounts, run: george.py accounts")
    print(f"[setup] To override user_id without editing config: george.py --user-id <id> ...")
    
    # Check playwright
    print("[setup] Checking playwright...")
    try:
        from playwright.sync_api import sync_playwright
        print("[setup] ✓ Playwright available")
    except ImportError:
        print("[setup] ERROR: Playwright not installed")
        print("[setup] Run: pip install playwright && playwright install chromium")
        return 1
    
    print()
    print("[setup] ✓ Setup complete!")
    print(f"[setup] Next steps:")
    print(f"  1. george.py accounts                # Discover + save your accounts")
    print(f"  2. george.py balances           # Test with balances")
    
    return 0


def cmd_accounts(args):
    """List accounts for the selected user (live; no local config/cache)."""
    try:
        user_id = _resolve_user_id(args)
    except Exception as e:
        print(f"[accounts] ERROR: {e}")
        return 1

    profile_dir = _get_profile_dir(user_id)
    global USER_ID_OVERRIDE
    USER_ID_OVERRIDE = user_id

    raw_payload = None
    raw_path = None
    normalized: list[dict] = []

    print(f"[accounts] Fetching live accounts for {user_id}...", flush=True)
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=not args.visible,
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        try:
            auth_header_value: str | None = None

            # 1) Prefer cached token to avoid interactive login.
            token_cache = _load_token_cache(user_id) or {}
            token = token_cache.get("accessToken") if isinstance(token_cache, dict) else None
            if isinstance(token, str) and token.strip():
                try:
                    auth_header_value = f"Bearer {token.strip()}"
                    raw_payload = fetch_my_accounts(context, auth_header_value)
                except Exception:
                    raw_payload = None
                    auth_header_value = None

            # 2) If token didn't work, do interactive login (phone approval) and capture auth.
            if raw_payload is None:
                if not login(page, timeout_seconds=_login_timeout(args)):
                    return 1

                dismiss_modals(page)

                auth_header = capture_bearer_auth_header(context, page, timeout_s=10)
                if not auth_header:
                    print("[accounts] ERROR: Could not capture API Authorization header", flush=True)
                    return 1

                auth_header_value = auth_header
                raw_payload = fetch_my_accounts(context, auth_header_value)
                tok = _extract_bearer_token(auth_header_value)
                if tok:
                    _save_token_cache(user_id, tok, source="auth_header")

            raw_path = _write_debug_json("my-accounts-raw", raw_payload)

            normalized = normalize_accounts_from_api(raw_payload)

            # Also fetch credit card metadata, so we can add CC 'shadow accounts' without scraping.
            try:
                if auth_header_value:
                    cards_payload = fetch_my_cards(context, auth_header_value)
                    cc_accounts = normalize_creditcard_accounts_from_cards(cards_payload)
                else:
                    cc_accounts = []
            except Exception:
                cc_accounts = []

            if cc_accounts:
                by_id = {str(a.get("id") or ""): a for a in normalized if str(a.get("id") or "").strip()}
                for acc in cc_accounts:
                    acc_id = str(acc.get("id") or "").strip()
                    if not acc_id:
                        continue
                    if acc_id in by_id:
                        by_id[acc_id].update({k: v for k, v in acc.items() if v is not None})
                    else:
                        normalized.append(acc)
                        by_id[acc_id] = acc

            # Fetch securities (depot) accounts and merge.
            securities_payload = None
            if auth_header_value:
                try:
                    securities_payload = fetch_my_securities(context, auth_header_value)
                except Exception:
                    securities_payload = None

            if securities_payload:
                _write_debug_json("my-securities-raw", securities_payload)
                depot_accounts = normalize_depot_accounts_from_securities(securities_payload)
                if depot_accounts:
                    by_id = {str(a.get("id") or ""): a for a in normalized if str(a.get("id") or "").strip()}
                    for acc in depot_accounts:
                        acc_id = str(acc.get("id") or "").strip()
                        if not acc_id:
                            continue
                        if acc_id in by_id:
                            by_id[acc_id].update({k: v for k, v in acc.items() if v is not None})
                        else:
                            normalized.append(acc)
                            by_id[acc_id] = acc

        finally:
            context.close()

    if not normalized:
        if getattr(args, "json", False):
            print(json.dumps({"institution": "george", "fetchedAt": _now_iso_local(), "rawPath": None, "accounts": []}, indent=2))
        else:
            print("[accounts] No accounts found", flush=True)
        return 0

    wrapper = canonicalize_accounts_george(raw_payload, normalized, raw_path=raw_path)

    if getattr(args, "json", False):
        print(json.dumps(wrapper, ensure_ascii=False, indent=2))
        return 0

    print(f"[accounts] {len(wrapper['accounts'])} account(s):", flush=True)
    for acc in wrapper["accounts"]:
        name = acc.get("name") or "N/A"
        iban_short = _short_iban(acc.get("iban"))
        typ = acc.get("type") or "other"

        print(f"- {name} — {iban_short} — id={acc.get('id')} — {typ}", flush=True)

    if wrapper.get("rawPath"):
        print(f"[accounts] raw payload saved: {wrapper['rawPath']}", flush=True)

    return 0



def cmd_balances(args):
    """List all accounts and their balances from the George overview."""
    try:
        user_id = _resolve_user_id(args)
    except Exception as e:
        print(f"[balances] ERROR: {e}")
        return 1

    profile_dir = _get_profile_dir(user_id)
    global USER_ID_OVERRIDE
    USER_ID_OVERRIDE = user_id

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=not args.visible,
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        try:
            if not login(page, timeout_seconds=_login_timeout(args)):
                return 1

            dismiss_modals(page)
            auth_header = capture_bearer_auth_header(context, page, timeout_s=10)
            if not auth_header:
                print("[balances] ERROR: Could not capture API Authorization header", flush=True)
                return 1
            
            # Save token
            tok = _extract_bearer_token(auth_header)
            if tok:
                _save_token_cache(user_id, tok, source="auth_header")

            payload = fetch_my_accounts(context, auth_header)
            accounts = normalize_accounts_from_api(payload)

            def fmt(amount: float | None, cur: str | None) -> str:
                if amount is None:
                    return "N/A"
                cur = (cur or "EUR").strip()
                s = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                return f"{s} {cur}"

            # Try to enrich with balance/disposable fields from raw payload if present.
            # We iterate over raw accounts to preserve any balance data.
            raw_accounts = None
            if isinstance(payload, list):
                raw_accounts = payload
            elif isinstance(payload, dict):
                for key in ("items", "accounts", "data", "content", "accountList"):
                    v = payload.get(key)
                    if isinstance(v, list):
                        raw_accounts = v
                        break
            if raw_accounts is None:
                raw_accounts = []

            print("[balances] Balances (API):", flush=True)
            for idx, acc in enumerate(raw_accounts):
                if not isinstance(acc, dict):
                    continue
                name = _extract_first(acc, ["name", "alias", "productName", "description", "accountLabel", "accountName"]) or "N/A"

                balance, currency = _extract_money_from_account(
                    acc,
                    ["balance", "accountBalance", "amount", "currentBalance", "value"],
                    ["currency", "ccy"],
                )
                disposable, disp_currency = _extract_money_from_account(
                    acc,
                    ["disposable", "disposableAmount", "available", "availableAmount", "disposableBalance"],
                    ["currency", "ccy"],
                )
                if disp_currency is None:
                    disp_currency = currency

                bal_str = fmt(balance, currency)
                disp_str = fmt(disposable, disp_currency)
                print(f"- {name}: {bal_str} (disposable: {disp_str})", flush=True)

            return 0
        finally:
            context.close()


def cmd_statements(args):
    """Download PDF statements for an account."""
    account = get_account(args.account)
    
    # Determine user from account owner or fallback to default/args
    user_id = account.get("owner")
    if not user_id:
        # Fallback to current default resolution
        global CONFIG
        if CONFIG is None: CONFIG = load_config()
        user_id = _resolve_user_id(args, CONFIG)

    profile_dir = _get_profile_dir(user_id)
    global USER_ID_OVERRIDE
    USER_ID_OVERRIDE = user_id

    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR / f"{args.year}-Q{args.quarter}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Statement IDs for Q4 (validated mapping)
    if args.quarter == 4:
        stmt_ids = [11, 12, 13, 14]
    else:
        raise NotImplementedError(f"Q{args.quarter} statement mapping not yet validated")
    
    print(f"[george] Downloading Q{args.quarter}/{args.year} statements for {account['name']} (User: {user_id})")
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=not args.visible,
            accept_downloads=True,
            downloads_path=str(output_dir),
            viewport={"width": 1280, "height": 900},
        )
        context.on("dialog", lambda d: d.accept())
        page = context.new_page()
        
        try:
            if not login(page, timeout_seconds=_login_timeout(args)):
                return 1
            
            dismiss_modals(page)
            files = download_statements_pdf(
                page, account, stmt_ids,
                include_receipts=not args.no_receipts,
                download_dir=output_dir
            )
            
            print(f"\n[george] Downloaded {len(files)} PDF files")
        finally:
            context.close()
    
    return 0


def cmd_export(args):
    """Download data exports (CAMT53/MT940) for all available accounts."""
    try:
        user_id = _resolve_user_id(args)
    except Exception as e:
        print(f"[export] ERROR: {e}")
        return 1
        
    profile_dir = _get_profile_dir(user_id)
    global USER_ID_OVERRIDE
    USER_ID_OVERRIDE = user_id

    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)

    export_type = args.type.lower()
    if export_type not in EXPORT_TYPES:
        print(f"[export] Invalid type '{export_type}'. Supported: {', '.join(EXPORT_TYPES)}")
        return 1

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=not args.visible,
            accept_downloads=True,
            downloads_path=str(output_dir),
            viewport={"width": 1280, "height": 900},
        )
        context.on("dialog", lambda d: d.accept())
        page = context.new_page()

        try:
            if not login(page, timeout_seconds=_login_timeout(args)):
                return 1

            dismiss_modals(page)
            files = download_data_exports(page, export_type, download_dir=output_dir)
            label = EXPORT_TYPE_LABELS[export_type]
            print(f"\n[george] Downloaded {len(files)} {label} export files")
        finally:
            context.close()

    return 0


def cmd_datacarrier_list(args):
    """List data-carrier files and orders (uploaded SEPA/CAMT/MT940)."""
    try:
        user_id = _resolve_user_id(args)
    except Exception as e:
        print(f"[datacarrier-list] ERROR: {e}")
        return 1

    profile_dir = _get_profile_dir(user_id)
    global USER_ID_OVERRIDE
    USER_ID_OVERRIDE = user_id

    state_filter = getattr(args, "state", None)
    if state_filter:
        state_filter = state_filter.upper()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=not args.visible,
            viewport={"width": 1280, "height": 900},
        )
        context.on("dialog", lambda d: d.accept())
        page = context.new_page()

        try:
            if not login(page, timeout_seconds=_login_timeout(args)):
                return 1

            dismiss_modals(page)

            # Intercept API responses from the datacarrier page
            captured_files = []  # datacarrier-files (uploaded XMLs)
            captured_orders = []  # datacarriers (imported orders with sign info)

            def _capture_dc_response(response):
                url = response.url or ""
                if response.status != 200:
                    return
                try:
                    if "/datacarrier-files" in url:
                        body = response.json()
                        items = body.get("datacarrierFiles", []) if isinstance(body, dict) else body
                        if isinstance(items, list):
                            captured_files.extend(items)
                    elif "/datacarriers" in url and "/sign/" not in url and "/settings" not in url:
                        body = response.json()
                        items = body.get("dataCarriers", []) if isinstance(body, dict) else body
                        if isinstance(items, list):
                            captured_orders.extend(items)
                except Exception:
                    pass

            page.on("response", _capture_dc_response)

            # Navigate to the datacarrier upload page (triggers API calls)
            page.goto(DATACARRIER_UPLOAD_URL, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # Allow XHR to complete

            # Apply state filter to orders
            if state_filter:
                captured_orders = [o for o in captured_orders
                                   if isinstance(o, dict) and (o.get("state") or "").upper() == state_filter]

            if args.json:
                output = {
                    "files": captured_files,
                    "orders": captured_orders,
                }
                print(json.dumps(output, indent=2, sort_keys=True, default=str), flush=True)
            else:
                # --- Uploaded files ---
                if captured_files:
                    print(f"\n  {len(captured_files)} uploaded file(s):", flush=True)
                    for f in captured_files:
                        if not isinstance(f, dict):
                            continue
                        name = f.get("name") or f.get("fileName") or "?"
                        state = f.get("state") or "?"
                        fid = f.get("id") or "?"
                        print(f"    {state:<8s}  {name}  ({fid})", flush=True)

                # --- Imported orders ---
                if captured_orders:
                    print(f"\n  {len(captured_orders)} order(s):", flush=True)
                    for o in captured_orders:
                        if not isinstance(o, dict):
                            continue
                        oid = o.get("id") or "?"
                        ident = o.get("identification") or o.get("name") or "?"
                        state = o.get("state") or "?"
                        amt = o.get("sumAmount", {})
                        amount_val = amt.get("value", 0)
                        precision = amt.get("precision", 2)
                        currency = amt.get("currency", "EUR")
                        amount_str = f"{amount_val / (10 ** precision):,.2f} {currency}"
                        date = (o.get("uploadedDate") or o.get("creationDate") or "")[:10]
                        orders_n = o.get("orderCount", "?")
                        flags = o.get("flags", [])
                        signable = "signable" in flags
                        sign_marker = " [SIGNABLE]" if signable else ""
                        print(f"    {state:<8s}  {date}  {ident}  {amount_str}  ({orders_n} order(s)){sign_marker}", flush=True)
                        if signable:
                            print(f"             → datacarrier-sign {oid}", flush=True)
                else:
                    if not captured_files:
                        print("[datacarrier-list] No data-carrier files or orders found.", flush=True)
        finally:
            context.close()

    return 0


def cmd_datacarrier_upload(args):
    """Upload a data-carrier file."""
    try:
        user_id = _resolve_user_id(args)
    except Exception as e:
        print(f"[datacarrier-upload] ERROR: {e}")
        return 1
        
    profile_dir = _get_profile_dir(user_id)
    global USER_ID_OVERRIDE
    USER_ID_OVERRIDE = user_id

    file_path = Path(args.file).expanduser().resolve()
    if not file_path.exists() or not file_path.is_file():
        print(f"[datacarrier-upload] ERROR: File not found: {file_path}", flush=True)
        return 1

    try:
        _validate_upload_file(file_path)
    except ValueError as e:
        print(f"[datacarrier-upload] ERROR: {e}", flush=True)
        return 1

    output_dir = Path(args.output) if args.output else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=not args.visible,
            viewport={"width": 1280, "height": 900},
        )
        context.on("dialog", lambda d: d.accept())
        page = context.new_page()

        try:
            if not login(page, timeout_seconds=_login_timeout(args)):
                return 1

            dismiss_modals(page)
            payload = upload_datacarrier_file(page, file_path, args.type)
            if payload is None:
                return 1

            resp_id = None
            resp_status = None
            if isinstance(payload, dict):
                resp_id = (
                    payload.get("id")
                    or payload.get("fileId")
                    or payload.get("uuid")
                    or payload.get("reference")
                    or payload.get("datacarrierFileId")
                )
                resp_status = payload.get("status") or payload.get("state") or payload.get("result")

            id_part = f" id={resp_id}" if resp_id is not None else ""
            status_part = f" status={resp_status}" if resp_status is not None else ""
            print(f"[datacarrier-upload] Uploaded {file_path.name}{id_part}{status_part}", flush=True)

            if output_dir:
                ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                out_path = output_dir / f"{file_path.name}.datacarrier.{ts}.json"
                with open(out_path, "w") as f:
                    json.dump(payload, f, indent=2, sort_keys=True)
                print(f"[datacarrier-upload] Saved response: {out_path}", flush=True)

            if args.wait_done:
                if resp_id is None:
                    print("[datacarrier-upload] --wait-done requested but upload response has no file id", flush=True)
                else:
                    print(f"[datacarrier-upload] Waiting for file id={resp_id} to reach DONE...", flush=True)
                    last_state = None
                    start = time.time()
                    timeout_s = max(int(getattr(args, "wait_done_timeout", 120) or 0), 0)
                    while True:
                        if timeout_s > 0 and time.time() - start > timeout_s:
                            print(f"[datacarrier-upload] Timed out after {timeout_s}s waiting for DONE", flush=True)
                            break
                        try:
                            resp = context.request.get(_build_datacarrier_files_list_url(), timeout=30000)
                            payload = resp.json()
                        except Exception as e:
                            print(f"[datacarrier-upload] Polling error: {e}", flush=True)
                            time.sleep(3)
                            continue

                        state, _item = _extract_datacarrier_file_state(payload, resp_id)
                        if state and state != last_state:
                            print(f"[datacarrier-upload] State={state}", flush=True)
                            last_state = state
                        if state == "DONE":
                            break
                        time.sleep(3)
        finally:
            context.close()

    return 0


def cmd_datacarrier_sign(args):
    """Sign a data-carrier upload via George API.

    Flow:
    1. Login and navigate to upload page (establishes session + captures Bearer token)
    2. Look up order details and signId from the datacarriers API response
    3. POST to sign API with Bearer token → triggers phone approval
    4. Poll until signing completes or times out
    """
    try:
        user_id = _resolve_user_id(args)
    except Exception as e:
        print(f"[datacarrier-sign] ERROR: {e}")
        return 1

    profile_dir = _get_profile_dir(user_id)
    global USER_ID_OVERRIDE
    USER_ID_OVERRIDE = user_id

    datacarrier_id = _sanitize_id(args.datacarrier_id, "datacarrier_id")
    output_dir = Path(args.output) if args.output else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=not args.visible,
            viewport={"width": 1280, "height": 900},
        )
        context.on("dialog", lambda d: d.accept())
        page = context.new_page()

        try:
            if not login(page, timeout_seconds=_login_timeout(args)):
                return 1

            dismiss_modals(page)

            # Capture Bearer token from API request headers
            bearer_token = [None]
            order_details = {}
            sign_id_from_api = [None]

            def _capture_request(request):
                url = request.url or ""
                if "api.sparkasse" in url and not bearer_token[0]:
                    auth = request.headers.get("authorization", "")
                    if auth.startswith("Bearer "):
                        bearer_token[0] = auth

            def _capture_dc_response(response):
                url = response.url or ""
                if response.status != 200:
                    return
                if "/datacarriers" in url and "/sign/" not in url and "/settings" not in url:
                    try:
                        body = response.json()
                        items = body.get("dataCarriers", []) if isinstance(body, dict) else body
                        if isinstance(items, list):
                            for item in items:
                                if isinstance(item, dict) and item.get("id") == datacarrier_id:
                                    order_details.update(item)
                                    si = item.get("signInfo")
                                    if isinstance(si, dict):
                                        sign_id_from_api[0] = si.get("signId")
                    except Exception:
                        pass

            page.on("request", _capture_request)
            page.on("response", _capture_dc_response)

            # Navigate to upload page to trigger API calls and capture auth
            page.goto(DATACARRIER_UPLOAD_URL, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            token = bearer_token[0]
            if not token:
                print("[datacarrier-sign] ERROR: Could not capture Bearer token from API requests.", flush=True)
                return 1

            # Determine signId: from --sign-id flag, from API response, or from order details
            sign_id = getattr(args, "sign_id", None)
            if not sign_id:
                sign_id = sign_id_from_api[0]
            if not sign_id:
                si = order_details.get("signInfo", {})
                sign_id = si.get("signId") if isinstance(si, dict) else None

            if not sign_id:
                print(f"[datacarrier-sign] ERROR: Could not determine signId for order {datacarrier_id}.", flush=True)
                if order_details:
                    state = order_details.get("state", "?")
                    print(f"[datacarrier-sign] Order state={state}. May already be signed or not in signable state.", flush=True)
                else:
                    print(f"[datacarrier-sign] Order not found in API response.", flush=True)
                return 1

            # Show order info
            ident = order_details.get("identification") or datacarrier_id
            amt = order_details.get("sumAmount", {})
            amount_val = amt.get("value", 0) / (10 ** amt.get("precision", 2))
            currency = amt.get("currency", "EUR")
            print(f"[datacarrier-sign] Order {ident}: {amount_val:.2f} {currency}, signId={sign_id[:16]}...", flush=True)

            # POST to sign API with Bearer token via page.evaluate(fetch)
            sign_url = DATACARRIER_SIGN_API_TEMPLATE.format(datacarrier_id=datacarrier_id) + sign_id
            result = page.evaluate("""async ([url, token]) => {
                try {
                    const resp = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': token
                        },
                        body: JSON.stringify({authorizationType: 'GEORGE_TOKEN'})
                    });
                    const text = await resp.text();
                    let body = null;
                    try { body = JSON.parse(text); } catch(e) { body = text; }
                    return {status: resp.status, body: body};
                } catch(e) {
                    return {error: e.message};
                }
            }""", [sign_url, token])

            if isinstance(result, dict) and result.get("error"):
                print(f"[datacarrier-sign] ERROR: Sign request failed: {result['error']}", flush=True)
                return 1

            status_code = result.get("status", 0) if isinstance(result, dict) else 0
            body = result.get("body", {}) if isinstance(result, dict) else {}

            if status_code != 200:
                print(f"[datacarrier-sign] ERROR: Sign API returned HTTP {status_code}", flush=True)
                if isinstance(body, dict):
                    errors = body.get("errors", [])
                    for e in errors:
                        print(f"  {e.get('error', '')}: {e.get('message', '')}", flush=True)
                return 1

            # Extract signing state and poll info
            sign_info = body.get("signInfo", {}) if isinstance(body, dict) else {}
            state = sign_info.get("state") or body.get("state") or "?"
            auth_req_id = body.get("authorizationRequestId") or "?"
            poll_info = body.get("poll", {}) if isinstance(body, dict) else {}
            poll_url = poll_info.get("url")
            poll_interval = poll_info.get("interval", 3000)

            print(f"[datacarrier-sign] Signing initiated: state={state} authReqId={auth_req_id}", flush=True)
            print(f"[datacarrier-sign] Approve on your phone now!", flush=True)

            if output_dir:
                ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                out_path = output_dir / f"datacarrier-sign.{datacarrier_id}.{ts}.json"
                with open(out_path, "w") as f:
                    json.dump(body, f, indent=2, sort_keys=True)
                print(f"[datacarrier-sign] Saved response: {out_path}", flush=True)

            # Poll for completion
            if poll_url and args.timeout and args.timeout > 0:
                interval_s = max(poll_interval / 1000.0, 1.0)
                start = time.time()
                last_state = state

                while time.time() - start < args.timeout:
                    time.sleep(interval_s)
                    try:
                        poll_result = page.evaluate("""async ([url, token]) => {
                            try {
                                const resp = await fetch(url, {
                                    headers: {'Authorization': token}
                                });
                                const text = await resp.text();
                                let body = null;
                                try { body = JSON.parse(text); } catch(e) { body = text; }
                                return {status: resp.status, body: body};
                            } catch(e) {
                                return {error: e.message};
                            }
                        }""", [poll_url, token])

                        if isinstance(poll_result, dict) and not poll_result.get("error"):
                            poll_body = poll_result.get("body", {})
                            if isinstance(poll_body, dict):
                                new_state = poll_body.get("state") or poll_body.get("status")
                                if new_state and new_state != last_state:
                                    print(f"[datacarrier-sign] state={new_state}", flush=True)
                                    last_state = new_state
                                if new_state and new_state not in ("PROCESSING", "PENDING", "OPEN"):
                                    if new_state in ("DONE", "COMPLETED", "SIGNED"):
                                        print(f"[datacarrier-sign] SUCCESS: Signing completed.", flush=True)
                                    else:
                                        print(f"[datacarrier-sign] Final state: {new_state}", flush=True)
                                    break
                    except Exception as e:
                        # Page might have navigated; ignore poll errors
                        pass
                else:
                    print(f"[datacarrier-sign] Timed out after {args.timeout}s waiting for approval.", flush=True)
            elif not poll_url:
                print(f"[datacarrier-sign] No poll URL returned. Check George app for status.", flush=True)

        finally:
            context.close()

    return 0



def _george_transactions_export_fields() -> str:
    # Keep this list stable; it controls what the export endpoint returns.
    # (Taken from DevTools capture.)
    return (
        "booking,receiver,amount,currency,reference,referenceNumber,note,favorite,valuation,"
        "virtualCardNumber,virtualCardDevice,virtualCardMobilePaymentApplicationName,receiverReference,"
        "sepaMandateId,sepaCreditorId,ownerAccountTitle,ownerAccountNumber,vopResult,vopMatchedName"
    )


def fetch_transactions_export(context, access_token: str, account_id: str, date_from: str, date_to: str):
    """Fetch transactions export (JSON) for a George account.

    Endpoint requires:
    - Authorization: Bearer <token>
    - Content-Type: application/x-www-form-urlencoded
    - body: id=<ACCOUNT_ID>
    - query: from=YYYY-MM-DD&to=YYYY-MM-DD&sort=BOOKING_DATE_ASC&fields=...
    """
    fields = _george_transactions_export_fields()
    url = (
        "https://api.sparkasse.at/proxy/g/api/my/transactions/export.json"
        f"?lang=en&fields={fields.replace(',', '%2C')}"
        f"&sort=BOOKING_DATE_ASC&from={date_from}&to={date_to}"
        "&continuousCardIdFiltering=false"
    )

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    body = f"id={account_id}"

    try:
        resp = context.request.post(url, headers=headers, data=body, timeout=60000)
    except Exception as e:
        raise RuntimeError(f"[transactions] API request failed: {e}") from e

    if not resp or not resp.ok:
        status = resp.status if resp else "N/A"
        txt = None
        try:
            txt = resp.text()
        except Exception:
            txt = None
        raise RuntimeError(f"[transactions] API request failed (status={status}): {txt or '<no body>'}")

    try:
        return resp.json()
    except Exception:
        # last resort: keep raw text
        return {"raw": resp.text()}


def _date_to_yyyymmdd(s: str) -> str:
    return datetime.strptime(s, "%Y-%m-%d").strftime("%Y%m%d")


def fetch_securities_orders(context, access_token: str, account_id: str, date_from: str, date_to: str) -> list[dict]:
    """Fetch securities orders (finished) for a depot account."""
    base_url = "https://api.sparkasse.at/sec-trading/rest/securities/orders"
    headers = {
        "Accept": "application/vnd.at.sitsolutions.services.sec.trading.representation.orderbook.page.v2+json",
        "Accept-Language": "en",
        "Authorization": f"Bearer {access_token}",
    }
    from_s = _date_to_yyyymmdd(date_from)
    to_s = _date_to_yyyymmdd(date_to)

    page = 0
    size = 100
    all_items: list[dict] = []

    while True:
        url = (
            f"{base_url}?statusGroup=finished&size={size}&page={page}"
            f"&securitiesAccountId={account_id}&from={from_s}&to={to_s}"
        )
        try:
            resp = context.request.get(url, headers=headers, timeout=60000)
        except Exception as e:
            raise RuntimeError(f"[securities-orders] API request failed: {e}") from e

        if not resp or not resp.ok:
            status = resp.status if resp else "N/A"
            raise RuntimeError(f"[securities-orders] API request failed (status={status})")

        payload = resp.json()
        orders = []
        if isinstance(payload, dict):
            for key in ("securityOrders", "orders", "items", "content", "data"):
                v = payload.get(key)
                if isinstance(v, list):
                    orders = [x for x in v if isinstance(x, dict)]
                    break
        elif isinstance(payload, list):
            orders = [x for x in payload if isinstance(x, dict)]

        all_items.extend(orders)

        page_count = payload.get("pageCount") if isinstance(payload, dict) else None
        if isinstance(page_count, int) and page + 1 >= page_count:
            break
        if len(orders) < size:
            break
        page += 1

    return all_items


def _canonicalize_depot_order(order: dict) -> dict:
    out: dict = {}

    order_id = order.get("id") or order.get("orderNumber")
    if order_id is not None:
        out["id"] = str(order_id)

    submission = order.get("submissionDate")
    if isinstance(submission, str) and submission.strip():
        out["timestamp"] = submission
        if len(submission) >= 10:
            out["bookingDate"] = submission[:10]

    out["kind"] = "trade"

    action = order.get("type")
    if isinstance(action, str) and action.strip():
        action = action.strip().upper()
        out["action"] = action

    amount_amt, amount_ccy = _extract_money(order.get("amount"))
    if amount_amt is not None and amount_ccy:
        signed = amount_amt
        if action == "BUY":
            signed = -abs(amount_amt)
        elif action == "SELL":
            signed = abs(amount_amt)
        out["amount"] = {"amount": signed, "currency": amount_ccy}

    sec = order.get("security") if isinstance(order.get("security"), dict) else None
    isin = None
    name = None
    if sec:
        isin = sec.get("isin")
        name = sec.get("fullTitle") or sec.get("title")
    if isinstance(isin, str) and isin.strip():
        out["isin"] = isin.strip()
    if isinstance(isin, str) or isinstance(name, str):
        sec_obj: dict = {}
        if isinstance(isin, str) and isin.strip():
            sec_obj["isin"] = isin.strip()
        if isinstance(name, str) and name.strip():
            sec_obj["name"] = name.strip()
        if sec_obj:
            out["security"] = sec_obj

    qty = order.get("executedQuantity")
    if qty is None:
        qty = order.get("quantity")
    if isinstance(qty, (int, float)):
        out["quantity"] = qty
        out["unit"] = "STK"

    if amount_amt is not None and amount_ccy and isinstance(qty, (int, float)) and qty:
        out["price"] = {"amount": abs(amount_amt) / float(qty), "currency": amount_ccy}

    venue = None
    stock = order.get("stockExchange") if isinstance(order.get("stockExchange"), dict) else None
    if stock and isinstance(stock.get("name"), str):
        venue = stock.get("name").strip()
    if venue:
        out["venue"] = venue

    desc_bits = []
    if action and isinstance(qty, (int, float)) and name:
        desc_bits.append(f"{action} {qty} {name}")
    elif name:
        desc_bits.append(str(name))
    if isinstance(isin, str) and isin.strip():
        desc_bits.append(isin.strip())
    if isinstance(order.get("orderType"), str) and order.get("orderType").strip():
        desc_bits.append(order.get("orderType").strip())
    if venue:
        desc_bits.append(venue)
    if order.get("orderNumber"):
        desc_bits.append(f"order {order.get('orderNumber')}")
    if desc_bits:
        out["description"] = " · ".join(desc_bits)

    return out


def _canonicalize_portfolio(securities_account: dict) -> dict:
    account_id = str(securities_account.get("id") or "")
    account_iban = None
    settlement = securities_account.get("settlementAccount")
    if isinstance(settlement, dict):
        iban = settlement.get("iban")
        if isinstance(iban, str) and iban.strip():
            account_iban = iban.strip()
    if not account_iban:
        accountno = securities_account.get("accountno") or securities_account.get("accountNo") or securities_account.get("accountNumber")
        if isinstance(accountno, (str, int)):
            account_iban = str(accountno)

    positions: list[dict] = []
    titles = _collect_titles_from_securities_account(securities_account)
    for title in titles:
        name = title.get("title") or title.get("fullTitle")
        isin = title.get("isin")

        qty = title.get("numberOfShares")
        if qty is None:
            qty = 0.0
            for pos in title.get("positions") or []:
                if isinstance(pos, dict) and isinstance(pos.get("numberOfShares"), (int, float)):
                    qty += float(pos.get("numberOfShares"))
        if isinstance(qty, (int, float)) and qty == 0:
            qty = None

        price_obj = None
        positions_list = title.get("positions") if isinstance(title.get("positions"), list) else []
        if positions_list:
            last_price = positions_list[0].get("lastPrice") if isinstance(positions_list[0], dict) else None
            lp_amt, lp_ccy = _extract_money(last_price)
            if lp_amt is not None and lp_ccy:
                price_obj = {"amount": lp_amt, "currency": lp_ccy}

        mv_amt, mv_ccy = _extract_money(title.get("marketValue"))
        perf_amt, perf_ccy = _extract_money(title.get("performance"))
        perf_pct = title.get("performancePercent")
        if perf_pct is None:
            perf_pct = title.get("performancePercentInclFees") or title.get("performancePercentExclFees")

        pos: dict = {}
        if isinstance(isin, str) and isin.strip():
            pos["isin"] = isin.strip()
        if isinstance(name, str) and name.strip():
            pos["name"] = name.strip()
        if isinstance(qty, (int, float)):
            pos["quantity"] = qty
        if price_obj:
            pos["price"] = price_obj
        if mv_amt is not None and mv_ccy:
            pos["marketValue"] = {"amount": mv_amt, "currency": mv_ccy}
        if perf_amt is not None and perf_ccy:
            # Canonical schema expected by Banker: performance.absolute + performance.percent
            perf_obj = {"absolute": {"amount": perf_amt, "currency": perf_ccy}}
            if isinstance(perf_pct, (int, float)):
                perf_obj["percent"] = float(perf_pct)
            pos["performance"] = perf_obj

        if pos:
            positions.append(pos)

    return {
        "institution": "george",
        "kind": "portfolio",
        "account": {"id": account_id, "iban": account_iban},
        "fetchedAt": _now_iso_local(),
        "positions": positions,
    }


def _canonicalize_george_transaction(tx: dict) -> dict:
    """Best-effort mapping from George export.json to our canonical schema.

    Observed shape (from DevTools):
    - booking: "2026-01-02T00:00:00.000+0100"
    - valuation: "2026-01-02T00:00:00.000+0100"
    - partnerName, partnerAccount.{iban,bic}
    - amount.{value,precision,currency}
    - reference, referenceNumber, receiverReference
    - sepaMandateId, sepaCreditorId

    We keep bank-native payload separately in wrapper["raw"] when --debug.
    """

    out: dict = {}

    # status (export is booked history)
    out["status"] = "booked"

    # dates
    booking = tx.get("booking")
    if booking is None:
        booking = tx.get("bookingDate") # Paged API
    
    if isinstance(booking, str) and len(booking) >= 10:
        out["bookingDate"] = booking[:10]
    elif isinstance(booking, (int, float)):
        # Timestamp in ms
        try:
            out["bookingDate"] = datetime.fromtimestamp(booking / 1000.0).strftime("%Y-%m-%d")
        except Exception:
            pass

    valuation = tx.get("valuation") or tx.get("valueDate")
    if valuation is None:
        valuation = tx.get("valuationDate") # Paged API

    if isinstance(valuation, str) and len(valuation) >= 10:
        out["valueDate"] = valuation[:10]
    elif isinstance(valuation, (int, float)):
        try:
            out["valueDate"] = datetime.fromtimestamp(valuation / 1000.0).strftime("%Y-%m-%d")
        except Exception:
            pass

    # amount
    amount_obj = tx.get("amount")
    if isinstance(amount_obj, dict):
        v = amount_obj.get("value")
        prec = amount_obj.get("precision")
        cur = amount_obj.get("currency")
        if isinstance(v, (int, float)) and isinstance(prec, int) and isinstance(cur, str) and cur:
            out["amount"] = {"amount": float(v) / (10 ** prec), "currency": cur}

    # counterparty
    cp_name = tx.get("partnerName") or tx.get("receiver") or tx.get("receiverName")
    
    # Paged API often has 'sender'/'receiver' objects.
    # Determine which is the counterparty based on account ownership or direction?
    # Actually, paged API often has 'partnerName', 'partner' object.
    # In the example: partnerName is null, but senderName/receiverName exist.
    # And there is a 'partner' object.
    
    if not cp_name:
        # Paged API fallback
        p = tx.get("partner")
        if isinstance(p, dict):
            # partner object might be empty or have fields
            pass
        # Try sender/receiver names if partnerName is missing
        # We don't know "our" account ID easily here without context, but usually
        # export.json provides 'partnerName'.
        # Paged API has 'orderRole' (SENDER/RECEIVER). 
        # If orderRole == SENDER, we are sender -> partner is receiver.
        # If orderRole == RECEIVER, we are receiver -> partner is sender.
        role = tx.get("orderRole")
        if role == "SENDER":
            cp_name = tx.get("receiverName")
        elif role == "RECEIVER":
            cp_name = tx.get("senderName")

    partner_account = tx.get("partnerAccount") 
    if partner_account is None:
        # Paged API has 'partner' object with iban/bic
        partner_account = tx.get("partner")

    cp: dict = {}
    if isinstance(cp_name, str) and cp_name.strip():
        cp["name"] = cp_name.strip()
    if isinstance(partner_account, dict):
        iban = partner_account.get("iban")
        bic = partner_account.get("bic")
        if isinstance(iban, str) and iban.strip():
            cp["iban"] = iban.strip()
        if isinstance(bic, str) and bic.strip():
            cp["bic"] = bic.strip()
    if cp:
        out["counterparty"] = cp

    # description/purpose
    ref = tx.get("reference")
    note = tx.get("note")
    if isinstance(ref, str) and ref.strip():
        out["description"] = ref.strip()
    if isinstance(note, str) and note.strip():
        out["purpose"] = note.strip()

    # references
    refs: dict = {}
    rn = tx.get("referenceNumber")
    if isinstance(rn, str) and rn.strip():
        refs["bankReference"] = rn.strip()

    receiver_ref = tx.get("receiverReference")
    if isinstance(receiver_ref, str) and receiver_ref.strip():
        refs["paymentReference"] = receiver_ref.strip()

    mandate = tx.get("sepaMandateId")
    if isinstance(mandate, str) and mandate.strip():
        refs["mandateId"] = mandate.strip()

    creditor = tx.get("sepaCreditorId")
    if isinstance(creditor, str) and creditor.strip():
        refs["creditorId"] = creditor.strip()

    e2e = tx.get("e2eReference")
    if isinstance(e2e, str) and e2e.strip():
        refs["endToEndId"] = e2e.strip()

    if refs:
        out["references"] = refs

    # stable id (rarely present in export)
    tid = tx.get("transactionId") or tx.get("containedTransactionId")
    if tid is not None:
        out["id"] = str(tid)

    return out


def fetch_transactions_paged(context, access_token: str, account_id: str, date_from: str, date_to: str) -> list[dict]:
    """Fetch transactions via paged API (for older history)."""
    base_url = "https://api.sparkasse.at/proxy/g/api/my/transactions"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en",
        "Authorization": f"Bearer {access_token}",
        "x-request-id": str(uuid.uuid4()),
        "Priority": "u=3, i",
    }
    
    all_items = []
    page = 0
    page_size = 50
    
    print(f"[paged-fetch] Starting fetch for {account_id} ({date_from} to {date_to})...", flush=True)
    
    while True:
        params = {
            "continuousCardIdFiltering": "false",
            "from": date_from,
            "to": date_to,
            "id": account_id,
            "includeContainedTransactions": "true",
            "page": str(page),
            "pageSize": str(page_size),
            "sum": "true",
            "sumWithRoundup": "true",
            "count": "true",
            "balance": "false",
            "includeProducts": "false"
        }
        
        url_params = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{base_url}?{url_params}"
        
        print(f"[paged-fetch] DEBUG URL: {url}", flush=True)

        try:
            resp = context.request.get(url, headers=headers, timeout=60000)
        except Exception as e:
            raise RuntimeError(f"[paged-fetch] Request failed (page {page}): {e}") from e
            
        if not resp.ok:
            raise RuntimeError(f"[paged-fetch] API error {resp.status} on page {page}")
            
        data = resp.json()
        collection = data.get("collection", [])
        
        if not collection:
            break
            
        all_items.extend(collection)
        print(f"[paged-fetch] Page {page}: fetched {len(collection)} items (total {len(all_items)})", flush=True)
        
        if len(collection) < page_size:
            break
            
        page += 1
        time.sleep(0.2) # be nice
        
    return all_items


def cmd_portfolio(args):
    """Fetch portfolio holdings for a depot account."""
    try:
        account_id = _sanitize_id(str(args.account or ""), "account id")
    except Exception as e:
        print(f"[portfolio] ERROR: Invalid --account: {e}")
        return 1

    try:
        user_id = _resolve_user_id(args)
    except Exception as e:
        print(f"[portfolio] ERROR: {e}")
        return 1

    profile_dir = _get_profile_dir(user_id)
    global USER_ID_OVERRIDE
    USER_ID_OVERRIDE = user_id

    raw_payload = None
    auth_header_value: str | None = None

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=not args.visible,
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()
        try:
            token_cache = _load_token_cache(user_id) or {}
            token = token_cache.get("accessToken") if isinstance(token_cache, dict) else None
            if isinstance(token, str) and token.strip():
                try:
                    auth_header_value = f"Bearer {token.strip()}"
                    raw_payload = fetch_my_securities_account(context, auth_header_value, account_id)
                except Exception:
                    raw_payload = None
                    auth_header_value = None

            if raw_payload is None:
                if not login(page, timeout_seconds=_login_timeout(args)):
                    return 1
                dismiss_modals(page)

                auth_header = capture_bearer_auth_header(context, page, timeout_s=10)
                if not auth_header:
                    print("[portfolio] ERROR: Could not capture API Authorization header", flush=True)
                    return 1

                auth_header_value = auth_header
                raw_payload = fetch_my_securities_account(context, auth_header_value, account_id)
                tok = _extract_bearer_token(auth_header_value)
                if tok:
                    _save_token_cache(user_id, tok, source="auth_header")

            raw_path = _write_debug_json(f"securities-account-raw-{account_id}", raw_payload)

            wrapper = _canonicalize_portfolio(raw_payload if isinstance(raw_payload, dict) else {})
            if DEBUG_ENABLED:
                if raw_path:
                    wrapper["rawPath"] = str(raw_path)
                wrapper["raw"] = raw_payload

            if getattr(args, "json", False):
                print(json.dumps(wrapper, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(wrapper, ensure_ascii=False, separators=(",", ":")))

            return 0
        finally:
            context.close()


def cmd_transactions(args):
    """Download transactions for an account id (API-based).

    No local account config/cache is used. Pass the George internal account id via --account.
    """
    try:
        account_id = _sanitize_id(str(args.account or ""), "account id")
    except Exception as e:
        print(f"[transactions] ERROR: Invalid --account: {e}")
        return 1

    # User selection:
    # - --user-id overrides everything
    # - otherwise GEORGE_USER_ID from env
    try:
        user_id = _resolve_user_id(args)
    except Exception as e:
        print(f"[transactions] ERROR: {e}")
        return 1

    profile_dir = _get_profile_dir(user_id)
    global USER_ID_OVERRIDE
    USER_ID_OVERRIDE = user_id

    # Minimal account descriptor for output
    account = {"id": account_id, "iban": None, "name": account_id, "type": "unknown"}

    fmt = args.format.lower()
    if fmt not in TRANSACTION_EXPORT_FORMATS:
        print(f"[transactions] Invalid format '{fmt}'. Supported: {', '.join(TRANSACTION_EXPORT_FORMATS)}")
        return 1
    
    method = getattr(args, "method", "export") # export (default) or paging

    # Validate ISO dates
    from datetime import datetime
    try:
        datetime.strptime(args.date_from, "%Y-%m-%d")
        datetime.strptime(args.date_until, "%Y-%m-%d")
    except ValueError:
        print("ERROR: Dates must be in YYYY-MM-DD format.")
        return 1

    date_from = args.date_from
    date_until = args.date_until

    # Resolve output base
    output_target = args.output
    out_base: Path
    if output_target:
        p = Path(output_target)
        if p.is_dir() or str(output_target).endswith(os.sep):
            p.mkdir(parents=True, exist_ok=True)
            acct = _safe_filename_component(account.get("iban") or account.get("id") or "account", default="account")
            out_base = p / f"transactions_{acct}_{date_from}_{date_until}"
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            out_base = p
    else:
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        acct = _safe_filename_component(account.get("iban") or account.get("id") or "account", default="account")
        out_base = DEFAULT_OUTPUT_DIR / f"transactions_{acct}_{date_from}_{date_until}"

    print(f"[george] Fetching {fmt.upper()} for {account.get('name')} ({date_from} -> {date_until}) (User: {user_id}, Method: {method})", flush=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=not args.visible,
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()
        try:
            # Token reuse -> avoid interactive login when possible
            token_cache = _load_token_cache(user_id) or {}
            token = token_cache.get("accessToken") if isinstance(token_cache, dict) else None
            raw_payload = None
            depot_account = None
            is_depot = False

            def _do_fetch(t):
                if method == "paging":
                    return fetch_transactions_paged(
                        context,
                        t,
                        str(account.get("id") or ""),
                        date_from,
                        date_until,
                    )
                else:
                    return fetch_transactions_export(
                        context,
                        t,
                        str(account.get("id") or ""),
                        date_from,
                        date_until,
                    )

            if isinstance(token, str) and token.strip():
                token = token.strip()
                try:
                    securities_payload = fetch_my_securities(context, f"Bearer {token}")
                    depot_account = _find_securities_account(securities_payload, account_id)
                except Exception:
                    depot_account = None

                if depot_account:
                    is_depot = True
                    try:
                        raw_payload = fetch_securities_orders(context, token, account_id, date_from, date_until)
                    except Exception:
                        raw_payload = None

                if raw_payload is None and not is_depot:
                    try:
                        raw_payload = _do_fetch(token)
                    except Exception:
                        raw_payload = None

            if raw_payload is None:
                if not login(page, timeout_seconds=_login_timeout(args)):
                    return 1
                dismiss_modals(page)

                auth_header = capture_bearer_auth_header(context, page, timeout_s=10)
                if not auth_header:
                    print("[transactions] ERROR: Could not capture API Authorization header", flush=True)
                    return 1

                tok = _extract_bearer_token(auth_header)
                if not tok:
                    print("[transactions] ERROR: Could not extract bearer token", flush=True)
                    return 1

                _save_token_cache(user_id, tok, source="auth_header")
                is_depot = False
                try:
                    securities_payload = fetch_my_securities(context, f"Bearer {tok}")
                    depot_account = _find_securities_account(securities_payload, account_id)
                except Exception:
                    depot_account = None

                if depot_account:
                    is_depot = True
                    raw_payload = fetch_securities_orders(context, tok, account_id, date_from, date_until)
                else:
                    raw_payload = _do_fetch(tok)

            # Debug raw
            raw_path = _write_debug_json(
                f"transactions-raw-{(account.get('id') or 'account')}-{date_from}-{date_until}",
                raw_payload,
            )

            # Update account info for depots
            if depot_account:
                account["type"] = "depot"
                account["name"] = depot_account.get("description") or depot_account.get("productI18N") or account_id
                settlement = depot_account.get("settlementAccount") if isinstance(depot_account.get("settlementAccount"), dict) else None
                if settlement and isinstance(settlement.get("iban"), str) and settlement.get("iban").strip():
                    account["iban"] = settlement.get("iban").strip()
                else:
                    accountno = depot_account.get("accountno") or depot_account.get("accountNo") or depot_account.get("accountNumber")
                    if isinstance(accountno, (str, int)):
                        account["iban"] = str(accountno)

            # Canonical wrapper
            raw_list = raw_payload if isinstance(raw_payload, list) else []
            is_creditcard = "creditcard" in str(account.get("type") or "").lower()

            canonical: list[dict] = []
            for tx in raw_list:
                if not isinstance(tx, dict):
                    continue
                if is_depot:
                    c = _canonicalize_depot_order(tx)
                else:
                    c = _canonicalize_george_transaction(tx)

                # Credit cards: keep default output lean; only include raw per-item payload when --debug.
                if DEBUG_ENABLED and is_creditcard:
                    c["raw"] = tx

                canonical.append(c)

            wrapper = {
                "institution": "george",
                "account": {"id": str(account.get("id") or ""), "iban": account.get("iban")},
                "range": {"from": date_from, "until": date_until},
                "fetchedAt": _now_iso_local(),
                "transactions": canonical,
            }
            if DEBUG_ENABLED:
                # Always write the bank-native payload to the debug folder (rawPath).
                # For credit cards, keep the wrapper lean and rely on per-item raw + rawPath.
                if raw_path:
                    wrapper["rawPath"] = str(raw_path)
                if not is_creditcard:
                    wrapper["raw"] = raw_payload

            if fmt == "json":
                out_file = out_base.with_suffix(".json")
                out_file.write_text(json.dumps(wrapper, ensure_ascii=False, indent=2))
                print(f"[transactions] Saved JSON: {out_file}", flush=True)
            else:
                # Simple CSV from canonical rows
                import csv

                out_file = out_base.with_suffix(".csv")
                out_file.parent.mkdir(parents=True, exist_ok=True)
                fieldnames = [
                    "bookingDate",
                    "amount",
                    "currency",
                    "counterparty",
                    "description",
                    "purpose",
                    "bankReference",
                ]
                with out_file.open("w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=fieldnames)
                    w.writeheader()
                    for tx in canonical:
                        amt = (tx.get("amount") or {}) if isinstance(tx.get("amount"), dict) else {}
                        cp = (tx.get("counterparty") or {}) if isinstance(tx.get("counterparty"), dict) else {}
                        refs = (tx.get("references") or {}) if isinstance(tx.get("references"), dict) else {}
                        w.writerow(
                            {
                                "bookingDate": tx.get("bookingDate"),
                                "amount": amt.get("amount"),
                                "currency": amt.get("currency"),
                                "counterparty": cp.get("name"),
                                "description": tx.get("description"),
                                "purpose": tx.get("purpose"),
                                "bankReference": refs.get("bankReference"),
                            }
                        )
                print(f"[transactions] Saved CSV: {out_file}", flush=True)

            return 0
        finally:
            context.close()



def main():
    parser = argparse.ArgumentParser(
        description="George Banking Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  george.py login                                # Login only
  george.py accounts                             # List accounts
  george.py transactions --account <ACCOUNT_ID> --from 2024-01-01 --until 2024-01-31 [--method paging]
        """
    )
    
    # Global options
    parser.add_argument("--visible", action="store_true", help="Show browser window")
    # State dir is always workspace/george (no override).
    parser.add_argument("--login-timeout", type=int, default=DEFAULT_LOGIN_TIMEOUT, help="Seconds to wait for phone approval")
    parser.add_argument("--user-id", default=None, help="Override George user number/username (or set GEORGE_USER_ID)")
    parser.add_argument("--debug", action="store_true", help="Save bank-native payloads to <stateDir>/debug (default: off)")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    login_parser = subparsers.add_parser("login", help="Perform login only")
    login_parser.set_defaults(func=cmd_login)

    logout_parser = subparsers.add_parser("logout", help="Clear session/profile")
    logout_parser.set_defaults(func=cmd_logout)

    acc_parser = subparsers.add_parser("accounts", help="List available accounts (live)")
    acc_parser.add_argument("--json", action="store_true", help="Output canonical JSON")
    acc_parser.set_defaults(func=cmd_accounts)

    portfolio_parser = subparsers.add_parser("portfolio", help="Fetch depot portfolio holdings")
    portfolio_parser.add_argument("--account", required=True, help="Depot account id")
    portfolio_parser.add_argument("--json", action="store_true", help="Pretty JSON output (default: compact)")
    portfolio_parser.set_defaults(func=cmd_portfolio)

    transactions_parser = subparsers.add_parser("transactions", help="Download transactions")
    transactions_parser.add_argument("--account", required=True, help="Account id (use 'accounts' to list)")
    transactions_parser.add_argument("--format", default="json", choices=["csv", "json"], help="Output format (default: json)")
    transactions_parser.add_argument("--method", default="export", choices=["export", "paging"], help="Fetch method (default: export)")
    transactions_parser.add_argument("--out", dest="output", help="Output file base or directory")
    transactions_parser.add_argument("--from", dest="date_from", required=True, help="Start date (YYYY-MM-DD)")
    transactions_parser.add_argument("--until", dest="date_until", required=True, help="End date (YYYY-MM-DD)")
    transactions_parser.set_defaults(func=cmd_transactions)

    dc_list_parser = subparsers.add_parser("datacarrier-list", help="List uploaded data-carrier files and orders")
    dc_list_parser.add_argument("--json", action="store_true", help="Full JSON output")
    dc_list_parser.add_argument("--state", default=None, help="Filter orders by state (e.g. OPEN, CLOSED)")
    dc_list_parser.set_defaults(func=cmd_datacarrier_list)

    dc_upload_parser = subparsers.add_parser("datacarrier-upload", help="Upload a data-carrier file (SEPA XML, CAMT, MT940)")
    dc_upload_parser.add_argument("file", help="Path to the file to upload")
    dc_upload_parser.add_argument("--type", default=None, help="Override file type hint (e.g. pain.001, camt.053)")
    dc_upload_parser.add_argument("--out", dest="output", default=None, help="Directory to save the upload response JSON")
    dc_upload_parser.add_argument("--wait-done", action="store_true", default=False, help="Poll until file reaches DONE state")
    dc_upload_parser.add_argument("--wait-done-timeout", type=int, default=120, help="Timeout in seconds for --wait-done (default: 120)")
    dc_upload_parser.set_defaults(func=cmd_datacarrier_upload)

    dc_sign_parser = subparsers.add_parser("datacarrier-sign", help="Sign a data-carrier upload")
    dc_sign_parser.add_argument("datacarrier_id", help="Data-carrier file id to sign")
    dc_sign_parser.add_argument("--sign-id", default=None, help="Skip UI discovery and use this signId directly")
    dc_sign_parser.add_argument("--out", dest="output", default=None, help="Directory to save the signing response JSON")
    dc_sign_parser.add_argument("--timeout", type=int, default=120, help="Seconds to wait for phone approval (default: 120)")
    dc_sign_parser.set_defaults(func=cmd_datacarrier_sign)

    args = parser.parse_args()
    _apply_state_dir()

    global DEBUG_ENABLED
    DEBUG_ENABLED = bool(getattr(args, "debug", False))

    global USER_ID_OVERRIDE
    USER_ID_OVERRIDE = getattr(args, "user_id", None)

    return args.func(args)

if __name__ == "__main__":
    sys.exit(main() or 0)
