#!/usr/bin/env python3
"""pettracer_watch.py — live update stream for PetTracer (SockJS + STOMP).

This implements the same SockJS/STOMP flow used by the PetTracer web portal:
- Connects to the PetTracer SockJS WebSocket endpoint
- Speaks STOMP to subscribe to updates
- Prints newline-delimited JSON (NDJSON) messages to stdout

Requires:
  pip install aiohttp

Environment variables (preferred):
- PETTRACER_TOKEN              (bearer token; skips login)
- PETTRACER_USERNAME or PETTRACER_EMAIL
- PETTRACER_PASSWORD
- PETTRACER_API_BASE           (optional; default: https://portal.pettracer.com/api)
- PETTRACER_WS_BASE            (optional; default: wss://pt.pettracer.com/sc)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import string
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_API_BASE_URL = "https://portal.pettracer.com/api"
API_BASE_URL = os.getenv("PETTRACER_API_BASE", DEFAULT_API_BASE_URL).rstrip("/")

LOGIN_ENDPOINT = "/user/login"
GET_CCS_ENDPOINT = "/map/getccs"

DEFAULT_TIMEOUT_S = 20
DEFAULT_WS_BASE = os.getenv("PETTRACER_WS_BASE", "wss://pt.pettracer.com/sc").rstrip("/")
USER_AGENT = "pettracer-agent-skill/0.3"


def _env_first(*names: str) -> Optional[str]:
    for n in names:
        v = os.getenv(n)
        if v:
            return v
    return None


def _request_json(
    method: str,
    endpoint: str,
    *,
    token: Optional[str] = None,
    json_body: Optional[dict] = None,
    timeout_s: int = DEFAULT_TIMEOUT_S,
) -> Any:
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data: Optional[bytes] = None
    if json_body is not None:
        data = json.dumps(json_body, separators=(",", ":")).encode("utf-8")
        headers["Content-Length"] = str(len(data))

    req = Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {body}".strip())
    except URLError as e:
        raise RuntimeError(f"Network error: {e}") from e


def get_token_or_login(*, username: Optional[str], password: Optional[str], timeout_s: int) -> str:
    token = _env_first("PETTRACER_TOKEN")
    if token:
        return token

    username = username or _env_first("PETTRACER_USERNAME", "PETTRACER_EMAIL")
    password = password or _env_first("PETTRACER_PASSWORD")
    if not username or not password:
        raise RuntimeError(
            "Missing credentials. Set PETTRACER_TOKEN or (PETTRACER_USERNAME/PETTRACER_EMAIL + PETTRACER_PASSWORD)."
        )

    resp = _request_json("POST", LOGIN_ENDPOINT, json_body={"login": username, "password": password}, timeout_s=timeout_s)
    if not isinstance(resp, dict):
        raise RuntimeError("Login response was not a JSON object.")
    token = resp.get("access_token") or resp.get("token") or resp.get("id_token")
    if not token:
        raise RuntimeError("Login response did not contain an access token.")
    return str(token)


def fetch_devices(*, token: str, timeout_s: int) -> List[Dict[str, Any]]:
    resp = _request_json("GET", GET_CCS_ENDPOINT, token=token, timeout_s=timeout_s)
    if not isinstance(resp, list):
        raise RuntimeError("Unexpected response from /map/getccs (expected a JSON list).")
    return resp


def _device_name(device: Dict[str, Any]) -> str:
    details = device.get("details") or {}
    name = details.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return f"Pet {device.get('id')}"


def resolve_device_ids(devices: List[Dict[str, Any]], *, device_ids: List[int], pet_name: Optional[str]) -> List[int]:
    if device_ids:
        return device_ids
    if pet_name:
        key = pet_name.casefold().strip()
        exact = [int(d.get("id")) for d in devices if _device_name(d).casefold() == key]
        if len(exact) == 1:
            return exact
        if len(exact) > 1:
            raise RuntimeError(f"Multiple devices matched name={pet_name!r}. Use --device-id. Matches: {exact}")

        contains = [int(d.get("id")) for d in devices if key and key in _device_name(d).casefold()]
        if len(contains) == 1:
            return contains
        if len(contains) > 1:
            raise RuntimeError(f"Multiple devices partially matched name={pet_name!r}. Use --device-id. Matches: {contains}")

        raise RuntimeError(f"No device found with name={pet_name!r}. Available: {[ _device_name(d) for d in devices ]}")

    # If no pet selection provided, subscribe to the single collar if there is exactly one.
    if len(devices) == 1:
        return [int(devices[0].get("id"))]

    raise RuntimeError("Must provide --device-id (one or more) or --pet")


def _rand_session_id() -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))


def _rand_server_id() -> str:
    return f"{random.randint(0, 999):03d}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_location(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Some messages may include lastPos dict; others might include posLat/posLong directly
    last_pos = msg.get("lastPos")
    if isinstance(last_pos, dict):
        lat = last_pos.get("posLat")
        lon = last_pos.get("posLong")
        if lat is not None and lon is not None:
            try:
                lat_f = float(lat)
                lon_f = float(lon)
            except Exception:
                return None
            return {
                "lat": lat_f,
                "lon": lon_f,
                "time": last_pos.get("timeMeasure") or last_pos.get("timeDb"),
                "accuracy_m": last_pos.get("acc") if last_pos.get("acc") is not None else last_pos.get("horiPrec"),
            }

    lat = msg.get("posLat")
    lon = msg.get("posLong")
    if lat is not None and lon is not None:
        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except Exception:
            return None
        return {
            "lat": lat_f,
            "lon": lon_f,
            "time": msg.get("timeMeasure") or msg.get("timeDb") or msg.get("lastContact"),
            "accuracy_m": msg.get("acc") if msg.get("acc") is not None else msg.get("horiPrec"),
        }

    return None


class SockJsStompClient:
    def __init__(self, *, ws_base: str, token: str, device_ids: List[int], verbose: bool = False) -> None:
        self.ws_base = ws_base.rstrip("/")
        self.token = token
        self.device_ids = [int(x) for x in device_ids]
        self.verbose = verbose
        self._running = True

        # Lazily imported dependency
        try:
            import aiohttp  # noqa: F401
        except Exception as e:
            raise RuntimeError("aiohttp is required. Install with: pip install aiohttp") from e

    async def run_forever(self) -> None:
        import aiohttp

        backoff_s = 10
        backoff_max_s = 60

        while self._running:
            session_id = _rand_session_id()
            server_id = _rand_server_id()
            url = f"{self.ws_base}/{server_id}/{session_id}/websocket?access_token={self.token}"

            if self.verbose:
                print(f"[pettracer_watch] connecting: {url}", file=sys.stderr)

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(url, heartbeat=30) as ws:
                        if self.verbose:
                            print("[pettracer_watch] websocket connected", file=sys.stderr)

                        # Reset backoff after a successful connection.
                        backoff_s = 10

                        async for msg in ws:
                            if not self._running:
                                break
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self._handle_sockjs_frame(ws, msg.data)
                            elif msg.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSED):
                                if self.verbose:
                                    print(f"[pettracer_watch] websocket closed/error: {msg.type}", file=sys.stderr)
                                break

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[pettracer_watch] connection error: {e}", file=sys.stderr)

            if self._running:
                if self.verbose:
                    print(f"[pettracer_watch] reconnecting in {backoff_s}s", file=sys.stderr)
                await asyncio.sleep(backoff_s)
                backoff_s = min(backoff_max_s, int(backoff_s * 2))

    def stop(self) -> None:
        self._running = False

    async def _handle_sockjs_frame(self, ws, data: str) -> None:
        if not data:
            return
        frame_type = data[0]

        if frame_type == "o":
            # Open frame → send STOMP CONNECT
            await self._send_stomp_connect(ws)
            return

        if frame_type == "h":
            # Heartbeat
            return

        if frame_type == "a":
            # Array of messages
            try:
                messages = json.loads(data[1:])
                if isinstance(messages, list):
                    for m in messages:
                        if isinstance(m, str):
                            await self._handle_stomp_message(ws, m)
            except json.JSONDecodeError:
                if self.verbose:
                    print(f"[pettracer_watch] failed to decode sockjs: {data[:200]}", file=sys.stderr)
            return

        if frame_type == "c":
            # Close frame
            if self.verbose:
                print(f"[pettracer_watch] sockjs close: {data}", file=sys.stderr)
            return

    async def _send_sockjs(self, ws, message: str) -> None:
        # Client → server SockJS WebSocket transport sends a JSON array of strings.
        frame = json.dumps([message], separators=(",", ":"))
        await ws.send_str(frame)

    async def _send_stomp_connect(self, ws) -> None:
        connect_frame = (
            "CONNECT\n"
            "accept-version:1.1,1.0\n"
            "heart-beat:10000,10000\n"
            "\n"
            "\u0000"
        )
        await self._send_sockjs(ws, connect_frame)

    async def _send_stomp_subscribe(self, ws) -> None:
        # Subscribe to queues
        sub0 = "SUBSCRIBE\nid:sub-0\ndestination:/user/queue/messages\n\n\u0000"
        sub1 = "SUBSCRIBE\nid:sub-1\ndestination:/user/queue/portal\n\n\u0000"
        await self._send_sockjs(ws, sub0)
        await self._send_sockjs(ws, sub1)

        # Subscribe to specific devices
        if self.device_ids:
            payload = json.dumps({"deviceIds": self.device_ids}, separators=(",", ":"))
            send_frame = (
                "SEND\n"
                "destination:/app/subscribe\n"
                f"content-length:{len(payload)}\n"
                "\n"
                f"{payload}"
                "\u0000"
            )
            await self._send_sockjs(ws, send_frame)

        # Start heartbeats (client side)
        asyncio.create_task(self._heartbeat_sender(ws))

    async def _heartbeat_sender(self, ws) -> None:
        # STOMP heartbeat is just newline in a SockJS array frame
        try:
            while self._running and not ws.closed:
                await asyncio.sleep(9)
                await ws.send_str(json.dumps(["\n"], separators=(",", ":")))
        except Exception:
            return

    async def _handle_stomp_message(self, ws, msg: str) -> None:
        # STOMP heartbeats are newlines
        if not msg or msg in ("\n", "\r\n"):
            return

        # Messages may contain multiple STOMP frames separated by NULL bytes
        frames = msg.split("\u0000")
        for frame in frames:
            frame = frame.strip()
            if not frame:
                continue

            if frame.startswith("CONNECTED"):
                if self.verbose:
                    print("[pettracer_watch] STOMP CONNECTED", file=sys.stderr)
                await self._send_stomp_subscribe(ws)
                continue

            if frame.startswith("MESSAGE"):
                body_start = frame.find("\n\n")
                if body_start == -1:
                    continue
                body = frame[body_start + 2 :]

                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    payload = {"_raw": body}

                if isinstance(payload, dict):
                    dev_id = payload.get("id")
                    try:
                        dev_id_int = int(dev_id) if dev_id is not None else None
                    except Exception:
                        dev_id_int = None

                    # Even though we subscribe to specific deviceIds, be defensive and filter.
                    if self.device_ids and dev_id_int is not None and dev_id_int not in self.device_ids:
                        continue

                    out = {
                        "received_at": _now_iso(),
                        "device_id": dev_id_int,
                        "location": _extract_location(payload),
                        "message": payload,
                    }
                else:
                    out = {"received_at": _now_iso(), "message": payload}

                print(json.dumps(out, separators=(",", ":"), ensure_ascii=False))
                sys.stdout.flush()
                continue

            # Other STOMP frames are ignored (ERROR, RECEIPT, etc)
            if self.verbose:
                print(f"[pettracer_watch] other STOMP frame: {frame[:40]}...", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pettracer_watch.py")
    p.add_argument("--timeout-s", type=int, default=DEFAULT_TIMEOUT_S)
    p.add_argument("--ws-base", default=DEFAULT_WS_BASE, help="SockJS WS base (default: PetTracer).")
    p.add_argument("--username", help="PetTracer login (prefer env var PETTRACER_USERNAME).")
    p.add_argument("--password", help="PetTracer password (prefer env var PETTRACER_PASSWORD).")
    p.add_argument("--device-id", action="append", type=int, default=[], help="Device id to subscribe to (repeatable).")
    p.add_argument("--pet", help="Pet name (matches device.details.name).")
    p.add_argument("--verbose", action="store_true")
    return p


async def _amain() -> int:
    args = build_parser().parse_args()
    token = get_token_or_login(username=args.username, password=args.password, timeout_s=args.timeout_s)
    devices = fetch_devices(token=token, timeout_s=args.timeout_s)
    device_ids = resolve_device_ids(devices, device_ids=args.device_id, pet_name=args.pet)

    if args.verbose:
        names = {int(d.get("id")): _device_name(d) for d in devices}
        print(f"[pettracer_watch] subscribing to: {[ (i, names.get(i)) for i in device_ids ]}", file=sys.stderr)

    client = SockJsStompClient(ws_base=args.ws_base, token=token, device_ids=device_ids, verbose=args.verbose)
    try:
        await client.run_forever()
    except KeyboardInterrupt:
        client.stop()
    return 0


def main() -> int:
    try:
        return asyncio.run(_amain())
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
