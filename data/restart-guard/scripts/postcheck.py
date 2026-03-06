#!/usr/bin/env python3
"""
restart-guard: postcheck.py
Post-restart verification. Reads context file, runs verify commands, reports results.

Usage:
  python3 postcheck.py --config <path>

Exit codes:
  0 = all verifications passed
  1 = one or more verifications failed
  2 = context file missing or parse error
"""
import argparse
import json
import os
import shlex
import subprocess
import shutil
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SHELL_METACHARS = ("|", ">", "<", ";", "&&", "||", "$(", "`")


def main():
    parser = argparse.ArgumentParser(description="Post-restart verification")
    parser.add_argument("--config", required=True, help="Path to restart-guard.yaml")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    config = load_config(args.config)
    paths = config.get("paths", {})
    context_path = expand(paths.get("context_file", "~/.openclaw/custom/work/restart-context.md"))
    oc_bin = find_openclaw(paths.get("openclaw_bin", ""))

    if not os.path.isfile(context_path):
        if args.json:
            print(json.dumps({"status": "no_context", "message": "No restart context file found"}))
        else:
            print("No restart context file found. Nothing to verify.")
        sys.exit(0)  # Not an error — just no pending restart

    # Parse YAML frontmatter
    frontmatter, _ = parse_markdown_frontmatter(context_path)
    if not isinstance(frontmatter, dict):
        print("Error: cannot parse context file frontmatter", file=sys.stderr)
        sys.exit(2)

    reason = frontmatter.get("reason", "unknown")
    restart_id = frontmatter.get("restart_id", "")
    delivery_status = frontmatter.get("delivery_status", "")
    diagnostics_file = frontmatter.get("diagnostics_file", "")
    verify_list = frontmatter.get("verify", [])
    resume_list = frontmatter.get("resume", [])
    rollback = frontmatter.get("rollback", {})

    results = []
    all_passed = True

    for item in verify_list:
        if isinstance(item, dict):
            cmd = item.get("command", "")
            expect = item.get("expect", "")
        elif isinstance(item, str):
            cmd = item
            expect = ""
        else:
            continue

        if not cmd:
            continue

        # Replace 'openclaw' with actual binary
        actual_cmd_str = cmd
        if oc_bin and cmd.startswith("openclaw "):
            actual_cmd_str = oc_bin + cmd[8:]

        try:
            # Hard block shell metacharacters to keep execution deterministic and non-shell.
            if contains_shell_metachar(actual_cmd_str):
                raise ValueError("shell metacharacters are not allowed in verify commands")
            exec_args = shlex.split(actual_cmd_str)
            if not exec_args:
                raise ValueError("empty command after parsing")

            proc = subprocess.run(
                exec_args, shell=False, capture_output=True, text=True, timeout=30,
            )
            output = proc.stdout.strip()
            passed = True
            if expect:
                passed = expect.lower() in output.lower()
            if proc.returncode != 0:
                passed = False

            results.append({
                "command": cmd,
                "expect": expect,
                "output": output[:500],
                "returncode": proc.returncode,
                "passed": passed,
            })
            if not passed:
                all_passed = False
        except (subprocess.TimeoutExpired, OSError) as e:
            results.append({
                "command": cmd,
                "expect": expect,
                "output": str(e),
                "returncode": -1,
                "passed": False,
            })
            all_passed = False
        except ValueError as e:
            results.append({
                "command": cmd,
                "expect": expect,
                "output": str(e),
                "returncode": -1,
                "passed": False,
            })
            all_passed = False

    report = {
        "status": "passed" if all_passed else "failed",
        "restart_id": restart_id,
        "reason": reason,
        "delivery_status": delivery_status,
        "diagnostics_file": diagnostics_file,
        "checks": results,
        "resume": resume_list,
        "rollback": rollback,
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Restart postcheck: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        print(f"Reason: {reason}")
        for r in results:
            status = "✅" if r["passed"] else "❌"
            print(f"  {status} {r['command']}")
            if r["expect"]:
                print(f"     expect: {r['expect']}")
            if not r["passed"]:
                print(f"     output: {r['output'][:200]}")
        if resume_list:
            print("\nResume steps:")
            for i, step in enumerate(resume_list, 1):
                print(f"  {i}. {step}")

    sys.exit(0 if all_passed else 1)


def expand(p):
    return os.path.expanduser(p) if p else p


def find_openclaw(configured):
    if configured:
        p = expand(configured)
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    p = shutil.which("openclaw")
    if p:
        return p
    import glob
    candidates = sorted(glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin/openclaw")))
    return candidates[-1] if candidates else None


def load_config(path):
    sys.path.insert(0, SCRIPT_DIR)
    from write_context import load_config as _load
    return _load(path)


def parse_markdown_frontmatter(path):
    sys.path.insert(0, SCRIPT_DIR)
    from write_context import parse_markdown_frontmatter as _parse
    return _parse(path)


def contains_shell_metachar(cmd):
    text = str(cmd or "")
    return any(token in text for token in SHELL_METACHARS)


if __name__ == "__main__":
    main()
