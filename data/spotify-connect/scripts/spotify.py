#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["spotipy>=2.24.0"]
# ///
"""Spotify Connect controller for OpenClaw — multi-account support."""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth

CONFIG_DIR = Path.home() / ".openclaw" / "spotify-connect"
ACCOUNTS_PATH = CONFIG_DIR / "accounts.json"
DEVICES_PATH = CONFIG_DIR / "devices.json"
SCOPES = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

# Legacy single-account token path (migrated on first use)
LEGACY_TOKEN_PATH = CONFIG_DIR / "token.json"


def load_accounts():
    """Load accounts config. Structure:
    {
      "active": "alice",
      "accounts": {
        "alice": {"email": "alice@example.com", "token_file": "token_alice.json"},
        "bob": {"email": "bob@example.com", "token_file": "token_bob.json"}
      }
    }
    """
    if ACCOUNTS_PATH.exists():
        return json.loads(ACCOUNTS_PATH.read_text())
    # Migrate legacy single-account setup
    if LEGACY_TOKEN_PATH.exists():
        accounts = {
            "active": "default",
            "accounts": {
                "default": {"email": "", "token_file": "token.json"}
            }
        }
        save_accounts(accounts)
        return accounts
    return {"active": None, "accounts": {}}


def save_accounts(accounts):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ACCOUNTS_PATH.write_text(json.dumps(accounts, indent=2) + "\n")
    ACCOUNTS_PATH.chmod(0o600)


def get_active_account(accounts):
    active = accounts.get("active")
    if not active or active not in accounts.get("accounts", {}):
        print("ERROR: No active account. Run 'auth' to add one or 'switch' to select.", file=sys.stderr)
        sys.exit(1)
    return active, accounts["accounts"][active]


def get_sp(account_name=None):
    """Create authenticated Spotify client for the given or active account."""
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("ERROR: Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET env vars", file=sys.stderr)
        sys.exit(1)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    accounts = load_accounts()
    if account_name:
        if account_name not in accounts.get("accounts", {}):
            print(f"ERROR: Account '{account_name}' not found. Use 'accounts' to list.", file=sys.stderr)
            sys.exit(1)
        acct = accounts["accounts"][account_name]
    else:
        _, acct = get_active_account(accounts)

    token_file = CONFIG_DIR / acct["token_file"]
    auth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://127.0.0.1:8888/callback",
        scope=SCOPES,
        cache_path=str(token_file),
    )
    return spotipy.Spotify(auth_manager=auth)


def load_aliases():
    """Load device name aliases."""
    if DEVICES_PATH.exists():
        return json.loads(DEVICES_PATH.read_text())
    return {}


def resolve_device(sp, name):
    """Resolve a device name/alias to a device ID. Fuzzy match."""
    if not name:
        return None
    aliases = load_aliases()
    target = aliases.get(name.lower(), name)
    devices = sp.devices().get("devices", [])
    if not devices:
        print("ERROR: No Spotify devices found. Open Spotify on a device first.", file=sys.stderr)
        sys.exit(1)
    # Exact match
    for d in devices:
        if d["name"].lower() == target.lower():
            return d["id"]
    # Fuzzy: substring match
    matches = [d for d in devices if target.lower() in d["name"].lower()]
    if len(matches) == 1:
        return matches[0]["id"]
    if len(matches) > 1:
        print(f"ERROR: Ambiguous device '{name}'. Matches:", file=sys.stderr)
        for m in matches:
            print(f"  - {m['name']} ({m['type']})", file=sys.stderr)
        sys.exit(1)
    print(f"ERROR: Device '{name}' not found. Available devices:", file=sys.stderr)
    for d in devices:
        print(f"  - {d['name']} ({d['type']}) {'[active]' if d['is_active'] else ''}", file=sys.stderr)
    sys.exit(1)


def cmd_auth(args):
    """Authenticate a Spotify account. Optionally name it."""
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("ERROR: Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET env vars", file=sys.stderr)
        sys.exit(1)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    accounts = load_accounts()
    name = args.name if args.name else "default"
    token_file = f"token_{name}.json"

    auth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://127.0.0.1:8888/callback",
        scope=SCOPES,
        cache_path=str(CONFIG_DIR / token_file),
    )
    sp = spotipy.Spotify(auth_manager=auth)
    user = sp.current_user()
    email = user.get("email", "")
    display = user.get("display_name", user["id"])

    acct_entry = {"email": email, "display_name": display, "token_file": token_file}
    if "accounts" not in accounts:
        accounts["accounts"] = {}
    accounts["accounts"][name] = acct_entry

    # Auto-activate if first account or no active
    if not accounts.get("active") or len(accounts["accounts"]) == 1:
        accounts["active"] = name

    save_accounts(accounts)
    active_marker = " [active]" if accounts["active"] == name else ""
    print(f"Authenticated: {display} ({email})")
    print(f"Account name: {name}{active_marker}")
    print(f"Token cached: {CONFIG_DIR / token_file}")


def cmd_accounts(_args):
    """List all authenticated accounts."""
    accounts = load_accounts()
    active = accounts.get("active")
    accts = accounts.get("accounts", {})
    if not accts:
        print("No accounts configured. Run 'auth' to add one.")
        return
    for name, info in accts.items():
        marker = " [active]" if name == active else ""
        email = info.get("email", "")
        display = info.get("display_name", "")
        label = display if display else email if email else "unknown"
        print(f"  {name} — {label} ({email}){marker}")


def cmd_switch(args):
    """Switch active account by name or email."""
    accounts = load_accounts()
    target = args.account.lower()
    accts = accounts.get("accounts", {})

    # Try exact name match
    if target in accts:
        accounts["active"] = target
        save_accounts(accounts)
        info = accts[target]
        print(f"Switched to: {target} ({info.get('email', '')})")
        return

    # Try email match
    for name, info in accts.items():
        if info.get("email", "").lower() == target:
            accounts["active"] = name
            save_accounts(accounts)
            print(f"Switched to: {name} ({info.get('email', '')})")
            return

    # Fuzzy name match
    matches = [n for n in accts if target in n.lower()]
    if len(matches) == 1:
        accounts["active"] = matches[0]
        save_accounts(accounts)
        info = accts[matches[0]]
        print(f"Switched to: {matches[0]} ({info.get('email', '')})")
        return

    print(f"ERROR: Account '{args.account}' not found. Available:", file=sys.stderr)
    for name, info in accts.items():
        print(f"  {name} — {info.get('email', '')}", file=sys.stderr)
    sys.exit(1)


def cmd_logout(args):
    """Remove an account's cached token."""
    accounts = load_accounts()
    target = args.account
    accts = accounts.get("accounts", {})

    if target not in accts:
        print(f"ERROR: Account '{target}' not found.", file=sys.stderr)
        sys.exit(1)

    info = accts[target]
    token_file = CONFIG_DIR / info["token_file"]
    if token_file.exists():
        token_file.unlink()
        print(f"Removed token: {token_file}")

    del accts[target]
    if accounts.get("active") == target:
        accounts["active"] = next(iter(accts), None)
        if accounts["active"]:
            print(f"Active account switched to: {accounts['active']}")
        else:
            print("No accounts remaining.")

    save_accounts(accounts)
    print(f"Logged out: {target}")


def _fetch_devices_for_account(account_name):
    """Fetch devices for a single account. Returns (account_name, devices_list, error)."""
    try:
        sp = get_sp(account_name)
        devices = sp.devices().get("devices", [])
        return (account_name, devices, None)
    except SystemExit:
        return (account_name, [], "auth error")
    except Exception as e:
        return (account_name, [], str(e))


def cmd_devices(args):
    """List available Spotify Connect devices."""
    all_accounts = getattr(args, "all_accounts", False)
    aliases = load_aliases()
    alias_reverse = {v.lower(): k for k, v in aliases.items()}

    if all_accounts:
        accounts = load_accounts()
        acct_names = list(accounts.get("accounts", {}).keys())
        if not acct_names:
            print("No accounts configured. Run 'auth' to add one.")
            return

        # Parallel fetch across all accounts
        results = []
        with ThreadPoolExecutor(max_workers=len(acct_names)) as pool:
            futures = {pool.submit(_fetch_devices_for_account, name): name for name in acct_names}
            for future in as_completed(futures):
                results.append(future.result())

        # Sort by account name for consistent output
        results.sort(key=lambda r: r[0])
        active = accounts.get("active")
        total = 0
        for acct_name, devices, error in results:
            marker = " [active]" if acct_name == active else ""
            print(f"[{acct_name}]{marker}:")
            if error:
                print(f"  (error: {error})")
                continue
            if not devices:
                print("  (no devices online)")
                continue
            for d in devices:
                act = " [active]" if d["is_active"] else ""
                alias = alias_reverse.get(d["name"].lower(), "")
                alias_str = f" (alias: {alias})" if alias else ""
                vol = f" vol:{d['volume_percent']}%" if d.get("volume_percent") is not None else ""
                print(f"  {d['name']} — {d['type']}{vol}{act}{alias_str}")
                total += 1
        print(f"\n{total} device(s) across {len(acct_names)} account(s)")
    else:
        sp = get_sp()
        devices = sp.devices().get("devices", [])
        if not devices:
            print("No devices found. Open Spotify on a device first.")
            return
        for d in devices:
            active = " [active]" if d["is_active"] else ""
            alias = alias_reverse.get(d["name"].lower(), "")
            alias_str = f" (alias: {alias})" if alias else ""
            vol = f" vol:{d['volume_percent']}%" if d.get("volume_percent") is not None else ""
            print(f"  {d['name']} — {d['type']}{vol}{active}{alias_str}")


def cmd_play(args):
    """Play music."""
    sp = get_sp()
    device_id = resolve_device(sp, args.device) if args.device else None
    kwargs = {}
    if device_id:
        kwargs["device_id"] = device_id

    if args.uri:
        uri = args.uri
        if uri.startswith("spotify:track:"):
            kwargs["uris"] = [uri]
        else:
            kwargs["context_uri"] = uri
        sp.start_playback(**kwargs)
        print(f"Playing URI: {uri}")
        return

    if args.query:
        query = args.query
        search_type = "track"
        q = query
        for prefix in ("artist:", "album:", "playlist:"):
            if query.lower().startswith(prefix):
                search_type = prefix.rstrip(":")
                q = query[len(prefix):].strip()
                break

        results = sp.search(q=q, type=search_type, limit=1)
        items_key = search_type + "s"
        items = results.get(items_key, {}).get("items", [])
        if not items:
            print(f"No {search_type} found for: {q}", file=sys.stderr)
            sys.exit(1)

        item = items[0]
        uri = item["uri"]
        name = item.get("name", uri)
        if search_type == "track":
            artist = item.get("artists", [{}])[0].get("name", "")
            kwargs["uris"] = [uri]
            sp.start_playback(**kwargs)
            print(f"Playing: {name} — {artist}")
        else:
            kwargs["context_uri"] = uri
            sp.start_playback(**kwargs)
            label = search_type.title()
            print(f"Playing {label}: {name}")
        return

    # No query/uri — just resume
    try:
        sp.start_playback(**kwargs)
        print("Resumed playback")
    except spotipy.SpotifyException as e:
        if "NO_ACTIVE_DEVICE" in str(e) or "Not found" in str(e):
            print("ERROR: No active device. Specify --device or open Spotify somewhere.", file=sys.stderr)
            sys.exit(1)
        raise


def cmd_pause(_args):
    sp = get_sp()
    sp.pause_playback()
    print("Paused")


def cmd_next(_args):
    sp = get_sp()
    sp.next_track()
    print("Skipped to next track")


def cmd_prev(_args):
    sp = get_sp()
    sp.previous_track()
    print("Previous track")


def cmd_volume(args):
    sp = get_sp()
    try:
        level = int(args.level)
    except ValueError:
        print(f"ERROR: Volume must be a number 0-100, got '{args.level}'", file=sys.stderr)
        sys.exit(1)
    if not 0 <= level <= 100:
        print(f"ERROR: Volume must be 0-100, got {level}", file=sys.stderr)
        sys.exit(1)
    device_id = resolve_device(sp, args.device) if args.device else None
    sp.volume(level, device_id=device_id)
    print(f"Volume set to {level}%")


def cmd_shuffle(args):
    sp = get_sp()
    state = args.state.lower() == "on"
    sp.shuffle(state)
    print(f"Shuffle {'on' if state else 'off'}")


def cmd_repeat(args):
    sp = get_sp()
    sp.repeat(args.state)  # track, context, off
    print(f"Repeat: {args.state}")


def cmd_transfer(args):
    sp = get_sp()
    device_id = resolve_device(sp, args.device)
    sp.transfer_playback(device_id, force_play=True)
    print(f"Transferred playback to: {args.device}")


def cmd_status(_args):
    sp = get_sp()
    accounts = load_accounts()
    active_name, active_info = get_active_account(accounts)

    pb = sp.current_playback()
    if not pb or not pb.get("item"):
        print(f"[{active_name}] Nothing playing")
        return
    item = pb["item"]
    name = item.get("name", "Unknown")
    artists = ", ".join(a["name"] for a in item.get("artists", []))
    album = item.get("album", {}).get("name", "")
    device = pb.get("device", {})
    dev_name = device.get("name", "?")
    vol = device.get("volume_percent", "?")
    progress_ms = pb.get("progress_ms", 0)
    duration_ms = item.get("duration_ms", 0)
    progress = f"{progress_ms // 60000}:{(progress_ms // 1000) % 60:02d}"
    duration = f"{duration_ms // 60000}:{(duration_ms // 1000) % 60:02d}"
    state = "▶" if pb.get("is_playing") else "⏸"
    shuffle = "🔀" if pb.get("shuffle_state") else ""
    repeat = pb.get("repeat_state", "off")
    repeat_icon = {"track": "🔂", "context": "🔁"}.get(repeat, "")
    print(f"[{active_name}] {state} {name} — {artists}")
    print(f"   Album: {album}")
    print(f"   {progress} / {duration}  {shuffle}{repeat_icon}")
    print(f"   Device: {dev_name} (vol {vol}%)")


def main():
    parser = argparse.ArgumentParser(description="Spotify Connect controller")
    sub = parser.add_subparsers(dest="command")

    p_auth = sub.add_parser("auth", help="Authenticate a Spotify account")
    p_auth.add_argument("--name", "-n", help="Local name for this account (default: 'default')")

    sub.add_parser("accounts", help="List authenticated accounts")

    p_switch = sub.add_parser("switch", help="Switch active account")
    p_switch.add_argument("account", help="Account name or email")

    p_logout = sub.add_parser("logout", help="Remove an account")
    p_logout.add_argument("account", help="Account name to remove")

    p_dev = sub.add_parser("devices", help="List devices")
    p_dev.add_argument("--all-accounts", "-a", action="store_true", help="List devices across all accounts (parallel)")

    p_play = sub.add_parser("play", help="Play music")
    p_play.add_argument("--query", "-q", help="Search query (prefix with artist:/album:/playlist:)")
    p_play.add_argument("--uri", "-u", help="Spotify URI")
    p_play.add_argument("--device", "-d", help="Device name or alias")

    sub.add_parser("pause", help="Pause playback")
    sub.add_parser("next", help="Next track")
    sub.add_parser("prev", help="Previous track")

    p_vol = sub.add_parser("volume", help="Set volume")
    p_vol.add_argument("level", help="Volume 0-100")
    p_vol.add_argument("--device", "-d", help="Device name or alias")

    p_shuf = sub.add_parser("shuffle", help="Toggle shuffle")
    p_shuf.add_argument("state", choices=["on", "off"])

    p_rep = sub.add_parser("repeat", help="Set repeat mode")
    p_rep.add_argument("state", choices=["track", "context", "off"])

    p_trans = sub.add_parser("transfer", help="Transfer playback")
    p_trans.add_argument("device", help="Device name or alias")

    sub.add_parser("status", help="Now playing")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "auth": cmd_auth, "accounts": cmd_accounts, "switch": cmd_switch,
        "logout": cmd_logout, "devices": cmd_devices, "play": cmd_play,
        "pause": cmd_pause, "next": cmd_next, "prev": cmd_prev,
        "volume": cmd_volume, "shuffle": cmd_shuffle, "repeat": cmd_repeat,
        "transfer": cmd_transfer, "status": cmd_status,
    }
    try:
        cmds[args.command](args)
    except spotipy.SpotifyException as e:
        msg = str(e)
        if "PREMIUM_REQUIRED" in msg or "premium" in msg.lower():
            print("ERROR: Spotify Premium required for playback control.", file=sys.stderr)
        elif "NO_ACTIVE_DEVICE" in msg:
            print("ERROR: No active device. Open Spotify on a device or specify --device.", file=sys.stderr)
        else:
            print(f"Spotify API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
