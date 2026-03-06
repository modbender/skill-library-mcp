#!/usr/bin/env python3
"""Control4 CLI wrapper using pyControl4.

Supports convenience commands (lights/relays/rooms) plus generic method exposure
for most pyControl4 entity classes.
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from pyControl4.account import C4Account
from pyControl4.alarm import C4ContactSensor, C4SecurityPanel
from pyControl4.blind import C4Blind
from pyControl4.climate import C4Climate
from pyControl4.director import C4Director
from pyControl4.fan import C4Fan
from pyControl4.light import C4Light
from pyControl4.relay import C4Relay
from pyControl4.room import C4Room

ENV_FILE = Path(__file__).resolve().parent / ".env"
SENSITIVE_METHOD_KEYWORDS = (
    "arm",
    "disarm",
    "emergency",
    "open",
    "close",
    "unlock",
    "lock",
    "garage",
    "gate",
)


def _load_env_file() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _env(name: str, required: bool = True) -> Optional[str]:
    value = os.getenv(name)
    if required and not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


async def _login_and_director() -> C4Director:
    username = _env("CONTROL4_USERNAME")
    password = _env("CONTROL4_PASSWORD")
    ip = _env("CONTROL4_CONTROLLER_IP")

    account = C4Account(username, password)
    await account.getAccountBearerToken()

    controller_name = os.getenv("CONTROL4_CONTROLLER_NAME")
    if not controller_name:
        controllers = await account.getAccountControllers()
        controller_name = controllers.get("controllerCommonName")
        if not controller_name:
            raise RuntimeError("Could not determine controller name. Set CONTROL4_CONTROLLER_NAME.")

    director_token = (await account.getDirectorBearerToken(controller_name))["token"]
    return C4Director(ip, director_token)


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)


def _entity_factory(name: str, director: C4Director, item_id: Optional[int]) -> Any:
    key = name.lower()
    mapping: Dict[str, Callable[..., Any]] = {
        "light": C4Light,
        "relay": C4Relay,
        "climate": C4Climate,
        "blind": C4Blind,
        "room": C4Room,
        "fan": C4Fan,
        "security-panel": C4SecurityPanel,
        "contact-sensor": C4ContactSensor,
    }
    if key == "director":
        return director
    cls = mapping.get(key)
    if not cls:
        raise RuntimeError(f"Unknown entity: {name}")
    if item_id is None:
        raise RuntimeError(f"--id is required for entity {name}")
    return cls(director, int(item_id))


def _public_methods(obj: Any) -> list[str]:
    return sorted(
        m
        for m in dir(obj)
        if not m.startswith("_") and callable(getattr(obj, m, None))
    )


async def cmd_discover(_: argparse.Namespace) -> int:
    account = C4Account(_env("CONTROL4_USERNAME"), _env("CONTROL4_PASSWORD"))
    await account.getAccountBearerToken()
    info = await account.getAccountControllers()
    print(json.dumps(info, indent=2))
    return 0


async def cmd_list_items(args: argparse.Namespace) -> int:
    director = await _login_and_director()
    items = await director.getAllItemInfo()
    if isinstance(items, str):
        items = json.loads(items)
    if isinstance(items, dict):
        items = list(items.values())

    if args.category:
        category = args.category.lower()
        items = [
            i
            for i in items
            if isinstance(i, dict)
            and (
                str(i.get("category", "")).lower() == category
                or str(i.get("typeName", "")).lower() == category
                or str(i.get("control", "")).lower() == category
                or category in str(i.get("name", "")).lower()
            )
        ]

    if args.compact:
        out = [
            {
                "id": i.get("id"),
                "name": i.get("name"),
                "typeName": i.get("typeName"),
                "control": i.get("control"),
                "parentId": i.get("parentId"),
            }
            for i in items
            if isinstance(i, dict)
        ]
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(items, indent=2))
    return 0


async def cmd_light_set(args: argparse.Namespace) -> int:
    director = await _login_and_director()
    light = C4Light(director, int(args.id))
    level = max(0, min(100, int(args.level)))
    if args.ramp_ms and args.ramp_ms > 0:
        await light.rampToLevel(level, int(args.ramp_ms))
    else:
        await light.setLevel(level)
    print(json.dumps(_jsonable(await light.getState()), indent=2))
    return 0


async def cmd_relay_toggle(args: argparse.Namespace) -> int:
    director = await _login_and_director()
    relay = C4Relay(director, int(args.id))
    await relay.toggle()
    print(json.dumps(_jsonable(await relay.getRelayStateVerified()), indent=2))
    return 0


async def cmd_relay_set(args: argparse.Namespace) -> int:
    director = await _login_and_director()
    relay = C4Relay(director, int(args.id))
    if args.state.lower() == "open":
        await relay.open()
    else:
        await relay.close()
    print(json.dumps(_jsonable(await relay.getRelayStateVerified()), indent=2))
    return 0


async def cmd_room_set_source(args: argparse.Namespace) -> int:
    director = await _login_and_director()
    room = C4Room(director, int(args.room_id))
    if args.audio_only:
        await room.setAudioSource(int(args.source_id))
    else:
        await room.setVideoAndAudioSource(int(args.source_id))
    print(json.dumps({"ok": True, "room_id": int(args.room_id), "source_id": int(args.source_id), "audio_only": bool(args.audio_only)}, indent=2))
    return 0


async def cmd_room_mute(args: argparse.Namespace) -> int:
    director = await _login_and_director()
    room = C4Room(director, int(args.room_id))
    action = args.state.lower()
    if action == "on":
        await room.setMuteOn()
    elif action == "off":
        await room.setMuteOff()
    else:
        await room.toggleMute()
    print(json.dumps({"ok": True, "room_id": int(args.room_id), "mute": _jsonable(await room.isMuted())}, indent=2))
    return 0


async def cmd_room_volume(args: argparse.Namespace) -> int:
    director = await _login_and_director()
    room = C4Room(director, int(args.room_id))
    if args.level is not None:
        await room.setVolume(max(0, min(100, int(args.level))))
    elif args.delta == "up":
        await room.setIncrementVolume()
    elif args.delta == "down":
        await room.setDecrementVolume()
    print(json.dumps({"ok": True, "room_id": int(args.room_id), "volume": _jsonable(await room.getVolume())}, indent=2))
    return 0


async def cmd_room_status(args: argparse.Namespace) -> int:
    director = await _login_and_director()
    room = C4Room(director, int(args.room_id))
    print(
        json.dumps(
            {
                "room_id": int(args.room_id),
                "is_on": _jsonable(await room.isOn()),
                "is_muted": _jsonable(await room.isMuted()),
                "volume": _jsonable(await room.getVolume()),
            },
            indent=2,
        )
    )
    return 0


async def cmd_methods(args: argparse.Namespace) -> int:
    director = await _login_and_director()
    obj = _entity_factory(args.entity, director, args.id)
    methods = []
    for m in _public_methods(obj):
        fn = getattr(obj, m)
        try:
            sig = str(inspect.signature(fn))
        except Exception:
            sig = "(...)"
        methods.append({"name": m, "signature": f"{m}{sig}"})
    print(json.dumps(methods, indent=2))
    return 0


async def cmd_call(args: argparse.Namespace) -> int:
    director = await _login_and_director()
    obj = _entity_factory(args.entity, director, args.id)
    fn = getattr(obj, args.method, None)
    is_sensitive = any(k in args.method.lower() for k in SENSITIVE_METHOD_KEYWORDS)
    if is_sensitive and not args.allow_sensitive:
        raise RuntimeError(
            "Sensitive method blocked. Re-run with --allow-sensitive if intentional."
        )
    if not callable(fn):
        raise RuntimeError(f"Method not found: {args.method}")

    call_args = json.loads(args.args_json) if args.args_json else []
    call_kwargs = json.loads(args.kwargs_json) if args.kwargs_json else {}

    if not isinstance(call_args, list):
        raise RuntimeError("--args-json must decode to a JSON array")
    if not isinstance(call_kwargs, dict):
        raise RuntimeError("--kwargs-json must decode to a JSON object")

    result = fn(*call_args, **call_kwargs)
    if inspect.isawaitable(result):
        result = await result

    if isinstance(result, str):
        try:
            result = json.loads(result)
        except Exception:
            pass

    print(json.dumps({"ok": True, "entity": args.entity, "id": args.id, "method": args.method, "result": _jsonable(result)}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Control4 CLI wrapper")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("discover", help="Discover account/controller info")
    sp.set_defaults(func=cmd_discover)

    sp = sub.add_parser("list-items", help="List Control4 items")
    sp.add_argument("--category", help="Filter by category/typeName/control/name fragment")
    sp.add_argument("--compact", action="store_true", help="Compact output")
    sp.set_defaults(func=cmd_list_items)

    sp = sub.add_parser("light-set", help="Set light level")
    sp.add_argument("--id", required=True)
    sp.add_argument("--level", required=True, type=int)
    sp.add_argument("--ramp-ms", type=int, default=0)
    sp.set_defaults(func=cmd_light_set)

    sp = sub.add_parser("relay-toggle", help="Toggle relay")
    sp.add_argument("--id", required=True)
    sp.set_defaults(func=cmd_relay_toggle)

    sp = sub.add_parser("relay-set", help="Set relay state")
    sp.add_argument("--id", required=True)
    sp.add_argument("--state", required=True, choices=["open", "close"])
    sp.set_defaults(func=cmd_relay_set)

    sp = sub.add_parser("room-set-source", help="Set room source")
    sp.add_argument("--room-id", required=True)
    sp.add_argument("--source-id", required=True)
    sp.add_argument("--audio-only", action="store_true")
    sp.set_defaults(func=cmd_room_set_source)

    sp = sub.add_parser("room-mute", help="Mute/unmute/toggle room")
    sp.add_argument("--room-id", required=True)
    sp.add_argument("--state", required=True, choices=["on", "off", "toggle"])
    sp.set_defaults(func=cmd_room_mute)

    sp = sub.add_parser("room-volume", help="Set or nudge room volume")
    sp.add_argument("--room-id", required=True)
    sp.add_argument("--level", type=int)
    sp.add_argument("--delta", choices=["up", "down"])
    sp.set_defaults(func=cmd_room_volume)

    sp = sub.add_parser("room-status", help="Get room status")
    sp.add_argument("--room-id", required=True)
    sp.set_defaults(func=cmd_room_status)

    sp = sub.add_parser("methods", help="List callable methods for an entity")
    sp.add_argument("--entity", required=True, choices=["director", "light", "relay", "climate", "blind", "room", "fan", "security-panel", "contact-sensor"])
    sp.add_argument("--id", type=int)
    sp.set_defaults(func=cmd_methods)

    sp = sub.add_parser("call", help="Call any exposed method on an entity")
    sp.add_argument("--entity", required=True, choices=["director", "light", "relay", "climate", "blind", "room", "fan", "security-panel", "contact-sensor"])
    sp.add_argument("--id", type=int)
    sp.add_argument("--method", required=True)
    sp.add_argument("--args-json", help='JSON array, e.g. "[10,1000]"')
    sp.add_argument("--kwargs-json", help='JSON object, e.g. "{\"LEVEL\":20}"')
    sp.add_argument("--allow-sensitive", action="store_true", help="Allow sensitive methods (arm/disarm/open/close/etc)")
    sp.set_defaults(func=cmd_call)

    return p


def main() -> int:
    _load_env_file()
    parser = build_parser()
    args = parser.parse_args()
    try:
        return asyncio.run(args.func(args))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
