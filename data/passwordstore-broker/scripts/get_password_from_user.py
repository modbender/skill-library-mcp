#!/usr/bin/env python3
import argparse
import base64
import dataclasses
import hashlib
import hmac
import html
import ipaddress
import json
import os
import re
import secrets
import shutil
import socket
import socketserver
import ssl
import struct
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Optional


FORM_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Submit secret</title>
  <style>
    body {{
      margin: 0;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f4f7fb;
      display: grid;
      place-items: center;
      min-height: 100vh;
    }}
    .card {{
      width: min(480px, 92vw);
      background: white;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
      padding: 24px;
    }}
    h1 {{ margin-top: 0; font-size: 1.1rem; }}
    code {{
      background: #eef3fa;
      padding: 2px 6px;
      border-radius: 6px;
      font-size: 0.9em;
    }}
    input[type="password"], input[type="text"] {{
      width: 100%;
      box-sizing: border-box;
      border: 1px solid #d1d9e5;
      border-radius: 8px;
      padding: 10px 12px;
      font-size: 1rem;
      margin-top: 6px;
      margin-bottom: 10px;
    }}
    button {{
      margin-top: 8px;
      width: 100%;
      border: 0;
      border-radius: 8px;
      background: #1d4ed8;
      color: white;
      font-weight: 600;
      padding: 10px 12px;
      cursor: pointer;
    }}
    .hint {{
      color: #4b5563;
      font-size: 0.9rem;
      margin-top: 8px;
    }}
  </style>
</head>
<body>
  <main class="card">
    <h1>Provide secret for <code>{secret_name}</code></h1>
    <form method="POST" action="/submit">
      <input type="hidden" name="token" value="{token}">
      <label for="secret">Secret</label>
      <input type="password" id="secret" name="secret" autocomplete="off" required autofocus>
      {totp_section}
      <button type="submit">Store Secret</button>
    </form>
    <p class="hint">This page can be used once and then expires.</p>
  </main>
</body>
</html>
"""

TOTP_SECTION_TEMPLATE = """
<label for=\"totp\">Authenticator code</label>
<input type=\"text\" id=\"totp\" name=\"totp\" inputmode=\"numeric\" pattern=\"[0-9]{6}\" maxlength=\"6\" autocomplete=\"one-time-code\" required>
"""

OK_TEMPLATE = """<!doctype html>
<html><body style="font-family: sans-serif; padding: 2rem;">
<h2>Secret stored.</h2>
<p>You can close this tab now.</p>
</body></html>"""

FAIL_TEMPLATE = """<!doctype html>
<html><body style="font-family: sans-serif; padding: 2rem;">
<h2>Request failed.</h2>
<p>{message}</p>
</body></html>"""

DEFAULT_TOTP_SECRET_FILE = "~/.passwordstore-broker/totp.secret"
DEFAULT_LOCAL_TIMEOUT = 300
DEFAULT_LAN_TIMEOUT = 120
TOTP_WINDOW_SECONDS = 300
TOTP_MAX_FAILURES = 5
TOTP_LOCKOUT_SECONDS = 300


@dataclasses.dataclass
class AccessConfig:
    mode: str
    bind_host: str
    allowed_net: ipaddress.IPv4Network
    require_totp: bool
    totp_secret: Optional[str]
    timeout_seconds: int


@dataclasses.dataclass
class TotpAttempt:
    failed_at: list[float] = dataclasses.field(default_factory=list)
    locked_until: float = 0.0


def _base32_decode(key: str) -> bytes:
    padding = "=" * ((8 - len(key) % 8) % 8)
    return base64.b32decode(key.upper() + padding, casefold=True)


def _totp_at(secret: str, timestamp: int, step: int = 30, digits: int = 6) -> str:
    key = _base32_decode(secret)
    counter = int(timestamp // step)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = (struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF) % (10**digits)
    return str(code).zfill(digits)


def verify_totp(secret: str, code: str, window: int = 1, step: int = 30, digits: int = 6) -> bool:
    now = int(time.time())
    for drift in range(-window, window + 1):
        if _totp_at(secret, now + drift * step, step=step, digits=digits) == code:
            return True
    return False


def _detect_outbound_ipv4() -> ipaddress.IPv4Address:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            host = sock.getsockname()[0]
    except OSError as exc:
        raise RuntimeError(f"Unable to detect outbound IPv4 address: {exc}") from exc

    try:
        ip = ipaddress.ip_address(host)
    except ValueError as exc:
        raise RuntimeError(f"Detected invalid local IP address: {host}") from exc

    if not isinstance(ip, ipaddress.IPv4Address):
        raise RuntimeError(f"Detected non-IPv4 address ({host}); only IPv4 is supported")

    return ip


def _linux_network_for_ip(local_ip: ipaddress.IPv4Address) -> Optional[ipaddress.IPv4Network]:
    ip_cmd = shutil.which("ip")
    if ip_cmd is None:
        raise RuntimeError("Missing required command 'ip' for Linux LAN detection")

    try:
        route_proc = subprocess.run(
            [ip_cmd, "-j", "route", "get", "1.1.1.1"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or "could not inspect interfaces"
        raise RuntimeError(f"Linux LAN detection failed: {message}") from exc

    try:
        route_info = json.loads(route_proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Linux LAN detection failed: invalid route JSON output") from exc

    if not route_info or not isinstance(route_info, list):
        raise RuntimeError("Linux LAN detection failed: empty route output")

    iface_name = route_info[0].get("dev")
    if not iface_name:
        raise RuntimeError("Linux LAN detection failed: route output missing interface name")

    try:
        addr_proc = subprocess.run(
            [ip_cmd, "-j", "-f", "inet", "addr", "show", "dev", iface_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or "could not read interface addresses"
        raise RuntimeError(f"Linux LAN detection failed: {message}") from exc

    try:
        addr_info = json.loads(addr_proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Linux LAN detection failed: invalid interface JSON output") from exc

    for iface in addr_info:
        for entry in iface.get("addr_info", []):
            if entry.get("family") != "inet":
                continue
            if entry.get("local") != str(local_ip):
                continue
            prefix = entry.get("prefixlen")
            if not isinstance(prefix, int):
                continue
            return ipaddress.ip_network(f"{local_ip}/{prefix}", strict=False)
    return None


def _prefix_from_netmask(mask: str) -> int:
    if mask.startswith("0x"):
        dotted = str(ipaddress.IPv4Address(int(mask, 16)))
    else:
        dotted = mask
    return ipaddress.IPv4Network(f"0.0.0.0/{dotted}").prefixlen


def _macos_network_for_ip(local_ip: ipaddress.IPv4Address) -> Optional[ipaddress.IPv4Network]:
    route_cmd = shutil.which("route")
    if route_cmd is None:
        raise RuntimeError("Missing required command 'route' for macOS LAN detection")

    try:
        route_proc = subprocess.run(
            [route_cmd, "-n", "get", "default"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or "could not inspect default route"
        raise RuntimeError(f"macOS LAN detection failed: {message}") from exc

    iface_name = None
    for line in route_proc.stdout.splitlines():
        if "interface:" in line:
            iface_name = line.split("interface:", 1)[1].strip()
            break

    if not iface_name:
        raise RuntimeError("macOS LAN detection failed: default route missing interface name")

    try:
        proc = subprocess.run(
            ["ifconfig", iface_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or "could not inspect interfaces"
        raise RuntimeError(f"macOS LAN detection failed: {message}") from exc

    inet_pattern = re.compile(r"\sinet\s+(\d+\.\d+\.\d+\.\d+)\s+netmask\s+(0x[0-9a-fA-F]+|\d+\.\d+\.\d+\.\d+)")
    for line in proc.stdout.splitlines():
        match = inet_pattern.match(line)
        if not match:
            continue
        found_ip = ipaddress.ip_address(match.group(1))
        if found_ip != local_ip:
            continue
        prefix = _prefix_from_netmask(match.group(2))
        return ipaddress.ip_network(f"{local_ip}/{prefix}", strict=False)
    return None


def _detect_lan_network(local_ip: ipaddress.IPv4Address) -> ipaddress.IPv4Network:
    if sys.platform.startswith("linux"):
        network = _linux_network_for_ip(local_ip)
    elif sys.platform == "darwin":
        network = _macos_network_for_ip(local_ip)
    else:
        raise RuntimeError(
            f"Unsupported platform '{sys.platform}' for LAN autodetection; use local access mode"
        )

    if network is None:
        raise RuntimeError(
            f"Unable to resolve LAN subnet for local IP {local_ip}; use local access mode"
        )

    return network


def _load_totp_secret(path: str) -> str:
    expanded = os.path.expanduser(path)
    try:
        with open(expanded, "r", encoding="utf-8") as fh:
            secret = fh.read().strip().replace(" ", "")
    except OSError as exc:
        raise RuntimeError(f"Failed to read TOTP secret file ({expanded}): {exc}") from exc

    if not secret:
        raise RuntimeError(f"TOTP secret file is empty ({expanded})")

    try:
        _base32_decode(secret)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Invalid base32 TOTP secret in {expanded}") from exc

    return secret


def build_access_config(access_mode: str, timeout: Optional[int], totp_secret_file: str) -> AccessConfig:
    if access_mode == "local":
        return AccessConfig(
            mode="local",
            bind_host="127.0.0.1",
            allowed_net=ipaddress.ip_network("127.0.0.1/32"),
            require_totp=False,
            totp_secret=None,
            timeout_seconds=timeout if timeout is not None else DEFAULT_LOCAL_TIMEOUT,
        )

    local_ip = _detect_outbound_ipv4()
    if not local_ip.is_private:
        raise RuntimeError(
            f"Detected outbound IP {local_ip} is not private; refusing LAN mode"
        )

    network = _detect_lan_network(local_ip)
    secret = _load_totp_secret(totp_secret_file)

    return AccessConfig(
        mode="lan",
        bind_host=str(local_ip),
        allowed_net=network,
        require_totp=True,
        totp_secret=secret,
        timeout_seconds=timeout if timeout is not None else DEFAULT_LAN_TIMEOUT,
    )


class BrokerState:
    def __init__(self, secret_name: str, token: str, vault_script: str, access: AccessConfig) -> None:
        self.secret_name = secret_name
        self.token = token
        self.vault_script = vault_script
        self.access = access
        self.done = threading.Event()
        self.error = None
        self._totp_attempts: dict[tuple[str, str], TotpAttempt] = {}
        self._totp_lock = threading.Lock()

    def _attempt_key(self, client_ip: str) -> tuple[str, str]:
        return (client_ip, self.token)

    def is_totp_locked(self, client_ip: str, now: float) -> bool:
        key = self._attempt_key(client_ip)
        with self._totp_lock:
            attempt = self._totp_attempts.get(key)
            if attempt is None:
                return False

            if attempt.locked_until > now:
                return True

            if attempt.locked_until and attempt.locked_until <= now:
                attempt.locked_until = 0
                attempt.failed_at.clear()
                return False

            attempt.failed_at = [ts for ts in attempt.failed_at if ts >= now - TOTP_WINDOW_SECONDS]
            return False

    def record_totp_failure(self, client_ip: str, now: float) -> None:
        key = self._attempt_key(client_ip)
        with self._totp_lock:
            attempt = self._totp_attempts.setdefault(key, TotpAttempt())
            attempt.failed_at = [ts for ts in attempt.failed_at if ts >= now - TOTP_WINDOW_SECONDS]
            attempt.failed_at.append(now)
            if len(attempt.failed_at) >= TOTP_MAX_FAILURES:
                attempt.locked_until = now + TOTP_LOCKOUT_SECONDS

    def clear_totp_failures(self, client_ip: str) -> None:
        key = self._attempt_key(client_ip)
        with self._totp_lock:
            self._totp_attempts.pop(key, None)


class OneShotHandler(BaseHTTPRequestHandler):
    server_version = "passwordstore-broker/0.1"

    def log_message(self, fmt, *args):
        return

    @property
    def state(self) -> BrokerState:
        return self.server.state  # type: ignore[attr-defined]

    def _send_html(self, status: int, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _client_ip(self) -> Optional[ipaddress.IPv4Address]:
        try:
            ip = ipaddress.ip_address(self.client_address[0])
        except ValueError:
            return None
        if not isinstance(ip, ipaddress.IPv4Address):
            return None
        return ip

    def _client_allowed(self, client_ip: Optional[ipaddress.IPv4Address]) -> bool:
        return client_ip is not None and client_ip in self.state.access.allowed_net

    def do_GET(self):
        if self.path != "/":
            self._send_html(
                HTTPStatus.NOT_FOUND,
                FAIL_TEMPLATE.format(message="Unknown path."),
            )
            return

        client_ip = self._client_ip()
        if not self._client_allowed(client_ip):
            self._send_html(
                HTTPStatus.FORBIDDEN,
                FAIL_TEMPLATE.format(message="Source IP not allowed."),
            )
            return

        totp_section = TOTP_SECTION_TEMPLATE if self.state.access.require_totp else ""
        self._send_html(
            HTTPStatus.OK,
            FORM_TEMPLATE.format(
                secret_name=html.escape(self.state.secret_name),
                token=html.escape(self.state.token),
                totp_section=totp_section,
            ),
        )

    def do_POST(self):
        if self.path != "/submit":
            self._send_html(
                HTTPStatus.NOT_FOUND,
                FAIL_TEMPLATE.format(message="Unknown path."),
            )
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        form = urllib.parse.parse_qs(raw)

        token = form.get("token", [""])[0]
        if token != self.state.token:
            self._send_html(
                HTTPStatus.FORBIDDEN,
                FAIL_TEMPLATE.format(message="Invalid token."),
            )
            return

        client_ip = self._client_ip()
        if not self._client_allowed(client_ip):
            self._send_html(
                HTTPStatus.FORBIDDEN,
                FAIL_TEMPLATE.format(message="Source IP not allowed."),
            )
            return

        client_ip_str = str(client_ip)
        if self.state.access.require_totp:
            now = time.time()
            if self.state.is_totp_locked(client_ip_str, now):
                self._send_html(
                    HTTPStatus.TOO_MANY_REQUESTS,
                    FAIL_TEMPLATE.format(message="Authentication failed. Try again shortly."),
                )
                return

            totp_code = form.get("totp", [""])[0].strip()
            secret = self.state.access.totp_secret or ""
            valid = len(totp_code) == 6 and totp_code.isdigit() and verify_totp(secret, totp_code)
            if not valid:
                self.state.record_totp_failure(client_ip_str, now)
                self._send_html(
                    HTTPStatus.FORBIDDEN,
                    FAIL_TEMPLATE.format(message="Authentication failed."),
                )
                return

        secret_value = form.get("secret", [""])[0]
        if not secret_value:
            self._send_html(
                HTTPStatus.BAD_REQUEST,
                FAIL_TEMPLATE.format(message="Missing secret."),
            )
            return

        try:
            subprocess.run(
                [self.state.vault_script, "put", self.state.secret_name],
                input=secret_value.encode("utf-8"),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as exc:
            self.state.error = exc.stderr.decode("utf-8", errors="replace").strip()
            self._send_html(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                FAIL_TEMPLATE.format(message="Could not store secret in vault."),
            )
            self.state.done.set()
            return

        if self.state.access.require_totp:
            self.state.clear_totp_failures(client_ip_str)

        self._send_html(HTTPStatus.OK, OK_TEMPLATE)
        self.state.done.set()


def ensure_self_signed_cert(hostname: str, cert_dir: str):
    cert_path = os.path.join(cert_dir, "cert.pem")
    key_path = os.path.join(cert_dir, "key.pem")
    openssl = shutil.which("openssl")
    if openssl is None:
        raise RuntimeError("openssl is required to generate a self-signed cert")

    san = "DNS:localhost,IP:127.0.0.1"
    try:
        ipaddress.ip_address(hostname)
        san = f"IP:{hostname},DNS:localhost,IP:127.0.0.1"
    except ValueError:
        san = f"DNS:{hostname},DNS:localhost,IP:127.0.0.1"

    subprocess.run(
        [
            openssl,
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-sha256",
            "-days",
            "1",
            "-nodes",
            "-keyout",
            key_path,
            "-out",
            cert_path,
            "-subj",
            f"/CN={hostname}",
            "-addext",
            f"subjectAltName={san}",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return cert_path, key_path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Open one-time HTTPS page to collect secret and store in pass"
    )
    parser.add_argument("--secretname", required=True, help="Vault secret name/key")
    parser.add_argument("--port", type=int, required=True, help="Local HTTPS port")
    parser.add_argument(
        "--access",
        choices=["local", "lan"],
        default="local",
        help="Access mode: 'local' for localhost only, 'lan' for private-network intake with webform TOTP",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Seconds to wait for submission before exiting",
    )
    parser.add_argument(
        "--totp-secret-file",
        default=DEFAULT_TOTP_SECRET_FILE,
        help="Path to base32 TOTP secret file (used in LAN mode)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        access = build_access_config(args.access, args.timeout, args.totp_secret_file)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    script_dir = os.path.dirname(os.path.abspath(__file__))
    vault_script = os.path.join(script_dir, "vault.sh")

    if not os.path.exists(vault_script):
        print("vault.sh not found next to this script", file=sys.stderr)
        return 2

    token = secrets.token_urlsafe(24)
    state = BrokerState(args.secretname, token, vault_script, access)

    with tempfile.TemporaryDirectory(prefix="passwordstore-broker-cert-") as cert_dir:
        try:
            cert_path, key_path = ensure_self_signed_cert(access.bind_host, cert_dir)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 2

        class ThreadingTCPServer(socketserver.ThreadingTCPServer):
            allow_reuse_address = True

        try:
            with ThreadingTCPServer((access.bind_host, args.port), OneShotHandler) as httpd:
                httpd.state = state  # type: ignore[attr-defined]
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(certfile=cert_path, keyfile=key_path)
                httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

                thread = threading.Thread(target=httpd.serve_forever, daemon=True)
                thread.start()

                if access.mode == "lan":
                    print(
                        f"[LAN MODE] bind={access.bind_host}:{args.port} allow={access.allowed_net} totp=form",
                        flush=True,
                    )
                url = f"https://{access.bind_host}:{args.port}/"
                print(url, flush=True)

                completed = state.done.wait(timeout=access.timeout_seconds)
                httpd.shutdown()
                thread.join(timeout=2)
        except OSError as exc:
            print(
                f"Failed to start HTTPS intake server on {access.bind_host}:{args.port}: {exc}",
                file=sys.stderr,
            )
            return 2

    if not completed:
        print("Timed out waiting for secret submission", file=sys.stderr)
        return 3
    if state.error:
        print(state.error, file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
