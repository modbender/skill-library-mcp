#!/usr/bin/env python3
"""
AI-powered Android phone control via DroidRun.

Usage:
    python run-task.py "Open Chrome and search for weather in Bangalore"
    python run-task.py --timeout 180 "Install Spotify from Play Store"
    python run-task.py --no-unlock "Take a screenshot"

This script handles EVERYTHING automatically:
1. Detects connected device (or uses ANDROID_SERIAL)
2. Wakes screen if asleep
3. Unlocks phone if locked (using ANDROID_PIN)
4. Sets keep-awake mode
5. Dismisses common dialogs/popups
6. Runs your task via DroidRun AI agent
7. Reports results
"""

import argparse
import asyncio
import os
import subprocess
import sys
import time

# ---------------------------------------------------------------------------
# ADB helpers
# ---------------------------------------------------------------------------

def adb(serial: str, *args: str, check: bool = True) -> str:
    """Run an ADB command and return stdout."""
    cmd = ["adb"]
    if serial:
        cmd += ["-s", serial]
    cmd += list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if check and result.returncode != 0:
        raise RuntimeError(f"adb {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def detect_serial(explicit: str | None) -> str:
    """Return the device serial to use."""
    if explicit:
        return explicit
    env = os.environ.get("ANDROID_SERIAL")
    if env:
        return env
    # Auto-detect from adb devices
    output = adb("", "devices", check=False)
    lines = [l for l in output.splitlines()[1:] if l.strip() and "device" in l and "offline" not in l]
    if not lines:
        print("❌ No Android device found. Connect via USB or set ANDROID_SERIAL.")
        sys.exit(1)
    if len(lines) > 1:
        print("⚠️  Multiple devices found. Set ANDROID_SERIAL or use --serial:")
        for l in lines:
            print(f"   {l.split()[0]}")
        sys.exit(1)
    serial = lines[0].split()[0]
    print(f"📱 Auto-detected device: {serial}")
    return serial


# ---------------------------------------------------------------------------
# Phone preparation
# ---------------------------------------------------------------------------

def wake_screen(serial: str) -> None:
    """Wake the screen if it's off."""
    display_state = adb(serial, "shell", "dumpsys", "power", check=False)
    if any(x in display_state for x in ["mWakefulness=Asleep", "mWakefulness=Dozing", "getWakefulnessLocked()=Asleep", "getWakefulnessLocked()=Dozing", "Display Power: state=OFF"]):
        print("💡 Waking screen...")
        adb(serial, "shell", "input", "keyevent", "KEYCODE_WAKEUP")
        time.sleep(1)


def is_locked(serial: str) -> bool:
    """Check if the phone is locked."""
    output = adb(serial, "shell", "dumpsys", "window", check=False)
    # Different Android versions use different fields
    if "mDreamingLockscreen=true" in output:
        return True
    if "isStatusBarKeyguard=true" in output:
        return True
    if "showing=true" in output and "mOccluded=false" in output:
        return True
    return False


def unlock_phone(serial: str) -> None:
    """Unlock the phone using ANDROID_PIN env var."""
    if not is_locked(serial):
        print("🔓 Phone already unlocked")
        return

    pin = os.environ.get("ANDROID_PIN")
    if not pin:
        print("🔒 Phone is locked but ANDROID_PIN not set — skipping unlock")
        print("   Set ANDROID_PIN environment variable or unlock manually")
        return

    print("🔑 Unlocking phone...")
    # Swipe up to reveal PIN pad
    adb(serial, "shell", "input", "swipe", "540", "1800", "540", "800", "300")
    time.sleep(1)

    # Type the PIN — works on most devices
    adb(serial, "shell", "input", "text", pin)
    time.sleep(0.5)

    # Press Enter to confirm
    adb(serial, "shell", "input", "keyevent", "KEYCODE_ENTER")
    time.sleep(1)

    if is_locked(serial):
        print("⚠️  PIN entry via input text didn't work.")
        print("   Your device may need tap-based PIN entry.")
        print("   Find your PIN pad coordinates with: adb shell getevent -l")
        print("   Then tap each digit manually or unlock the phone by hand.")
    else:
        print("🔓 Phone unlocked!")


def set_keep_awake(serial: str) -> None:
    """Keep the screen on while charging."""
    adb(serial, "shell", "svc", "power", "stayon", "true", check=False)
    adb(serial, "shell", "settings", "put", "system", "screen_off_timeout", "1800000", check=False)


def restore_screen_timeout(serial: str) -> None:
    """Restore default screen timeout (30 seconds)."""
    adb(serial, "shell", "settings", "put", "system", "screen_off_timeout", "30000", check=False)
    adb(serial, "shell", "svc", "power", "stayon", "false", check=False)


def dismiss_dialogs(serial: str) -> None:
    """Try to dismiss common system dialogs that confuse the AI agent."""
    # Press Back to dismiss any floating dialog
    adb(serial, "shell", "input", "keyevent", "KEYCODE_BACK", check=False)
    time.sleep(0.5)
    # Press Home then recent to clear any overlay, then back to last app
    # (lightweight — just a back press is usually enough)


def take_screenshot(serial: str, out_path: str = "/tmp/android-screenshot.png") -> str:
    """Take a screenshot using ADB screencap (bypasses DroidRun's screenshot tooling)."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # Use exec-out so bytes stream directly and avoid CRLF mangling.
    cmd = ["adb"]
    if serial:
        cmd += ["-s", serial]
    cmd += ["exec-out", "screencap", "-p"]
    with open(out_path, "wb") as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"screencap failed: {result.stderr.decode(errors='ignore').strip()}")
    size = os.path.getsize(out_path)
    if size < 1024:
        raise RuntimeError(f"screencap produced a tiny file ({size} bytes): {out_path}")
    print(f" Screenshot saved: {out_path} ({size} bytes)")
    return out_path


# ---------------------------------------------------------------------------
# DroidRun agent
# ---------------------------------------------------------------------------

async def run_droidrun(serial: str, goal: str, model: str, timeout: int, verbose: bool) -> str:
    """Run a DroidRun agent task."""
    try:
        from droidrun.tools import AdbTools
        from droidrun.agent.droid import DroidAgent
        from droidrun.agent.utils.llm_picker import load_llm
        from droidrun.config_manager.config_manager import DroidrunConfig, AgentConfig
    except ImportError:
        print("❌ DroidRun not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Export it first:")
        print('   export OPENAI_API_KEY="sk-..."')
        sys.exit(1)

    if verbose:
        print(f"🤖 Model: {model}")
        print(f"⏱️  Timeout: {timeout}s")
        print(f"🎯 Goal: {goal}")

    print("📡 Connecting to device...")
    tools = AdbTools(serial=serial)
    await tools.connect()

    print("🧠 Loading LLM...")
    llm = load_llm(provider_name="OpenAI", model=model, temperature=0.2)

    print(f"🚀 Running task: {goal}")
    print("   (this may take a minute — the AI is looking at the screen and deciding what to do)")
    print()

    config = DroidrunConfig(agent=AgentConfig(reasoning=True))

    agent = DroidAgent(
        goal=goal,
        llms=llm,
        tools=tools,
        config=config,
        timeout=timeout,
    )

    result = await agent.run()
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="AI-powered Android phone control via DroidRun",
        epilog="Examples:\n"
               '  python run-task.py "Open Settings and turn on Dark Mode"\n'
               '  python run-task.py --timeout 180 "Install Spotify from Play Store"\n'
               '  python run-task.py --no-unlock "Take a screenshot"',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("goal", nargs="?", help="Task for the AI to perform on the phone")
    parser.add_argument("--screenshot", action="store_true", help="Take a screenshot via ADB screencap and exit")
    parser.add_argument("--screenshot-path", default="/tmp/android-screenshot.png", help="Where to save screenshot (default: /tmp/android-screenshot.png)")
    parser.add_argument("--timeout", type=int, default=None,
                        help=f"Timeout in seconds (default: {os.environ.get('DROIDRUN_TIMEOUT', '120')})")
    parser.add_argument("--model", default="gpt-4o", help="LLM model (default: gpt-4o)")
    parser.add_argument("--no-unlock", action="store_true", help="Skip auto-unlock step")
    parser.add_argument("--serial", default=None, help="Device serial (default: auto-detect)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    # Validate args
    if not args.screenshot and not args.goal:
        parser.error("goal is required unless --screenshot is used")

    timeout = args.timeout or int(os.environ.get("DROIDRUN_TIMEOUT", "120"))

    # Detect device
    serial = detect_serial(args.serial)

    # Prepare phone
    print()
    print("=" * 60)
    if args.screenshot:
        print("📸 Action: Take screenshot")
    else:
        print(f"🎯 Task: {args.goal}")
    print("=" * 60)
    print()

    try:
        wake_screen(serial)

        if not args.no_unlock:
            unlock_phone(serial)

        set_keep_awake(serial)
        dismiss_dialogs(serial)

        if args.screenshot:
            take_screenshot(serial, args.screenshot_path)
            return

        # Run the AI agent
        result = asyncio.run(run_droidrun(serial, args.goal, args.model, timeout, args.verbose))

        print()
        print("=" * 60)
        print("✅ Task completed!")
        print("=" * 60)
        if result:
            print(result)

    except KeyboardInterrupt:
        print("\n⏹️  Task cancelled by user")
        sys.exit(130)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Task failed: {e}")
        print("=" * 60)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        # Restore screen timeout
        try:
            restore_screen_timeout(serial)
        except Exception:
            pass


if __name__ == "__main__":
    main()
