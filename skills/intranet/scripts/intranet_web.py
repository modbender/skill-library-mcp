#!/usr/bin/env python3
"""intranet_web.py

Lightweight HTTP file server with plugin support and CGI execution.

Features:
- Serves static files from a configurable webroot directory
- Plugin system: mount external directories at URL prefixes via config.json
- CGI execution limited to index.py files only (webroot or plugin roots)
- Token authentication with cookie-based sessions
- Host allowlist for restricting access by hostname
- Symlinks followed; resolved targets must stay within their base directory

Security model:
- Only files named index.py can execute (must have +x bit)
- All other .py files return 403 Forbidden
- Plugins are explicitly registered in config.json (no auto-discovery)
- Path traversal protection on all requests
- Symlinks followed with path containment (resolved target must stay in base directory)
"""

import hashlib
import hmac
import html
import http.cookies
import json as _json
import mimetypes
import os
import posixpath
import secrets
import subprocess
import sys
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Optional

# Session cookie name and max age (30 days)
_COOKIE_NAME = "intranet_session"
_COOKIE_MAX_AGE = 30 * 24 * 3600

# CGI script timeout (seconds)
_CGI_TIMEOUT = 30


def _find_workspace_root() -> Path:
    """Walk up from script location to find workspace root (parent of 'skills/')."""
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


# Initialize mimetypes
mimetypes.init()


# ---------------------------------------------------------------------------
# Ignore-list support (for directory listings)
# ---------------------------------------------------------------------------

def _read_ignore_list(path: Path) -> set[str]:
    """Read a simple ignore file (one token per line, # comments, case-insensitive)."""
    try:
        if not path.exists() or not path.is_file():
            return set()
        out: set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            s = (line or "").strip()
            if not s or s.startswith("#"):
                continue
            out.add(s.lower())
        return out
    except Exception:
        return set()


def _collect_ignore_tokens(root_dir: Path, dir_path: Path, url_path: str) -> set[str]:
    """Collect ignore tokens from .intranetignore files up to the plugin/webroot boundary."""
    tokens: set[str] = set()
    root_resolved = root_dir.resolve()
    cur = dir_path.resolve()

    if cur == root_resolved or root_resolved in cur.parents:
        p = cur
        while True:
            tokens |= _read_ignore_list(p / ".intranetignore")
            # Also support legacy .bankerignore for banker plugin
            tokens |= _read_ignore_list(p / ".bankerignore")
            if p == root_resolved:
                break
            p = p.parent

    return tokens


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _h(s) -> str:
    """HTML escape helper."""
    return html.escape("" if s is None else str(s), quote=True)


def _bytes_format(n: int) -> str:
    """Format bytes as human-readable size."""
    for unit, div in (("B", 1), ("KB", 1024), ("MB", 1024**2), ("GB", 1024**3)):
        if n < 1024 or unit == "GB":
            if unit == "B":
                return f"{n} B"
            return f"{n / div:.2f} {unit}"
    return f"{n} B"


# ---------------------------------------------------------------------------
# Path safety
# ---------------------------------------------------------------------------

def _safe_path(base: Path, rel: str) -> Optional[Path]:
    """Resolve a relative URL path within a base directory.

    Returns the resolved Path if it stays within base, None otherwise.
    Symlinks are allowed as long as the resolved target stays within base.
    """
    rel = rel.lstrip("/")
    base_res = base.resolve()
    candidate = (base / rel).resolve()
    if candidate == base_res or base_res in candidate.parents:
        return candidate
    return None


# ---------------------------------------------------------------------------
# HTML page template
# ---------------------------------------------------------------------------

def _page(title: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_h(title)}</title>
  <style>
    body {{
      font-family: -apple-system, system-ui, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
      margin: 24px;
      max-width: 1200px;
    }}
    h1 {{ margin-bottom: 8px; }}
    .muted {{ color: #666; font-size: 14px; }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin-top: 16px;
    }}
    th, td {{
      border-bottom: 1px solid #eee;
      padding: 8px 12px;
      text-align: left;
    }}
    th {{
      background: #f8f8f8;
      font-weight: 600;
      position: sticky;
      top: 0;
    }}
    tr:hover td {{ background: #fafafa; }}
    a {{ color: #0066cc; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .icon {{
      display: inline-block;
      width: 20px;
      text-align: center;
      margin-right: 8px;
    }}
    .right {{ text-align: right; }}
  </style>
</head>
<body>
  {body_html}
</body>
</html>"""


# ---------------------------------------------------------------------------
# Server classes
# ---------------------------------------------------------------------------

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP server."""
    daemon_threads = True


class IntranetHandler(BaseHTTPRequestHandler):
    """HTTP request handler with plugin support."""

    server_version = "intranet-web/2.0"

    # ------------------------------------------------------------------
    # Auth: host check, token/cookie
    # ------------------------------------------------------------------

    def _check_host(self) -> bool:
        allowed = getattr(self.server, "allowed_hosts", None)
        if not allowed:
            return True
        host = (self.headers.get("Host") or "").lower().split(":")[0]
        if host in allowed:
            return True
        self._send_plain(HTTPStatus.FORBIDDEN, "403 Forbidden\n")
        return False

    def _make_session_mac(self, token: str) -> str:
        secret = getattr(self.server, "session_secret", b"")
        return hmac.new(secret, token.encode(), hashlib.sha256).hexdigest()

    def _get_cookie(self, name: str) -> str | None:
        cookie_header = self.headers.get("Cookie", "")
        if not cookie_header:
            return None
        try:
            cookies = http.cookies.SimpleCookie(cookie_header)
            morsel = cookies.get(name)
            return morsel.value if morsel else None
        except Exception:
            return None

    def _set_session_cookie(self, mac: str) -> str:
        c = http.cookies.SimpleCookie()
        c[_COOKIE_NAME] = mac
        c[_COOKIE_NAME]["httponly"] = True
        c[_COOKIE_NAME]["samesite"] = "Strict"
        c[_COOKIE_NAME]["max-age"] = str(_COOKIE_MAX_AGE)
        c[_COOKIE_NAME]["path"] = "/"
        return c[_COOKIE_NAME].OutputString()

    def _check_auth(self) -> bool:
        required_token = getattr(self.server, "auth_token", None)
        if not required_token:
            return True

        expected_mac = self._make_session_mac(required_token)

        # Session cookie
        cookie_val = self._get_cookie(_COOKIE_NAME)
        if cookie_val and hmac.compare_digest(cookie_val, expected_mac):
            return True

        # Bearer header
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer ") and hmac.compare_digest(auth_header[7:], required_token):
            return True

        # Query param → set cookie + redirect
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        token_values = params.get("token", [])
        if token_values and hmac.compare_digest(token_values[0], required_token):
            remaining = {k: v for k, v in params.items() if k != "token"}
            clean_query = urllib.parse.urlencode(remaining, doseq=True)
            clean_path = parsed.path + ("?" + clean_query if clean_query else "")
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", clean_path)
            self.send_header("Set-Cookie", self._set_session_cookie(expected_mac))
            self.send_header("Content-Length", "0")
            self.end_headers()
            return False

        # Denied
        self.send_response(HTTPStatus.UNAUTHORIZED)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("WWW-Authenticate", "Bearer")
        body = b"401 Unauthorized\n"
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return False

    # ------------------------------------------------------------------
    # Request routing
    # ------------------------------------------------------------------

    def do_HEAD(self):
        self._head_request = True
        self.do_GET()

    def do_GET(self):
        if not hasattr(self, "_head_request"):
            self._head_request = False
        if not self._check_host():
            return
        if not self._check_auth():
            return

        parsed = urllib.parse.urlparse(self.path)
        url_path = urllib.parse.unquote(parsed.path)

        # Try plugin routing first
        plugins: dict[str, Path] = getattr(self.server, "plugins", {})
        for prefix, plugin_dir in plugins.items():
            url_prefix = f"/{prefix}"
            if url_path == url_prefix or url_path.startswith(url_prefix + "/"):
                # Redirect /prefix to /prefix/
                if url_path == url_prefix:
                    self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                    self.send_header("Location", url_prefix + "/")
                    self.end_headers()
                    return
                sub_path = url_path[len(url_prefix):]  # includes leading /
                self._serve_from_dir(plugin_dir, sub_path, url_path, is_plugin=True, plugin_prefix=prefix)
                return

        # Fall back to webroot
        self._serve_from_dir(self.server.root_dir, url_path, url_path, is_plugin=False)

    def _serve_from_dir(self, base_dir: Path, rel_path: str, url_path: str, is_plugin: bool, plugin_prefix: str = ""):
        """Serve a request from a directory (webroot or plugin).

        For plugins: index.py at the plugin root handles ALL sub-paths as CGI.
        For webroot: index.py in any directory handles that directory's requests.
        """
        cgi_enabled = getattr(self.server, "cgi_enabled", False)

        # Resolve the file path (strict containment) — try static files first
        fs_path = _safe_path(base_dir, rel_path)
        if fs_path is None:
            self._send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            return

        if fs_path.exists():
            if fs_path.is_dir():
                # Redirect dirs without trailing /
                if not url_path.endswith("/"):
                    self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                    self.send_header("Location", url_path + "/")
                    self.end_headers()
                    return

                # Try index.py (CGI, if enabled) → index.html → directory listing
                if cgi_enabled:
                    index_py = fs_path / "index.py"
                    if index_py.is_file() and index_py.name == "index.py":
                        # Containment: resolved script must stay within base dir
                        resolved_cgi = index_py.resolve()
                        base_res = base_dir.resolve()
                        if base_res not in resolved_cgi.parents:
                            self._send_error(HTTPStatus.FORBIDDEN, "CGI script escapes base directory")
                            return
                        self._execute_cgi(index_py, url_path)
                        return

                index_html = fs_path / "index.html"
                if index_html.is_file():
                    self._serve_file(index_html)
                    return

                self._serve_directory(fs_path, url_path)
                return

            if fs_path.is_file():
                # Block all .py files that aren't index.py
                if fs_path.suffix == ".py":
                    self._send_error(HTTPStatus.FORBIDDEN, "Forbidden")
                    return
                self._serve_file(fs_path)
                return

        # Plugin CGI fallback: if no static file matched, try plugin-root index.py
        if is_plugin and cgi_enabled:
            index_py = base_dir / "index.py"
            if index_py.is_file() and index_py.name == "index.py":
                resolved = index_py.resolve()
                if not self._verify_cgi_hash(resolved, plugin_prefix):
                    self._send_error(HTTPStatus.FORBIDDEN, "CGI hash mismatch")
                    return
                self._execute_cgi(index_py, url_path)
                return

        self._send_error(HTTPStatus.NOT_FOUND, "Not Found")

    # ------------------------------------------------------------------
    # CGI execution (index.py only)
    # ------------------------------------------------------------------

    def _verify_cgi_hash(self, script_path: Path, plugin_prefix: str) -> bool:
        """Verify a CGI script's SHA-256 hash against the configured hash.

        If no hash is configured for this plugin, CGI is blocked (fail-closed).
        For webroot CGI, use plugin_prefix="" (no hash required for webroot).
        """
        if not plugin_prefix:
            return True  # Webroot CGI doesn't require hash (it's user's own files)

        expected_hashes = getattr(self.server, "plugin_hashes", {})
        expected = expected_hashes.get(plugin_prefix)
        if not expected:
            # No hash configured → block CGI for this plugin
            print(f"[intranet] CGI blocked for plugin '{plugin_prefix}' — no hash in config.json")
            return False

        actual = hashlib.sha256(script_path.read_bytes()).hexdigest()
        if actual != expected:
            print(f"[intranet] CGI hash mismatch for plugin '{plugin_prefix}': expected {expected[:12]}..., got {actual[:12]}...")
            return False
        return True

    def _execute_cgi(self, script_path: Path, url_path: str):
        """Execute an index.py script as CGI."""
        actual_script = script_path.resolve()

        if not actual_script.is_file():
            self._send_error(HTTPStatus.NOT_FOUND, "Script not found")
            return

        if not os.access(actual_script, os.X_OK):
            self._send_error(HTTPStatus.FORBIDDEN, "Script is not executable")
            return

        parsed = urllib.parse.urlparse(self.path)

        env = os.environ.copy()
        env.update({
            "REQUEST_METHOD": "GET",
            "SCRIPT_NAME": url_path,
            "PATH_INFO": url_path,
            "QUERY_STRING": parsed.query or "",
            "SERVER_NAME": self.server.server_address[0],
            "SERVER_PORT": str(self.server.server_address[1]),
            "SERVER_PROTOCOL": self.request_version,
            "HTTP_HOST": self.headers.get("Host", ""),
            "HTTP_ACCEPT": self.headers.get("Accept", ""),
            "HTTP_USER_AGENT": self.headers.get("User-Agent", ""),
            "DOCUMENT_ROOT": str(self.server.root_dir),
        })

        try:
            result = subprocess.run(
                [sys.executable, str(actual_script)],
                capture_output=True,
                timeout=_CGI_TIMEOUT,
                env=env,
                cwd=str(script_path.parent.resolve()),
            )

            output = result.stdout

            # Parse CGI headers
            if b"\r\n\r\n" in output:
                header_data, body = output.split(b"\r\n\r\n", 1)
            elif b"\n\n" in output:
                header_data, body = output.split(b"\n\n", 1)
            else:
                header_data = b""
                body = output

            status_code = HTTPStatus.OK
            content_type = "text/html; charset=utf-8"
            extra_headers = []

            if header_data:
                for line in header_data.decode("utf-8", errors="replace").split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    if line.lower().startswith("status:"):
                        try:
                            status_code = int(line.split(":", 1)[1].strip().split()[0])
                        except (ValueError, IndexError):
                            pass
                    elif line.lower().startswith("content-type:"):
                        content_type = line.split(":", 1)[1].strip()
                    elif ":" in line:
                        key, val = line.split(":", 1)
                        extra_headers.append((key.strip(), val.strip()))

            self.send_response(status_code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            for key, val in extra_headers:
                if key.lower() not in ("status", "content-type", "content-length"):
                    self.send_header(key, val)
            self.end_headers()
            self.wfile.write(body)

        except subprocess.TimeoutExpired:
            self._send_error(HTTPStatus.GATEWAY_TIMEOUT, "Script timed out")
        except Exception as e:
            self._send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Script error: {e}")

    # ------------------------------------------------------------------
    # Static file serving
    # ------------------------------------------------------------------

    def _serve_file(self, file_path: Path):
        try:
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = "application/octet-stream"
            data = file_path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if not getattr(self, "_head_request", False):
                self.wfile.write(data)
        except OSError as e:
            self._send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error reading file: {e}")

    # ------------------------------------------------------------------
    # Directory listing
    # ------------------------------------------------------------------

    def _serve_directory(self, dir_path: Path, url_path: str):
        try:
            entries = []

            if url_path != "/":
                parent_url = posixpath.dirname(url_path.rstrip("/")) + "/"
                entries.append({
                    "name": "..",
                    "url": parent_url,
                    "is_dir": True,
                    "size": "",
                    "icon": "📁",
                })

            ignore_tokens = _collect_ignore_tokens(dir_path, dir_path, url_path)

            for entry in sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                if entry.name.startswith("."):
                    continue
                if ignore_tokens and entry.name.lower() in ignore_tokens:
                    continue
                # Skip broken symlinks
                if entry.is_symlink() and not entry.exists():
                    continue
                # Skip .py files from listings (they're not servable)
                if entry.is_file() and entry.suffix == ".py":
                    continue

                is_dir = entry.is_dir()
                size = ""
                if not is_dir:
                    try:
                        size = _bytes_format(entry.stat().st_size)
                    except OSError:
                        size = "?"

                entry_url = posixpath.join(url_path, urllib.parse.quote(entry.name))
                if is_dir and not entry_url.endswith("/"):
                    entry_url += "/"

                if is_dir:
                    icon = "📁"
                else:
                    suffix = entry.suffix.lower()
                    icon = {
                        ".html": "🌐", ".htm": "🌐",
                        ".md": "📄", ".txt": "📄",
                        ".json": "📋", ".xml": "📋", ".yaml": "📋", ".yml": "📋",
                        ".jpg": "🖼️", ".jpeg": "🖼️", ".png": "🖼️",
                        ".gif": "🖼️", ".svg": "🖼️", ".webp": "🖼️",
                        ".pdf": "📕",
                        ".zip": "📦", ".tar": "📦", ".gz": "📦", ".bz2": "📦",
                    }.get(suffix, "📄")

                entries.append({
                    "name": entry.name + ("/" if is_dir else ""),
                    "url": entry_url,
                    "is_dir": is_dir,
                    "size": size,
                    "icon": icon,
                })

            rows = []
            for entry in entries:
                rows.append(
                    f"<tr>"
                    f"<td><span class='icon'>{entry['icon']}</span>"
                    f"<a href='{_h(entry['url'])}'>{_h(entry['name'])}</a></td>"
                    f"<td class='right'>{_h(entry['size'])}</td>"
                    f"</tr>"
                )

            is_root = url_path == "/"
            is_empty = len([e for e in entries if e.get("name") != ".."]) == 0

            if is_root and is_empty:
                body = self._get_empty_root_guide()
            else:
                body = f"""
                <h1>Index of {_h(url_path)}</h1>
                <p class="muted">{_h(str(dir_path))}</p>
                <table>
                  <thead><tr><th>Name</th><th class="right">Size</th></tr></thead>
                  <tbody>
                    {''.join(rows) if rows else '<tr><td colspan="2" class="muted">(empty)</td></tr>'}
                  </tbody>
                </table>
                """

            self._send_html(HTTPStatus.OK, _page(f"Index of {url_path}", body))

        except OSError as e:
            self._send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Error reading directory: {e}")

    # ------------------------------------------------------------------
    # Response helpers
    # ------------------------------------------------------------------

    def _send_html(self, status: int, html_text: str):
        data = html_text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_plain(self, status: int, text: str):
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_error(self, status: int, message: str):
        if status == HTTPStatus.NOT_FOUND:
            body = self._get_404_guide()
        else:
            body = f"<h1>{status} {message}</h1>"
        self._send_html(status, _page(f"{status} {message}", body))

    # ------------------------------------------------------------------
    # Guide pages
    # ------------------------------------------------------------------

    def _get_empty_root_guide(self) -> str:
        root_dir = self.server.root_dir
        plugins = getattr(self.server, "plugins", {})
        plugin_html = ""
        if plugins:
            items = "".join(
                f"<li><a href='/{_h(p)}/'>{_h(p)}</a> → <code>{_h(str(d))}</code></li>"
                for p, d in plugins.items()
            )
            plugin_html = f"""
            <h3>Active Plugins</h3>
            <ul>{items}</ul>
            """

        return f"""
        <h1>Welcome to Intranet</h1>
        <p class="muted">Your local file server is running.</p>
        {plugin_html}
        <h2>Quick Start</h2>
        <p>Root folder: <code>{_h(str(root_dir))}</code></p>
        <p>Add files to the root folder or register plugins in
        <code>config.json</code>.</p>
        <p style="margin-top: 24px; padding: 12px; background: #f0f7ff; border-radius: 4px;">
          <strong>Tip:</strong> Refresh this page after adding content.
        </p>
        """

    def _get_404_guide(self) -> str:
        root_dir = self.server.root_dir
        return f"""
        <h1>404 — Not Found</h1>
        <p>The requested page doesn't exist.</p>
        <p>Root folder: <code>{_h(str(root_dir))}</code></p>
        <p style="margin-top: 24px;"><a href="/">← Back to root</a></p>
        """

    def log_message(self, fmt: str, *args):
        """Suppress logging in daemon mode."""
        pass


# ---------------------------------------------------------------------------
# Server startup
# ---------------------------------------------------------------------------

def _load_config(root_dir: Path) -> dict:
    """Load config.json from the webroot directory."""
    config_file = root_dir / "config.json"
    if not config_file.exists():
        return {}
    try:
        return _json.loads(config_file.read_text())
    except Exception:
        return {}


def run_server(host: str = "127.0.0.1", port: int = 8080, token: str = None):
    """Start the intranet web server."""
    intranet_dir = (_find_workspace_root() / "intranet").resolve()
    if not intranet_dir.exists():
        intranet_dir.mkdir(parents=True, exist_ok=True)

    # Config lives in workspace/intranet/config.json (not served)
    cfg = _load_config(intranet_dir)

    # Webroot is workspace/intranet/www/ (separate from config)
    root_dir = intranet_dir / "www"
    if not root_dir.exists():
        root_dir.mkdir(parents=True, exist_ok=True)

    # Token: --token flag or config.json only (no env var)
    token = token or cfg.get("token")

    # Non-loopback binding requires auth + allowed_hosts
    allowed_hosts_list = cfg.get("allowed_hosts", [])
    if host not in ("127.0.0.1", "localhost", "::1"):
        missing = []
        if not token:
            missing.append("token auth (--token or config.json token)")
        if not allowed_hosts_list:
            missing.append("allowed_hosts in config.json")
        if missing:
            raise SystemExit(f"[intranet] Binding to {host} requires: {' and '.join(missing)}")

    # CGI: off by default, enable via "cgi": true in config.json
    cgi_enabled = cfg.get("cgi", False)

    httpd = ThreadingHTTPServer((host, port), IntranetHandler)
    httpd.root_dir = root_dir
    httpd.auth_token = token
    httpd.session_secret = secrets.token_bytes(32)
    httpd.cgi_enabled = cgi_enabled

    # Allowed hosts
    httpd.allowed_hosts = {h.lower() for h in allowed_hosts_list} if allowed_hosts_list else None

    # Plugins: prefix → resolved directory path (must be inside workspace)
    # Supports both simple format ("prefix": "/path") and extended ("prefix": {"dir": "/path", "hash": "sha256:..."})
    raw_plugins = cfg.get("plugins", {})
    plugins: dict[str, Path] = {}
    plugin_hashes: dict[str, str] = {}  # prefix → expected sha256 hex
    workspace_root = intranet_dir.parent  # intranet_dir is workspace/intranet
    allowed_roots = [workspace_root.resolve()]
    for prefix, value in raw_plugins.items():
        if isinstance(value, dict):
            dir_str = value.get("dir", "")
            raw_hash = value.get("hash", "")
        else:
            dir_str = value
            raw_hash = ""
        p = Path(dir_str).expanduser().resolve()
        p_str = str(p)
        if not any(p_str.startswith(str(a) + "/") or p_str == str(a) for a in allowed_roots):
            print(f"[intranet] WARNING: Skipping plugin '{prefix}' — path '{dir_str}' is outside workspace")
            continue
        clean_prefix = prefix.strip("/")
        if p.is_dir():
            plugins[clean_prefix] = p
            if raw_hash:
                # Accept "sha256:abc..." or plain "abc..."
                h = raw_hash.removeprefix("sha256:").strip().lower()
                plugin_hashes[clean_prefix] = h
    httpd.plugins = plugins
    httpd.plugin_hashes = plugin_hashes

    if cgi_enabled:
        print("[intranet-web] CGI execution enabled")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


def main() -> int:
    """Main entry point for standalone execution."""
    import argparse

    ap = argparse.ArgumentParser(description="Serve local files over HTTP")
    ap.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    ap.add_argument("--port", type=int, default=8080, help="Port to bind to")
    ap.add_argument("--token", default=None, help="Bearer token for authentication")
    args = ap.parse_args()

    intranet_dir = (_find_workspace_root() / "intranet").resolve()
    print(f"[intranet-web] Serving {intranet_dir}/www on http://{args.host}:{args.port}/")
    run_server(args.host, args.port, token=args.token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
