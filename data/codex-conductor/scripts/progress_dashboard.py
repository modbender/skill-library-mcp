#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def read_status(root: Path):
    p = root / ".orchestrator" / "status.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Render orchestrator progress dashboard")
    parser.add_argument("--root", default=".", help="Project root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    data = read_status(root)

    if not data:
        print("No .orchestrator/status.json found")
        return

    gates = data.get("gates", {})
    total = len(gates)
    passed = sum(1 for g in gates.values() if g.get("state") == "PASS")
    pct = int((passed / total) * 100) if total else 0

    print("=== Codex Orchestrator Dashboard ===")
    print(f"Root: {root}")
    print(f"Overall Status: {data.get('meta', {}).get('status', 'UNKNOWN')}")
    print(f"Completion: {pct}% ({passed}/{total} gates passed)")
    print()
    print("Gate States:")
    for gate in sorted(gates.keys()):
        state = gates[gate].get("state")
        note = gates[gate].get("note")
        print(f"- {gate}: {state} {('- ' + note) if note else ''}")

    hist = data.get("history", [])
    if hist:
        print()
        print("Recent Activity:")
        for item in hist[-5:]:
            print(f"- {item.get('timestamp')} | {item.get('gate')} -> {item.get('state')} | {item.get('note', '')}")


if __name__ == "__main__":
    main()
