#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PY = SCRIPT_DIR / "realm_manager.py"


def run(args):
    cmd = [sys.executable, str(PY), *args]
    return subprocess.call(cmd)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", nargs="?", default="help")
    p.add_argument("rest", nargs="*")
    ns = p.parse_args()

    c = ns.command.lower()
    r = ns.rest

    if c == "init":
        model = r[0] if r else "qwen3-max"
        raise SystemExit(run(["install", "--default-model", model, "--restart-gateway"]))
    if c in ("key", "k"):
        if not r:
            print("Usage: rr key <api-key>")
            raise SystemExit(1)
        raise SystemExit(run(["set-key", "--api-key", r[0], "--restart-gateway"]))
    if c in ("use", "m"):
        if not r:
            print("Usage: rr use <model-id|alias|index>")
            raise SystemExit(1)
        raise SystemExit(run(["set-model", "--model", r[0], "--restart-gateway"]))
    if c == "pick":
        raise SystemExit(run(["models"]))
    if c == "test":
        raise SystemExit(run(["test", *r]))
    if c == "show":
        raise SystemExit(run(["show"]))
    if c == "list":
        raise SystemExit(run(["list-models"]))
    if c in ("rollback", "rb"):
        if r:
            raise SystemExit(run(["rollback", "--backup", r[0], "--restart-gateway"]))
        raise SystemExit(run(["rollback", "--restart-gateway"]))

    print("""rr (Windows) - short wrapper for realmrouter-switch

Commands:
  rr init [model]
  rr key|k <api-key>
  rr use|m <model>
  rr pick
  rr test
  rr show
  rr list
  rr rollback|rb [file]
""")


if __name__ == "__main__":
    main()
