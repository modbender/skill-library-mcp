#!/usr/bin/env python3
import json
import subprocess
import sys

CASES = [
    "great job celebration",
    "thanks appreciate it",
    "haha funny",
    "ok got it",
    "sorry my bad",
    "john wick suit",
]


def run(cmd):
    return subprocess.check_output(cmd, text=True)


def main():
    ok = 0
    fail = 0

    for q in CASES:
        try:
            out = run([sys.executable, "skills/openclaw-whatsapp-gif/scripts/send_gif.py", "+10000000000", q, "--delivery-mode", "remote", "--json"])
            data = json.loads(out)
            payload = data.get("payload", {})
            if payload.get("filePath") or payload.get("media"):
                ok += 1
                print(f"PASS: {q}")
            else:
                fail += 1
                print(f"FAIL: {q} (no payload media)")
        except Exception as e:
            fail += 1
            print(f"FAIL: {q} ({e})")

    print(f"\nSummary: pass={ok} fail={fail}")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
