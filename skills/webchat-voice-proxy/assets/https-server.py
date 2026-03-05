#!/usr/bin/env python3
"""HTTPS reverse proxy: Control UI + /transcribe + WebSocket proxy to gateway."""
import asyncio
import re
import ssl
import os
import mimetypes
import urllib.request
import subprocess
import sys
from pathlib import Path

from aiohttp import web, WSMsgType, ClientSession, WSCloseCode

# --- Input validation for env vars ---
_raw_port = os.environ.get("VOICE_HTTPS_PORT", "8443")
if not re.fullmatch(r'[0-9]+', _raw_port) or not (1 <= int(_raw_port) <= 65535):
    print(f"ERROR: VOICE_HTTPS_PORT must be 1-65535, got: {_raw_port}", file=sys.stderr)
    sys.exit(1)
PORT = int(_raw_port)

_raw_bind = os.environ.get("VOICE_BIND_HOST", "127.0.0.1")
if not re.fullmatch(r'[a-zA-Z0-9._-]+', _raw_bind):
    print(f"ERROR: VOICE_BIND_HOST contains invalid characters: {_raw_bind}", file=sys.stderr)
    sys.exit(1)

WORKSPACE = os.environ.get("WORKSPACE", os.path.join(Path.home(), ".openclaw", "workspace"))
CERT = os.environ.get("VOICE_CERT", os.path.join(WORKSPACE, "voice-input", "certs", "voice-cert.pem"))
KEY = os.environ.get("VOICE_KEY", os.path.join(WORKSPACE, "voice-input", "certs", "voice-key.pem"))

def _detect_control_ui():
    """Find Control UI directory dynamically."""
    explicit = os.environ.get("OPENCLAW_UI_DIR")
    if explicit and os.path.isdir(explicit):
        return explicit
    try:
        # Safe: fixed argument list, no user input, no shell=True
        npm_root = subprocess.check_output(["npm", "-g", "root"], text=True, stderr=subprocess.DEVNULL).strip()
        candidate = os.path.join(npm_root, "openclaw", "dist", "control-ui")
        if os.path.isdir(candidate):
            return candidate
    except Exception:
        pass
    # Fallback: common default
    fallback = os.path.join(Path.home(), ".npm-global", "lib", "node_modules", "openclaw", "dist", "control-ui")
    return fallback

CONTROL_UI = _detect_control_ui()
TRANSCRIBE = os.environ.get("VOICE_TRANSCRIBE_URL", "http://127.0.0.1:18790/transcribe")
GATEWAY_WS = os.environ.get("VOICE_GATEWAY_WS", "ws://127.0.0.1:18789")
# SECURITY: Default bind address is localhost only. Set VOICE_BIND_HOST to
# 0.0.0.0 or a specific IP to expose externally (e.g. for LAN access).
BIND_HOST = _raw_bind
ALLOWED_ORIGIN = os.environ.get("VOICE_ALLOWED_ORIGIN", f"https://127.0.0.1:{PORT}")


def _read_gateway_token():
    """Read gateway auth token from openclaw config."""
    try:
        import json
        cfg_path = os.path.join(Path.home(), ".openclaw", "openclaw.json")
        with open(cfg_path, "r") as f:
            cfg = json.load(f)
        return cfg.get("gateway", {}).get("auth", {}).get("token", None)
    except Exception:
        return None


def _check_auth(request):
    """Validate Bearer token against gateway auth token. Returns error response or None."""
    gateway_token = _read_gateway_token()
    if not gateway_token:
        # No gateway token configured — allow (localhost-only safe default)
        return None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        provided = auth_header[7:].strip()
        if provided == gateway_token:
            return None
    return web.json_response(
        {"error": "unauthorized"},
        status=401,
        headers={"Access-Control-Allow-Origin": ALLOWED_ORIGIN},
    )


async def handle_transcribe(request):
    auth_err = _check_auth(request)
    if auth_err is not None:
        return auth_err
    body = await request.read()
    try:
        req = urllib.request.Request(
            TRANSCRIBE,
            data=body,
            headers={"Content-Type": "application/octet-stream"},
        )
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None,
            lambda: urllib.request.urlopen(req, timeout=120).read(),
        )
        return web.Response(
            body=data,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": ALLOWED_ORIGIN},
        )
    except Exception as e:
        return web.json_response({"error": str(e)}, status=502)


async def handle_options(_request):
    return web.Response(
        status=204,
        headers={
            "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )


async def handle_catchall(request):
    # --- WebSocket proxy ---
    if request.headers.get("Upgrade", "").lower() == "websocket":
        ws_browser = web.WebSocketResponse(autoclose=False, autoping=False)
        await ws_browser.prepare(request)

        gw_headers = {}
        origin = request.headers.get("Origin")
        if origin:
            gw_headers["Origin"] = origin

        session = ClientSession()
        try:
            ws_gw = await session.ws_connect(
                GATEWAY_WS,
                autoclose=False,
                autoping=False,
                headers=gw_headers,
            )
        except Exception:
            await ws_browser.close(code=WSCloseCode.INTERNAL_ERROR, message=b"gateway unreachable")
            await session.close()
            return ws_browser

        async def gw_to_browser():
            try:
                async for msg in ws_gw:
                    if ws_browser.closed:
                        break
                    if msg.type == WSMsgType.TEXT:
                        await ws_browser.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await ws_browser.send_bytes(msg.data)
                    elif msg.type == WSMsgType.PING:
                        await ws_browser.ping(msg.data)
                    elif msg.type == WSMsgType.PONG:
                        await ws_browser.pong(msg.data)
                    elif msg.type == WSMsgType.CLOSE:
                        await ws_browser.close(code=ws_gw.close_code or WSCloseCode.OK)
                        break
                    elif msg.type == WSMsgType.ERROR:
                        break
            except Exception:
                pass

        async def browser_to_gw():
            try:
                async for msg in ws_browser:
                    if ws_gw.closed:
                        break
                    if msg.type == WSMsgType.TEXT:
                        await ws_gw.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await ws_gw.send_bytes(msg.data)
                    elif msg.type == WSMsgType.PING:
                        await ws_gw.ping(msg.data)
                    elif msg.type == WSMsgType.PONG:
                        await ws_gw.pong(msg.data)
                    elif msg.type == WSMsgType.CLOSE:
                        await ws_gw.close(code=ws_browser.close_code or WSCloseCode.OK)
                        break
                    elif msg.type == WSMsgType.ERROR:
                        break
            except Exception:
                pass

        _, pending = await asyncio.wait(
            [asyncio.ensure_future(gw_to_browser()), asyncio.ensure_future(browser_to_gw())],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for t in pending:
            t.cancel()

        if not ws_gw.closed:
            await ws_gw.close()
        if not ws_browser.closed:
            await ws_browser.close()
        await session.close()
        return ws_browser

    # --- Static files (SPA fallback) ---
    path = request.path
    if path == "/":
        path = "/index.html"

    fpath = os.path.normpath(os.path.join(CONTROL_UI, path.lstrip("/")))
    # Path traversal protection: ensure resolved path is within CONTROL_UI
    if not fpath.startswith(os.path.normpath(CONTROL_UI) + os.sep) and fpath != os.path.normpath(CONTROL_UI):
        raise web.HTTPForbidden()

    if not os.path.isfile(fpath):
        fpath = os.path.join(CONTROL_UI, "index.html")

    mime, _ = mimetypes.guess_type(fpath)
    if not mime or fpath.endswith("index.html"):
        mime = "text/html"

    return web.FileResponse(fpath, headers={"Content-Type": mime})


def create_app():
    app = web.Application()
    app.router.add_route("POST", "/transcribe", handle_transcribe)
    app.router.add_route("OPTIONS", "/transcribe", handle_options)
    app.router.add_route("GET", "/{path:.*}", handle_catchall)
    return app


def ensure_cert_files():
    cert_path = Path(CERT)
    key_path = Path(KEY)
    cert_path.parent.mkdir(parents=True, exist_ok=True)

    if cert_path.exists() and key_path.exists():
        return

    # Safe: fixed argument list, no user input, no shell=True
    subprocess.run([
        "openssl", "req", "-x509", "-nodes", "-newkey", "rsa:2048",
        "-keyout", str(key_path),
        "-out", str(cert_path),
        "-days", "3650",
        "-subj", "/CN=openclaw-voice-local",
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # SECURITY: Ensure private key is not group/world-readable
    os.chmod(str(key_path), 0o600)


if __name__ == "__main__":
    ensure_cert_files()
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_ctx.load_cert_chain(CERT, KEY)

    app = create_app()
    print(f"[voice-https] HTTPS+WSS on https://{BIND_HOST}:{PORT}", flush=True)
    web.run_app(app, host=BIND_HOST, port=PORT, ssl_context=ssl_ctx, print=None)
