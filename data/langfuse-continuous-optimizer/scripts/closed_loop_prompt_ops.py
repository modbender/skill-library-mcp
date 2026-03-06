#!/usr/bin/env python3
"""Closed-loop prompt ops utilities."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple


SCRIPT_VERSION = "0.1.0"


def first_non_empty(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        return value
    return None


def to_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if not math.isnan(value) else None
    if isinstance(value, str):
        text = value.strip()
        if text == "":
            return None
        try:
            return int(float(text))
        except ValueError:
            return None
    return None


def to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        value = float(value)
        return value if not math.isnan(value) else None
    if isinstance(value, str):
        text = value.strip()
        if text == "":
            return None
        try:
            value = float(text)
            return value if not math.isnan(value) else None
        except ValueError:
            return None
    return None


def to_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes", "y"}:
            return True
        if text in {"false", "0", "no", "n"}:
            return False
    return None


def parse_json_maybe(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if text == "":
        return None
    if (text.startswith("{") and text.endswith("}")) or (
        text.startswith("[") and text.endswith("]")
    ):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return value
    return value


def parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not isinstance(value, str):
        return None
    text = value.strip()
    if text == "":
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def to_iso_z(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def percentile(values: List[float], pct: float) -> Optional[float]:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    rank = (len(ordered) - 1) * (pct / 100.0)
    low = int(math.floor(rank))
    high = int(math.ceil(rank))
    if low == high:
        return float(ordered[low])
    low_v = ordered[low]
    high_v = ordered[high]
    return float(low_v + (high_v - low_v) * (rank - low))


def mean(values: List[float]) -> Optional[float]:
    return float(statistics.fmean(values)) if values else None


def clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def slugify(text: str, max_words: int = 6) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return "-".join(words[:max_words]) if words else ""


def parse_tags(raw: Any) -> List[str]:
    parsed = parse_json_maybe(raw)
    if isinstance(parsed, list):
        return [str(v).strip() for v in parsed if str(v).strip()]
    if isinstance(parsed, str):
        stripped = parsed.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            maybe_list = parse_json_maybe(stripped)
            if isinstance(maybe_list, list):
                return [str(v).strip() for v in maybe_list if str(v).strip()]
        if "," in stripped:
            return [v.strip() for v in stripped.split(",") if v.strip()]
        if stripped:
            return [stripped]
    return []


def flatten_content(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        text = value.get("text")
        return text if isinstance(text, str) else ""
    if isinstance(value, list):
        parts: List[str] = []
        for part in value:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
        return "\n".join(parts)
    return ""


def extract_input_text(payload: Any) -> str:
    if isinstance(payload, dict):
        messages = payload.get("messages")
        if isinstance(messages, list):
            parts: List[str] = []
            for msg in messages:
                if not isinstance(msg, dict):
                    continue
                role = str(msg.get("role", "")).strip()
                content = flatten_content(msg.get("content"))
                if content:
                    parts.append(f"{role}: {content}" if role else content)
            return "\n".join(parts).strip()
    if isinstance(payload, str):
        return payload.strip()
    return ""


def infer_task_key(
    name: Optional[str],
    trace_name: Optional[str],
    operation: Optional[str],
    app_name: Optional[str],
    tags: List[str],
    explicit_task_key: Optional[str] = None,
) -> str:
    if explicit_task_key:
        key = slugify(explicit_task_key)
        return key if key else "general"
    searchable = " ".join(
        [name or "", trace_name or "", operation or "", app_name or "", " ".join(tags)]
    ).lower()
    patterns = [
        (r"\bseed|bootstrap|proposal|draft|generate", "generation"),
        (r"\bmutat|cross|recombine|breed|edit|revise|transform", "transformation"),
        (r"\beval|judge|score|grader|rank", "evaluation"),
        (r"\brout|policy|select model", "routing"),
        (r"\blive|execution|run", "execution"),
        (r"\bsummary|summariz", "summarization"),
        (r"\bretriev|context", "retrieval"),
    ]
    for pattern, label in patterns:
        if re.search(pattern, searchable):
            return label
    for candidate in [name, trace_name, app_name, operation]:
        if candidate:
            key = slugify(candidate)
            if key:
                return key
    for tag in tags:
        key = slugify(tag)
        if key:
            return key
    return "general"


def load_records_from_json_file(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig")
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [x for x in parsed if isinstance(x, dict)]
        if isinstance(parsed, dict):
            if isinstance(parsed.get("data"), list):
                return [x for x in parsed["data"] if isinstance(x, dict)]
            return [parsed]
    except json.JSONDecodeError:
        pass

    records: List[Dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            records.append(row)
    return records


def parse_langfuse_json(path: Path, explicit_task_key: Optional[str]) -> List[Dict[str, Any]]:
    raw_records = load_records_from_json_file(path)
    normalized: List[Dict[str, Any]] = []

    for idx, row in enumerate(raw_records, start=1):
        metadata = parse_json_maybe(row.get("metadata"))
        metadata = metadata if isinstance(metadata, dict) else {}

        attributes = parse_json_maybe(metadata.get("attributes"))
        attributes = attributes if isinstance(attributes, dict) else {}

        resource_attrs = metadata.get("resourceAttributes")
        resource_attrs = resource_attrs if isinstance(resource_attrs, dict) else {}

        input_payload = parse_json_maybe(row.get("input"))
        output_payload = parse_json_maybe(row.get("output"))
        output_payload = output_payload if isinstance(output_payload, dict) else {}

        usage = output_payload.get("usage")
        usage = usage if isinstance(usage, dict) else {}

        row_usage_details = parse_json_maybe(
            first_non_empty(row.get("usageDetails"), row.get("usage_details"))
        )
        row_usage_details = row_usage_details if isinstance(row_usage_details, dict) else {}

        usage_details = parse_json_maybe(attributes.get("langfuse.observation.usage_details"))
        usage_details = usage_details if isinstance(usage_details, dict) else {}
        if not usage_details:
            usage_details = row_usage_details

        prompt_details = usage.get("prompt_tokens_details")
        prompt_details = prompt_details if isinstance(prompt_details, dict) else {}

        completion_details = usage.get("completion_tokens_details")
        completion_details = completion_details if isinstance(completion_details, dict) else {}

        row_cost_details = parse_json_maybe(
            first_non_empty(row.get("costDetails"), row.get("cost_details"))
        )
        row_cost_details = row_cost_details if isinstance(row_cost_details, dict) else {}

        cost_details = parse_json_maybe(attributes.get("langfuse.observation.cost_details"))
        cost_details = cost_details if isinstance(cost_details, dict) else {}
        if not cost_details:
            cost_details = row_cost_details

        prompt_tokens = first_non_empty(
            to_int(usage.get("prompt_tokens")),
            to_int(attributes.get("gen_ai.usage.input_tokens")),
            to_int(usage_details.get("input")),
            to_int(usage_details.get("prompt")),
        )
        completion_tokens = first_non_empty(
            to_int(usage.get("completion_tokens")),
            to_int(attributes.get("gen_ai.usage.output_tokens")),
            to_int(usage_details.get("output")),
            to_int(usage_details.get("completion")),
        )
        total_tokens = first_non_empty(
            to_int(usage.get("total_tokens")),
            to_int(attributes.get("gen_ai.usage.total_tokens")),
            to_int(usage_details.get("total")),
        )
        if total_tokens is None and prompt_tokens is not None and completion_tokens is not None:
            total_tokens = prompt_tokens + completion_tokens

        reasoning_tokens = first_non_empty(
            to_int(completion_details.get("reasoning_tokens")),
            to_int(attributes.get("gen_ai.usage.output_tokens.reasoning")),
            to_int(usage_details.get("output_reasoning")),
            to_int(usage_details.get("reasoning")),
        )
        cached_prompt_tokens = first_non_empty(
            to_int(prompt_details.get("cached_tokens")),
            to_int(attributes.get("gen_ai.usage.input_tokens.cached")),
            to_int(usage_details.get("input_cached")),
            to_int(usage_details.get("cached")),
        )

        input_cost = first_non_empty(
            to_float(attributes.get("gen_ai.usage.input_cost")),
            to_float(cost_details.get("input")),
        )
        output_cost = first_non_empty(
            to_float(attributes.get("gen_ai.usage.output_cost")),
            to_float(cost_details.get("output")),
        )
        total_cost = first_non_empty(
            to_float(attributes.get("gen_ai.usage.cost")),
            to_float(attributes.get("gen_ai.usage.total_cost")),
            to_float(cost_details.get("total")),
            to_float(row.get("totalCost")),
            to_float(row.get("total_cost")),
        )
        if total_cost is None and input_cost is not None and output_cost is not None:
            total_cost = input_cost + output_cost

        start_dt = parse_datetime(first_non_empty(row.get("startTime"), row.get("start_time")))
        end_dt = parse_datetime(first_non_empty(row.get("endTime"), row.get("end_time")))
        latency_ms = None
        if start_dt and end_dt:
            latency_ms = max((end_dt - start_dt).total_seconds() * 1000.0, 0.0)
        if latency_ms is None:
            latency_ms = to_float(first_non_empty(row.get("latency"), row.get("latencyMs"), row.get("latency_ms")))

        trace_name = first_non_empty(
            attributes.get("langfuse.trace.name"),
            row.get("traceName"),
            row.get("trace_name"),
            row.get("name"),
        )
        operation = first_non_empty(
            attributes.get("gen_ai.operation.name"),
            attributes.get("langfuse.trace.metadata.source"),
            row.get("observationType"),
            row.get("type"),
        )
        app_name = first_non_empty(
            resource_attrs.get("service.name"),
            attributes.get("langfuse.trace.metadata.openrouter.source"),
            row.get("appName"),
            row.get("app_name"),
        )
        tags = parse_tags(
            first_non_empty(
                attributes.get("langfuse.trace.tags"),
                row.get("tags"),
                metadata.get("tags"),
            )
        )

        input_text = extract_input_text(input_payload)
        input_sha256 = (
            hashlib.sha256(input_text.encode("utf-8")).hexdigest() if input_text else None
        )

        choices = output_payload.get("choices")
        choice_finish = None
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            choice_finish = choices[0].get("finish_reason")

        finish_reason = first_non_empty(
            choice_finish,
            attributes.get("gen_ai.response.finish_reason"),
            attributes.get("langfuse.trace.metadata.openrouter.finish_reason"),
            row.get("completionStatus"),
            row.get("status"),
        )

        record = {
            "source": "langfuse_json",
            "source_file": str(path),
            "source_row": idx,
            "event_id": first_non_empty(row.get("id"), row.get("observationId"), row.get("event_id")),
            "trace_id": first_non_empty(
                row.get("traceId"),
                resource_attrs.get("openrouter.trace.id"),
                attributes.get("langfuse.trace.id"),
                attributes.get("langfuse.trace.metadata.testId"),
            ),
            "name": row.get("name"),
            "task_key": infer_task_key(
                name=row.get("name"),
                trace_name=trace_name,
                operation=operation,
                app_name=app_name,
                tags=tags,
                explicit_task_key=explicit_task_key,
            ),
            "model": first_non_empty(
                row.get("model"),
                output_payload.get("model"),
                attributes.get("gen_ai.response.model"),
                attributes.get("gen_ai.request.model"),
                attributes.get("langfuse.observation.model.name"),
            ),
            "provider": first_non_empty(
                row.get("provider"),
                attributes.get("gen_ai.provider.name"),
                attributes.get("langfuse.trace.metadata.openrouter.provider_name"),
            ),
            "operation": operation,
            "app_name": app_name,
            "environment": first_non_empty(
                row.get("environment"),
                attributes.get("langfuse.trace.metadata.environment"),
            ),
            "tags": tags,
            "started_at": to_iso_z(start_dt),
            "ended_at": to_iso_z(end_dt),
            "latency_ms": latency_ms,
            "ttft_ms": to_float(first_non_empty(row.get("ttftMs"), row.get("ttft_ms"))),
            "finish_reason": finish_reason,
            "status": (
                "cancelled"
                if str(first_non_empty(row.get("status"), finish_reason)).lower() in {"cancelled", "canceled"}
                else "ok"
            ),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "reasoning_tokens": reasoning_tokens,
            "cached_prompt_tokens": cached_prompt_tokens,
            "total_tokens": total_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "prompt_char_count": len(input_text) if input_text else None,
            "input_sha256": input_sha256,
            "prompt_name": first_non_empty(
                row.get("promptName"),
                attributes.get("langfuse.prompt.name"),
                attributes.get("prompt_name"),
            ),
            "prompt_version": first_non_empty(
                row.get("promptVersion"),
                attributes.get("langfuse.prompt.version"),
                attributes.get("prompt_version"),
            ),
            "eval_score": None,
        }
        normalized.append(record)

    return normalized


def parse_openrouter_csv(path: Path, explicit_task_key: Optional[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, row in enumerate(reader, start=2):
            prompt_tokens = to_int(row.get("tokens_prompt"))
            completion_tokens = to_int(row.get("tokens_completion"))
            total_tokens = (
                prompt_tokens + completion_tokens
                if prompt_tokens is not None and completion_tokens is not None
                else None
            )

            started_dt = parse_datetime(row.get("created_at"))
            latency_ms = to_float(row.get("generation_time_ms"))
            ended_dt = None
            if started_dt and latency_ms is not None:
                ended_dt = started_dt + timedelta(milliseconds=max(latency_ms, 0.0))

            app_name = row.get("app_name")
            task_key = infer_task_key(
                name=app_name,
                trace_name=None,
                operation="chat",
                app_name=app_name,
                tags=[],
                explicit_task_key=explicit_task_key,
            )
            cancelled = to_bool(row.get("cancelled"))

            record = {
                "source": "openrouter_csv",
                "source_file": str(path),
                "source_row": idx,
                "event_id": row.get("generation_id"),
                "trace_id": None,
                "name": app_name or "openrouter-generation",
                "task_key": task_key,
                "model": row.get("model_permaslug"),
                "provider": row.get("provider_name"),
                "operation": "chat",
                "app_name": app_name,
                "environment": None,
                "tags": [],
                "started_at": to_iso_z(started_dt),
                "ended_at": to_iso_z(ended_dt),
                "latency_ms": latency_ms,
                "ttft_ms": to_float(row.get("time_to_first_token_ms")),
                "finish_reason": first_non_empty(
                    row.get("finish_reason_normalized"),
                    row.get("finish_reason_raw"),
                ),
                "status": "cancelled" if cancelled else "ok",
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "reasoning_tokens": to_int(row.get("tokens_reasoning")),
                "cached_prompt_tokens": to_int(row.get("tokens_cached")),
                "total_tokens": total_tokens,
                "input_cost": None,
                "output_cost": None,
                "total_cost": to_float(row.get("cost_total")),
                "prompt_char_count": None,
                "input_sha256": None,
                "prompt_name": None,
                "prompt_version": None,
                "eval_score": None,
            }
            rows.append(record)
    return rows


def dedupe_records(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set = set()
    unique: List[Dict[str, Any]] = []
    for rec in records:
        key = (
            rec.get("source"),
            rec.get("event_id"),
            rec.get("started_at"),
            rec.get("model"),
            rec.get("total_tokens"),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(rec)
    return unique


def write_jsonl(path: Path, records: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for rec in records:
            handle.write(json.dumps(rec, ensure_ascii=True, sort_keys=True) + "\n")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            try:
                row = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                records.append(row)
    return records


def load_score_rows(path: Path) -> List[Dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        rows: List[Dict[str, Any]] = []
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows.append(dict(row))
        return rows
    return load_records_from_json_file(path)


def normalize_score(value: Any) -> Optional[float]:
    score = to_float(value)
    if score is None:
        return None
    if score > 1.0 and score <= 100.0:
        score /= 100.0
    return clamp01(score)


def load_scores(paths: List[Path]) -> Tuple[Dict[str, List[float]], Dict[str, List[str]]]:
    score_map: Dict[str, List[float]] = defaultdict(list)
    metric_map: Dict[str, set] = defaultdict(set)

    for path in paths:
        rows = load_score_rows(path)
        for row in rows:
            if not isinstance(row, dict):
                continue
            event_id = first_non_empty(
                row.get("event_id"),
                row.get("observation_id"),
                row.get("observationId"),
                row.get("generation_id"),
                row.get("id"),
                row.get("trace_id"),
            )
            if not event_id:
                continue
            score = normalize_score(
                first_non_empty(row.get("score"), row.get("value"), row.get("numeric_score"))
            )
            if score is None:
                continue
            metric = first_non_empty(
                row.get("metric"),
                row.get("name"),
                row.get("score_name"),
                "score",
            )
            event_id = str(event_id)
            score_map[event_id].append(score)
            metric_map[event_id].add(str(metric))

    collapsed: Dict[str, List[str]] = {}
    for key, names in metric_map.items():
        collapsed[key] = sorted(names)
    return dict(score_map), collapsed


def normalize_metric(value: Optional[float], floor: float, ceiling: float) -> float:
    if value is None:
        return 1.0
    if math.isclose(floor, ceiling):
        return 0.0
    return clamp01((value - floor) / (ceiling - floor))


def event_quality(record: Dict[str, Any]) -> float:
    explicit = normalize_score(record.get("eval_score"))
    if explicit is not None:
        return explicit

    finish_reason = str(record.get("finish_reason") or "").strip().lower()
    status = str(record.get("status") or "").strip().lower()
    if status == "cancelled" or finish_reason in {"cancelled", "error", "failed", "timeout"}:
        return 0.0
    if finish_reason in {"stop", "completed", "success", "tool_calls", "end_turn"}:
        return 1.0
    if finish_reason in {"length"}:
        return 0.65
    if finish_reason == "":
        return 0.5
    return 0.75


def summarize_groups(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for rec in records:
        task_key = str(rec.get("task_key") or "general")
        model = str(rec.get("model") or "unknown")
        groups[(task_key, model)].append(rec)

    summaries: List[Dict[str, Any]] = []
    for (task_key, model), rows in sorted(groups.items()):
        costs = [float(v) for v in [to_float(r.get("total_cost")) for r in rows] if v is not None]
        latencies = [float(v) for v in [to_float(r.get("latency_ms")) for r in rows] if v is not None]
        prompt_tokens = [float(v) for v in [to_int(r.get("prompt_tokens")) for r in rows] if v is not None]
        completion_tokens = [
            float(v) for v in [to_int(r.get("completion_tokens")) for r in rows] if v is not None
        ]
        cached_prompt_tokens = [
            float(v) for v in [to_int(r.get("cached_prompt_tokens")) for r in rows] if v is not None
        ]
        qualities = [event_quality(r) for r in rows]
        evaluator_scores = [normalize_score(r.get("eval_score")) for r in rows]
        evaluator_scores = [x for x in evaluator_scores if x is not None]

        ratios: List[float] = []
        for r in rows:
            p = to_float(r.get("prompt_tokens"))
            c = to_float(r.get("completion_tokens"))
            if p is None or c is None or c <= 0:
                continue
            ratios.append(float(p / c))

        summaries.append(
            {
                "task_key": task_key,
                "model": model,
                "calls": len(rows),
                "evaluator_coverage": (len(evaluator_scores) / len(rows)) if rows else 0.0,
                "quality_mean": mean(qualities),
                "quality_p50": percentile(qualities, 50.0),
                "cost_mean": mean(costs),
                "cost_p50": percentile(costs, 50.0),
                "cost_p95": percentile(costs, 95.0),
                "latency_mean_ms": mean(latencies),
                "latency_p95_ms": percentile(latencies, 95.0),
                "prompt_tokens_mean": mean(prompt_tokens),
                "prompt_tokens_p95": percentile(prompt_tokens, 95.0),
                "completion_tokens_mean": mean(completion_tokens),
                "cached_prompt_tokens_mean": mean(cached_prompt_tokens),
                "prompt_to_completion_ratio_mean": mean(ratios),
            }
        )
    return summaries


def route_recommendations(
    selected: Dict[str, Any],
    prompt_token_p95_warn: int,
    prompt_ratio_warn: float,
) -> List[str]:
    actions: List[str] = []
    p95 = selected.get("prompt_tokens_p95")
    ratio = selected.get("prompt_to_completion_ratio_mean")
    cached_mean = selected.get("cached_prompt_tokens_mean")
    prompt_mean = selected.get("prompt_tokens_mean")

    if p95 is not None and p95 > float(prompt_token_p95_warn):
        actions.append("cap-context-and-summarize-history")
    if ratio is not None and ratio > prompt_ratio_warn:
        actions.append("trim-instructions-and-redundant-context")
    if (
        prompt_mean is not None
        and prompt_mean > 5000
        and cached_mean is not None
        and cached_mean / max(prompt_mean, 1.0) < 0.10
    ):
        actions.append("increase-prefix-reuse-or-cacheable-prompt-segments")
    return actions


def build_policy(
    records: List[Dict[str, Any]],
    min_samples: int,
    quality_floor: float,
    quality_weight: float,
    cost_weight: float,
    latency_weight: float,
    max_cost_p95: Optional[float],
    max_latency_p95_ms: Optional[float],
    fallback_model: Optional[str],
    prompt_token_p95_warn: int,
    prompt_ratio_warn: float,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    summaries = summarize_groups(records)
    by_task: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in summaries:
        by_task[str(row["task_key"])].append(row)

    routes: List[Dict[str, Any]] = []
    selected_models: List[str] = []

    for task_key in sorted(by_task.keys()):
        candidates = by_task[task_key]
        if not candidates:
            continue

        cost_values = [c["cost_mean"] for c in candidates if c["cost_mean"] is not None]
        latency_values = [c["latency_p95_ms"] for c in candidates if c["latency_p95_ms"] is not None]
        cost_floor = min(cost_values) if cost_values else 0.0
        cost_ceiling = max(cost_values) if cost_values else 1.0
        latency_floor = min(latency_values) if latency_values else 0.0
        latency_ceiling = max(latency_values) if latency_values else 1.0

        ranked: List[Dict[str, Any]] = []
        for c in candidates:
            q = float(c.get("quality_mean") or 0.0)
            c_norm = normalize_metric(c.get("cost_mean"), cost_floor, cost_ceiling)
            l_norm = normalize_metric(c.get("latency_p95_ms"), latency_floor, latency_ceiling)
            utility = (quality_weight * q) - (cost_weight * c_norm) - (latency_weight * l_norm)
            row = dict(c)
            row["cost_norm"] = c_norm
            row["latency_norm"] = l_norm
            row["utility"] = utility
            ranked.append(row)

        def rank_key(item: Dict[str, Any]) -> Tuple[float, float, float, float]:
            cost = item["cost_mean"] if item["cost_mean"] is not None else 1e18
            latency = item["latency_p95_ms"] if item["latency_p95_ms"] is not None else 1e18
            return (float(item["utility"]), float(item["quality_mean"] or 0.0), -cost, -latency)

        ranked = sorted(ranked, key=rank_key, reverse=True)
        eligible = [r for r in ranked if int(r.get("calls") or 0) >= min_samples]
        eligible = [r for r in eligible if float(r.get("quality_mean") or 0.0) >= quality_floor]
        if max_cost_p95 is not None:
            eligible = [r for r in eligible if r.get("cost_p95") is None or float(r["cost_p95"]) <= max_cost_p95]
        if max_latency_p95_ms is not None:
            eligible = [
                r
                for r in eligible
                if r.get("latency_p95_ms") is None or float(r["latency_p95_ms"]) <= max_latency_p95_ms
            ]
        if not eligible:
            eligible = [r for r in ranked if int(r.get("calls") or 0) >= 1]
        if not eligible:
            continue

        selected = eligible[0]
        selected_models.append(str(selected["model"]))
        next_best = ranked[1] if len(ranked) > 1 else None
        route_fallback = fallback_model or (next_best["model"] if next_best else selected["model"])
        recs = route_recommendations(selected, prompt_token_p95_warn, prompt_ratio_warn)

        routes.append(
            {
                "task_key": task_key,
                "selected_model": selected["model"],
                "fallback_model": route_fallback,
                "selection_reason": "Selected by weighted utility with quality and safety constraints.",
                "observed": {
                    "calls": int(selected["calls"]),
                    "quality_mean": round(float(selected.get("quality_mean") or 0.0), 4),
                    "cost_mean": round(float(selected["cost_mean"]), 6) if selected.get("cost_mean") is not None else None,
                    "cost_p95": round(float(selected["cost_p95"]), 6) if selected.get("cost_p95") is not None else None,
                    "latency_p95_ms": round(float(selected["latency_p95_ms"]), 2)
                    if selected.get("latency_p95_ms") is not None
                    else None,
                    "prompt_tokens_p95": int(round(float(selected["prompt_tokens_p95"])))
                    if selected.get("prompt_tokens_p95") is not None
                    else None,
                    "evaluator_coverage": round(float(selected.get("evaluator_coverage") or 0.0), 4),
                },
                "limits": {
                    "max_prompt_tokens": int(round(float(selected["prompt_tokens_p95"])))
                    if selected.get("prompt_tokens_p95") is not None
                    else None
                },
                "prompt_actions": recs,
                "candidate_rank": [
                    {
                        "model": c["model"],
                        "calls": int(c["calls"]),
                        "quality_mean": round(float(c.get("quality_mean") or 0.0), 4),
                        "cost_mean": round(float(c["cost_mean"]), 6) if c.get("cost_mean") is not None else None,
                        "latency_p95_ms": round(float(c["latency_p95_ms"]), 2)
                        if c.get("latency_p95_ms") is not None
                        else None,
                        "utility": round(float(c.get("utility") or 0.0), 6),
                    }
                    for c in ranked
                ],
            }
        )

    default_model = None
    if selected_models:
        counts: Dict[str, int] = defaultdict(int)
        for model in selected_models:
            counts[model] += 1
        default_model = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)[0][0]

    prompt_values = [float(v) for v in [to_int(r.get("prompt_tokens")) for r in records] if v is not None]
    global_prompt_p95 = percentile(prompt_values, 95.0) if prompt_values else None
    global_prompt_max = max(prompt_values) if prompt_values else None
    global_recommendations: List[str] = []
    if global_prompt_p95 is not None and global_prompt_p95 > 20000:
        global_recommendations.append(
            "Prompt p95 exceeds 20k tokens. Cap retrieval/context size and summarize long history/tool output."
        )
    if global_prompt_max is not None and global_prompt_max > 100000:
        global_recommendations.append(
            "Prompt max exceeds 100k tokens. Enforce hard token budget guards before requests."
        )

    policy = {
        "policy_type": "closed-loop-routing",
        "version": SCRIPT_VERSION,
        "generated_at": to_iso_z(datetime.now(timezone.utc)),
        "selection": {
            "min_samples": min_samples,
            "quality_floor": quality_floor,
            "weights": {"quality": quality_weight, "cost": cost_weight, "latency": latency_weight},
            "max_cost_p95": max_cost_p95,
            "max_latency_p95_ms": max_latency_p95_ms,
        },
        "defaults": {"model": default_model, "fallback_model": fallback_model or default_model},
        "routes": routes,
        "global_recommendations": global_recommendations,
        "global_prompt_stats": {
            "prompt_tokens_p95": int(round(global_prompt_p95)) if global_prompt_p95 is not None else None,
            "prompt_tokens_max": int(round(global_prompt_max)) if global_prompt_max is not None else None,
        },
    }
    return policy, summaries


def write_model_stats_csv(path: Path, summaries: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "task_key",
        "model",
        "calls",
        "evaluator_coverage",
        "quality_mean",
        "quality_p50",
        "cost_mean",
        "cost_p50",
        "cost_p95",
        "latency_mean_ms",
        "latency_p95_ms",
        "prompt_tokens_mean",
        "prompt_tokens_p95",
        "completion_tokens_mean",
        "cached_prompt_tokens_mean",
        "prompt_to_completion_ratio_mean",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in summaries:
            writer.writerow({k: row.get(k) for k in fieldnames})


def cmd_normalize(args: argparse.Namespace) -> int:
    records: List[Dict[str, Any]] = []

    for raw in args.langfuse_json:
        path = Path(raw).expanduser()
        if not path.exists():
            print(f"[warn] Missing LangFuse JSON file: {path}", file=sys.stderr)
            continue
        records.extend(parse_langfuse_json(path, explicit_task_key=args.task_key))

    for raw in args.openrouter_csv:
        path = Path(raw).expanduser()
        if not path.exists():
            print(f"[warn] Missing OpenRouter CSV file: {path}", file=sys.stderr)
            continue
        records.extend(parse_openrouter_csv(path, explicit_task_key=args.task_key))

    if not records:
        print("No records parsed. Provide at least one valid input file.", file=sys.stderr)
        return 2

    if args.dedupe:
        records = dedupe_records(records)

    records = sorted(
        records,
        key=lambda x: (
            str(x.get("started_at") or ""),
            str(x.get("event_id") or ""),
            str(x.get("source") or ""),
        ),
    )

    out_jsonl = Path(args.out_jsonl).expanduser()
    write_jsonl(out_jsonl, records)

    source_counts: Dict[str, int] = defaultdict(int)
    for rec in records:
        source_counts[str(rec.get("source") or "unknown")] += 1

    print(f"Wrote {len(records)} normalized events to {out_jsonl}")
    for source, count in sorted(source_counts.items()):
        print(f"  {source}: {count}")
    return 0


def cmd_build_policy(args: argparse.Namespace) -> int:
    normalized_path = Path(args.normalized_jsonl).expanduser()
    if not normalized_path.exists():
        print(f"Missing normalized JSONL: {normalized_path}", file=sys.stderr)
        return 2

    records = load_jsonl(normalized_path)
    if not records:
        print(f"No usable events in: {normalized_path}", file=sys.stderr)
        return 2

    score_paths = [Path(p).expanduser() for p in args.scores]
    score_map, metric_map = load_scores(score_paths)
    for rec in records:
        event_id = str(rec.get("event_id") or "")
        if event_id and event_id in score_map:
            rec["eval_score"] = mean(score_map[event_id])
            rec["eval_metrics"] = metric_map.get(event_id, [])

    policy, summaries = build_policy(
        records=records,
        min_samples=args.min_samples,
        quality_floor=args.quality_floor,
        quality_weight=args.quality_weight,
        cost_weight=args.cost_weight,
        latency_weight=args.latency_weight,
        max_cost_p95=args.max_cost_p95,
        max_latency_p95_ms=args.max_latency_p95_ms,
        fallback_model=args.fallback_model if args.fallback_model else None,
        prompt_token_p95_warn=args.prompt_token_p95_warn,
        prompt_ratio_warn=args.prompt_ratio_warn,
    )

    out_policy = Path(args.out_policy_json).expanduser()
    out_policy.parent.mkdir(parents=True, exist_ok=True)
    out_policy.write_text(json.dumps(policy, indent=2, ensure_ascii=True), encoding="utf-8")

    out_stats = Path(args.out_model_stats_csv).expanduser()
    write_model_stats_csv(out_stats, summaries)

    print(f"Wrote routing policy: {out_policy}")
    print(f"Wrote model stats: {out_stats}")
    print(f"Routes generated: {len(policy.get('routes', []))}")
    return 0


def cmd_full_cycle(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    normalized_path = out_dir / "normalized_events.jsonl"
    policy_path = out_dir / "routing_policy.json"
    stats_path = out_dir / "model_stats.csv"

    normalize_args = argparse.Namespace(
        langfuse_json=args.langfuse_json,
        openrouter_csv=args.openrouter_csv,
        out_jsonl=str(normalized_path),
        dedupe=args.dedupe,
        task_key=args.task_key,
    )
    rc = cmd_normalize(normalize_args)
    if rc != 0:
        return rc

    build_args = argparse.Namespace(
        normalized_jsonl=str(normalized_path),
        scores=args.scores,
        out_policy_json=str(policy_path),
        out_model_stats_csv=str(stats_path),
        min_samples=args.min_samples,
        quality_floor=args.quality_floor,
        quality_weight=args.quality_weight,
        cost_weight=args.cost_weight,
        latency_weight=args.latency_weight,
        max_cost_p95=args.max_cost_p95,
        max_latency_p95_ms=args.max_latency_p95_ms,
        fallback_model=args.fallback_model,
        prompt_token_p95_warn=args.prompt_token_p95_warn,
        prompt_ratio_warn=args.prompt_ratio_warn,
    )
    rc = cmd_build_policy(build_args)
    if rc != 0:
        return rc

    print("Full cycle complete.")
    print(f"  normalized: {normalized_path}")
    print(f"  policy:     {policy_path}")
    print(f"  stats:      {stats_path}")
    return 0


def add_build_policy_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--scores", action="append", default=[], help="Score CSV/JSON path.")
    parser.add_argument("--out-policy-json", required=True, help="Output routing policy JSON.")
    parser.add_argument("--out-model-stats-csv", required=True, help="Output model stats CSV.")
    parser.add_argument("--min-samples", type=int, default=5, help="Minimum calls before strict selection.")
    parser.add_argument(
        "--quality-floor",
        type=float,
        default=0.75,
        help="Minimum mean quality score for preferred model selection.",
    )
    parser.add_argument("--quality-weight", type=float, default=0.65, help="Utility weight for quality.")
    parser.add_argument("--cost-weight", type=float, default=0.2, help="Utility penalty weight for cost.")
    parser.add_argument(
        "--latency-weight", type=float, default=0.15, help="Utility penalty weight for latency."
    )
    parser.add_argument("--max-cost-p95", type=float, default=None, help="Optional hard cap for p95 cost.")
    parser.add_argument(
        "--max-latency-p95-ms", type=float, default=None, help="Optional hard cap for p95 latency."
    )
    parser.add_argument("--fallback-model", default="", help="Optional global fallback model override.")
    parser.add_argument(
        "--prompt-token-p95-warn", type=int, default=20000, help="Warn threshold for prompt token p95."
    )
    parser.add_argument(
        "--prompt-ratio-warn",
        type=float,
        default=8.0,
        help="Warn threshold for prompt/completion token ratio.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Closed-loop prompt operations for telemetry normalization and policy generation.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    normalize = sub.add_parser(
        "normalize", help="Normalize LangFuse JSON and OpenRouter CSV into unified JSONL."
    )
    normalize.add_argument("--langfuse-json", action="append", default=[], help="LangFuse JSON export path.")
    normalize.add_argument("--openrouter-csv", action="append", default=[], help="OpenRouter CSV export path.")
    normalize.add_argument("--out-jsonl", required=True, help="Output normalized JSONL.")
    normalize.add_argument("--task-key", default=None, help="Force one task_key for all records.")
    normalize.add_argument("--dedupe", action="store_true", help="Drop duplicate records.")
    normalize.set_defaults(func=cmd_normalize)

    build = sub.add_parser(
        "build-policy", help="Build routing policy JSON and model stats CSV from normalized JSONL."
    )
    build.add_argument("--normalized-jsonl", required=True, help="Normalized JSONL input path.")
    add_build_policy_flags(build)
    build.set_defaults(func=cmd_build_policy)

    full = sub.add_parser("full-cycle", help="Run normalize and build-policy in one command.")
    full.add_argument("--langfuse-json", action="append", default=[], help="LangFuse JSON export path.")
    full.add_argument("--openrouter-csv", action="append", default=[], help="OpenRouter CSV export path.")
    full.add_argument("--task-key", default=None, help="Force one task_key for all records.")
    full.add_argument("--dedupe", action="store_true", help="Drop duplicate records.")
    full.add_argument("--out-dir", required=True, help="Output directory for generated artifacts.")
    full.add_argument("--scores", action="append", default=[], help="Score CSV/JSON path.")
    full.add_argument("--min-samples", type=int, default=5, help="Minimum calls before strict selection.")
    full.add_argument("--quality-floor", type=float, default=0.75, help="Minimum mean quality score.")
    full.add_argument("--quality-weight", type=float, default=0.65, help="Utility weight for quality.")
    full.add_argument("--cost-weight", type=float, default=0.2, help="Utility penalty weight for cost.")
    full.add_argument("--latency-weight", type=float, default=0.15, help="Utility penalty weight for latency.")
    full.add_argument("--max-cost-p95", type=float, default=None, help="Optional hard cap for p95 cost.")
    full.add_argument(
        "--max-latency-p95-ms", type=float, default=None, help="Optional hard cap for p95 latency."
    )
    full.add_argument("--fallback-model", default="", help="Optional global fallback model override.")
    full.add_argument(
        "--prompt-token-p95-warn", type=int, default=20000, help="Warn threshold for prompt token p95."
    )
    full.add_argument(
        "--prompt-ratio-warn", type=float, default=8.0, help="Warn threshold for prompt/completion ratio."
    )
    full.set_defaults(func=cmd_full_cycle)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
