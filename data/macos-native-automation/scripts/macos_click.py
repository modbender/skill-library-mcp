#!/usr/bin/env python3
"""
macOS Native Click — Hardware-level mouse & keyboard automation via CoreGraphics.

When CDP .click(), AppleScript, and setFileInputFiles all fail, CGEvent works.
It simulates HID events that macOS and browsers can't distinguish from real input.

Usage:
    python3 macos_click.py click 500 300          # Left click at (500, 300)
    python3 macos_click.py doubleclick 500 300     # Double-click
    python3 macos_click.py rightclick 500 300      # Right-click
    python3 macos_click.py move 500 300            # Move mouse (no click)
    python3 macos_click.py drag 100 200 500 300    # Drag from (100,200) to (500,300)
    python3 macos_click.py window "Safari"         # Get window position & size
    python3 macos_click.py windows "Safari"        # List all windows for an app

Requirements: macOS, Python 3 (stdlib only — ctypes, subprocess, sys)
Permissions: Accessibility access for the calling process (System Settings → Privacy → Accessibility)
"""

import ctypes
import ctypes.util
import subprocess
import sys
import time

# --- CoreGraphics Setup ---

_cg = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreGraphics"))


class CGPoint(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]


_cg.CGEventCreateMouseEvent.restype = ctypes.c_void_p
_cg.CGEventCreateMouseEvent.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint32,
    CGPoint,
    ctypes.c_uint32,
]
_cg.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]

# Event types
_LEFT_DOWN = 1   # kCGEventLeftMouseDown
_LEFT_UP = 2     # kCGEventLeftMouseUp
_RIGHT_DOWN = 3  # kCGEventRightMouseDown
_RIGHT_UP = 4    # kCGEventRightMouseUp
_MOUSE_MOVED = 5 # kCGEventMouseMoved
_LEFT_DRAG = 6   # kCGEventLeftMouseDragged
_HID_TAP = 0     # kCGHIDEventTap


def click(x: float, y: float, pause: float = 0.05) -> None:
    """Left-click at absolute screen coordinates."""
    point = CGPoint(x, y)
    down = _cg.CGEventCreateMouseEvent(None, _LEFT_DOWN, point, 0)
    _cg.CGEventPost(_HID_TAP, down)
    time.sleep(pause)
    up = _cg.CGEventCreateMouseEvent(None, _LEFT_UP, point, 0)
    _cg.CGEventPost(_HID_TAP, up)


def doubleclick(x: float, y: float) -> None:
    """Double-click at absolute screen coordinates."""
    point = CGPoint(x, y)
    for _ in range(2):
        down = _cg.CGEventCreateMouseEvent(None, _LEFT_DOWN, point, 0)
        _cg.CGEventPost(_HID_TAP, down)
        time.sleep(0.02)
        up = _cg.CGEventCreateMouseEvent(None, _LEFT_UP, point, 0)
        _cg.CGEventPost(_HID_TAP, up)
        time.sleep(0.05)


def rightclick(x: float, y: float, pause: float = 0.05) -> None:
    """Right-click at absolute screen coordinates."""
    point = CGPoint(x, y)
    down = _cg.CGEventCreateMouseEvent(None, _RIGHT_DOWN, point, 0)
    _cg.CGEventPost(_HID_TAP, down)
    time.sleep(pause)
    up = _cg.CGEventCreateMouseEvent(None, _RIGHT_UP, point, 0)
    _cg.CGEventPost(_HID_TAP, up)


def move(x: float, y: float) -> None:
    """Move mouse to absolute screen coordinates without clicking."""
    point = CGPoint(x, y)
    event = _cg.CGEventCreateMouseEvent(None, _MOUSE_MOVED, point, 0)
    _cg.CGEventPost(_HID_TAP, event)


def drag(x1: float, y1: float, x2: float, y2: float, duration: float = 0.3) -> None:
    """Click-drag from (x1, y1) to (x2, y2)."""
    start = CGPoint(x1, y1)
    down = _cg.CGEventCreateMouseEvent(None, _LEFT_DOWN, start, 0)
    _cg.CGEventPost(_HID_TAP, down)

    steps = max(int(duration / 0.016), 5)
    for i in range(1, steps + 1):
        t = i / steps
        cx = x1 + (x2 - x1) * t
        cy = y1 + (y2 - y1) * t
        pt = CGPoint(cx, cy)
        mv = _cg.CGEventCreateMouseEvent(None, _LEFT_DRAG, pt, 0)
        _cg.CGEventPost(_HID_TAP, mv)
        time.sleep(0.016)

    end = CGPoint(x2, y2)
    up = _cg.CGEventCreateMouseEvent(None, _LEFT_UP, end, 0)
    _cg.CGEventPost(_HID_TAP, up)


def _sanitize_app_name(name: str) -> str:
    """Sanitize app name to prevent AppleScript injection."""
    # Allow letters, numbers, spaces, hyphens, periods (covers all normal app names)
    clean = "".join(c for c in name if c.isalnum() or c in " -.")
    if not clean or clean != name:
        raise ValueError(f"Invalid app name: {name!r}")
    return clean


def get_window(app_name: str) -> dict:
    """Get front window position and size for an app. Returns {x, y, w, h}."""
    app_name = _sanitize_app_name(app_name)
    script = f'''
    tell application "System Events"
        tell process "{app_name}"
            set p to position of front window
            set s to size of front window
            return (item 1 of p as text) & "," & (item 2 of p as text) & "," & (item 1 of s as text) & "," & (item 2 of s as text)
        end tell
    end tell
    '''
    result = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript error: {result.stderr.strip()}")
    parts = result.stdout.strip().split(",")
    return {"x": int(parts[0]), "y": int(parts[1]), "w": int(parts[2]), "h": int(parts[3])}


def get_all_windows(app_name: str) -> list:
    """Get all windows for an app. Returns list of {x, y, w, h, title}."""
    app_name = _sanitize_app_name(app_name)
    script = f'''
    tell application "System Events"
        tell process "{app_name}"
            set output to ""
            repeat with w in every window
                set p to position of w
                set s to size of w
                set t to name of w
                set output to output & (item 1 of p) & "," & (item 2 of p) & "," & (item 1 of s) & "," & (item 2 of s) & "," & t & linefeed
            end repeat
            return output
        end tell
    end tell
    '''
    result = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript error: {result.stderr.strip()}")
    windows = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split(",", 4)
        windows.append({
            "x": int(parts[0]), "y": int(parts[1]),
            "w": int(parts[2]), "h": int(parts[3]),
            "title": parts[4] if len(parts) > 4 else ""
        })
    return windows


# --- CLI ---

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "click" and len(sys.argv) >= 4:
        x, y = float(sys.argv[2]), float(sys.argv[3])
        click(x, y)
        print(f"Clicked ({x}, {y})")

    elif cmd == "doubleclick" and len(sys.argv) >= 4:
        x, y = float(sys.argv[2]), float(sys.argv[3])
        doubleclick(x, y)
        print(f"Double-clicked ({x}, {y})")

    elif cmd == "rightclick" and len(sys.argv) >= 4:
        x, y = float(sys.argv[2]), float(sys.argv[3])
        rightclick(x, y)
        print(f"Right-clicked ({x}, {y})")

    elif cmd == "move" and len(sys.argv) >= 4:
        x, y = float(sys.argv[2]), float(sys.argv[3])
        move(x, y)
        print(f"Moved to ({x}, {y})")

    elif cmd == "drag" and len(sys.argv) >= 6:
        x1, y1 = float(sys.argv[2]), float(sys.argv[3])
        x2, y2 = float(sys.argv[4]), float(sys.argv[5])
        drag(x1, y1, x2, y2)
        print(f"Dragged ({x1}, {y1}) → ({x2}, {y2})")

    elif cmd == "window" and len(sys.argv) >= 3:
        app = sys.argv[2]
        w = get_window(app)
        print(f"{app}: x={w['x']}, y={w['y']}, w={w['w']}, h={w['h']}")

    elif cmd == "windows" and len(sys.argv) >= 3:
        app = sys.argv[2]
        for i, w in enumerate(get_all_windows(app)):
            print(f"  [{i}] x={w['x']}, y={w['y']}, w={w['w']}, h={w['h']}  \"{w['title']}\"")

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
