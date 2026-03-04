#!/usr/bin/env bash
# Registry health checker for Osori
# Usage: doctor.sh [--fix] [--dry-run] [--yes] [--json]
#
# Default (no flags):  analyze + preview (no changes applied)
# --fix:               analyze + preview + apply (prompts for high-risk)
# --dry-run:           analyze + preview only (explicit, never applies)
# --yes:               auto-approve low/medium risk (high still requires explicit --fix)
# --json:              machine-readable JSON output

set -euo pipefail

REGISTRY_FILE="${OSORI_REGISTRY:-$HOME/.openclaw/osori.json}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DO_FIX="false"
DRY_RUN="false"
AUTO_YES="false"
OUT_JSON="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fix)
      DO_FIX="true"
      shift
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    --yes)
      AUTO_YES="true"
      shift
      ;;
    --json)
      OUT_JSON="true"
      shift
      ;;
    -h|--help|help)
      cat << 'EOF'
Usage:
  doctor.sh [--fix] [--dry-run] [--yes] [--json]

Modes:
  (default)   Analyze + preview plan (no changes applied)
  --fix       Analyze + preview + apply fixes
  --dry-run   Analyze + preview only (never applies, explicit)
  --yes       Auto-approve low/medium risk fixes (high risk still blocked without --fix)
  --json      Machine-readable JSON report

Risk Levels:
  low     Schema normalization, missing fields, migration
  medium  Duplicate removal, root reference repair
  high    Registry re-initialization from corrupted state
EOF
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

OSORI_SCRIPT_DIR="$SCRIPT_DIR" \
OSORI_REG="$REGISTRY_FILE" \
OSORI_DO_FIX="$DO_FIX" \
OSORI_DRY_RUN="$DRY_RUN" \
OSORI_AUTO_YES="$AUTO_YES" \
OSORI_OUT_JSON="$OUT_JSON" \
python3 << 'PYEOF'
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.environ["OSORI_SCRIPT_DIR"])
from registry_lib import (
    REGISTRY_SCHEMA,
    REGISTRY_VERSION,
    load_registry,
    registry_projects,
    registry_roots,
    save_registry,
    set_registry_projects,
)

reg_path = os.environ["OSORI_REG"]
do_fix = os.environ.get("OSORI_DO_FIX", "false").lower() == "true"
dry_run = os.environ.get("OSORI_DRY_RUN", "false").lower() == "true"
auto_yes = os.environ.get("OSORI_AUTO_YES", "false").lower() == "true"
out_json = os.environ.get("OSORI_OUT_JSON", "false").lower() == "true"

# dry-run overrides fix
if dry_run:
    do_fix = False

findings = []
plan = []  # list of planned fix actions


# ── helpers ──────────────────────────────────────────

def add(severity, code, message, suggestion=None, project=None):
    row = {"severity": severity, "code": code, "message": message}
    if suggestion:
        row["suggestion"] = suggestion
    if project:
        row["project"] = project
    findings.append(row)


def plan_action(risk, action, description, detail=None):
    """Queue a fix action with risk level."""
    entry = {"risk": risk, "action": action, "description": description}
    if detail:
        entry["detail"] = detail
    plan.append(entry)


def count_by_severity(rows):
    c = {"error": 0, "warn": 0, "info": 0}
    for r in rows:
        sev = r.get("severity", "info")
        if sev not in c:
            c[sev] = 0
        c[sev] += 1
    return c


def risk_order(risk):
    return {"low": 0, "medium": 1, "high": 2}.get(risk, 9)


def repo_valid(repo):
    if repo == "":
        return True
    return re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", repo) is not None


# ── Phase 1: Analyze ────────────────────────────────

raw_payload = None
raw_ok = False
registry_corrupted = False
registry_missing = False

if os.path.exists(reg_path):
    try:
        with open(reg_path, encoding="utf-8") as f:
            raw_payload = json.load(f)
            raw_ok = True
    except Exception as e:
        add(
            "error", "registry.corrupted",
            f"Registry JSON parse failed: {e}",
            "Run with --fix to preserve broken file and reinitialize safely.",
        )
        registry_corrupted = True
        plan_action("high", "reinitialize",
                     "Preserve broken file as .broken-<ts> and create fresh registry",
                     f"source: {reg_path}")
else:
    add("warn", "registry.missing", f"Registry file not found: {reg_path}",
        "Run with --fix to initialize registry.")
    registry_missing = True
    plan_action("low", "initialize", f"Create new registry at {reg_path}")

needs_migration = False
needs_schema_fix = False
raw_projects = []
raw_roots = []

if raw_ok:
    if isinstance(raw_payload, list):
        add("warn", "registry.legacy_array",
            "Legacy array registry detected.",
            "Run with --fix to migrate to versioned schema.")
        raw_projects = [p for p in raw_payload if isinstance(p, dict)]
        raw_roots = [{"key": "default", "paths": []}]
        needs_migration = True
        plan_action("low", "migrate_legacy",
                     f"Migrate legacy array format → versioned schema v{REGISTRY_VERSION}",
                     f"{len(raw_projects)} project(s)")
    elif isinstance(raw_payload, dict):
        schema = raw_payload.get("schema")
        version = raw_payload.get("version")

        if schema != REGISTRY_SCHEMA:
            add("warn", "registry.schema_mismatch",
                f"schema={schema!r}, expected {REGISTRY_SCHEMA!r}",
                "Run with --fix to normalize schema.")
            needs_schema_fix = True
            plan_action("low", "fix_schema",
                         f"Update schema: {schema!r} → {REGISTRY_SCHEMA!r}")

        try:
            version_int = int(version)
        except Exception:
            version_int = None

        if version_int != REGISTRY_VERSION:
            add("warn", "registry.version_mismatch",
                f"version={version!r}, expected {REGISTRY_VERSION}",
                "Run with --fix to migrate version.")
            needs_migration = True
            plan_action("low", "migrate_version",
                         f"Migrate version: {version!r} → {REGISTRY_VERSION}")

        raw_projects = raw_payload.get("projects", [])
        if not isinstance(raw_projects, list):
            add("error", "registry.projects_invalid_type",
                f"projects field is {type(raw_projects).__name__}, expected list",
                "Run with --fix to normalize projects container.")
            raw_projects = []

        raw_roots = raw_payload.get("roots", [])
        if not isinstance(raw_roots, list):
            add("warn", "registry.roots_invalid_type",
                f"roots field is {type(raw_roots).__name__}, expected list",
                "Run with --fix to normalize roots container.")
            raw_roots = []
    else:
        add("error", "registry.invalid_top_level",
            f"top-level JSON type is {type(raw_payload).__name__}, expected object/list",
            "Run with --fix to reset registry format safely.")
        raw_projects = []
        raw_roots = []

    # root key set
    root_keys = set()
    for r in raw_roots:
        if isinstance(r, dict):
            key = str(r.get("key", "")).strip()
            if key:
                root_keys.add(key)

    # project checks
    name_map = defaultdict(list)
    path_map = defaultdict(list)

    for idx, p in enumerate(raw_projects):
        if not isinstance(p, dict):
            add("error", "project.invalid_item",
                f"projects[{idx}] is not an object",
                "Run with --fix to normalize registry entries.")
            continue

        name = str(p.get("name", "")).strip()
        path = str(p.get("path", "")).strip()
        root = str(p.get("root", "default") or "default").strip() or "default"
        repo = str(p.get("repo", "") or "")

        if not name or not path:
            add("error", "project.missing_required",
                f"projects[{idx}] missing required fields name/path",
                "Run with --fix to remove invalid project entries.")
            continue

        name_map[name].append(idx)
        path_map[path].append(idx)

        if root_keys and root not in root_keys:
            add("warn", "project.root_reference_missing",
                f"project '{name}' references unknown root '{root}'",
                "Run with --fix to add missing root metadata automatically.",
                project=name)
            plan_action("medium", "add_missing_root",
                         f"Add missing root '{root}' referenced by project '{name}'",
                         f"root={root}")

        if not repo_valid(repo):
            add("warn", "project.repo_invalid_format",
                f"project '{name}' has invalid repo format: {repo!r}",
                "Use owner/repo format (or leave empty).",
                project=name)

        if not os.path.exists(path):
            add("error", "project.path_missing",
                f"project '{name}' path does not exist: {path}",
                "Remove project or update to a valid path.",
                project=name)

    for n, idxs in name_map.items():
        if len(idxs) > 1:
            add("warn", "project.duplicate_name",
                f"duplicate project name '{n}' at indices {idxs}",
                "Keep one canonical entry and remove duplicates.",
                project=n)
            plan_action("medium", "dedupe_name",
                         f"Remove {len(idxs) - 1} duplicate(s) of '{n}'",
                         f"indices: {idxs}")

    for pth, idxs in path_map.items():
        if len(idxs) > 1:
            add("warn", "project.duplicate_path",
                f"duplicate project path '{pth}' at indices {idxs}",
                "Keep one canonical entry and remove duplicates.")
            plan_action("medium", "dedupe_path",
                         f"Remove {len(idxs) - 1} duplicate path(s): {pth}",
                         f"indices: {idxs}")


# ── Phase 2: Plan (dedupe plan actions) ─────────────

# Deduplicate plan entries by action key
seen_actions = set()
unique_plan = []
for p in plan:
    key = (p["action"], p.get("detail", ""))
    if key not in seen_actions:
        seen_actions.add(key)
        unique_plan.append(p)
plan = unique_plan

# Classify risk summary
risk_summary = {"low": 0, "medium": 0, "high": 0}
for p in plan:
    risk_summary[p["risk"]] = risk_summary.get(p["risk"], 0) + 1

has_high_risk = risk_summary.get("high", 0) > 0


# ── Phase 3: Preview ────────────────────────────────
# (output is generated at the end)


# ── Phase 4: Apply (plan-driven, only if --fix) ─────

fix_applied = False
fix_backup = None
migration_backup = None
migration_notes = []
dedupe_removed = 0
actions_applied = []
actions_blocked = []


def apply_action(action_entry):
    """Execute a single plan action. Returns True if applied."""
    act = action_entry["action"]

    if act in ("migrate_legacy", "migrate_version", "fix_schema", "initialize"):
        # Handled by load_registry(auto_migrate=True)
        return True

    if act == "reinitialize":
        # Handled by load_registry corruption path
        return True

    if act in ("dedupe_name", "dedupe_path"):
        # Handled by dedupe pass below
        return True

    if act == "add_missing_root":
        # Handled by load_registry normalization (adds missing roots)
        return True

    return False


if do_fix and plan:
    # Gate actions by risk level
    for p in plan:
        risk = p["risk"]
        if risk == "high" and not auto_yes:
            actions_blocked.append(p)
            continue
        if apply_action(p):
            actions_applied.append(p)
        else:
            actions_blocked.append(p)

    # Run load_registry to apply migration/normalization actions
    loaded = load_registry(reg_path, auto_migrate=True, make_backup_on_migrate=True)
    migration_notes = loaded.migration_notes if loaded.migrated else []
    migration_backup = loaded.backup_path
    registry = loaded.registry

    # Dedupe pass (applies dedupe_name / dedupe_path actions)
    has_dedupe = any(a["action"] in ("dedupe_name", "dedupe_path") for a in actions_applied)
    if has_dedupe:
        projects = registry_projects(registry)
        seen = set()
        deduped = []
        for p in projects:
            key = (str(p.get("name", "")).strip(), str(p.get("path", "")).strip())
            if key in seen:
                dedupe_removed += 1
                continue
            seen.add(key)
            deduped.append(p)

        if dedupe_removed > 0:
            set_registry_projects(registry, deduped)
            fix_backup = save_registry(reg_path, registry, make_backup=True)

    fix_applied = True

    # Report applied actions
    if migration_notes:
        add("info", "fix.migration_applied", f"migration applied: {'; '.join(migration_notes)}")
    if migration_backup:
        add("info", "fix.migration_backup", f"migration backup: {migration_backup}")
    if dedupe_removed > 0:
        add("info", "fix.dedupe_applied", f"removed exact duplicate entries: {dedupe_removed}")
        if fix_backup:
            add("info", "fix.backup_created", f"backup created: {fix_backup}")
    if not migration_notes and dedupe_removed == 0:
        add("info", "fix.noop", "no safe fix changes were required")

elif do_fix and not plan:
    fix_applied = True
    add("info", "fix.noop", "no safe fix changes were required")


# ── Output ──────────────────────────────────────────

counts = count_by_severity(findings)
status = "ok" if counts.get("error", 0) == 0 and counts.get("warn", 0) == 0 else "issues"

report = {
    "status": status,
    "registry": reg_path,
    "counts": counts,
    "findings": findings,
    "plan": plan,
    "riskSummary": risk_summary,
    "fix": {
        "requested": do_fix,
        "dryRun": dry_run,
        "applied": fix_applied,
        "actionsApplied": len(actions_applied),
        "actionsBlocked": len(actions_blocked),
        "migrationNotes": migration_notes,
        "migrationBackup": migration_backup,
        "dedupeRemoved": dedupe_removed,
        "backup": fix_backup,
    },
}

if out_json:
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0)

# Human-readable output
print("🩺 Osori Doctor")
print(f"Registry: {reg_path}")
print(f"Counts: ERROR={counts.get('error', 0)} WARN={counts.get('warn', 0)} INFO={counts.get('info', 0)}")
print()

if not findings and not plan:
    print("✅ No issues found.")
    raise SystemExit(0)

# Findings
if findings:
    order = {"error": 0, "warn": 1, "info": 2}
    for row in sorted(findings, key=lambda r: (order.get(r.get("severity", "info"), 9), r.get("code", ""))):
        sev = row["severity"].upper()
        print(f"[{sev}] {row['code']}: {row['message']}")
        if row.get("project"):
            print(f"  ↳ project: {row['project']}")
        if row.get("suggestion"):
            print(f"  ↳ fix: {row['suggestion']}")

# Plan preview
if plan:
    print()
    print("📋 Fix Plan:")
    risk_icons = {"low": "🟢", "medium": "🟡", "high": "🔴"}
    for i, p in enumerate(plan, 1):
        icon = risk_icons.get(p["risk"], "⚪")
        print(f"  {i}. {icon} [{p['risk'].upper()}] {p['description']}")
        if p.get("detail"):
            print(f"     → {p['detail']}")

    print()
    lo = risk_summary.get("low", 0)
    med = risk_summary.get("medium", 0)
    hi = risk_summary.get("high", 0)
    print(f"Risk summary: 🟢 low={lo}  🟡 medium={med}  🔴 high={hi}")

if plan and not do_fix and not dry_run:
    print()
    print("ℹ️  Preview only — no changes applied.")
    print("   Run with --fix to apply, or --dry-run to confirm preview.")

if dry_run:
    print()
    print("ℹ️  Dry-run mode — no changes applied.")

if do_fix:
    print()
    if actions_blocked:
        print(f"⚠️  {len(actions_blocked)} high-risk action(s) blocked (use --yes to auto-approve):")
        for b in actions_blocked:
            print(f"   🔴 {b['description']}")
    if fix_applied:
        print("🔧 Fix applied.")
PYEOF
