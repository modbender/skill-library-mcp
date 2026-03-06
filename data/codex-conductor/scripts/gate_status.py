#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

GATES = ["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7"]
STATES = ["PENDING", "IN_PROGRESS", "PASS", "FAIL", "BLOCKED"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_status():
    return {
        "meta": {
            "createdAt": now_iso(),
            "updatedAt": now_iso(),
            "status": "IN_PROGRESS",
        },
        "gates": {g: {"state": "PENDING", "updatedAt": None, "note": ""} for g in GATES},
        "history": [],
    }


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    data["meta"]["updatedAt"] = now_iso()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def status_path(root: Path) -> Path:
    return root / ".orchestrator" / "status.json"


def context_path(root: Path) -> Path:
    return root / ".orchestrator" / "context.json"


def load(root: Path):
    return load_json(status_path(root), default_status())


def load_context(root: Path):
    return load_json(
        context_path(root),
        {
            "projectMode": "greenfield",
            "executionMode": "gated",
            "researchMode": False,
        },
    )


def validate_status_schema(data):
    if not isinstance(data, dict):
        return False, "status.json must be an object"
    if "meta" not in data or "gates" not in data or "history" not in data:
        return False, "status.json missing required top-level keys: meta/gates/history"

    if not isinstance(data["gates"], dict):
        return False, "gates must be an object"

    for g in GATES:
        if g not in data["gates"]:
            return False, f"missing gate entry: {g}"
        entry = data["gates"][g]
        if not isinstance(entry, dict):
            return False, f"gate entry must be object: {g}"
        if entry.get("state") not in STATES:
            return False, f"invalid state for {g}: {entry.get('state')}"

    if not isinstance(data["history"], list):
        return False, "history must be an array"

    return True, "OK"


def doc_has_substance(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        # Ignore markdown table separator lines like |---|---|
        if set(line.replace("|", "").replace("-", "").replace(":", "").strip()) == set():
            continue
        if line.startswith("-") and len(line) <= 3:
            continue
        if "TBD" in line.upper():
            continue
        return True
    return False


def sequential_prereq(gate: str):
    i = GATES.index(gate)
    if i == 0:
        return []
    return GATES[:i]


def mode_preconditions(root: Path, gate: str, project_mode: str):
    checks = []
    if gate == "G2" and project_mode == "greenfield":
        checks.extend(
            [
                root / "docs" / "requirements.md",
                root / "docs" / "architecture.md",
                root / "docs" / "adr" / "ADR-0001-initial-architecture.md",
            ]
        )
    if gate == "G2" and project_mode == "brownfield":
        checks.extend(
            [
                root / "docs" / "as-is-architecture.md",
                root / "docs" / "system-inventory.md",
                root / "docs" / "dependency-map.md",
                root / "docs" / "legacy-risk-register.md",
                root / "docs" / "compatibility-matrix.md",
                root / "docs" / "migration-plan.md",
                root / "docs" / "characterization-tests.md",
            ]
        )
    if gate in ("G4", "G6") and project_mode == "brownfield":
        checks.extend(
            [
                root / "docs" / "compatibility-matrix.md",
                root / "docs" / "migration-plan.md",
            ]
        )
    return checks


def check_preconditions(root: Path, data, gate: str, target_state: str):
    if target_state not in ("IN_PROGRESS", "PASS"):
        return True, "No preconditions required for this transition"

    # Sequential progression
    required_prev = sequential_prereq(gate)
    for g in required_prev:
        if data["gates"][g]["state"] != "PASS":
            return False, f"Precondition failed: previous gate {g} must be PASS"

    # Mode-specific docs checks
    ctx = load_context(root)
    project_mode = ctx.get("projectMode", "greenfield")
    for p in mode_preconditions(root, gate, project_mode):
        if not p.exists():
            return False, f"Precondition failed: missing required document {p.relative_to(root)}"
        if gate in ("G2",) and not doc_has_substance(p):
            return False, f"Precondition failed: document lacks substantive content {p.relative_to(root)}"

    return True, "OK"


def set_meta_status(data):
    if all(data["gates"][g]["state"] == "PASS" for g in GATES):
        data["meta"]["status"] = "COMPLETE"
    elif any(data["gates"][g]["state"] in ("FAIL", "BLOCKED") for g in GATES):
        data["meta"]["status"] = "ATTENTION"
    else:
        data["meta"]["status"] = "IN_PROGRESS"


def cmd_set(args):
    root = Path(args.root).resolve()
    path = status_path(root)
    data = load(root)

    ok, msg = validate_status_schema(data)
    if not ok:
        raise SystemExit(f"Invalid status schema: {msg}")

    if args.gate not in GATES:
        raise SystemExit(f"Invalid gate: {args.gate}")
    if args.state not in STATES:
        raise SystemExit(f"Invalid state: {args.state}")

    if not args.no_enforce:
        ok, msg = check_preconditions(root, data, args.gate, args.state)
        if not ok:
            raise SystemExit(msg)

    data["gates"][args.gate] = {"state": args.state, "updatedAt": now_iso(), "note": args.note or ""}
    data["history"].append(
        {
            "timestamp": now_iso(),
            "gate": args.gate,
            "state": args.state,
            "note": args.note or "",
        }
    )

    set_meta_status(data)
    save(path, data)
    print(f"Updated {args.gate} -> {args.state}")


def cmd_show(args):
    root = Path(args.root).resolve()
    data = load(root)
    print(json.dumps(data, indent=2))


def cmd_validate(args):
    root = Path(args.root).resolve()
    p = status_path(root)
    if not p.exists():
        raise SystemExit(f"Missing {p}")
    data = load(root)
    ok, msg = validate_status_schema(data)
    if not ok:
        raise SystemExit(f"Invalid: {msg}")
    print("status.json schema: OK")


def main():
    parser = argparse.ArgumentParser(description="Gate status manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_set = sub.add_parser("set", help="Set a gate state")
    p_set.add_argument("--root", default=".", help="Project root")
    p_set.add_argument("--gate", required=True, help="Gate id (G0..G7)")
    p_set.add_argument("--state", required=True, help="State")
    p_set.add_argument("--note", default="", help="Optional note")
    p_set.add_argument("--no-enforce", action="store_true", help="Disable precondition enforcement")
    p_set.set_defaults(func=cmd_set)

    p_show = sub.add_parser("show", help="Show current status")
    p_show.add_argument("--root", default=".", help="Project root")
    p_show.set_defaults(func=cmd_show)

    p_validate = sub.add_parser("validate", help="Validate status schema")
    p_validate.add_argument("--root", default=".", help="Project root")
    p_validate.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
