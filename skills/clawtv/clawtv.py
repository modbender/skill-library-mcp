#!/usr/bin/env python3
"""
ClawTV — AI-powered Apple TV remote that can see your screen.

Tell it what you want in plain English and it navigates any app autonomously
using vision + remote control. No per-app APIs needed.

Requirements:
    - macOS with pyatv installed (pip install pyatv)
    - Anthropic API key (ANTHROPIC_API_KEY env var)
    - One of: QuickTime Player, Lookout tvOS app, or Xcode for screenshots

Usage:
    python clawtv.py pair                          # Discover and pair with your Apple TV
    python clawtv.py screenshot                    # Take a screenshot (auto-detect method)
    python clawtv.py screenshot --method quicktime # Use QuickTime mirroring
    python clawtv.py screenshot --method lookout   # Use Lookout tvOS app
    python clawtv.py screenshot --method xcode     # Use Xcode Devices (legacy)
    python clawtv.py cmd <action>                  # Send a remote command
    python clawtv.py type <text>                   # Type text into a search field
    python clawtv.py disconnect                    # Stop QuickTime mirror (restore TV audio + remove red border)
    python clawtv.py do "<goal>"                   # AI agent mode

    python clawtv.py plex play "Movie"             # Play directly via Plex API (no vision needed)
    python clawtv.py plex play "Show" -s 2 -e 6    # Play specific episode
    python clawtv.py plex search "query"            # Search Plex library
    python clawtv.py plex clients                   # List Plex clients
    python clawtv.py plex libraries                 # List Plex libraries
"""

import asyncio
import glob
import json
import os
import subprocess
import sys
import time

import pyatv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG_PATH = os.path.expanduser("~/.clawtv/config.json")
SCREENSHOT_DIR = os.path.expanduser("~/.clawtv/screenshots")


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


# ---------------------------------------------------------------------------
# Discovery & Pairing
# ---------------------------------------------------------------------------

async def discover():
    """Scan the local network for Apple TVs."""
    print("Scanning for Apple TVs...")
    atvs = await pyatv.scan(asyncio.get_event_loop())
    if not atvs:
        print("No Apple TVs found on the network.")
        return []
    for i, atv in enumerate(atvs):
        print(f"  [{i}] {atv.name}  ({atv.address})  {atv.device_info.model_str}")
    return atvs


async def pair_device(atv_conf):
    """Pair with an Apple TV using the Companion protocol."""
    pairing = await pyatv.pair(atv_conf, pyatv.Protocol.Companion, asyncio.get_event_loop())
    await pairing.begin()
    pin = input("Enter the PIN shown on your Apple TV: ").strip()
    pairing.pin(int(pin))
    await pairing.finish()
    if pairing.has_paired:
        print(f"Paired successfully with {atv_conf.name}!")
        return pairing.service.credentials
    else:
        print("Pairing failed.")
        return None


async def cmd_pair():
    """Interactive discovery and pairing flow."""
    atvs = await discover()
    if not atvs:
        return

    if len(atvs) == 1:
        idx = 0
    else:
        idx = int(input("Select a device [number]: "))

    atv = atvs[idx]
    credentials = await pair_device(atv)
    if credentials:
        cfg = load_config()
        cfg["device"] = {
            "name": atv.name,
            "identifier": atv.all_identifiers[0],
            "address": str(atv.address),
            "credentials": credentials,
        }
        save_config(cfg)
        print(f"Saved to {CONFIG_PATH}")


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

async def connect():
    """Connect to the configured Apple TV. Returns (atv, config)."""
    cfg = load_config()
    device = cfg.get("device")
    if not device:
        print("No device configured. Run: clawtv pair")
        sys.exit(1)

    atvs = await pyatv.scan(asyncio.get_event_loop(), identifier=device["identifier"])
    if not atvs:
        print(f"Apple TV '{device['name']}' not found on the network.")
        sys.exit(1)

    atv_conf = atvs[0]
    atv_conf.set_credentials(pyatv.Protocol.Companion, device["credentials"])
    atv = await pyatv.connect(atv_conf, asyncio.get_event_loop())
    return atv


# ---------------------------------------------------------------------------
# Remote Control
# ---------------------------------------------------------------------------

REMOTE_COMMANDS = [
    "up", "down", "left", "right", "select", "menu", "home",
    "play", "pause", "play_pause", "next", "previous",
    "volume_up", "volume_down", "top_menu",
]


async def cmd_remote(commands):
    """Send one or more remote control commands."""
    atv = await connect()
    try:
        rc = atv.remote_control
        for cmd in commands:
            if cmd.startswith("sleep:"):
                await asyncio.sleep(float(cmd.split(":")[1]))
                continue
            action = getattr(rc, cmd, None)
            if action:
                await action()
                print(f"  -> {cmd}")
            else:
                print(f"  !! Unknown command: {cmd}")
            await asyncio.sleep(0.3)
    finally:
        atv.close()


async def cmd_type(text):
    """Type text using the Apple TV keyboard API."""
    atv = await connect()
    try:
        await atv.keyboard.text_set(text)
        print(f"  -> typed: {text}")
    finally:
        atv.close()


async def cmd_launch(app_id):
    """Launch an app by bundle ID."""
    atv = await connect()
    try:
        await atv.apps.launch_app(app_id)
        print(f"  -> launched: {app_id}")
    finally:
        atv.close()


async def cmd_app_list():
    """List installed apps."""
    atv = await connect()
    try:
        apps = await atv.apps.app_list()
        for app in sorted(apps, key=lambda a: a.name):
            print(f"  {app.name:40s}  {app.identifier}")
    finally:
        atv.close()


async def cmd_playing():
    """Show what's currently playing."""
    atv = await connect()
    try:
        playing = await atv.metadata.playing()
        print(f"  State:  {playing.device_state}")
        print(f"  Title:  {playing.title}")
        print(f"  Type:   {playing.media_type}")
        if playing.position:
            print(f"  Pos:    {playing.position}s / {playing.total_time}s")
    finally:
        atv.close()


# ---------------------------------------------------------------------------
# Plex Direct Control
# ---------------------------------------------------------------------------

def _plex_connect():
    """Connect to the Plex server using config credentials."""
    try:
        from plexapi.server import PlexServer
    except ImportError:
        print("Install plexapi: pip install plexapi")
        sys.exit(1)

    cfg = load_config()
    url = cfg.get("plex_url")
    token = cfg.get("plex_token")
    if not url or not token:
        print("Configure Plex in ~/.clawtv/config.json:")
        print('  "plex_url": "http://192.168.86.X:32400"')
        print('  "plex_token": "your-token"')
        sys.exit(1)

    return PlexServer(url, token)


def _plex_get_client(plex):
    """Get the configured Plex client. Tries local GDM first, then cloud resources."""
    cfg = load_config()
    client_name = cfg.get("plex_client", "Apple TV")
    # Try local GDM discovery first
    try:
        return plex.client(client_name)
    except Exception:
        pass

    # Fallback: find via MyPlex account resources (cloud discovery)
    try:
        account = plex.myPlexAccount()
        for res in account.resources():
            if "player" in res.provides and res.name == client_name:
                print(f"  Found '{client_name}' via cloud discovery")
                return res.connect()
    except Exception:
        pass

    # Last resort: list what's available
    clients = plex.clients()
    if clients:
        names = [c.title for c in clients]
        print(f"Client '{client_name}' not found. Available: {', '.join(names)}")
    else:
        # Check cloud too
        try:
            account = plex.myPlexAccount()
            players = [r for r in account.resources() if "player" in r.provides]
            if players:
                names = [r.name for r in players]
                print(f"Client '{client_name}' not found. Available (cloud): {', '.join(names)}")
            else:
                print(f"No Plex clients found. Is the Plex app open on '{client_name}'?")
        except Exception:
            print(f"No Plex clients found. Is the Plex app open on '{client_name}'?")
    sys.exit(1)


def cmd_plex_play(query, season=None, episode=None, media_type=None):
    """Play content directly via Plex API — zero screenshots needed."""
    plex = _plex_connect()
    client = _plex_get_client(plex)

    # Search across all libraries
    results = plex.search(query)
    if not results:
        print(f"No results found for: {query}")
        return False

    # Filter by type if specified
    if media_type == "movie":
        results = [r for r in results if r.type == "movie"] or results
    elif media_type in ("show", "episode"):
        results = [r for r in results if r.type == "show"] or results

    item = results[0]
    print(f"  Found: {item.title} ({item.type})")

    # Navigate to specific episode if requested
    if season is not None and hasattr(item, 'season'):
        try:
            ep = item.season(int(season)).episode(int(episode or 1))
            print(f"  -> S{season:02d}E{(episode or 1):02d}: {ep.title}")
            item = ep
        except Exception as e:
            print(f"  Could not find S{season}E{episode}: {e}")
            return False

    # Play it
    try:
        client.playMedia(item)
        print(f"  -> Playing on {client.title}")
        return True
    except Exception as e:
        print(f"  Playback failed: {e}")
        return False


def cmd_plex_search(query):
    """Search Plex library and display results."""
    plex = _plex_connect()
    results = plex.search(query)
    if not results:
        print(f"No results for: {query}")
        return []

    for r in results[:15]:
        extra = ""
        if r.type == "movie" and hasattr(r, 'year') and r.year:
            extra = f" ({r.year})"
        elif r.type == "show" and hasattr(r, 'childCount'):
            extra = f" ({r.childCount} seasons)"
        elif r.type == "episode":
            extra = f" — S{r.parentIndex}E{r.index}"
        print(f"  [{r.type:8s}] {r.title}{extra}")
    return results


def cmd_plex_clients():
    """List available Plex clients."""
    plex = _plex_connect()
    clients = plex.clients()
    if not clients:
        print("No active Plex clients found.")
        return
    for c in clients:
        print(f"  {c.title:30s}  {c.product}  ({c.platform})")


def cmd_plex_libraries():
    """List Plex libraries."""
    plex = _plex_connect()
    for section in plex.library.sections():
        print(f"  {section.title:30s}  [{section.type}]  {section.totalSize} items")


# ---------------------------------------------------------------------------
# Screenshot
# ---------------------------------------------------------------------------

def _get_quicktime_window_id():
    """
    Find the CGWindowID of a QuickTime Player window that's mirroring Apple TV.
    Uses CGWindowListCopyWindowInfo via Python's objc bridge.
    Returns the window ID (int) or None.
    """
    try:
        import Quartz
    except ImportError:
        print("QuickTime method requires pyobjc-framework-Quartz: pip install pyobjc-framework-Quartz")
        return None

    window_list = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
        Quartz.kCGNullWindowID,
    )
    for win in window_list:
        owner = win.get("kCGWindowOwnerName", "")
        name = win.get("kCGWindowName", "")
        if owner == "QuickTime Player" and name:
            return win.get("kCGWindowNumber")
    return None


def _ensure_quicktime_mirroring():
    """
    Start QuickTime mirroring of the Apple TV if not already running.
    Opens QuickTime → New Movie Recording → selects Apple TV as video source.
    Returns True if mirroring is active.
    """
    wid = _get_quicktime_window_id()
    if wid is not None:
        return True

    cfg = load_config()
    device = cfg.get("device", {})
    atv_name = device.get("name", "Apple TV")

    script = f'''
    tell application "QuickTime Player"
        activate
        delay 0.5
        set newDoc to new movie recording
        delay 1.5
    end tell

    -- Select Apple TV as camera source via accessibility
    tell application "System Events"
        tell process "QuickTime Player"
            set recordingWin to window "Movie Recording"
            -- Find the dropdown button by its description
            set allBtns to every button of recordingWin
            repeat with btn in allBtns
                if description of btn is "show capture device selection menu" then
                    click btn
                    delay 0.8
                    -- Look for the Apple TV in the popup menu
                    set menuItems to every menu item of menu 1 of btn
                    repeat with mi in menuItems
                        if name of mi contains "{atv_name}" then
                            click mi
                            delay 6
                            return true
                        end if
                    end repeat
                end if
            end repeat
        end tell
    end tell
    return false
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"QuickTime setup failed: {result.stderr}")
        return False

    # Wait for the mirroring window to appear
    for _ in range(10):
        time.sleep(0.5)
        if _get_quicktime_window_id() is not None:
            return True

    print("QuickTime mirroring window did not appear.")
    return False


async def disconnect_quicktime():
    """
    Disconnect QuickTime mirroring and resume playback on the Apple TV.

    When QuickTime mirrors the Apple TV:
    - A red recording border appears on the TV screen
    - Audio is routed to the Mac instead of the TV

    Closing the recording document releases the AirPlay session. Playback pauses
    when the session drops, so we send play twice to resume it on the TV.
    """
    script = '''
        tell application "QuickTime Player"
            if (count of documents) > 0 then
                close every document saving no
            end if
        end tell
    '''
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print("  -> QuickTime mirror released, resuming playback...")
        # Playback pauses when AirPlay drops — double-play resumes it
        await asyncio.sleep(2)
        await cmd_remote(["play"])
        await asyncio.sleep(1)
        await cmd_remote(["play"])
        print("  -> Playback resumed on TV (audio + video restored)")
    else:
        print(f"  -> QuickTime disconnect failed: {result.stderr}")


def take_screenshot_quicktime():
    """
    Take a screenshot via QuickTime wireless mirroring + screencapture.

    How it works:
    1. QuickTime Player mirrors the Apple TV screen wirelessly
    2. screencapture -l <CGWindowID> captures that specific window instantly
    3. Works even if the window is behind other windows

    Requires:
        - QuickTime Player (comes with macOS)
        - Apple TV on the same WiFi network
        - pyobjc-framework-Quartz (pip install pyobjc-framework-Quartz)
    """
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Ensure QuickTime is mirroring
    if not _ensure_quicktime_mirroring():
        print("Could not set up QuickTime mirroring.")
        return None

    # Get the window ID
    wid = _get_quicktime_window_id()
    if wid is None:
        print("QuickTime window not found.")
        return None

    # Capture the specific window
    ts = time.strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(SCREENSHOT_DIR, f"atv_{ts}.png")
    result = subprocess.run(
        ["screencapture", "-l", str(wid), "-x", dst],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"screencapture failed: {result.stderr}")
        return None

    if not os.path.exists(dst):
        print("Screenshot file was not created.")
        return None

    # Validate: a real Apple TV mirror is at least 1280px wide.
    # If the QuickTime window is idle/disconnected (DRM killed the mirror),
    # the capture will be the small Movie Recording UI (~900px).
    try:
        result = subprocess.run(
            ["sips", "-g", "pixelWidth", dst],
            capture_output=True, text=True,
        )
        for line in result.stdout.splitlines():
            if "pixelWidth" in line:
                width = int(line.split(":")[-1].strip())
                if width < 1280:
                    print(f"QuickTime mirror disconnected (captured {width}px window, not Apple TV).")
                    print("A DRM-protected app (YouTube, Netflix, etc.) may have killed the mirror.")
                    os.remove(dst)
                    return None
    except Exception:
        pass  # sips check is best-effort

    return dst


def take_screenshot_xcode():
    """
    Take a screenshot of the paired Apple TV using Xcode's Devices window.

    Requires:
        - Xcode open with Devices and Simulators window (Cmd+Shift+2)
        - Apple TV paired as a developer device
    """
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Record existing screenshots to detect the new one
    before = set(glob.glob(os.path.expanduser("~/Desktop/Screenshot*.png")))

    # Click the "Take Screenshot" button via AppleScript
    # First ensure Devices window is open and not minimized
    script = '''
    tell application "Xcode" to activate
    delay 0.3
    tell application "System Events"
        tell process "Xcode"
            -- Reopen Devices window if minimized or closed
            if not (exists window "Devices") then
                keystroke "2" using {command down, shift down}
                delay 1
            else if (value of attribute "AXMinimized" of window "Devices") is true then
                set value of attribute "AXMinimized" of window "Devices" to false
                delay 0.5
            end if
            click button "Take Screenshot" of scroll area 1 of splitter group 1 of splitter group 1 of window "Devices"
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Screenshot failed: {result.stderr}")
        print("Make sure Xcode Devices window is open (Cmd+Shift+2) with the Apple TV selected.")
        return None

    # Wait for the new file to appear
    for _ in range(20):
        time.sleep(0.25)
        after = set(glob.glob(os.path.expanduser("~/Desktop/Screenshot*.png")))
        new_files = after - before
        if new_files:
            src = new_files.pop()
            # Move to our screenshot dir with a clean name
            ts = time.strftime("%Y%m%d_%H%M%S")
            dst = os.path.join(SCREENSHOT_DIR, f"atv_{ts}.png")
            os.rename(src, dst)
            return dst

    print("Timed out waiting for screenshot file.")
    return None


def take_screenshot_lookout():
    """
    Take a screenshot from a Lookout tvOS app running on the Apple TV.
    Uses the HTTP API: GET /screenshot on the Apple TV's IP.
    """
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    cfg = load_config()
    device = cfg.get("device", {})
    address = device.get("address")
    if not address:
        print("No device configured. Run: clawtv pair")
        return None

    lookout_port = cfg.get("lookout_port", 8080)
    url = f"http://{address}:{lookout_port}/screenshot"

    try:
        import urllib.request
        ts = time.strftime("%Y%m%d_%H%M%S")
        dst = os.path.join(SCREENSHOT_DIR, f"atv_{ts}.png")
        urllib.request.urlretrieve(url, dst)
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            return dst
        print("Lookout returned empty screenshot.")
        return None
    except Exception as e:
        print(f"Lookout screenshot failed: {e}")
        return None


def take_screenshot(method=None):
    """
    Take a screenshot using the configured method.

    Methods:
        - quicktime: QuickTime wireless mirroring + screencapture (fastest, no Xcode)
        - lookout: HTTP fetch from Lookout tvOS app (no Mac needed after setup)
        - xcode: Xcode Devices window GUI automation (legacy fallback)
        - auto: try quicktime → lookout → xcode
    """
    if method is None:
        cfg = load_config()
        method = cfg.get("screenshot_method", "auto")

    if method == "quicktime":
        return take_screenshot_quicktime()
    elif method == "lookout":
        return take_screenshot_lookout()
    elif method == "xcode":
        return take_screenshot_xcode()
    elif method == "auto":
        # Try QuickTime first (fastest), then Lookout, then Xcode
        result = take_screenshot_quicktime()
        if result:
            return result
        result = take_screenshot_lookout()
        if result:
            return result
        return take_screenshot_xcode()
    else:
        print(f"Unknown screenshot method: {method}")
        return None


def cmd_screenshot(method=None):
    """Take a screenshot and print the path."""
    path = take_screenshot(method=method)
    if path:
        print(f"  -> saved: {path}")
    return path


# ---------------------------------------------------------------------------
# AI Agent Mode
# ---------------------------------------------------------------------------

def _compress_screenshot(path):
    """Always convert to JPEG at 800px wide, quality 50. Returns (bytes, media_type)."""
    jpeg_path = path.rsplit(".", 1)[0] + "_opt.jpg"
    subprocess.run(
        ["sips", "--resampleWidth", "800", "--setProperty", "format", "jpeg",
         "--setProperty", "formatOptions", "50", path, "--out", jpeg_path],
        capture_output=True,
    )
    if os.path.exists(jpeg_path):
        img_data = open(jpeg_path, "rb").read()
        os.remove(jpeg_path)
        return img_data, "image/jpeg"
    # Fallback: read original
    return open(path, "rb").read(), "image/png"


def _apply_sliding_window(messages, max_images=2):
    """Keep only the last N screenshots in messages; replace older ones with text summaries."""
    image_indices = []
    for i, msg in enumerate(messages):
        if isinstance(msg.get("content"), list):
            for block in msg["content"]:
                if block.get("type") == "image":
                    image_indices.append(i)
                    break

    # Remove images from older messages, keep text
    to_strip = image_indices[:-max_images] if len(image_indices) > max_images else []
    for i in to_strip:
        msg = messages[i]
        text_parts = [b.get("text", "") for b in msg["content"] if b.get("type") == "text"]
        messages[i] = {"role": "user", "content": " ".join(text_parts) + " [screenshot removed to save tokens]"}


async def cmd_do(goal):
    """
    AI agent mode: describe what you want and ClawTV figures it out.

    Uses Claude vision to analyze screenshots and decide which remote
    commands to send, repeating until the goal is accomplished.

    Optimizations:
    - Plex goals use direct API (zero vision calls)
    - Sliding window: only last 2 screenshots kept in context
    - All screenshots compressed to JPEG 800px q50
    - System prompt cached via cache_control
    - Haiku 4.5 for routine steps, Sonnet 4.5 when stuck
    - Skips redundant screenshots after sleep commands
    """
    # --- Plex smart routing: skip the entire vision loop ---
    goal_lower = goal.lower()
    plex_keywords = ["plex", "on plex", "in plex"]
    cfg = load_config()
    has_plex = cfg.get("plex_url") and cfg.get("plex_token")

    if has_plex and any(kw in goal_lower for kw in plex_keywords):
        print("  Plex goal detected — using direct API (no vision needed)")
        try:
            import anthropic
        except ImportError:
            print("Install the anthropic SDK: pip install anthropic")
            sys.exit(1)

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("Set ANTHROPIC_API_KEY environment variable.")
            sys.exit(1)

        client = anthropic.Anthropic(api_key=api_key)
        # One API call to parse the goal into structured Plex params
        parse_response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            system="Extract Plex playback info from the user's request. Return JSON only.\n"
                   "Format: {\"query\": \"title\", \"type\": \"movie\"|\"episode\", \"season\": N|null, \"episode\": N|null}\n"
                   "Examples:\n"
                   "- \"play Fight Club on Plex\" -> {\"query\": \"Fight Club\", \"type\": \"movie\", \"season\": null, \"episode\": null}\n"
                   "- \"play Westworld S2E6\" -> {\"query\": \"Westworld\", \"type\": \"episode\", \"season\": 2, \"episode\": 6}\n"
                   "- \"play the office season 3 episode 10\" -> {\"query\": \"The Office\", \"type\": \"episode\", \"season\": 3, \"episode\": 10}",
            messages=[{"role": "user", "content": goal}],
        )
        try:
            import re
            raw = parse_response.content[0].text.strip()
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            parsed = json.loads(match.group() if match else raw)
            print(f"  Parsed: {parsed}")
            success = cmd_plex_play(
                parsed["query"],
                season=parsed.get("season"),
                episode=parsed.get("episode"),
                media_type=parsed.get("type"),
            )
            if success:
                print("\n  Done: Playing via Plex direct API (2 API calls total)")
            else:
                print("\n  Plex direct play failed — falling back to vision loop")
                # Fall through to vision loop below
                has_plex = False
        except Exception as e:
            print(f"  Parse failed ({e}) — falling back to vision loop")
            has_plex = False

        if has_plex:
            return

    # --- Vision loop (for non-Plex apps or Plex fallback) ---
    try:
        import anthropic
        import base64
        import re
    except ImportError:
        print("Install the anthropic SDK: pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY environment variable.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    SYSTEM = """You are ClawTV, an AI agent controlling an Apple TV via remote commands.
You can see the TV screen via screenshots and send commands to navigate.

Available actions (return as JSON):
- {"action": "remote", "commands": ["up"]}  — navigate (up/down/left/right/select/menu/home/play_pause)
- {"action": "type", "text": "search query"}  — type text when a search/text field is active
- {"action": "launch", "app": "com.plexapp.plex"}  — launch an app by bundle ID
- {"action": "plex_play", "query": "Fight Club", "type": "movie"}  — play via Plex API directly (instant, no navigation)
- {"action": "plex_play", "query": "Westworld", "type": "episode", "season": 2, "episode": 6}  — play specific episode
- {"action": "plex_search", "query": "matrix"}  — search Plex library (returns text results, no screenshot needed)
- {"action": "disconnect", "message": "reason"}  — disconnect QuickTime mirror (restores audio + removes red border on TV)
- {"action": "done", "message": "what was accomplished"}
- {"action": "fail", "message": "why it couldn't be completed"}

You can chain multiple remote commands: {"action": "remote", "commands": ["down", "down", "right", "select"]}
Use "sleep:N" between commands for timing: {"action": "remote", "commands": ["select", "sleep:1.5", "down"]}

IMPORTANT — Plex shortcuts:
- If the goal involves playing something on Plex, use "plex_play" immediately. It uses the Plex API to play
  content directly on the TV — no navigation, no screenshots, instant playback. Use this FIRST.
- Use "plex_search" to check what's available before playing.
- Only fall back to manual navigation if plex_play fails.

Navigation tips:
- GO SLOW. Send 1-2 commands at a time, then verify with the next screenshot.
- "menu" = back/cancel. "home" = Apple TV home screen. "select" = click/confirm.
- On screensavers, press "select" or "home" to wake up.
- Apple TV home screen: top row = "Continue Watching", middle = app dock, below = more apps.
- When on the Apple TV home screen, use "launch" to open apps directly instead of navigating.

Plex navigation (manual fallback only):
- Plex sidebar: Search > Home > Watchlist > Movies > TV Shows > Live TV > More > Settings
- From Plex home, go LEFT to enter sidebar, then UP/DOWN to pick a section, SELECT to enter.
- Search: navigate to Search in sidebar, select it, then navigate UP to the search input area.
  The keyboard API ("type" action) only works when the search text field is focused.
  You must be on the search screen AND have focus on the keyboard/input area.
- During playback, press DOWN to see chapter selection, playback settings, and technical details.
- "menu" during playback shows the movie details page. Another "menu" goes back to the previous screen.

General app patterns:
- Most streaming apps: search is in the top bar or sidebar
- Settings/options usually accessible via DOWN during playback
- Use "launch" with bundle IDs for fast app switching:
  Plex=com.plexapp.plex, YouTube=com.google.ios.youtube, Netflix (if installed),
  HBO=com.wbd.stream, Prime=com.amazon.aiv.AIVApp, Spotify=com.spotify.client

Handoff to human:
- When you start playing content for the user, use "disconnect" BEFORE "done".
  QuickTime mirroring causes a red border on the TV and steals audio to the Mac.
  Disconnecting releases the mirror and auto-resumes playback with audio on the TV.
- If you see a "Skip Intro" button on screen, click it (select) before disconnecting.
- Pattern: navigate → start playback → verify playing → skip intro if visible → disconnect → done

Rules:
- Analyze each screenshot carefully — identify what's highlighted/focused before acting
- Send minimal commands per step — it's better to take more steps than to overshoot
- After each action, you'll get a new screenshot to verify the result
- If something went wrong, use "menu" to back up and try again
- Always respond with a single JSON object, no markdown or explanation"""

    system_with_cache = [
        {"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}
    ]

    messages = [{"role": "user", "content": f"Goal: {goal}\n\nI'll show you the current screen."}]

    # Model routing: start with Haiku, escalate to Sonnet when stuck
    MODEL_HAIKU = "claude-haiku-4-5-20251001"
    MODEL_SONNET = "claude-sonnet-4-5-20250929"
    current_model = MODEL_HAIKU
    steps_without_progress = 0
    last_action_type = None

    MAX_STEPS = 20
    last_commands_had_sleep = False

    for step in range(MAX_STEPS):
        print(f"\n--- Step {step + 1} ({current_model.split('-')[1]}) ---")

        # Skip screenshot if last action was only a sleep command
        if last_commands_had_sleep and step > 0:
            print("  (reusing previous screenshot — last action was sleep)")
        else:
            # Take screenshot
            path = take_screenshot()
            if not path:
                print("Failed to take screenshot. Aborting.")
                return

            # Compress to JPEG 800px q50
            img_data, media_type = _compress_screenshot(path)
            img_b64 = base64.b64encode(img_data).decode()

            # Add screenshot to conversation
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Step {step + 1} screenshot:"},
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img_b64}},
                ]
            })

        # Apply sliding window — keep only last 2 screenshots
        _apply_sliding_window(messages, max_images=2)

        # Ask Claude what to do
        response = client.messages.create(
            model=current_model,
            max_tokens=500,
            system=system_with_cache,
            messages=messages,
        )

        reply = response.content[0].text.strip()
        print(f"  AI: {reply}")
        messages.append({"role": "assistant", "content": reply})

        # Parse action
        try:
            action = json.loads(reply)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', reply, re.DOTALL)
            if match:
                action = json.loads(match.group())
            else:
                print("  !! Couldn't parse AI response")
                steps_without_progress += 1
                continue

        # Track progress for model escalation
        action_type = action.get("action")
        if action_type == last_action_type and action_type == "remote":
            steps_without_progress += 1
        else:
            steps_without_progress = 0
        last_action_type = action_type

        # Escalate to Sonnet if stuck (3+ steps without clear progress)
        if steps_without_progress >= 3 and current_model == MODEL_HAIKU:
            print("  ** Escalating to Sonnet (stuck detected)")
            current_model = MODEL_SONNET
            steps_without_progress = 0

        # Check if last remote commands were only sleep
        last_commands_had_sleep = False
        if action_type == "remote":
            cmds = action.get("commands", [])
            last_commands_had_sleep = all(c.startswith("sleep:") for c in cmds)

        # Execute
        if action["action"] == "done":
            print(f"\n  Done: {action['message']}")
            return
        elif action["action"] == "fail":
            print(f"\n  Failed: {action['message']}")
            return
        elif action["action"] == "disconnect":
            await disconnect_quicktime()
        elif action["action"] == "remote":
            await cmd_remote(action["commands"])
        elif action["action"] == "type":
            await cmd_type(action["text"])
        elif action["action"] == "launch":
            await cmd_launch(action["app"])
        elif action["action"] == "plex_play":
            success = cmd_plex_play(
                action["query"],
                season=action.get("season"),
                episode=action.get("episode"),
                media_type=action.get("type"),
            )
            if success:
                # Add result as text (no screenshot needed)
                messages.append({"role": "user", "content": "Plex playback started successfully."})
            else:
                messages.append({"role": "user", "content": "Plex direct play failed. Try manual navigation."})
        elif action["action"] == "plex_search":
            results = cmd_plex_search(action["query"])
            summary = "\n".join(f"  [{r.type}] {r.title}" for r in results[:10]) if results else "No results."
            messages.append({"role": "user", "content": f"Plex search results:\n{summary}"})
        else:
            print(f"  !! Unknown action: {action['action']}")

        # Brief pause before next screenshot
        await asyncio.sleep(1)

    print("\n  Reached max steps without completing goal.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "pair":
        asyncio.run(cmd_pair())
    elif cmd == "scan":
        asyncio.run(discover())
    elif cmd == "screenshot":
        method = None
        if "--method" in sys.argv:
            idx = sys.argv.index("--method")
            if idx + 1 < len(sys.argv):
                method = sys.argv[idx + 1]
        cmd_screenshot(method=method)
    elif cmd == "cmd":
        if len(sys.argv) < 3:
            print(f"Available commands: {', '.join(REMOTE_COMMANDS)}")
            sys.exit(1)
        asyncio.run(cmd_remote(sys.argv[2:]))
    elif cmd == "type":
        if len(sys.argv) < 3:
            print("Usage: clawtv type <text>")
            sys.exit(1)
        asyncio.run(cmd_type(" ".join(sys.argv[2:])))
    elif cmd == "launch":
        if len(sys.argv) < 3:
            print("Usage: clawtv launch <bundle_id>")
            sys.exit(1)
        asyncio.run(cmd_launch(sys.argv[2]))
    elif cmd == "disconnect":
        asyncio.run(disconnect_quicktime())
    elif cmd == "apps":
        asyncio.run(cmd_app_list())
    elif cmd == "playing":
        asyncio.run(cmd_playing())
    elif cmd == "plex":
        if len(sys.argv) < 3:
            print("Usage: clawtv plex <play|search|clients|libraries> [args]")
            sys.exit(1)
        subcmd = sys.argv[2]
        if subcmd == "play":
            if len(sys.argv) < 4:
                print('Usage: clawtv plex play "Movie Name" [-s SEASON -e EPISODE]')
                sys.exit(1)
            query = sys.argv[3]
            season = episode = None
            args = sys.argv[4:]
            for i, a in enumerate(args):
                if a in ("-s", "--season") and i + 1 < len(args):
                    season = int(args[i + 1])
                elif a in ("-e", "--episode") and i + 1 < len(args):
                    episode = int(args[i + 1])
            cmd_plex_play(query, season=season, episode=episode)
        elif subcmd == "search":
            if len(sys.argv) < 4:
                print('Usage: clawtv plex search "query"')
                sys.exit(1)
            cmd_plex_search(sys.argv[3])
        elif subcmd == "clients":
            cmd_plex_clients()
        elif subcmd == "libraries":
            cmd_plex_libraries()
        else:
            print(f"Unknown plex command: {subcmd}")
            sys.exit(1)
    elif cmd == "do":
        if len(sys.argv) < 3:
            print('Usage: clawtv do "play Fury on Plex in 4K"')
            sys.exit(1)
        asyncio.run(cmd_do(" ".join(sys.argv[2:])))
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
