#!/usr/bin/env python3
"""
Raiffeisen ELBA Banking Automation

Automates login and basic data retrieval for Raiffeisen ELBA (Austria).
"""

import sys
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
import os
import time
import re
import argparse
from datetime import datetime
import json
import subprocess
from pathlib import Path
import requests

# Try importing playwright
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("ERROR: playwright not installed. Run: pip3 install playwright && playwright install chromium")
    sys.exit(1)

# --- Configuration ---
DEFAULT_LOGIN_TIMEOUT = 300  # seconds (standard: 5 minutes)
LOGIN_TIMEOUT = DEFAULT_LOGIN_TIMEOUT

BASE_DIR = Path(__file__).parent.parent


def _find_workspace_root() -> Path:
    """Find the workspace root (directory containing 'skills/')."""
    env = os.environ.get("OPENCLAW_WORKSPACE")
    if env:
        return Path(env).resolve()

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
    return cwd


def _set_strict_umask() -> None:
    """Best-effort hardening: ensure new files/dirs are private by default."""
    try:
        os.umask(0o077)
    except Exception:
        pass


def _harden_path(p: Path) -> None:
    """Best-effort: set restrictive permissions on a path."""
    try:
        if p.is_dir():
            os.chmod(p, 0o700)
        elif p.is_file() and not p.is_symlink():
            os.chmod(p, 0o600)
    except Exception:
        pass


def _safe_filename_component(value: str, default: str = "value") -> str:
    """Sanitize a user-controlled string for safe use in filenames."""
    s = str(value or "").strip()
    if not s:
        return default
    s = s.replace("/", "_").replace("\\", "_")
    s = re.sub(r'\.\.+', '.', s)
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    s = s.strip("._-")
    return (s or default)[:80]


def _safe_download_filename(suggested: str) -> str:
    """Sanitize a Playwright suggested_filename against path traversal."""
    name = Path(suggested).name  # strip any directory components
    name = name.replace("\x00", "")
    if not name or name in (".", ".."):
        name = "download"
    return _safe_filename_component(name, default="download")


def _safe_output_path(raw: str, workspace: Path) -> Path:
    """Validate that an output path is within the workspace or /tmp."""
    p = Path(raw).expanduser().resolve()
    tmp = Path("/tmp").resolve()
    if p == workspace or p.is_relative_to(workspace):
        return p
    if p == tmp or p.is_relative_to(tmp):
        return p
    raise ValueError(
        f"Output path '{raw}' is outside the workspace and /tmp. "
        f"Allowed: {workspace} or /tmp"
    )


_set_strict_umask()

WORKSPACE_ROOT = _find_workspace_root()
CONFIG_DIR = WORKSPACE_ROOT / "raiffeisen-elba"
CONFIG_FILE = CONFIG_DIR / "config.json"
STATE_ROOT = WORKSPACE_ROOT / "raiffeisen-elba"
PROFILE_DIR = STATE_ROOT / ".pw-profile"
SESSION_URL_FILE = PROFILE_DIR / "last_url.txt"
TOKEN_CACHE_FILE = PROFILE_DIR / "token.json"
DEBUG_DIR = STATE_ROOT / "debug"

# Ephemeral outputs (documents, canonical exports) go to /tmp by default.
# Override with OPENCLAW_TMP if you want a different temp root.
_TMP_ROOT = Path(os.environ.get("OPENCLAW_TMP") or "/tmp").expanduser().resolve()
DEFAULT_OUTPUT_DIR = _TMP_ROOT / "openclaw" / "elba"

# Harden state directory permissions (best-effort)
if STATE_ROOT.exists():
    _harden_path(STATE_ROOT)
    if PROFILE_DIR.exists():
        _harden_path(PROFILE_DIR)
    if TOKEN_CACHE_FILE.exists():
        _harden_path(TOKEN_CACHE_FILE)

URL_LOGIN = "https://sso.raiffeisen.at/mein-login/identify"
URL_DASHBOARD = "https://mein.elba.raiffeisen.at/bankingws-widgetsystem/meine-produkte/dashboard"
URL_DOCUMENTS = "https://mein.elba.raiffeisen.at/bankingws-widgetsystem/mailbox/dokumente"

# Mapping from ID prefix to region name (for matching in dropdown)
REGION_MAPPING = {
    "ELVIE33V": "Burgenland",
    "ELOOE03V": "Carinthia",  # or "Kärnten"
    "ELVIE32V": "Lower Austria",  # "Lower Austria" or "Wien" 
    "ELOOE01V": "Upper Austria",  # could also be "Bank Direct" or "Privat Bank"
    "ELOOE05V": "Salzburg",
    "ELVIE38V": "Styria",  # or "Steiermark"
    "ELOOE11V": "Tyrol",   # could also be "Jungholz" or "Alpen Privatbank"
    "ELVIE37V": "Vorarlberg"
}

def load_credentials():
    """Load credentials from env vars or config.json.

    Priority: env vars > config.json.
    """
    elba_id = os.environ.get("RAIFFEISEN_ELBA_ID")
    pin = os.environ.get("RAIFFEISEN_ELBA_PIN")
    if elba_id and pin:
        return elba_id, pin

    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            elba_id = cfg.get("elba_id")
            pin = cfg.get("pin")
            if elba_id and pin:
                return elba_id, pin
        except Exception:
            pass

    # Legacy fallback: .env file (deprecated — migrate to config.json)
    legacy_env = CONFIG_DIR / ".env"
    if legacy_env.exists():
        config = {}
        for line in legacy_env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            config[key.strip()] = value.strip().strip("'").strip('"')

        elba_id = config.get('ELBA_ID')
        pin = config.get('ELBA_PIN')
        if elba_id and pin:
            print("[credentials] Loaded from legacy .env — consider migrating to config.json", file=sys.stderr)
            return elba_id, pin

    return None, None



def _now_iso_local() -> str:
    from datetime import datetime
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


DEBUG_ENABLED: bool = False


def _write_debug_json(prefix: str, payload) -> Path | None:
    if not DEBUG_ENABLED:
        return None
    _ensure_dir(DEBUG_DIR)
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    out = DEBUG_DIR / f"{ts}-{prefix}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    return out


def _eu_amount(amount: float | None) -> str:
    if amount is None:
        return "N/A"
    s = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def _canonical_account_type_elba(raw_type: str | None) -> str:
    t = (raw_type or "").lower()
    # ELBA 'type' here is UI label (e.g. Giro, Sparkonto, Kredit, Depot)
    if 'depot' in t:
        return 'depot'
    if 'giro' in t or 'konto' in t:
        return 'checking'
    if 'spar' in t:
        return 'savings'
    if 'kredit' in t or 'loan' in t:
        return 'debt'
    return 'other'


def canonicalize_accounts_elba(accounts: list[dict], raw_path: Path | None = None) -> dict:
    out_accounts = []
    for a in accounts or []:
        if not isinstance(a, dict):
            continue
        name = a.get('name') or 'N/A'
        iban = a.get('iban')
        typ = _canonical_account_type_elba(a.get('type'))

        currency = None
        # Determine currency from balance/value object
        for key in ('balance','available','value'):
            v = a.get(key)
            if isinstance(v, dict):
                currency = v.get('currencyCode') or v.get('currency')
                if currency:
                    break
        currency = (currency or 'EUR').strip()

        balances = None
        securities = None

        if a.get('type') == 'Depot' or typ == 'depot':
            v = a.get('value') if isinstance(a.get('value'), dict) else None
            pl = a.get('profit_loss') if isinstance(a.get('profit_loss'), dict) else None
            securities = {
                'value': {'amount': v.get('amount'), 'currency': currency} if v and v.get('amount') is not None else None,
                'profitLoss': {
                    'amount': pl.get('amount'),
                    'currency': (pl.get('currencyCode') or currency) if pl else currency,
                    'percent': pl.get('percent')
                } if pl else None
            }
        else:
            b = a.get('balance') if isinstance(a.get('balance'), dict) else None
            av = a.get('available') if isinstance(a.get('available'), dict) else None
            balances = {
                'booked': {'amount': b.get('amount'), 'currency': currency} if b and b.get('amount') is not None else None,
                'available': {'amount': av.get('amount'), 'currency': currency} if av and av.get('amount') is not None else None,
            }

        # Normalize depot identifiers: use digits-only id (e.g. "32939 / 66.252.586" -> "3293966252586")
        acct_id = iban or name
        acct_iban = iban
        if typ == 'depot':
            d = _digits(str(iban or ""))
            if d:
                acct_id = d
                acct_iban = d

        acct = {
            'id': acct_id,
            'type': typ,
            'name': name,
            'currency': currency,
        }
        # Omit "iban": null
        if acct_iban:
            acct['iban'] = acct_iban

        # Omit null/empty balances
        if isinstance(balances, dict):
            if any(v is not None for v in balances.values()):
                acct['balances'] = balances
        elif balances is not None:
            acct['balances'] = balances

        # Omit null/empty securities
        if isinstance(securities, dict):
            if any(v is not None for v in securities.values()):
                acct['securities'] = securities
        elif securities is not None:
            acct['securities'] = securities

        out_accounts.append(acct)

    return {
        'institution': 'elba',
        'fetchedAt': _now_iso_local(),
        'rawPath': str(raw_path) if raw_path else None,
        'accounts': out_accounts,
    }


def get_region_name(elba_id):
    """Determine region name from ELBA_ID prefix."""
    if not elba_id:
        return None
    prefix = elba_id[:8].upper()
    
    # Check specific mapping
    if prefix in REGION_MAPPING:
        return REGION_MAPPING[prefix]
    
    return None

def login(page, elba_id, pin, timeout_seconds: int | None = None):
    """Perform the login flow."""
    # Allow runtime override via global LOGIN_TIMEOUT
    if timeout_seconds is None:
        timeout_seconds = LOGIN_TIMEOUT
    print(f"[login] Navigating to {URL_LOGIN}...")
    page.goto(URL_LOGIN)
    
    # Check for service unavailable
    time.sleep(1)
    page_content = page.content()
    if "Service Unavailable" in page_content or "503" in page.title():
        print("[login] ERROR: Service Unavailable (503). ELBA may be temporarily down.")
        print("[login] Please try again later.")
        return False
    
    # Check for session expired page
    if page.locator('text="Session expired"').is_visible() or page.locator('text="Page Expired"').is_visible():
        print("[login] Session expired, restarting...")
        # Click Restart button if present
        if page.locator('button:has-text("Restart")').is_visible():
            page.locator('button:has-text("Restart")').click()
            time.sleep(2)
        # Don't return - continue with login flow
    else:
        # Check if we are already redirected to dashboard (session reuse)
        time.sleep(1)
        if "mein.elba.raiffeisen.at" in page.url:
            print("[login] Already logged in!")
            return True

    # 1. Select Region
    region_name = get_region_name(elba_id)
    if not region_name:
        print(f"[login] ERROR: Could not determine region for ID {elba_id}")
        return False
    
    print(f"[login] Selecting region for {elba_id[:8]} -> looking for '{region_name}'...")
    
    # Navigate dropdown option by option using arrow keys
    try:
        # Region dropdown: rds-select[formcontrolname="mandant"]
        dropdown = page.locator('rds-select[formcontrolname="mandant"]')
        dropdown.click()
        time.sleep(0.5)
        
        # Try to find the option by navigating with arrow keys
        # First, get the initial selected value
        max_attempts = 20  # Prevent infinite loop
        
        found = False
        for attempt in range(max_attempts):
            # Check the currently highlighted option
            try:
                # Get all options and find the active/highlighted one
                options = page.locator('rds-option')
                
                # Check each visible option for a match
                for i in range(options.count()):
                    option_text = options.nth(i).inner_text()
                    if region_name.lower() in option_text.lower():
                        print(f"[login] Found matching option: {option_text}")
                        options.nth(i).click()
                        time.sleep(0.5)
                        found = True
                        break
                        
            except Exception:
                pass
            
            if found:
                break
                
            # If not found yet, press down arrow to move to next option
            page.keyboard.press("ArrowDown")
            time.sleep(0.2)
        
        if not found:
            print(f"[login] ERROR: Could not find region '{region_name}' in dropdown")
            return False
        
    except Exception as e:
        print(f"[login] Error selecting region: {e}")
        return False

    # 2. Fill Form
    print("[login] Entering credentials...")
    try:
        # Signatory number: input[formcontrolname="verfuegerNr"]
        page.locator('input[formcontrolname="verfuegerNr"]').fill(elba_id)
        
        # PIN: input[formcontrolname="pin"]
        page.locator('input[formcontrolname="pin"]').fill(pin)
        
        # Wait for Continue button to become enabled
        print("[login] Waiting for Continue button to enable...")
        submit_button = page.locator('button[type="submit"]:not([disabled])')
        submit_button.wait_for(timeout=10000, state="visible")
        time.sleep(1)  # Extra safety delay for validation
        
        # Submit: button[type="submit"]
        submit_button.click()
    except Exception as e:
        print(f"[login] Error filling form: {e}")
        return False

    # 3. Handle 2FA (pushTAN)
    print("[login] Waiting for pushTAN screen...")
    
    try:
        # Wait for the code element: p.rds-display-1
        # Timeout 10s for the element to appear
        code_locator = page.locator('p.rds-display-1')
        code_locator.wait_for(timeout=10000)
        
        code = code_locator.inner_text().strip()
        print("\n" + "="*40)
        print(f"ELBA PUSHTAN CODE: {code}")
        print("="*40 + "\n")
        
        # Send to Telegram via stdout (Agent will see this)
        # Assuming the user is running this interactively or the agent is watching.
        
    except PlaywrightTimeout:
        # Maybe no 2FA needed or error?
        print("[login] Did not see pushTAN code. Checking for errors...")
    
    # 4. Wait for success or error
    print("[login] Waiting for navigation to dashboard...")
    start_time = time.time()
    while time.time() - start_time < max(int(timeout_seconds), 1):  # timeout for pushTAN approval
        # Check for service unavailable (skip if page is still navigating)
        try:
            page_content = page.content()
            if "Service Unavailable" in page_content or "503" in page.title():
                print("[login] ERROR: Service Unavailable (503). ELBA may be temporarily down.")
                return False
        except Exception:
            # Page is still navigating, skip this check
            pass
        
        if "mein.elba.raiffeisen.at" in page.url:
            print("[login] Login successful!")
            
            # Navigate to the full dashboard to ensure all cookies are set
            print("[login] Loading products dashboard to establish session...")
            # domcontentloaded is usually enough; occasionally Playwright reports net::ERR_ABORTED
            # even though the SPA is usable. Treat that as a warning and continue.
            try:
                page.goto(URL_DASHBOARD, wait_until="domcontentloaded", timeout=15000)
            except Exception as e:
                print(f"[login] WARNING: Dashboard navigation error: {e}")
            time.sleep(3)
            
            # Verify we didn't get redirected back to login
            if "sso.raiffeisen.at" in page.url or "mein-login" in page.url:
                print("[login] ERROR: Redirected back to login after initial success.")
                return False
            
            # Try to find at least one banking product card to confirm page loaded
            try:
                page.locator('banking-product-card').first.wait_for(timeout=5000, state="visible")
                print("[login] Dashboard loaded successfully!")
            except PlaywrightTimeout:
                print("[login] WARNING: Dashboard loaded but no product cards visible yet.")
            
            # Save the current URL for later use
            SESSION_URL_FILE.parent.mkdir(parents=True, exist_ok=True)
            SESSION_URL_FILE.write_text(page.url, encoding='utf-8')
            print(f"[login] Saved session URL: {page.url}")
            
            # Give browser extra time to persist everything
            time.sleep(2)
            
            return True
        
        # Check for session expired
        if page.locator('text="Session expired"').is_visible() or page.locator('text="Page Expired"').is_visible():
            print("[login] ERROR: Session expired during login.")
            return False
        
        # Check for invalid signature error
        if page.locator('text="Invalid signature data"').is_visible():
            print("[login] ERROR: Invalid signature data were entered. Please try again.")
            return False
        
        # Check errors
        if page.locator('div#error_message').is_visible():
            err = page.locator('div#error_message').inner_text()
            print(f"[login] ERROR: {err}")
            return False
            
        time.sleep(1)
        
    print("[login] Timeout waiting for approval.")
    return False


def fetch_accounts(page):
    """Fetch accounts from the dashboard carousel (assumes already on dashboard)."""
    # Ensure we're on the products dashboard
    if "meine-produkte/dashboard" not in page.url:
        print(f"[accounts] Navigating to products dashboard...")
        try:
            # networkidle is brittle for SPA apps; use domcontentloaded with a timeout.
            page.goto(URL_DASHBOARD, wait_until="domcontentloaded", timeout=15000)
            time.sleep(2)
        except Exception as e:
            error_msg = str(e)
            if "ERR_CONNECTION_RESET" in error_msg or "connection was reset" in error_msg.lower():
                print("[accounts] ERROR: Connection reset. ELBA server connection failed.")
                print("[accounts] Please try again later.")
                return []
            else:
                print(f"[accounts] ERROR: Navigation failed: {e}")
                return []
    
    # Check for connection errors on the page
    page_content = page.content()
    if "ERR_CONNECTION_RESET" in page_content or "connection was reset" in page_content.lower():
        print("[accounts] ERROR: Connection reset. ELBA server connection failed.")
        print("[accounts] Please try again later.")
        return []
    
    # Check for session expired or login page
    if "sso.raiffeisen.at" in page.url or "mein-login" in page.url:
        print("[accounts] ERROR: Redirected to login page. Session expired.")
        return []
    
    print(f"[accounts] Current URL: {page.url}")
    
    # Wait for banking product cards to load
    try:
        print("[accounts] Waiting for banking-product-card elements...")
        page.locator('banking-product-card').first.wait_for(timeout=15000, state="visible")
        print("[accounts] Found banking product cards!")
    except PlaywrightTimeout:
        print(f"[accounts] ERROR: Could not find banking product cards after timeout.")
        print(f"[accounts] Page title: {page.title()}")
        # Try to find what IS on the page
        try:
            body_text = page.locator('body').inner_text()[:500]
            print(f"[accounts] Page content preview: {body_text}")
        except:
            pass
        return []
    
    accounts = []
    seen_ibans = set()  # Track IBANs to avoid duplicates
    
    # Carousel navigation: click right arrow until it disappears
    carousel_page = 1
    max_pages = 20  # Safety limit
    
    while carousel_page <= max_pages:
        print(f"[accounts] Processing carousel page {carousel_page}...")
        
        # Wait a moment for carousel to settle
        time.sleep(1)
        
        # Get ALL banking-product-card elements in the DOM
        all_cards = page.locator('banking-product-card').all()
        
        # Filter to only actually visible cards (in viewport)
        visible_cards = []
        for card in all_cards:
            try:
                # Check if card is visible AND in viewport
                if card.is_visible():
                    bbox = card.bounding_box()
                    if bbox and bbox['width'] > 0 and bbox['height'] > 0:
                        visible_cards.append(card)
            except:
                pass
        
        print(f"[accounts] Found {len(visible_cards)} visible card(s) (out of {len(all_cards)} total in DOM)")
        
        cards_processed_this_page = 0
        
        # Process all visible cards
        for i, card in enumerate(visible_cards):
            print(f"[accounts] Processing card {i}...")
            
            # Try quick IBAN extraction for duplicate check
            quick_iban = None
            try:
                footer = card.locator('rds-card-footer')
                # Get all text content
                footer_text = footer.text_content(timeout=2000)
                
                # Remove screen reader text and clean up
                footer_text = footer_text.replace("Produkt-Id:", "")
                footer_text = footer_text.replace("IBAN bzw. Produkt ID kopieren", "")
                
                # Clean and normalize - just take all remaining text
                quick_iban = ' '.join(footer_text.split()).strip()
                
                if not quick_iban:
                    print(f"[accounts] Card {i}: Empty IBAN after cleaning")
                else:
                    print(f"[accounts] Card {i}: Extracted IBAN: '{quick_iban}'")
                    
                    if quick_iban in seen_ibans:
                        print(f"[accounts] Card {i}: Already processed")
                        continue  # Skip - already processed
            except Exception as e:
                print(f"[accounts] Card {i}: Could not quick-extract IBAN: {e}")
                # Continue processing - we'll get IBAN in the full extraction below
            
            try:
                # Extract account type from rds-card-subtitle
                account_type = card.locator('rds-card-subtitle').inner_text(timeout=5000).strip()
            except Exception as e:
                print(f"[accounts] Card {i}: Could not extract type: {e}")
                account_type = "Unknown"
            
            try:
                # Extract account name from rds-card-title
                name = card.locator('rds-card-title').inner_text(timeout=5000).strip()
            except Exception as e:
                print(f"[accounts] Card {i}: Could not extract name: {e}")
                name = "Unknown"
            
            try:
                # Extract balance from strong (could be text-success, text-danger, or plain strong)
                # Try text-success first (positive balance)
                balance_elem = card.locator('strong.text-success').first
                if balance_elem.count() > 0:
                    balance_text = balance_elem.inner_text(timeout=2000).strip()
                else:
                    # Try text-danger (negative balance for loans/credits)
                    balance_elem = card.locator('strong.text-danger').first
                    if balance_elem.count() > 0:
                        balance_text = balance_elem.inner_text(timeout=2000).strip()
                    else:
                        # For depots with 0, try any strong tag (might be plain styling)
                        balance_elem = card.locator('rds-card-content strong').first
                        balance_text = balance_elem.inner_text(timeout=2000).strip()
            except Exception as e:
                print(f"[accounts] Card {i}: Could not extract balance: {e}")
                # For Depot with no balance, default to 0
                if account_type == "Depot":
                    balance_text = "0,00 EUR"
                else:
                    balance_text = ""
            
            available_text = ""
            entwicklung_text = ""
            try:
                # Try to extract available amount from "verfügbar" (bank accounts)
                available_elem = card.locator('small:has-text("verfügbar")')
                available_text = available_elem.inner_text(timeout=2000).strip()
                # Extract just the amount part after "verfügbar"
                if "verfügbar" in available_text:
                    available_text = available_text.split("verfügbar")[1].strip()
            except Exception:
                # For Depot accounts, try to extract "Entwicklung" (performance)
                try:
                    entwicklung_elem = card.locator('small:has-text("Entwicklung")')
                    entwicklung_text = entwicklung_elem.inner_text(timeout=2000).strip()
                except Exception:
                    available_text = ""
            
            # Extract IBAN if we didn't get it in the quick check
            if quick_iban:
                iban = quick_iban
            else:
                try:
                    footer = card.locator('rds-card-footer')
                    footer_text = footer.text_content(timeout=5000)
                    footer_text = footer_text.replace("Produkt-Id:", "").replace("IBAN bzw. Produkt ID kopieren", "")
                    iban = ' '.join(footer_text.split()).strip()
                    if not iban:
                        iban = "Unknown"
                except Exception as e:
                    print(f"[accounts] Card {i}: Could not extract IBAN: {e}")
                    iban = "Unknown"
            
            # Skip if we couldn't extract valid data
            if not iban or iban == "Unknown" or account_type == "Unknown":
                print(f"[accounts] Card {i}: Skipping - incomplete data (iban={iban}, type={account_type})")
                continue
            
            # Add to seen set and increment counter
            seen_ibans.add(iban)
            cards_processed_this_page += 1
            
            balance_primary, balance_eur = _parse_money_pair(balance_text)
            
            if account_type == "Depot":
                profit_loss_percent = _parse_percent_text(entwicklung_text)
                available_primary = None
                available_eur = None
                profit_loss = {
                    "amount": None,
                    "currencyCode": None,
                    "percent": profit_loss_percent
                }
            else:
                available_primary, available_eur = _parse_money_pair(available_text)
                if available_primary is None:
                    available_primary = balance_primary
                profit_loss = None
            
            if account_type == "Depot":
                accounts.append({
                    "type": account_type,
                    "name": name,
                    "iban": iban,
                    "value": balance_primary,
                    "value_eur": balance_eur,
                    "profit_loss": profit_loss
                })
            else:
                accounts.append({
                    "type": account_type,
                    "name": name,
                    "iban": iban,
                    "balance": balance_primary,
                    "balance_eur": balance_eur,
                    "available": available_primary,
                    "available_eur": available_eur,
                    "profit_loss": profit_loss
                })
            
            print(f"[accounts] Card {i}: {account_type} - {name}")
        
        print(f"[accounts] Processed {cards_processed_this_page} new account(s) on this page")
        
        # If we didn't process any new cards for 2 consecutive pages, we're done
        if cards_processed_this_page == 0 and carousel_page > 2:
            print("[accounts] No new accounts found, stopping.")
            break
        
        # Check for right arrow to navigate to next carousel page
        print("[accounts] Checking for right arrow...")
        try:
            right_arrow = page.locator('rds-directional-arrow button.right').first
            
            # Check if arrow exists and is visible
            if right_arrow.count() > 0:
                is_visible = right_arrow.is_visible()
                is_disabled = right_arrow.is_disabled()
                print(f"[accounts] Right arrow found: visible={is_visible}, disabled={is_disabled}")
                
                if is_visible and not is_disabled:
                    print("[accounts] Clicking right arrow to next page...")
                    right_arrow.click()
                    time.sleep(2)  # Wait for carousel animation
                    carousel_page += 1
                else:
                    print("[accounts] Right arrow disabled or not visible - reached end.")
                    break
            else:
                print("[accounts] No right arrow found - single page carousel.")
                break
        except Exception as e:
            print(f"[accounts] Error checking right arrow: {e}")
            break
    
    if carousel_page > max_pages:
        print(f"[accounts] WARNING: Reached max carousel pages ({max_pages}), stopping.")
    
    print(f"[accounts] Total unique accounts found: {len(accounts)}")
    return accounts

def _extract_bearer_token(page):
    """Try to extract bearer token from storage."""
    token = page.evaluate("""() => {
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            const value = localStorage.getItem(key);
            if (value && (value.includes('Bearer') || key.includes('token') || key.includes('auth'))) {
                try {
                    const parsed = JSON.parse(value);
                    if (parsed.access_token) return parsed.access_token;
                    if (parsed.token) return parsed.token;
                    if (typeof parsed === 'string' && parsed.startsWith('Bearer ')) {
                        return parsed.substring(7);
                    }
                } catch {
                    if (typeof value === 'string' && value.match(/^[A-Za-z0-9_-]{20,}$/)) {
                        return value;
                    }
                }
            }
        }
        
        for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i);
            const value = sessionStorage.getItem(key);
            if (value && (value.includes('Bearer') || key.includes('token') || key.includes('auth'))) {
                try {
                    const parsed = JSON.parse(value);
                    if (parsed.access_token) return parsed.access_token;
                    if (parsed.token) return parsed.token;
                    if (typeof parsed === 'string' && parsed.startsWith('Bearer ')) {
                        return parsed.substring(7);
                    }
                } catch {
                    if (typeof value === 'string' && value.match(/^[A-Za-z0-9_-]{20,}$/)) {
                        return value;
                    }
                }
            }
        }
        return null;
    }""")
    
    if token:
        print(f"[token] Found token in storage: {token[:20]}...", flush=True)
    return token

def _load_cached_token():
    if not TOKEN_CACHE_FILE.exists():
        return None
    try:
        data = TOKEN_CACHE_FILE.read_text(encoding="utf-8").strip()
        if not data:
            return None
        payload = None
        try:
            payload = json.loads(data)
        except Exception:
            payload = None
        if isinstance(payload, dict):
            token = payload.get("token")
            if token:
                return token
        if isinstance(data, str) and data.startswith("{") is False:
            return data
    except Exception:
        return None
    return None

def _save_cached_token(token):
    if not token:
        return
    try:
        TOKEN_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_CACHE_FILE.write_text(json.dumps({"token": token}), encoding="utf-8")
    except Exception:
        pass

def _clear_cached_token():
    try:
        if TOKEN_CACHE_FILE.exists():
            TOKEN_CACHE_FILE.unlink()
    except Exception:
        pass

def _extract_bearer_token_from_storage_state(context):
    try:
        state = context.storage_state()
    except Exception:
        return None
    origins = state.get("origins", []) if isinstance(state, dict) else []
    for origin in origins:
        for item in origin.get("localStorage", []) + origin.get("sessionStorage", []):
            key = item.get("name", "")
            value = item.get("value", "")
            if value and (value.find("Bearer") >= 0 or "token" in key or "auth" in key):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, dict):
                        if parsed.get("access_token"):
                            return parsed.get("access_token")
                        if parsed.get("token"):
                            return parsed.get("token")
                    if isinstance(parsed, str) and parsed.startswith("Bearer "):
                        return parsed[7:]
                except Exception:
                    if isinstance(value, str) and re.match(r'^[A-Za-z0-9_-]{20,}$', value):
                        return value
    return None

def _get_bearer_token(context, page):
    """Extract bearer token from storage/cache or capture from API requests."""
    print("[token] Extracting bearer token...", flush=True)
    cached = _load_cached_token()
    if cached:
        print("[token] Using cached token...", flush=True)
        return cached
    
    token = _extract_bearer_token_from_storage_state(context)
    if token:
        print(f"[token] Found token in storage state: {token[:20]}...", flush=True)
        _save_cached_token(token)
        return token
    
    token = _extract_bearer_token(page)
    if token:
        _save_cached_token(token)
        return token
    
    print("[token] Token not found in storage, capturing from API requests...", flush=True)
    captured_token = {'value': None}
    
    def handle_request(route, request):
        auth_header = request.headers.get('authorization', '')
        if auth_header.startswith('Bearer '):
            captured_token['value'] = auth_header[7:]
            print(f"[token] Captured: {captured_token['value'][:20]}...", flush=True)
        route.continue_()
    
    # Hard time-limit the capture phase so we never hang here.
    page.set_default_timeout(15000)
    page.set_default_navigation_timeout(15000)

    page.route('**/api/**', handle_request)
    try:
        start = time.time()

        # Force a fresh navigation so the SPA triggers API calls (cache can short-circuit).
        try:
            page.goto("about:blank", timeout=5000)
        except Exception:
            pass

        try:
            # networkidle is brittle for SPA apps; use domcontentloaded with a timeout.
            page.goto(URL_DASHBOARD, wait_until="domcontentloaded", timeout=15000)
        except Exception:
            # If navigation fails, try a reload to trigger requests
            try:
                page.reload(wait_until="domcontentloaded", timeout=15000)
            except Exception:
                pass

        # Give it a moment for API calls to fire.
        time.sleep(3)
        if not captured_token['value'] and (time.time() - start) < 20:
            try:
                page.reload(wait_until="domcontentloaded", timeout=15000)
                time.sleep(2)
            except Exception:
                pass
    finally:
        try:
            page.unroute('**/api/**')
        except Exception:
            pass

    token = captured_token['value']
    if token:
        _save_cached_token(token)
    return token

def _money_dict_from_api(amount_obj):
    if not amount_obj or not isinstance(amount_obj, dict):
        return None
    amount = amount_obj.get('amount')
    currency = amount_obj.get('currencyCode') or amount_obj.get('currency')
    return {"amount": amount, "currencyCode": currency}

def _parse_money_text(text):
    if not text:
        return None
    s = ' '.join(text.split()).strip()
    if not s:
        return None
    
    currency_match = re.search(r'([A-Z]{3})$', s)
    currency = currency_match.group(1) if currency_match else None
    
    number_match = re.search(r'-?[\d\.\s]+,\d+|-?[\d\.\s]+', s)
    if not number_match:
        return {"amount": None, "currencyCode": currency}
    
    num = number_match.group(0).replace(' ', '').replace('.', '').replace(',', '.')
    try:
        amount = float(num)
    except Exception:
        amount = None
    
    return {"amount": amount, "currencyCode": currency}

def _parse_money_pair(text):
    if not text:
        return (None, None)
    parts = [p.strip() for p in text.split(" / ")]
    primary = _parse_money_text(parts[0]) if len(parts) > 0 else None
    secondary = _parse_money_text(parts[1]) if len(parts) > 1 else None
    return (primary, secondary)

def _parse_percent_text(text):
    if not text:
        return None
    m = re.search(r'-?[\d\.\s]+,\d+|-?[\d\.\s]+', text)
    if not m:
        return None
    num = m.group(0).replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(num) / 100.0
    except Exception:
        return None

def _format_money_for_print(money):
    if not money or not isinstance(money, dict):
        return "N/A"
    amount = money.get("amount")
    currency = money.get("currencyCode")
    if amount is None:
        return "N/A" if not currency else f"N/A {currency}"
    if currency:
        return f"{amount:,.2f} {currency}"
    return f"{amount:,.2f}"

def _format_money_pair_for_print(primary, secondary):
    primary_str = _format_money_for_print(primary)
    if secondary and isinstance(secondary, dict) and secondary.get("amount") is not None:
        secondary_str = _format_money_for_print(secondary)
        return f"{primary_str} / {secondary_str}"
    return primary_str

def _format_profit_loss_for_print(profit_loss):
    if not profit_loss or not isinstance(profit_loss, dict):
        return "N/A"
    percent = profit_loss.get("percent")
    if percent is None:
        return "N/A"
    return f"{percent * 100:.2f}%"

def _prune_none(value):
    if isinstance(value, dict):
        pruned = {}
        for k, v in value.items():
            pv = _prune_none(v)
            if pv is not None:
                pruned[k] = pv
        return pruned or None
    if isinstance(value, list):
        items = [v for v in (_prune_none(v) for v in value) if v is not None]
        return items or None
    return value

def _product_to_account(product):
    account_type = product.get('smallHeader') or product.get('type') or "Unknown"
    name = product.get('largeHeader') or "Unknown"
    product_type = product.get('type') or ""
    details = product.get('details') or {}
    
    if product_type == "DEPOT":
        iban = product.get('productId') or product.get('uniqueId') or "Unknown"
        value = _money_dict_from_api(details.get('betragKontoWaehrung'))
        value_eur = None
        profit_loss_eur = _money_dict_from_api(details.get('betragInEuro'))
        profit_loss_percent = details.get('entwicklungProzent')
        profit_loss = {
            "amount": profit_loss_eur.get("amount") if profit_loss_eur else None,
            "currencyCode": profit_loss_eur.get("currencyCode") if profit_loss_eur else None,
            "percent": (profit_loss_percent / 100.0) if profit_loss_percent is not None else None
        }
        available = None
        available_eur = None
    else:
        iban = product.get('uniqueId') or "Unknown"
        balance = _money_dict_from_api(details.get('betragKontoWaehrung'))
        balance_eur = _money_dict_from_api(details.get('betragInEuro'))
        available = _money_dict_from_api(details.get('verfuegbarKontoWaehrung'))
        available_eur = _money_dict_from_api(details.get('verfuegbarInEuro'))
        if available is None:
            available = balance
        profit_loss = None
    
    if product_type == "DEPOT":
        return {
            "type": account_type,
            "name": name,
            "iban": iban,
            "value": value,
            "value_eur": value_eur,
            "profit_loss": profit_loss
        }
    
    return {
        "type": account_type,
        "name": name,
        "iban": iban,
        "balance": balance,
        "balance_eur": balance_eur,
        "available": available,
        "available_eur": available_eur,
        "profit_loss": profit_loss
    }

def _digits(s: str | None) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


def fetch_accounts_api(token, cookies):
    """Fetch accounts via products API.

    Returns: (accounts, raw_path) where raw_path points to the bank-native products JSON.
    """
    url = "https://mein.elba.raiffeisen.at/api/bankingws-widgetsystem/bankingws-ui/rest/produkte?skipImages=true"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3 Safari/605.1.15",
    }

    print("[api] Fetching products...", flush=True)

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            products = response.json()
            print(f"[api] Found {len(products)} products", flush=True)
            raw_path = _write_debug_json("products-raw", products)
            return ([_product_to_account(p) for p in products], raw_path)

        print(f"[api] Request failed with status {response.status_code}: {response.text}", flush=True)
        return (None, None)
    except Exception as e:
        print(f"[api] Error: {e}", flush=True)
        return (None, None)


def fetch_depot_transactions_api(token, cookies, bankleitzahl: str, depotnummer: str, date_from: str, date_to: str):
    """Fetch depot (portfolio) transactions via ELBA depotzentrale endpoint.

    Returns: (payload, status_code, raw_path)
    """
    url = "https://mein.elba.raiffeisen.at/api/bankingwp-depotzentrale/depotzentrale-ui/rest/bewegungsuebersicht"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3 Safari/605.1.15",
    }

    body = {
        "bankleitzahl": str(bankleitzahl),
        "depotnummer": str(depotnummer),
        "datumVon": f"{date_from}T00:00:00.000Z",
        "datumBis": f"{date_to}T23:59:59.999Z",
        "auftragstyp": "ALLE",
        "status": "ALLE",
        "dauerauftrag": "OHNE",
    }

    try:
        resp = requests.post(url, headers=headers, cookies=cookies, data=json.dumps(body))
        payload = None
        try:
            payload = resp.json()
        except Exception:
            payload = {"_error": "non-json response", "text": resp.text}

        raw_path = _write_debug_json(
            f"depot-transactions-raw-{bankleitzahl}{depotnummer}-{date_from}-{date_to}",
            payload,
        )
        return payload, resp.status_code, raw_path
    except Exception as e:
        return {"_error": str(e)}, 0, None


def fetch_documents(page, output_dir=None, date_from=None, date_to=None):
    """Fetch and download documents from mailbox."""
    print("[documents] Navigating to documents page...")
    try:
        page.goto(URL_DOCUMENTS, wait_until="networkidle")
        time.sleep(3)
    except Exception as e:
        error_msg = str(e)
        if "ERR_CONNECTION_RESET" in error_msg or "connection was reset" in error_msg.lower():
            print("[documents] ERROR: Connection reset. ELBA server connection failed.")
            return []
        else:
            print(f"[documents] ERROR: Navigation failed: {e}")
            return []
    
    # Apply date filter if provided
    if date_from or date_to:
        print(f"[documents] Applying date filter: {date_from or 'any'} to {date_to or 'any'}", flush=True)
        try:
            if date_from:
                from_input = page.locator('input[formcontrolname="fromDate"]')
                from_input.fill(date_from)
                print(f"[documents] Filled 'from' date: {date_from}, pressing Tab...", flush=True)
                page.keyboard.press("Tab")
                print("[documents] Waiting for page to reload after 'from' date...", flush=True)
                time.sleep(3)
            
            if date_to:
                to_input = page.locator('input[formcontrolname="toDate"]')
                to_input.fill(date_to)
                print(f"[documents] Filled 'to' date: {date_to}, pressing Tab...", flush=True)
                page.keyboard.press("Tab")
                print("[documents] Waiting for page to reload after 'to' date...", flush=True)
                time.sleep(3)
            
            # Wait for results to fully load
            print("[documents] Waiting for filtered results to load...", flush=True)
            time.sleep(3)
        except Exception as e:
            print(f"[documents] Warning: Could not apply date filter: {e}", flush=True)
    
    # Set up download directory
    if not output_dir:
        output_dir = DEFAULT_OUTPUT_DIR / "documents"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[documents] Saving to: {output_dir}")
    
    # Configure browser downloads
    # Note: Playwright handles downloads via download events
    
    documents = []
    downloaded_files = set()  # Track downloaded files to avoid duplicates
    processed_docs = set()  # Track document names we've already processed
    
    # Download documents while scrolling (virtual scroller removes items from DOM as you scroll)
    print("[documents] Starting download with infinite scroll...")
    print("[documents] Downloading documents as they appear (virtual scroller)", flush=True)
    time.sleep(3)
    
    no_new_downloads_count = 0
    max_no_change_attempts = 50  # Increased to ensure we get all 189+ documents (need more scrolling)
    total_processed = 0
    successful_downloads = 0
    
    # Find the virtual scroller (the inner scroll container)
    scroller = page.locator('virtual-scroller.vertical.selfScroll')
    
    while no_new_downloads_count < max_no_change_attempts:
        # Get currently visible document rows
        doc_rows = page.locator('rds-list-item-row').all()
        
        downloads_this_batch = 0
        
        # Process each visible row
        for row in doc_rows:
            try:
                # Check if this row has a download button
                download_btn = row.locator('button[icon="download"]').first
                if download_btn.count() == 0:
                    continue  # Skip rows without download buttons
                
                # Extract document name for logging
                try:
                    name_elem = row.locator('p.rds-body-strong.dok-truncate-2-lines')
                    doc_name = name_elem.inner_text(timeout=1000).strip()
                except:
                    doc_name = f"document_{total_processed}"
                
                # Create a unique identifier for this row (button element ID or position)
                try:
                    button_aria = download_btn.get_attribute('aria-label', timeout=1000)
                    row_id = button_aria if button_aria else doc_name
                except:
                    row_id = doc_name
                
                # Skip if we've already processed this exact button
                if row_id in processed_docs:
                    continue
                
                processed_docs.add(row_id)
                total_processed += 1
                
                print(f"\n[documents] Processing {total_processed}: {doc_name}", flush=True)
                
                # Try to download
                try:
                    
                    print(f"[documents]   → Initiating download...", flush=True)
                    with page.expect_download(timeout=30000) as download_info:
                        download_btn.click()
                        time.sleep(0.5)
                    
                    download = download_info.value
                    filename = _safe_download_filename(download.suggested_filename)
                    
                    # Handle duplicate filenames by adding (2), (3), etc.
                    base_filepath = output_dir / filename
                    if base_filepath.exists() or filename in downloaded_files:
                        # Extract name and extension
                        name_parts = filename.rsplit('.', 1)
                        if len(name_parts) == 2:
                            base_name, ext = name_parts
                        else:
                            base_name, ext = filename, ''
                        
                        # Find next available number
                        counter = 2
                        while True:
                            new_filename = f"{base_name} ({counter}){('.' + ext) if ext else ''}"
                            new_filepath = output_dir / new_filename
                            if not new_filepath.exists() and new_filename not in downloaded_files:
                                filename = new_filename
                                filepath = new_filepath
                                break
                            counter += 1
                    else:
                        filepath = base_filepath
                    
                    download.save_as(filepath)
                    downloaded_files.add(filename)
                    successful_downloads += 1
                    downloads_this_batch += 1
                    
                    print(f"[documents]   ✓ Downloaded {successful_downloads}: {filename}", flush=True)
                    print(f"[documents]   ✓ Saved to: {filepath}", flush=True)
                    
                    time.sleep(1)  # Rate limit
                    
                except Exception as e:
                    print(f"[documents]   ✗ Error downloading: {e}", flush=True)
            except Exception as e:
                print(f"[documents] Error processing row: {e}", flush=True)
                continue
        
        # Scroll to load more
        if downloads_this_batch > 0:
            no_new_downloads_count = 0
            print(f"[documents] Downloaded {downloads_this_batch} new document(s) this batch, scrolling for more...", flush=True)
        else:
            no_new_downloads_count += 1
            print(f"[documents] No new documents this batch ({no_new_downloads_count}/{max_no_change_attempts}), scrolling...", flush=True)
        
        # Scroll more aggressively to trigger lazy loading
        scroller.evaluate("el => el.scrollBy(0, 2000)")
        time.sleep(5)  # Longer wait to ensure lazy load completes
    
    print(f"\n[documents] Downloaded {successful_downloads} document(s) to {output_dir}", flush=True)
    return documents


def cmd_setup():
    """Interactive setup wizard."""
    print("Raiffeisen ELBA Setup")
    print("---------------------")

    # Ensure directories
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)
        _harden_path(CONFIG_DIR)
        print(f"Created {CONFIG_DIR}")

    elba_id = input("Enter ELBA-Verfügernummer (e.g., ELVIE32V...): ").strip()
    pin = input("Enter PIN (5 digits): ").strip()

    if not elba_id or not pin:
        print("Error: ID and PIN are required.")
        return

    # Write to config.json
    cfg = {"elba_id": elba_id, "pin": pin}
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    _harden_path(CONFIG_FILE)

    print(f"Credentials saved to {CONFIG_FILE}")

    # Verify Playwright
    print("Verifying Playwright installation...")
    try:
        import playwright
        subprocess.run(["playwright", "install", "chromium"], check=False)
    except (ImportError, FileNotFoundError):
        print("Please install playwright: pip3 install playwright")

def cmd_login(headless=True):
    """Run the login flow."""
    elba_id, pin = load_credentials()
    if not elba_id or not pin:
        print("Credentials not found. Run 'setup' first.")
        sys.exit(1)
        
    with sync_playwright() as p:
        # Create persistent context
        if not PROFILE_DIR.exists():
            PROFILE_DIR.mkdir(parents=True)
            
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.new_page()
        try:
            if login(page, elba_id, pin, timeout_seconds=LOGIN_TIMEOUT):
                print("Session saved.")
            else:
                sys.exit(1)
        finally:
            context.close()

def cmd_logout():
    """Clear the session."""
    if PROFILE_DIR.exists():
        import shutil
        shutil.rmtree(PROFILE_DIR)
        print("Session cleared.")
    else:
        print("No session found.")


def cmd_accounts(headless=True, json_output=False):
    """List all accounts (logs in automatically if needed)."""
    elba_id, pin = load_credentials()
    if not elba_id or not pin:
        print("Credentials not found. Run 'setup' first.")
        sys.exit(1)
    
    # Ensure profile dir exists
    if not PROFILE_DIR.exists():
        PROFILE_DIR.mkdir(parents=True)
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.new_page()
        raw_path = None
        
        try:
            # Try to use existing session first (no forced login)
            print("[accounts] Attempting to access dashboard (reuse session)...")
            try:
                page.goto(URL_DASHBOARD, wait_until="domcontentloaded")
                time.sleep(2)
            except Exception as e:
                error_msg = str(e)
                if "ERR_CONNECTION_RESET" in error_msg or "connection was reset" in error_msg.lower():
                    print("[accounts] ERROR: Connection reset. ELBA server connection failed.")
                    print("[accounts] Please try again later.")
                    sys.exit(1)
                else:
                    raise
            
            # Check for connection errors on the page
            page_content = page.content()
            if "ERR_CONNECTION_RESET" in page_content or "connection was reset" in page_content.lower():
                print("[accounts] ERROR: Connection reset. ELBA server connection failed.")
                print("[accounts] Please try again later.")
                sys.exit(1)
            
            # Prefer API for accounts (reuse token from prior login)
            token = _get_bearer_token(context, page)
            accounts = None
            if token:
                cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}
                accounts, raw_path = fetch_accounts_api(token, cookies)

                # Common failure: cached token expired -> 401. Clear cache and retry once.
                if accounts is None:
                    _clear_cached_token()
                    token = _get_bearer_token(context, page)
                    if token:
                        cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}
                        accounts, raw_path = fetch_accounts_api(token, cookies)

            # If API failed, then login and retry once
            if accounts is None:
                print("[accounts] API request failed or no token; performing login...")
                if not login(page, elba_id, pin, timeout_seconds=LOGIN_TIMEOUT):
                    print("[accounts] Login failed.")
                    sys.exit(1)

                # After login, force token re-extraction (cached token might be stale).
                _clear_cached_token()
                token = _get_bearer_token(context, page)
                if token:
                    cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}
                    accounts, raw_path = fetch_accounts_api(token, cookies)

            if accounts is None:
                print("[accounts] WARNING: API unavailable, falling back to scraping.")
                accounts = fetch_accounts(page)

            wrapper = canonicalize_accounts_elba(accounts or [], raw_path=raw_path)

            if json_output:
                print(json.dumps(wrapper, ensure_ascii=False, indent=2))
            else:
                print(f"[accounts] {len(wrapper['accounts'])} account(s):")
                for acc in wrapper["accounts"]:
                    name = acc.get("name") or "N/A"
                    iban = acc.get("iban")
                    iban_clean = "".join(str(iban).split()) if iban is not None else ""
                    iban_short = f"{iban_clean[:4]}...{iban_clean[-4:]}" if len(iban_clean) > 8 else (iban_clean or "IBAN N/A")
                    typ = acc.get("type") or "other"
                    cur = acc.get("currency") or "EUR"

                    balances = acc.get("balances") if isinstance(acc.get("balances"), dict) else None
                    booked = balances.get("booked") if isinstance(balances, dict) else None
                    available = balances.get("available") if isinstance(balances, dict) else None

                    sec = acc.get("securities") if isinstance(acc.get("securities"), dict) else None
                    sec_value = sec.get("value") if isinstance(sec, dict) else None

                    if isinstance(sec_value, dict) and sec_value.get("amount") is not None:
                        v_s = f"{_eu_amount(float(sec_value['amount']))} {cur}"
                        pl = sec.get("profitLoss") if isinstance(sec, dict) else None
                        pl_s = ""
                        if isinstance(pl, dict) and pl.get("amount") is not None:
                            pl_s = f" (P/L {_eu_amount(float(pl['amount']))} {cur}" + (f" / {float(pl.get('percent'))*100:.1f}%" if pl.get("percent") is not None else "") + ")"
                        print(f"- {name} — {iban_short} — value {v_s}{pl_s} — {typ}")
                        continue

                    booked_s = "N/A"
                    avail_s = None
                    if isinstance(booked, dict) and booked.get("amount") is not None:
                        booked_s = f"{_eu_amount(float(booked['amount']))} {cur}"
                    if isinstance(available, dict) and available.get("amount") is not None:
                        avail_s = f"{_eu_amount(float(available['amount']))} {cur}"

                    if avail_s and avail_s != booked_s:
                        print(f"- {name} — {iban_short} — {booked_s} (avail {avail_s}) — {typ}")
                    else:
                        print(f"- {name} — {iban_short} — {booked_s} — {typ}")

                if wrapper.get("rawPath"):
                    print(f"[accounts] raw payload saved: {wrapper['rawPath']}")
            
        finally:
            context.close()


def cmd_download(headless=True, output_dir=None, date_from=None, date_to=None, json_output=False):
    """Download documents from mailbox (logs in automatically if needed)."""
    print("[INIT] Starting ELBA document download...", flush=True)
    elba_id, pin = load_credentials()
    if not elba_id or not pin:
        print("Credentials not found. Run 'setup' first.", flush=True)
        sys.exit(1)
    print(f"[INIT] Loaded credentials for {elba_id[:8]}...", flush=True)
    
    # Ensure profile dir exists
    if not PROFILE_DIR.exists():
        PROFILE_DIR.mkdir(parents=True)
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1280, "height": 800},
            accept_downloads=True
        )
        
        page = context.new_page()
        raw_path = None
        
        try:
            # Try to navigate to documents first
            print("[download] Attempting to access documents page...")
            try:
                page.goto(URL_DOCUMENTS, wait_until="networkidle")
                time.sleep(2)
            except Exception as e:
                error_msg = str(e)
                if "ERR_CONNECTION_RESET" in error_msg or "connection was reset" in error_msg.lower():
                    print("[download] ERROR: Connection reset. ELBA server connection failed.")
                    print("[download] Please try again later.")
                    sys.exit(1)
                else:
                    raise
            
            # Check if we got redirected to login
            if "sso.raiffeisen.at" in page.url or "mein-login" in page.url:
                print("[download] Not logged in, performing login...")
                if not login(page, elba_id, pin, timeout_seconds=LOGIN_TIMEOUT):
                    print("[download] Login failed.")
                    sys.exit(1)
                # After successful login, navigate to documents
                print("[download] Login successful, navigating to documents...")
                page.goto(URL_DOCUMENTS, wait_until="networkidle")
                time.sleep(2)
            else:
                print("[download] Already logged in!")
            
            # Now fetch and download documents
            documents = fetch_documents(page, output_dir, date_from, date_to)
            
            if json_output:
                import json
                print(json.dumps(documents, ensure_ascii=False, indent=2))
            elif not documents:
                print("No documents downloaded.")
            
        finally:
            context.close()

def _first_nonempty(*vals: object) -> str | None:
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _canonicalize_elba_transaction(tx: dict) -> dict:
    """Map ELBA kontoumsaetze transaction into the canonical transaction schema."""
    out: dict = {"status": "booked"}

    tid = tx.get("id")
    if tid is not None:
        out["id"] = str(tid)

    bd = tx.get("buchungstag")
    if isinstance(bd, str) and len(bd) >= 10:
        out["bookingDate"] = bd[:10]

    vd = tx.get("valuta")
    if isinstance(vd, str) and len(vd) >= 10:
        out["valueDate"] = vd[:10]

    betrag = tx.get("betrag")
    if isinstance(betrag, dict):
        amt = betrag.get("amount")
        cur = betrag.get("currencyCode") or betrag.get("currency")
        if isinstance(amt, (int, float)) and isinstance(cur, str) and cur:
            out["amount"] = {"amount": float(amt), "currency": cur}

    # counterparty
    cp_name = _first_nonempty(
        tx.get("transaktionsteilnehmer"),
        tx.get("transaktionsteilnehmerZeile1"),
        tx.get("transaktionsteilnehmerZeile2u3"),
        tx.get("auftraggeberInformation"),
    )
    cp: dict = {}
    if cp_name:
        cp["name"] = cp_name

    cp_iban = tx.get("auftraggeberIban")
    if isinstance(cp_iban, str) and cp_iban.strip():
        cp["iban"] = cp_iban.strip()

    cp_bic = tx.get("auftraggeberBic")
    if isinstance(cp_bic, str) and cp_bic.strip():
        cp["bic"] = cp_bic.strip()

    if cp:
        out["counterparty"] = cp

    # description/purpose
    desc = _first_nonempty(tx.get("auftragskurzVerwendungszweck"), tx.get("verwendungszweckZeile1"))
    purpose_parts = [
        tx.get("verwendungszweckZeile1"),
        tx.get("verwendungszweckZeile2"),
        tx.get("verwendungszweckZeile3"),
    ]
    purpose = " ".join([p.strip() for p in purpose_parts if isinstance(p, str) and p.strip()])

    if desc:
        out["description"] = desc
    if purpose:
        out["purpose"] = purpose

    # references
    refs: dict = {}
    zr = tx.get("zahlungsreferenz")
    if isinstance(zr, str) and zr.strip():
        refs["paymentReference"] = zr.strip()

    br = tx.get("bestandreferenz") or tx.get("ersterfasserreferenz")
    if isinstance(br, str) and br.strip():
        refs["bankReference"] = br.strip()

    mandate = tx.get("mandatsreferenz")
    if isinstance(mandate, str) and mandate.strip():
        refs["mandateId"] = mandate.strip()

    if refs:
        out["references"] = refs

    # category
    cat = tx.get("kategorieCode")
    if isinstance(cat, str) and cat.strip():
        out["category"] = {"code": cat.strip()}

    return out


def cmd_transactions(headless=True, account=None, date_from=None, date_to=None, output=None, fmt="json"):
    """Download transactions for an account (logs in automatically if needed)."""
    if not account or not date_from or not date_to:
        print("Missing required arguments: --account, --from, --until")
        sys.exit(1)

    # ISO date validation
    try:
        datetime.strptime(date_from, "%Y-%m-%d")
        datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        print("ERROR: Dates must be in YYYY-MM-DD format.")
        sys.exit(1)

    elba_id, pin = load_credentials()
    if not elba_id or not pin:
        print("Credentials not found. Run 'setup' first.")
        sys.exit(1)

    if not PROFILE_DIR.exists():
        PROFILE_DIR.mkdir(parents=True)

    from download_transactions import fetch_transactions_all

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1280, "height": 800},
        )

        page = context.new_page()
        try:
            print("[transactions] Attempting to access documents (reuse session)...")
            page.goto(URL_DOCUMENTS, wait_until="domcontentloaded")
            time.sleep(2)

            token = _get_bearer_token(context, page)
            if not token:
                print("[transactions] Token not found, performing login...")
                if not login(page, elba_id, pin, timeout_seconds=LOGIN_TIMEOUT):
                    print("[transactions] Login failed.")
                    sys.exit(1)
                token = _get_bearer_token(context, page)

            if not token:
                print("[transactions] ERROR: Could not extract bearer token")
                sys.exit(1)

            cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}

            transactions, status_code = fetch_transactions_all(token, cookies, account, date_from, date_to)

            if transactions is None and status_code == 401:
                print("[transactions] Token rejected (401). Clearing cache and re-authenticating...", flush=True)
                _clear_cached_token()
                if not login(page, elba_id, pin, timeout_seconds=LOGIN_TIMEOUT):
                    print("[transactions] Login failed.")
                    sys.exit(1)
                token = _get_bearer_token(context, page)
                if not token:
                    print("[transactions] ERROR: Could not extract bearer token")
                    sys.exit(1)
                cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}
                transactions, status_code = fetch_transactions_all(token, cookies, account, date_from, date_to)

            if transactions is None:
                print("[transactions] Failed to fetch transactions")
                sys.exit(1)

            raw_path = None
            if DEBUG_ENABLED:
                raw_path = _write_debug_json("transactions-raw", transactions)
                print(f"[debug] Raw transactions saved to: {raw_path}")

            # Resolve output base (even if there are 0 transactions)
            acc_clean = _safe_filename_component(account, default="account")
            if output:
                out_path = _safe_output_path(output, WORKSPACE_ROOT)
                if out_path.is_dir() or str(output).endswith(os.sep):
                    out_path.mkdir(parents=True, exist_ok=True)
                    base_name = f"transactions_{acc_clean}_{date_from}_{date_to}"
                    file_base = out_path / base_name
                else:
                    _safe_output_path(str(out_path.parent), WORKSPACE_ROOT)
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    file_base = out_path
            else:
                base_name = f"transactions_{acc_clean}_{date_from}_{date_to}"
                DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                file_base = DEFAULT_OUTPUT_DIR / base_name

            if len(transactions) == 0:
                print("[transactions] No transactions found in date range", flush=True)

            canonical = [_canonicalize_elba_transaction(tx) for tx in transactions if isinstance(tx, dict)]

            wrapper = {
                "institution": "elba",
                "account": {"id": account, "iban": account if "AT" in account else None},
                "range": {"from": date_from, "until": date_to},
                "fetchedAt": _now_iso_local(),
                "transactions": canonical,
            }
            if DEBUG_ENABLED:
                wrapper["raw"] = transactions
                if raw_path:
                    wrapper["rawPath"] = str(raw_path)

            if fmt == "json":
                out_file = file_base.with_suffix(".json")
                out_file.write_text(json.dumps(wrapper, ensure_ascii=False, indent=2))
                print(f"[transactions] Saved JSON: {out_file}")
            else:
                import csv

                out_file = file_base.with_suffix(".csv")
                out_file.parent.mkdir(parents=True, exist_ok=True)
                fieldnames = [
                    "bookingDate",
                    "valueDate",
                    "amount",
                    "currency",
                    "counterparty",
                    "description",
                    "purpose",
                    "bankReference",
                    "paymentReference",
                ]
                with out_file.open("w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=fieldnames)
                    w.writeheader()
                    for tx in canonical:
                        amt = tx.get("amount") if isinstance(tx.get("amount"), dict) else {}
                        cp = tx.get("counterparty") if isinstance(tx.get("counterparty"), dict) else {}
                        refs = tx.get("references") if isinstance(tx.get("references"), dict) else {}
                        w.writerow(
                            {
                                "bookingDate": tx.get("bookingDate"),
                                "valueDate": tx.get("valueDate"),
                                "amount": amt.get("amount"),
                                "currency": amt.get("currency"),
                                "counterparty": cp.get("name"),
                                "description": tx.get("description"),
                                "purpose": tx.get("purpose"),
                                "bankReference": refs.get("bankReference"),
                                "paymentReference": refs.get("paymentReference"),
                            }
                        )
                print(f"[transactions] Saved CSV: {out_file}")

        finally:
            context.close()



def _fetch_portfolio_positions(token: str, cookies: dict, depot_id: str, as_of_date: str | None = None):
    """Fetch depot portfolio positions via ELBA depotzentrale API.

    This is the JSON API for "stocks data" (positions overview).

    Endpoint (observed):
      GET https://mein.elba.raiffeisen.at/api/bankingwp-depotzentrale/depotzentrale-ui/rest/positionsuebersicht/<depotId>[/<YYYY-MM-DD>]

    Returns: (payload, status_code)
    """
    base_url = "https://mein.elba.raiffeisen.at/api/bankingwp-depotzentrale/depotzentrale-ui/rest/positionsuebersicht"
    url = f"{base_url}/{depot_id}/{as_of_date}" if as_of_date else f"{base_url}/{depot_id}"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3 Safari/605.1.15",
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            return response.json(), response.status_code
        return {"error": response.text, "status": response.status_code}, response.status_code
    except Exception as e:
        return {"error": str(e)}, None


def _canonicalize_elba_portfolio(payload: dict, *, depot_id: str, as_of_date: str | None) -> dict:
    """Best-effort canonicalization for ELBA portfolio positions.

    We keep the full bank-native payload in wrapper.raw when --debug.
    """
    # NOTE: We don't yet know all payload shapes; this is defensive.
    positions = []
    
    # Try different structures based on observed API responses
    # 1. Structure from input.txt: "gruppen" -> "positionen"
    if isinstance(payload, dict) and "gruppen" in payload:
        gruppen = payload.get("gruppen", [])
        if isinstance(gruppen, list):
            for g in gruppen:
                if isinstance(g, dict) and "positionen" in g:
                    pos = g.get("positionen")
                    if isinstance(pos, list):
                        positions.extend([x for x in pos if isinstance(x, dict)])
    
    # 2. Fallback: direct list keys
    if not positions and isinstance(payload, dict):
        for key in ("positionen", "positions", "data", "items"):
            v = payload.get(key)
            if isinstance(v, list):
                positions = [x for x in v if isinstance(x, dict)]
                break

    def money(amount_obj):
        if not amount_obj:
            return None
        if isinstance(amount_obj, dict):
            try:
                amt = amount_obj.get("wert") or amount_obj.get("amount")
                curr = amount_obj.get("einheit") or amount_obj.get("currency") or "EUR"
                if amt is not None:
                    return {"amount": float(amt), "currency": str(curr)}
            except Exception:
                pass
        return None

    out_positions = []
    for p in positions:
        # Mapping based on input.txt schema
        isin = p.get("isin") or p.get("ISIN")
        name = p.get("wpBezeichnung") or p.get("bezeichnung") or p.get("name") or p.get("instrumentName")
        
        # Quantity
        qty_obj = p.get("stueck") or p.get("bestand") or p.get("quantity")
        qty = None
        if isinstance(qty_obj, dict):
            qty = qty_obj.get("wert")
        elif isinstance(qty_obj, (int, float)):
            qty = qty_obj
            
        # Price (Current quote)
        price_obj = p.get("aktKurs") or p.get("kurs") or p.get("price")
        price = money(price_obj)
        
        # Purchase Price (Avg Cost)
        cost_obj = p.get("kaufKurs")
        cost_price = money(cost_obj)
        
        # Market Value
        value_obj = p.get("aktKurswert") or p.get("wert") or p.get("marketValue") or p.get("value")
        market_value = money(value_obj)
        
        # Performance
        perf_abs_obj = p.get("veraenderungAbsolut")
        perf_abs = money(perf_abs_obj)
        
        perf_pct = p.get("veraenderungAbsolutProzent")

        out_positions.append(
            {
                "isin": str(isin) if isin else None,
                "name": str(name).strip() if name else None,
                "quantity": qty,
                "price": price,
                "costPrice": cost_price,
                "marketValue": market_value,
                "performance": {
                    "absolute": perf_abs,
                    "percent": float(perf_pct) if perf_pct is not None else None
                }
            }
        )

    return {
        "institution": "elba",
        "account": {"id": depot_id, "iban": None},
        "asOf": as_of_date,
        "fetchedAt": _now_iso_local(),
        "positions": out_positions,
    }


def _canonicalize_elba_depot_transaction(item: dict) -> dict | None:
    if not isinstance(item, dict):
        return None

    bewegungsart = item.get("bewegungsart")
    auftragsart = item.get("auftragsart")

    ts = item.get("zeitstempel")
    booking_date = None
    if isinstance(ts, str) and len(ts) >= 10:
        booking_date = ts[:10]

    # id: prefer execution number (seems stable), then order key, then numeric id.
    tid = item.get("ausfuehrungsnummer") or item.get("keyAuftrag")
    if isinstance(tid, str) and tid.strip():
        tid = tid.strip()
    else:
        tid = item.get("id")
        tid = str(tid) if tid is not None else None

    # Determine kind/action
    kind = None
    action = None
    if isinstance(auftragsart, str) and auftragsart.strip():
        kind = auftragsart.strip().lower()
        if kind == "verkauf":
            action = "sell"
            kind = "trade"
        elif kind == "kauf":
            action = "buy"
            kind = "trade"
        elif kind == "ertrag":
            action = "dividend"
            kind = "dividend"

    sec_name = item.get("wpBezeichnung")
    isin = item.get("isin")

    qty = item.get("ausfuehrungsMenge")
    if qty is None:
        qty = item.get("menge")

    unit = item.get("masseinheit")

    kurs = item.get("kurs") if isinstance(item.get("kurs"), dict) else {}
    price_amt = kurs.get("amount")
    price_cur = kurs.get("currency") or kurs.get("currencyCode")

    refs = {}
    if isinstance(item.get("keyAuftrag"), str) and item.get("keyAuftrag").strip():
        refs["orderKey"] = item.get("keyAuftrag").strip()
    if isinstance(item.get("ausfuehrungsnummer"), str) and item.get("ausfuehrungsnummer").strip():
        refs["executionNumber"] = item.get("ausfuehrungsnummer").strip()
    if isinstance(item.get("keyFremdsystem"), str) and item.get("keyFremdsystem").strip():
        refs["externalKey"] = item.get("keyFremdsystem").strip()
    if isinstance(item.get("positionskey"), str) and item.get("positionskey").strip():
        refs["positionKey"] = item.get("positionskey").strip()

    out = {
        "id": tid,
        "bookingDate": booking_date,
        "timestamp": ts,
        "kind": kind,
        "action": action,
        "security": {"isin": isin, "name": sec_name},
        "quantity": qty,
        "unit": unit,
        "price": {"amount": price_amt, "currency": price_cur} if (price_amt is not None and price_cur) else None,
        "venue": item.get("handelsplatz"),
        "status": item.get("statustext") or ("executed" if bewegungsart == "AUSFUEHRUNG" else None),
        "references": refs or None,
        "document": {
            "available": bool(item.get("belegVorhanden")),
            "key": item.get("belegkey"),
            "timestamp": item.get("belegtimestamp"),
        },
    }

    # prune None keys recursively
    pruned = _prune_none(out)
    return pruned


def canonicalize_depot_transactions_elba(payload: dict, depot_id: str, date_from: str, date_to: str, raw_path: Path | None = None) -> dict:
    items = payload.get("positionen") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        items = []

    out = []
    for it in items:
        if not isinstance(it, dict):
            continue

        bewegungsart = str(it.get("bewegungsart") or "").upper()
        auftragsart = str(it.get("auftragsart") or "")

        # Default filter: executed trades + dividends/earnings
        if bewegungsart == "AUSFUEHRUNG":
            pass
        elif bewegungsart == "UMSATZ" and auftragsart.strip().lower() == "ertrag":
            pass
        else:
            continue

        c = _canonicalize_elba_depot_transaction(it)
        if c:
            out.append(c)

    wrapper = {
        "institution": "elba",
        "account": {"id": str(depot_id)},
        "range": {"from": date_from, "until": date_to},
        "fetchedAt": _now_iso_local(),
        "transactions": out,
    }

    if DEBUG_ENABLED and raw_path:
        wrapper["rawPath"] = str(raw_path)

    return wrapper


def cmd_portfolio(headless=True, depot_id=None, as_of_date=None, json_output=False):
    """Fetch depot portfolio positions."""
    if not depot_id:
        print("Missing required argument: --depot-id")
        sys.exit(1)

    elba_id, pin = load_credentials()
    if not elba_id or not pin:
        print("Credentials not found. Run 'setup' first.")
        sys.exit(1)

    if not PROFILE_DIR.exists():
        PROFILE_DIR.mkdir(parents=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1280, "height": 800},
        )

        page = context.new_page()
        try:
            print("[portfolio] Attempting to access dashboard/documents (reuse session)...", flush=True)
            try:
                page.goto(URL_DOCUMENTS, wait_until="domcontentloaded")
                time.sleep(2)
            except Exception:
                pass

            token = _get_bearer_token(context, page)
            if not token:
                print("[portfolio] Token not found, performing login...", flush=True)
                if not login(page, elba_id, pin, timeout_seconds=LOGIN_TIMEOUT):
                    print("[portfolio] Login failed.")
                    sys.exit(1)
                token = _get_bearer_token(context, page)

            if not token:
                print("[portfolio] ERROR: Could not extract bearer token")
                sys.exit(1)

            cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}
            payload, status_code = _fetch_portfolio_positions(token, cookies, str(depot_id), as_of_date)

            if status_code == 401:
                print("[portfolio] Token rejected (401). Clearing cache and re-authenticating...", flush=True)
                _clear_cached_token()
                if not login(page, elba_id, pin, timeout_seconds=LOGIN_TIMEOUT):
                    print("[portfolio] Login failed.")
                    sys.exit(1)
                token = _get_bearer_token(context, page)
                cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}
                payload, status_code = _fetch_portfolio_positions(token, cookies, str(depot_id), as_of_date)

            if status_code != 200:
                print("[portfolio] Failed to fetch portfolio", flush=True)
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                sys.exit(1)

            canonical = _canonicalize_elba_portfolio(payload if isinstance(payload, dict) else {}, depot_id=str(depot_id), as_of_date=as_of_date)

            if DEBUG_ENABLED:
                raw_path = _write_debug_json(f"portfolio-raw-{depot_id}", payload)
                canonical["rawPath"] = str(raw_path) if raw_path else None
                canonical["raw"] = payload

            if json_output:
                print(json.dumps(canonical, ensure_ascii=False, indent=2))
            else:
                # Human summary
                print(json.dumps(canonical, ensure_ascii=False, indent=2))

        finally:
            context.close()


def main():
    parser = argparse.ArgumentParser(description="Raiffeisen ELBA Automation")
    # Global flags (keep ordering consistent with george.py)
    parser.add_argument("--visible", action="store_true", help="Show browser")
    parser.add_argument("--login-timeout", type=int, default=DEFAULT_LOGIN_TIMEOUT, help="Seconds to wait for pushTAN approval (default: 300)")
    parser.add_argument("--debug", action="store_true", help="Save bank-native payloads to workspace/raiffeisen-elba/debug (default: off)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("login", help="Login and save session")
    subparsers.add_parser("logout", help="Clear session")

    accounts_parser = subparsers.add_parser("accounts", help="List accounts")
    accounts_parser.add_argument("--json", action="store_true", help="Output as JSON")

    transactions_parser = subparsers.add_parser("transactions", help="Download transactions")
    transactions_parser.add_argument("--account", required=True, help="Account IBAN")
    transactions_parser.add_argument("--from", dest="date_from", required=True, help="Start date (YYYY-MM-DD)")
    transactions_parser.add_argument("--until", dest="date_to", required=True, help="End date (YYYY-MM-DD)")
    transactions_parser.add_argument("--format", dest="fmt", choices=["csv", "json"], default="json", help="Output format")
    transactions_parser.add_argument("--out", dest="output", help="Output file base or directory")

    args = parser.parse_args()

    global DEBUG_ENABLED
    DEBUG_ENABLED = bool(getattr(args, "debug", False))

    # Propagate login timeout to login() calls.
    global LOGIN_TIMEOUT
    try:
        LOGIN_TIMEOUT = int(getattr(args, "login_timeout", DEFAULT_LOGIN_TIMEOUT))
    except Exception:
        LOGIN_TIMEOUT = DEFAULT_LOGIN_TIMEOUT

    if args.command == "login":
        cmd_login(headless=not args.visible)
    elif args.command == "logout":
        cmd_logout()
    elif args.command == "accounts":
        cmd_accounts(headless=not args.visible, json_output=getattr(args, 'json', False))
    elif args.command == "transactions":
        cmd_transactions(
            headless=not args.visible,
            account=getattr(args, 'account', None),
            date_from=getattr(args, 'date_from', None),
            date_to=getattr(args, 'date_to', None),
            output=getattr(args, 'output', None),
            fmt=getattr(args, 'fmt', "json")
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
