#!/usr/bin/env python3
import argparse
import json
import shlex
import subprocess
import time


def run(cmd: str):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {
        "cmd": cmd,
        "code": p.returncode,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
    }


def parse_json(stdout: str):
    try:
        return json.loads(stdout)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-cmd", required=True, help="command that outputs verifier JSON")
    ap.add_argument("--execute-cmd", required=True, help="executor command to run when no progress")
    ap.add_argument("--sleep-sec", type=int, default=8)
    args = ap.parse_args()

    before_raw = run(args.verify_cmd)
    before = parse_json(before_raw["stdout"]) or {"progress_detected": False, "parse_error": True}

    triggered = False
    exec_raw = None

    if not before.get("progress_detected", False):
        triggered = True
        exec_raw = run(args.execute_cmd)
        time.sleep(args.sleep_sec)

    after_raw = run(args.verify_cmd)
    after = parse_json(after_raw["stdout"]) or {"progress_detected": False, "parse_error": True}

    result = {
        "ok": True,
        "before": before,
        "triggered_execute": triggered,
        "execute_result": exec_raw,
        "after": after,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
