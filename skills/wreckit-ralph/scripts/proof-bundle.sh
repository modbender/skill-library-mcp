#!/usr/bin/env bash
# wreckit — Proof Bundle writer
# Reads gate results from stdin (JSON array) and writes .wreckit/ folder
# Usage: cat gate-results.json | ./proof-bundle.sh [project-path] [mode] [verdict]
# Output: .wreckit/proof.json, .wreckit/dashboard.json, .wreckit/decision.md

set -euo pipefail
PROJECT="${1:-.}"
MODE="${2:-AUDIT}"
VERDICT="${3:-}"

mkdir -p "$PROJECT/.wreckit"

GATES_INPUT_FILE="$(mktemp)"
cat > "$GATES_INPUT_FILE"

python3 - "$PROJECT" "$MODE" "$VERDICT" "$GATES_INPUT_FILE" <<'PYEOF'
import datetime
import json
import os
import subprocess
import sys
import uuid
from typing import Any, Dict, List, Optional, Tuple

project, mode, verdict_arg, gates_input_file = sys.argv[1:]
try:
    with open(gates_input_file, "r", encoding="utf-8") as fh:
        raw = fh.read().strip()
except Exception:
    raw = ""

if not raw:
    gates_input = []
else:
    try:
        gates_input = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON on stdin"}))
        sys.exit(1)

if not isinstance(gates_input, list):
    print(json.dumps({"error": "Gate results must be a JSON array"}))
    sys.exit(1)

now = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
run_id = str(uuid.uuid4())

try:
    git_sha = subprocess.check_output(["git", "-C", project, "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
except Exception:
    git_sha = None


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _normalize_status(value: Any) -> str:
    status_up = str(value or "UNKNOWN").upper()
    if status_up == "SKIPPED":
        return "SKIP"
    if status_up == "BLOCKED":
        return "FAIL"
    if status_up == "SHIP":
        return "PASS"
    return status_up


def _load_project_profile(project_path: str) -> Dict[str, Any]:
    fallback = {
        "type": "unknown",
        "confidence": 0.0,
        "signals": ["profile_missing"],
        "calibration": {
            "slop_per_kloc": 5,
            "god_module_fanin": 10,
            "ci_required": False,
            "coverage_min": 70,
            "skip_gates": [],
            "tolerated_warns": [],
        },
    }

    candidates = []
    env_path = os.environ.get("WRECKIT_PROJECT_PROFILE_FILE")
    if env_path:
        candidates.append(env_path)
    candidates.append(os.path.join(project_path, ".wreckit", "project-type.json"))

    for c in candidates:
        if not c:
            continue
        try:
            with open(c, "r", encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict) and "type" in d:
                return d
        except Exception:
            continue
    return fallback


project_profile = _load_project_profile(project)
project_type = str(project_profile.get("type", "unknown"))
calibration = project_profile.get("calibration", {}) if isinstance(project_profile.get("calibration", {}), dict) else {}

# Normalize gate results
gates: List[Dict[str, Any]] = []
normalized: Dict[str, Dict[str, Any]] = {}
mutation_rate: Optional[float] = None

for item in gates_input:
    if not isinstance(item, dict):
        continue

    name = item.get("gate") or item.get("name") or item.get("id") or "unknown"
    status = _normalize_status(item.get("status") or item.get("verdict") or item.get("result"))
    confidence = _to_float(item.get("confidence", 0.0), 0.0)

    row = {
        "gate": name,
        "status": status,
        "confidence": confidence,
        "raw": item,
    }
    gates.append(row)
    normalized[name] = {
        "verdict": status,
        "score": item.get("score"),
        "confidence": confidence,
        "raw": item,
    }

    if name.lower() in {"mutation", "mutation_kill", "mutation-kill", "mutation_test", "mutationtest"}:
        rate = item.get("killRate") or item.get("kill_rate") or item.get("mutation_kill") or item.get("mutation_kill_rate")
        if rate is not None:
            parsed = _to_float(rate, -1.0)
            if parsed >= 0.0:
                mutation_rate = parsed

mutation_rate_fraction = None
if mutation_rate is not None:
    mutation_rate_fraction = mutation_rate / 100.0 if mutation_rate > 1.5 else mutation_rate


def gate_by_name(name: str) -> Optional[Dict[str, Any]]:
    for g in gates:
        if g.get("gate") == name:
            return g
    return None


BASE_WEIGHTS = {
    "check_deps": 1.2,
    "slop_scan": 1.0,
    "type_check": 1.1,
    "coverage_stats": 0.8,
    "red_team": 1.0,
    "regex_complexity": 0.7,
    "design_review": 0.9,
    "ci_integration": 0.8,
    "ralph_loop": 0.8,
    "mutation_test": 1.1,
}

TYPE_DELTAS = {
    "library": {"type_check": 0.35, "design_review": 0.2, "ci_integration": -0.2},
    "app": {"ci_integration": 0.35, "red_team": 0.25, "coverage_stats": 0.2},
    "ai-generated": {"check_deps": 0.35, "slop_scan": 0.4, "type_check": 0.25},
    "monorepo": {"design_review": 0.35, "check_deps": 0.2, "ci_integration": 0.2},
}

GATE_DOMAINS = {
    "check_deps": "dependencies",
    "slop_scan": "code_quality",
    "type_check": "correctness",
    "coverage_stats": "testing",
    "mutation_test": "testing",
    "red_team": "security",
    "regex_complexity": "security",
    "design_review": "architecture",
    "ci_integration": "delivery",
    "ralph_loop": "planning",
}


def weight_for_gate(gate_name: str) -> float:
    base = BASE_WEIGHTS.get(gate_name, 0.9)
    delta = TYPE_DELTAS.get(project_type, {}).get(gate_name, 0.0)
    weight = base + delta
    return max(0.3, min(2.0, round(weight, 3)))


def domain_for_gate(gate_name: str) -> str:
    return GATE_DOMAINS.get(gate_name, "misc")


hard_blocks: List[str] = []
hard_block_reasons: List[str] = []
hard_block_confs: List[float] = []


def add_hard_block(gate: str, reason: str, confidence: float) -> None:
    if gate not in hard_blocks:
        hard_blocks.append(gate)
    hard_block_reasons.append(reason)
    hard_block_confs.append(max(0.0, min(1.0, confidence)))


check_deps_gate = gate_by_name("check_deps")
if check_deps_gate and check_deps_gate.get("status") == "FAIL":
    raw_deps = check_deps_gate.get("raw", {})
    findings = _to_int(raw_deps.get("findings", 0), 0)
    hallucinated = raw_deps.get("hallucinated", [])
    confirmed = findings > 0 or (isinstance(hallucinated, list) and len(hallucinated) > 0)
    if confirmed and check_deps_gate.get("confidence", 0.0) >= 0.9:
        add_hard_block("check_deps", "Critical: hallucinated dependency confirmed", check_deps_gate.get("confidence", 1.0))

type_check_gate = gate_by_name("type_check")
if type_check_gate and type_check_gate.get("status") == "FAIL":
    errors = _to_int(type_check_gate.get("raw", {}).get("errors", 0), 0)
    if errors > 0:
        add_hard_block("type_check", f"Critical: type_check reports {errors} error(s)", max(type_check_gate.get("confidence", 1.0), 0.95))

slop_gate = gate_by_name("slop_scan")
if slop_gate and slop_gate.get("status") == "FAIL":
    raw_slop = slop_gate.get("raw", {})
    density = raw_slop.get("density_per_kloc")
    threshold = raw_slop.get("threshold_per_kloc")
    density = _to_float(density, -1.0)
    threshold = _to_float(threshold, -1.0)
    if density >= 0 and threshold > 0 and density > (3.0 * threshold):
        add_hard_block("slop_scan", f"Critical: slop density {density:.2f}/KLOC > 3x threshold {threshold:.2f}", max(slop_gate.get("confidence", 1.0), 0.95))

# Evidence aggregation for non-hard failures
soft_fails: List[Dict[str, Any]] = []
warn_high: List[Dict[str, Any]] = []

for g in gates:
    name = g.get("gate", "unknown")
    status = g.get("status")
    conf = max(0.0, min(1.0, _to_float(g.get("confidence", 0.0), 0.0)))

    if status == "FAIL" and name in hard_blocks:
        continue

    if status in {"FAIL", "ERROR"}:
        confidence_used = conf if conf > 0 else 0.6
        weight = weight_for_gate(name)
        soft_fails.append({
            "gate": name,
            "status": status,
            "domain": domain_for_gate(name),
            "confidence": confidence_used,
            "weight": weight,
            "evidence": round(confidence_used * weight, 4),
        })
    elif status == "WARN" and conf >= 0.5:
        warn_high.append(g)

mutation_warnings: List[str] = []
if mutation_rate is not None:
    if mutation_rate < 90:
        confidence_used = 0.95
        weight = weight_for_gate("mutation_test")
        soft_fails.append({
            "gate": "mutation_test",
            "status": "FAIL",
            "domain": domain_for_gate("mutation_test"),
            "confidence": confidence_used,
            "weight": weight,
            "evidence": round(confidence_used * weight, 4),
            "reason": f"mutation kill rate {mutation_rate:.1f}% (<90)",
        })
    elif mutation_rate < 95:
        mutation_warnings.append(f"mutation kill rate {mutation_rate:.1f}% (90-94 caution)")

corroborating_signals = len(soft_fails)
weighted_evidence = round(sum(_to_float(x.get("evidence", 0.0), 0.0) for x in soft_fails), 4)
corroborating_domains = sorted({str(x.get("domain", "misc")) for x in soft_fails})
corroborating_domain_count = len(corroborating_domains)
avg_soft_confidence = round((sum(_to_float(x.get("confidence", 0.0), 0.0) for x in soft_fails) / corroborating_signals), 4) if corroborating_signals > 0 else 0.0

# Count status buckets
passed = warned = failed = skipped = 0
for g in gates:
    verdict = g.get("status")
    if verdict == "PASS":
        passed += 1
    elif verdict == "WARN":
        warned += 1
    elif verdict in {"FAIL", "ERROR"}:
        failed += 1
    elif verdict == "SKIP":
        skipped += 1

executed_gates = passed + warned + failed
dissenting_signals = max(0, executed_gates - corroborating_signals - len(hard_blocks))

blockers: List[str] = []
warnings: List[str] = []
verdict_reasoning = ""
verdict_confidence = 1.0

mode_up = str(mode or "AUDIT").upper()
mutation_expected = mode_up in {"BUILD", "REBUILD", "FIX"}

if verdict_arg:
    verdict = verdict_arg.upper()
    verdict_reasoning = f"Override: {verdict_arg}"
    verdict_confidence = 1.0
else:
    if hard_blocks:
        verdict = "BLOCKED"
        verdict_reasoning = hard_block_reasons[0]
        verdict_confidence = max(hard_block_confs) if hard_block_confs else 1.0
    elif (
        corroborating_signals >= 2
        and weighted_evidence >= 1.4
        and corroborating_domain_count >= 2
        and avg_soft_confidence >= 0.65
    ):
        verdict = "BLOCKED"
        verdict_reasoning = (
            f"{corroborating_signals} corroborating failures across {corroborating_domain_count} domains "
            f"(weighted evidence {weighted_evidence:.2f}, avg confidence {avg_soft_confidence:.2f})"
        )
        verdict_confidence = min(0.95, 0.55 + (weighted_evidence / 3.0))
    elif corroborating_signals >= 1:
        verdict = "CAUTION"
        verdict_reasoning = f"{corroborating_signals} gate(s) failed; corroboration below block threshold"
        verdict_confidence = min(0.85, 0.45 + (weighted_evidence / 4.0))
    elif warn_high or mutation_warnings:
        verdict = "CAUTION"
        verdict_reasoning = f"{len(warn_high) + len(mutation_warnings)} cautionary warning signal(s)"
        max_warn_conf = max([_to_float(w.get("confidence", 0.5), 0.5) for w in warn_high], default=0.5)
        verdict_confidence = min(0.8, max_warn_conf)
    elif mutation_rate is None and mutation_expected:
        verdict = "CAUTION"
        verdict_reasoning = "mutation kill rate missing in mutation-required mode"
        verdict_confidence = 0.55
        warnings.append("mutation kill rate missing in mutation-required mode")
    else:
        verdict = "SHIP"
        verdict_reasoning = "No corroborated failures; no hard blocks"
        verdict_confidence = 0.9

if hard_block_reasons:
    blockers.extend(hard_block_reasons)
if soft_fails:
    warnings.append(
        f"{corroborating_signals} non-hard fail signal(s) across {corroborating_domain_count} domain(s); "
        f"weighted evidence={weighted_evidence:.2f}; avg confidence={avg_soft_confidence:.2f}"
    )
if warn_high:
    warnings.append(f"{len(warn_high)} high-confidence WARN gate(s)")
if mutation_warnings:
    warnings.extend(mutation_warnings)

# Score formula
eligible = max(0, (passed + warned + failed) - skipped)
if eligible == 0:
    score = 0
else:
    score = int(((passed + (0.5 * warned)) / eligible) * 100)
score = max(0, min(100, score))
if blockers:
    score = 0

proof = {
    "wreckit_version": "2.1.0",
    "run_id": run_id,
    "timestamp": now,
    "mode": mode,
    "project": os.path.abspath(project),
    "git_sha": git_sha,
    "project_type": {
        "type": project_type,
        "confidence": _to_float(project_profile.get("confidence", 0.0), 0.0),
        "signals": project_profile.get("signals", []),
    },
    "calibration": calibration,
    "gates": normalized,
    "verdict": verdict.title(),
    "verdict_reasoning": verdict_reasoning,
    "corroborating_signals": corroborating_signals,
    "corroborating_domains": corroborating_domains,
    "dissenting_signals": dissenting_signals,
    "hard_blocks": hard_blocks,
    "soft_fails": [g.get("gate") for g in soft_fails],
    "aggregation": {
        "weighted_evidence": weighted_evidence,
        "avg_soft_confidence": avg_soft_confidence,
        "corroborating_domains": corroborating_domains,
        "required_domains": 2,
        "block_threshold": 1.4,
        "required_corroborating_fails": 2,
        "min_avg_soft_confidence": 0.65,
        "gate_weights": {g.get("gate"): g.get("weight") for g in soft_fails},
    },
    "confidence": round(float(verdict_confidence), 4),
    "blockers": blockers,
    "warnings": warnings,
    "score": score,
}

verdict_emoji = "✅" if verdict == "SHIP" else ("⚠️" if verdict == "CAUTION" else "🚫")

dashboard = {
    "verdict": verdict.title(),
    "verdict_emoji": verdict_emoji,
    "score": score,
    "gates_passed": passed,
    "gates_failed": failed,
    "gates_warned": warned,
    "gates_skipped": skipped,
    "mutation_kill_rate": mutation_rate_fraction,
    "run_id": run_id,
    "timestamp": now,
    "project_type": project_type,
}

project_wreckit = os.path.join(project, ".wreckit")
with open(os.path.join(project_wreckit, "proof.json"), "w", encoding="utf-8") as f:
    json.dump(proof, f, indent=2)

with open(os.path.join(project_wreckit, "dashboard.json"), "w", encoding="utf-8") as f:
    json.dump(dashboard, f, indent=2)

# decision.md
lines = [
    f"# Verdict: {verdict.title()} {verdict_emoji}",
    "",
    "## Decision Date",
    now,
    "",
]

if blockers:
    lines += ["## Blocking Gates"]
    for b in blockers:
        lines.append(f"- {b}")
    lines.append("")

if warnings:
    lines += ["## Warning Gates"]
    for w in warnings:
        lines.append(f"- {w}")
    lines.append("")

lines += [
    "## Gate Summary",
    f"- Passed: {passed}",
    f"- Warned: {warned}",
    f"- Failed: {failed}",
    f"- Skipped: {skipped}",
    f"- Corroborating fail signals: {corroborating_signals}",
    f"- Corroborating domains: {', '.join(corroborating_domains) if corroborating_domains else 'none'}",
    f"- Dissenting signals: {dissenting_signals}",
    f"- Weighted evidence: {weighted_evidence}",
    f"- Avg soft-fail confidence: {avg_soft_confidence}",
    "",
]
lines += [
    "## Verdict Criteria Applied",
    "Ship: no hard blocks and no corroborated fail evidence above block threshold.",
    "Caution: single non-hard fail, warning-only signals, or evidence below corroboration threshold.",
    "Blocked: any hard block OR at least 2 corroborating non-hard failures across >=2 domains with weighted evidence >= 1.4 and avg confidence >= 0.65.",
    "Hard blocks are deterministic critical failures (e.g., confirmed hallucinated deps, real type errors, extreme slop density).",
    "",
]

with open(os.path.join(project_wreckit, "decision.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(verdict)
PYEOF

rm -f "$GATES_INPUT_FILE"
