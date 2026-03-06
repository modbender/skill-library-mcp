#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
google_tv_skill.py

Control Chromecast with Google TV and cast to it via ADB.

Usage:
  ./google_tv_skill.py status [--device IP] [--port PORT]
  ./google_tv_skill.py pair [--pairing-ip IP] [--pairing-port PORT] [--pairing-code CODE] [--save-to-cache] [--show-instructions]
  ./google_tv_skill.py play <query_or_id_or_url> [--device IP] [--port PORT]
  ./google_tv_skill.py pause [--device IP] [--port PORT]
  ./google_tv_skill.py resume [--device IP] [--port PORT]

Notes:
- Requires uv and adb on PATH; no venv required.
- Caches last successful IP:PORT to .last_device.json in the skill folder.
- Does NOT perform port scanning. It will attempt the explicit port passed or cached one.
- Pairing: Use `pair` command to perform ADB wireless pairing with your Chromecast. This is a prerequisite before connecting.
  - Use --show-instructions to display detailed setup guide.
  - After pairing, use the connection port shown on the Wireless debugging screen for other commands.
  - If connection is refused, the script will offer to retry or pair interactively (when running in a tty).
- YouTube: prefers resolving to a video ID using the yt-api CLI (calls `yt-api` on PATH). If an ID is obtained, it launches the YouTube app via ADB intent restricted to the YouTube package.
- Tubi: expects an https URL. The script will attempt a VIEW https intent restricted to the Tubi package.

Architecture:
- All ADB connection management and device discovery happens here.
- The global-search fallback (play_show_via_global_search.py) is a helper that receives an already-connected device address.
- The fallback only orchestrates UI automation via pre-established ADB connection.

Exit codes:
  0 success
  2 adb connect/connection error
  3 resolution (YouTube ID) failure
  4 adb command failure

"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple
from urllib.parse import parse_qs, urlparse

SKILL_DIR = Path(__file__).resolve().parent
CACHE_FILE = SKILL_DIR / '.last_device.json'
ADB_TIMEOUT_SECONDS = 10
ADB_CONNECT_ATTEMPTS = 3
DEFAULT_YOUTUBE_PACKAGE = 'com.google.android.youtube.tv'
DEFAULT_TUBI_PACKAGE = 'com.tubitv'

YOUTUBE_ID_RE = re.compile(r'^[A-Za-z0-9_-]{6,}$')
YOUTUBE_HOSTS = {'youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com'}
YOUTUBE_SHORT_HOSTS = {'youtu.be', 'www.youtu.be'}

KEYCODE_MEDIA_PLAY = 126
KEYCODE_MEDIA_PAUSE = 127

def print_pairing_instructions():
    """Display instructions for enabling wireless debugging and pairing with Chromecast."""
    print("""
=== ADB Wireless Debugging & Pairing Instructions ===

To pair with your Chromecast with Google TV:

1. Enable Developer Options on your Chromecast:
   - Navigate to Settings > System > About
   - Scroll down to "Android TV OS build"
   - Press SELECT on the build number 7 times
   - You'll see "You are now a developer!" message

2. Enable USB Debugging and Wireless Debugging:
   - Go back to Settings > System > Developer options
   - Turn ON "USB debugging"
   - Turn ON "Wireless debugging"

3. Pair with pairing code:
   - In Wireless debugging menu, select "Pair device with pairing code"
   - A dialog will show:
     * IP address and port (e.g., 192.168.1.100:12345)
     * 6-digit pairing code
   - Use these values with the `pair` command:
     ./run pair --pairing-ip <IP> --pairing-port <PORT> --pairing-code <CODE>
   - Example:
     ./run pair --pairing-ip 192.168.1.100 --pairing-port 12345 --pairing-code 123456

4. Get the connection port:
   - After successful pairing, press BACK on the Chromecast remote
   - You'll see the Wireless debugging screen with IP address and port
   - This port is what you'll use for --port in other commands
   - Example: ./run status --device 192.168.1.100 --port <CONNECTION_PORT>

Note: Pairing only needs to be done once. After pairing, you can connect
directly using the device IP and connection port shown on the Wireless debugging screen.

If connection is refused, you may need to re-pair or verify that Wireless
debugging is still enabled on the Chromecast.
""")

def adb_pair(ip: str, port: int, code: str, timeout: int = ADB_TIMEOUT_SECONDS) -> Tuple[bool, str]:
    """
    Pair with a device using ADB wireless pairing.
    Returns (success, output_message).
    """
    addr = f"{ip}:{port}"
    cmd = ['adb', 'pair', addr, code]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (p.stdout or '') + (p.stderr or '')
        # Treat adb's return code as the primary success indicator. The output may contain
        # phrases like "Successfully paired" or "paired to", but that is not required.
        success = p.returncode == 0
        return success, out
    except FileNotFoundError:
        return False, 'adb not found on PATH'
    except subprocess.TimeoutExpired:
        return False, f'adb pair timed out after {timeout} seconds'
    except Exception as e:
        return False, str(e)

def ensure_python3() -> bool:
    if sys.version_info[0] < 3:
        print('python3 is required. Please run with python3.')
        return False
    return True

def load_cache() -> Optional[dict]:
    if not CACHE_FILE.exists():
        return None
    try:
        data = json.loads(CACHE_FILE.read_text())
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    ip = data.get('ip')
    port = data.get('port')
    if not ip or port is None:
        return None
    try:
        port_int = int(port)
    except Exception:
        return None
    return {'ip': str(ip), 'port': port_int}

def save_cache(ip: str, port: int):
    try:
        CACHE_FILE.write_text(json.dumps({'ip': ip, 'port': int(port)}))
    except Exception as e:
        print(f'Failed to write cache: {e}')

def adb_available() -> bool:
    return bool(shutil.which('adb'))

def uv_available() -> bool:
    return bool(shutil.which('uv'))

def is_youtube_id(value: str) -> bool:
    return bool(YOUTUBE_ID_RE.fullmatch(value or ''))

def extract_youtube_id(value: str) -> Optional[str]:
    """
    Extract a YouTube video ID from an ID string or a YouTube URL.
    """
    if not value:
        return None
    value = value.strip()
    if is_youtube_id(value):
        return value

    try:
        parsed = urlparse(value)
    except Exception:
        return None

    if not parsed.scheme or not parsed.netloc:
        return None

    host = parsed.netloc.lower()
    if host in YOUTUBE_SHORT_HOSTS:
        candidate = parsed.path.lstrip('/').split('/')[0]
        return candidate if is_youtube_id(candidate) else None

    if host in YOUTUBE_HOSTS:
        if parsed.path in ('/watch', '/watch/'):
            qs = parse_qs(parsed.query or '')
            candidate = (qs.get('v') or [None])[0]
            if candidate and is_youtube_id(candidate):
                return candidate
        for prefix in ('/shorts/', '/embed/', '/live/'):
            if parsed.path.startswith(prefix):
                candidate = parsed.path[len(prefix):].split('/')[0]
                return candidate if is_youtube_id(candidate) else None
        if parsed.fragment:
            frag = parsed.fragment
            if frag.startswith('watch?'):
                qs = parse_qs(frag[len('watch?'):])
                candidate = (qs.get('v') or [None])[0]
                if candidate and is_youtube_id(candidate):
                    return candidate
    return None

def find_video_id(data) -> Optional[str]:
    """
    Walk a JSON-like structure and return the first plausible YouTube video id.
    """
    if isinstance(data, dict):
        for key in ('videoId', 'video_id', 'id'):
            val = data.get(key)
            if isinstance(val, str) and is_youtube_id(val):
                return val
            if isinstance(val, dict):
                nested = find_video_id(val)
                if nested:
                    return nested
        for val in data.values():
            nested = find_video_id(val)
            if nested:
                return nested
    elif isinstance(data, list):
        for item in data:
            nested = find_video_id(item)
            if nested:
                return nested
    return None

def yt_api_candidates() -> Iterable[str]:
    seen = set()
    path = shutil.which('yt-api')
    if path:
        seen.add(path)
        yield path

def run_adb(args: Sequence[str], device: Optional[str] = None, timeout: int = ADB_TIMEOUT_SECONDS) -> Tuple[int, str]:
    cmd = ['adb']
    if device:
        cmd += ['-s', device]
    cmd += list(args)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (p.stdout or '') + (p.stderr or '')
        return p.returncode, out
    except FileNotFoundError:
        return 127, 'adb not found on PATH'
    except Exception as e:
        return 1, str(e)


def adb_shell(args: Sequence[str], device: Optional[str], timeout: int = ADB_TIMEOUT_SECONDS) -> Tuple[int, str]:
    return run_adb(['shell', *args], device, timeout=timeout)

def adb_intent_view(device: str, url: str, package: Optional[str] = None) -> Tuple[bool, str]:
    cmd = ['am', 'start', '-a', 'android.intent.action.VIEW', '-d', url]
    if package and package.strip():
        cmd += ['-p', package]
    code, out = adb_shell(cmd, device)
    return code == 0, out

def youtube_package() -> str:
    return (os.environ.get('YOUTUBE_PACKAGE') or DEFAULT_YOUTUBE_PACKAGE).strip()

def tubi_package() -> str:
    return (os.environ.get('TUBI_PACKAGE') or DEFAULT_TUBI_PACKAGE).strip()

def launch_global_search_show(
    show: str,
    season: int,
    episode: int,
    app_name: str,
    device: str,
) -> Tuple[bool, str]:
    """Launch global-search fallback with pre-verified device connection.
    
    Passes the already-connected device address to the fallback helper.
    The helper only orchestrates UI automation; all ADB connection logic
    remains in google_tv_skill.py.
    """
    script_path = SKILL_DIR / 'play_show_via_global_search.py'
    cmd = [
        'uv',
        'run',
        str(script_path),
        show,
        str(season),
        str(episode),
        '--device',
        device,
        '--app',
        app_name,
    ]
    try:
        p = subprocess.run(cmd, timeout=180)
    except subprocess.TimeoutExpired:
        return False, 'Global search helper timed out after 180 seconds'
    except Exception as e:
        return False, str(e)
    return p.returncode == 0, ''

def adb_connect(
    ip: str,
    port: int,
    timeout: int = ADB_TIMEOUT_SECONDS,
    attempts: int = ADB_CONNECT_ATTEMPTS,
) -> Tuple[bool, str]:
    """
    Attempt to adb connect with a small retry/backoff strategy.
    Returns (ok, output).
    """
    addr = f"{ip}:{port}"
    last_out = ''
    for attempt in range(1, attempts + 1):
        code, out = run_adb(['connect', addr], None, timeout=timeout)
        last_out = out
        if code == 127:
            return False, out
        ok = code == 0 and ('connected to' in out.lower() or 'already connected' in out.lower())
        if ok:
            return True, out
        # short exponential backoff (0.5s, 1s, 2s)
        if attempt < attempts:
            backoff = 0.5 * (2 ** (attempt - 1))
            try:
                time.sleep(backoff)
            except Exception:
                pass
    return False, last_out

def discover_mdns_device() -> Optional[dict]:
    code, out = run_adb(['mdns', 'services'])
    if code != 0:
        return None
    match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', out)
    if not match:
        return None
    try:
        return {'ip': match.group(1), 'port': int(match.group(2))}
    except Exception:
        return None

def connection_refused(message: str) -> bool:
    if not message:
        return False
    lowered = message.lower()
    return (
        'connection refused' in lowered
        or 'refused' in lowered
        or 'failed to connect' in lowered
        or 'cannot connect' in lowered
    )

def prompt_for_port(ip: str) -> Optional[int]:
    if not sys.stdin.isatty():
        return None
    prompt = f'Enter new ADB port for {ip} (blank to cancel): '
    while True:
        try:
            value = input(prompt).strip()
        except EOFError:
            return None
        if not value:
            return None
        if value.isdigit():
            port = int(value)
            if 0 < port < 65536:
                return port
        print('Invalid port. Enter a number between 1 and 65535.')

def prompt_for_pairing(ip: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Prompt user to pair with the device when connection is refused.
    Returns (device_spec, error_message).
    """
    if not sys.stdin.isatty():
        return None, None

    print(f"\nConnection to {ip} refused. This may mean the device needs to be paired.")
    print("Options:")
    print("  1. Retry with a different port")
    print("  2. Pair with the device")
    print("  3. Show pairing instructions")
    print("  4. Cancel")

    while True:
        try:
            choice = input("Enter choice (1-4): ").strip()
        except EOFError:
            return None, None

        if choice == '1':
            # Retry with different port
            new_port = prompt_for_port(ip)
            if not new_port:
                return None, None
            ok, out = adb_connect(ip, new_port)
            if ok:
                save_cache(ip, new_port)
                return f"{ip}:{new_port}", None
            return None, f'adb connect failed (new port): {out.strip()}'

        elif choice == '2':
            # Pair with device
            print("\nEnter pairing details from Chromecast 'Pair device with pairing code' screen:")
            try:
                pairing_ip = input(f"Pairing IP address (default: {ip}): ").strip() or ip
                pairing_port_str = input("Pairing port: ").strip()
                if not pairing_port_str:
                    print("Pairing port is required.")
                    continue
                pairing_port = int(pairing_port_str)
                if not (1 <= pairing_port <= 65535):
                    print("Pairing port must be between 1 and 65535.")
                    continue
                pairing_code = input("6-digit pairing code: ").strip()
                if not pairing_code:
                    print("Pairing code is required.")
                    continue
            except (ValueError, EOFError):
                print("Invalid input.")
                continue

            print(f"Pairing with {pairing_ip}:{pairing_port}...")
            ok, out = adb_pair(pairing_ip, pairing_port, pairing_code)
            if ok:
                print("Successfully paired!")
                print("\nNow enter the connection port from the Wireless debugging screen")
                print("(press BACK on the Chromecast remote to see it):")
                try:
                    connect_port_str = input(f"Connection port: ").strip()
                    if not connect_port_str:
                        print("Connection port is required.")
                        continue
                    connect_port = int(connect_port_str)
                    if not (1 <= connect_port <= 65535):
                        print("Connection port must be between 1 and 65535.")
                        continue
                except ValueError:
                    print("Invalid port value.")
                    continue
                except EOFError:
                    print("Input cancelled.")
                    continue

                ok_connect, out_connect = adb_connect(pairing_ip, connect_port)
                if ok_connect:
                    save_cache(pairing_ip, connect_port)
                    return f"{pairing_ip}:{connect_port}", None
                print(f"Pairing succeeded but connection failed: {out_connect.strip()}")
                print("You can try a different connection port or select another option.")
                continue
            else:
                print(f"Pairing failed: {out.strip()}")
                print("Please verify the pairing code and try again.")
                continue

        elif choice == '3':
            # Show instructions
            print_pairing_instructions()
            continue

        elif choice == '4':
            # Cancel
            return None, None

        else:
            print("Invalid choice. Enter 1, 2, 3, or 4.")

def try_prompt_new_port(ip: str, message: str) -> Tuple[Optional[str], Optional[str]]:
    if not connection_refused(message):
        return None, None
    return prompt_for_pairing(ip)

def ensure_connected(ip: Optional[str], port: Optional[int]) -> Tuple[Optional[str], Optional[str]]:
    # Returns (device_spec, error_message)
    cache = load_cache()

    if ip and not port:
        if cache and cache['ip'] == ip:
            port = cache['port']
        else:
            return None, f'port required for device {ip} (no cached port available)'

    if port and not ip:
        if cache:
            ip = cache['ip']
        else:
            return None, 'device IP required when port is provided without cache'

    if not ip and not port:
        if cache:
            ip = cache['ip']
            port = cache['port']
        else:
            mdns_device = discover_mdns_device()
            if mdns_device:
                ip = mdns_device['ip']
                port = mdns_device['port']
            else:
                return None, 'no device specified and no cached device found'

    ok, out = adb_connect(ip, port)
    if ok:
        save_cache(ip, port)
        return f"{ip}:{port}", None

    # If connection failed and looks like a refused/timeout error, try mDNS rediscovery
    # before prompting the user. This handles cases where the device moved to a new IP
    # (e.g., after router restart or network change).
    if connection_refused(out):
        mdns_device = discover_mdns_device()
        if mdns_device:
            mdns_ip = mdns_device['ip']
            mdns_port = mdns_device['port']
            ok_mdns, out_mdns = adb_connect(mdns_ip, mdns_port)
            if ok_mdns:
                save_cache(mdns_ip, mdns_port)
                return f"{mdns_ip}:{mdns_port}", None

    prompted_device, prompt_err = try_prompt_new_port(ip, out)
    if prompted_device:
        return prompted_device, None
    if prompt_err:
        return None, prompt_err

    if cache and (cache['ip'], cache['port']) != (ip, port):
        ok2, out2 = adb_connect(cache['ip'], cache['port'])
        if ok2:
            return f"{cache['ip']}:{cache['port']}", None

        # For cached fallback, also try mDNS rediscovery if connection refused
        if connection_refused(out2):
            mdns_device = discover_mdns_device()
            if mdns_device:
                mdns_ip = mdns_device['ip']
                mdns_port = mdns_device['port']
                ok_mdns, out_mdns = adb_connect(mdns_ip, mdns_port)
                if ok_mdns:
                    save_cache(mdns_ip, mdns_port)
                    return f"{mdns_ip}:{mdns_port}", None

        prompted_device, prompt_err = try_prompt_new_port(cache['ip'], out2)
        if prompted_device:
            return prompted_device, None
        if prompt_err:
            return None, prompt_err

        return None, f'adb connect failed (explicit): {out.strip()} ; cached attempt: {out2.strip()}'

    return None, f'adb connect failed: {out.strip()}'

def status_cmd(args) -> int:
    device, err = ensure_connected(args.ip, args.port)
    if not device:
        if err:
            print(err)
        code, out = run_adb(['devices'])
        print(out.strip())
        return 2
    code, out = run_adb(['devices'])
    print(out.strip())
    return 0 if code == 0 else 4

def pair_cmd(args) -> int:
    """Handle the pair command to pair with a Chromecast device."""
    if args.show_instructions:
        print_pairing_instructions()
        return 0

    if not args.pairing_ip or not args.pairing_port or not args.pairing_code:
        print("Error: --pairing-ip, --pairing-port, and --pairing-code are required for pairing.")
        print("\nTo see pairing instructions, run: ./run pair --show-instructions")
        return 1

    print(f"Pairing with {args.pairing_ip}:{args.pairing_port}...")
    ok, out = adb_pair(args.pairing_ip, args.pairing_port, args.pairing_code)

    if ok:
        print("Successfully paired!")
        print("\nNext steps:")
        print("1. Press BACK on the Chromecast remote to return to Wireless debugging screen")
        print("2. Note the IP address and port shown on that screen")
        print("3. Use these values to connect:")
        print(f"   ./run status --device {args.pairing_ip} --port <CONNECTION_PORT>")

        # If cache should be updated with pairing IP and a chosen connection port
        if args.save_to_cache:
            if sys.stdin.isatty():
                try:
                    port_input = input("\nEnter connection port to save: ").strip()
                except EOFError:
                    port_input = ""

                if not port_input:
                    print("Connection port is required; cache was not updated.")
                    port = None
                else:
                    try:
                        port = int(port_input)
                        if not (1 <= port <= 65535):
                            print("Connection port must be between 1 and 65535; cache was not updated.")
                            port = None
                    except ValueError:
                        print("Invalid port value entered; cache was not updated.")
                        port = None

                if port is not None:
                    save_cache(args.pairing_ip, port)
                    print(f"\nSaved {args.pairing_ip}:{port} to cache.")
            else:
                print(
                    "\nNon-interactive session detected; skipping cache update. "
                    "Use --device and --port explicitly on future commands."
                )
        return 0
    else:
        print(f"Pairing failed: {out.strip()}")
        print("\nTroubleshooting:")
        print("- Verify the pairing code is correct (6 digits)")
        print("- Make sure you're using the pairing port, not the connection port")
        print("- Ensure Wireless debugging is enabled on the Chromecast")
        print("\nFor detailed instructions, run: ./run pair --show-instructions")
        return 2

def pause_cmd(args) -> int:
    device, err = ensure_connected(args.ip, args.port)
    if not device:
        print(err)
        return 2
    # Send media keycode: KEYCODE_MEDIA_PAUSE (127)
    code, out = adb_shell(['input', 'keyevent', str(KEYCODE_MEDIA_PAUSE)], device)
    if code != 0:
        print('adb command failed:', out)
        return 4
    print('paused')
    return 0

def resume_cmd(args) -> int:
    device, err = ensure_connected(args.ip, args.port)
    if not device:
        print(err)
        return 2
    code, out = adb_shell(['input', 'keyevent', str(KEYCODE_MEDIA_PLAY)], device)
    if code != 0:
        print('adb command failed:', out)
        return 4
    print('resumed')
    return 0

def resolve_youtube_id_with_yt_api(query: str) -> Optional[str]:
    """
    Try to resolve a YouTube ID using an available yt-api CLI on PATH.
    Expects a simple invocation that returns JSON or plain ID when asked.
    """
    for bin_path in yt_api_candidates():
        try:
            p = subprocess.run([bin_path, 'search', query], capture_output=True, text=True, timeout=15)
            out = (p.stdout or '').strip()
            if p.returncode != 0:
                continue
            if not out:
                continue

            try:
                data = json.loads(out)
                found = find_video_id(data)
                if found:
                    return found
            except Exception:
                pass

            for line in out.splitlines():
                candidate = extract_youtube_id(line.strip())
                if candidate:
                    return candidate

            m = re.search(r'v=([A-Za-z0-9_-]{6,})', out)
            if m:
                return m.group(1)
            if is_youtube_id(out):
                return out
        except FileNotFoundError:
            continue
        except Exception as e:
            continue
    return None

def launch_youtube_intent(device: str, video_id: str) -> Tuple[bool, str]:
    url = f'https://www.youtube.com/watch?v={video_id}'
    return adb_intent_view(device, url, youtube_package())

def looks_like_tubi(term: str) -> bool:
    if not term:
        return False
    value = term.strip().lower()
    return (
        value.startswith('https://www.tubitv.com/')
        or value.startswith('https://tubitv.com/')
        or value.startswith('www.tubitv.com/')
        or value.startswith('tubitv.com/')
        or 'tubitv.com' in value
    )

def handle_tubi(device: str, term: str) -> Tuple[bool, str]:
    if term.startswith('https://'):
        return adb_intent_view(device, term, tubi_package())

    if term.startswith('tubitv.com') or term.startswith('www.tubitv.com'):
        return adb_intent_view(device, f'https://{term}', tubi_package())

    return False, 'Tubi term must be an https Tubi URL.'


def play_cmd(args) -> int:
    device, err = ensure_connected(args.ip, args.port)
    if not device:
        print(err)
        return 2
    query = args.query.strip()
    app_raw = (args.app or '').strip()
    app_hint = app_raw.lower()

    if app_hint == 'tubi':
        ok, out = handle_tubi(device, query)
        if ok:
            print('launched tubi')
            return 0
        print('tubi launch failed:', out)
        return 4

    if app_hint == 'youtube':
        video_id = extract_youtube_id(query) or resolve_youtube_id_with_yt_api(query)
        if not video_id:
            print('failed to resolve YouTube ID for query')
            return 3
        ok, out = launch_youtube_intent(device, video_id)
        if ok:
            print('launched youtube video', video_id)
            return 0
        print('adb intent failed:', out)
        return 4

    video_id = extract_youtube_id(query)
    if video_id:
        ok, out = launch_youtube_intent(device, video_id)
        if ok:
            print('launched youtube video', video_id)
            return 0
        print('adb intent failed:', out)
        return 4

    if looks_like_tubi(query):
        ok, out = handle_tubi(device, query)
        if ok:
            print('launched tubi')
            return 0

    # Otherwise attempt to resolve a YouTube ID using yt-api CLI as requested
    video_id = resolve_youtube_id_with_yt_api(query)
    if video_id:
        ok, out = launch_youtube_intent(device, video_id)
        if ok:
            print('launched youtube video', video_id)
            return 0
        print('adb intent failed:', out)
        return 4

    if app_raw and app_hint not in {'youtube', 'tubi'}:
        if args.season is None or args.episode is None:
            print('for non-youtube/tubi fallback, pass --season and --episode')
            return 1
        ok, out = launch_global_search_show(query, args.season, args.episode, app_raw, device)
        if ok:
            print('launched global-search fallback')
            return 0
        print('global-search fallback failed:', out)
        return 4

    print('failed to resolve YouTube ID for query')
    print('for non-youtube/tubi content, pass --app "<streaming app>" --season N --episode N')
    return 3

def build_parser():
    p = argparse.ArgumentParser(prog='google_tv_skill.py')
    sub = p.add_subparsers(dest='cmd')

    sp_status = sub.add_parser('status')
    sp_status.add_argument('--device', dest='ip', help='Chromecast IP address')
    sp_status.add_argument('--port', type=int, dest='port', help='ADB port')
    sp_status.set_defaults(func=status_cmd)

    sp_pair = sub.add_parser('pair', help='Pair with Chromecast using wireless debugging')
    sp_pair.add_argument('--pairing-ip', dest='pairing_ip', help='IP address from pairing screen')
    sp_pair.add_argument('--pairing-port', type=int, dest='pairing_port', help='Port from pairing screen')
    sp_pair.add_argument('--pairing-code', dest='pairing_code', help='6-digit pairing code')
    sp_pair.add_argument('--save-to-cache', action='store_true', help='Save paired device to cache')
    sp_pair.add_argument('--show-instructions', action='store_true', help='Display pairing instructions')
    sp_pair.set_defaults(func=pair_cmd)

    sp_play = sub.add_parser('play')
    sp_play.add_argument('query', help='Query, YouTube id, or provider-specific id/url')
    sp_play.add_argument('--device', dest='ip', help='Chromecast IP address')
    sp_play.add_argument('--port', type=int, dest='port', help='ADB port')
    sp_play.add_argument('--app', dest='app', help='App hint (youtube, tubi, or streaming app for fallback)')
    sp_play.add_argument('--season', type=int, help='Season number for non-youtube/tubi fallback')
    sp_play.add_argument('--episode', type=int, help='Episode number for non-youtube/tubi fallback')
    sp_play.set_defaults(func=play_cmd)

    sp_pause = sub.add_parser('pause')
    sp_pause.add_argument('--device', dest='ip', help='Chromecast IP address')
    sp_pause.add_argument('--port', type=int, dest='port', help='ADB port')
    sp_pause.set_defaults(func=pause_cmd)

    sp_resume = sub.add_parser('resume')
    sp_resume.add_argument('--device', dest='ip', help='Chromecast IP address')
    sp_resume.add_argument('--port', type=int, dest='port', help='ADB port')
    sp_resume.set_defaults(func=resume_cmd)

    return p

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not ensure_python3():
        return 2
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 1

    # Apply env overrides
    if hasattr(args, 'ip') and not args.ip:
        args.ip = os.environ.get('CHROMECAST_HOST')
    if hasattr(args, 'port') and not args.port:
        p = os.environ.get('CHROMECAST_PORT')
        if p:
            try:
                args.port = int(p)
            except Exception:
                pass

    if not uv_available():
        print('uv not found on PATH. Install uv and run again.')
        return 2
    if not adb_available():
        print('adb not found on PATH. Install Android platform-tools and ensure adb is available.')
        return 2

    # Run the command
    try:
        rc = args.func(args)
    except Exception as e:
        print('error:', e)
        return 1
    return rc

if __name__ == '__main__':
    raise SystemExit(main())
