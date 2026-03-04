#!/usr/bin/env python3
"""
Hinge Auto-Liker — Full profile review, smart likes with witty comments.
Scrolls through entire profile, picks best photo/prompt, sends personalized comments.

Requirements:
  - Android emulator with Hinge installed and logged in
  - adb in PATH
  - GEMINI_API_KEY environment variable set

Usage:
  python3 hinge_android.py --likes 8 [--adb /path/to/adb] [--user-desc "description of you"]
"""

import argparse
import base64
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Defaults — overridable via args or env
ADB = os.environ.get("ADB_PATH", "adb")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

WORK_DIR = Path(os.environ.get("HINGE_WORK_DIR", Path(__file__).parent.parent))
SCREENSHOT_DIR = WORK_DIR / "screenshots"
LOG_DIR = WORK_DIR / "logs"

DEFAULT_MAX_LIKES = 8
MIN_DELAY = 1
MAX_DELAY = 3

# User description — personalized via --user-desc flag
USER_DESC = "a guy on Hinge looking for attractive, fun matches"

ANALYSIS_PROMPT_TEMPLATE = """You are evaluating a Hinge dating profile for the user — {user_desc}.

You're seeing multiple screenshots of the same profile scrolled through. The screenshots are numbered in order from top to bottom of the profile (screenshot 1 = top, screenshot 2 = second section, etc).

EVALUATE:
1. Is she attractive? If she's hot, LIKE. Fitness/active lifestyle is a bonus but not required.
2. Does she seem fun, interesting, good energy?
3. Pick the BEST photo or prompt to like — NOT just the first one! Look through ALL the screenshots. Pick the one that:
   - Shows her looking her best (bikini pic, dressed up, great smile, doing something cool)
   - OR has a funny/interesting prompt that gives a great opening for a comment
   - The best content is often NOT the first photo — scroll through everything!
4. Write a SHORT witty/funny comment about THAT SPECIFIC photo/prompt (1 sentence max, casual tone, confident — not cringe, not try-hard, not generic)

VERY IMPORTANT about "which_one":
- which_one = 1 means the content visible in screenshot 1 (top of profile)
- which_one = 2 means content visible in screenshot 2 (after first scroll)
- which_one = 3, 4, etc for content further down
- DO NOT default to 1. Actually look at all screenshots and pick the best one!

BE VERY GENEROUS. Like almost everyone — only skip if she's genuinely unattractive or the profile is completely empty/low effort. When in doubt, LIKE.

Respond with ONLY valid JSON:
{{
  "like": true/false,
  "reason": "brief reason (include name/age if visible)",
  "best_content": "photo" or "prompt",
  "which_one": <number 1-6 indicating which screenshot has the best content to like>,
  "comment": "witty comment about that specific photo/prompt",
  "profile_summary": "1-2 sentence summary of who this person is (name, age, job, vibe)"
}}

Examples of good comments:
- "ok but how competitive do you get at mini golf though"
- "that hiking spot looks unreal, where is that?"
- "the dog is clearly the star of this profile"
- "that dress is doing exactly what it's supposed to do"

Keep it natural. No emojis. No "hey beautiful". Just be clever and specific to what you see."""


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


def adb_cmd(*args):
    try:
        result = subprocess.run([ADB] + list(args), capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        log(f"  ⚠️ ADB command timed out: {args}")
        return ""


def tap(x, y):
    rx, ry = x + random.randint(-3, 3), y + random.randint(-3, 3)
    adb_cmd("shell", "input", "tap", str(rx), str(ry))


def swipe(x1, y1, x2, y2, duration_ms=300):
    adb_cmd("shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms))


def screenshot(path):
    with open(path, "wb") as f:
        subprocess.run([ADB, "exec-out", "screencap", "-p"], stdout=f, timeout=10)


def dump_ui():
    try:
        adb_cmd("shell", "uiautomator", "dump", "/sdcard/ui_dump.xml")
        subprocess.run([ADB, "pull", "/sdcard/ui_dump.xml", "/tmp/ui_dump.xml"],
                       capture_output=True, text=True, timeout=10)
        with open("/tmp/ui_dump.xml") as f:
            return f.read()
    except Exception as e:
        log(f"  ⚠️ UI dump failed: {e}")
        return ""


def find_button(xml, content_desc=None, text=None):
    if content_desc:
        patterns = [
            f'content-desc="{content_desc}"[^>]*bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"',
            f'bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"[^>]*content-desc="{content_desc}"'
        ]
    elif text:
        patterns = [
            f'text="{re.escape(text)}"[^>]*bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"',
            f'bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"[^>]*text="{re.escape(text)}"'
        ]
    else:
        return None
    for pattern in patterns:
        match = re.search(pattern, xml, re.IGNORECASE)
        if match:
            x1, y1, x2, y2 = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
            return ((x1 + x2) // 2, (y1 + y2) // 2)
    return None


def find_all_hearts(xml):
    hearts = []
    for pattern in [
        r'content-desc="[^"]*[Ll]ike[^"]*"[^>]*bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',
        r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*content-desc="[^"]*[Ll]ike[^"]*"'
    ]:
        for m in re.finditer(pattern, xml):
            x1, y1, x2, y2 = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
            center = ((x1 + x2) // 2, (y1 + y2) // 2)
            if center not in hearts:
                hearts.append(center)
    return hearts


def find_skip_button(xml):
    for desc in ["Remove", "Skip", "Pass", "Dismiss"]:
        for pattern in [
            f'content-desc="{desc}"[^>]*bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"',
            f'bounds="\\[(\\d+),(\\d+)\\]\\[(\\d+),(\\d+)\\]"[^>]*content-desc="{desc}"'
        ]:
            match = re.search(pattern, xml, re.IGNORECASE)
            if match:
                x1, y1, x2, y2 = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
                return ((x1 + x2) // 2, (y1 + y2) // 2)
    return None


def dismiss_popups():
    time.sleep(0.3)
    xml = dump_ui()
    for text in ["Send Like anyway", "Ask me later", "Not now", "No thanks", "Maybe later", "Close"]:
        btn = find_button(xml, text=text)
        if btn:
            log(f"  Dismissing '{text}'...")
            tap(*btn)
            time.sleep(0.5)
            xml = dump_ui()


def scroll_full_profile():
    """Scroll through entire profile, taking screenshots at each position."""
    screenshots = []
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = str(SCREENSHOT_DIR / f"profile_{ts}_top.png")
    screenshot(path)
    screenshots.append(path)

    for i in range(5):
        swipe(540, 1800, 540, 400, 300)
        time.sleep(0.6)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = str(SCREENSHOT_DIR / f"profile_{ts}_scroll{i+1}.png")
        screenshot(path)
        screenshots.append(path)

    return screenshots


def analyze_profile(image_paths):
    """Send screenshots to Gemini for profile analysis."""
    if not GEMINI_API_KEY:
        log("  ⚠️ No GEMINI_API_KEY set — liking by default")
        return {"like": True, "reason": "no API key", "comment": "", "profile_summary": "unknown"}

    prompt = ANALYSIS_PROMPT_TEMPLATE.format(user_desc=USER_DESC)
    parts = [{"text": prompt}]
    for img_path in image_paths[:4]:
        with open(img_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()
        parts.append({"inline_data": {"mime_type": "image/png", "data": image_b64}})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 300}
    }

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(payload, tmp)
            tmp_path = tmp.name

        result = subprocess.run(
            ["curl", "-s", "-X", "POST",
             f"{GEMINI_URL}?key={GEMINI_API_KEY}",
             "-H", "Content-Type: application/json",
             "-d", f"@{tmp_path}"],
            capture_output=True, text=True, timeout=45
        )
        os.unlink(tmp_path)

        response = json.loads(result.stdout)
        parts_out = response["candidates"][0]["content"]["parts"]
        text = ""
        for p in parts_out:
            if "text" in p:
                text = p["text"].strip()

        if "```" in text:
            json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
            if json_match:
                text = json_match.group(1).strip()

        json_match = re.search(r'\{[^{}]*"like"[^{}]*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return json.loads(text)
    except Exception as e:
        log(f"  ⚠️ Analysis error: {e}")
        return {"like": True, "reason": "analysis failed, liking by default", "comment": "", "profile_summary": "unknown"}


def like_with_comment(comment="", which_one=1):
    """Like a specific photo/prompt on the profile."""
    # Scroll back to top
    for _ in range(7):
        swipe(540, 400, 540, 1800, 150)
        time.sleep(0.2)
    time.sleep(0.3)

    # Scroll to target position
    target_idx = max(0, which_one - 1)
    log(f"  🎯 Scrolling to content #{which_one}")
    for _ in range(target_idx):
        swipe(540, 1800, 540, 400, 300)
        time.sleep(0.5)
    time.sleep(0.3)

    xml = dump_ui()
    hearts = find_all_hearts(xml)

    if not hearts:
        swipe(540, 1200, 540, 900, 200)
        time.sleep(0.3)
        xml = dump_ui()
        hearts = find_all_hearts(xml)

    if not hearts:
        log(f"  ⚠️ No heart found, falling back to first available")
        for _ in range(7):
            swipe(540, 400, 540, 1800, 150)
            time.sleep(0.2)
        time.sleep(0.3)
        xml = dump_ui()
        hearts = find_all_hearts(xml)
        if not hearts:
            log("  ⚠️ No heart button found at all")
            return False

    tap(*hearts[0])
    time.sleep(1.5)

    if comment:
        xml = dump_ui()
        comment_btn = find_button(xml, text="Add a comment")
        if comment_btn:
            tap(*comment_btn)
            time.sleep(0.5)
        safe_comment = comment.replace("'", "\\'").replace('"', '\\"').replace(" ", "%s")
        adb_cmd("shell", "input", "text", safe_comment)
        time.sleep(0.5)

    xml = dump_ui()
    send_btn = find_button(xml, content_desc="Send like")
    if not send_btn:
        send_btn = find_button(xml, text="Send like")
    if not send_btn:
        send_btn = find_button(xml, text="Send Like")
    if send_btn:
        tap(*send_btn)
        time.sleep(1.5)
    else:
        log("  ⚠️ Could not find 'Send like' button")
        return False

    dismiss_popups()
    return True


def skip_profile():
    xml = dump_ui()
    skip = find_skip_button(xml)
    if not skip:
        skip = (135, 2045)
    tap(*skip)
    time.sleep(1)
    dismiss_popups()


def run(max_likes=DEFAULT_MAX_LIKES):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log(f"=== Hinge Auto-Liker (Android) ===")
    log(f"Max likes: {max_likes}")
    log(f"Model: {GEMINI_MODEL}")

    dismiss_popups()

    # Check for paywall
    xml = dump_ui()
    if "out of free likes" in xml.lower() or "hinge+" in xml.lower() or "hingex" in xml.lower():
        log("⚠️ Out of free likes! Paywall detected.")
        adb_cmd("shell", "input", "keyevent", "4")
        time.sleep(1)
        xml = dump_ui()
        if "out of free likes" in xml.lower() or "hinge+" in xml.lower():
            log("Likes haven't reset. Try again later.")
            return {"date": datetime.now().isoformat(), "profiles_seen": 0, "likes": 0,
                    "skips": 0, "actions": [], "error": "out_of_likes"}

    actions = []
    likes_used = 0
    profiles_seen = 0

    for i in range(max_likes * 3):
        if likes_used >= max_likes:
            log(f"\nUsed all {max_likes} likes. Done!")
            break

        profiles_seen += 1
        log(f"\n--- Profile #{profiles_seen} ---")

        xml = dump_ui()
        if "out of free likes" in xml.lower() or "hingex" in xml.lower():
            log(f"Hit daily limit after {likes_used} likes!")
            dismiss_popups()
            break

        log("  📸 Reviewing full profile...")
        screenshots = scroll_full_profile()

        log(f"  🔍 Analyzing with {GEMINI_MODEL}...")
        analysis = analyze_profile(screenshots)
        should_like = analysis.get("like", False)
        reason = analysis.get("reason", "?")
        comment = analysis.get("comment", "")
        profile_summary = analysis.get("profile_summary", "")

        if should_like:
            which_one = analysis.get("which_one", 1)
            log(f"  ❤️  LIKE (#{likes_used + 1}/{max_likes}) — {reason} [content #{which_one}]")
            if comment:
                log(f"  💬 Comment: \"{comment}\"")
            success = like_with_comment(comment, which_one=which_one)
            if success:
                likes_used += 1
                action = "like"
            else:
                log("  ⚠️ Like failed, skipping")
                skip_profile()
                action = "skip_failed"
        else:
            log(f"  ✖️  SKIP — {reason}")
            skip_profile()
            action = "skip"

        actions.append({
            "profile": profiles_seen,
            "action": action,
            "reason": reason,
            "comment": comment if action == "like" else "",
            "profile_summary": profile_summary,
            "which_one": analysis.get("which_one", 1),
            "best_content": analysis.get("best_content", ""),
            "timestamp": datetime.now().isoformat()
        })

        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        log(f"  ⏳ {delay:.1f}s...")
        time.sleep(delay)

    # Build summary
    summary = {
        "date": datetime.now().isoformat(),
        "profiles_seen": profiles_seen,
        "likes": sum(1 for a in actions if a["action"] == "like"),
        "skips": sum(1 for a in actions if a["action"] in ("skip", "skip_failed")),
        "actions": actions
    }

    # Save JSON log
    log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
    with open(log_file, "w") as f:
        json.dump(summary, f, indent=2)
    log(f"Log saved: {log_file}")

    # Print report for the agent to relay
    print("\n" + "=" * 50)
    print("HINGE SESSION REPORT")
    print("=" * 50)
    print(f"Date: {summary['date']}")
    print(f"Profiles seen: {summary['profiles_seen']}")
    print(f"Liked: {summary['likes']} | Skipped: {summary['skips']}")
    if summary.get("error"):
        print(f"Error: {summary['error']}")
    print()
    for a in actions:
        emoji = "❤️" if a["action"] == "like" else "✖️"
        print(f"{emoji} Profile #{a['profile']}: {a['action'].upper()}")
        if a.get("profile_summary"):
            print(f"   Who: {a['profile_summary']}")
        print(f"   Why: {a['reason']}")
        if a.get("comment"):
            print(f"   Comment sent: \"{a['comment']}\"")
        if a.get("best_content") and a["action"] == "like":
            print(f"   Liked: {a['best_content']} #{a.get('which_one', '?')}")
        print()
    print("=" * 50)
    print("END REPORT")
    print("=" * 50)

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hinge Auto-Liker")
    parser.add_argument("--likes", type=int, default=DEFAULT_MAX_LIKES, help="Max likes per session")
    parser.add_argument("--adb", type=str, default=None, help="Path to adb binary")
    parser.add_argument("--user-desc", type=str, default=None, help="Description of you for AI matching")
    args = parser.parse_args()

    if args.adb:
        ADB = args.adb
    if args.user_desc:
        USER_DESC = args.user_desc

    result = run(args.likes)
    sys.exit(0 if result.get("likes", 0) > 0 or not result.get("error") else 1)
