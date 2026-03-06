from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from benchmark import ContinuityBenchmarkHarness, ContinuityRun
from policy import (
    COMPACTION_POLICY_ATTENTION_PRESERVING_EXPERIMENTAL,
    COMPACTION_POLICY_SIZE_ONLY,
    SELECTOR_MODE_DETERMINISTIC,
    SELECTOR_MODE_DUAL_ROUTE_EXPERIMENTAL,
    normalize_compaction_policy,
    normalize_selector_mode,
)


SHADOW_EVAL_SCHEMA_VERSION = "v1"
DEFAULT_APPEND_NOTES = "Eval results from shadowed mode deployments. Updated by Anvil after each sprint review."
SUITE_CORE_SHADOW = "core-shadow"
SUITE_MEMORYARENA_MINI = "memoryarena-mini"
SUITE_MEMORYARENA_MINI_PERTURB = "memoryarena-mini-perturb"
DEFAULT_SUITE = SUITE_MEMORYARENA_MINI
SUPPORTED_SUITES = frozenset({SUITE_CORE_SHADOW, SUITE_MEMORYARENA_MINI, SUITE_MEMORYARENA_MINI_PERTURB})

PERTURB_PROFILE_NONE = "none"
PERTURB_PROFILE_DELETION = "deletion"
PERTURB_PROFILE_NOISE_INJECTION = "noise_injection"
PERTURB_PROFILE_REORDER = "reorder"
DEFAULT_PERTURB_PROFILE = PERTURB_PROFILE_NONE
SUPPORTED_PERTURB_PROFILES = frozenset(
    {
        PERTURB_PROFILE_NONE,
        PERTURB_PROFILE_DELETION,
        PERTURB_PROFILE_NOISE_INJECTION,
        PERTURB_PROFILE_REORDER,
    }
)

ROLLING_CALIBRATION_WINDOW = 5

QUALITY_THRESHOLDS = {
    "resume_success_rate": {"operator": ">=", "value": 95.0},
    "reprompt_rate": {"operator": "<=", "value": 5.0},
    "off_goal_tool_call_rate": {"operator": "<=", "value": 3.0},
    "continuity_lift_delta": {"operator": ">=", "value": 5.0},
    "incorrect_accept_rate": {"operator": "<=", "value": 5.0},
    "incorrect_reject_rate": {"operator": "<=", "value": 5.0},
    "runtime_state_fingerprint_drift_rate": {"operator": "==", "value": 0.0},
}


@dataclass(frozen=True)
class ShadowEvalTask:
    task_id: str
    continuity_difficulty: float
    distractor_pressure: float
    context_shift: float
    verification_risk: float


@dataclass(frozen=True)
class ParsedTraceOutcome:
    variant: str
    suite: str
    perturb_profile: str
    selector_mode: str
    compaction_policy: str
    trace_id: str
    run_index: int
    task_id: str
    resumed_successfully: bool
    reprompted: bool
    off_goal_tool_call: bool
    duplicate_work: bool
    weak_check_score: float
    strong_check_triggered: bool
    incorrect_accept: bool
    incorrect_reject: bool
    dropped_fields_count: float
    runtime_state_fingerprint: str
    runtime_state_fingerprint_drift: bool
    local_score: float
    global_score: float
    chosen_fields: list[str]
    dropped_fields: list[str]
    source_name: str
    source_line: int


MEMORYARENA_MINI_TASKS = (
    ShadowEvalTask("resume-after-compaction", 0.35, 0.18, 0.28, 0.22),
    ShadowEvalTask("mission-lock-preservation", 0.31, 0.2, 0.3, 0.24),
    ShadowEvalTask("ticket-carry-forward", 0.37, 0.16, 0.36, 0.26),
    ShadowEvalTask("persona-consistency", 0.34, 0.22, 0.26, 0.21),
    ShadowEvalTask("handoff-context-merge", 0.46, 0.3, 0.44, 0.29),
    ShadowEvalTask("stale-memory-conflict", 0.56, 0.5, 0.46, 0.33),
    ShadowEvalTask("goal-drift-trap", 0.6, 0.7, 0.42, 0.45),
    ShadowEvalTask("tool-intent-ambiguity", 0.62, 0.62, 0.48, 0.5),
    ShadowEvalTask("constraint-overload", 0.58, 0.54, 0.5, 0.42),
    ShadowEvalTask("restart-rehydration", 0.5, 0.32, 0.62, 0.34),
    ShadowEvalTask("multi-hop-memory-retrieval", 0.55, 0.38, 0.66, 0.37),
    ShadowEvalTask("adversarial-side-quest", 0.67, 0.74, 0.54, 0.56),
)

CORE_SHADOW_TASKS = MEMORYARENA_MINI_TASKS[:8]

ABLATION_VARIANTS = (
    ("A_size_only", SELECTOR_MODE_DETERMINISTIC, COMPACTION_POLICY_SIZE_ONLY),
    (
        "B_dual_route_size_only",
        SELECTOR_MODE_DUAL_ROUTE_EXPERIMENTAL,
        COMPACTION_POLICY_SIZE_ONLY,
    ),
    (
        "C_dual_route_attention_preserving",
        SELECTOR_MODE_DUAL_ROUTE_EXPERIMENTAL,
        COMPACTION_POLICY_ATTENTION_PRESERVING_EXPERIMENTAL,
    ),
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100.0, 2)


def _hash_unit(seed: str) -> float:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    raw = int(digest[:16], 16)
    return raw / float(0xFFFFFFFFFFFFFFFF)


def _deterministic_digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _safe_fingerprint(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    stripped = value.strip().lower()
    if len(stripped) != 64:
        return ""
    if not all(ch in "0123456789abcdef" for ch in stripped):
        return ""
    return stripped


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except Exception:
        return default
    if out != out:  # NaN
        return default
    return out


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "y", "on"}:
            return True
        if normalized in {"0", "false", "no", "n", "off"}:
            return False
    return default


def _coerce_str_list(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        out = [str(item) for item in value]
        return sorted(set(out))
    return []


def _normalize_variant(value: Any, kernel_enabled: Any) -> str | None:
    if isinstance(value, str):
        lowered = value.strip().lower().replace("-", "_")
        if lowered in {"kernel", "candidate", "treatment", "enabled"}:
            return "kernel"
        if lowered in {"baseline", "control", "disabled"}:
            return "baseline"
    if isinstance(kernel_enabled, bool):
        return "kernel" if kernel_enabled else "baseline"
    return None


def _normalize_suite(suite: str) -> str:
    if isinstance(suite, str) and suite in SUPPORTED_SUITES:
        return suite
    return DEFAULT_SUITE


def _normalize_perturb_profile(perturb_profile: str, suite: str) -> str:
    suite_name = _normalize_suite(suite)
    if suite_name != SUITE_MEMORYARENA_MINI_PERTURB:
        return PERTURB_PROFILE_NONE

    if not isinstance(perturb_profile, str) or not perturb_profile.strip():
        return PERTURB_PROFILE_DELETION

    normalized = perturb_profile.strip().lower().replace("-", "_")
    aliases = {
        "delete": PERTURB_PROFILE_DELETION,
        "deletion": PERTURB_PROFILE_DELETION,
        "noise": PERTURB_PROFILE_NOISE_INJECTION,
        "noise_injection": PERTURB_PROFILE_NOISE_INJECTION,
        "reorder": PERTURB_PROFILE_REORDER,
        "reordered": PERTURB_PROFILE_REORDER,
        "none": PERTURB_PROFILE_NONE,
    }
    mapped = aliases.get(normalized, "")
    if mapped in {
        PERTURB_PROFILE_DELETION,
        PERTURB_PROFILE_NOISE_INJECTION,
        PERTURB_PROFILE_REORDER,
    }:
        return mapped

    # For perturb suite we default to deletion when input is unsupported/none.
    return PERTURB_PROFILE_DELETION


def _suite_tasks(suite: str) -> tuple[ShadowEvalTask, ...]:
    if suite == SUITE_CORE_SHADOW:
        return CORE_SHADOW_TASKS
    return MEMORYARENA_MINI_TASKS


def _perturb_penalty(perturb_profile: str) -> float:
    if perturb_profile == PERTURB_PROFILE_DELETION:
        return 0.1
    if perturb_profile == PERTURB_PROFILE_NOISE_INJECTION:
        return 0.08
    if perturb_profile == PERTURB_PROFILE_REORDER:
        return 0.07
    return 0.0


def _simulate_run(
    *,
    task: ShadowEvalTask,
    run_index: int,
    suite: str,
    perturb_profile: str,
    selector_mode: str,
    compaction_policy: str,
    kernel_enabled: bool,
) -> dict[str, Any]:
    noise = (_hash_unit(f"{suite}|{perturb_profile}|{task.task_id}|{run_index}|alignment") - 0.5) * 0.08

    base_alignment = (
        0.86
        - (0.33 * task.continuity_difficulty)
        - (0.24 * task.distractor_pressure)
        - (0.18 * task.context_shift)
    )

    if kernel_enabled:
        base_alignment += 0.17

    if kernel_enabled and selector_mode == SELECTOR_MODE_DUAL_ROUTE_EXPERIMENTAL:
        base_alignment += 0.03 * (0.5 + task.context_shift)

    if kernel_enabled and compaction_policy == COMPACTION_POLICY_ATTENTION_PRESERVING_EXPERIMENTAL:
        base_alignment += 0.02 * (0.5 + task.context_shift)

    if suite == SUITE_MEMORYARENA_MINI_PERTURB:
        penalty = _perturb_penalty(perturb_profile)
        if kernel_enabled:
            base_alignment -= penalty * 0.35
        else:
            base_alignment -= penalty * 1.25

    alignment = _clamp(base_alignment + noise, 0.0, 1.0)

    reprompt_threshold = 0.52 if kernel_enabled else 0.42
    off_goal_threshold = 0.51 if kernel_enabled else 0.39
    duplicate_threshold = 0.54 if kernel_enabled else 0.45

    reprompted = alignment < reprompt_threshold
    off_goal = alignment < off_goal_threshold and task.distractor_pressure >= 0.45
    duplicate = alignment < duplicate_threshold and task.context_shift >= 0.4
    resumed_successfully = not (reprompted or off_goal)

    weak_noise = (_hash_unit(f"{suite}|{perturb_profile}|{task.task_id}|{run_index}|weak") - 0.5) * 0.06
    weak_score = _clamp(
        (0.42 + (0.58 * alignment) - (0.18 * task.verification_risk) + weak_noise),
        0.0,
        1.0,
    )
    strong_check_triggered = bool(off_goal or (0.42 <= weak_score <= 0.58))

    should_accept = resumed_successfully and not off_goal
    weak_accept = weak_score >= 0.5

    incorrect_accept = weak_accept and not should_accept
    incorrect_reject = (not weak_accept) and should_accept

    dropped_noise = (_hash_unit(f"{suite}|{perturb_profile}|{task.task_id}|{run_index}|dropped") - 0.5) * 0.8
    dropped_fields = 2.8 + (2.2 * task.continuity_difficulty) + (1.4 * task.context_shift) + dropped_noise
    if kernel_enabled:
        dropped_fields -= 0.4
    if kernel_enabled and compaction_policy == COMPACTION_POLICY_ATTENTION_PRESERVING_EXPERIMENTAL:
        dropped_fields -= 0.9
    if suite == SUITE_MEMORYARENA_MINI_PERTURB:
        dropped_fields += _perturb_penalty(perturb_profile) * (1.8 if not kernel_enabled else 0.8)
    dropped_fields = max(0.0, dropped_fields)

    local_noise = (_hash_unit(f"{suite}|{perturb_profile}|{task.task_id}|{run_index}|local") - 0.5) * 0.1
    global_noise = (_hash_unit(f"{suite}|{perturb_profile}|{task.task_id}|{run_index}|global") - 0.5) * 0.1

    local_score = _clamp(0.34 + (0.62 * alignment) + local_noise, 0.0, 1.0)
    global_score = _clamp(
        0.4
        + (0.5 * alignment)
        + (0.08 if selector_mode == SELECTOR_MODE_DUAL_ROUTE_EXPERIMENTAL else 0.0)
        + global_noise,
        0.0,
        1.0,
    )

    if selector_mode == SELECTOR_MODE_DUAL_ROUTE_EXPERIMENTAL:
        chosen_fields = [
            "mission",
            "definition_of_done",
            "mission_constraints",
            "role",
            "soul_constraints",
            "persona",
        ]
    else:
        chosen_fields = [
            "mission",
            "definition_of_done",
            "role",
            "persona",
            "mission_constraints",
        ]

    if compaction_policy == COMPACTION_POLICY_ATTENTION_PRESERVING_EXPERIMENTAL:
        dropped_fields_set = ["preferences"]
    else:
        dropped_fields_set = ["preferences", "user_profile"]

    fingerprint_seed = f"{suite}|{perturb_profile}|{task.task_id}|runtime_state|v1"
    runtime_state_fingerprint = hashlib.sha256(fingerprint_seed.encode("utf-8")).hexdigest() if kernel_enabled else ""

    return {
        "task_id": task.task_id,
        "resumed_successfully": resumed_successfully,
        "reprompted": reprompted,
        "off_goal_tool_call": off_goal,
        "duplicate_work": duplicate,
        "weak_check_score": round(weak_score, 3),
        "strong_check_triggered": strong_check_triggered,
        "incorrect_accept": incorrect_accept,
        "incorrect_reject": incorrect_reject,
        "dropped_fields_count": round(dropped_fields, 2),
        "runtime_state_fingerprint": runtime_state_fingerprint,
        "runtime_state_fingerprint_drift": False,
        "local_score": round(local_score, 3),
        "global_score": round(global_score, 3),
        "chosen_fields": chosen_fields,
        "dropped_fields": dropped_fields_set,
    }


def evaluate_shadow_suite(
    *,
    suite: str,
    runs: int,
    selector_mode: str,
    compaction_policy: str,
    kernel_enabled: bool,
    perturb_profile: str = DEFAULT_PERTURB_PROFILE,
) -> list[dict[str, Any]]:
    suite_name = _normalize_suite(suite)
    profile = _normalize_perturb_profile(perturb_profile, suite_name)
    tasks = _suite_tasks(suite_name)
    total_runs = max(1, int(runs))
    compaction_mode, _ = normalize_compaction_policy(compaction_policy)

    outcomes: list[dict[str, Any]] = []
    for run_index in range(total_runs):
        task = tasks[run_index % len(tasks)]
        outcome = _simulate_run(
            task=task,
            run_index=run_index,
            suite=suite_name,
            perturb_profile=profile,
            selector_mode=selector_mode,
            compaction_policy=compaction_mode,
            kernel_enabled=kernel_enabled,
        )
        outcome["run_index"] = run_index
        outcome["trace_id"] = f"{suite_name}:{profile}:{run_index}:{task.task_id}"
        outcome["perturb_profile"] = profile
        outcomes.append(outcome)

    return outcomes


def _to_runs(outcomes: list[dict[str, Any]]) -> list[ContinuityRun]:
    return [
        ContinuityRun(
            resumed_successfully=bool(item.get("resumed_successfully", False)),
            reprompted=bool(item.get("reprompted", False)),
            off_goal_tool_call=bool(item.get("off_goal_tool_call", False)),
            duplicate_work=bool(item.get("duplicate_work", False)),
        )
        for item in outcomes
    ]


def _threshold_pass(metric: str, value: float) -> bool:
    threshold = QUALITY_THRESHOLDS[metric]
    operator = threshold["operator"]
    threshold_value = float(threshold["value"])

    if operator == ">=":
        return value >= threshold_value
    if operator == "<=":
        return value <= threshold_value
    if operator == "==":
        return abs(value - threshold_value) < 1e-9
    return False


def _trace_paths(
    trace_jsonl_paths: list[str | Path] | None,
    trace_dirs: list[str | Path] | None,
) -> list[Path]:
    out: list[Path] = []

    for raw in trace_jsonl_paths or []:
        path = Path(raw).expanduser()
        if path.exists() and path.is_file():
            out.append(path.resolve())

    for raw in trace_dirs or []:
        directory = Path(raw).expanduser()
        if not directory.exists() or not directory.is_dir():
            continue
        for candidate in sorted(directory.glob("*.jsonl")):
            if candidate.is_file():
                out.append(candidate.resolve())

    deduped: list[Path] = []
    seen: set[str] = set()
    for path in out:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(path)
    return deduped


def _parse_trace_outcome(
    raw: Any,
    *,
    source_name: str,
    source_line: int,
    default_suite: str,
) -> ParsedTraceOutcome | None:
    if not isinstance(raw, dict):
        return None

    nested = raw.get("outcome")
    outcome_payload = nested if isinstance(nested, dict) else raw

    variant = _normalize_variant(
        raw.get("variant") if "variant" in raw else outcome_payload.get("variant"),
        raw.get("kernel_enabled") if "kernel_enabled" in raw else outcome_payload.get("kernel_enabled"),
    )
    if variant is None:
        return None

    suite_raw = raw.get("suite") if isinstance(raw.get("suite"), str) else outcome_payload.get("suite")
    suite_name = _normalize_suite(str(suite_raw)) if isinstance(suite_raw, str) else _normalize_suite(default_suite)

    perturb_raw = (
        raw.get("perturb_profile")
        if isinstance(raw.get("perturb_profile"), str)
        else outcome_payload.get("perturb_profile")
    )
    perturb_profile = _normalize_perturb_profile(
        str(perturb_raw) if isinstance(perturb_raw, str) else DEFAULT_PERTURB_PROFILE,
        suite_name,
    )

    selector_input = (
        raw.get("selector_mode")
        if isinstance(raw.get("selector_mode"), str)
        else outcome_payload.get("selector_mode")
    )
    selector_mode, _ = normalize_selector_mode(selector_input)

    compaction_input = (
        raw.get("compaction_policy")
        if isinstance(raw.get("compaction_policy"), str)
        else outcome_payload.get("compaction_policy")
    )
    compaction_policy, _ = normalize_compaction_policy(compaction_input)

    run_index = _coerce_int(
        raw.get("run_index") if raw.get("run_index") is not None else outcome_payload.get("run_index"),
        default=max(0, source_line - 1),
    )

    task_id_raw = raw.get("task_id") if isinstance(raw.get("task_id"), str) else outcome_payload.get("task_id")
    task_id = str(task_id_raw or f"trace-task-{run_index}")

    trace_id_raw = raw.get("trace_id") if raw.get("trace_id") is not None else outcome_payload.get("trace_id")
    if isinstance(trace_id_raw, str) and trace_id_raw.strip():
        trace_id = trace_id_raw.strip()
    else:
        trace_id = f"{suite_name}:{perturb_profile}:{max(0, run_index)}:{task_id}"

    weak_check_score = _clamp(_coerce_float(outcome_payload.get("weak_check_score"), default=0.0), 0.0, 1.0)
    dropped_fields = max(0.0, _coerce_float(outcome_payload.get("dropped_fields_count"), default=0.0))

    runtime_state_fingerprint = _safe_fingerprint(outcome_payload.get("runtime_state_fingerprint", ""))
    drift_flag_raw = outcome_payload.get("runtime_state_fingerprint_drift")
    runtime_state_fingerprint_drift = _coerce_bool(drift_flag_raw, default=False)

    expected_fp = _safe_fingerprint(outcome_payload.get("expected_runtime_state_fingerprint", ""))
    if runtime_state_fingerprint and expected_fp:
        runtime_state_fingerprint_drift = runtime_state_fingerprint != expected_fp

    local_score = _clamp(_coerce_float(outcome_payload.get("local_score"), default=0.0), 0.0, 1.0)
    global_score = _clamp(_coerce_float(outcome_payload.get("global_score"), default=0.0), 0.0, 1.0)

    return ParsedTraceOutcome(
        variant=variant,
        suite=suite_name,
        perturb_profile=perturb_profile,
        selector_mode=selector_mode,
        compaction_policy=compaction_policy,
        trace_id=trace_id,
        run_index=max(0, run_index),
        task_id=task_id,
        resumed_successfully=_coerce_bool(outcome_payload.get("resumed_successfully"), default=False),
        reprompted=_coerce_bool(outcome_payload.get("reprompted"), default=False),
        off_goal_tool_call=_coerce_bool(outcome_payload.get("off_goal_tool_call"), default=False),
        duplicate_work=_coerce_bool(outcome_payload.get("duplicate_work"), default=False),
        weak_check_score=round(weak_check_score, 3),
        strong_check_triggered=_coerce_bool(outcome_payload.get("strong_check_triggered"), default=False),
        incorrect_accept=_coerce_bool(outcome_payload.get("incorrect_accept"), default=False),
        incorrect_reject=_coerce_bool(outcome_payload.get("incorrect_reject"), default=False),
        dropped_fields_count=round(dropped_fields, 2),
        runtime_state_fingerprint=runtime_state_fingerprint,
        runtime_state_fingerprint_drift=runtime_state_fingerprint_drift,
        local_score=round(local_score, 3),
        global_score=round(global_score, 3),
        chosen_fields=_coerce_str_list(outcome_payload.get("chosen_fields")),
        dropped_fields=_coerce_str_list(outcome_payload.get("dropped_fields")),
        source_name=source_name,
        source_line=max(1, source_line),
    )


def _to_outcome_dict(parsed: ParsedTraceOutcome) -> dict[str, Any]:
    return {
        "trace_id": parsed.trace_id,
        "task_id": parsed.task_id,
        "run_index": parsed.run_index,
        "perturb_profile": parsed.perturb_profile,
        "resumed_successfully": parsed.resumed_successfully,
        "reprompted": parsed.reprompted,
        "off_goal_tool_call": parsed.off_goal_tool_call,
        "duplicate_work": parsed.duplicate_work,
        "weak_check_score": parsed.weak_check_score,
        "strong_check_triggered": parsed.strong_check_triggered,
        "incorrect_accept": parsed.incorrect_accept,
        "incorrect_reject": parsed.incorrect_reject,
        "dropped_fields_count": parsed.dropped_fields_count,
        "runtime_state_fingerprint": parsed.runtime_state_fingerprint,
        "runtime_state_fingerprint_drift": parsed.runtime_state_fingerprint_drift,
        "local_score": parsed.local_score,
        "global_score": parsed.global_score,
        "chosen_fields": parsed.chosen_fields,
        "dropped_fields": parsed.dropped_fields,
        "trace_source": parsed.source_name,
        "trace_line": parsed.source_line,
    }


def _stable_pair_key(record: ParsedTraceOutcome) -> str:
    if record.trace_id:
        return f"trace:{record.trace_id}"
    return f"task:{record.run_index}:{record.task_id}"


def _unique_by_pair_key(records: list[ParsedTraceOutcome]) -> list[ParsedTraceOutcome]:
    ordered = sorted(
        records,
        key=lambda r: (
            r.run_index,
            r.task_id,
            r.trace_id,
            r.source_name,
            r.source_line,
        ),
    )
    out: list[ParsedTraceOutcome] = []
    seen: set[str] = set()
    for item in ordered:
        key = _stable_pair_key(item)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _index_by_pair_key(records: list[ParsedTraceOutcome]) -> dict[str, ParsedTraceOutcome]:
    out: dict[str, ParsedTraceOutcome] = {}
    for item in _unique_by_pair_key(records):
        out[_stable_pair_key(item)] = item
    return out


def _collect_variant_candidates(
    records: list[ParsedTraceOutcome],
    selector_mode: str,
    compaction_policy: str,
) -> list[ParsedTraceOutcome]:
    return [
        item
        for item in records
        if item.variant == "kernel"
        and item.selector_mode == selector_mode
        and item.compaction_policy == compaction_policy
    ]


def _ablation_indices(records: list[ParsedTraceOutcome]) -> dict[str, dict[str, ParsedTraceOutcome]]:
    out: dict[str, dict[str, ParsedTraceOutcome]] = {}
    for variant_id, selector_mode, compaction_policy in ABLATION_VARIANTS:
        out[variant_id] = _index_by_pair_key(_collect_variant_candidates(records, selector_mode, compaction_policy))
    return out


def _load_trace_dataset(
    *,
    suite: str,
    perturb_profile: str,
    runs: int,
    selector_mode: str,
    compaction_policy: str,
    trace_jsonl_paths: list[str | Path] | None,
    trace_dirs: list[str | Path] | None,
) -> dict[str, Any] | None:
    trace_paths = _trace_paths(trace_jsonl_paths=trace_jsonl_paths, trace_dirs=trace_dirs)
    if not trace_paths:
        return None

    parsed_records: list[ParsedTraceOutcome] = []
    for path in trace_paths:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        for line_no, line in enumerate(text.splitlines(), start=1):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            try:
                raw = json.loads(line_stripped)
            except Exception:
                continue
            parsed = _parse_trace_outcome(
                raw,
                source_name=path.name,
                source_line=line_no,
                default_suite=suite,
            )
            if parsed is None:
                continue
            if parsed.suite != suite:
                continue
            if parsed.perturb_profile != perturb_profile:
                continue
            parsed_records.append(parsed)

    if not parsed_records:
        raise ValueError("No parseable trace outcomes found for selected suite/perturb profile.")

    kernel_candidates = _collect_variant_candidates(parsed_records, selector_mode, compaction_policy)
    baseline_candidates = [item for item in parsed_records if item.variant == "baseline"]
    size_only_kernel_candidates = _collect_variant_candidates(parsed_records, selector_mode, COMPACTION_POLICY_SIZE_ONLY)

    if not kernel_candidates:
        raise ValueError("Trace dataset does not contain kernel outcomes for requested selector/compaction policy.")
    if not baseline_candidates:
        raise ValueError("Trace dataset does not contain baseline outcomes.")

    kernel_unique = _unique_by_pair_key(kernel_candidates)
    baseline_index = _index_by_pair_key(baseline_candidates)
    size_only_index = _index_by_pair_key(size_only_kernel_candidates)

    aligned_keys = [_stable_pair_key(item) for item in kernel_unique if _stable_pair_key(item) in baseline_index]
    if not aligned_keys:
        raise ValueError("Trace dataset has no stable-key aligned kernel/baseline outcomes.")

    if compaction_policy != COMPACTION_POLICY_SIZE_ONLY:
        missing_size_only = [key for key in aligned_keys if key not in size_only_index]
        if missing_size_only:
            raise ValueError(
                "Observed trace dataset missing size_only kernel outcomes required for compaction A/B alignment."
            )

    requested_runs = max(1, int(runs))
    effective_runs = min(requested_runs, len(aligned_keys))
    keys_used = aligned_keys[:effective_runs]

    kernel_index = _index_by_pair_key(kernel_unique)
    kernel_outcomes = [_to_outcome_dict(kernel_index[key]) for key in keys_used]
    baseline_outcomes = [_to_outcome_dict(baseline_index[key]) for key in keys_used]

    if compaction_policy == COMPACTION_POLICY_SIZE_ONLY:
        size_only_outcomes = list(kernel_outcomes)
    else:
        size_only_outcomes = [_to_outcome_dict(size_only_index[key]) for key in keys_used]

    ablation_idx = _ablation_indices(parsed_records)
    require_full_ablation = suite == SUITE_MEMORYARENA_MINI_PERTURB
    if require_full_ablation:
        for key in keys_used:
            missing = [variant_id for variant_id, index in ablation_idx.items() if key not in index]
            if missing:
                raise ValueError(
                    "Observed trace dataset missing A/B/C compaction outcomes for perturb suite alignment."
                )
        ablation_keys = list(keys_used)
    else:
        ablation_keys = [key for key in keys_used if all(key in index for index in ablation_idx.values())]

    ablation_outcomes: dict[str, list[dict[str, Any]]] = {}
    for variant_id, index in ablation_idx.items():
        ablation_outcomes[variant_id] = [_to_outcome_dict(index[key]) for key in ablation_keys if key in index]

    return {
        "mode": "observed_trace",
        "trace_sources": [path.name for path in trace_paths],
        "trace_sources_full": [str(path) for path in trace_paths],
        "trace_records_total": len(parsed_records),
        "trace_records_used": {
            "kernel_candidate": len(kernel_outcomes),
            "baseline": len(baseline_outcomes),
            "kernel_size_only": len(size_only_outcomes),
        },
        "paired_keys": keys_used,
        "kernel_outcomes": kernel_outcomes,
        "baseline_outcomes": baseline_outcomes,
        "size_only_kernel_outcomes": size_only_outcomes,
        "compaction_baseline_source": "observed_trace",
        "ablation_outcomes": ablation_outcomes,
        "ablation_keys": ablation_keys,
        "ablation_require_full": require_full_ablation,
    }


def _variant_report(outcomes: list[dict[str, Any]]) -> dict[str, Any]:
    harness = ContinuityBenchmarkHarness()
    report = harness.evaluate(_to_runs(outcomes))
    avg_dropped_fields = round(
        sum(float(item.get("dropped_fields_count", 0.0)) for item in outcomes) / max(len(outcomes), 1),
        2,
    )
    return {
        "runs": len(outcomes),
        "resume_success_rate": float(report.resume_success_rate),
        "reprompt_rate": float(report.reprompt_rate),
        "off_goal_tool_call_rate": float(report.off_goal_tool_call_rate),
        "avg_dropped_fields": avg_dropped_fields,
    }


def _build_compaction_abc(
    *,
    suite: str,
    perturb_profile: str,
    runs: int,
    ablation_outcomes: dict[str, list[dict[str, Any]]] | None,
    require_complete: bool,
    source: str,
) -> dict[str, Any]:
    outcomes: dict[str, list[dict[str, Any]]] = {}

    if ablation_outcomes is not None:
        for variant_id, _, _ in ABLATION_VARIANTS:
            outcomes[variant_id] = list(ablation_outcomes.get(variant_id, []))

    target_runs = max(1, int(runs))
    for variant_id, selector_mode, compaction_policy in ABLATION_VARIANTS:
        variant_rows = outcomes.get(variant_id, [])
        if variant_rows:
            outcomes[variant_id] = variant_rows[:target_runs]
            continue

        if require_complete:
            raise ValueError("Missing required A/B/C ablation outcomes for perturb suite.")

        outcomes[variant_id] = evaluate_shadow_suite(
            suite=suite,
            perturb_profile=perturb_profile,
            runs=target_runs,
            selector_mode=selector_mode,
            compaction_policy=compaction_policy,
            kernel_enabled=True,
        )

    reports: dict[str, dict[str, Any]] = {}
    variants: list[dict[str, Any]] = []
    for variant_id, selector_mode, compaction_policy in ABLATION_VARIANTS:
        report = _variant_report(outcomes[variant_id])
        reports[variant_id] = report
        variants.append(
            {
                "id": variant_id,
                "selector_mode": selector_mode,
                "compaction_policy": compaction_policy,
                **report,
            }
        )

    a = reports["A_size_only"]
    b = reports["B_dual_route_size_only"]
    c = reports["C_dual_route_attention_preserving"]

    deltas = {
        "B_vs_A": {
            "resume_success_delta": round(b["resume_success_rate"] - a["resume_success_rate"], 2),
            "reprompt_delta": round(b["reprompt_rate"] - a["reprompt_rate"], 2),
            "off_goal_delta": round(b["off_goal_tool_call_rate"] - a["off_goal_tool_call_rate"], 2),
            "dropped_fields_delta": round(b["avg_dropped_fields"] - a["avg_dropped_fields"], 2),
        },
        "C_vs_A": {
            "resume_success_delta": round(c["resume_success_rate"] - a["resume_success_rate"], 2),
            "reprompt_delta": round(c["reprompt_rate"] - a["reprompt_rate"], 2),
            "off_goal_delta": round(c["off_goal_tool_call_rate"] - a["off_goal_tool_call_rate"], 2),
            "dropped_fields_delta": round(c["avg_dropped_fields"] - a["avg_dropped_fields"], 2),
        },
        "C_vs_B": {
            "resume_success_delta": round(c["resume_success_rate"] - b["resume_success_rate"], 2),
            "reprompt_delta": round(c["reprompt_rate"] - b["reprompt_rate"], 2),
            "off_goal_delta": round(c["off_goal_tool_call_rate"] - b["off_goal_tool_call_rate"], 2),
            "dropped_fields_delta": round(c["avg_dropped_fields"] - b["avg_dropped_fields"], 2),
        },
    }

    return {
        "source": source,
        "baseline_variant": "A_size_only",
        "variants": variants,
        "deltas": deltas,
    }


def _default_verification_calibration(evaluation_source: str, suite: str) -> dict[str, Any]:
    return {
        "method": "rolling_observed_trace_v1",
        "suite": suite,
        "window_size": ROLLING_CALIBRATION_WINDOW,
        "window_count": 0,
        "window_snapshot_digests": [],
        "weak_accept_threshold": 0.78,
        "weak_reject_threshold": 0.6,
        "incorrect_accept_rate_window_avg": 0.0,
        "incorrect_accept_rate_window_max": 0.0,
        "incorrect_reject_rate_window_avg": 0.0,
        "incorrect_reject_rate_window_max": 0.0,
        "bounded_error_window_pass": evaluation_source == "observed_trace",
    }


def _snapshot_digest(snapshot: dict[str, Any]) -> str:
    payload = {k: v for k, v in snapshot.items() if k not in {"generated_at", "deterministic_digest"}}
    return _deterministic_digest(payload)


def build_shadow_snapshot(
    layer: str,
    chunk: str,
    runs: int,
    suite: str = DEFAULT_SUITE,
    perturb_profile: str = DEFAULT_PERTURB_PROFILE,
    selector_mode: str = SELECTOR_MODE_DETERMINISTIC,
    compaction_policy: str = COMPACTION_POLICY_SIZE_ONLY,
    generated_at: str | None = None,
    trace_jsonl_paths: list[str | Path] | None = None,
    trace_dirs: list[str | Path] | None = None,
    allow_synthetic: bool = False,
) -> dict[str, Any]:
    requested_runs = max(1, int(runs))
    suite_name = _normalize_suite(suite)
    profile = _normalize_perturb_profile(perturb_profile, suite_name)
    mode, _ = normalize_selector_mode(selector_mode)
    compaction_mode, _ = normalize_compaction_policy(compaction_policy)

    observed_dataset = _load_trace_dataset(
        suite=suite_name,
        perturb_profile=profile,
        runs=requested_runs,
        selector_mode=mode,
        compaction_policy=compaction_mode,
        trace_jsonl_paths=trace_jsonl_paths,
        trace_dirs=trace_dirs,
    )

    if observed_dataset is not None:
        evaluation_source = "observed_trace"
        kernel_outcomes = list(observed_dataset["kernel_outcomes"])
        baseline_outcomes = list(observed_dataset["baseline_outcomes"])
        size_only_kernel_outcomes = list(observed_dataset["size_only_kernel_outcomes"])
        compaction_baseline_source = str(observed_dataset["compaction_baseline_source"])
        trace_sources = list(observed_dataset["trace_sources"])
        trace_sources_full = list(observed_dataset["trace_sources_full"])
        trace_records_total = int(observed_dataset["trace_records_total"])
        trace_records_used = dict(observed_dataset["trace_records_used"])
        ablation_outcomes = dict(observed_dataset.get("ablation_outcomes", {}))
        require_complete_ablation = bool(observed_dataset.get("ablation_require_full", False))
    else:
        synthetic_allowed = allow_synthetic or suite_name == SUITE_CORE_SHADOW
        if not synthetic_allowed:
            raise ValueError(
                "Trace-backed outcomes are required for review-grade shadow eval. "
                "Provide --trace-jsonl/--trace-dir or pass --allow-synthetic (which forces pass=false except core-shadow)."
            )

        evaluation_source = "synthetic"
        kernel_outcomes = evaluate_shadow_suite(
            suite=suite_name,
            perturb_profile=profile,
            runs=requested_runs,
            selector_mode=mode,
            compaction_policy=compaction_mode,
            kernel_enabled=True,
        )
        baseline_outcomes = evaluate_shadow_suite(
            suite=suite_name,
            perturb_profile=profile,
            runs=requested_runs,
            selector_mode=SELECTOR_MODE_DETERMINISTIC,
            compaction_policy=COMPACTION_POLICY_SIZE_ONLY,
            kernel_enabled=False,
        )
        if compaction_mode == COMPACTION_POLICY_SIZE_ONLY:
            size_only_kernel_outcomes = list(kernel_outcomes)
        else:
            size_only_kernel_outcomes = evaluate_shadow_suite(
                suite=suite_name,
                perturb_profile=profile,
                runs=requested_runs,
                selector_mode=mode,
                compaction_policy=COMPACTION_POLICY_SIZE_ONLY,
                kernel_enabled=True,
            )
        compaction_baseline_source = "synthetic"
        trace_sources = []
        trace_sources_full = []
        trace_records_total = 0
        trace_records_used = {
            "kernel_candidate": len(kernel_outcomes),
            "baseline": len(baseline_outcomes),
            "kernel_size_only": len(size_only_kernel_outcomes),
        }
        ablation_outcomes = {}
        require_complete_ablation = suite_name == SUITE_MEMORYARENA_MINI_PERTURB

    total_runs = max(1, min(len(kernel_outcomes), len(baseline_outcomes)))
    kernel_outcomes = kernel_outcomes[:total_runs]
    baseline_outcomes = baseline_outcomes[:total_runs]

    harness = ContinuityBenchmarkHarness()
    kernel_report = harness.evaluate(_to_runs(kernel_outcomes))
    baseline_report = harness.evaluate(_to_runs(baseline_outcomes))

    metrics = {
        "resume_success_rate": float(kernel_report.resume_success_rate),
        "reprompt_rate": float(kernel_report.reprompt_rate),
        "off_goal_tool_call_rate": float(kernel_report.off_goal_tool_call_rate),
    }

    weak_scores = [float(item.get("weak_check_score", 0.0)) for item in kernel_outcomes]
    strong_count = sum(1 for item in kernel_outcomes if bool(item.get("strong_check_triggered", False)))
    incorrect_accept_count = sum(1 for item in kernel_outcomes if bool(item.get("incorrect_accept", False)))
    incorrect_reject_count = sum(1 for item in kernel_outcomes if bool(item.get("incorrect_reject", False)))
    fingerprint_drift_count = sum(
        1 for item in kernel_outcomes if bool(item.get("runtime_state_fingerprint_drift", False))
    )

    continuity_lift_delta = round(
        float(kernel_report.resume_success_rate) - float(baseline_report.resume_success_rate),
        2,
    )

    weak_check_score = round(sum(weak_scores) / max(len(weak_scores), 1), 3)
    strong_check_triggered = strong_count > 0
    strong_check_triggered_rate = _pct(strong_count, total_runs)
    incorrect_accept_rate = _pct(incorrect_accept_count, total_runs)
    incorrect_reject_rate = _pct(incorrect_reject_count, total_runs)
    runtime_state_fingerprint_drift_rate = _pct(fingerprint_drift_count, total_runs)

    avg_dropped_fields = round(
        sum(float(item.get("dropped_fields_count", 0.0)) for item in kernel_outcomes)
        / max(total_runs, 1),
        2,
    )

    if compaction_mode == COMPACTION_POLICY_SIZE_ONLY:
        size_only_kernel_report = kernel_report
        size_only_kernel_outcomes = kernel_outcomes
    else:
        if size_only_kernel_outcomes:
            size_only_kernel_report = harness.evaluate(_to_runs(size_only_kernel_outcomes))
        else:
            size_only_kernel_outcomes = evaluate_shadow_suite(
                suite=suite_name,
                perturb_profile=profile,
                runs=total_runs,
                selector_mode=mode,
                compaction_policy=COMPACTION_POLICY_SIZE_ONLY,
                kernel_enabled=True,
            )
            size_only_kernel_report = harness.evaluate(_to_runs(size_only_kernel_outcomes))
            compaction_baseline_source = "synthetic_fallback"

    baseline_compaction_dropped = round(
        sum(float(item.get("dropped_fields_count", 0.0)) for item in size_only_kernel_outcomes)
        / max(len(size_only_kernel_outcomes), 1),
        2,
    )

    compaction_ab = {
        "baseline_policy": COMPACTION_POLICY_SIZE_ONLY,
        "candidate_policy": compaction_mode,
        "baseline_source": compaction_baseline_source,
        "baseline_resume_success_rate": float(size_only_kernel_report.resume_success_rate),
        "candidate_resume_success_rate": float(kernel_report.resume_success_rate),
        "resume_success_delta": round(
            float(kernel_report.resume_success_rate) - float(size_only_kernel_report.resume_success_rate),
            2,
        ),
        "baseline_avg_dropped_fields": baseline_compaction_dropped,
        "candidate_avg_dropped_fields": avg_dropped_fields,
        "dropped_fields_delta": round(avg_dropped_fields - baseline_compaction_dropped, 2),
    }

    compaction_abc = _build_compaction_abc(
        suite=suite_name,
        perturb_profile=profile,
        runs=total_runs,
        ablation_outcomes=ablation_outcomes,
        require_complete=require_complete_ablation,
        source=evaluation_source,
    )

    threshold_inputs = {
        "resume_success_rate": metrics["resume_success_rate"],
        "reprompt_rate": metrics["reprompt_rate"],
        "off_goal_tool_call_rate": metrics["off_goal_tool_call_rate"],
        "continuity_lift_delta": continuity_lift_delta,
        "incorrect_accept_rate": incorrect_accept_rate,
        "incorrect_reject_rate": incorrect_reject_rate,
        "runtime_state_fingerprint_drift_rate": runtime_state_fingerprint_drift_rate,
    }
    threshold_status = {
        metric: _threshold_pass(metric, threshold_inputs[metric])
        for metric in QUALITY_THRESHOLDS.keys()
    }

    source_gate = evaluation_source == "observed_trace" or suite_name == SUITE_CORE_SHADOW
    passed = all(threshold_status.values()) and source_gate

    if evaluation_source == "synthetic" and suite_name != SUITE_CORE_SHADOW:
        passed = False

    task_outcomes_digest = _deterministic_digest(
        {
            "suite": suite_name,
            "perturb_profile": profile,
            "selector_mode": mode,
            "compaction_policy": compaction_mode,
            "runs": total_runs,
            "evaluation_source": evaluation_source,
            "kernel_outcomes": kernel_outcomes,
        }
    )

    verification_calibration = _default_verification_calibration(
        evaluation_source=evaluation_source,
        suite=suite_name,
    )

    snapshot = {
        "schema_version": SHADOW_EVAL_SCHEMA_VERSION,
        "kind": "shadow_eval",
        "layer": str(layer),
        "chunk": str(chunk),
        "suite": suite_name,
        "perturb_profile": profile,
        "selector_mode": mode,
        "compaction_policy": compaction_mode,
        "generated_at": generated_at or utc_now_iso(),
        "runs": total_runs,
        "task_grounding": {
            "suite": suite_name,
            "perturb_profile": profile,
            "catalog_size": len(_suite_tasks(suite_name)),
            "tasks_evaluated": total_runs,
            "memory_dependent_tasks": total_runs,
            "baseline_resume_success_rate": float(baseline_report.resume_success_rate),
            "evaluation_source": evaluation_source,
            "trace_sources": trace_sources,
            "trace_sources_full": trace_sources_full,
            "trace_records_total": trace_records_total,
            "trace_records_used": trace_records_used,
            "task_outcomes_digest": task_outcomes_digest,
        },
        "metrics": metrics,
        "continuity_lift_delta": continuity_lift_delta,
        "weak_check_score": weak_check_score,
        "strong_check_triggered": strong_check_triggered,
        "incorrect_accept_rate": incorrect_accept_rate,
        "incorrect_reject_rate": incorrect_reject_rate,
        "runtime_state_fingerprint_drift_rate": runtime_state_fingerprint_drift_rate,
        "verification": {
            "weak_check_score": weak_check_score,
            "strong_check_triggered": strong_check_triggered,
            "strong_check_triggered_rate": strong_check_triggered_rate,
            "incorrect_accept_rate": incorrect_accept_rate,
            "incorrect_reject_rate": incorrect_reject_rate,
            "weak_accept_threshold": verification_calibration["weak_accept_threshold"],
            "weak_reject_threshold": verification_calibration["weak_reject_threshold"],
        },
        "verification_calibration": verification_calibration,
        "compaction_ab": compaction_ab,
        "compaction_abc": compaction_abc,
        "thresholds": QUALITY_THRESHOLDS,
        "threshold_status": threshold_status,
        "baseline_reference": {
            "resume_success_rate": float(baseline_report.resume_success_rate),
            "reprompt_rate": float(baseline_report.reprompt_rate),
            "off_goal_tool_call_rate": float(baseline_report.off_goal_tool_call_rate),
            "avg_dropped_fields": baseline_compaction_dropped,
        },
        "run_outcomes": kernel_outcomes,
        "pass": passed,
    }
    snapshot["deterministic_digest"] = _snapshot_digest(snapshot)
    return snapshot


def _is_observed_snapshot(snapshot: dict[str, Any], suite: str) -> bool:
    if not isinstance(snapshot, dict):
        return False
    if snapshot.get("suite") != suite:
        return False
    task_grounding = snapshot.get("task_grounding")
    if not isinstance(task_grounding, dict):
        return False
    return task_grounding.get("evaluation_source") == "observed_trace"


def _build_verification_calibration(
    snapshots: list[dict[str, Any]],
    *,
    suite: str,
) -> dict[str, Any]:
    observed = [item for item in snapshots if _is_observed_snapshot(item, suite)]
    window = observed[-ROLLING_CALIBRATION_WINDOW:]

    if not window:
        return {
            "method": "rolling_observed_trace_v1",
            "suite": suite,
            "window_size": ROLLING_CALIBRATION_WINDOW,
            "window_count": 0,
            "window_snapshot_digests": [],
            "weak_accept_threshold": 0.78,
            "weak_reject_threshold": 0.6,
            "incorrect_accept_rate_window_avg": 0.0,
            "incorrect_accept_rate_window_max": 0.0,
            "incorrect_reject_rate_window_avg": 0.0,
            "incorrect_reject_rate_window_max": 0.0,
            "bounded_error_window_pass": False,
        }

    weak_scores = [_coerce_float(item.get("weak_check_score"), default=0.0) for item in window]
    incorrect_accept_rates = [_coerce_float(item.get("incorrect_accept_rate"), default=100.0) for item in window]
    incorrect_reject_rates = [_coerce_float(item.get("incorrect_reject_rate"), default=100.0) for item in window]

    weak_accept_threshold = _clamp(round(sum(weak_scores) / max(len(weak_scores), 1), 3), 0.5, 0.95)
    weak_reject_threshold = _clamp(round(weak_accept_threshold - 0.18, 3), 0.3, weak_accept_threshold)

    incorrect_accept_avg = round(sum(incorrect_accept_rates) / max(len(incorrect_accept_rates), 1), 2)
    incorrect_reject_avg = round(sum(incorrect_reject_rates) / max(len(incorrect_reject_rates), 1), 2)
    incorrect_accept_max = round(max(incorrect_accept_rates), 2)
    incorrect_reject_max = round(max(incorrect_reject_rates), 2)

    bounded_pass = incorrect_accept_max <= 5.0 and incorrect_reject_max <= 5.0

    return {
        "method": "rolling_observed_trace_v1",
        "suite": suite,
        "window_size": ROLLING_CALIBRATION_WINDOW,
        "window_count": len(window),
        "window_snapshot_digests": [str(item.get("deterministic_digest", "")) for item in window],
        "weak_accept_threshold": weak_accept_threshold,
        "weak_reject_threshold": weak_reject_threshold,
        "incorrect_accept_rate_window_avg": incorrect_accept_avg,
        "incorrect_accept_rate_window_max": incorrect_accept_max,
        "incorrect_reject_rate_window_avg": incorrect_reject_avg,
        "incorrect_reject_rate_window_max": incorrect_reject_max,
        "bounded_error_window_pass": bounded_pass,
    }


def append_shadow_snapshot(snapshot: dict[str, Any], append_path: str | Path) -> dict[str, Any]:
    path = Path(append_path)

    payload: dict[str, Any]
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            loaded = {}
        payload = loaded if isinstance(loaded, dict) else {}
    else:
        payload = {}

    version_raw = payload.get("version", 1)
    try:
        version = int(version_raw)
        if version <= 0:
            version = 1
    except Exception:
        version = 1

    snapshots_raw = payload.get("snapshots", [])
    snapshots = snapshots_raw if isinstance(snapshots_raw, list) else []

    notes = payload.get("notes", DEFAULT_APPEND_NOTES)
    if not isinstance(notes, str) or not notes:
        notes = DEFAULT_APPEND_NOTES

    normalized_snapshot = dict(snapshot)
    suite_name = str(normalized_snapshot.get("suite", DEFAULT_SUITE))
    calibration = _build_verification_calibration(
        snapshots + [normalized_snapshot],
        suite=suite_name,
    )

    verification = normalized_snapshot.get("verification")
    if isinstance(verification, dict):
        verification_out = dict(verification)
        verification_out["weak_accept_threshold"] = calibration["weak_accept_threshold"]
        verification_out["weak_reject_threshold"] = calibration["weak_reject_threshold"]
        verification_out["calibration_window_count"] = calibration["window_count"]
        normalized_snapshot["verification"] = verification_out

    normalized_snapshot["verification_calibration"] = calibration

    pass_value = _coerce_bool(normalized_snapshot.get("pass"), default=False)
    if _is_observed_snapshot(normalized_snapshot, suite=suite_name):
        normalized_snapshot["pass"] = bool(pass_value and calibration["bounded_error_window_pass"])
    else:
        normalized_snapshot["pass"] = pass_value

    normalized_snapshot["deterministic_digest"] = _snapshot_digest(normalized_snapshot)

    out = {
        "version": version,
        "snapshots": list(snapshots),
        "notes": notes,
    }
    out["snapshots"].append(normalized_snapshot)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def _build_trace_bundle(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    digest_prefix = str(snapshot.get("deterministic_digest", ""))[:12]
    selector_mode = str(snapshot.get("selector_mode", SELECTOR_MODE_DETERMINISTIC))
    compaction_policy = str(snapshot.get("compaction_policy", COMPACTION_POLICY_SIZE_ONLY))
    perturb_profile = str(snapshot.get("perturb_profile", PERTURB_PROFILE_NONE))
    task_grounding = snapshot.get("task_grounding") if isinstance(snapshot.get("task_grounding"), dict) else {}
    evaluation_source = str(task_grounding.get("evaluation_source", ""))

    rows: list[dict[str, Any]] = []
    run_outcomes = snapshot.get("run_outcomes")
    if not isinstance(run_outcomes, list):
        return rows

    for idx, item in enumerate(run_outcomes):
        if not isinstance(item, dict):
            continue

        run_index = _coerce_int(item.get("run_index"), default=idx)
        trace_id = str(item.get("trace_id", "")).strip() or f"shadow-{digest_prefix}-{run_index:04d}"
        span_id = f"{trace_id}:{run_index:04d}"

        if _coerce_bool(item.get("off_goal_tool_call"), default=False):
            result_status = "off_goal"
        elif _coerce_bool(item.get("reprompted"), default=False):
            result_status = "reprompt"
        elif _coerce_bool(item.get("resumed_successfully"), default=False):
            result_status = "resumed"
        else:
            result_status = "unknown"

        confidence = _clamp(_coerce_float(item.get("weak_check_score"), default=0.0), 0.0, 1.0)
        rows.append(
            {
                "trace_id": trace_id,
                "span_id": span_id,
                "hook": "shadow_eval",
                "tool_intent": str(item.get("task_id", f"task-{run_index}")),
                "result_status": result_status,
                "confidence": round(confidence, 3),
                "selector_mode": selector_mode,
                "compaction_policy": compaction_policy,
                "perturb_profile": perturb_profile,
                "evaluation_source": evaluation_source,
            }
        )

    rows.sort(key=lambda row: row.get("span_id", ""))
    return rows


def write_shadow_summary(
    snapshot: dict[str, Any],
    append_path: str | Path,
    artifacts_root: str | Path,
    generated_at: str | None = None,
) -> Path:
    ts_source = generated_at or utc_now_iso()
    try:
        parsed = datetime.fromisoformat(ts_source.replace("Z", "+00:00"))
    except Exception:
        parsed = datetime.now(timezone.utc)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    ts_compact = parsed.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    bucket = Path(artifacts_root) / ts_compact
    bucket.mkdir(parents=True, exist_ok=True)

    trace_bundle_rows = _build_trace_bundle(snapshot)
    trace_bundle_path = bucket / "trace-bundle.jsonl"
    with trace_bundle_path.open("w", encoding="utf-8") as fh:
        for row in trace_bundle_rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": SHADOW_EVAL_SCHEMA_VERSION,
        "generated_at": ts_source,
        "append_path": str(Path(append_path)),
        "trace_bundle_path": str(trace_bundle_path),
        "snapshot": snapshot,
    }

    out_path = bucket / "summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out_path
