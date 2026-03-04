#!/usr/bin/env python3
"""
Ghost Browser Daemon
Launches an undetected Chrome browser using nodriver and exposes it via CDP for chrome-devtools-mcp.
Includes a command server for full browser control (screenshots, JS eval, DOM interaction, etc.).
Optimized for LLM agents with text-based interaction, markdown output, and smart element matching.

Usage:
    python ghost_browser.py start [--headless] [--profile NAME] [--extension PATH] [--proxy URL]
    python ghost_browser.py stop
    python ghost_browser.py status [--json]
    python ghost_browser.py health
    python ghost_browser.py tabs [--json]
    python ghost_browser.py navigate <url> [--force-new] [--exact] [--json]
    python ghost_browser.py screenshot [--tab ID] [--output PATH] [--json]
    python ghost_browser.py content [--tab ID] [--json]
    python ghost_browser.py readable [--tab ID] [--max-length N] [--json]
    python ghost_browser.py elements [--form-only] [--limit N] [--tab ID] [--json]
    python ghost_browser.py page-summary [--tab ID] [--json]
    python ghost_browser.py eval <js> [--tab ID] [--json]
    python ghost_browser.py click <selector> [--tab ID] [--json]
    python ghost_browser.py type <selector> <text> [--tab ID] [--json]
    python ghost_browser.py interact <action> <text> [--type-text TEXT] [--index N] [--tab ID] [--json]
    python ghost_browser.py fill-form <json-string> [--submit] [--tab ID] [--json]
    python ghost_browser.py find <selector> [--tab ID] [--json]
    python ghost_browser.py scroll [--down|--up|--to Y] [--tab ID] [--json]
    python ghost_browser.py wait <selector> [--timeout N] [--tab ID] [--json]
    python ghost_browser.py wait-ready [--timeout N] [--tab ID] [--json]
    python ghost_browser.py hover <selector-or-text> [--by-text] [--tab ID] [--json]
    python ghost_browser.py close-tab <ID> [--json]
    python ghost_browser.py activate-tab <ID> [--json]
    python ghost_browser.py cookies [--domain X] [--tab ID] [--json]
    python ghost_browser.py set-cookie <name> <value> [--domain D] [--json]
    python ghost_browser.py clear-cookies [--domain D] [--json]
    python ghost_browser.py storage list|get|set|delete|clear [--session] [--tab ID] [--json]
    python ghost_browser.py session save|load <name> [--tab ID] [--json]
    python ghost_browser.py window [--size WxH] [--position XxY] [--json]
    python ghost_browser.py download <url> [--output PATH] [--json]
    python ghost_browser.py upload <file-path> [--selector SEL] [--tab ID] [--json]
    python ghost_browser.py pdf [--output PATH] [--landscape] [--tab ID] [--json]
    python ghost_browser.py network-log [--filter URL] [--limit N] [--clear] [--json]
    python ghost_browser.py console-log [--level error] [--limit N] [--clear] [--json]
    python ghost_browser.py profile list|create|delete|default|clone [--json]
    python ghost_browser.py save-cookies [--file PATH] [--json]
    python ghost_browser.py load-cookies <file> [--json]
    python ghost_browser.py cf-solve [--tab ID] [--all] [--json]
"""

import argparse
import asyncio
import json
import os
import random
import signal
import shutil
import sys
import time
import socket
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import base64
import urllib.parse
import urllib.request
import urllib.error

# State file locations
STATE_DIR = Path.home() / ".openclaw" / "workspace" / "SKILLS" / "ghost-browser" / "state"
PID_FILE = STATE_DIR / "browser.pid"
STATE_FILE = STATE_DIR / "browser.json"
LOG_FILE = STATE_DIR / "browser.log"
PROFILES_DIR = STATE_DIR / "profiles"
PROFILES_CONFIG = STATE_DIR / "profiles.json"
SESSIONS_DIR = STATE_DIR / "sessions"

DEFAULT_PORT = 9222
DEFAULT_PROFILE_NAME = "default"


def ensure_state_dir():
    """Ensure state directory exists."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def log(message: str, level: str = "INFO"):
    """Log message to file and stderr."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {message}"
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except IOError:
        pass
    if level == "ERROR":
        print(line, file=sys.stderr)


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def read_state() -> Optional[Dict[str, Any]]:
    """Read current browser state from file."""
    if not STATE_FILE.exists():
        return None
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def write_state(state: Dict[str, Any]):
    """Write browser state to file."""
    ensure_state_dir()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def clear_state():
    """Remove state files."""
    for f in [PID_FILE, STATE_FILE]:
        if f.exists():
            f.unlink()


def get_running_pid() -> Optional[int]:
    """Get PID of running browser if any."""
    if not PID_FILE.exists():
        return None
    try:
        pid = int(PID_FILE.read_text().strip())
        if is_process_running(pid):
            return pid
        # Stale PID file
        PID_FILE.unlink()
        return None
    except (ValueError, IOError):
        return None


def check_cdp_endpoint(port: int, timeout: float = 2.0) -> bool:
    """Check if CDP endpoint is responsive."""
    try:
        url = f"http://127.0.0.1:{port}/json/version"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
            return "webSocketDebuggerUrl" in data
    except (urllib.error.URLError, json.JSONDecodeError, socket.timeout, ConnectionRefusedError, OSError):
        return False


def get_open_tabs(port: int, timeout: float = 2.0) -> list:
    """Fetch all open tabs from CDP /json/list endpoint."""
    try:
        url = f"http://127.0.0.1:{port}/json/list"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            tabs = json.loads(resp.read().decode())
            return [
                {
                    "id": tab.get("id"),
                    "title": tab.get("title", ""),
                    "url": tab.get("url", ""),
                    "type": tab.get("type", ""),
                }
                for tab in tabs
                if tab.get("type") == "page"
            ]
    except (urllib.error.URLError, json.JSONDecodeError, socket.timeout, ConnectionRefusedError, OSError):
        return []


def normalize_url(url: str) -> str:
    """Normalize URL for comparison (strip trailing slash, lowercase domain)."""
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") if parsed.path != "/" else ""
    return urlunparse((parsed.scheme.lower(), netloc, path, "", parsed.query, ""))


def find_tab_by_url(port: int, url: str, exact: bool = False) -> Optional[Dict]:
    """Find an existing tab by URL."""
    tabs = get_open_tabs(port)
    target_normalized = normalize_url(url)
    for tab in tabs:
        tab_url = tab.get("url", "")
        if exact:
            if tab_url == url:
                return tab
        else:
            if normalize_url(tab_url) == target_normalized:
                return tab
    return None


def update_mcporter_config(port: int, restore: bool = False):
    """No-op. Previously modified mcporter.json — removed for safety.
    To manually integrate with MCP, add to your mcporter.json:
    {"mcpServers": {"chrome-devtools": {"command": "npx", "args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl=http://127.0.0.1:<port>"]}}}
    """
    pass


# ---------------------------------------------------------------------------
# Profile Management
# ---------------------------------------------------------------------------

def get_profile_dir(name: str) -> Path:
    """Get the directory path for a named profile."""
    return PROFILES_DIR / name


def read_profiles_config() -> Dict[str, Any]:
    """Read profiles configuration."""
    if not PROFILES_CONFIG.exists():
        return {"default_profile": DEFAULT_PROFILE_NAME}
    try:
        with open(PROFILES_CONFIG) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"default_profile": DEFAULT_PROFILE_NAME}


def write_profiles_config(config: Dict[str, Any]):
    """Write profiles configuration."""
    ensure_state_dir()
    with open(PROFILES_CONFIG, "w") as f:
        json.dump(config, f, indent=2)


def migrate_legacy_profile():
    """Migrate legacy chrome-profile to profiles/default if needed."""
    legacy_dir = STATE_DIR / "chrome-profile"
    default_profile = get_profile_dir(DEFAULT_PROFILE_NAME)

    if legacy_dir.exists() and not default_profile.exists():
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(legacy_dir), str(default_profile))
        log(f"Migrated legacy chrome-profile to profiles/{DEFAULT_PROFILE_NAME}")

    if not PROFILES_CONFIG.exists():
        write_profiles_config({"default_profile": DEFAULT_PROFILE_NAME})


def resolve_profile_dir(profile_name: Optional[str]) -> Path:
    """Resolve profile name to directory path. Creates profiles dir if needed."""
    migrate_legacy_profile()
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    if profile_name is None:
        config = read_profiles_config()
        profile_name = config.get("default_profile", DEFAULT_PROFILE_NAME)

    return get_profile_dir(profile_name)


def get_dir_size(path: Path) -> int:
    """Get total size of directory in bytes."""
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
    except OSError:
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


# ---------------------------------------------------------------------------
# Cloudflare Challenge Detection JavaScript
# ---------------------------------------------------------------------------

CF_DETECT_JS = """
(() => {
    const result = { found: false, solved: false, challenges: [] };

    // Check if already solved: cf-turnstile-response input has a value
    const responseInput = document.querySelector('input[name="cf-turnstile-response"]');
    if (responseInput && responseInput.value && responseInput.value.length > 0) {
        result.found = true;
        result.solved = true;
        return result;
    }

    // Detect Turnstile iframes
    const iframes = document.querySelectorAll(
        'iframe[src*="challenges.cloudflare.com"], iframe[src*="turnstile"]'
    );
    for (const iframe of iframes) {
        const rect = iframe.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
            result.found = true;
            result.challenges.push({
                type: "turnstile_iframe",
                x: rect.x, y: rect.y,
                width: rect.width, height: rect.height,
                src: iframe.src || ""
            });
        }
    }

    // Detect .cf-turnstile / [data-cf-turnstile] / [data-sitekey] widget containers
    const widgets = document.querySelectorAll('.cf-turnstile, [data-cf-turnstile], [data-sitekey]');
    for (const widget of widgets) {
        const rect = widget.getBoundingClientRect();
        // Check for an iframe inside the widget container
        const innerIframe = widget.querySelector('iframe');
        if (innerIframe) {
            const iRect = innerIframe.getBoundingClientRect();
            if (iRect.width > 0 && iRect.height > 0) {
                result.found = true;
                result.challenges.push({
                    type: "turnstile_iframe",
                    x: iRect.x, y: iRect.y,
                    width: iRect.width, height: iRect.height,
                    src: innerIframe.src || ""
                });
            }
        } else if (rect.width > 0 && rect.height > 0) {
            result.found = true;
            result.challenges.push({
                type: "widget_container",
                x: rect.x, y: rect.y,
                width: rect.width, height: rect.height
            });
        }
    }

    // Detect full-page interstitial by title or body text
    const title = document.title || "";
    const bodyText = (document.body && document.body.innerText) || "";
    const interstitialPatterns = [
        "just a moment", "checking your browser",
        "verify you are human", "attention required",
        "please wait", "cloudflare"
    ];
    const lowerTitle = title.toLowerCase();
    const lowerBody = bodyText.toLowerCase().substring(0, 2000);
    const isInterstitial = interstitialPatterns.some(
        p => lowerTitle.includes(p) || lowerBody.includes(p)
    );

    if (isInterstitial && !result.found) {
        // Look for a challenge iframe on the interstitial page
        const allIframes = document.querySelectorAll('iframe');
        for (const iframe of allIframes) {
            const src = iframe.src || "";
            if (src.includes("challenges.cloudflare.com") || src.includes("turnstile")) {
                const rect = iframe.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    result.found = true;
                    result.challenges.push({
                        type: "challenge_iframe",
                        x: rect.x, y: rect.y,
                        width: rect.width, height: rect.height,
                        src: src
                    });
                }
            }
        }
        // If no clickable iframe found, it may be a waiting/auto-resolving challenge
        if (!result.found) {
            result.found = true;
            result.challenges.push({ type: "challenge_waiting" });
        }
    }

    // Detect reCAPTCHA v2 (image selection / "I'm not a robot" checkbox)
    const recaptchaFrames = document.querySelectorAll(
        'iframe[src*="google.com/recaptcha"], iframe[src*="recaptcha/api2"], iframe[src*="recaptcha/enterprise"]'
    );
    for (const iframe of recaptchaFrames) {
        const rect = iframe.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
            result.found = true;
            result.has_recaptcha = true;
            result.challenges.push({
                type: "recaptcha_v2",
                x: rect.x, y: rect.y,
                width: rect.width, height: rect.height,
                src: iframe.src || ""
            });
        }
    }
    // Also detect .g-recaptcha container
    const gRecaptcha = document.querySelectorAll('.g-recaptcha, [data-sitekey]:not([data-cf-turnstile])');
    for (const el of gRecaptcha) {
        if (el.querySelector('iframe[src*="recaptcha"]')) {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0 && !result.has_recaptcha) {
                result.found = true;
                result.has_recaptcha = true;
                result.challenges.push({
                    type: "recaptcha_v2",
                    x: rect.x, y: rect.y,
                    width: rect.width, height: rect.height
                });
            }
        }
    }

    return JSON.stringify(result);
})()
"""


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------

class _RecaptchaRestartSignal(Exception):
    """Raised inside cf_scanner_loop to signal that a browser restart is needed
    to evade a persistent reCAPTCHA v2 challenge."""
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"reCAPTCHA restart needed for: {url}")


# ---------------------------------------------------------------------------
# Command Server (IPC between CLI and daemon)
# ---------------------------------------------------------------------------

class CommandServer:
    """Asyncio HTTP server embedded in the daemon for receiving CLI commands."""

    # MouseEvent/PointerEvent screenX/screenY patcher — injected via CDP.
    # Chrome 145+ blocks --load-extension on branded builds, so we inject via
    # Page.addScriptToEvaluateOnNewDocument instead of a content-script extension.
    # Fixes Chromium bug crbug.com/40280325 where CDP Input.dispatchMouseEvent
    # sets screenX/screenY equal to clientX/clientY, which Cloudflare Turnstile
    # detects as synthetic (screenY < 100).
    _MOUSE_EVENT_PATCH_JS = """try {
  var _OrigME = window.MouseEvent;
  window.MouseEvent = function(type, init) {
    if (init && typeof init === 'object') {
      var cx = init.clientX || 0;
      var cy = init.clientY || 0;
      var offX = window.screenX + (window.outerWidth - window.innerWidth);
      var offY = window.screenY + (window.outerHeight - window.innerHeight);
      if (window.screenX === 0 && window.screenY === 0) { offX = 100; offY = 200; }
      if (!init.hasOwnProperty('screenX') || init.screenX === cx) { init.screenX = offX + cx; }
      if (!init.hasOwnProperty('screenY') || init.screenY === cy) { init.screenY = offY + cy; }
    }
    return new _OrigME(type, init);
  };
  window.MouseEvent.prototype = _OrigME.prototype;
} catch(e) {}
try {
  var _OrigPE = window.PointerEvent;
  window.PointerEvent = function(type, init) {
    if (init && typeof init === 'object') {
      var cx = init.clientX || 0;
      var cy = init.clientY || 0;
      var offX = window.screenX + (window.outerWidth - window.innerWidth);
      var offY = window.screenY + (window.outerHeight - window.innerHeight);
      if (window.screenX === 0 && window.screenY === 0) { offX = 100; offY = 200; }
      if (!init.hasOwnProperty('screenX') || init.screenX === cx) { init.screenX = offX + cx; }
      if (!init.hasOwnProperty('screenY') || init.screenY === cy) { init.screenY = offY + cy; }
    }
    return new _OrigPE(type, init);
  };
  window.PointerEvent.prototype = _OrigPE.prototype;
} catch(e) {}"""

    # Extensions handled via CDP injection rather than chrome://extensions loading.
    _CDP_INJECTED_EXTENSIONS = {"cdp-input-fix"}

    def __init__(self, browser):
        self.browser = browser
        self.server = None
        self.port = 0
        self.active_tab_id = None  # Track the last navigated/activated tab
        self._cf_cooldowns = {}  # tab_id -> last_attempt timestamp for CF scanner
        self._cf_cooldown_secs = {}  # tab_id -> dynamic cooldown seconds for CF scanner
        self._recaptcha_attempts = {}  # tab_id -> number of evasion attempts
        self._recaptcha_restart_url = None  # URL to re-navigate after restart
        self._network_log = []  # Circular buffer, max 200 entries
        self._console_log = []  # Circular buffer, max 200 entries
        self._injected_tabs = set()  # tab IDs that have the mouse patch injected
        self._loaded_extensions = {}  # folder_name -> {id, name, path}
        self.handlers = {
            "navigate": self._handle_navigate,
            "screenshot": self._handle_screenshot,
            "content": self._handle_content,
            "readable": self._handle_readable,
            "elements": self._handle_elements,
            "page_summary": self._handle_page_summary,
            "eval": self._handle_eval,
            "click": self._handle_click,
            "type": self._handle_type,
            "interact": self._handle_interact,
            "fill_form": self._handle_fill_form,
            "find": self._handle_find,
            "scroll": self._handle_scroll,
            "wait": self._handle_wait,
            "wait_ready": self._handle_wait_ready,
            "hover": self._handle_hover,
            "close_tab": self._handle_close_tab,
            "activate_tab": self._handle_activate_tab,
            "cookies": self._handle_cookies,
            "set_cookie": self._handle_set_cookie,
            "clear_cookies": self._handle_clear_cookies,
            "storage": self._handle_storage,
            "session": self._handle_session,
            "window": self._handle_window,
            "download": self._handle_download,
            "upload": self._handle_upload,
            "pdf": self._handle_pdf,
            "network_log": self._handle_network_log,
            "console_log": self._handle_console_log,
            "save_cookies": self._handle_save_cookies,
            "load_cookies": self._handle_load_cookies,
            "cf_solve": self._handle_cf_solve,
            "load_extension": self._handle_load_extension,
            "unload_extension": self._handle_unload_extension,
            "list_loaded_extensions": self._handle_list_loaded_extensions,
        }

    async def start(self) -> int:
        """Start the command server on an auto-assigned port. Returns the port."""
        self.server = await asyncio.start_server(
            self._handle_connection, '127.0.0.1', 0
        )
        self.port = self.server.sockets[0].getsockname()[1]
        log(f"Command server started on port {self.port}")
        return self.port

    async def inject_mouse_patch(self, tab):
        """Inject the screenX/screenY patcher into a tab via CDP.

        Uses Page.addScriptToEvaluateOnNewDocument so it runs on every frame
        (including cross-origin Turnstile iframes) before any page scripts.
        Persists across navigations within the same tab.
        """
        tab_id = tab.target.target_id
        if tab_id in self._injected_tabs:
            return
        try:
            import nodriver.cdp.page as cdp_page
            # Page domain must be enabled for addScriptToEvaluateOnNewDocument
            await tab.send(cdp_page.enable())
            await tab.send(cdp_page.add_script_to_evaluate_on_new_document(
                source=self._MOUSE_EVENT_PATCH_JS,
            ))
            self._injected_tabs.add(tab_id)
            log(f"Injected MouseEvent patch on tab {tab_id[:8]}")
        except Exception as e:
            log(f"Warning: could not inject mouse patch on tab {tab_id[:8]}: {e}", "WARN")

    async def stop(self):
        """Stop the command server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            log("Command server stopped")

    def _list_available_tabs(self) -> List[Dict]:
        """List available tabs with id, title, url."""
        available = []
        for tab in (self.browser.tabs or []):
            tid = tab.target.target_id
            title = ""
            url = ""
            try:
                title = tab.target.title or ""
            except Exception:
                pass
            try:
                url = tab.target.url or ""
            except Exception:
                pass
            available.append({"id": tid, "title": title, "url": url})
        return available

    def _tab_not_found_error(self, tab_id: str) -> Dict:
        """Build an error dict when a tab ID isn't found, including available tabs."""
        available = self._list_available_tabs()
        return {
            "error": f"Tab not found: {tab_id}",
            "available_tabs": available,
            "hint": f"Use 'ghost-browser tabs' to list open tabs. {len(available)} tab(s) currently open."
        }

    async def _get_tab(self, tab_id: Optional[str] = None):
        """Get a tab by ID or return the best active tab. Returns None on failure."""
        tabs = self.browser.tabs
        if not tabs:
            return None

        if tab_id:
            for tab in tabs:
                if tab.target.target_id == tab_id:
                    return tab
            return None

        # Prefer the last navigated/activated tab
        if self.active_tab_id:
            for tab in tabs:
                if tab.target.target_id == self.active_tab_id:
                    return tab

        # Fallback: return the last tab (most recently opened)
        return tabs[-1]

    async def _get_tab_or_error(self, params: dict) -> tuple:
        """Get tab or return (None, error_dict). Returns (tab, None) on success."""
        tab_id = params.get("tab_id")
        tab = await self._get_tab(tab_id)
        if tab is not None:
            return tab, None
        if tab_id:
            return None, self._tab_not_found_error(tab_id)
        return None, {"error": "No tab available", "available_tabs": self._list_available_tabs()}

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle an incoming HTTP connection."""
        try:
            # Read the HTTP request
            request_data = await asyncio.wait_for(reader.read(65536), timeout=30)
            request_text = request_data.decode('utf-8', errors='replace')

            # Parse HTTP request minimally
            if '\r\n\r\n' in request_text:
                headers_part, body = request_text.split('\r\n\r\n', 1)
            elif '\n\n' in request_text:
                headers_part, body = request_text.split('\n\n', 1)
            else:
                body = ""
                headers_part = request_text

            request_line = headers_part.split('\n')[0].strip()
            parts = request_line.split(' ')

            if len(parts) < 2 or parts[0] != 'POST' or not parts[1].startswith('/command'):
                response = self._http_response(400, {"error": "Bad request"})
                writer.write(response)
                await writer.drain()
                writer.close()
                return

            # Check Content-Length for proper body reading
            content_length = 0
            for line in headers_part.split('\n'):
                if line.lower().strip().startswith('content-length:'):
                    try:
                        content_length = int(line.split(':', 1)[1].strip())
                    except ValueError:
                        pass

            # If we haven't read the full body yet, read more
            while len(body.encode('utf-8')) < content_length:
                more = await asyncio.wait_for(reader.read(65536), timeout=10)
                if not more:
                    break
                body += more.decode('utf-8', errors='replace')

            # Parse JSON body
            try:
                payload = json.loads(body) if body.strip() else {}
            except json.JSONDecodeError:
                response = self._http_response(400, {"error": "Invalid JSON"})
                writer.write(response)
                await writer.drain()
                writer.close()
                return

            command = payload.get("command", "")
            params = payload.get("params", {})

            handler = self.handlers.get(command)
            if not handler:
                response = self._http_response(404, {"error": f"Unknown command: {command}"})
            else:
                try:
                    result = await handler(params)
                    response = self._http_response(200, result)
                except Exception as e:
                    log(f"Command '{command}' failed: {e}", "ERROR")
                    response = self._http_response(500, {"error": str(e)})

            writer.write(response)
            await writer.drain()

        except asyncio.TimeoutError:
            try:
                writer.write(self._http_response(408, {"error": "Timeout"}))
                await writer.drain()
            except Exception:
                pass
        except Exception as e:
            log(f"Command server connection error: {e}", "ERROR")
            try:
                writer.write(self._http_response(500, {"error": str(e)}))
                await writer.drain()
            except Exception:
                pass
        finally:
            try:
                writer.close()
            except Exception:
                pass

    def _http_response(self, status: int, body: dict) -> bytes:
        """Build a raw HTTP response."""
        status_text = {200: "OK", 400: "Bad Request", 404: "Not Found",
                       408: "Timeout", 500: "Internal Server Error"}.get(status, "Error")
        body_bytes = json.dumps(body).encode('utf-8')
        header = (
            f"HTTP/1.1 {status} {status_text}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body_bytes)}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        return header.encode('utf-8') + body_bytes

    # -----------------------------------------------------------------------
    # Command handlers
    # -----------------------------------------------------------------------

    async def _handle_navigate(self, params: dict) -> dict:
        url = params.get("url", "")
        if not url:
            return {"error": "No URL provided"}

        force_new = params.get("force_new", False)
        tab_id = params.get("tab_id")

        try:
            tabs = self.browser.tabs or []

            if force_new or not tabs:
                # Open URL in a new tab via nodriver
                tab = await self.browser.get(url)
            else:
                # Navigate the specified or active tab
                tab = await self._get_tab(tab_id)
                if tab is None and tab_id:
                    return self._tab_not_found_error(tab_id)
                if tab is None:
                    tab = await self.browser.get(url)
                else:
                    await tab.get(url)

            # Track this as the active tab
            new_tab_id = tab.target.target_id
            self.active_tab_id = new_tab_id

            # Inject mouse event patch on new tabs
            await self.inject_mouse_patch(tab)

            # Wait a moment for page to start loading
            await asyncio.sleep(1)

            title = ""
            try:
                title = tab.target.title or ""
            except Exception:
                pass

            return {
                "status": "ok",
                "url": url,
                "tab_id": new_tab_id,
                "title": title,
                "message": f"Navigated to: {url}"
            }
        except Exception as e:
            return {"error": f"Navigate failed: {e}"}

    async def _handle_screenshot(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        output_path = params.get("output")
        if not output_path:
            output_path = str(STATE_DIR / f"screenshot_{int(time.time())}.png")

        try:
            await tab.save_screenshot(output_path)
            return {"status": "ok", "path": output_path}
        except Exception as e:
            return {"error": f"Screenshot failed: {e}"}

    async def _handle_content(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        try:
            content = await tab.get_content()
            return {"status": "ok", "content": content,
                    "hint": "Tip: Use 'readable' for LLM-friendly markdown, or 'elements' for interactive element list, or 'page-summary' for a compact overview."}
        except Exception as e:
            return {"error": f"Get content failed: {e}"}

    async def _handle_eval(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        js = params.get("js", "")
        if not js:
            return {"error": "No JavaScript provided"}

        try:
            result = await tab.evaluate(js)
            # Convert result to JSON-serializable form
            if result is None:
                return {"status": "ok", "result": None}
            try:
                json.dumps(result)
                return {"status": "ok", "result": result}
            except (TypeError, ValueError):
                return {"status": "ok", "result": str(result)}
        except Exception as e:
            return {"error": f"Eval failed: {e}"}

    async def _handle_click(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        selector = params.get("selector", "")
        if not selector:
            return {"error": "No selector provided"}

        try:
            element = await tab.find(selector, timeout=10)
            if element:
                await element.click()
                return {"status": "ok", "selector": selector,
                        "hint": "Tip: Use 'interact click \"Button Text\"' to click by visible text instead of CSS selectors."}
            return {"error": f"Element not found: {selector}",
                    "hint": "Tip: Use 'elements' to see all interactive elements, or 'interact click \"text\"' to click by visible text."}
        except Exception as e:
            return {"error": f"Click failed: {e}"}

    async def _handle_type(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        selector = params.get("selector", "")
        text = params.get("text", "")
        if not selector:
            return {"error": "No selector provided"}

        try:
            element = await tab.find(selector, timeout=10)
            if element:
                await element.send_keys(text)
                return {"status": "ok", "selector": selector, "text": text,
                        "hint": "Tip: Use 'interact type \"Label\" --type-text \"value\"' to type by visible text, or 'fill-form' to fill multiple fields at once."}
            return {"error": f"Element not found: {selector}",
                    "hint": "Tip: Use 'elements --form-only' to see form inputs, or 'fill-form' to auto-fill by field names."}
        except Exception as e:
            return {"error": f"Type failed: {e}"}

    async def _handle_find(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        selector = params.get("selector", "")
        if not selector:
            return {"error": "No selector provided"}

        try:
            elements = await tab.find_all(selector)
            results = []
            for el in elements:
                tag = el.tag_name if hasattr(el, 'tag_name') else el.node_name if hasattr(el, 'node_name') else ""
                text = ""
                try:
                    text = el.text if hasattr(el, 'text') else ""
                except Exception:
                    pass
                attrs = {}
                try:
                    if hasattr(el, 'attrs'):
                        attrs = dict(el.attrs) if el.attrs else {}
                    elif hasattr(el, 'attributes'):
                        attrs = dict(el.attributes) if el.attributes else {}
                except Exception:
                    pass
                results.append({"tag": tag, "text": text[:200], "attrs": attrs})
            return {"status": "ok", "count": len(results), "elements": results}
        except Exception as e:
            return {"error": f"Find failed: {e}"}

    async def _handle_scroll(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        direction = params.get("direction", "down")
        amount = params.get("amount")

        try:
            if amount is not None:
                # Scroll to specific Y position
                await tab.evaluate(f"window.scrollTo(0, {int(amount)})")
                return {"status": "ok", "action": "scroll_to", "y": int(amount)}
            elif direction == "up":
                await tab.evaluate("window.scrollBy(0, -500)")
                return {"status": "ok", "action": "scroll_up"}
            else:
                await tab.evaluate("window.scrollBy(0, 500)")
                return {"status": "ok", "action": "scroll_down"}
        except Exception as e:
            return {"error": f"Scroll failed: {e}"}

    async def _handle_wait(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        selector = params.get("selector", "")
        timeout = params.get("timeout", 30)
        if not selector:
            return {"error": "No selector provided"}

        try:
            element = await tab.find(selector, timeout=timeout)
            if element:
                tag = element.tag_name if hasattr(element, 'tag_name') else ""
                text = ""
                try:
                    text = element.text if hasattr(element, 'text') else ""
                except Exception:
                    pass
                return {"status": "ok", "found": True, "tag": tag, "text": text[:200]}
            return {"status": "ok", "found": False}
        except Exception as e:
            return {"error": f"Wait failed: {e}"}

    async def _handle_close_tab(self, params: dict) -> dict:
        tab_id = params.get("tab_id")
        if not tab_id:
            return {"error": "No tab ID provided", "available_tabs": self._list_available_tabs()}

        for tab in self.browser.tabs:
            if tab.target.target_id == tab_id:
                try:
                    await tab.close()
                    return {"status": "ok", "closed": tab_id}
                except Exception as e:
                    return {"error": f"Close tab failed: {e}"}

        return self._tab_not_found_error(tab_id)

    async def _handle_activate_tab(self, params: dict) -> dict:
        tab_id = params.get("tab_id")
        if not tab_id:
            return {"error": "No tab ID provided", "available_tabs": self._list_available_tabs()}

        for tab in self.browser.tabs:
            if tab.target.target_id == tab_id:
                try:
                    await tab.activate()
                    self.active_tab_id = tab_id
                    return {"status": "ok", "activated": tab_id}
                except Exception as e:
                    return {"error": f"Activate tab failed: {e}"}

        return self._tab_not_found_error(tab_id)

    async def _handle_cookies(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        domain = params.get("domain")

        try:
            import nodriver.cdp.network as net
            result = await tab.send(net.get_cookies())
            cookies = []
            for cookie in result:
                c = {
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                    "secure": cookie.secure,
                    "http_only": cookie.http_only,
                }
                if domain and domain not in cookie.domain:
                    continue
                cookies.append(c)
            return {"status": "ok", "count": len(cookies), "cookies": cookies}
        except Exception as e:
            return {"error": f"Get cookies failed: {e}"}

    async def _handle_set_cookie(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        name = params.get("name", "")
        value = params.get("value", "")
        domain = params.get("domain", "")

        if not name:
            return {"error": "Cookie name required"}

        try:
            import nodriver.cdp.network as net
            await tab.send(net.set_cookie(
                name=name,
                value=value,
                domain=domain if domain else None,
                path="/",
            ))
            return {"status": "ok", "name": name, "value": value, "domain": domain}
        except Exception as e:
            return {"error": f"Set cookie failed: {e}"}

    async def _handle_clear_cookies(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        try:
            import nodriver.cdp.network as net
            await tab.send(net.clear_browser_cookies())
            return {"status": "ok", "message": "All cookies cleared"}
        except Exception as e:
            return {"error": f"Clear cookies failed: {e}"}

    async def _handle_window(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        size = params.get("size")
        position = params.get("position")

        try:
            if size:
                parts = size.split("x")
                if len(parts) == 2:
                    w, h = int(parts[0]), int(parts[1])
                    await tab.set_window_size(w, h)
            if position:
                parts = position.split("x")
                if len(parts) == 2:
                    x, y = int(parts[0]), int(parts[1])
                    await tab.set_window_position(x, y)

            return {"status": "ok", "size": size, "position": position}
        except Exception as e:
            return {"error": f"Window resize failed: {e}"}

    async def _handle_download(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        url = params.get("url", "")
        output = params.get("output")
        if not url:
            return {"error": "No URL provided"}

        if not output:
            # Extract filename from URL or use timestamp
            from urllib.parse import urlparse
            parsed = urlparse(url)
            filename = Path(parsed.path).name or f"download_{int(time.time())}"
            output = str(STATE_DIR / filename)

        try:
            # Use JavaScript to fetch and convert to base64
            js = f"""
            (async () => {{
                const resp = await fetch("{url}");
                const blob = await resp.blob();
                const reader = new FileReader();
                return new Promise((resolve, reject) => {{
                    reader.onload = () => resolve(reader.result.split(',')[1]);
                    reader.onerror = reject;
                    reader.readAsDataURL(blob);
                }});
            }})()
            """
            b64_data = await tab.evaluate(js, await_promise=True)
            if b64_data:
                import base64
                data = base64.b64decode(b64_data)
                with open(output, 'wb') as f:
                    f.write(data)
                return {"status": "ok", "path": output, "size": len(data)}
            return {"error": "Download returned no data"}
        except Exception as e:
            return {"error": f"Download failed: {e}"}

    async def _handle_save_cookies(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        output_file = params.get("file")
        if not output_file:
            output_file = str(STATE_DIR / f"cookies_{int(time.time())}.json")

        try:
            import nodriver.cdp.network as net
            result = await tab.send(net.get_cookies())
            cookies = []
            for cookie in result:
                cookies.append({
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                    "secure": cookie.secure,
                    "http_only": cookie.http_only,
                    "expires": cookie.expires if hasattr(cookie, 'expires') else None,
                    "same_site": str(cookie.same_site) if hasattr(cookie, 'same_site') and cookie.same_site else None,
                })
            with open(output_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            return {"status": "ok", "path": output_file, "count": len(cookies)}
        except Exception as e:
            return {"error": f"Save cookies failed: {e}"}

    async def _handle_load_cookies(self, params: dict) -> dict:
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        input_file = params.get("file", "")
        if not input_file or not Path(input_file).exists():
            return {"error": f"Cookie file not found: {input_file}"}

        try:
            import nodriver.cdp.network as net
            with open(input_file) as f:
                cookies = json.load(f)

            loaded = 0
            for cookie in cookies:
                try:
                    await tab.send(net.set_cookie(
                        name=cookie["name"],
                        value=cookie["value"],
                        domain=cookie.get("domain"),
                        path=cookie.get("path", "/"),
                        secure=cookie.get("secure", False),
                        http_only=cookie.get("http_only", False),
                    ))
                    loaded += 1
                except Exception:
                    pass

            return {"status": "ok", "loaded": loaded, "total": len(cookies)}
        except Exception as e:
            return {"error": f"Load cookies failed: {e}"}

    # -------------------------------------------------------------------
    # LLM-friendly features
    # -------------------------------------------------------------------

    async def _handle_readable(self, params: dict) -> dict:
        """Convert page content to LLM-friendly markdown."""
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        max_length = params.get("max_length", 10000)

        js = """
(() => {
    const SKIP_TAGS = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'SVG', 'PATH', 'LINK', 'META']);
    const SKIP_ROLES = new Set(['navigation', 'banner', 'contentinfo', 'complementary']);
    const SKIP_CLASSES = /\\b(nav|sidebar|footer|header|menu|ad|advertisement|social|share|comment-form|cookie)\\b/i;

    function isVisible(el) {
        if (!el || !el.getBoundingClientRect) return true;
        try {
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
        } catch(e) { return true; }
    }

    function walkNode(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            const t = node.textContent.replace(/\\s+/g, ' ').trim();
            return t || '';
        }
        if (node.nodeType !== Node.ELEMENT_NODE) return '';

        const el = node;
        const tag = el.tagName;
        if (SKIP_TAGS.has(tag)) return '';
        if (!isVisible(el)) return '';

        const role = el.getAttribute('role');
        if (role && SKIP_ROLES.has(role)) return '';

        const cls = el.className;
        if (typeof cls === 'string' && SKIP_CLASSES.test(cls)) return '';

        // Handle TABLE specially to avoid double-processing
        if (tag === 'TABLE') {
            const rows = el.querySelectorAll('tr');
            if (!rows.length) return '';
            let lines = [];
            let isFirst = true;
            for (const row of rows) {
                const cells = Array.from(row.querySelectorAll('th, td'))
                    .map(c => c.textContent.trim().replace(/\\|/g, '\\\\|').replace(/\\n/g, ' '));
                if (!cells.length) continue;
                lines.push('| ' + cells.join(' | ') + ' |');
                if (isFirst) {
                    lines.push('| ' + cells.map(() => '---').join(' | ') + ' |');
                    isFirst = false;
                }
            }
            return lines.join('\\n');
        }

        let children = Array.from(el.childNodes).map(walkNode).filter(Boolean);

        switch(tag) {
            case 'H1': return '\\n# ' + children.join(' ') + '\\n';
            case 'H2': return '\\n## ' + children.join(' ') + '\\n';
            case 'H3': return '\\n### ' + children.join(' ') + '\\n';
            case 'H4': return '\\n#### ' + children.join(' ') + '\\n';
            case 'H5': return '\\n##### ' + children.join(' ') + '\\n';
            case 'H6': return '\\n###### ' + children.join(' ') + '\\n';
            case 'P': return children.join(' ') + '\\n\\n';
            case 'BR': return '\\n';
            case 'A': {
                const href = el.getAttribute('href') || '';
                const text = children.join(' ');
                return href && !href.startsWith('javascript:') ? '[' + text + '](' + href + ')' : text;
            }
            case 'IMG': {
                const alt = el.getAttribute('alt') || '';
                const src = el.getAttribute('src') || '';
                return '![' + alt + '](' + src + ')';
            }
            case 'STRONG': case 'B': return '**' + children.join(' ') + '**';
            case 'EM': case 'I': return '*' + children.join(' ') + '*';
            case 'CODE': return '`' + children.join(' ') + '`';
            case 'PRE': return '\\n```\\n' + children.join('\\n') + '\\n```\\n';
            case 'LI': return '- ' + children.join(' ');
            case 'UL': case 'OL': return '\\n' + children.join('\\n') + '\\n';
            case 'BLOCKQUOTE': return '\\n> ' + children.join(' ') + '\\n';
            case 'HR': return '\\n---\\n';
            case 'DIV': case 'SECTION': case 'ARTICLE': case 'MAIN': case 'FORM':
                return children.join('\\n');
            case 'SPAN': return children.join(' ');
            default: return children.join(' ');
        }
    }

    const title = document.title || '';
    const url = window.location.href;
    let markdown = walkNode(document.body || document.documentElement);
    markdown = markdown.replace(/\\n{3,}/g, '\\n\\n').trim();
    return JSON.stringify({title: title, url: url, markdown: markdown});
})()
"""
        try:
            result = await tab.evaluate(js)
            if isinstance(result, str):
                data = json.loads(result)
            elif isinstance(result, dict):
                data = result
            else:
                return {"error": "Unexpected result from readable JS"}

            md = data.get("markdown", "")
            truncated = False
            if len(md) > max_length:
                md = md[:max_length] + "\n\n... [truncated]"
                truncated = True

            return {
                "status": "ok",
                "title": data.get("title", ""),
                "url": data.get("url", ""),
                "markdown": md,
                "length": len(md),
                "truncated": truncated,
            }
        except Exception as e:
            return {"error": f"Readable failed: {e}"}

    async def _handle_elements(self, params: dict) -> dict:
        """List all interactive elements on the page in a compact format for LLMs."""
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        form_only = params.get("form_only", False)
        max_elements = params.get("limit", 100)

        js = """
((formOnly, maxElements) => {
    const results = [];
    let idx = 0;

    function addElement(el, type, extra) {
        if (idx >= maxElements) return;
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) return;
        try {
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden') return;
        } catch(e) {}

        const text = (el.innerText || el.textContent || '').trim().replace(/\\s+/g, ' ').substring(0, 80);
        const entry = {idx: idx++, type, text};

        if (el.tagName === 'A') {
            entry.href = (el.getAttribute('href') || '').substring(0, 120);
        }
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT') {
            const inputType = el.getAttribute('type') || (el.tagName === 'TEXTAREA' ? 'textarea' : el.tagName === 'SELECT' ? 'select' : 'text');
            entry.input_type = inputType;
            if (el.getAttribute('name')) entry.name = el.getAttribute('name');
            if (el.getAttribute('placeholder')) entry.placeholder = el.getAttribute('placeholder');
            if (el.value && inputType !== 'password') entry.value = el.value.substring(0, 50);
            if (el.tagName === 'SELECT') {
                entry.options = Array.from(el.options).slice(0, 10).map(o => o.textContent.trim().substring(0, 40));
            }
        }
        if (el.getAttribute('aria-label')) entry.aria_label = el.getAttribute('aria-label');
        if (el.getAttribute('role')) entry.role = el.getAttribute('role');
        if (el.disabled) entry.disabled = true;

        // Find associated label
        const id = el.id;
        if (id) {
            const label = document.querySelector('label[for="' + CSS.escape(id) + '"]');
            if (label) entry.label = label.textContent.trim().substring(0, 60);
        }
        if (!entry.label) {
            const parentLabel = el.closest('label');
            if (parentLabel) entry.label = parentLabel.textContent.trim().substring(0, 60);
        }

        Object.assign(entry, extra || {});
        results.push(entry);
    }

    if (!formOnly) {
        // Links
        document.querySelectorAll('a[href]').forEach(el => {
            const href = el.getAttribute('href') || '';
            if (href && !href.startsWith('javascript:') && !href.startsWith('#')) {
                addElement(el, 'link', {});
            }
        });

        // Buttons (non-form)
        document.querySelectorAll('button, [role=button], input[type=button], input[type=reset]').forEach(el => {
            addElement(el, 'button', {});
        });
    }

    // Form inputs
    document.querySelectorAll('input:not([type=hidden]):not([type=button]):not([type=reset]), textarea, select').forEach(el => {
        addElement(el, 'input', {});
    });

    // Submit buttons
    document.querySelectorAll('button[type=submit], input[type=submit]').forEach(el => {
        addElement(el, 'submit', {});
    });

    if (!formOnly) {
        // Clickable elements with onclick or role
        document.querySelectorAll('[onclick], [role=link], [role=tab], [role=menuitem]').forEach(el => {
            // Skip if already captured
            if (['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName)) return;
            addElement(el, 'clickable', {});
        });
    }

    return JSON.stringify(results);
})""" + f"({str(form_only).lower()}, {max_elements})"

        try:
            result = await tab.evaluate(js)
            if isinstance(result, str):
                elements = json.loads(result)
            elif isinstance(result, list):
                elements = result
            else:
                elements = []

            # Build compact text representation
            lines = []
            for el in elements:
                idx = el.get("idx", "?")
                etype = el.get("type", "?")
                text = el.get("text", "")

                if etype == "link":
                    href = el.get("href", "")
                    display = text or href
                    lines.append(f"[{idx}] link \"{display}\"" + (f" → {href}" if href and href != text else ""))

                elif etype == "button" or etype == "submit" or etype == "clickable":
                    label = text or el.get("aria_label", "") or el.get("value", "") or etype
                    prefix = "submit" if etype == "submit" else "button" if etype == "button" else "clickable"
                    lines.append(f"[{idx}] {prefix} \"{label}\"")

                elif etype == "input":
                    itype = el.get("input_type", "text")
                    label = el.get("label", "") or el.get("placeholder", "") or el.get("name", "") or el.get("aria_label", "")
                    parts = [f"[{idx}] input[{itype}]"]
                    if label:
                        parts.append(f"\"{label}\"")
                    if el.get("value"):
                        parts.append(f"value=\"{el['value']}\"")
                    if el.get("options"):
                        opts = ", ".join(el["options"][:5])
                        parts.append(f"options=[{opts}]")
                    if el.get("disabled"):
                        parts.append("(disabled)")
                    lines.append(" ".join(parts))
                else:
                    lines.append(f"[{idx}] {etype} \"{text}\"")

            compact = "\n".join(lines)

            return {
                "status": "ok",
                "count": len(elements),
                "elements": elements,
                "compact": compact,
            }
        except Exception as e:
            return {"error": f"Elements failed: {e}"}

    async def _handle_page_summary(self, params: dict) -> dict:
        """Get a minimal page summary for LLM situational awareness."""
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        js = """
(() => {
    const title = document.title || '';
    const url = window.location.href;

    // Count interactive elements
    const links = document.querySelectorAll('a[href]').length;
    const buttons = document.querySelectorAll('button, [role=button], input[type=button], input[type=submit]').length;
    const inputs = document.querySelectorAll('input:not([type=hidden]), textarea, select').length;
    const forms = document.querySelectorAll('form').length;
    const images = document.querySelectorAll('img').length;
    const iframes = document.querySelectorAll('iframe').length;

    // Get visible text preview (first ~500 chars of meaningful content)
    const body = document.body;
    let textPreview = '';
    if (body) {
        const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT, {
            acceptNode: function(node) {
                const parent = node.parentElement;
                if (!parent) return NodeFilter.FILTER_REJECT;
                const tag = parent.tagName;
                if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'SVG'].includes(tag)) return NodeFilter.FILTER_REJECT;
                try {
                    const style = window.getComputedStyle(parent);
                    if (style.display === 'none' || style.visibility === 'hidden') return NodeFilter.FILTER_REJECT;
                } catch(e) {}
                const text = node.textContent.trim();
                if (text.length < 2) return NodeFilter.FILTER_REJECT;
                return NodeFilter.FILTER_ACCEPT;
            }
        });

        const chunks = [];
        let totalLen = 0;
        while (walker.nextNode() && totalLen < 500) {
            const t = walker.currentNode.textContent.trim().replace(/\\s+/g, ' ');
            if (t) {
                chunks.push(t);
                totalLen += t.length;
            }
        }
        textPreview = chunks.join(' ').substring(0, 500);
    }

    // Detect page state
    const readyState = document.readyState;
    const hasCF = !!(document.querySelector('iframe[src*="challenges.cloudflare.com"]') ||
                     document.querySelector('.cf-turnstile'));
    const hasLogin = !!(document.querySelector('input[type=password]') ||
                       document.querySelector('form[action*=login]') ||
                       document.querySelector('form[action*=signin]'));

    // Meta description
    const metaDesc = (document.querySelector('meta[name=description]') || {}).content || '';

    return JSON.stringify({
        title, url, readyState,
        meta_description: metaDesc.substring(0, 200),
        counts: {links, buttons, inputs, forms, images, iframes},
        flags: {has_cloudflare: hasCF, has_login_form: hasLogin},
        text_preview: textPreview
    });
})()
"""
        try:
            result = await tab.evaluate(js)
            if isinstance(result, str):
                data = json.loads(result)
            elif isinstance(result, dict):
                data = result
            else:
                return {"error": "Unexpected page-summary result"}

            # Build compact summary
            counts = data.get("counts", {})
            flags = data.get("flags", {})
            lines = [
                f"Title: {data.get('title', '(none)')}",
                f"URL: {data.get('url', '')}",
                f"State: {data.get('readyState', '?')}",
            ]
            if data.get("meta_description"):
                lines.append(f"Description: {data['meta_description']}")

            parts = []
            for k, v in counts.items():
                if v > 0:
                    parts.append(f"{v} {k}")
            if parts:
                lines.append(f"Contains: {', '.join(parts)}")

            flag_parts = []
            if flags.get("has_cloudflare"):
                flag_parts.append("Cloudflare challenge detected")
            if flags.get("has_login_form"):
                flag_parts.append("Login form present")
            if flag_parts:
                lines.append(f"Flags: {', '.join(flag_parts)}")

            preview = data.get("text_preview", "")
            if preview:
                lines.append(f"Preview: {preview[:300]}")

            data["compact"] = "\n".join(lines)
            data["status"] = "ok"
            return data

        except Exception as e:
            return {"error": f"Page summary failed: {e}"}

    async def _find_element_by_text(self, tab, text: str, index: int = 0) -> dict:
        """Find an interactive element by visible text. Returns match info or error."""
        js = """
((targetText) => {
    const selectors = 'a, button, input, select, textarea, [role=button], [role=link], [onclick]';
    const elements = Array.from(document.querySelectorAll(selectors));

    function getMatchScore(el) {
        const lower = targetText.toLowerCase();

        const innerText = (el.innerText || el.textContent || '').trim().toLowerCase();
        if (innerText === lower) return 100;
        if (innerText.includes(lower)) return 80;

        const placeholder = (el.getAttribute('placeholder') || '').toLowerCase();
        if (placeholder === lower) return 90;
        if (placeholder.includes(lower)) return 70;

        const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
        if (ariaLabel === lower) return 90;
        if (ariaLabel.includes(lower)) return 70;

        const title = (el.getAttribute('title') || '').toLowerCase();
        if (title === lower) return 85;
        if (title.includes(lower)) return 65;

        const id = el.id;
        if (id) {
            const label = document.querySelector('label[for="' + CSS.escape(id) + '"]');
            if (label) {
                const labelText = label.textContent.trim().toLowerCase();
                if (labelText === lower) return 85;
                if (labelText.includes(lower)) return 65;
            }
        }
        const parentLabel = el.closest('label');
        if (parentLabel) {
            const labelText = parentLabel.textContent.trim().toLowerCase();
            if (labelText.includes(lower)) return 60;
        }

        const value = (el.getAttribute('value') || '').toLowerCase();
        if (value === lower) return 80;
        if (value.includes(lower)) return 60;

        return 0;
    }

    const matches = elements
        .map(el => ({el, score: getMatchScore(el)}))
        .filter(m => m.score > 0)
        .sort((a, b) => b.score - a.score);

    return JSON.stringify({
        count: matches.length,
        matches: matches.slice(0, 10).map(m => {
            const rect = m.el.getBoundingClientRect();
            return {
                tag: m.el.tagName,
                type: m.el.getAttribute('type') || '',
                text: (m.el.innerText || m.el.textContent || '').trim().substring(0, 100),
                score: m.score,
                rect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height},
                cx: rect.x + rect.width / 2,
                cy: rect.y + rect.height / 2
            };
        })
    });
})""" + f'("{text.replace(chr(34), chr(92)+chr(34))}")'

        try:
            result = await tab.evaluate(js)
            if isinstance(result, str):
                return json.loads(result)
            if isinstance(result, dict):
                return result
            return {"count": 0, "matches": []}
        except Exception as e:
            return {"count": 0, "matches": [], "error": str(e)}

    async def _handle_interact(self, params: dict) -> dict:
        """Click or type by visible text instead of CSS selectors."""
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        action = params.get("action", "click")
        text = params.get("text", "")
        input_text = params.get("input_text", "")
        index = params.get("index", 0)

        if not text:
            return {"error": "No text provided to match"}
        if action not in ("click", "type"):
            return {"error": f"Invalid action: {action}. Use 'click' or 'type'"}
        if action == "type" and not input_text:
            return {"error": "No input_text provided for type action"}

        search = await self._find_element_by_text(tab, text, index)
        if search.get("error"):
            return {"error": f"Element search failed: {search['error']}"}
        if search.get("count", 0) == 0:
            return {"error": f"No element found matching text: '{text}'", "matches": []}

        matches = search.get("matches", [])
        if index >= len(matches):
            return {"error": f"Index {index} out of range (found {len(matches)} matches)",
                    "matches": matches}

        match = matches[index]
        cx = match.get("cx", 0)
        cy = match.get("cy", 0)

        try:
            import nodriver.cdp.input_ as cdp_input

            if action == "click":
                # Move mouse, then click
                await tab.send(cdp_input.dispatch_mouse_event(
                    type_="mouseMoved", x=cx, y=cy,
                ))
                await asyncio.sleep(random.uniform(0.03, 0.1))
                await tab.send(cdp_input.dispatch_mouse_event(
                    type_="mousePressed", x=cx, y=cy,
                    button=cdp_input.MouseButton("left"), click_count=1,
                ))
                await asyncio.sleep(random.uniform(0.02, 0.06))
                await tab.send(cdp_input.dispatch_mouse_event(
                    type_="mouseReleased", x=cx, y=cy,
                    button=cdp_input.MouseButton("left"), click_count=1,
                ))

                return {
                    "status": "ok",
                    "action": "click",
                    "matched_text": match.get("text", ""),
                    "tag": match.get("tag", ""),
                    "score": match.get("score", 0),
                    "position": {"x": round(cx, 1), "y": round(cy, 1)},
                    "total_matches": search.get("count", 0),
                    "message": f"Clicked '{match.get('text', '')[:50]}' at ({round(cx)}, {round(cy)})"
                }
            else:
                # Type: click to focus, then insert text
                await tab.send(cdp_input.dispatch_mouse_event(
                    type_="mouseMoved", x=cx, y=cy,
                ))
                await asyncio.sleep(0.05)
                await tab.send(cdp_input.dispatch_mouse_event(
                    type_="mousePressed", x=cx, y=cy,
                    button=cdp_input.MouseButton("left"), click_count=1,
                ))
                await asyncio.sleep(0.03)
                await tab.send(cdp_input.dispatch_mouse_event(
                    type_="mouseReleased", x=cx, y=cy,
                    button=cdp_input.MouseButton("left"), click_count=1,
                ))
                await asyncio.sleep(0.1)

                # Select all existing text and replace
                await tab.send(cdp_input.dispatch_key_event(
                    type_="keyDown", modifiers=2 if sys.platform == "darwin" else 4,
                    key="a", code="KeyA",
                ))
                await tab.send(cdp_input.dispatch_key_event(
                    type_="keyUp", key="a", code="KeyA",
                ))
                await asyncio.sleep(0.05)

                await tab.send(cdp_input.insert_text(text=input_text))

                return {
                    "status": "ok",
                    "action": "type",
                    "matched_text": match.get("text", ""),
                    "tag": match.get("tag", ""),
                    "typed": input_text,
                    "message": f"Typed into '{match.get('text', '')[:50]}'"
                }

        except Exception as e:
            return {"error": f"Interact {action} failed: {e}"}

    async def _handle_fill_form(self, params: dict) -> dict:
        """Auto-fill form fields from a JSON dict."""
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        fields = params.get("fields", {})
        submit = params.get("submit", False)

        if not fields:
            return {"error": "No fields provided"}

        # Build JS that finds and fills each field
        fields_json = json.dumps(fields)
        js = """
((fields) => {
    const results = [];

    function findInput(key, value) {
        // 1. name attribute exact match
        let el = document.querySelector('[name="' + CSS.escape(key) + '"]');
        if (el) return {el, method: 'name'};

        // 2. id attribute exact match
        el = document.querySelector('#' + CSS.escape(key));
        if (el) return {el, method: 'id'};

        // 3. placeholder contains (case-insensitive)
        const lower = key.toLowerCase();
        const allInputs = document.querySelectorAll('input, select, textarea');
        for (const inp of allInputs) {
            const ph = (inp.getAttribute('placeholder') || '').toLowerCase();
            if (ph.includes(lower)) return {el: inp, method: 'placeholder'};
        }

        // 4. Associated label text
        const labels = document.querySelectorAll('label');
        for (const label of labels) {
            const labelText = label.textContent.trim().toLowerCase();
            if (labelText.includes(lower)) {
                const forId = label.getAttribute('for');
                if (forId) {
                    el = document.getElementById(forId);
                    if (el) return {el, method: 'label-for'};
                }
                el = label.querySelector('input, select, textarea');
                if (el) return {el, method: 'label-parent'};
            }
        }

        // 5. aria-label
        for (const inp of allInputs) {
            const aria = (inp.getAttribute('aria-label') || '').toLowerCase();
            if (aria.includes(lower)) return {el: inp, method: 'aria-label'};
        }

        // 6. type attribute match
        const typeMatch = document.querySelector('input[type="' + CSS.escape(key) + '"]');
        if (typeMatch) return {el: typeMatch, method: 'type'};

        return null;
    }

    for (const [key, value] of Object.entries(fields)) {
        const found = findInput(key, value);
        if (!found) {
            results.push({key, status: 'not_found'});
            continue;
        }
        const el = found.el;
        const tag = el.tagName.toLowerCase();

        try {
            if (tag === 'select') {
                // Find matching option by value or text
                let matched = false;
                for (const opt of el.options) {
                    if (opt.value === value || opt.textContent.trim().toLowerCase() === value.toLowerCase()) {
                        el.value = opt.value;
                        matched = true;
                        break;
                    }
                }
                if (!matched) el.value = value;
            } else {
                el.focus();
                el.value = '';
                el.value = value;
            }
            el.dispatchEvent(new Event('input', {bubbles: true}));
            el.dispatchEvent(new Event('change', {bubbles: true}));
            results.push({key, status: 'filled', method: found.method, tag});
        } catch(e) {
            results.push({key, status: 'error', error: e.message});
        }
    }

    // Find submit button if requested
    let submitInfo = null;
    const submitBtn = document.querySelector('button[type=submit], input[type=submit]')
        || Array.from(document.querySelectorAll('button')).find(b => {
            const t = b.textContent.trim().toLowerCase();
            return /^(submit|login|sign.?in|register|send|continue|next|go)$/i.test(t);
        });
    if (submitBtn) {
        const rect = submitBtn.getBoundingClientRect();
        submitInfo = {
            tag: submitBtn.tagName,
            text: (submitBtn.textContent || submitBtn.value || '').trim().substring(0, 50),
            cx: rect.x + rect.width / 2,
            cy: rect.y + rect.height / 2
        };
    }

    return JSON.stringify({results, submitInfo});
})""" + f"({fields_json})"

        try:
            result = await tab.evaluate(js)
            if isinstance(result, str):
                data = json.loads(result)
            elif isinstance(result, dict):
                data = result
            else:
                return {"error": "Unexpected fill-form result"}

            filled = [r for r in data.get("results", []) if r.get("status") == "filled"]
            not_found = [r for r in data.get("results", []) if r.get("status") == "not_found"]

            response = {
                "status": "ok",
                "filled": len(filled),
                "not_found": len(not_found),
                "details": data.get("results", []),
            }

            # Handle submit
            if submit and data.get("submitInfo"):
                si = data["submitInfo"]
                try:
                    import nodriver.cdp.input_ as cdp_input
                    cx, cy = si["cx"], si["cy"]
                    await tab.send(cdp_input.dispatch_mouse_event(
                        type_="mouseMoved", x=cx, y=cy,
                    ))
                    await asyncio.sleep(0.05)
                    await tab.send(cdp_input.dispatch_mouse_event(
                        type_="mousePressed", x=cx, y=cy,
                        button=cdp_input.MouseButton("left"), click_count=1,
                    ))
                    await asyncio.sleep(0.03)
                    await tab.send(cdp_input.dispatch_mouse_event(
                        type_="mouseReleased", x=cx, y=cy,
                        button=cdp_input.MouseButton("left"), click_count=1,
                    ))
                    response["submitted"] = True
                    response["submit_button"] = si.get("text", "")
                except Exception as e:
                    response["submitted"] = False
                    response["submit_error"] = str(e)
            elif submit:
                response["submitted"] = False
                response["submit_error"] = "No submit button found"

            return response
        except Exception as e:
            return {"error": f"Fill form failed: {e}"}

    async def _handle_storage(self, params: dict) -> dict:
        """Get/set/delete/clear/list localStorage or sessionStorage."""
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        action = params.get("action", "list")
        storage_type = params.get("storage_type", "local")
        key = params.get("key", "")
        value = params.get("value", "")

        store = "localStorage" if storage_type == "local" else "sessionStorage"

        try:
            if action == "list":
                result = await tab.evaluate(
                    f"JSON.stringify(Object.fromEntries(Object.entries({store})))"
                )
                data = json.loads(result) if isinstance(result, str) else (result or {})
                return {"status": "ok", "storage_type": storage_type,
                        "count": len(data), "entries": data}

            elif action == "get":
                if not key:
                    return {"error": "Key required for get"}
                result = await tab.evaluate(f'{store}.getItem({json.dumps(key)})')
                return {"status": "ok", "key": key, "value": result,
                        "storage_type": storage_type}

            elif action == "set":
                if not key:
                    return {"error": "Key required for set"}
                await tab.evaluate(
                    f'{store}.setItem({json.dumps(key)}, {json.dumps(value)})'
                )
                return {"status": "ok", "key": key, "value": value,
                        "storage_type": storage_type}

            elif action == "delete":
                if not key:
                    return {"error": "Key required for delete"}
                await tab.evaluate(f'{store}.removeItem({json.dumps(key)})')
                return {"status": "ok", "key": key, "deleted": True,
                        "storage_type": storage_type}

            elif action == "clear":
                await tab.evaluate(f'{store}.clear()')
                return {"status": "ok", "cleared": True,
                        "storage_type": storage_type}

            else:
                return {"error": f"Unknown storage action: {action}"}
        except Exception as e:
            return {"error": f"Storage {action} failed: {e}"}

    async def _handle_wait_ready(self, params: dict) -> dict:
        """Wait for page to fully load (network idle + DOM stable)."""
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        timeout = params.get("timeout", 30)
        strategy = params.get("strategy", "both")

        check_js = """
(() => {
    const readyState = document.readyState;
    const bodyLen = (document.body && document.body.innerHTML) ? document.body.innerHTML.length : 0;
    const pendingResources = performance.getEntriesByType('resource')
        .filter(r => r.responseEnd === 0).length;
    return JSON.stringify({readyState, bodyLen, pendingResources});
})()
"""
        try:
            start_time = time.time()
            last_body_len = -1
            stable_since = None
            network_idle_since = None

            while (time.time() - start_time) < timeout:
                result = await tab.evaluate(check_js)
                if isinstance(result, str):
                    data = json.loads(result)
                elif isinstance(result, dict):
                    data = result
                else:
                    data = {}

                ready_state = data.get("readyState", "loading")
                body_len = data.get("bodyLen", 0)
                pending = data.get("pendingResources", 0)
                now = time.time()

                # Track network idle
                if pending == 0 and ready_state == "complete":
                    if network_idle_since is None:
                        network_idle_since = now
                else:
                    network_idle_since = None

                # Track DOM stability
                if body_len == last_body_len and body_len > 0:
                    if stable_since is None:
                        stable_since = now
                else:
                    stable_since = None
                last_body_len = body_len

                # Check conditions based on strategy
                net_ok = network_idle_since and (now - network_idle_since >= 0.5)
                dom_ok = stable_since and (now - stable_since >= 0.5)

                if strategy == "networkidle" and net_ok:
                    break
                elif strategy == "domstable" and dom_ok:
                    break
                elif strategy == "both" and net_ok and dom_ok:
                    break

                await asyncio.sleep(0.3)
            else:
                elapsed = round(time.time() - start_time, 1)
                return {
                    "status": "ok",
                    "ready": False,
                    "timeout": True,
                    "elapsed": elapsed,
                    "message": f"Page did not stabilize within {timeout}s"
                }

            elapsed = round(time.time() - start_time, 1)
            return {
                "status": "ok",
                "ready": True,
                "timeout": False,
                "elapsed": elapsed,
                "strategy": strategy,
                "message": f"Page ready after {elapsed}s ({strategy})"
            }
        except Exception as e:
            return {"error": f"Wait-ready failed: {e}"}

    async def _handle_hover(self, params: dict) -> dict:
        """Hover over an element by selector or visible text."""
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        selector = params.get("selector", "")
        by_text = params.get("by_text", False)

        if not selector:
            return {"error": "No selector or text provided"}

        try:
            import nodriver.cdp.input_ as cdp_input

            if by_text:
                search = await self._find_element_by_text(tab, selector)
                if search.get("count", 0) == 0:
                    return {"error": f"No element found matching text: '{selector}'"}
                match = search["matches"][0]
                cx, cy = match["cx"], match["cy"]
                desc = match.get("text", "")[:50]
            else:
                # Get bounding rect via JS
                js = f"""
(() => {{
    const el = document.querySelector({json.dumps(selector)});
    if (!el) return JSON.stringify({{error: 'not_found'}});
    const rect = el.getBoundingClientRect();
    return JSON.stringify({{
        cx: rect.x + rect.width / 2,
        cy: rect.y + rect.height / 2,
        text: (el.textContent || '').trim().substring(0, 50)
    }});
}})()
"""
                result = await tab.evaluate(js)
                data = json.loads(result) if isinstance(result, str) else result
                if data.get("error"):
                    return {"error": f"Element not found: {selector}"}
                cx, cy = data["cx"], data["cy"]
                desc = data.get("text", "")

            await tab.send(cdp_input.dispatch_mouse_event(
                type_="mouseMoved", x=cx, y=cy,
            ))

            return {
                "status": "ok",
                "action": "hover",
                "position": {"x": round(cx, 1), "y": round(cy, 1)},
                "element_text": desc,
                "message": f"Hovered at ({round(cx)}, {round(cy)})"
            }
        except Exception as e:
            return {"error": f"Hover failed: {e}"}

    async def _handle_pdf(self, params: dict) -> dict:
        """Print page to PDF."""
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        output = params.get("output")
        if not output:
            output = str(STATE_DIR / f"page_{int(time.time())}.pdf")
        landscape = params.get("landscape", False)
        scale = params.get("scale", 1.0)

        try:
            import nodriver.cdp.page as cdp_page
            result = await tab.send(cdp_page.print_to_pdf(
                landscape=landscape,
                scale=scale,
                print_background=True,
            ))
            # result is (data, stream) tuple or just data depending on nodriver version
            if isinstance(result, tuple):
                pdf_data = result[0]
            else:
                pdf_data = result

            pdf_bytes = base64.b64decode(pdf_data)
            with open(output, 'wb') as f:
                f.write(pdf_bytes)

            return {
                "status": "ok",
                "path": output,
                "size": len(pdf_bytes),
                "message": f"PDF saved to: {output}"
            }
        except Exception as e:
            return {"error": f"PDF generation failed: {e}"}

    async def _handle_upload(self, params: dict) -> dict:
        """Upload a file to a file input element."""
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        file_path = params.get("file", "")
        selector = params.get("selector", "")

        if not file_path:
            return {"error": "No file path provided"}
        if not Path(file_path).exists():
            return {"error": f"File not found: {file_path}"}

        # Make path absolute
        file_path = str(Path(file_path).resolve())

        if not selector:
            selector = 'input[type="file"]'

        try:
            import nodriver.cdp.dom as cdp_dom
            import nodriver.cdp.runtime as cdp_runtime

            # Get the backend node ID for the file input
            js = f"""
(() => {{
    const el = document.querySelector({json.dumps(selector)});
    if (!el) return JSON.stringify({{error: 'not_found'}});
    return JSON.stringify({{found: true}});
}})()
"""
            check = await tab.evaluate(js)
            data = json.loads(check) if isinstance(check, str) else check
            if data.get("error"):
                return {"error": f"File input not found: {selector}"}

            # Use nodriver's element finding + CDP to set files
            element = await tab.find(selector, timeout=5)
            if not element:
                return {"error": f"File input not found: {selector}"}

            # Get the remote object id and resolve to backend node id
            node_id = element.node_id if hasattr(element, 'node_id') else None
            backend_node_id = element.backend_node_id if hasattr(element, 'backend_node_id') else None

            if backend_node_id:
                await tab.send(cdp_dom.set_file_input_files(
                    files=[file_path],
                    backend_node_id=backend_node_id,
                ))
            elif node_id:
                await tab.send(cdp_dom.set_file_input_files(
                    files=[file_path],
                    node_id=node_id,
                ))
            else:
                # Fallback: use JS to get the node
                js_get_id = f"""
(() => {{
    const el = document.querySelector({json.dumps(selector)});
    if (!el) return -1;
    // Store element globally for CDP reference
    window.__uploadTarget = el;
    return 1;
}})()
"""
                await tab.evaluate(js_get_id)
                # Try via evaluate handle
                doc = await tab.send(cdp_dom.get_document())
                node = await tab.send(cdp_dom.query_selector(
                    node_id=doc.node_id,
                    selector=selector,
                ))
                if node:
                    await tab.send(cdp_dom.set_file_input_files(
                        files=[file_path],
                        node_id=node,
                    ))
                else:
                    return {"error": "Could not resolve file input node for CDP"}

            return {
                "status": "ok",
                "file": file_path,
                "selector": selector,
                "message": f"Uploaded: {Path(file_path).name}"
            }
        except Exception as e:
            return {"error": f"Upload failed: {e}"}

    async def _handle_session(self, params: dict) -> dict:
        """Save or load full auth state (cookies + localStorage + sessionStorage)."""
        tab, err = await self._get_tab_or_error(params)
        if err:
            return err

        action = params.get("action", "")
        name = params.get("name", "")
        file_path = params.get("file", "")

        if not action:
            return {"error": "No action provided (save or load)"}

        if file_path:
            session_file = Path(file_path)
        elif name:
            SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
            session_file = SESSIONS_DIR / f"{name}.json"
        else:
            return {"error": "Session name or file path required"}

        if action == "save":
            try:
                # Get cookies via CDP
                import nodriver.cdp.network as net
                cookie_result = await tab.send(net.get_cookies())
                cookies = []
                for cookie in cookie_result:
                    cookies.append({
                        "name": cookie.name,
                        "value": cookie.value,
                        "domain": cookie.domain,
                        "path": cookie.path,
                        "secure": cookie.secure,
                        "http_only": cookie.http_only,
                        "expires": cookie.expires if hasattr(cookie, 'expires') else None,
                        "same_site": str(cookie.same_site) if hasattr(cookie, 'same_site') and cookie.same_site else None,
                    })

                # Get localStorage and sessionStorage via JS
                storage_js = """
JSON.stringify({
    localStorage: Object.fromEntries(Object.entries(localStorage)),
    sessionStorage: Object.fromEntries(Object.entries(sessionStorage)),
    url: window.location.href
})
"""
                storage_result = await tab.evaluate(storage_js)
                storage_data = json.loads(storage_result) if isinstance(storage_result, str) else (storage_result or {})

                session_data = {
                    "cookies": cookies,
                    "localStorage": storage_data.get("localStorage", {}),
                    "sessionStorage": storage_data.get("sessionStorage", {}),
                    "url": storage_data.get("url", ""),
                    "saved_at": datetime.now().isoformat(),
                }

                session_file.parent.mkdir(parents=True, exist_ok=True)
                with open(session_file, 'w') as f:
                    json.dump(session_data, f, indent=2)

                return {
                    "status": "ok",
                    "action": "save",
                    "path": str(session_file),
                    "cookies": len(cookies),
                    "localStorage_keys": len(storage_data.get("localStorage", {})),
                    "sessionStorage_keys": len(storage_data.get("sessionStorage", {})),
                    "url": storage_data.get("url", ""),
                    "message": f"Session saved to: {session_file}"
                }
            except Exception as e:
                return {"error": f"Session save failed: {e}"}

        elif action == "load":
            if not session_file.exists():
                return {"error": f"Session file not found: {session_file}"}
            try:
                with open(session_file) as f:
                    session_data = json.load(f)

                # Restore cookies
                import nodriver.cdp.network as net
                loaded_cookies = 0
                for cookie in session_data.get("cookies", []):
                    try:
                        await tab.send(net.set_cookie(
                            name=cookie["name"],
                            value=cookie["value"],
                            domain=cookie.get("domain"),
                            path=cookie.get("path", "/"),
                            secure=cookie.get("secure", False),
                            http_only=cookie.get("http_only", False),
                        ))
                        loaded_cookies += 1
                    except Exception:
                        pass

                # Restore localStorage
                local_data = session_data.get("localStorage", {})
                if local_data:
                    for k, v in local_data.items():
                        await tab.evaluate(
                            f'localStorage.setItem({json.dumps(k)}, {json.dumps(v)})'
                        )

                # Restore sessionStorage
                session_store = session_data.get("sessionStorage", {})
                if session_store:
                    for k, v in session_store.items():
                        await tab.evaluate(
                            f'sessionStorage.setItem({json.dumps(k)}, {json.dumps(v)})'
                        )

                return {
                    "status": "ok",
                    "action": "load",
                    "path": str(session_file),
                    "cookies_loaded": loaded_cookies,
                    "localStorage_keys": len(local_data),
                    "sessionStorage_keys": len(session_store),
                    "url": session_data.get("url", ""),
                    "message": f"Session loaded from: {session_file}"
                }
            except Exception as e:
                return {"error": f"Session load failed: {e}"}
        else:
            return {"error": f"Unknown session action: {action}. Use 'save' or 'load'"}

    async def _handle_network_log(self, params: dict) -> dict:
        """Return captured network log entries."""
        url_filter = params.get("filter", "")
        clear = params.get("clear", False)
        limit = params.get("limit", 50)

        entries = list(self._network_log)

        if url_filter:
            entries = [e for e in entries if url_filter in e.get("url", "")]

        entries = entries[-limit:]

        if clear:
            self._network_log.clear()

        return {
            "status": "ok",
            "count": len(entries),
            "total_captured": len(self._network_log) if not clear else 0,
            "entries": entries,
        }

    async def _handle_console_log(self, params: dict) -> dict:
        """Return captured console log entries."""
        level_filter = params.get("level", "")
        clear = params.get("clear", False)
        limit = params.get("limit", 50)

        entries = list(self._console_log)

        if level_filter:
            entries = [e for e in entries if e.get("level", "") == level_filter]

        entries = entries[-limit:]

        if clear:
            self._console_log.clear()

        return {
            "status": "ok",
            "count": len(entries),
            "total_captured": len(self._console_log) if not clear else 0,
            "entries": entries,
        }

    def _append_network_entry(self, entry: dict):
        """Append to network log, maintaining max 200 entries."""
        self._network_log.append(entry)
        if len(self._network_log) > 200:
            self._network_log = self._network_log[-200:]

    def _append_console_entry(self, entry: dict):
        """Append to console log, maintaining max 200 entries."""
        self._console_log.append(entry)
        if len(self._console_log) > 200:
            self._console_log = self._console_log[-200:]

    # -------------------------------------------------------------------
    # Cloudflare challenge detection & solving
    # -------------------------------------------------------------------

    async def _detect_cf_challenge(self, tab) -> dict:
        """Run CF detection JS on a tab and return parsed result."""
        try:
            result = await tab.evaluate(CF_DETECT_JS)
            if isinstance(result, str):
                return json.loads(result)
            if isinstance(result, dict):
                return result
            return {"found": False, "solved": False, "challenges": []}
        except Exception as e:
            return {"found": False, "solved": False, "challenges": [], "error": str(e)}

    async def _human_mouse_move(self, tab, from_x: float, from_y: float, to_x: float, to_y: float):
        """Simulate human-like mouse movement with a curved path and micro-jitter."""
        import nodriver.cdp.input_ as cdp_input
        import math

        # Generate bezier-like curved path with 8-15 steps
        steps = random.randint(8, 15)
        # Random control point offset for curve (humans don't move in straight lines)
        ctrl_x = (from_x + to_x) / 2 + random.uniform(-60, 60)
        ctrl_y = (from_y + to_y) / 2 + random.uniform(-40, 40)

        for i in range(steps + 1):
            t = i / steps
            # Quadratic bezier: B(t) = (1-t)^2*P0 + 2*(1-t)*t*P1 + t^2*P2
            inv_t = 1 - t
            mx = inv_t * inv_t * from_x + 2 * inv_t * t * ctrl_x + t * t * to_x
            my = inv_t * inv_t * from_y + 2 * inv_t * t * ctrl_y + t * t * to_y
            # Add micro-jitter (real mice are not perfectly smooth)
            mx += random.uniform(-1.5, 1.5)
            my += random.uniform(-1.5, 1.5)

            await tab.send(cdp_input.dispatch_mouse_event(
                type_="mouseMoved", x=mx, y=my,
            ))
            # Variable speed — slower at start and end (ease in/out)
            speed = 0.01 + 0.03 * math.sin(t * math.pi)
            await asyncio.sleep(speed + random.uniform(0, 0.015))

    async def _human_click(self, tab, cx: float, cy: float):
        """Simulate a human-like click with natural mouse movement and timing."""
        import nodriver.cdp.input_ as cdp_input

        # Start from a random position on the page (as if mouse was somewhere)
        start_x = cx + random.uniform(-200, 200)
        start_y = cy + random.uniform(-100, 150)
        start_x = max(10, start_x)
        start_y = max(10, start_y)

        # Move mouse along curved path to target
        await self._human_mouse_move(tab, start_x, start_y, cx, cy)

        # Brief pause before clicking (human reaction time)
        await asyncio.sleep(random.uniform(0.08, 0.25))

        # mousePressed with slight position variation
        press_x = cx + random.uniform(-1, 1)
        press_y = cy + random.uniform(-1, 1)
        await tab.send(cdp_input.dispatch_mouse_event(
            type_="mousePressed", x=press_x, y=press_y,
            button=cdp_input.MouseButton("left"), click_count=1,
        ))

        # Hold duration varies (humans don't instant-release)
        await asyncio.sleep(random.uniform(0.05, 0.15))

        # mouseReleased at slightly different position (micro-movement during click)
        release_x = press_x + random.uniform(-0.5, 0.5)
        release_y = press_y + random.uniform(-0.5, 0.5)
        await tab.send(cdp_input.dispatch_mouse_event(
            type_="mouseReleased", x=release_x, y=release_y,
            button=cdp_input.MouseButton("left"), click_count=1,
        ))

    async def _solve_cf_challenge(self, tab) -> dict:
        """Attempt to solve a Cloudflare challenge on the given tab with human-like behavior."""
        detection = await self._detect_cf_challenge(tab)

        if not detection.get("found"):
            return {"status": "ok", "action": "none", "message": "No CF challenge detected"}

        if detection.get("solved"):
            return {"status": "ok", "action": "none", "already_solved": True,
                    "message": "Challenge already solved"}

        challenges = detection.get("challenges", [])
        for challenge in challenges:
            ctype = challenge.get("type", "")

            if ctype == "challenge_waiting":
                # Wait a bit — it might auto-resolve
                await asyncio.sleep(3)
                recheck = await self._detect_cf_challenge(tab)
                if recheck.get("solved"):
                    return {"status": "ok", "action": "auto_solved",
                            "message": "Challenge auto-resolved while waiting"}
                return {"status": "ok", "action": "waiting",
                        "message": "Challenge is auto-resolving (no clickable element)"}

            if ctype in ("turnstile_iframe", "challenge_iframe", "widget_container"):
                x = challenge.get("x", 0)
                y = challenge.get("y", 0)
                width = challenge.get("width", 0)
                height = challenge.get("height", 0)

                if width <= 0 or height <= 0:
                    continue

                # --- Phase 1: wait for auto-resolve (managed mode) ---
                # Turnstile in managed mode often auto-passes after 2-5s if
                # background checks (TLS fingerprint, etc.) are clean.
                for _wait in range(5):
                    await asyncio.sleep(1)
                    auto_check = await self._detect_cf_challenge(tab)
                    if auto_check.get("solved") or not auto_check.get("found"):
                        return {
                            "status": "ok",
                            "action": "auto_solved",
                            "challenge_type": ctype,
                            "solved_after_click": False,
                            "message": "Challenge auto-resolved without click"
                        }

                # --- Phase 2: click attempts ---
                max_attempts = 4
                for attempt in range(max_attempts):
                    # Re-detect challenge position between retries (iframe
                    # may shift after a failed verification attempt).
                    if attempt > 0:
                        re_det = await self._detect_cf_challenge(tab)
                        if re_det.get("solved") or not re_det.get("found"):
                            return {
                                "status": "ok",
                                "action": "clicked",
                                "challenge_type": ctype,
                                "solved_after_click": True,
                                "attempts": attempt,
                                "message": f"Challenge resolved before attempt {attempt + 1}"
                            }
                        # Update position from fresh detection
                        for c in re_det.get("challenges", []):
                            if c.get("type") == ctype:
                                x = c.get("x", x)
                                y = c.get("y", y)
                                width = c.get("width", width)
                                height = c.get("height", height)
                                break

                    # Checkbox is ~28px from left edge, vertically centered
                    cx = x + 28 + random.uniform(-4, 4)
                    cy = y + (height / 2) + random.uniform(-4, 4)

                    try:
                        # Human-like click with curved mouse movement
                        await self._human_click(tab, cx, cy)

                        # Wait for Turnstile to verify — it needs 3-5s
                        wait_time = random.uniform(3.5, 5.0)
                        await asyncio.sleep(wait_time)

                        recheck = await self._detect_cf_challenge(tab)

                        if recheck.get("solved"):
                            return {
                                "status": "ok",
                                "action": "clicked",
                                "challenge_type": ctype,
                                "click_position": {"x": round(cx, 1), "y": round(cy, 1)},
                                "solved_after_click": True,
                                "attempts": attempt + 1,
                                "message": f"Solved {ctype} after {attempt + 1} attempt(s)"
                            }

                        if not recheck.get("found"):
                            # Challenge disappeared (page might have redirected)
                            return {
                                "status": "ok",
                                "action": "clicked",
                                "challenge_type": ctype,
                                "solved_after_click": True,
                                "attempts": attempt + 1,
                                "message": f"Challenge gone after {attempt + 1} attempt(s) (page redirected)"
                            }

                        # Not solved yet — wait before retry
                        if attempt < max_attempts - 1:
                            await asyncio.sleep(random.uniform(1.5, 3.0))

                    except Exception as e:
                        if attempt == max_attempts - 1:
                            return {"status": "error", "action": "click_failed",
                                    "challenge_type": ctype, "attempts": attempt + 1,
                                    "error": str(e)}

                # All attempts exhausted
                return {
                    "status": "ok",
                    "action": "clicked",
                    "challenge_type": ctype,
                    "click_position": {"x": round(cx, 1), "y": round(cy, 1)},
                    "solved_after_click": False,
                    "attempts": max_attempts,
                    "message": f"Clicked {ctype} {max_attempts}x but not solved yet"
                }

        return {"status": "ok", "action": "none",
                "message": "Challenge detected but no clickable element found",
                "detection": detection}

    async def _evade_recaptcha(self, tab) -> dict:
        """When reCAPTCHA v2 is detected, try to evade it by opening the URL
        in a fresh tab (new JS context). If that fails, signal that a browser
        restart is needed."""
        url = ""
        old_tid = ""
        try:
            url = tab.target.url or ""
            old_tid = tab.target.target_id
        except Exception:
            pass

        if not url or url.startswith("chrome"):
            return {"status": "ok", "action": "none",
                    "message": "reCAPTCHA detected but no navigable URL"}

        log(f"reCAPTCHA v2 detected on {url[:60]} — trying fresh tab")

        # Strategy 1: Open URL in a brand-new tab, close the old one
        try:
            new_tab = await self.browser.get(url)
            new_tid = new_tab.target.target_id
            self.active_tab_id = new_tid

            # Close the old tab
            try:
                await tab.close()
            except Exception:
                pass

            # Wait for the new page to settle
            await asyncio.sleep(random.uniform(3.0, 5.0))

            detection = await self._detect_cf_challenge(new_tab)
            has_recaptcha = detection.get("has_recaptcha", False)

            if not has_recaptcha:
                log(f"reCAPTCHA evaded via fresh tab on {url[:60]}")
                return {
                    "status": "ok",
                    "action": "recaptcha_evaded",
                    "method": "new_tab",
                    "tab_id": new_tid,
                    "message": f"reCAPTCHA evaded by opening fresh tab"
                }

            log(f"reCAPTCHA still present after fresh tab — flagging for restart")
        except Exception as e:
            log(f"reCAPTCHA fresh-tab attempt failed: {e}", "WARN")

        # Strategy 2: Flag that browser restart is needed
        # The scanner loop will handle the actual restart.
        return {
            "status": "ok",
            "action": "recaptcha_needs_restart",
            "url": url,
            "message": "reCAPTCHA persists — browser restart recommended"
        }

    async def _handle_load_extension(self, params: dict) -> dict:
        """Load unpacked extension(s) into the running browser via chrome://extensions.

        Uses macOS AppleScript to interact with the native file dialog since
        Chrome 145+ blocks --load-extension and Extensions.loadUnpacked requires
        pipe-based debugging.

        Supports batched loading: accepts `paths` (list) or `path` (single).
        When multiple extensions are provided, navigates to chrome://extensions
        once, enables dev mode once, then loads each extension sequentially.
        """
        # Build list of paths to load
        ext_paths = params.get("paths", [])
        single = params.get("path", "")
        if single and not ext_paths:
            ext_paths = [single]
        if not ext_paths:
            return {"error": "No extension path(s) provided"}

        # Validate all paths and skip CDP-injected / already-loaded
        validated = []
        skipped = []
        for p in ext_paths:
            p = os.path.abspath(p)
            folder_name = os.path.basename(p)

            # Skip CDP-injected extensions
            if folder_name in self._CDP_INJECTED_EXTENSIONS:
                skipped.append({"path": p, "reason": "cdp_injected"})
                continue

            # Skip already-loaded extensions
            if folder_name in self._loaded_extensions:
                skipped.append({"path": p, "reason": "already_loaded"})
                continue

            if not os.path.isdir(p) or not os.path.isfile(os.path.join(p, "manifest.json")):
                skipped.append({"path": p, "reason": "invalid_directory"})
                continue

            validated.append(p)

        if not validated:
            return {
                "status": "ok",
                "loaded": [],
                "skipped": skipped,
                "message": "No extensions to load (all skipped or already loaded)"
            }

        if sys.platform != "darwin":
            return {"error": "Live extension loading currently only supported on macOS"}

        # Save current tab to restore later
        prev_tab = await self._get_tab()
        prev_url = ""
        if prev_tab:
            try:
                prev_url = prev_tab.target.url or ""
            except Exception:
                pass

        try:
            # Navigate to chrome://extensions ONCE
            tab = await self._get_tab()
            if tab:
                await tab.get("chrome://extensions")
            else:
                tab = await self.browser.get("chrome://extensions")
            await asyncio.sleep(2)

            # Enable developer mode ONCE
            await tab.evaluate('''(function() {
                var mgr = document.querySelector('extensions-manager');
                var toolbar = mgr.shadowRoot.querySelector('extensions-toolbar');
                var toggle = toolbar.shadowRoot.querySelector('#devMode');
                if (!toggle.checked) toggle.click();
            })()''')
            await asyncio.sleep(0.5)

            # Snapshot existing extension IDs before loading
            pre_ids_json = await tab.evaluate('''(function() {
                var mgr = document.querySelector('extensions-manager');
                var sr = mgr.shadowRoot;
                var itemsList = sr.querySelector('extensions-item-list');
                if (!itemsList) return '[]';
                var ilSR = itemsList.shadowRoot;
                var items = ilSR.querySelectorAll('extensions-item');
                var ids = [];
                for (var item of items) ids.push(item.id);
                return JSON.stringify(ids);
            })()''')
            pre_ids = set(json.loads(pre_ids_json) if pre_ids_json else [])

            loaded = []
            errors = []

            for ext_path in validated:
                folder_name = os.path.basename(ext_path)
                log(f"Loading extension: {ext_path}")

                # Click "Load unpacked" button
                click_result = await tab.evaluate('''(function() {
                    var mgr = document.querySelector('extensions-manager');
                    var toolbar = mgr.shadowRoot.querySelector('extensions-toolbar');
                    var devDrawer = toolbar.shadowRoot.querySelector('#devDrawer');
                    if (!devDrawer) return 'no devDrawer';
                    var allBtns = devDrawer.querySelectorAll('cr-button');
                    for (var b of allBtns) {
                        if (b.textContent.trim().toLowerCase().includes('load')) {
                            b.click();
                            return 'clicked';
                        }
                    }
                    return 'no button';
                })()''')

                if click_result != 'clicked':
                    errors.append({"path": ext_path, "error": f"Could not click Load unpacked: {click_result}"})
                    continue

                await asyncio.sleep(1.5)

                # Use AppleScript to interact with the macOS file dialog
                applescript = f'''
tell application "System Events"
    delay 0.5
    keystroke "g" using {{command down, shift down}}
    delay 1
    keystroke "a" using command down
    delay 0.2
    keystroke "{ext_path}"
    delay 0.5
    keystroke return
    delay 1
    keystroke return
end tell
'''
                proc = await asyncio.create_subprocess_exec(
                    'osascript', '-e', applescript,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                _, stderr = await asyncio.wait_for(proc.communicate(), timeout=15)
                if proc.returncode != 0:
                    errors.append({"path": ext_path, "error": f"AppleScript failed: {stderr.decode().strip()}"})
                    continue

                await asyncio.sleep(3)
                loaded.append(ext_path)
                log(f"Extension loaded: {folder_name}")

            # Query all loaded extensions ONCE at the end
            ext_list = await tab.evaluate('''(function() {
                var mgr = document.querySelector('extensions-manager');
                var sr = mgr.shadowRoot;
                var itemsList = sr.querySelector('extensions-item-list');
                if (!itemsList) return '[]';
                var ilSR = itemsList.shadowRoot;
                var items = ilSR.querySelectorAll('extensions-item');
                var result = [];
                for (var item of items) {
                    var iSR = item.shadowRoot;
                    var nameEl = iSR.querySelector('#name');
                    result.push({id: item.id, name: nameEl ? nameEl.textContent.trim() : '?'});
                }
                return JSON.stringify(result);
            })()''')

            browser_extensions = json.loads(ext_list) if ext_list else []

            # Find newly added extensions by diffing with pre-load snapshot
            new_exts = [be for be in browser_extensions if be.get("id") not in pre_ids]

            # Update _loaded_extensions state for successfully loaded paths.
            # Match new extensions to loaded paths by order (they were loaded sequentially).
            for i, ext_path in enumerate(loaded):
                folder_name = os.path.basename(ext_path)
                chrome_id = ""
                chrome_name = folder_name
                if i < len(new_exts):
                    chrome_id = new_exts[i].get("id", "")
                    chrome_name = new_exts[i].get("name", folder_name)
                self._loaded_extensions[folder_name] = {
                    "id": chrome_id,
                    "name": chrome_name,
                    "path": ext_path,
                }

            # Navigate back to previous page ONCE
            if prev_url and prev_url != "chrome://extensions/" and not prev_url.startswith("chrome://"):
                await tab.get(prev_url)
                await asyncio.sleep(1)

            return {
                "status": "ok",
                "loaded": [os.path.basename(p) for p in loaded],
                "skipped": skipped,
                "errors": errors,
                "browser_extensions": browser_extensions,
                "message": f"Loaded {len(loaded)} extension(s), skipped {len(skipped)}, errors {len(errors)}"
            }
        except Exception as e:
            return {"error": f"Failed to load extension: {e}"}

    async def _handle_unload_extension(self, params: dict) -> dict:
        """Unload (remove) an extension from the running browser via chrome://extensions.

        Finds the extension by name/id in the shadow DOM, clicks its remove button,
        and updates _loaded_extensions state.
        """
        name = params.get("name", "")
        if not name:
            return {"error": "No extension name provided"}

        if sys.platform != "darwin":
            return {"error": "Extension unloading currently only supported on macOS"}

        # Resolve folder name and Chrome extension ID from _loaded_extensions
        folder_name = None
        chrome_id = ""
        if name in self._loaded_extensions:
            folder_name = name
            chrome_id = self._loaded_extensions[name].get("id", "")
        else:
            for fn, info in self._loaded_extensions.items():
                if info.get("name", "").lower() == name.lower():
                    folder_name = fn
                    chrome_id = info.get("id", "")
                    break

        # Build search terms: the input name, plus the chrome_id if known
        search_names = [name]
        if chrome_id:
            search_names.append(chrome_id)

        # Save current tab to restore later
        prev_tab = await self._get_tab()
        prev_url = ""
        if prev_tab:
            try:
                prev_url = prev_tab.target.url or ""
            except Exception:
                pass

        try:
            # Navigate to chrome://extensions
            tab = await self._get_tab()
            if tab:
                await tab.get("chrome://extensions")
            else:
                tab = await self.browser.get("chrome://extensions")
            await asyncio.sleep(2)

            # Find and remove the extension by name, ID, or normalized name match
            remove_result = await tab.evaluate('''(function() {
                var searchTerms = ''' + json.dumps(search_names) + ''';
                function norm(s) { return s.toLowerCase().replace(/[^a-z0-9]/g, ''); }
                var mgr = document.querySelector('extensions-manager');
                var sr = mgr.shadowRoot;
                var itemsList = sr.querySelector('extensions-item-list');
                if (!itemsList) return JSON.stringify({error: 'no items list'});
                var ilSR = itemsList.shadowRoot;
                var items = ilSR.querySelectorAll('extensions-item');
                for (var item of items) {
                    var iSR = item.shadowRoot;
                    var nameEl = iSR.querySelector('#name');
                    var extName = nameEl ? nameEl.textContent.trim() : '';
                    var matched = false;
                    for (var term of searchTerms) {
                        if (item.id === term ||
                            extName.toLowerCase() === term.toLowerCase() ||
                            norm(extName).indexOf(norm(term)) !== -1) {
                            matched = true;
                            break;
                        }
                    }
                    if (matched) {
                        var removeBtn = iSR.querySelector('#removeButton');
                        if (removeBtn) {
                            removeBtn.click();
                            return JSON.stringify({status: 'clicked', id: item.id, name: extName});
                        }
                        return JSON.stringify({error: 'no remove button for ' + extName});
                    }
                }
                return JSON.stringify({error: 'extension not found: ' + searchTerms.join(', ')});
            })()''')

            result = json.loads(remove_result) if remove_result else {"error": "no response"}

            if "error" in result:
                # Navigate back
                if prev_url and not prev_url.startswith("chrome://"):
                    await tab.get(prev_url)
                    await asyncio.sleep(1)
                return result

            # Wait for confirmation dialog and confirm removal
            await asyncio.sleep(1)
            await tab.evaluate('''(function() {
                var dialog = document.querySelector('extensions-manager')
                    .shadowRoot.querySelector('cr-dialog');
                if (dialog) {
                    var confirmBtn = dialog.querySelector('.action-button');
                    if (confirmBtn) confirmBtn.click();
                }
            })()''')
            await asyncio.sleep(1)

            # Update state
            if folder_name and folder_name in self._loaded_extensions:
                del self._loaded_extensions[folder_name]

            # Navigate back to previous page
            if prev_url and not prev_url.startswith("chrome://"):
                await tab.get(prev_url)
                await asyncio.sleep(1)

            return {
                "status": "ok",
                "removed_id": result.get("id", ""),
                "removed_name": result.get("name", name),
                "message": f"Extension '{result.get('name', name)}' removed from browser"
            }
        except Exception as e:
            return {"error": f"Failed to unload extension: {e}"}

    async def _handle_list_loaded_extensions(self, params: dict) -> dict:
        """Return the current set of loaded extensions tracked by the daemon."""
        return {
            "status": "ok",
            "loaded_extensions": self._loaded_extensions,
            "cdp_injected": list(self._CDP_INJECTED_EXTENSIONS),
        }

    async def _handle_cf_solve(self, params: dict) -> dict:
        """Command handler for cf_solve — solve CF challenges on tab(s)."""
        tab_id = params.get("tab_id")

        if tab_id:
            tab = await self._get_tab(tab_id)
            if tab is None:
                return self._tab_not_found_error(tab_id)
            result = await self._solve_cf_challenge(tab)
            result["tab_id"] = tab_id
            return result

        # Default: check all tabs
        results = []
        tabs = self.browser.tabs or []
        for tab in tabs:
            tid = tab.target.target_id
            try:
                r = await self._solve_cf_challenge(tab)
                r["tab_id"] = tid
                results.append(r)
            except Exception as e:
                results.append({"tab_id": tid, "error": str(e)})

        return {"status": "ok", "tabs_checked": len(results), "results": results}

    async def cf_scanner_loop(self):
        """Background loop: scan all tabs for CF challenges every 2 seconds."""
        log("CF challenge scanner started")
        while True:
            try:
                await asyncio.sleep(2)
                tabs = self.browser.tabs or []
                now = time.time()

                for tab in tabs:
                    try:
                        tid = tab.target.target_id
                        # Cooldown: skip if attempted recently
                        last_attempt = self._cf_cooldowns.get(tid, 0)
                        cooldown = self._cf_cooldown_secs.get(tid, 3)
                        if now - last_attempt < cooldown:
                            continue

                        detection = await self._detect_cf_challenge(tab)
                        if not detection.get("found") or detection.get("solved"):
                            # Reset cooldown when challenge is gone
                            self._cf_cooldown_secs.pop(tid, None)
                            self._recaptcha_attempts.pop(tid, None)
                            continue

                        # reCAPTCHA v2 detected — try evasion instead of clicking
                        if detection.get("has_recaptcha"):
                            self._cf_cooldowns[tid] = now
                            attempts = self._recaptcha_attempts.get(tid, 0)
                            tab_url = ""
                            try:
                                tab_url = tab.target.url or ""
                            except Exception:
                                pass
                            log(f"CF scanner: reCAPTCHA v2 on tab {tid[:12]} ({tab_url[:60]}), attempt #{attempts + 1}")

                            if attempts == 0:
                                # First try: open in new tab
                                result = await self._evade_recaptcha(tab)
                                self._recaptcha_attempts[tid] = 1
                                action = result.get("action", "unknown")
                                log(f"CF scanner: recaptcha evasion result={action}")
                                if action == "recaptcha_evaded":
                                    self._recaptcha_attempts.pop(tid, None)
                                else:
                                    # Set longer cooldown before restart attempt
                                    self._cf_cooldown_secs[tid] = 5
                            elif attempts == 1:
                                # Second try: restart browser, re-navigate
                                log(f"CF scanner: reCAPTCHA persists — restarting browser for {tab_url[:60]}")
                                self._recaptcha_restart_url = tab_url
                                self._recaptcha_attempts[tid] = 2
                                # Signal the daemon loop to restart
                                raise _RecaptchaRestartSignal(tab_url)
                            else:
                                # Already tried restart, long cooldown
                                self._cf_cooldown_secs[tid] = 30
                                log(f"CF scanner: reCAPTCHA still present after restart, backing off")
                            continue

                        # CF/Turnstile challenge found — attempt to solve
                        self._cf_cooldowns[tid] = now
                        tab_url = ""
                        try:
                            tab_url = tab.target.url or ""
                        except Exception:
                            pass
                        log(f"CF scanner: challenge detected on tab {tid[:12]} ({tab_url[:60]})")

                        result = await self._solve_cf_challenge(tab)
                        action = result.get("action", "unknown")
                        solved = result.get("solved_after_click", False)
                        auto = result.get("action") == "auto_solved"
                        log(f"CF scanner: action={action}, solved={solved} on tab {tid[:12]}")

                        # If not solved, retry sooner (2s instead of default 3s)
                        if not solved and not auto:
                            self._cf_cooldown_secs[tid] = 2
                        else:
                            self._cf_cooldown_secs.pop(tid, None)
                    except _RecaptchaRestartSignal:
                        raise  # propagate to outer handler
                    except Exception as e:
                        log(f"CF scanner: error on tab: {e}", "WARN")
            except asyncio.CancelledError:
                log("CF challenge scanner stopped")
                return
            except _RecaptchaRestartSignal as sig:
                log(f"CF scanner: browser restart requested for reCAPTCHA on {sig.url}")
                # The run_daemon loop will catch this and restart the browser
                raise
            except Exception as e:
                log(f"CF scanner loop error: {e}", "WARN")


# ---------------------------------------------------------------------------
# daemon_request: CLI → daemon IPC
# ---------------------------------------------------------------------------

def daemon_request(command: str, params: Optional[Dict] = None, timeout: float = 30.0) -> Dict[str, Any]:
    """Send a command to the daemon's command server and return the response."""
    state = read_state()
    if not state:
        return {"error": "Browser is not running"}

    cmd_port = state.get("cmd_port")
    if not cmd_port:
        return {"error": "Command server not available (browser may need restart)"}

    payload = json.dumps({"command": command, "params": params or {}}).encode('utf-8')

    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{cmd_port}/command",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode())
            return body
        except Exception:
            return {"error": f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"error": f"Cannot connect to command server: {e.reason}"}
    except socket.timeout:
        return {"error": "Command timed out"}
    except Exception as e:
        return {"error": str(e)}


def print_error(result: dict):
    """Print an error result, including available tabs if present."""
    print(f"error: {result['error']}")
    if "available_tabs" in result:
        tabs = result["available_tabs"]
        if tabs:
            print(f"\nAvailable tabs ({len(tabs)}):")
            for tab in tabs:
                tid = tab.get("id", "?")
                title = tab.get("title", "(untitled)")
                url = tab.get("url", "")
                print(f"  [{tid[:12]}] {title[:50]}")
                if url:
                    print(f"    {url[:70]}")
        else:
            print("  (no tabs open)")
    if "hint" in result:
        print(f"\n{result['hint']}")


def format_available_tabs(result: dict) -> str:
    """Format available_tabs from an error response into readable text."""
    tabs = result.get("available_tabs", [])
    if not tabs:
        return "  (no tabs open)"
    lines = []
    for tab in tabs:
        tid = tab.get("id", "?")
        title = tab.get("title", "(untitled)")
        url = tab.get("url", "")
        short_id = tid[:12]
        lines.append(f"  [{short_id}] {title[:50]}")
        if url:
            lines.append(f"    {url[:70]}")
    return "\n".join(lines)


def print_result(result: dict, as_json: bool = False):
    """Print a daemon command result, either as JSON or human-readable."""
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"error: {result['error']}")
            if "available_tabs" in result:
                print(f"\nAvailable tabs:")
                print(format_available_tabs(result))
            if "hint" in result:
                print(f"\n{result['hint']}")
        elif "message" in result:
            print(result["message"])
        elif "status" in result:
            print(f"ok")


# ---------------------------------------------------------------------------
# Browser startup
# ---------------------------------------------------------------------------

async def start_browser(port: int, headless: bool, profile_dir: Path, extensions: Optional[List[str]] = None, proxy: Optional[str] = None):
    """Start nodriver browser with remote debugging enabled. Returns (browser, actual_port)."""
    try:
        import nodriver as uc
    except ImportError:
        log("nodriver not installed. Run: pip install nodriver", "ERROR")
        sys.exit(1)

    ensure_state_dir()
    profile_dir.mkdir(parents=True, exist_ok=True)

    log(f"Starting ghost browser...")
    log(f"Profile directory: {profile_dir}")
    log(f"Headless: {headless}")

    browser_args = [
        "--enable-unsafe-extension-debugging",
    ]

    if proxy:
        browser_args.append(f"--proxy-server={proxy}")
        log(f"Using proxy: {proxy}")

    # NOTE: Chrome 145+ branded builds block --load-extension entirely
    # (extension_service.cc: "--load-extension is not allowed in Google Chrome").
    # Extensions like the MouseEvent patcher are now injected via CDP
    # (Page.addScriptToEvaluateOnNewDocument) after browser start instead.
    # For runtime extension loading, we use the Extensions.loadUnpacked CDP command.
    config = uc.Config(
        user_data_dir=str(profile_dir),
        headless=headless,
        browser_args=browser_args if browser_args else None,
    )

    browser = await uc.start(config=config)

    actual_port = browser.config.port
    log(f"nodriver assigned port: {actual_port}")

    pid = os.getpid()

    # Wait for CDP to be available
    for _ in range(30):
        if check_cdp_endpoint(actual_port):
            break
        await asyncio.sleep(1)
    else:
        log("CDP endpoint did not become available within 30 seconds", "ERROR")
        browser.stop()
        sys.exit(1)

    # Write state with actual port
    state = {
        "pid": pid,
        "port": actual_port,
        "headless": headless,
        "profile_dir": str(profile_dir),
        "started_at": datetime.now().isoformat(),
        "cdp_url": f"http://127.0.0.1:{actual_port}",
        "ws_url": f"ws://127.0.0.1:{actual_port}",
    }
    if proxy:
        state["proxy"] = proxy
    write_state(state)
    PID_FILE.write_text(str(pid))

    log(f"Ghost browser started successfully (PID: {pid})")
    log(f"CDP endpoint: http://127.0.0.1:{actual_port}")

    return browser, actual_port


async def run_daemon(port: int, headless: bool, profile_dir: Path, extensions: Optional[List[str]] = None, proxy: Optional[str] = None):
    """Run browser as a daemon process."""
    browser, actual_port = await start_browser(port, headless, profile_dir, extensions, proxy)

    # Start command server
    cmd_server = CommandServer(browser)
    cmd_port = await cmd_server.start()

    # Update state with command port
    state = read_state() or {}
    state["cmd_port"] = cmd_port
    write_state(state)

    # Update mcporter config with actual port
    update_mcporter_config(actual_port)

    # Set up network and console logging on the first tab
    try:
        tabs = browser.tabs
        if tabs:
            first_tab = tabs[0]
            import nodriver.cdp.network as net
            import nodriver.cdp.runtime as cdp_runtime
            import nodriver.cdp.log as cdp_log
            import nodriver.cdp.console as cdp_console

            # STEALTH: Block Runtime and Console domains from auto-enabling.
            # nodriver's _register_handlers() auto-enables CDP domains when
            # handlers are registered. Runtime.enable and Console.enable are
            # detectable by anti-bot systems (Cloudflare, DataDome) via the
            # console.debug(Error) getter trick. We block them the same way
            # nodriver blocks target/storage/input_ domains.
            _orig_register = first_tab._connection._register_handlers

            async def _stealth_register_handlers(self_conn=first_tab._connection):
                # Temporarily mark runtime and console as "already enabled"
                # so _register_handlers skips them
                import nodriver.cdp as cdp
                _blocked = []
                for blocked_mod in (cdp.runtime, cdp.console):
                    if blocked_mod not in self_conn.enabled_domains:
                        self_conn.enabled_domains.append(blocked_mod)
                        _blocked.append(blocked_mod)
                try:
                    await _orig_register()
                finally:
                    # Remove our fake entries so they don't accumulate
                    for blocked_mod in _blocked:
                        try:
                            self_conn.enabled_domains.remove(blocked_mod)
                        except ValueError:
                            pass

            first_tab._connection._register_handlers = _stealth_register_handlers

            # Enable network domain for logging
            await first_tab.send(net.enable())

            # Set up network event handlers
            async def on_request(event: net.RequestWillBeSent):
                cmd_server._append_network_entry({
                    "type": "request",
                    "method": event.request.method,
                    "url": event.request.url,
                    "timestamp": time.time(),
                })

            async def on_response(event: net.ResponseReceived):
                cmd_server._append_network_entry({
                    "type": "response",
                    "url": event.response.url,
                    "status": event.response.status,
                    "mime_type": event.response.mime_type,
                    "timestamp": time.time(),
                })

            async def on_loading_failed(event: net.LoadingFailed):
                cmd_server._append_network_entry({
                    "type": "failed",
                    "url": "",
                    "error": event.error_text,
                    "timestamp": time.time(),
                })

            first_tab.add_handler(net.RequestWillBeSent, on_request)
            first_tab.add_handler(net.ResponseReceived, on_response)
            first_tab.add_handler(net.LoadingFailed, on_loading_failed)

            # Use Log domain instead of Runtime for console capture.
            # SECURITY: Runtime.enable is detectable by Cloudflare/DataDome
            # via the console.debug(Error) getter trick. Log.enable is safe.
            await first_tab.send(cdp_log.enable())

            async def on_log_entry(event: cdp_log.EntryAdded):
                entry = event.entry
                text = entry.text or ""
                if entry.args:
                    arg_texts = []
                    for arg in entry.args:
                        if arg.value is not None:
                            arg_texts.append(str(arg.value))
                        elif arg.description:
                            arg_texts.append(arg.description)
                    if arg_texts:
                        text = " ".join(arg_texts)
                cmd_server._append_console_entry({
                    "level": entry.level or "log",
                    "text": text,
                    "timestamp": time.time(),
                    "source": entry.source or "",
                    "url": entry.url or "",
                })

            first_tab.add_handler(cdp_log.EntryAdded, on_log_entry)

            log("Network and console logging enabled")

            # Inject MouseEvent/PointerEvent screenX/screenY patcher via CDP.
            # This replaces the Chrome extension approach which doesn't work on
            # Chrome 145+ branded builds (--load-extension is blocked).
            await cmd_server.inject_mouse_patch(first_tab)
    except Exception as e:
        log(f"Warning: Could not set up network/console logging: {e}", "WARN")

    # Auto-load installed extensions (except CDP-injected ones)
    try:
        ext_dir = _get_extensions_dir()
        if ext_dir.is_dir():
            auto_paths = []
            for entry in sorted(ext_dir.iterdir()):
                if entry.is_dir() and (entry / "manifest.json").exists():
                    auto_paths.append(str(entry.resolve()))
            if auto_paths:
                log(f"Auto-loading {len(auto_paths)} extension(s) from {ext_dir}")
                result = await cmd_server._handle_load_extension({"paths": auto_paths})
                loaded = result.get("loaded", [])
                skipped = result.get("skipped", [])
                errors = result.get("errors", [])
                log(f"Auto-load complete: {len(loaded)} loaded, {len(skipped)} skipped, {len(errors)} errors")
    except Exception as e:
        log(f"Warning: Auto-load extensions failed: {e}", "WARN")

    # Set up signal handlers for graceful shutdown
    stop_event = asyncio.Event()

    def handle_signal(sig, frame):
        log(f"Received signal {sig}, shutting down...")
        stop_event.set()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    log(f"Browser daemon running. Command server on port {cmd_port}. Press Ctrl+C or send SIGTERM to stop.")

    # Start background CF challenge scanner
    cf_task = asyncio.create_task(cmd_server.cf_scanner_loop())

    try:
        while not stop_event.is_set():
            # Check if CF scanner signalled a reCAPTCHA restart
            if cf_task.done():
                try:
                    cf_task.result()
                except _RecaptchaRestartSignal as sig:
                    restart_url = sig.url
                    log(f"reCAPTCHA restart: stopping browser to evade reCAPTCHA on {restart_url[:60]}")

                    # Stop command server and browser
                    await cmd_server.stop()
                    try:
                        browser.stop()
                    except Exception:
                        pass

                    # Brief pause before restarting
                    await asyncio.sleep(random.uniform(2.0, 4.0))

                    # Restart browser with same settings
                    log("reCAPTCHA restart: starting fresh browser...")
                    browser, actual_port = await start_browser(port, headless, profile_dir, extensions, proxy)
                    cmd_server = CommandServer(browser)
                    cmd_port = await cmd_server.start()

                    # Update state
                    state = read_state() or {}
                    state["cmd_port"] = cmd_port
                    state["port"] = actual_port
                    state["cdp_url"] = f"http://127.0.0.1:{actual_port}"
                    state["ws_url"] = f"ws://127.0.0.1:{actual_port}"
                    write_state(state)
                    update_mcporter_config(actual_port)

                    # Navigate to the URL that had the reCAPTCHA
                    if restart_url:
                        log(f"reCAPTCHA restart: re-navigating to {restart_url[:60]}")
                        await asyncio.sleep(1)
                        try:
                            tab = await browser.get(restart_url)
                            cmd_server.active_tab_id = tab.target.target_id
                        except Exception as e:
                            log(f"reCAPTCHA restart: navigate failed: {e}", "WARN")

                    # Restart scanner
                    cf_task = asyncio.create_task(cmd_server.cf_scanner_loop())
                    log(f"reCAPTCHA restart: complete, scanner resumed")
                    continue
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    log(f"CF scanner task ended unexpectedly: {e}", "WARN")
                    # Restart the scanner
                    cf_task = asyncio.create_task(cmd_server.cf_scanner_loop())

            if not check_cdp_endpoint(actual_port):
                log("Browser appears to have crashed!", "ERROR")
                break
            await asyncio.sleep(5)
    finally:
        log("Stopping CF scanner...")
        cf_task.cancel()
        try:
            await cf_task
        except (asyncio.CancelledError, _RecaptchaRestartSignal):
            pass

        log("Stopping command server...")
        await cmd_server.stop()

        log("Stopping browser...")
        try:
            browser.stop()
        except Exception as e:
            log(f"Error stopping browser: {e}", "WARN")

        clear_state()
        update_mcporter_config(actual_port, restore=True)
        log("Browser stopped cleanly.")


# ---------------------------------------------------------------------------
# CLI command handlers
# ---------------------------------------------------------------------------

def cmd_start(args):
    """Handle start command."""
    existing_pid = get_running_pid()
    if existing_pid:
        state = read_state()
        port = state.get("port", "unknown") if state else "unknown"
        print(json.dumps({
            "status": "already_running",
            "pid": existing_pid,
            "port": port,
            "message": f"Ghost browser already running (PID: {existing_pid}, port: {port})"
        }))
        return 0

    profile_dir = resolve_profile_dir(args.profile)
    extensions = args.extension if hasattr(args, 'extension') and args.extension else None
    proxy = args.proxy if hasattr(args, 'proxy') and args.proxy else None

    if args.daemon:
        script_path = Path(__file__).resolve()

        cmd = [
            sys.executable,
            str(script_path),
            "start",
            "--profile", args.profile or read_profiles_config().get("default_profile", DEFAULT_PROFILE_NAME),
            "--no-daemon",
        ]
        if args.headless:
            cmd.append("--headless")
        if extensions:
            for ext in extensions:
                cmd.extend(["--extension", ext])
        if proxy:
            cmd.extend(["--proxy", proxy])

        with open(LOG_FILE, 'a') as log_f:
            proc = subprocess.Popen(
                cmd,
                stdout=log_f,
                stderr=log_f,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )

        for i in range(30):
            time.sleep(1)
            if proc.poll() is not None:
                print(json.dumps({
                    "status": "error",
                    "error": "process_died",
                    "message": f"Browser process died unexpectedly (exit code: {proc.returncode}). Check {LOG_FILE}"
                }))
                return 1

            state = read_state()
            if state and state.get("port") and state.get("cmd_port"):
                actual_port = state["port"]
                if check_cdp_endpoint(actual_port):
                    print(json.dumps({
                        "status": "started",
                        "pid": state.get("pid", proc.pid),
                        "port": actual_port,
                        "cmd_port": state["cmd_port"],
                        "cdp_url": f"http://127.0.0.1:{actual_port}",
                        "message": "Ghost browser started in background"
                    }))
                    return 0

        print(json.dumps({
            "status": "error",
            "error": "startup_failed",
            "message": f"Browser failed to start within 30 seconds. Check {LOG_FILE}"
        }))
        proc.terminate()
        return 1
    else:
        print(json.dumps({
            "status": "starting",
            "message": "Starting ghost browser in foreground..."
        }), flush=True)
        asyncio.run(run_daemon(0, args.headless, profile_dir, extensions, proxy))
        return 0


def cmd_stop(args):
    """Handle stop command."""
    pid = get_running_pid()
    if not pid:
        print(json.dumps({
            "status": "not_running",
            "message": "Ghost browser is not running"
        }))
        return 0

    log(f"Stopping browser (PID: {pid})...")

    try:
        os.kill(pid, signal.SIGTERM)
        for _ in range(10):
            if not is_process_running(pid):
                break
            time.sleep(0.5)
        else:
            log("Graceful shutdown timeout, forcing kill", "WARN")
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)

        # Read state before clearing for mcporter restore
        state = read_state()
        port = state.get("port", DEFAULT_PORT) if state else DEFAULT_PORT

        clear_state()
        update_mcporter_config(port, restore=True)

        print(json.dumps({
            "status": "stopped",
            "pid": pid,
            "message": f"Ghost browser stopped (PID: {pid})"
        }))
        return 0

    except ProcessLookupError:
        clear_state()
        print(json.dumps({
            "status": "stopped",
            "message": "Browser process was already dead, cleaned up state"
        }))
        return 0
    except PermissionError:
        print(json.dumps({
            "status": "error",
            "error": "permission_denied",
            "message": f"Cannot stop browser (PID: {pid}), permission denied"
        }))
        return 1


def cmd_status(args):
    """Handle status command."""
    pid = get_running_pid()
    state = read_state()

    if not pid:
        result = {
            "running": False,
            "message": "Ghost browser is not running"
        }
    else:
        port = state.get("port", DEFAULT_PORT) if state else DEFAULT_PORT
        cdp_healthy = check_cdp_endpoint(port)

        result = {
            "running": True,
            "healthy": cdp_healthy,
            "pid": pid,
            "port": port,
            "cmd_port": state.get("cmd_port") if state else None,
            "cdp_url": f"http://127.0.0.1:{port}",
            "started_at": state.get("started_at") if state else None,
            "headless": state.get("headless") if state else None,
            "profile_dir": state.get("profile_dir") if state else None,
            "proxy": state.get("proxy") if state else None,
            "message": "Ghost browser is running" + (" and healthy" if cdp_healthy else " but CDP not responding")
        }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["running"]:
            print(f"Status: RUNNING")
            print(f"PID: {result['pid']}")
            print(f"Port: {result['port']}")
            if result.get("cmd_port"):
                print(f"Cmd Port: {result['cmd_port']}")
            print(f"CDP URL: {result['cdp_url']}")
            print(f"Health: {'OK' if result.get('healthy') else 'UNHEALTHY'}")
            if result.get("profile_dir"):
                print(f"Profile: {result['profile_dir']}")
            if result.get("proxy"):
                print(f"Proxy: {result['proxy']}")
            if result.get("started_at"):
                print(f"Started: {result['started_at']}")
        else:
            print("Status: NOT RUNNING")

    return 0 if not result["running"] or result.get("healthy", False) else 1


def cmd_health(args):
    """Quick health check - returns exit code 0 if healthy, 1 if not."""
    state = read_state()
    if not state:
        sys.exit(1)

    port = state.get("port", DEFAULT_PORT)
    if check_cdp_endpoint(port):
        print("healthy")
        sys.exit(0)
    else:
        print("unhealthy")
        sys.exit(1)


def cmd_tabs(args):
    """List all open browser tabs."""
    state = read_state()
    if not state:
        result = {
            "status": "error",
            "error": "not_running",
            "message": "Ghost browser is not running"
        }
        print(json.dumps(result) if args.json else result["message"])
        return 1

    port = state.get("port", DEFAULT_PORT)
    if not check_cdp_endpoint(port):
        result = {
            "status": "error",
            "error": "cdp_unavailable",
            "message": "Browser is running but CDP is not responding"
        }
        print(json.dumps(result) if args.json else result["message"])
        return 1

    tabs = get_open_tabs(port)

    if args.json:
        print(json.dumps({
            "status": "ok",
            "count": len(tabs),
            "tabs": tabs
        }, indent=2))
    else:
        if not tabs:
            print("No tabs open")
        else:
            print(f"Open tabs ({len(tabs)}):\n")
            for i, tab in enumerate(tabs, 1):
                title = tab["title"][:50] + "..." if len(tab["title"]) > 50 else tab["title"]
                url = tab["url"][:60] + "..." if len(tab["url"]) > 60 else tab["url"]
                print(f"  {i}. [{tab['id'][:8]}] {title}")
                print(f"     {url}")
                print()

    return 0


def navigate_cdp(port: int, url: str) -> Dict[str, Any]:
    """Open a new tab and navigate to URL via CDP HTTP API."""
    try:
        encoded_url = urllib.parse.quote(url, safe=':/?#[]@!$&\'()*+,;=-._~')
        new_tab_url = f"http://127.0.0.1:{port}/json/new?{encoded_url}"
        req = urllib.request.Request(new_tab_url, method='PUT')
        with urllib.request.urlopen(req, timeout=15) as resp:
            tab_data = json.loads(resp.read().decode())
            return {
                "success": True,
                "tab_id": tab_data.get("id"),
                "title": tab_data.get("title", ""),
                "url": tab_data.get("url", url),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def cmd_navigate(args):
    """Smart navigation - checks for existing tabs, then actually navigates."""
    state = read_state()
    if not state:
        result = {
            "status": "error",
            "error": "not_running",
            "message": "Ghost browser is not running"
        }
        print(json.dumps(result) if args.json else result["message"])
        return 1

    port = state.get("port", DEFAULT_PORT)
    if not check_cdp_endpoint(port):
        result = {
            "status": "error",
            "error": "cdp_unavailable",
            "message": "Browser is running but CDP is not responding"
        }
        print(json.dumps(result) if args.json else result["message"])
        return 1

    url = args.url

    if not args.force_new:
        existing_tab = find_tab_by_url(port, url, exact=args.exact)
        if existing_tab:
            result = {
                "status": "exists",
                "action": "reuse",
                "tab_id": existing_tab["id"],
                "title": existing_tab["title"],
                "url": existing_tab["url"],
                "message": f"Tab already open: {existing_tab['title']}"
            }
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"exists: Tab already open")
                print(f"  Title: {existing_tab['title']}")
                print(f"  URL: {existing_tab['url']}")
            return 0

    # Try daemon route first (keeps active tab tracking in sync)
    cmd_port = state.get("cmd_port")
    if cmd_port:
        params = {"url": url, "force_new": args.force_new}
        result = daemon_request("navigate", params, timeout=30)
        if "error" not in result:
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                tab_id = result.get("tab_id", "")
                print(f"ok: Navigated to {url}")
                if tab_id:
                    print(f"  Tab: [{tab_id[:12]}]")
            return 0
        # If daemon navigate failed, log and fall through to CDP
        log(f"Daemon navigate failed: {result.get('error')}, falling back to CDP", "WARN")

    # Fallback: direct CDP HTTP API (won't track active tab in daemon)
    nav_result = navigate_cdp(port, url)

    if nav_result.get("success"):
        result = {
            "status": "ok",
            "action": "navigated",
            "url": url,
            "tab_id": nav_result.get("tab_id"),
            "message": f"Navigated to: {url}"
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"ok: Navigated to {url}")
        return 0
    else:
        result = {
            "status": "error",
            "error": "navigate_failed",
            "url": url,
            "detail": nav_result.get("error", "unknown"),
            "message": f"Failed to navigate: {nav_result.get('error', 'unknown')}"
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"error: Failed to navigate - {nav_result.get('error', 'unknown')}")
        return 1


# ---------------------------------------------------------------------------
# New command handlers (using daemon_request)
# ---------------------------------------------------------------------------

def _require_running(args) -> Optional[int]:
    """Check if browser is running. Returns exit code if not, None if ok."""
    state = read_state()
    if not state or not get_running_pid():
        msg = "Ghost browser is not running"
        if hasattr(args, 'json') and args.json:
            print(json.dumps({"status": "error", "error": "not_running", "message": msg}))
        else:
            print(msg)
        return 1
    return None


def cmd_screenshot(args):
    """Take a screenshot of the current page."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {}
    if args.tab:
        params["tab_id"] = args.tab
    if args.output:
        params["output"] = args.output

    result = daemon_request("screenshot", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(f"Screenshot saved to: {result.get('path', 'unknown')}")
    return 0


def cmd_content(args):
    """Get page HTML content."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("content", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(result.get("content", ""))
    return 0


def cmd_eval(args):
    """Execute JavaScript in the browser."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"js": args.js}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("eval", params, timeout=60)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        r = result.get("result")
        if r is not None:
            if isinstance(r, str):
                print(r)
            else:
                print(json.dumps(r, indent=2))
        else:
            print("undefined")
    return 0


def cmd_click(args):
    """Click an element by selector."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"selector": args.selector}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("click", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(f"Clicked: {args.selector}")
    return 0


def cmd_type(args):
    """Type text into an element."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"selector": args.selector, "text": args.text}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("type", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(f"Typed into: {args.selector}")
    return 0


def cmd_find(args):
    """Find elements by selector."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"selector": args.selector}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("find", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        elements = result.get("elements", [])
        print(f"Found {result.get('count', 0)} element(s):\n")
        for i, el in enumerate(elements, 1):
            tag = el.get("tag", "?")
            text = el.get("text", "")[:80]
            attrs = el.get("attrs", {})
            attr_str = " ".join(f'{k}="{v}"' for k, v in list(attrs.items())[:3])
            print(f"  {i}. <{tag} {attr_str}>")
            if text:
                print(f"     {text}")
    return 0


def cmd_scroll(args):
    """Scroll the page."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {}
    if args.tab:
        params["tab_id"] = args.tab

    if args.to is not None:
        params["direction"] = "to"
        params["amount"] = args.to
    elif args.up:
        params["direction"] = "up"
    else:
        params["direction"] = "down"

    result = daemon_request("scroll", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        action = result.get("action", "scroll")
        print(f"ok: {action}")
    return 0


def cmd_wait(args):
    """Wait for an element to appear."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"selector": args.selector, "timeout": args.timeout}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("wait", params, timeout=args.timeout + 5)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        if result.get("found"):
            print(f"Found: <{result.get('tag', '?')}> {result.get('text', '')[:80]}")
        else:
            print(f"Element not found within {args.timeout}s: {args.selector}")
            return 1
    return 0


def cmd_close_tab(args):
    """Close a browser tab."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    result = daemon_request("close_tab", {"tab_id": args.tab_id})
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(f"Closed tab: {args.tab_id}")
    return 0


def cmd_activate_tab(args):
    """Activate (switch to) a browser tab."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    result = daemon_request("activate_tab", {"tab_id": args.tab_id})
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(f"Activated tab: {args.tab_id}")
    return 0


def cmd_cookies(args):
    """Get browser cookies."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {}
    if args.tab:
        params["tab_id"] = args.tab
    if args.domain:
        params["domain"] = args.domain

    result = daemon_request("cookies", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        cookies = result.get("cookies", [])
        print(f"Cookies ({result.get('count', 0)}):\n")
        for c in cookies:
            flags = []
            if c.get("secure"):
                flags.append("Secure")
            if c.get("http_only"):
                flags.append("HttpOnly")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            print(f"  {c['name']}={c['value'][:50]}")
            print(f"    Domain: {c.get('domain', '?')}{flag_str}")
    return 0


def cmd_set_cookie(args):
    """Set a browser cookie."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"name": args.name, "value": args.value}
    if args.domain:
        params["domain"] = args.domain
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("set_cookie", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(f"Set cookie: {args.name}={args.value}")
    return 0


def cmd_clear_cookies(args):
    """Clear browser cookies."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {}
    if args.domain:
        params["domain"] = args.domain
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("clear_cookies", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print("Cookies cleared")
    return 0


def cmd_window(args):
    """Resize or reposition the browser window."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {}
    if args.tab:
        params["tab_id"] = args.tab
    if args.size:
        params["size"] = args.size
    if args.position:
        params["position"] = args.position

    result = daemon_request("window", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        parts = []
        if args.size:
            parts.append(f"size={args.size}")
        if args.position:
            parts.append(f"position={args.position}")
        print(f"Window updated: {', '.join(parts)}")
    return 0


def cmd_download(args):
    """Download a file via the browser."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"url": args.url}
    if args.tab:
        params["tab_id"] = args.tab
    if args.output:
        params["output"] = args.output

    result = daemon_request("download", params, timeout=120)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(f"Downloaded to: {result.get('path', 'unknown')} ({format_size(result.get('size', 0))})")
    return 0


def cmd_save_cookies(args):
    """Export cookies to a JSON file."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {}
    if args.file:
        params["file"] = args.file
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("save_cookies", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(f"Saved {result.get('count', 0)} cookies to: {result.get('path', 'unknown')}")
    return 0


def cmd_load_cookies(args):
    """Import cookies from a JSON file."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    result = daemon_request("load_cookies", {"file": args.file})
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(f"Loaded {result.get('loaded', 0)}/{result.get('total', 0)} cookies")
    return 0


def cmd_cf_solve(args):
    """Detect and solve Cloudflare challenges."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("cf_solve", params, timeout=60)

    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        # Single tab result
        if "action" in result:
            action = result.get("action", "none")
            if result.get("already_solved"):
                print("CF challenge already solved")
            elif action == "clicked":
                solved = result.get("solved_after_click", False)
                pos = result.get("click_position", {})
                print(f"Clicked {result.get('challenge_type', 'challenge')} at ({pos.get('x', '?')}, {pos.get('y', '?')})")
                print(f"Solved: {solved}")
            elif action == "waiting":
                print("Challenge is auto-resolving (no click needed)")
            else:
                print(result.get("message", "No CF challenge detected"))
        # Multi-tab results
        elif "results" in result:
            results = result["results"]
            print(f"Checked {result.get('tabs_checked', 0)} tab(s):\n")
            for r in results:
                tid = r.get("tab_id", "?")[:12]
                action = r.get("action", "none")
                if r.get("error"):
                    print(f"  [{tid}] error: {r['error']}")
                elif r.get("already_solved"):
                    print(f"  [{tid}] already solved")
                elif action == "clicked":
                    solved = r.get("solved_after_click", False)
                    print(f"  [{tid}] clicked -> solved={solved}")
                elif action == "waiting":
                    print(f"  [{tid}] auto-resolving (waiting)")
                else:
                    print(f"  [{tid}] no challenge")
    return 0


# ---------------------------------------------------------------------------
# New LLM-friendly CLI commands
# ---------------------------------------------------------------------------

def cmd_readable(args):
    """Get page content as LLM-friendly markdown."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"max_length": args.max_length}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("readable", params, timeout=30)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(result.get("markdown", ""))
    return 0


def cmd_elements(args):
    """List all interactive elements on the page."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"limit": args.limit}
    if args.form_only:
        params["form_only"] = True
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("elements", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(result.get("compact", ""))
    return 0


def cmd_page_summary(args):
    """Get a compact page summary."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("page_summary", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(result.get("compact", ""))
    return 0


def cmd_interact(args):
    """Click or type by visible text."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"action": args.action, "text": args.text}
    if args.type_text:
        params["input_text"] = args.type_text
    if args.index is not None:
        params["index"] = args.index
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("interact", params, timeout=30)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(result.get("message", "ok"))
    return 0


def cmd_fill_form(args):
    """Auto-fill form fields from JSON."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    try:
        fields = json.loads(args.fields)
    except json.JSONDecodeError as e:
        print(f"error: Invalid JSON: {e}")
        return 1

    params = {"fields": fields, "submit": args.submit}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("fill_form", params, timeout=30)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        filled = result.get("filled", 0)
        not_found = result.get("not_found", 0)
        print(f"Filled {filled} field(s), {not_found} not found")
        if result.get("submitted"):
            print(f"Submitted via: {result.get('submit_button', 'button')}")
        elif result.get("submit_error"):
            print(f"Submit failed: {result['submit_error']}")
    return 0


def cmd_storage(args):
    """Manage localStorage/sessionStorage."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"action": args.storage_action, "storage_type": "session" if args.session else "local"}
    if hasattr(args, 'key') and args.key:
        params["key"] = args.key
    if hasattr(args, 'value') and args.value:
        params["value"] = args.value
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("storage", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        action = args.storage_action
        if action == "list":
            entries = result.get("entries", {})
            store = "sessionStorage" if args.session else "localStorage"
            print(f"{store} ({result.get('count', 0)} entries):\n")
            for k, v in entries.items():
                v_short = str(v)[:80]
                print(f"  {k} = {v_short}")
        elif action == "get":
            val = result.get("value")
            if val is None:
                print(f"(not set)")
            else:
                print(val)
        elif action == "set":
            print(f"Set: {params.get('key')} = {params.get('value', '')[:50]}")
        elif action == "delete":
            print(f"Deleted: {params.get('key')}")
        elif action == "clear":
            print("Storage cleared")
    return 0


def cmd_wait_ready(args):
    """Wait for page to fully load."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"timeout": args.timeout}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("wait_ready", params, timeout=args.timeout + 5)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        if result.get("ready"):
            print(f"Page ready ({result.get('elapsed', '?')}s)")
        else:
            print(f"Timeout after {args.timeout}s - page may still be loading")
            return 1
    return 0


def cmd_hover(args):
    """Hover over an element."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"selector": args.target, "by_text": args.by_text}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("hover", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(result.get("message", "ok"))
    return 0


def cmd_pdf(args):
    """Print page to PDF."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {}
    if args.output:
        params["output"] = args.output
    if args.landscape:
        params["landscape"] = True
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("pdf", params, timeout=30)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(f"PDF saved: {result.get('path', 'unknown')} ({format_size(result.get('size', 0))})")
    return 0


def cmd_upload(args):
    """Upload a file to a file input."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"file": args.file_path}
    if args.selector:
        params["selector"] = args.selector
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("upload", params, timeout=30)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        print(result.get("message", "ok"))
    return 0


def cmd_session(args):
    """Save or load full auth state."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"action": args.session_action, "name": args.name}
    if args.tab:
        params["tab_id"] = args.tab

    result = daemon_request("session", params, timeout=30)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        if args.session_action == "save":
            print(f"Session saved: {result.get('path', '?')}")
            print(f"  Cookies: {result.get('cookies', 0)}")
            print(f"  localStorage: {result.get('localStorage_keys', 0)} keys")
            print(f"  sessionStorage: {result.get('sessionStorage_keys', 0)} keys")
        else:
            print(f"Session loaded: {result.get('path', '?')}")
            print(f"  Cookies: {result.get('cookies_loaded', 0)}")
            print(f"  localStorage: {result.get('localStorage_keys', 0)} keys")
            print(f"  sessionStorage: {result.get('sessionStorage_keys', 0)} keys")
    return 0


def cmd_network_log(args):
    """View captured network requests."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"limit": args.limit}
    if args.filter:
        params["filter"] = args.filter
    if args.clear:
        params["clear"] = True

    result = daemon_request("network_log", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        entries = result.get("entries", [])
        print(f"Network log ({result.get('count', 0)} entries, {result.get('total_captured', 0)} total):\n")
        for e in entries:
            etype = e.get("type", "?")
            url = e.get("url", "")[:80]
            if etype == "request":
                method = e.get("method", "?")
                print(f"  -> {method} {url}")
            elif etype == "response":
                status = e.get("status", "?")
                mime = e.get("mime_type", "")
                print(f"  <- {status} {url} [{mime}]")
            elif etype == "failed":
                err = e.get("error", "?")
                print(f"  !! FAILED: {err} {url}")
    return 0


def cmd_console_log(args):
    """View captured console output."""
    rc = _require_running(args)
    if rc is not None:
        return rc

    params = {"limit": args.limit}
    if args.level:
        params["level"] = args.level
    if args.clear:
        params["clear"] = True

    result = daemon_request("console_log", params)
    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print_error(result)
        return 1
    else:
        entries = result.get("entries", [])
        print(f"Console log ({result.get('count', 0)} entries, {result.get('total_captured', 0)} total):\n")
        for e in entries:
            level = e.get("level", "log")
            text = e.get("text", "")[:200]
            prefix = {"error": "ERR", "warning": "WRN", "info": "INF"}.get(level, "LOG")
            print(f"  [{prefix}] {text}")
    return 0


# ---------------------------------------------------------------------------
# Extension management commands
# ---------------------------------------------------------------------------

def _get_extensions_dir() -> Path:
    """Return the built-in extensions directory."""
    return Path(__file__).resolve().parent.parent / "extensions"


def _extract_extension_id(source: str) -> Optional[str]:
    """Extract a Chrome Web Store extension ID from a URL or raw ID string.
    Accepts:
      - Full URL: https://chromewebstore.google.com/detail/name/abcdef123456...
      - Old URL:  https://chrome.google.com/webstore/detail/name/abcdef123456...
      - Raw ID:   abcdef123456...  (32 lowercase a-p chars)
    """
    import re
    source = source.strip()
    # Try to extract ID from URL (last path segment that looks like an ID)
    url_match = re.search(r'/([a-p]{32})(?:[/?#]|$)', source)
    if url_match:
        return url_match.group(1)
    # Raw ID (32 lowercase a-p characters)
    if re.fullmatch(r'[a-p]{32}', source):
        return source
    return None


def _download_crx(extension_id: str, dest_path: Path) -> bool:
    """Download a .crx file from Google's CRX endpoint."""
    # Google's public CRX download URL (used by Chromium update mechanism)
    crx_url = (
        f"https://clients2.google.com/service/update2/crx"
        f"?response=redirect"
        f"&prodversion=131.0.0.0"
        f"&acceptformat=crx2,crx3"
        f"&x=id%3D{extension_id}%26uc"
    )
    try:
        req = urllib.request.Request(crx_url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36",
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if len(data) < 100:
                return False
            dest_path.write_bytes(data)
            return True
    except Exception as e:
        log(f"CRX download failed: {e}", "WARN")
        return False


def _extract_crx(crx_path: Path, dest_dir: Path) -> bool:
    """Extract a .crx file (CRX2 or CRX3 format) into dest_dir.
    CRX files are ZIP archives with a binary header that must be skipped."""
    import zipfile

    data = crx_path.read_bytes()

    # Find the ZIP start (PK\x03\x04 signature)
    zip_start = data.find(b'PK\x03\x04')
    if zip_start < 0:
        log("CRX file does not contain a valid ZIP archive", "ERROR")
        return False

    # Write the ZIP portion to a temp file and extract
    zip_data = data[zip_start:]
    import io
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
            zf.extractall(dest_dir)
        return True
    except zipfile.BadZipFile as e:
        log(f"CRX extraction failed: {e}", "ERROR")
        return False


def _get_extension_name_from_manifest(ext_dir: Path) -> str:
    """Read the extension name from its manifest.json."""
    manifest_path = ext_dir / "manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            name = manifest.get("name", "")
            # Handle Chrome i18n message references like "__MSG_appName__"
            if name.startswith("__MSG_"):
                return ""
            return name
        except Exception:
            pass
    return ""


def cmd_install_extension(args):
    """Install a Chrome extension from the Web Store or a local .crx file."""
    source = args.source
    ext_dir = _get_extensions_dir()
    ext_dir.mkdir(parents=True, exist_ok=True)

    # Check if it's a local .crx file
    local_crx = Path(source)
    if local_crx.exists() and local_crx.suffix == ".crx":
        # Extract local CRX
        name = args.name or local_crx.stem
        dest = ext_dir / name
        if dest.exists() and not args.force:
            msg = f"Extension '{name}' already exists. Use --force to overwrite."
            if args.json:
                print(json.dumps({"error": msg}))
            else:
                print(f"error: {msg}")
            return 1

        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)

        if not _extract_crx(local_crx, dest):
            shutil.rmtree(dest, ignore_errors=True)
            msg = "Failed to extract CRX file"
            if args.json:
                print(json.dumps({"error": msg}))
            else:
                print(f"error: {msg}")
            return 1

        ext_name = _get_extension_name_from_manifest(dest) or name

        # Auto-load into running browser if possible
        auto_loaded = False
        state = read_state()
        if state and name not in CommandServer._CDP_INJECTED_EXTENSIONS:
            load_result = daemon_request("load_extension", {"path": str(dest.resolve())}, timeout=30)
            if load_result and load_result.get("status") == "ok":
                auto_loaded = True

        result = {
            "status": "ok",
            "name": ext_name,
            "folder": name,
            "path": str(dest),
            "source": "local_crx",
            "loaded": auto_loaded,
            "message": f"Installed and loaded '{ext_name}'" if auto_loaded else f"Installed '{ext_name}' from local CRX. Restart browser to activate."
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if auto_loaded:
                print(f"ok: Installed and loaded '{ext_name}' → extensions/{name}/")
            else:
                print(f"ok: Installed '{ext_name}' → extensions/{name}/")
                print("    Restart browser to activate: ghost-browser stop && ghost-browser start")
        return 0

    # Try as Chrome Web Store URL or extension ID
    ext_id = _extract_extension_id(source)
    if not ext_id:
        msg = f"Cannot parse extension ID from: {source}\nExpected: Chrome Web Store URL or 32-char extension ID"
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(f"error: {msg}")
        return 1

    folder_name = args.name or ext_id
    dest = ext_dir / folder_name
    if dest.exists() and not args.force:
        msg = f"Extension '{folder_name}' already exists. Use --force to overwrite."
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(f"error: {msg}")
        return 1

    # Download CRX
    if not args.json:
        print(f"Downloading extension {ext_id}...")

    crx_tmp = ext_dir / f".{ext_id}.crx.tmp"
    try:
        if not _download_crx(ext_id, crx_tmp):
            msg = f"Failed to download extension {ext_id}. It may not exist or be unavailable."
            if args.json:
                print(json.dumps({"error": msg}))
            else:
                print(f"error: {msg}")
            return 1

        # Extract
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)

        if not _extract_crx(crx_tmp, dest):
            shutil.rmtree(dest, ignore_errors=True)
            msg = "Failed to extract downloaded CRX"
            if args.json:
                print(json.dumps({"error": msg}))
            else:
                print(f"error: {msg}")
            return 1

        ext_name = _get_extension_name_from_manifest(dest) or ext_id

        # Rename folder to a friendlier name if we got the extension name
        final_folder = folder_name
        if folder_name == ext_id and ext_name and ext_name != ext_id:
            # Sanitize name for filesystem
            import re
            safe_name = re.sub(r'[^\w\s-]', '', ext_name).strip().lower()
            safe_name = re.sub(r'[\s-]+', '-', safe_name)[:50]
            if safe_name and not (ext_dir / safe_name).exists():
                new_dest = ext_dir / safe_name
                dest.rename(new_dest)
                dest = new_dest
                final_folder = safe_name

        # Auto-load into running browser if possible
        auto_loaded = False
        state = read_state()
        if state and final_folder not in CommandServer._CDP_INJECTED_EXTENSIONS:
            load_result = daemon_request("load_extension", {"path": str(dest.resolve())}, timeout=30)
            if load_result and load_result.get("status") == "ok":
                auto_loaded = True

        result = {
            "status": "ok",
            "name": ext_name,
            "extension_id": ext_id,
            "folder": final_folder,
            "path": str(dest),
            "source": "chrome_web_store",
            "loaded": auto_loaded,
            "message": f"Installed and loaded '{ext_name}'" if auto_loaded else f"Installed '{ext_name}'. Restart browser to activate."
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if auto_loaded:
                print(f"ok: Installed and loaded '{ext_name}' → extensions/{final_folder}/")
            else:
                print(f"ok: Installed '{ext_name}' → extensions/{final_folder}/")
                print("    Restart browser to activate: ghost-browser stop && ghost-browser start")
        return 0
    finally:
        crx_tmp.unlink(missing_ok=True)


def cmd_list_extensions(args):
    """List all installed extensions with loaded state."""
    ext_dir = _get_extensions_dir()

    # Query daemon for loaded state if browser is running
    loaded_info = {}
    cdp_injected = set()
    state = read_state()
    if state:
        resp = daemon_request("list_loaded_extensions", {}, timeout=5)
        if resp and resp.get("status") == "ok":
            loaded_info = resp.get("loaded_extensions", {})
            cdp_injected = set(resp.get("cdp_injected", []))

    extensions = []
    if ext_dir.is_dir():
        for entry in sorted(ext_dir.iterdir()):
            if entry.is_dir() and (entry / "manifest.json").exists():
                name = _get_extension_name_from_manifest(entry) or entry.name
                try:
                    with open(entry / "manifest.json") as f:
                        manifest = json.load(f)
                    version = manifest.get("version", "?")
                except Exception:
                    version = "?"
                size = get_dir_size(entry)
                folder = entry.name

                ext_entry = {
                    "folder": folder,
                    "name": name,
                    "version": version,
                    "path": str(entry),
                    "size": size,
                    "size_human": format_size(size),
                }

                # Add loaded/cdp-injected state
                if folder in cdp_injected:
                    ext_entry["cdp_injected"] = True
                    ext_entry["loaded"] = False
                elif folder in loaded_info:
                    ext_entry["loaded"] = True
                    ext_entry["chrome_id"] = loaded_info[folder].get("id", "")
                else:
                    ext_entry["loaded"] = False

                extensions.append(ext_entry)

    if args.json:
        print(json.dumps({"status": "ok", "extensions": extensions}, indent=2))
    else:
        if not extensions:
            print("No extensions installed.")
        else:
            print(f"Installed extensions ({len(extensions)}):\n")
            for ext in extensions:
                tag = ""
                if ext.get("cdp_injected"):
                    tag = "  [cdp-injected]"
                elif ext.get("loaded"):
                    tag = "  [loaded]"
                print(f"  {ext['name']} v{ext['version']}  ({ext['size_human']}){tag}")
                print(f"    {ext['folder']}/")
    return 0


def cmd_remove_extension(args):
    """Remove an installed extension."""
    ext_dir = _get_extensions_dir()
    name = args.name

    target = ext_dir / name
    if not target.exists():
        # Try fuzzy match on extension names
        for entry in ext_dir.iterdir():
            if entry.is_dir():
                ext_name = _get_extension_name_from_manifest(entry)
                if ext_name and ext_name.lower() == name.lower():
                    target = entry
                    break
        else:
            msg = f"Extension '{name}' not found"
            if args.json:
                print(json.dumps({"error": msg}))
            else:
                print(f"error: {msg}")
            return 1

    folder_name = target.name
    ext_name = _get_extension_name_from_manifest(target) or folder_name
    shutil.rmtree(target)

    result = {
        "status": "ok",
        "removed": folder_name,
        "name": ext_name,
        "message": f"Removed '{ext_name}'. Restart browser to take effect."
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"ok: Removed '{ext_name}' (extensions/{folder_name}/)")
        print("    Restart browser to take effect: ghost-browser stop && ghost-browser start")
    return 0


def cmd_load_extension(args):
    """Load extension(s) into the running browser via chrome://extensions automation.

    Uses batched loading: sends all paths in a single request so the daemon
    navigates to chrome://extensions only once.
    """
    state = read_state()
    if not state:
        msg = "Browser is not running. Start it first."
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(f"error: {msg}")
        return 1

    ext_dir = _get_extensions_dir()

    # Determine which extensions to load
    if args.name:
        # Specific extension
        ext_path = Path(args.name)
        if not ext_path.is_dir():
            ext_path = ext_dir / args.name
        if not ext_path.is_dir() or not (ext_path / "manifest.json").exists():
            msg = f"Extension not found: {args.name}"
            if args.json:
                print(json.dumps({"error": msg}))
            else:
                print(f"error: {msg}")
            return 1
        ext_paths = [str(ext_path.resolve())]
    else:
        # Load all extensions from extensions/ dir (daemon will skip already-loaded & CDP-injected)
        ext_paths = []
        if ext_dir.is_dir():
            for entry in sorted(ext_dir.iterdir()):
                if entry.is_dir() and (entry / "manifest.json").exists():
                    ext_paths.append(str(entry.resolve()))
        if not ext_paths:
            msg = "No extensions found in extensions/ directory."
            if args.json:
                print(json.dumps({"error": msg}))
            else:
                print(msg)
            return 0

    if not args.json:
        print(f"Loading {len(ext_paths)} extension(s)...")

    # Send batched request — single chrome://extensions session
    timeout = max(30, len(ext_paths) * 15)
    result = daemon_request("load_extension", {"paths": ext_paths}, timeout=timeout)

    if not result or "error" in result:
        err = result.get("error", "no response") if result else "no response"
        if args.json:
            print(json.dumps({"error": err}))
        else:
            print(f"error: {err}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        loaded = result.get("loaded", [])
        skipped = result.get("skipped", [])
        errors = result.get("errors", [])
        for name in loaded:
            print(f"  ok: {name} loaded")
        for s in skipped:
            folder = os.path.basename(s["path"])
            print(f"  skip: {folder} ({s['reason']})")
        for e in errors:
            folder = os.path.basename(e["path"])
            print(f"  error: {folder} — {e['error']}")
        print(f"\n{len(loaded)} loaded, {len(skipped)} skipped, {len(errors)} errors")
    return 0


def cmd_unload_extension(args):
    """Unload (remove) an extension from the running browser."""
    state = read_state()
    if not state:
        msg = "Browser is not running."
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(f"error: {msg}")
        return 1

    name = args.name

    # Resolve display name for better UX
    ext_dir = _get_extensions_dir()
    display_name = name
    target = ext_dir / name
    if target.is_dir():
        display_name = _get_extension_name_from_manifest(target) or name

    if not args.json:
        print(f"Unloading {display_name}...")

    result = daemon_request("unload_extension", {"name": display_name}, timeout=20)

    if not result or "error" in result:
        err = result.get("error", "no response") if result else "no response"
        if args.json:
            print(json.dumps({"error": err}))
        else:
            print(f"error: {err}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"ok: {result.get('removed_name', name)} removed from browser")
    return 0


# ---------------------------------------------------------------------------
# Profile management commands
# ---------------------------------------------------------------------------

def cmd_profile(args):
    """Handle profile subcommands."""
    migrate_legacy_profile()
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    action = args.profile_action

    if action == "list":
        profiles = []
        if PROFILES_DIR.exists():
            for entry in sorted(PROFILES_DIR.iterdir()):
                if entry.is_dir():
                    size = get_dir_size(entry)
                    profiles.append({
                        "name": entry.name,
                        "path": str(entry),
                        "size": size,
                        "size_human": format_size(size),
                    })

        config = read_profiles_config()
        default = config.get("default_profile", DEFAULT_PROFILE_NAME)

        if args.json:
            print(json.dumps({
                "status": "ok",
                "default": default,
                "profiles": profiles,
            }, indent=2))
        else:
            if not profiles:
                print("No profiles found.")
            else:
                print(f"Profiles (default: {default}):\n")
                for p in profiles:
                    marker = " *" if p["name"] == default else ""
                    print(f"  {p['name']}{marker}  ({p['size_human']})")
        return 0

    elif action == "create":
        name = args.profile_name
        if not name:
            print("error: Profile name required")
            return 1
        profile_dir = get_profile_dir(name)
        if profile_dir.exists():
            print(f"error: Profile '{name}' already exists")
            return 1
        profile_dir.mkdir(parents=True)
        if args.json:
            print(json.dumps({"status": "ok", "name": name, "path": str(profile_dir)}))
        else:
            print(f"Created profile: {name}")
        return 0

    elif action == "delete":
        name = args.profile_name
        if not name:
            print("error: Profile name required")
            return 1
        profile_dir = get_profile_dir(name)
        if not profile_dir.exists():
            print(f"error: Profile '{name}' does not exist")
            return 1
        # Safety: don't delete if browser is using this profile
        state = read_state()
        if state and state.get("profile_dir") == str(profile_dir):
            print(f"error: Profile '{name}' is currently in use by the running browser")
            return 1
        shutil.rmtree(profile_dir)
        # If this was the default, reset to 'default'
        config = read_profiles_config()
        if config.get("default_profile") == name:
            config["default_profile"] = DEFAULT_PROFILE_NAME
            write_profiles_config(config)
        if args.json:
            print(json.dumps({"status": "ok", "deleted": name}))
        else:
            print(f"Deleted profile: {name}")
        return 0

    elif action == "default":
        name = args.profile_name
        config = read_profiles_config()
        if not name:
            # Get current default
            default = config.get("default_profile", DEFAULT_PROFILE_NAME)
            if args.json:
                print(json.dumps({"status": "ok", "default": default}))
            else:
                print(f"Default profile: {default}")
            return 0
        # Set new default
        profile_dir = get_profile_dir(name)
        if not profile_dir.exists():
            print(f"error: Profile '{name}' does not exist")
            return 1
        config["default_profile"] = name
        write_profiles_config(config)
        if args.json:
            print(json.dumps({"status": "ok", "default": name}))
        else:
            print(f"Default profile set to: {name}")
        return 0

    elif action == "clone":
        src = args.profile_name
        dst = args.clone_dest
        if not src or not dst:
            print("error: Source and destination profile names required")
            return 1
        src_dir = get_profile_dir(src)
        dst_dir = get_profile_dir(dst)
        if not src_dir.exists():
            print(f"error: Source profile '{src}' does not exist")
            return 1
        if dst_dir.exists():
            print(f"error: Destination profile '{dst}' already exists")
            return 1
        shutil.copytree(src_dir, dst_dir)
        if args.json:
            print(json.dumps({"status": "ok", "source": src, "destination": dst}))
        else:
            print(f"Cloned profile: {src} -> {dst}")
        return 0

    else:
        print(f"error: Unknown profile action: {action}")
        return 1


# ---------------------------------------------------------------------------
# Argparse setup
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Ghost Browser Daemon - Undetected Chrome for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start                          Start in background (daemon mode)
  %(prog)s start --headless               Run headless
  %(prog)s start --profile work           Start with "work" profile
  %(prog)s start --extension /path/ext    Start with Chrome extension
  %(prog)s start --proxy socks5://1.2.3.4:1080  Start with proxy
  %(prog)s stop                           Stop the browser
  %(prog)s status                         Check if running
  %(prog)s status --json                  Status as JSON

Navigation & Tabs:
  %(prog)s navigate <url>                 Navigate to URL
  %(prog)s tabs                           List open tabs
  %(prog)s close-tab <ID>                 Close a tab
  %(prog)s activate-tab <ID>              Switch to a tab
  %(prog)s wait-ready --timeout 10        Wait for page to fully load

LLM-Friendly (use these instead of raw HTML/CSS selectors):
  %(prog)s page-summary                   Quick page overview (~10 tokens)
  %(prog)s elements                       List all buttons/links/inputs
  %(prog)s elements --form-only           List only form fields
  %(prog)s readable                       Full page as markdown
  %(prog)s readable --max-length 5000     Limit markdown length
  %(prog)s interact click "Sign In"       Click by visible text
  %(prog)s interact type "Email" --type-text "a@b.com"  Type by label
  %(prog)s fill-form '{"email":"a@b.com","password":"x"}' --submit
  %(prog)s hover "Menu" --by-text         Hover by visible text

Page Interaction:
  %(prog)s screenshot [--output PATH]     Capture screenshot
  %(prog)s content                        Get page HTML
  %(prog)s eval "document.title"          Execute JavaScript
  %(prog)s click "button.submit"          Click by CSS selector
  %(prog)s type "input#email" "a@b.com"   Type by CSS selector
  %(prog)s find "h1"                      Find elements by selector
  %(prog)s scroll --down                  Scroll page
  %(prog)s wait ".loaded" --timeout 10    Wait for element
  %(prog)s hover ".dropdown"              Hover by CSS selector
  %(prog)s pdf --output page.pdf          Save page as PDF
  %(prog)s upload photo.jpg               Upload file

Cookies & Data:
  %(prog)s cookies                        List cookies
  %(prog)s set-cookie name value          Set a cookie
  %(prog)s clear-cookies                  Clear all cookies
  %(prog)s save-cookies --file out.json   Export cookies
  %(prog)s load-cookies cookies.json      Import cookies
  %(prog)s storage list                   List localStorage entries
  %(prog)s storage get <key>              Get a storage value
  %(prog)s storage set <key> <value>      Set a storage value
  %(prog)s storage list --session         List sessionStorage instead
  %(prog)s session save mysite            Save full auth state
  %(prog)s session load mysite            Restore full auth state

Debugging:
  %(prog)s network-log --limit 20         View network requests
  %(prog)s network-log --filter api       Filter by URL
  %(prog)s console-log                    View JS console output
  %(prog)s console-log --level error      Show only errors

Window & Downloads:
  %(prog)s window --size 1920x1080        Resize window
  %(prog)s download <url> --output f.pdf  Download file

Cloudflare:
  %(prog)s cf-solve                       Auto-detect and solve CF challenges (all tabs)
  %(prog)s cf-solve --tab <ID>            Solve on specific tab
  %(prog)s cf-solve --json                JSON output

Profiles:
  %(prog)s profile list                   List profiles
  %(prog)s profile create <name>          Create profile
  %(prog)s profile delete <name>          Delete profile
  %(prog)s profile default [name]         Get/set default profile
  %(prog)s profile clone <src> <dst>      Clone a profile

Note: CDP port is auto-assigned. Use 'status' for the actual port.
      CF challenges are also auto-solved in the background every 3 seconds.
      Network and console logging are always-on in the background.
      All commands support --json for machine-readable output.
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # --- start ---
    start_parser = subparsers.add_parser("start", help="Start ghost browser")
    start_parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    start_parser.add_argument("--profile", type=str, default=None, help="Profile name to use")
    start_parser.add_argument("--no-daemon", dest="daemon", action="store_false", help="Run in foreground")
    start_parser.add_argument("--extension", action="append", default=[], help="Path to unpacked extension (can be repeated)")
    start_parser.add_argument("--proxy", type=str, default=None, help="Proxy server URL (e.g. socks5://127.0.0.1:1080)")
    start_parser.set_defaults(daemon=True, func=cmd_start)

    # --- stop ---
    stop_parser = subparsers.add_parser("stop", help="Stop ghost browser")
    stop_parser.set_defaults(func=cmd_stop)

    # --- status ---
    status_parser = subparsers.add_parser("status", help="Check browser status")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON")
    status_parser.set_defaults(func=cmd_status)

    # --- health ---
    health_parser = subparsers.add_parser("health", help="Quick health check")
    health_parser.set_defaults(func=cmd_health)

    # --- tabs ---
    tabs_parser = subparsers.add_parser("tabs", help="List open browser tabs")
    tabs_parser.add_argument("--json", action="store_true", help="Output as JSON")
    tabs_parser.set_defaults(func=cmd_tabs)

    # --- navigate ---
    nav_parser = subparsers.add_parser("navigate", help="Navigate to URL")
    nav_parser.add_argument("url", help="URL to navigate to")
    nav_parser.add_argument("--force-new", action="store_true", help="Always open new tab")
    nav_parser.add_argument("--exact", action="store_true", help="Require exact URL match")
    nav_parser.add_argument("--json", action="store_true", help="Output as JSON")
    nav_parser.set_defaults(func=cmd_navigate)

    # --- screenshot ---
    ss_parser = subparsers.add_parser("screenshot", help="Capture page screenshot")
    ss_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    ss_parser.add_argument("--output", "-o", type=str, default=None, help="Output file path")
    ss_parser.add_argument("--json", action="store_true", help="Output as JSON")
    ss_parser.set_defaults(func=cmd_screenshot)

    # --- content ---
    content_parser = subparsers.add_parser("content", help="Get page HTML content")
    content_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    content_parser.add_argument("--json", action="store_true", help="Output as JSON")
    content_parser.set_defaults(func=cmd_content)

    # --- eval ---
    eval_parser = subparsers.add_parser("eval", help="Execute JavaScript")
    eval_parser.add_argument("js", help="JavaScript code to execute")
    eval_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    eval_parser.add_argument("--json", action="store_true", help="Output as JSON")
    eval_parser.set_defaults(func=cmd_eval)

    # --- click ---
    click_parser = subparsers.add_parser("click", help="Click an element")
    click_parser.add_argument("selector", help="CSS selector of element to click")
    click_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    click_parser.add_argument("--json", action="store_true", help="Output as JSON")
    click_parser.set_defaults(func=cmd_click)

    # --- type ---
    type_parser = subparsers.add_parser("type", help="Type text into an element")
    type_parser.add_argument("selector", help="CSS selector of input element")
    type_parser.add_argument("text", help="Text to type")
    type_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    type_parser.add_argument("--json", action="store_true", help="Output as JSON")
    type_parser.set_defaults(func=cmd_type)

    # --- find ---
    find_parser = subparsers.add_parser("find", help="Find elements by selector")
    find_parser.add_argument("selector", help="CSS selector")
    find_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    find_parser.add_argument("--json", action="store_true", help="Output as JSON")
    find_parser.set_defaults(func=cmd_find)

    # --- scroll ---
    scroll_parser = subparsers.add_parser("scroll", help="Scroll the page")
    scroll_group = scroll_parser.add_mutually_exclusive_group()
    scroll_group.add_argument("--down", action="store_true", default=True, help="Scroll down (default)")
    scroll_group.add_argument("--up", action="store_true", help="Scroll up")
    scroll_group.add_argument("--to", type=int, default=None, metavar="Y", help="Scroll to Y position")
    scroll_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    scroll_parser.add_argument("--json", action="store_true", help="Output as JSON")
    scroll_parser.set_defaults(func=cmd_scroll)

    # --- wait ---
    wait_parser = subparsers.add_parser("wait", help="Wait for element to appear")
    wait_parser.add_argument("selector", help="CSS selector to wait for")
    wait_parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds (default: 30)")
    wait_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    wait_parser.add_argument("--json", action="store_true", help="Output as JSON")
    wait_parser.set_defaults(func=cmd_wait)

    # --- close-tab ---
    close_parser = subparsers.add_parser("close-tab", help="Close a browser tab")
    close_parser.add_argument("tab_id", help="Tab ID to close")
    close_parser.add_argument("--json", action="store_true", help="Output as JSON")
    close_parser.set_defaults(func=cmd_close_tab)

    # --- activate-tab ---
    activate_parser = subparsers.add_parser("activate-tab", help="Switch to a browser tab")
    activate_parser.add_argument("tab_id", help="Tab ID to activate")
    activate_parser.add_argument("--json", action="store_true", help="Output as JSON")
    activate_parser.set_defaults(func=cmd_activate_tab)

    # --- cookies ---
    cookies_parser = subparsers.add_parser("cookies", help="List browser cookies")
    cookies_parser.add_argument("--domain", type=str, default=None, help="Filter by domain")
    cookies_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    cookies_parser.add_argument("--json", action="store_true", help="Output as JSON")
    cookies_parser.set_defaults(func=cmd_cookies)

    # --- set-cookie ---
    setcookie_parser = subparsers.add_parser("set-cookie", help="Set a browser cookie")
    setcookie_parser.add_argument("name", help="Cookie name")
    setcookie_parser.add_argument("value", help="Cookie value")
    setcookie_parser.add_argument("--domain", type=str, default=None, help="Cookie domain")
    setcookie_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    setcookie_parser.add_argument("--json", action="store_true", help="Output as JSON")
    setcookie_parser.set_defaults(func=cmd_set_cookie)

    # --- clear-cookies ---
    clearcookies_parser = subparsers.add_parser("clear-cookies", help="Clear browser cookies")
    clearcookies_parser.add_argument("--domain", type=str, default=None, help="Clear only for domain")
    clearcookies_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    clearcookies_parser.add_argument("--json", action="store_true", help="Output as JSON")
    clearcookies_parser.set_defaults(func=cmd_clear_cookies)

    # --- window ---
    window_parser = subparsers.add_parser("window", help="Resize/reposition browser window")
    window_parser.add_argument("--size", type=str, default=None, metavar="WxH", help="Window size (e.g. 1920x1080)")
    window_parser.add_argument("--position", type=str, default=None, metavar="XxY", help="Window position (e.g. 0x0)")
    window_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    window_parser.add_argument("--json", action="store_true", help="Output as JSON")
    window_parser.set_defaults(func=cmd_window)

    # --- download ---
    download_parser = subparsers.add_parser("download", help="Download a file via the browser")
    download_parser.add_argument("url", help="URL to download")
    download_parser.add_argument("--output", "-o", type=str, default=None, help="Output file path")
    download_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    download_parser.add_argument("--json", action="store_true", help="Output as JSON")
    download_parser.set_defaults(func=cmd_download)

    # --- profile ---
    profile_parser = subparsers.add_parser("profile", help="Manage browser profiles")
    profile_parser.add_argument("profile_action", choices=["list", "create", "delete", "default", "clone"],
                                help="Profile action")
    profile_parser.add_argument("profile_name", nargs="?", default=None, help="Profile name")
    profile_parser.add_argument("clone_dest", nargs="?", default=None, help="Destination name (for clone)")
    profile_parser.add_argument("--json", action="store_true", help="Output as JSON")
    profile_parser.set_defaults(func=cmd_profile)

    # --- save-cookies ---
    savecookies_parser = subparsers.add_parser("save-cookies", help="Export cookies to JSON file")
    savecookies_parser.add_argument("--file", "-f", type=str, default=None, help="Output file path")
    savecookies_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    savecookies_parser.add_argument("--json", action="store_true", help="Output as JSON")
    savecookies_parser.set_defaults(func=cmd_save_cookies)

    # --- load-cookies ---
    loadcookies_parser = subparsers.add_parser("load-cookies", help="Import cookies from JSON file")
    loadcookies_parser.add_argument("file", help="Cookie JSON file to import")
    loadcookies_parser.add_argument("--json", action="store_true", help="Output as JSON")
    loadcookies_parser.set_defaults(func=cmd_load_cookies)

    # --- cf-solve ---
    cfsolve_parser = subparsers.add_parser("cf-solve", help="Detect and solve Cloudflare challenges")
    cfsolve_parser.add_argument("--tab", type=str, default=None, help="Tab ID (default: all tabs)")
    cfsolve_parser.add_argument("--json", action="store_true", help="Output as JSON")
    cfsolve_parser.set_defaults(func=cmd_cf_solve)

    # --- readable ---
    readable_parser = subparsers.add_parser("readable", help="Get page content as LLM-friendly markdown")
    readable_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    readable_parser.add_argument("--max-length", type=int, default=10000, help="Max markdown length (default: 10000)")
    readable_parser.add_argument("--json", action="store_true", help="Output as JSON")
    readable_parser.set_defaults(func=cmd_readable)

    # --- elements ---
    elements_parser = subparsers.add_parser("elements", help="List all interactive page elements (LLM-optimized)")
    elements_parser.add_argument("--form-only", action="store_true", help="Only show form inputs (skip links/buttons)")
    elements_parser.add_argument("--limit", type=int, default=100, help="Max elements to return (default: 100)")
    elements_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    elements_parser.add_argument("--json", action="store_true", help="Output as JSON")
    elements_parser.set_defaults(func=cmd_elements)

    # --- page-summary ---
    pagesummary_parser = subparsers.add_parser("page-summary", help="Compact page overview for LLM situational awareness")
    pagesummary_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    pagesummary_parser.add_argument("--json", action="store_true", help="Output as JSON")
    pagesummary_parser.set_defaults(func=cmd_page_summary)

    # --- interact ---
    interact_parser = subparsers.add_parser("interact", help="Click/type by visible text (LLM-friendly)")
    interact_parser.add_argument("action", choices=["click", "type"], help="Action to perform")
    interact_parser.add_argument("text", help="Visible text to match (button label, placeholder, etc.)")
    interact_parser.add_argument("--type-text", type=str, default=None, help="Text to type (required for type action)")
    interact_parser.add_argument("--index", type=int, default=None, help="Which match to use if multiple (default: 0)")
    interact_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    interact_parser.add_argument("--json", action="store_true", help="Output as JSON")
    interact_parser.set_defaults(func=cmd_interact)

    # --- fill-form ---
    fillform_parser = subparsers.add_parser("fill-form", help="Auto-fill form fields from JSON")
    fillform_parser.add_argument("fields", help='JSON string of field:value pairs, e.g. \'{"email":"a@b.com","password":"x"}\'')
    fillform_parser.add_argument("--submit", action="store_true", help="Auto-click submit button after filling")
    fillform_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    fillform_parser.add_argument("--json", action="store_true", help="Output as JSON")
    fillform_parser.set_defaults(func=cmd_fill_form)

    # --- storage ---
    storage_parser = subparsers.add_parser("storage", help="Manage localStorage/sessionStorage")
    storage_parser.add_argument("storage_action", choices=["list", "get", "set", "delete", "clear"],
                                help="Storage action")
    storage_parser.add_argument("key", nargs="?", default=None, help="Storage key (for get/set/delete)")
    storage_parser.add_argument("value", nargs="?", default=None, help="Value to set (for set)")
    storage_parser.add_argument("--session", action="store_true", help="Use sessionStorage instead of localStorage")
    storage_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    storage_parser.add_argument("--json", action="store_true", help="Output as JSON")
    storage_parser.set_defaults(func=cmd_storage)

    # --- wait-ready ---
    waitready_parser = subparsers.add_parser("wait-ready", help="Wait for page to fully load")
    waitready_parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds (default: 30)")
    waitready_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    waitready_parser.add_argument("--json", action="store_true", help="Output as JSON")
    waitready_parser.set_defaults(func=cmd_wait_ready)

    # --- hover ---
    hover_parser = subparsers.add_parser("hover", help="Hover over an element")
    hover_parser.add_argument("target", help="CSS selector or visible text")
    hover_parser.add_argument("--by-text", action="store_true", help="Match by visible text instead of CSS selector")
    hover_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    hover_parser.add_argument("--json", action="store_true", help="Output as JSON")
    hover_parser.set_defaults(func=cmd_hover)

    # --- pdf ---
    pdf_parser = subparsers.add_parser("pdf", help="Print page to PDF")
    pdf_parser.add_argument("--output", "-o", type=str, default=None, help="Output file path")
    pdf_parser.add_argument("--landscape", action="store_true", help="Landscape orientation")
    pdf_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    pdf_parser.add_argument("--json", action="store_true", help="Output as JSON")
    pdf_parser.set_defaults(func=cmd_pdf)

    # --- upload ---
    upload_parser = subparsers.add_parser("upload", help="Upload a file to a file input")
    upload_parser.add_argument("file_path", help="Path to file to upload")
    upload_parser.add_argument("--selector", type=str, default=None, help="CSS selector of file input (default: auto-detect)")
    upload_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    upload_parser.add_argument("--json", action="store_true", help="Output as JSON")
    upload_parser.set_defaults(func=cmd_upload)

    # --- session ---
    session_parser = subparsers.add_parser("session", help="Save/load full auth state (cookies + storage)")
    session_parser.add_argument("session_action", choices=["save", "load"], help="Session action")
    session_parser.add_argument("name", help="Session name")
    session_parser.add_argument("--tab", type=str, default=None, help="Tab ID")
    session_parser.add_argument("--json", action="store_true", help="Output as JSON")
    session_parser.set_defaults(func=cmd_session)

    # --- network-log ---
    netlog_parser = subparsers.add_parser("network-log", help="View captured network requests")
    netlog_parser.add_argument("--filter", type=str, default=None, help="Filter by URL substring")
    netlog_parser.add_argument("--limit", type=int, default=50, help="Max entries to show (default: 50)")
    netlog_parser.add_argument("--clear", action="store_true", help="Clear the log after reading")
    netlog_parser.add_argument("--json", action="store_true", help="Output as JSON")
    netlog_parser.set_defaults(func=cmd_network_log)

    # --- console-log ---
    consolelog_parser = subparsers.add_parser("console-log", help="View captured JS console output")
    consolelog_parser.add_argument("--level", type=str, default=None, help="Filter by level (error, warning, info, log)")
    consolelog_parser.add_argument("--limit", type=int, default=50, help="Max entries to show (default: 50)")
    consolelog_parser.add_argument("--clear", action="store_true", help="Clear the log after reading")
    consolelog_parser.add_argument("--json", action="store_true", help="Output as JSON")
    consolelog_parser.set_defaults(func=cmd_console_log)

    # --- install-extension ---
    installext_parser = subparsers.add_parser("install-extension",
        help="Install Chrome extension from Web Store URL/ID or local .crx file")
    installext_parser.add_argument("source", help="Chrome Web Store URL, extension ID, or path to .crx file")
    installext_parser.add_argument("--name", type=str, default=None, help="Custom folder name for the extension")
    installext_parser.add_argument("--force", action="store_true", help="Overwrite if already installed")
    installext_parser.add_argument("--json", action="store_true", help="Output as JSON")
    installext_parser.set_defaults(func=cmd_install_extension)

    # --- list-extensions ---
    listext_parser = subparsers.add_parser("list-extensions", help="List all installed extensions")
    listext_parser.add_argument("--json", action="store_true", help="Output as JSON")
    listext_parser.set_defaults(func=cmd_list_extensions)

    # --- remove-extension ---
    removeext_parser = subparsers.add_parser("remove-extension", help="Remove an installed extension")
    removeext_parser.add_argument("name", help="Extension folder name or extension name")
    removeext_parser.add_argument("--json", action="store_true", help="Output as JSON")
    removeext_parser.set_defaults(func=cmd_remove_extension)

    # --- load-extension ---
    loadext_parser = subparsers.add_parser("load-extension",
        help="Load an extension into the running browser (macOS only)")
    loadext_parser.add_argument("name", nargs="?", default=None,
        help="Extension folder name (from extensions/ dir) or path. Loads all if omitted.")
    loadext_parser.add_argument("--json", action="store_true", help="Output as JSON")
    loadext_parser.set_defaults(func=cmd_load_extension)

    # --- unload-extension ---
    unloadext_parser = subparsers.add_parser("unload-extension",
        help="Unload (remove) an extension from the running browser (macOS only)")
    unloadext_parser.add_argument("name", help="Extension folder name or display name")
    unloadext_parser.add_argument("--json", action="store_true", help="Output as JSON")
    unloadext_parser.set_defaults(func=cmd_unload_extension)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    ensure_state_dir()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
