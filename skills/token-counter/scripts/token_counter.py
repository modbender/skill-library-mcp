#!/usr/bin/env python3
"""
Token usage analyzer for OpenClaw sessions.

Reads local transcript/session data and outputs token attribution by:
- session
- category
- client
- tool
- model
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DEFAULT_SESSIONS_DIR = Path("/Users/mikek/.openclaw/agents/main/sessions")
DEFAULT_SESSIONS_INDEX = DEFAULT_SESSIONS_DIR / "sessions.json"
DEFAULT_CRON_JOBS = Path("/Users/mikek/.openclaw/cron/jobs.json")
DEFAULT_OUTPUT_DIR = Path("/Users/mikek/.openclaw/workspace/token-usage")
DEFAULT_DAILY_DIR = DEFAULT_OUTPUT_DIR / "daily"

CRON_PREFIX_RE = re.compile(r"^\[cron:([0-9a-fA-F-]{36})\s+([^\]]+)\]")
SESSION_KEY_RE = re.compile(r"\b(agent:main:(?:main|cron:[0-9a-fA-F-]{36}(?::run:[0-9a-fA-F-]{36})?|subagent:[0-9a-fA-F-]{36}))\b")
MESSAGE_ID_STYLE_RE = re.compile(r"^\[[A-Za-z]{3}\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+[A-Z]{2,4}\]")
CRON_KEY_RE = re.compile(r"agent:main:cron:([0-9a-fA-F-]{36})")


@dataclass
class SessionMeta:
    session_id: str
    session_key: str | None
    label: str | None
    model: str | None
    updated_at_ms: int | None
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    raw: dict[str, Any]


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def parse_iso_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        # Heuristic: values bigger than year-2000 seconds are likely epoch ms.
        if value > 10_000_000_000:
            return datetime.fromtimestamp(value / 1000.0, tz=timezone.utc)
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def parse_period(period: str) -> timedelta:
    m = re.match(r"^(\d+)([dhwm])$", period.strip().lower())
    if not m:
        raise ValueError("Invalid period. Use formats like 1d, 7d, 2w, 1m, 12h.")
    value = int(m.group(1))
    unit = m.group(2)
    if value <= 0:
        raise ValueError("Period value must be greater than zero.")
    if unit == "h":
        return timedelta(hours=value)
    if unit == "d":
        return timedelta(days=value)
    if unit == "w":
        return timedelta(weeks=value)
    if unit == "m":
        return timedelta(days=30 * value)
    raise ValueError(f"Unsupported period unit: {unit}")


def parse_content_text(content: Any, max_chars: int = 4000) -> str:
    if isinstance(content, str):
        return content[:max_chars]
    if not isinstance(content, list):
        return ""
    chunks: list[str] = []
    total = 0
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") != "text":
            continue
        text = block.get("text")
        if not isinstance(text, str):
            continue
        if total >= max_chars:
            break
        remaining = max_chars - total
        cut = text[:remaining]
        chunks.append(cut)
        total += len(cut)
    return "\n".join(chunks)


def parse_tool_calls(content: Any) -> list[str]:
    if not isinstance(content, list):
        return []
    names: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") != "toolCall":
            continue
        name = block.get("name")
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
    return names


def as_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return default
    return default


def safe_read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_sessions_index(index_path: Path) -> tuple[dict[str, SessionMeta], dict[str, list[str]]]:
    id_to_meta: dict[str, SessionMeta] = {}
    key_to_ids: dict[str, list[str]] = defaultdict(list)
    if not index_path.exists():
        return id_to_meta, key_to_ids
    raw = safe_read_json(index_path)
    if not isinstance(raw, dict):
        return id_to_meta, key_to_ids

    for session_key, entry in raw.items():
        if not isinstance(entry, dict):
            continue
        session_id = entry.get("sessionId")
        if not isinstance(session_id, str) or not session_id:
            continue
        meta = SessionMeta(
            session_id=session_id,
            session_key=session_key if isinstance(session_key, str) else None,
            label=entry.get("label") if isinstance(entry.get("label"), str) else None,
            model=entry.get("model") if isinstance(entry.get("model"), str) else None,
            updated_at_ms=as_int(entry.get("updatedAt"), default=0) or None,
            input_tokens=as_int(entry.get("inputTokens"), default=0) or None,
            output_tokens=as_int(entry.get("outputTokens"), default=0) or None,
            total_tokens=as_int(entry.get("totalTokens"), default=0) or None,
            raw=entry,
        )
        id_to_meta[session_id] = meta
        if meta.session_key:
            key_to_ids[meta.session_key].append(session_id)
    return id_to_meta, key_to_ids


def load_cron_jobs(cron_jobs_path: Path) -> dict[str, dict[str, Any]]:
    if not cron_jobs_path.exists():
        return {}
    raw = safe_read_json(cron_jobs_path)
    if not isinstance(raw, dict):
        return {}
    jobs = raw.get("jobs")
    if not isinstance(jobs, list):
        return {}

    out: dict[str, dict[str, Any]] = {}
    for job in jobs:
        if not isinstance(job, dict):
            continue
        job_id = job.get("id")
        if not isinstance(job_id, str):
            continue
        payload = job.get("payload") if isinstance(job.get("payload"), dict) else {}
        payload_text = ""
        for field in ("message", "text"):
            val = payload.get(field)
            if isinstance(val, str) and val.strip():
                payload_text = val
                break
        out[job_id] = {
            "id": job_id,
            "name": job.get("name") if isinstance(job.get("name"), str) else "",
            "enabled": bool(job.get("enabled")),
            "payload_text": payload_text,
            "raw": job,
        }
    return out


def infer_key_from_text(first_user_text: str) -> tuple[str | None, str | None]:
    if not first_user_text:
        return None, None
    m = CRON_PREFIX_RE.match(first_user_text)
    if m:
        cron_id = m.group(1).lower()
        cron_name = m.group(2).strip()
        return f"agent:main:cron:{cron_id}", cron_name

    key_match = SESSION_KEY_RE.search(first_user_text)
    if key_match:
        return key_match.group(1), None

    if MESSAGE_ID_STYLE_RE.match(first_user_text):
        return "agent:main:main", None

    return None, None


def detect_session_type(session_key: str | None, first_user_text: str) -> str:
    if session_key:
        lowered = session_key.lower()
        if ":subagent:" in lowered:
            return "subagent"
        if ":cron:" in lowered:
            return "cron"
        if lowered == "agent:main:main":
            return "main"
    if first_user_text.startswith("[cron:"):
        return "cron"
    if MESSAGE_ID_STYLE_RE.match(first_user_text):
        return "main"
    return "interactive"


def extract_cron_id(session_key: str | None, first_user_text: str) -> str | None:
    if session_key:
        m = CRON_KEY_RE.search(session_key)
        if m:
            return m.group(1).lower()
    m = CRON_PREFIX_RE.match(first_user_text)
    if m:
        return m.group(1).lower()
    return None


def classify_category(
    session_type: str,
    session_key: str | None,
    label: str | None,
    first_user_text: str,
    cron_job: dict[str, Any] | None,
) -> str:
    cron_id = extract_cron_id(session_key, first_user_text)
    explicit_cron_map = {
        "d3d76f7a-7090-41c3-bb19-e2324093f9b1": "content_generation",
        "736a84a6-162a-4301-9deb-810cefff0628": "outreach_management",
        "6c966232-5cc9-4e21-aec7-fb8f143e67f6": "monitoring",
    }
    if cron_id in explicit_cron_map:
        return explicit_cron_map[cron_id]

    tokens = " ".join(
        part
        for part in [
            session_key or "",
            label or "",
            first_user_text[:3000],
            (cron_job or {}).get("name", ""),
            (cron_job or {}).get("payload_text", "")[:3000],
        ]
        if part
    ).lower()

    content_keywords = [
        "content",
        "article",
        "blog",
        "youtube",
        "summarize",
        "writer-",
        "research-",
        "nano-banana",
        "seo article",
        "publish",
    ]
    outreach_keywords = [
        "outreach",
        "guest post",
        "lead",
        "reply checker",
        "gmail",
        "email check",
        "prospect",
        "pitch",
        "inbox",
        "client outreach",
    ]
    monitoring_keywords = [
        "monitor",
        "heartbeat",
        "health",
        "status",
        "daily summary",
        "check-in",
        "watcher",
        "scan",
    ]
    job_keywords = [
        "job search",
        "job hunt",
        "application",
        "resume",
        "linkedin",
        "remote role",
        "$100k",
    ]

    if any(k in tokens for k in job_keywords):
        return "job_search"
    if any(k in tokens for k in outreach_keywords):
        return "outreach_management"
    if any(k in tokens for k in content_keywords):
        return "content_generation"
    if any(k in tokens for k in monitoring_keywords):
        return "monitoring"

    if session_type == "main":
        return "interactive"
    if session_type == "cron":
        return "monitoring"
    if session_type == "subagent":
        return "content_generation"
    return "interactive"


def detect_client(*texts: str) -> str:
    blob = "\n".join(t for t in texts if t).lower()
    if not blob:
        return "unknown"

    bonsai_markers = [
        "bonsai",
        "bonsaimediagroup.com",
        "mike@bonsai",
        "/projects/bonsai",
        "regulator",
        "jayco",
        "ocala horse",
        "ohp",
    ]
    personal_markers = [
        "mkhaytman@gmail.com",
        "aimarketingpicks",
        "remoteworkpicks",
        "anonark",
        "soflotimes",
        "quicksummit",
        "this is a personal site task",
        "personal site",
    ]

    is_bonsai = any(m in blob for m in bonsai_markers)
    is_personal = any(m in blob for m in personal_markers)

    if is_bonsai and is_personal:
        return "mixed"
    if is_bonsai:
        return "bonsai"
    if is_personal:
        return "personal"
    return "unknown"


def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m"
    hours, mins = divmod(minutes, 60)
    return f"{hours}h{mins:02d}m"


def short_label(session: dict[str, Any]) -> str:
    label = session.get("label")
    if isinstance(label, str) and label.strip():
        return label
    key = session.get("sessionKey", "")
    if key == "agent:main:main":
        return "main session"
    return str(key)


def pct(value: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return (100.0 * value) / total


def analyze_transcript(path: Path) -> dict[str, Any]:
    session_id = path.stem
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    first_user_text = ""
    text_samples: list[str] = []
    total_sample_chars = 0
    sample_cap = 8000

    usage_input = 0
    usage_output = 0
    usage_cache_read = 0
    usage_cache_write = 0
    usage_total = 0

    assistant_count = 0
    assistant_success_count = 0
    assistant_error_count = 0
    tool_result_error_count = 0
    saw_max_tokens = False

    tool_calls = Counter()
    tool_tokens = defaultdict(float)
    model_tokens = defaultdict(float)
    last_model = None

    line_count = 0

    with path.open("r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            line_count += 1
            line = raw_line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            dt = parse_iso_timestamp(obj.get("timestamp"))
            if dt is not None:
                if first_ts is None or dt < first_ts:
                    first_ts = dt
                if last_ts is None or dt > last_ts:
                    last_ts = dt

            typ = obj.get("type")
            if typ == "model_change":
                model_id = obj.get("modelId")
                if isinstance(model_id, str) and model_id:
                    last_model = model_id
                continue

            if typ != "message":
                continue

            msg = obj.get("message")
            if not isinstance(msg, dict):
                continue

            role = msg.get("role")
            if role == "user":
                text = parse_content_text(msg.get("content"), max_chars=3000)
                if text and not first_user_text:
                    first_user_text = text
                if text and total_sample_chars < sample_cap:
                    remaining = sample_cap - total_sample_chars
                    clip = text[:remaining]
                    text_samples.append(clip)
                    total_sample_chars += len(clip)
                continue

            if role == "assistant":
                assistant_count += 1
                stop_reason = msg.get("stopReason")
                if stop_reason in ("stop", "toolUse"):
                    assistant_success_count += 1
                if stop_reason == "max_tokens":
                    saw_max_tokens = True
                if stop_reason == "error" or msg.get("errorMessage"):
                    assistant_error_count += 1

                usage = msg.get("usage") if isinstance(msg.get("usage"), dict) else {}
                input_t = as_int(usage.get("input"), 0)
                output_t = as_int(usage.get("output"), 0)
                cache_r = as_int(usage.get("cacheRead"), 0)
                cache_w = as_int(usage.get("cacheWrite"), 0)
                total_t = as_int(usage.get("totalTokens"), 0)
                if total_t <= 0:
                    total_t = input_t + output_t + cache_r + cache_w

                usage_input += input_t
                usage_output += output_t
                usage_cache_read += cache_r
                usage_cache_write += cache_w
                usage_total += total_t

                model = msg.get("model")
                if isinstance(model, str) and model:
                    model_tokens[model] += total_t
                elif last_model:
                    model_tokens[last_model] += total_t

                names = parse_tool_calls(msg.get("content"))
                if names:
                    for n in names:
                        tool_calls[n] += 1
                    if total_t > 0:
                        share = float(total_t) / float(len(names))
                        for n in names:
                            tool_tokens[n] += share
                continue

            if role == "toolResult":
                is_error = bool(msg.get("isError")) or bool(obj.get("isError"))
                if is_error:
                    tool_result_error_count += 1
                continue

    inferred_key, inferred_cron_name = infer_key_from_text(first_user_text)
    return {
        "sessionId": session_id,
        "path": str(path),
        "lineCount": line_count,
        "firstTs": first_ts,
        "lastTs": last_ts,
        "firstUserText": first_user_text,
        "textBlob": "\n".join(text_samples),
        "inferredKey": inferred_key,
        "inferredCronName": inferred_cron_name,
        "usage": {
            "input": usage_input,
            "output": usage_output,
            "cacheRead": usage_cache_read,
            "cacheWrite": usage_cache_write,
            "total": usage_total,
        },
        "assistantCount": assistant_count,
        "assistantSuccessCount": assistant_success_count,
        "assistantErrorCount": assistant_error_count,
        "toolResultErrorCount": tool_result_error_count,
        "sawMaxTokens": saw_max_tokens,
        "toolCalls": dict(tool_calls),
        "toolTokens": dict(tool_tokens),
        "modelTokens": dict(model_tokens),
        "lastModel": last_model,
    }


def build_session_record(
    parsed: dict[str, Any],
    meta: SessionMeta | None,
    cron_jobs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    session_id = parsed["sessionId"]
    first_user_text = parsed["firstUserText"] or ""
    session_key = meta.session_key if meta else parsed.get("inferredKey")
    if not session_key and MESSAGE_ID_STYLE_RE.match(first_user_text):
        session_key = "agent:main:main"

    session_type = detect_session_type(session_key, first_user_text)
    cron_id = extract_cron_id(session_key, first_user_text)
    cron_job = cron_jobs.get(cron_id) if cron_id else None

    label = meta.label if (meta and meta.label) else None
    if not label and session_type == "cron" and cron_job:
        label = f"Cron: {cron_job.get('name', cron_id)}"
    if not label and session_type == "main":
        label = "main session"
    if not label and session_type == "subagent":
        label = "subagent session"
    if not label and parsed.get("inferredCronName"):
        label = str(parsed.get("inferredCronName"))
    if not label and session_key:
        label = session_key

    model_from_usage = None
    model_tokens = parsed.get("modelTokens", {})
    if isinstance(model_tokens, dict) and model_tokens:
        model_from_usage = max(model_tokens.items(), key=lambda kv: kv[1])[0]

    model = model_from_usage or (meta.model if meta else None) or parsed.get("lastModel") or "unknown"

    usage = parsed["usage"]
    transcript_total = as_int(usage.get("total"), 0)
    transcript_input = as_int(usage.get("input"), 0)
    transcript_output = as_int(usage.get("output"), 0)
    meta_total = meta.total_tokens if (meta and meta.total_tokens is not None) else 0
    meta_input = meta.input_tokens if (meta and meta.input_tokens is not None) else 0
    meta_output = meta.output_tokens if (meta and meta.output_tokens is not None) else 0

    total_tokens = max(transcript_total, as_int(meta_total, 0))
    input_tokens = max(transcript_input, as_int(meta_input, 0))
    output_tokens = max(transcript_output, as_int(meta_output, 0))

    first_ts = parsed.get("firstTs")
    last_ts = parsed.get("lastTs")
    if isinstance(first_ts, datetime) and isinstance(last_ts, datetime):
        duration_seconds = max(0, int((last_ts - first_ts).total_seconds()))
    else:
        duration_seconds = 0

    outcome = "success"
    error_count = as_int(parsed.get("assistantErrorCount"), 0) + as_int(parsed.get("toolResultErrorCount"), 0)
    if error_count > 0 and as_int(parsed.get("assistantSuccessCount"), 0) == 0:
        outcome = "failure"
    elif error_count > 0 or bool(parsed.get("sawMaxTokens")):
        outcome = "partial"

    text_blob = "\n".join(
        [
            session_key or "",
            label or "",
            first_user_text,
            parsed.get("textBlob", ""),
            (cron_job or {}).get("name", ""),
            (cron_job or {}).get("payload_text", ""),
        ]
    )
    client = detect_client(text_blob)
    category = classify_category(session_type, session_key, label, first_user_text, cron_job)

    raw_tool_tokens = parsed.get("toolTokens", {})
    tools: dict[str, int] = {}
    if isinstance(raw_tool_tokens, dict):
        for name, value in raw_tool_tokens.items():
            if not isinstance(name, str):
                continue
            tok = as_int(value, 0)
            if tok > 0:
                tools[name] = tok

    start_dt = first_ts if isinstance(first_ts, datetime) else None
    end_dt = last_ts if isinstance(last_ts, datetime) else None
    updated_dt = (
        datetime.fromtimestamp(meta.updated_at_ms / 1000.0, tz=timezone.utc)
        if (meta and meta.updated_at_ms)
        else None
    )

    date_ref = end_dt or start_dt or updated_dt
    date_str = date_ref.astimezone().date().isoformat() if date_ref else datetime.now().date().isoformat()

    return {
        "date": date_str,
        "sessionId": session_id,
        "sessionKey": session_key or f"unknown:{session_id}",
        "type": session_type,
        "label": label or "",
        "model": model,
        "totalTokens": total_tokens,
        "inputTokens": input_tokens,
        "outputTokens": output_tokens,
        "duration": format_duration(duration_seconds),
        "durationSeconds": duration_seconds,
        "category": category,
        "client": client,
        "tools": tools,
        "outcome": outcome,
        "startedAt": start_dt.isoformat() if start_dt else None,
        "endedAt": end_dt.isoformat() if end_dt else None,
        "updatedAt": updated_dt.isoformat() if updated_dt else None,
        "sourcePath": parsed.get("path"),
    }


def within_period(session: dict[str, Any], cutoff: datetime) -> bool:
    for field in ("endedAt", "startedAt", "updatedAt"):
        value = session.get(field)
        dt = parse_iso_timestamp(value)
        if dt is not None:
            return dt >= cutoff
    return False


def build_totals(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    by_category = Counter()
    by_client = Counter()
    by_tool = Counter()
    by_model = Counter()
    by_outcome = Counter()

    total_tokens = 0
    total_input = 0
    total_output = 0

    for s in sessions:
        tok = as_int(s.get("totalTokens"), 0)
        inp = as_int(s.get("inputTokens"), 0)
        out = as_int(s.get("outputTokens"), 0)
        total_tokens += tok
        total_input += inp
        total_output += out

        by_category[str(s.get("category") or "unknown")] += tok
        by_client[str(s.get("client") or "unknown")] += tok
        by_model[str(s.get("model") or "unknown")] += tok
        by_outcome[str(s.get("outcome") or "unknown")] += 1

        tools = s.get("tools")
        if isinstance(tools, dict):
            for name, value in tools.items():
                by_tool[str(name)] += as_int(value, 0)

    return {
        "totalTokens": total_tokens,
        "totalInputTokens": total_input,
        "totalOutputTokens": total_output,
        "sessionCount": len(sessions),
        "byCategory": dict(by_category),
        "byClient": dict(by_client),
        "byTool": dict(by_tool),
        "byModel": dict(by_model),
        "byOutcome": dict(by_outcome),
    }


def build_opportunities(report: dict[str, Any]) -> list[str]:
    totals = report.get("totals", {})
    total_tokens = as_int(totals.get("totalTokens"), 0)
    if total_tokens <= 0:
        return []

    by_tool = totals.get("byTool", {})
    by_category = totals.get("byCategory", {})
    opportunities: list[str] = []

    def share(bucket: dict[str, Any], key: str) -> float:
        return float(as_int(bucket.get(key), 0)) / float(total_tokens) if total_tokens else 0.0

    if share(by_tool, "summarize") >= 0.20:
        opportunities.append("High summarize usage. Consider tighter transcript limits and chunked extraction.")
    if share(by_tool, "web_fetch") >= 0.15:
        opportunities.append("High web_fetch usage. Reduce maxChars and avoid full-page dumps.")
    if share(by_tool, "browser") >= 0.15:
        opportunities.append("High browser usage. Limit DOM snapshots and retry loops.")
    if share(by_tool, "read") >= 0.15:
        opportunities.append("High read usage. Narrow file reads and avoid repeated large context files.")
    if share(by_category, "content_generation") >= 0.60:
        opportunities.append("Content generation dominates usage. Prioritize optimization there first.")

    outcomes = totals.get("byOutcome", {})
    partial = as_int(outcomes.get("partial"), 0)
    failure = as_int(outcomes.get("failure"), 0)
    total_sessions = as_int(totals.get("sessionCount"), 0)
    if total_sessions > 0 and (partial + failure) / total_sessions >= 0.25:
        opportunities.append("Many sessions are partial/failure. Reducing retries and failure loops can save tokens.")

    return opportunities


def sorted_items(d: dict[str, Any]) -> list[tuple[str, int]]:
    pairs = [(str(k), as_int(v, 0)) for k, v in d.items()]
    return sorted(pairs, key=lambda kv: kv[1], reverse=True)


def render_table_section(title: str, items: list[tuple[str, int]], total_tokens: int, limit: int = 10) -> list[str]:
    lines = [title + ":"]
    if not items:
        lines.append("  (none)")
        return lines
    for name, value in items[:limit]:
        percent = pct(value, total_tokens)
        flag = "  HIGH" if percent >= 25.0 else ""
        lines.append(f"  {name:<24} {value:>10,} ({percent:>5.1f}%){flag}")
    return lines


def render_text_report(report: dict[str, Any], breakdown: set[str]) -> str:
    totals = report["totals"]
    sessions = report["sessions"]
    total_tokens = as_int(totals.get("totalTokens"), 0)

    period = report.get("period", "")
    lines: list[str] = []
    lines.append(f"TOKEN USAGE REPORT ({period})")
    lines.append("=" * 40)
    lines.append("")
    lines.append(f"TOTAL: {total_tokens:,} tokens across {len(sessions)} sessions")
    lines.append(f"INPUT: {as_int(totals.get('totalInputTokens'), 0):,}  OUTPUT: {as_int(totals.get('totalOutputTokens'), 0):,}")
    lines.append("")

    if "category" in breakdown:
        lines.extend(render_table_section("BY CATEGORY", sorted_items(totals.get("byCategory", {})), total_tokens))
        lines.append("")
    if "client" in breakdown:
        lines.extend(render_table_section("BY CLIENT", sorted_items(totals.get("byClient", {})), total_tokens))
        lines.append("")
    if "tools" in breakdown:
        lines.extend(render_table_section("BY TOOL", sorted_items(totals.get("byTool", {})), total_tokens))
        lines.append("")
    if "model" in breakdown:
        lines.extend(render_table_section("BY MODEL", sorted_items(totals.get("byModel", {})), total_tokens))
        lines.append("")

    lines.append("TOP TOKEN CONSUMERS:")
    if sessions:
        top = sorted(sessions, key=lambda s: as_int(s.get("totalTokens"), 0), reverse=True)[:10]
        for s in top:
            name = short_label(s)
            lines.append(f"  {name:<32} {as_int(s.get('totalTokens'), 0):>10,}")
    else:
        lines.append("  (none)")
    lines.append("")

    opportunities = report.get("opportunities", [])
    lines.append("OPTIMIZATION OPPORTUNITIES:")
    if opportunities:
        for item in opportunities:
            lines.append(f"  - {item}")
    else:
        lines.append("  - No obvious hotspots in this window.")

    return "\n".join(lines).rstrip() + "\n"


def write_output(content: str, output_path: Path | None) -> None:
    if output_path is None:
        print(content, end="")
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    eprint(f"Wrote output to {output_path}")


def build_report(
    sessions: list[dict[str, Any]],
    period_label: str,
    generated_at: datetime,
) -> dict[str, Any]:
    sessions_sorted = sorted(
        sessions,
        key=lambda s: (parse_iso_timestamp(s.get("endedAt")) or parse_iso_timestamp(s.get("updatedAt")) or datetime.min.replace(tzinfo=timezone.utc)),
        reverse=True,
    )
    totals = build_totals(sessions_sorted)
    report = {
        "date": generated_at.astimezone().date().isoformat(),
        "generatedAt": generated_at.astimezone().isoformat(),
        "period": period_label,
        "sessions": sessions_sorted,
        "totals": totals,
    }
    report["opportunities"] = build_opportunities(report)
    return report


def session_matches_filter(session: dict[str, Any], query: str) -> bool:
    q = query.strip().lower()
    if not q:
        return False
    session_id = str(session.get("sessionId", "")).lower()
    key = str(session.get("sessionKey", "")).lower()
    if q == session_id or q == key:
        return True
    if key.startswith(q + ":run:"):
        return True
    if q in key:
        return True
    label = str(session.get("label", "")).lower()
    if q in label:
        return True
    return False


def parse_breakdown(value: str | None) -> set[str]:
    valid = {"tools", "category", "client", "model"}
    if not value:
        return {"tools", "category", "client", "model"}
    parts = {p.strip().lower() for p in value.split(",") if p.strip()}
    selected = parts & valid
    if not selected:
        raise ValueError("Invalid breakdown. Use a comma list of: tools,category,client,model")
    return selected


def discover_transcripts(sessions_dir: Path) -> list[Path]:
    if not sessions_dir.exists():
        return []
    return sorted(p for p in sessions_dir.iterdir() if p.suffix.lower() == ".jsonl" and p.is_file())


def maybe_save_snapshot(report: dict[str, Any], save: bool, daily_dir: Path) -> Path | None:
    if not save:
        return None
    daily_dir.mkdir(parents=True, exist_ok=True)
    date_str = report.get("date") or datetime.now().date().isoformat()
    out_path = daily_dir / f"{date_str}.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=False), encoding="utf-8")
    return out_path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze OpenClaw token usage from local transcripts.")
    p.add_argument("--period", default="7d", help="Time window (e.g. 1d, 7d, 30d, 12h). Default: 7d")
    p.add_argument("--breakdown", default=None, help="Comma list: tools,category,client,model")
    p.add_argument("--session", default=None, help="Analyze a specific session key/id (supports prefix match for :run sessions)")
    p.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    p.add_argument("--output", default=None, help="Write output to file path instead of stdout")
    p.add_argument("--save", action="store_true", help="Save daily JSON snapshot to token-usage/daily/YYYY-MM-DD.json")

    p.add_argument("--sessions-dir", default=str(DEFAULT_SESSIONS_DIR), help=argparse.SUPPRESS)
    p.add_argument("--sessions-index", default=str(DEFAULT_SESSIONS_INDEX), help=argparse.SUPPRESS)
    p.add_argument("--cron-jobs", default=str(DEFAULT_CRON_JOBS), help=argparse.SUPPRESS)
    p.add_argument("--daily-dir", default=str(DEFAULT_DAILY_DIR), help=argparse.SUPPRESS)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        period_delta = parse_period(args.period)
        breakdown = parse_breakdown(args.breakdown)
    except ValueError as exc:
        eprint(f"Error: {exc}")
        return 2

    sessions_dir = Path(args.sessions_dir)
    sessions_index = Path(args.sessions_index)
    cron_jobs_path = Path(args.cron_jobs)
    daily_dir = Path(args.daily_dir)
    output_path = Path(args.output) if args.output else None

    now = datetime.now(timezone.utc)
    cutoff = now - period_delta

    id_to_meta, _ = load_sessions_index(sessions_index)
    cron_jobs = load_cron_jobs(cron_jobs_path)

    transcript_paths = discover_transcripts(sessions_dir)
    if not transcript_paths:
        eprint(f"No transcript files found in {sessions_dir}")
        return 1

    session_records: list[dict[str, Any]] = []
    for transcript in transcript_paths:
        parsed = analyze_transcript(transcript)
        meta = id_to_meta.get(parsed["sessionId"])
        record = build_session_record(parsed, meta, cron_jobs)
        session_records.append(record)

    if args.session:
        filtered = [s for s in session_records if session_matches_filter(s, args.session)]
        period_label = f"Session filter: {args.session}"
    else:
        filtered = [s for s in session_records if within_period(s, cutoff)]
        period_label = f"Past {args.period}"

    report = build_report(filtered, period_label=period_label, generated_at=now)

    snapshot_path = maybe_save_snapshot(report, args.save, daily_dir)
    if snapshot_path:
        eprint(f"Saved daily snapshot: {snapshot_path}")

    if args.format == "json":
        content = json.dumps(report, indent=2, sort_keys=False) + "\n"
    else:
        content = render_text_report(report, breakdown)

    write_output(content, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
