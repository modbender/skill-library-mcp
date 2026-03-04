#!/usr/bin/env python3
"""
HFP Klientenportal - RZL Portal Automation

Upload accounting documents to HFP tax accountant portal.
Uses sync Playwright for browser automation.
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
from pathlib import Path
from datetime import datetime

# Fast path: allow --help without requiring Playwright
if "-h" in sys.argv or "--help" in sys.argv:
    sync_playwright = None  # type: ignore[assignment]
    PlaywrightTimeout = Exception  # type: ignore[assignment]
else:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
        sys.exit(1)

# ---------------------------------------------------------------------------
# Workspace & path resolution (§5.1, §5.22)
# ---------------------------------------------------------------------------

_SKILL_NAME = "klientenportal"


def _find_workspace_root() -> Path:
    """Find the workspace root (directory containing 'skills/').

    Resolution order:
    1. OPENCLAW_WORKSPACE env var
    2. CWD if it contains 'skills/'
    3. Walk up from script location
    4. Fall back to CWD
    """
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


WORKSPACE_ROOT = _find_workspace_root()
CONFIG_DIR = WORKSPACE_ROOT / _SKILL_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"
PROFILE_DIR = CONFIG_DIR / ".pw-profile"

# ---------------------------------------------------------------------------
# State directory hardening (§5.15)
# ---------------------------------------------------------------------------


def _set_strict_umask() -> None:
    try:
        os.umask(0o077)
    except Exception:
        pass


def _harden_path(p: Path) -> None:
    try:
        if p.is_dir():
            os.chmod(p, 0o700)
        elif p.is_file():
            os.chmod(p, 0o600)
    except Exception:
        pass


_set_strict_umask()

# ---------------------------------------------------------------------------
# Output path sandboxing (§5.3)
# ---------------------------------------------------------------------------

_TMP_ROOT = Path(os.environ.get("OPENCLAW_TMP") or "/tmp").expanduser().resolve()
DEFAULT_OUTPUT_DIR = _TMP_ROOT / "openclaw" / _SKILL_NAME


def _safe_output_path(raw: str) -> Path:
    """Validate output path is within workspace or /tmp."""
    p = Path(raw).expanduser().resolve()
    ws = WORKSPACE_ROOT.resolve()
    tmp = Path("/tmp").resolve()
    if p == ws or p.is_relative_to(ws):
        return p
    if p == tmp or p.is_relative_to(tmp):
        return p
    raise SystemExit(
        f"ERROR: output path must be under workspace ({ws}) or /tmp, got: {p}"
    )


# ---------------------------------------------------------------------------
# Filename sanitization (§5.5)
# ---------------------------------------------------------------------------


def _safe_filename(name: str) -> str:
    """Sanitize a string for use as a filename component."""
    name = name.replace("/", "_").replace("\\", "_")
    name = re.sub(r"\.\.+", ".", name)
    name = re.sub(r"[^\w\s\-.]", "_", name)
    return name.strip().strip(".")


# ---------------------------------------------------------------------------
# Config (§5.2 — no .env, config.json only)
# ---------------------------------------------------------------------------

BELEGKREIS_MAP = {
    "ER": "Eingangsrechnungen",
    "AR": "Ausgangsrechnungen",
    "KA": "Kassa",
    "SP": "Sparkasse",
}


def _load_config() -> dict:
    """Load config from config.json or env vars.

    Env vars (override config.json values):
        KLIENTENPORTAL_PORTAL_ID, KLIENTENPORTAL_USER_ID, KLIENTENPORTAL_PASSWORD
    """
    cfg: dict = {}
    if CONFIG_FILE.exists():
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        _harden_path(CONFIG_FILE)

    # Env vars override / supplement config.json
    portal_id = os.environ.get("KLIENTENPORTAL_PORTAL_ID") or cfg.get("portal_id", "")
    user_id = os.environ.get("KLIENTENPORTAL_USER_ID") or cfg.get("user_id", "")
    password = os.environ.get("KLIENTENPORTAL_PASSWORD") or cfg.get("password", "")

    if not portal_id or not user_id or not password:
        missing = [n for n, v in [("portal_id", portal_id), ("user_id", user_id), ("password", password)] if not v]
        print(f"ERROR: Missing config: {', '.join(missing)}")
        print(f"Create {CONFIG_FILE} or set env vars. See SKILL.md for details.")
        sys.exit(1)

    cfg["portal_id"] = portal_id
    cfg["portal_url"] = cfg.get("portal_url") or f"https://klientenportal.at/prod/{portal_id}"
    cfg["user_id"] = user_id
    cfg["password"] = password
    return cfg


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
    _harden_path(p)


# ---------------------------------------------------------------------------
# Browser helpers
# ---------------------------------------------------------------------------


def dismiss_modals(page):
    """Dismiss any modal dialogs (Wartungsmeldung, etc.)."""
    for _attempt in range(5):
        try:
            ok_btn = page.locator('dialog button:has-text("OK")')
            if ok_btn.count() > 0:
                ok_btn.first.click(force=True, timeout=2000)
                time.sleep(0.5)
                continue
        except Exception:
            pass
        try:
            page.keyboard.press("Escape")
            time.sleep(0.3)
        except Exception:
            pass
        try:
            modal_root = page.locator("dxbl-modal-root")
            if modal_root.count() == 0:
                break
        except Exception:
            break
    try:
        page.locator('text="Klient:"').click(timeout=1000)
        time.sleep(0.3)
    except Exception:
        pass


def _launch_context(pw, *, visible: bool = False):
    """Launch a persistent browser context."""
    _ensure_dir(PROFILE_DIR)
    return pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=not visible,
        viewport={"width": 1280, "height": 900},
    )


def login(page, config: dict) -> bool:
    """Log in to the portal."""
    portal_url = config["portal_url"]

    # Already logged in?
    if page.locator("text=Abmelden").count() > 0:
        print("[login] Session still valid", flush=True)
        dismiss_modals(page)
        return True

    page.goto(f"{portal_url}/account/login", wait_until="networkidle")
    time.sleep(1)

    if page.locator("text=Abmelden").count() > 0:
        print("[login] Already logged in", flush=True)
        dismiss_modals(page)
        return True

    print("[login] Logging in...", flush=True)
    page.locator('input[type="text"]').first.fill(config["user_id"])
    page.locator('input[type="password"]').first.fill(config["password"])
    page.locator('button:has-text("Login")').click()

    page.wait_for_load_state("networkidle")
    time.sleep(1)
    dismiss_modals(page)

    if page.locator("text=Abmelden").count() > 0:
        print("[login] Success", flush=True)
        return True
    print("[login] Failed", flush=True)
    return False


def _ensure_logged_in(page, config: dict) -> bool:
    """Navigate to upload page, log in if needed."""
    portal_url = config["portal_url"]
    page.goto(f"{portal_url}/Klient/Beleg/BelegTransfer/upload", wait_until="networkidle")
    time.sleep(1)

    if "/account/login" in page.url:
        print("[upload] Session expired, logging in...", flush=True)
        if not login(page, config):
            return False
        page.goto(
            f"{portal_url}/Klient/Beleg/BelegTransfer/upload",
            wait_until="networkidle",
        )
        time.sleep(1)

    dismiss_modals(page)
    return True


def _select_belegkreis(page, belegkreis: str) -> None:
    """Select a Belegkreis on the upload page."""
    if belegkreis == "ER":
        return  # Default
    print(f"[upload] Selecting Belegkreis: {belegkreis}", flush=True)
    try:
        bk_combo = (
            page.locator('text="Belegkreis:"').locator("..").locator('[role="combobox"]')
        )
        bk_combo.click(force=True, timeout=5000)
        time.sleep(0.5)
        bk_combo.fill(belegkreis)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(0.5)
    except Exception as e:
        print(f"[upload] Warning: Could not set Belegkreis: {e}", flush=True)


def upload_file(page, file_path: Path) -> bool:
    """Upload a single file via Direktübermittlung."""
    print(f"[upload] Uploading: {file_path.name}", flush=True)
    try:
        file_inputs = page.locator('input[type="file"]')
        if file_inputs.count() == 0:
            print("[upload] ERROR: No file input found", flush=True)
            return False
        file_inputs.first.set_input_files(str(file_path))
        time.sleep(3)
        print(f"[upload] ✓ {file_path.name}", flush=True)
        return True
    except Exception as e:
        print(f"[upload] ERROR: {e}", flush=True)
        return False


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_login(args):
    """Test login."""
    config = _load_config()
    with sync_playwright() as p:
        context = _launch_context(p, visible=args.visible)
        page = context.new_page()
        try:
            return 0 if login(page, config) else 1
        finally:
            context.close()


def cmd_upload(args):
    """Upload files to portal."""
    config = _load_config()

    # Resolve files (restricted to workspace + /tmp)
    allowed_roots: list[Path] = [Path("/tmp").resolve()]
    cwd = Path.cwd()
    if (cwd / "skills").is_dir():
        allowed_roots.append(cwd.resolve())
    ws = os.environ.get("OPENCLAW_WORKSPACE")
    if ws:
        allowed_roots.append(Path(ws).resolve())

    def _is_allowed(p: Path) -> bool:
        s = str(p)
        return any(s.startswith(str(a) + "/") or s == str(a) for a in allowed_roots)

    files: list[Path] = []
    for pattern in args.file:
        path = Path(pattern).expanduser()
        if path.is_file():
            resolved = path.resolve()
            if not _is_allowed(resolved):
                print(f"ERROR: Refusing to upload '{pattern}' — must be inside workspace or /tmp")
                return 1
            files.append(resolved)
        else:
            parent = path.parent if path.parent.exists() else Path.cwd()
            for m in sorted(parent.glob(path.name)):
                if m.is_file():
                    resolved = m.resolve()
                    if not _is_allowed(resolved):
                        print(f"ERROR: Refusing to upload '{m}' — must be inside workspace or /tmp")
                        return 1
                    files.append(resolved)

    if not files:
        print("ERROR: No files found to upload")
        return 1

    print(f"[upload] Uploading {len(files)} file(s) to Belegkreis {args.belegkreis}")

    with sync_playwright() as p:
        context = _launch_context(p, visible=args.visible)
        page = context.new_page()
        try:
            if not _ensure_logged_in(page, config):
                return 1

            _select_belegkreis(page, args.belegkreis)

            ok = 0
            for file_path in files:
                if upload_file(page, file_path):
                    ok += 1
                time.sleep(1)

            print(f"\n[upload] Uploaded {ok}/{len(files)} files")
            return 0 if ok == len(files) else 1
        finally:
            context.close()


def cmd_released(args):
    """List released (freigegebene) files."""
    config = _load_config()
    with sync_playwright() as p:
        context = _launch_context(p, visible=args.visible)
        page = context.new_page()
        try:
            portal_url = config["portal_url"]
            page.goto(f"{portal_url}/Klient/Beleg/BelegHistory", wait_until="networkidle")
            time.sleep(1)
            if "/account/login" in page.url:
                if not login(page, config):
                    return 1
                page.goto(f"{portal_url}/Klient/Beleg/BelegHistory", wait_until="networkidle")
                time.sleep(1)
            dismiss_modals(page)

            # Extract table rows
            rows = page.locator("table tbody tr")
            count = rows.count()
            if count == 0:
                print("No released files found.")
                return 0
            for i in range(count):
                cells = rows.nth(i).locator("td")
                parts = [cells.nth(j).inner_text().strip() for j in range(min(cells.count(), 5))]
                print(" | ".join(parts))
            return 0
        finally:
            context.close()


def cmd_download(args):
    """Download Kanzleidokumente."""
    config = _load_config()
    out_dir = _safe_output_path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        context = _launch_context(p, visible=args.visible)
        page = context.new_page()
        try:
            portal_url = config["portal_url"]
            page.goto(f"{portal_url}/Klient/Beleg/BelegTransfer/noupload", wait_until="networkidle")
            time.sleep(1)
            if "/account/login" in page.url:
                if not login(page, config):
                    return 1
                page.goto(
                    f"{portal_url}/Klient/Beleg/BelegTransfer/noupload",
                    wait_until="networkidle",
                )
                time.sleep(1)
            dismiss_modals(page)

            # Find download links
            links = page.locator('a[href*="download"], a[href*="Download"]')
            count = links.count()
            if count == 0:
                print("No documents available for download.")
                return 0

            print(f"[download] Found {count} document(s)")
            for i in range(count):
                link = links.nth(i)
                with page.expect_download() as dl_info:
                    link.click()
                download = dl_info.value
                suggested = _safe_filename(download.suggested_filename or f"document_{i}.pdf")
                dest = out_dir / suggested
                download.save_as(dest)
                print(f"[download] ✓ {dest}")

            return 0
        finally:
            context.close()


# ---------------------------------------------------------------------------
# Received files (from accountant)
# ---------------------------------------------------------------------------


def _launch_fresh_context(pw, *, visible: bool = False):
    """Launch a fresh (non-persistent) browser + context.

    The ReceivedFiles page uses DevExpress Blazor grids that don't render
    reliably inside Playwright persistent contexts, so we use a regular
    browser launch with explicit login for these commands.
    """
    browser = pw.chromium.launch(headless=not visible)
    ctx = browser.new_context(
        accept_downloads=True,
        viewport={"width": 1920, "height": 1080},
    )
    return browser, ctx


def _login_fresh(page, config: dict) -> bool:
    """Login on a fresh (non-persistent) context.

    The Klientenportal uses Blazor — the URL may not change on login
    redirect, so we detect the login form by looking for the username
    input field rather than checking the URL.
    """
    portal_url = config["portal_url"]
    page.goto(f"{portal_url}/Klient/Info/ReceivedFiles", timeout=20000)
    time.sleep(3)

    # Detect login form (Blazor may keep URL as ReceivedFiles)
    username_input = page.locator(
        'input[name="Input.Username"], input[type="text"]'
    ).first
    if username_input.count() == 0 or not username_input.is_visible():
        # No login form visible — already logged in
        return True

    print("[login] Logging in...", flush=True)
    username_input.fill(config["user_id"])
    page.locator(
        'input[name="Input.Password"], input[type="password"]'
    ).first.fill(config["password"])

    # Click the "Login" button specifically (not "Passwort zurücksetzen")
    page.get_by_role("button", name="Login").click()
    page.wait_for_load_state("domcontentloaded")
    time.sleep(5)

    # Check if login succeeded: look for "Abmelden" link
    if page.locator("text=Abmelden").count() > 0:
        print("[login] Success", flush=True)
        dismiss_modals(page)
        return True

    # Fallback: check if login form is still showing
    login_btn = page.get_by_role("button", name="Login")
    if login_btn.count() > 0 and login_btn.is_visible():
        print("[login] Failed", flush=True)
        return False

    print("[login] Success", flush=True)
    dismiss_modals(page)
    return True


def _navigate_received(page, config: dict) -> bool:
    """Navigate to ReceivedFiles page, login if needed (fresh context)."""
    if not _login_fresh(page, config):
        return False

    # Ensure we're on ReceivedFiles
    portal_url = config["portal_url"]
    if "ReceivedFiles" not in page.url:
        page.goto(f"{portal_url}/Klient/Info/ReceivedFiles", timeout=20000)
        time.sleep(3)

    dismiss_modals(page)

    # Wait for the Blazor/DevExpress grid to render data rows
    for attempt in range(15):
        rows = page.locator("tr:has(td button span.dxbl-btn-caption)")
        if rows.count() > 0:
            break
        time.sleep(1)
    else:
        # Grid may need more time; final wait
        time.sleep(3)

    return True


def _parse_received_rows(page) -> list[dict]:
    """Parse rows from the ReceivedFiles grid.

    Table columns: (icon) | Datei [BTN] | Von | Dokumentbereich | Empfangen | Auswahl [CB] | (empty)
    """
    entries: list[dict] = []
    rows = page.locator("tr").all()
    for row in rows:
        cells = row.locator("td")
        count = cells.count()
        if count < 5:
            continue

        # The filename is in a button inside cell 1
        btn = cells.nth(1).locator("button").first
        if btn.count() == 0:
            continue
        name = btn.inner_text().strip()
        if not name or name.startswith("Anzahl"):
            continue

        von = cells.nth(2).inner_text().strip()
        bereich = cells.nth(3).inner_text().strip()
        empfangen = cells.nth(4).inner_text().strip()

        # Check if this row has a checkbox (data row, not filter)
        has_cb = cells.nth(5).locator("input[type='checkbox']").count() > 0
        if not has_cb:
            continue

        entries.append({
            "name": name,
            "from": von,
            "bereich": bereich,
            "received": empfangen,
        })
    return entries


def cmd_received(args):
    """List files received from accountant."""
    config = _load_config()
    use_json = getattr(args, "json", False)
    limit = getattr(args, "limit", None)

    with sync_playwright() as p:
        browser, context = _launch_fresh_context(p, visible=args.visible)
        page = context.new_page()
        try:
            if not _navigate_received(page, config):
                return 1

            entries = _parse_received_rows(page)
            if not entries:
                print("No received files found.")
                return 0

            if limit:
                entries = entries[:limit]

            if use_json:
                print(json.dumps(entries, indent=2, ensure_ascii=False))
            else:
                # Column-aligned output
                name_w = max(len(e["name"]) for e in entries)
                from_w = max(len(e["from"]) for e in entries)
                ber_w = max(len(e["bereich"]) for e in entries)
                for e in entries:
                    print(
                        f"{e['name']:<{name_w}}  {e['from']:<{from_w}}  "
                        f"{e['bereich']:<{ber_w}}  {e['received']}"
                    )
                print(f"\n{len(entries)} file(s)")
            return 0
        finally:
            context.close()
            browser.close()


def cmd_received_download(args):
    """Download specific files from the ReceivedFiles page.

    Supports:
      - Index: ``received-download 1`` (latest file)
      - Name pattern: ``received-download "10-12_2025"``
      - ``--latest`` shortcut
    """
    config = _load_config()
    out_dir = _safe_output_path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser, context = _launch_fresh_context(p, visible=args.visible)
        page = context.new_page()
        try:
            if not _navigate_received(page, config):
                return 1

            entries = _parse_received_rows(page)
            if not entries:
                print("No received files found.")
                return 0

            # Determine which files to download
            targets: list[str] = getattr(args, "target", []) or []
            latest = getattr(args, "latest", False)

            if latest:
                targets = ["1"]  # First row = latest

            if not targets:
                print("ERROR: Specify file(s) to download (index, name pattern, or --latest)")
                return 1

            to_download: list[int] = []  # row indices (0-based in entries list)

            for t in targets:
                # Try as index first
                try:
                    idx = int(t) - 1
                    if 0 <= idx < len(entries):
                        to_download.append(idx)
                    else:
                        print(f"WARNING: Index {t} out of range (1-{len(entries)})")
                    continue
                except ValueError:
                    pass

                # Match by name pattern (case-insensitive substring)
                pattern = t.lower()
                matched = False
                for i, e in enumerate(entries):
                    if pattern in e["name"].lower():
                        to_download.append(i)
                        matched = True
                if not matched:
                    print(f"WARNING: No file matching '{t}'")

            if not to_download:
                print("ERROR: No matching files to download")
                return 1

            # Deduplicate, preserve order
            seen: set[int] = set()
            unique: list[int] = []
            for idx in to_download:
                if idx not in seen:
                    seen.add(idx)
                    unique.append(idx)
            to_download = unique

            print(f"[received-download] Downloading {len(to_download)} file(s):", flush=True)
            for idx in to_download:
                print(f"  {idx + 1}. {entries[idx]['name']}", flush=True)

            # Select checkboxes for target files
            # Data rows start at tr index 2 (0=header, 1=filter row)
            data_rows = page.locator("tr").all()
            data_row_indices: list[int] = []
            row_idx = 0
            for i, tr in enumerate(data_rows):
                cells = tr.locator("td")
                if cells.count() < 5:
                    continue
                btn = cells.nth(1).locator("button").first
                if btn.count() == 0:
                    continue
                name = btn.inner_text().strip()
                if not name or name.startswith("Anzahl"):
                    continue
                has_cb = cells.nth(5).locator("input[type='checkbox']").count() > 0
                if not has_cb:
                    continue
                data_row_indices.append(i)
                row_idx += 1

            # Check the boxes
            for dl_idx in to_download:
                if dl_idx >= len(data_row_indices):
                    continue
                tr_idx = data_row_indices[dl_idx]
                tr = data_rows[tr_idx]
                cb = tr.locator("td").nth(5).locator("input[type='checkbox']").first
                if cb.count():
                    cb.check()
                    time.sleep(0.3)

            time.sleep(1)

            # Click download button
            dl_btn = page.locator("button:has-text('Ausgewählte Dateien herunterladen')").first
            if dl_btn.count() == 0:
                print("ERROR: Download button not found")
                return 1

            print("[received-download] Downloading...", flush=True)
            with page.expect_download(timeout=60000) as dl_info:
                dl_btn.click()
            download = dl_info.value
            suggested = download.suggested_filename or "received_files.zip"

            # If single file, it might come as PDF; if multiple, as ZIP
            dest = out_dir / _safe_filename(suggested)
            download.save_as(dest)
            size = dest.stat().st_size
            print(f"[received-download] ✓ {dest} ({size:,} bytes)", flush=True)

            # If ZIP with single file, extract it
            if dest.suffix.lower() == ".zip" and len(to_download) == 1:
                import zipfile
                with zipfile.ZipFile(dest) as zf:
                    names = zf.namelist()
                    if len(names) == 1:
                        extracted = out_dir / _safe_filename(names[0])
                        with zf.open(names[0]) as src, open(extracted, "wb") as dst:
                            dst.write(src.read())
                        print(f"[received-download] Extracted: {extracted}", flush=True)
                        dest.unlink()  # Remove zip wrapper

            return 0
        finally:
            context.close()
            browser.close()


def cmd_logout(args):
    """Clear session (delete Playwright profile)."""
    print(f"[logout] Clearing profile: {PROFILE_DIR}")
    if PROFILE_DIR.exists():
        shutil.rmtree(PROFILE_DIR)
        print("[logout] ✓ Session cleared")
    else:
        print("[logout] No profile to clear")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="HFP Klientenportal Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s login
  %(prog)s upload -f invoice.pdf --belegkreis KA
  %(prog)s upload -f *.xml --belegkreis SP
  %(prog)s released
  %(prog)s download
  %(prog)s logout
        """,
    )

    parser.add_argument("--visible", action="store_true", help="Show browser")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # login
    subparsers.add_parser("login", help="Test login").set_defaults(func=cmd_login)

    # upload
    upload_p = subparsers.add_parser("upload", help="Upload files")
    upload_p.add_argument(
        "-f", "--file", nargs="+", required=True, help="File(s) to upload"
    )
    upload_p.add_argument(
        "--belegkreis",
        default="ER",
        choices=list(BELEGKREIS_MAP.keys()),
        help="Document category (default: ER)",
    )
    upload_p.set_defaults(func=cmd_upload)

    # released
    subparsers.add_parser("released", help="List released files").set_defaults(
        func=cmd_released
    )

    # download (Kanzleidokumente)
    dl_p = subparsers.add_parser("download", help="Download Kanzleidokumente")
    dl_p.add_argument("-o", "--output", help="Output directory (default: /tmp/openclaw/klientenportal)")
    dl_p.set_defaults(func=cmd_download)

    # received (list files from accountant)
    recv_p = subparsers.add_parser("received", help="List files received from accountant")
    recv_p.add_argument("--json", action="store_true", help="Output as JSON")
    recv_p.add_argument("-n", "--limit", type=int, help="Show only the N most recent files")
    recv_p.set_defaults(func=cmd_received)

    # received-download (download specific received files)
    recv_dl_p = subparsers.add_parser("received-download", help="Download specific received files")
    recv_dl_p.add_argument("target", nargs="*", help="File index (1=latest) or name pattern")
    recv_dl_p.add_argument("--latest", action="store_true", help="Download the latest file")
    recv_dl_p.add_argument("-o", "--output", help="Output directory")
    recv_dl_p.set_defaults(func=cmd_received_download)

    # logout
    subparsers.add_parser("logout", help="Clear session").set_defaults(func=cmd_logout)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
