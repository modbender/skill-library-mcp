# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
play_show_via_global_search.py

Helper module for Google TV global search fallback. Orchestrates UI automation
for launching shows via Google TV's global search feature.

This module is called only by google_tv_skill.py. It assumes:
- The device is already connected via ADB (by caller)
- adb is available on PATH (verified by caller)
- The device address is passed as --device argument

All ADB connection management is handled by google_tv_skill.py.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

# Force unbuffered stdout so prints appear immediately when piped
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)

# Constants
ADB_TIMEOUT_SECONDS = 10
ADB_DUMP_RETRIES = 3
ADB_DUMP_RETRY_SLEEP = 1.0
KEYCODE_DOWN = "20"
KEYCODE_LEFT = "21"
KEYCODE_RIGHT = "22"
KEYCODE_ENTER = "66"
BATCH_KEYPRESS_SIZE = 10
KEYPRESS_INTERVAL = 0.1
VIEW_TRANSITION_WAIT = 3
PANE_SELECT_WAIT = 1.0
FOCUS_WAIT = 0.5
POPUP_WAIT = 2.0
SERIES_OVERVIEW_TIMEOUT = 60

def find_binary(name):
    """Find scrcpy binary in common locations."""
    result = shutil.which(name)
    if result:
        return result
    candidates = [
        f"/opt/homebrew/bin/{name}",
        f"/usr/local/bin/{name}",
        os.path.expanduser(f"~/Library/Android/sdk/platform-tools/{name}")
    ]
    for path in candidates:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    return None

SCRCPY_PATH = find_binary("scrcpy")

def run_adb(args, device=None, timeout=ADB_TIMEOUT_SECONDS):
    """Execute adb command. Returns output string; returns error string on failure instead of exiting."""
    cmd = ['adb']
    if device:
        cmd += ['-s', device]
    cmd += list(args)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = ((p.stdout or '') + (p.stderr or '')).strip()
        if p.returncode != 0:
            return f"[ADB ERR rc={p.returncode}] {out}"
        return out
    except subprocess.TimeoutExpired:
        return "[ADB TIMEOUT]"
    except Exception as e:
        return f"[ADB EXC] {str(e)}"

def launch_scrcpy(device):
    if not SCRCPY_PATH:
        return None
    return subprocess.Popen(
        [SCRCPY_PATH, "-s", device, "--max-size", "1024", "--always-on-top"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

def dump_screen(device):
    local_path = "/tmp/os_dump.xml"
    if os.path.exists(local_path):
        os.remove(local_path)
    for attempt in range(1, ADB_DUMP_RETRIES + 1):
        # Kill any stale uiautomator processes that may block new dumps
        run_adb(["shell", "killall", "uiautomator"], device, timeout=3)
        print(f"  [DEBUG] uiautomator dump attempt {attempt}/{ADB_DUMP_RETRIES}...")
        # Use device-side timeout to prevent uiautomator from hanging
        out1 = run_adb(["shell", "timeout", "5", "uiautomator", "dump", "/sdcard/window_dump.xml"], device, timeout=8)
        print(f"  [DEBUG] dump result: {out1}")
        if "[ADB TIMEOUT]" in out1 or "[ADB ERR" in out1:
            print(f"  [DEBUG] dump failed, retrying...")
            time.sleep(ADB_DUMP_RETRY_SLEEP)
            continue
        out2 = run_adb(["pull", "/sdcard/window_dump.xml", local_path], device)
        if os.path.exists(local_path):
            return local_path
        time.sleep(ADB_DUMP_RETRY_SLEEP)
    print(f"  [!] Failed to dump screen after {ADB_DUMP_RETRIES} attempts.")
    return None

def parse_screen_nodes(device):
    """Parse UI hierarchy and yield node information."""
    xml_path = dump_screen(device)
    if not xml_path:
        return

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for node in root.iter():
            text = (node.get("text") or "").strip()
            desc = (node.get("content-desc") or "").strip()
            content = text or desc
            yield {
                "text": text,
                "content": content,
                "bounds": node.get("bounds") or "",
            }
    except ET.ParseError:
        pass

def find_text_coords(device, text_target, strict=False):
    nodes = parse_screen_nodes(device)
    if not nodes:
        return None
    for node in nodes:
        content = node["content"]
        if strict:
            matched = content.lower() == text_target.lower()
        else:
            matched = text_target.lower() in content.lower()
        if not matched:
            continue
        coords = re.findall(r"\d+", node["bounds"])
        if len(coords) != 4:
            continue
        x1, y1, x2, y2 = map(int, coords)
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    return None

def click_text(device, text_target, strict=False):
    """Find text coordinate and tap it."""
    print(f"[*] Looking for: '{text_target}'...")
    found_coords = find_text_coords(device, text_target, strict=strict)
    if found_coords:
        print(f"  [+] Found at {found_coords}. Clicking...")
        run_adb(["shell", "input", "tap", str(found_coords[0]), str(found_coords[1])], device)
        return True
    return False

def wait_for_any_text(device, targets, timeout=45):
    print(f"[*] Waiting for series overview: {', '.join(targets)}")
    start = time.time()
    while time.time() - start < timeout:
        nodes = parse_screen_nodes(device)
        if nodes:
            for node in nodes:
                content = (node["content"] or "").lower()
                for target in targets:
                    if target.lower() in content:
                        print(f"  [+] Detected '{target}' on screen.")
                        return True
        time.sleep(1.0)
    return False

def navigate_pane(device, target_val, pane_name="Season"):
    """Navigate to target item in a pane using DOWN arrow keys."""
    steps = max(0, target_val - 1)
    print(f"  [#] {pane_name} {target_val}: Pressing DOWN {steps} times...")

    if steps > 0:
        current = 0
        while current < steps:
            batch = min(BATCH_KEYPRESS_SIZE, steps - current)
            keys = [KEYCODE_DOWN] * batch
            run_adb(["shell", "input", "keyevent", *keys], device)
            current += batch
            time.sleep(KEYPRESS_INTERVAL)

    time.sleep(FOCUS_WAIT)

    print(f"  [X] Selecting {pane_name} {target_val}...")
    run_adb(["shell", "input", "keyevent", KEYCODE_ENTER], device)
    time.sleep(PANE_SELECT_WAIT) 

def parse_args(argv):
    """Parse command-line arguments. Device must be pre-connected by caller."""
    parser = argparse.ArgumentParser(
        prog="play_show_via_global_search.py",
        description="Launch a TV show from Google TV global search and pick season/episode.",
    )
    parser.add_argument("show", help="Show title to search (example: Family Guy)")
    parser.add_argument("season", type=int, help="Season number (1-based)")
    parser.add_argument("episode", type=int, help="Episode number (1-based)")
    parser.add_argument("--device", dest="device", required=True, help="Device address (IP:PORT, must be already connected by caller)")
    parser.add_argument(
        "--app",
        dest="app_name",
        help="Streaming app name for final confirmation (example: Hulu, Max)",
    )
    return parser.parse_args(argv)

def main():
    args = parse_args(sys.argv[1:])
    if args.season < 1 or args.episode < 1:
        print("[!] Season and episode must be 1 or higher.")
        sys.exit(1)

    device = args.device

    # Capture the process so we can close it later
    scrcpy_proc = launch_scrcpy(device)

    try:
        # 1. Global Search — open text search UI, type query, select result
        print("[Step 1] Global Search...")
        # KEYCODE_SEARCH opens Google TV's text-based search (not voice assistant)
        run_adb(["shell", "input", "keyevent", "KEYCODE_SEARCH"], device)
        time.sleep(2)
        # Type the show name into the search field (%s = space in ADB input text)
        safe_text = args.show.replace(" ", "%s")
        run_adb(["shell", "input", "text", safe_text], device)
        time.sleep(1)
        # Press Enter to submit the search
        run_adb(["shell", "input", "keyevent", KEYCODE_ENTER], device)
        # Give the search results time to load
        time.sleep(VIEW_TRANSITION_WAIT)

        print(f">>> SELECT '{args.show}' IN SCRCPY IF NEEDED. "
              "Waiting for Series Overview... <<<")
        if not wait_for_any_text(
            device,
            ["Seasons", "Episodes", "Series overview"],
            timeout=SERIES_OVERVIEW_TIMEOUT
        ):
            print("  [!] Timed out waiting for Series Overview page.")
            sys.exit(1)

        # 2. Click Seasons Button
        print("[Step 2] Clicking 'Seasons'...")
        if not click_text(device, "Seasons"):
            print("  [!] Button not found via scan. Trying blind Enter...")
            run_adb(["shell", "input", "keyevent", KEYCODE_ENTER], device)

        # Wait for split view to load
        print("  [*] Waiting for view transition...")
        time.sleep(VIEW_TRANSITION_WAIT)

        # 3. Navigate Left Pane (Seasons)
        print("[Step 3] Entering Season List (Left Pane)...")

        # Focus navigation sequence
        run_adb(["shell", "input", "keyevent", KEYCODE_DOWN], device)
        time.sleep(0.2)
        run_adb(["shell", "input", "keyevent", KEYCODE_LEFT, KEYCODE_LEFT], device)
        time.sleep(FOCUS_WAIT)

        navigate_pane(device, args.season, pane_name="Season")

        # 4. Navigate Right Pane (Episodes)
        print("[Step 4] Navigating Episodes (Right Pane)...")

        run_adb(["shell", "input", "keyevent", KEYCODE_RIGHT], device)
        time.sleep(PANE_SELECT_WAIT)

        navigate_pane(device, args.episode, pane_name="Episode")

        # 5. Final Confirmation (Open in app)
        print("[Step 5] Confirming provider launch...")
        print("  [*] Waiting for popup...")
        time.sleep(POPUP_WAIT)

        if args.app_name:
            if click_text(device, f"Open in {args.app_name}", strict=False):
                print(f"  [SUCCESS] Clicked 'Open in {args.app_name}'.")
            else:
                print(f"  [!] 'Open in {args.app_name}' not found.")
                print("  [>] Pressing Enter to confirm provider...")
                run_adb(["shell", "input", "keyevent", KEYCODE_ENTER], device)
        else:
            print("  [>] Pressing Enter to confirm provider...")
            run_adb(["shell", "input", "keyevent", KEYCODE_ENTER], device)

        print("\n[DONE] Enjoy the show!")

    finally:
        # CLEANUP: Kill the scrcpy window
        if scrcpy_proc:
            print("[Cleanup] Closing scrcpy window...")
            scrcpy_proc.terminate()
            scrcpy_proc.wait()

if __name__ == "__main__":
    main()
