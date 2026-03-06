#!/usr/bin/env python3
"""🦞 Lobster Market WebSocket Protocol Adapter.

Pure protocol adapter: connects to the gateway broker via WebSocket and forwards
incoming task dispatches to a local Agent HTTP endpoint (--local-endpoint).

Architecture:
  Broker (WS) ←→ market-connect.py ←→ Local Agent HTTP (--local-endpoint)

market-connect.py does NOT know or care what agent technology runs behind the
local endpoint. It passes message and metadata through as-is.

Standard Local Agent HTTP Interface:
  POST /execute
  Request:
    {
      "task_id": "uuid",
      "message": {"parts": [...], "metadata": {...}},
      "metadata": {}
    }
  Response:
    {
      "status": "completed" | "failed",
      "artifacts": [{"name": "...", "parts": [...]}],
      "error": "..."
    }
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

try:
    import websockets
except ImportError:
    print("❌ websockets not installed. Run: pip3 install websockets", file=sys.stderr)
    sys.exit(1)

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

TOKEN_FILE = Path.home() / ".lobster-market" / "token.json"
MASTER_KEY_FILE = Path.home() / ".lobster-market" / "master-key.json"

BASE_HOST = os.environ.get("LOBSTER_HOST", "mindcore8.com")
PROTOCOL_VERSION = 1
HEARTBEAT_INTERVAL = 25
RECONNECT_DELAY = 5
MAX_RECONNECT_DELAY = 60

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("market-connect")


# ---------------------------------------------------------------------------
# Token management
# ---------------------------------------------------------------------------

def load_token() -> str:
    if not TOKEN_FILE.exists():
        log.error("No token file at %s. Run: lobster.py login-by-key <key>", TOKEN_FILE)
        sys.exit(1)
    data = json.loads(TOKEN_FILE.read_text())
    return data.get("access_token", "")


def refresh_token() -> str:
    import http.client

    # Method 1: refresh_token from token.json
    if TOKEN_FILE.exists():
        try:
            tk_data = json.loads(TOKEN_FILE.read_text())
            rt = tk_data.get("refresh_token", "")
            if rt:
                conn = http.client.HTTPSConnection(BASE_HOST, timeout=30)
                body = json.dumps({"refresh_token": rt})
                conn.request("POST", "/api/v1/users/refresh", body, {"Content-Type": "application/json"})
                resp = conn.getresponse()
                raw = resp.read().decode()
                conn.close()
                if resp.status == 200:
                    result = json.loads(raw)
                    token = result.get("access_token", "")
                    if token:
                        TOKEN_FILE.write_text(json.dumps(result, indent=2))
                        log.info("✅ Token refreshed via refresh_token")
                        return token
        except Exception as e:
            log.warning("refresh_token method failed: %s", e)

    # Method 2: master key login
    if MASTER_KEY_FILE.exists():
        try:
            mk_data = json.loads(MASTER_KEY_FILE.read_text())
            master_key = mk_data.get("master_key", "")
            master_secret = mk_data.get("master_secret", "")
            if master_key and master_secret:
                conn = http.client.HTTPSConnection(BASE_HOST, timeout=30)
                body = json.dumps({"api_key": master_key, "api_secret": master_secret})
                conn.request("POST", "/api/v1/auth/login-by-key", body, {"Content-Type": "application/json"})
                resp = conn.getresponse()
                raw = resp.read().decode()
                conn.close()
                if resp.status == 200:
                    result = json.loads(raw)
                    token = result.get("access_token", "")
                    if token:
                        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
                        TOKEN_FILE.write_text(json.dumps(result, indent=2))
                        log.info("✅ Token refreshed via master key")
                        return token
                else:
                    log.warning("Master key login failed: %d", resp.status)
        except Exception as e:
            log.warning("master_key method failed: %s", e)

    log.error("All token refresh methods failed")
    return ""


# ---------------------------------------------------------------------------
# HTTP forwarding (aiohttp preferred, urllib fallback)
# ---------------------------------------------------------------------------

async def _forward_aiohttp(endpoint: str, payload: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            endpoint,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=300),
        )
        return await resp.json()


async def _forward_urllib(endpoint: str, payload: dict) -> dict:
    """Fallback when aiohttp is not available."""
    import urllib.request
    loop = asyncio.get_event_loop()

    def _do():
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read().decode())

    return await loop.run_in_executor(None, _do)


async def forward_to_endpoint(endpoint: str, payload: dict) -> dict:
    if HAS_AIOHTTP:
        return await _forward_aiohttp(endpoint, payload)
    return await _forward_urllib(endpoint, payload)


# ---------------------------------------------------------------------------
# Task handling — pure passthrough
# ---------------------------------------------------------------------------

async def handle_task(task_msg: dict, ws, local_endpoint: str) -> None:
    """Receive task_send → forward to local-endpoint → relay result back."""
    task_id = task_msg.get("task_id", "")
    message = task_msg.get("message", {})
    metadata = task_msg.get("metadata", {})

    log.info("📥 Received task: %s", task_id)

    # 1. Accept
    await ws.send(json.dumps({
        "v": PROTOCOL_VERSION,
        "type": "task_accept",
        "task_id": task_id,
    }))
    log.info("✅ Accepted task: %s", task_id)

    # 2. Progress: working
    await ws.send(json.dumps({
        "v": PROTOCOL_VERSION,
        "type": "task_progress",
        "task_id": task_id,
        "status": {"state": "working"},
    }))

    # 3. Forward to local endpoint (message & metadata passed through as-is)
    try:
        result = await forward_to_endpoint(local_endpoint, {
            "task_id": task_id,
            "message": message,
            "metadata": metadata,
        })
    except Exception as e:
        log.error("❌ Local endpoint error: %s", e)
        await ws.send(json.dumps({
            "v": PROTOCOL_VERSION,
            "type": "task_failed",
            "task_id": task_id,
            "error": str(e),
        }))
        return

    # 4. Relay result
    if result.get("status") == "completed":
        await ws.send(json.dumps({
            "v": PROTOCOL_VERSION,
            "type": "task_complete",
            "task_id": task_id,
            "artifacts": result.get("artifacts", []),
        }))
        log.info("✅ Completed task: %s", task_id)
    else:
        error = result.get("error", "Unknown error")
        await ws.send(json.dumps({
            "v": PROTOCOL_VERSION,
            "type": "task_failed",
            "task_id": task_id,
            "error": error,
        }))
        log.error("❌ Task failed: %s – %s", task_id, error)


# ---------------------------------------------------------------------------
# Status check
# ---------------------------------------------------------------------------

async def check_status(agent_id: str):
    """Quick status check: auth + print agent info, then exit."""
    token = load_token()
    ws_url = f"wss://{BASE_HOST}/agent-ws"
    try:
        async with websockets.connect(ws_url, ping_interval=None, close_timeout=5) as ws:
            await ws.send(json.dumps({
                "v": PROTOCOL_VERSION,
                "type": "auth",
                "token": token,
                "agent_ids": [agent_id],
                "max_concurrent_tasks": 1,
            }))
            raw = await asyncio.wait_for(ws.recv(), timeout=10)
            resp = json.loads(raw)
            print(json.dumps(resp, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Status check failed: {e}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Connection loop
# ---------------------------------------------------------------------------

async def heartbeat_loop(ws):
    try:
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            await ws.send(json.dumps({
                "v": PROTOCOL_VERSION,
                "type": "ping",
                "ts": int(time.time()),
            }))
    except (asyncio.CancelledError, Exception):
        pass


async def connect_loop(agent_id: str, local_endpoint: str, max_concurrent: int):
    delay = RECONNECT_DELAY
    ws_url = f"wss://{BASE_HOST}/agent-ws"

    while True:
        token = load_token()
        if not token:
            log.warning("No token, attempting refresh...")
            token = refresh_token()
            if not token:
                log.error("Cannot obtain token, retrying in %ds", delay)
                await asyncio.sleep(delay)
                delay = min(delay * 2, MAX_RECONNECT_DELAY)
                continue

        try:
            log.info("🔌 Connecting to %s ...", ws_url)
            async with websockets.connect(ws_url, ping_interval=None, close_timeout=5) as ws:
                await ws.send(json.dumps({
                    "v": PROTOCOL_VERSION,
                    "type": "auth",
                    "token": token,
                    "agent_ids": [agent_id],
                    "max_concurrent_tasks": max_concurrent,
                }))
                log.info("🔐 Auth sent for agent: %s", agent_id)

                raw = await asyncio.wait_for(ws.recv(), timeout=10)
                resp = json.loads(raw)

                if resp.get("type") == "auth_fail":
                    reason = resp.get("reason", "unknown")
                    log.error("❌ Auth failed: %s", reason)
                    if "token" in reason.lower():
                        refresh_token()
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, MAX_RECONNECT_DELAY)
                    continue

                if resp.get("type") == "auth_ok":
                    log.info("✅ Authenticated as agent: %s", resp.get("agent_id", agent_id))
                    log.info("   Local endpoint: %s", local_endpoint)
                    pending = resp.get("pending_tasks", [])
                    if pending:
                        log.info("📬 %d pending tasks", len(pending))
                    delay = RECONNECT_DELAY

                    hb = asyncio.create_task(heartbeat_loop(ws))
                    try:
                        async for raw_msg in ws:
                            msg = json.loads(raw_msg)
                            mt = msg.get("type")
                            if mt == "ping":
                                await ws.send(json.dumps({
                                    "v": PROTOCOL_VERSION,
                                    "type": "pong",
                                    "ts": msg.get("ts", int(time.time())),
                                }))
                            elif mt == "pong":
                                pass
                            elif mt == "task_send":
                                asyncio.create_task(handle_task(msg, ws, local_endpoint))
                            else:
                                log.debug("Received: %s", mt)
                    finally:
                        hb.cancel()
                else:
                    log.warning("Unexpected response: %s", resp)
                    await asyncio.sleep(delay)

        except websockets.exceptions.ConnectionClosed as e:
            log.warning("🔌 Connection closed: %s", e)
        except asyncio.TimeoutError:
            log.warning("⏰ Connection timeout")
        except ConnectionRefusedError:
            log.warning("🚫 Connection refused")
        except Exception as e:
            log.warning("❌ Connection error: %s: %s", type(e).__name__, e)

        log.info("🔄 Reconnecting in %ds...", delay)
        await asyncio.sleep(delay)
        delay = min(delay * 2, MAX_RECONNECT_DELAY)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="🦞 Lobster Market Protocol Adapter (WS ↔ HTTP)")
    parser.add_argument("--agent-id", required=True, help="Agent UUID")
    parser.add_argument("--local-endpoint", required=True,
                        help="Local Agent HTTP endpoint, e.g. http://localhost:8900/execute")
    parser.add_argument("--max-concurrent", type=int, default=1,
                        help="Max concurrent tasks (default: 1)")
    parser.add_argument("--status", action="store_true",
                        help="Check connection status and exit")
    args = parser.parse_args()

    if args.status:
        asyncio.run(check_status(args.agent_id))
        return

    log.info("🦞 Lobster Market Protocol Adapter")
    log.info("   Agent: %s", args.agent_id)
    log.info("   Endpoint: %s", args.local_endpoint)
    log.info("   Max concurrent: %d", args.max_concurrent)
    log.info("   Host: %s", BASE_HOST)

    try:
        asyncio.run(connect_loop(args.agent_id, args.local_endpoint, args.max_concurrent))
    except KeyboardInterrupt:
        log.info("👋 Shutting down")


if __name__ == "__main__":
    main()
