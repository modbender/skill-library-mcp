#!/usr/bin/env python3
"""
PECO loop daemon for OpenClaw infinite execution.

Implements PLAN -> EXECUTE -> CHECK -> OPTIMIZE loop with:
- strict structured output parsing ([PHASE:...] + ```json block)
- direct Gateway API calls to /v1/chat/completions
- manual override file support
- simple circuit breaker
- optional Feishu webhook notifications (with mock/log fallback)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest
import re


PHASES = ("PLAN", "EXECUTE", "CHECK", "OPTIMIZE")
DEFAULT_NEXT = {
    "PLAN": "EXECUTE",
    "EXECUTE": "CHECK",
    "CHECK": "OPTIMIZE",
    "OPTIMIZE": "PLAN",
}
ALLOWED_TRANSITIONS = {
    "PLAN": {"PLAN", "EXECUTE"},
    "EXECUTE": {"EXECUTE", "CHECK"},
    "CHECK": {"CHECK", "OPTIMIZE", "PLAN"},
    "OPTIMIZE": {"OPTIMIZE", "PLAN"},
}
DECISIONS = {"continue", "retry", "halt"}

PHASE_TAG_RE = re.compile(r"\[PHASE:([A-Za-z_]+)\]")
HUMAN_TASK_TAG_RE = re.compile(r"\[HUMAN_TASK:(.*?)\]", re.IGNORECASE | re.DOTALL)
JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.IGNORECASE | re.DOTALL)
BACKLOG_TASK_RE = re.compile(r"task=(.*)$")

FEISHU_DEFAULT_APP_TOKEN = ""
FEISHU_DEFAULT_PROGRESS_TABLE_ID = ""
FEISHU_DEFAULT_HUMAN_TABLE_ID = ""

GATEWAY_BASE_URL = "http://127.0.0.1:17369"
GATEWAY_CONFIG_CANDIDATES = (
    Path("/root/.openclaw/openclaw.json"),
    Path.home() / ".openclaw" / "openclaw.json",
)

SYSTEM_PROMPT_TEMPLATE = """You are running inside a PECO (PLAN -> EXECUTE -> CHECK -> OPTIMIZE) loop.
Keep your original OpenClaw personality, voice, and reasoning style. Do not flatten into robotic tone.
The PECO contract only constrains structure and loop discipline.

Output contract:
1) Include exactly one phase tag line: [PHASE:PLAN|EXECUTE|CHECK|OPTIMIZE]
2) Optionally include one human-assistance tag when needed: [HUMAN_TASK:<task>]
3) Include exactly one JSON block in ```json ... ```
4) JSON keys (required):
   - phase (string)
   - next_phase (string)
   - decision (continue|retry|halt)
   - confidence (0..1)
   - summary (string)
   - phase_payload (object)
   - risks (array)
5) Keep output concise, concrete, and machine-parseable.
6) EXECUTE phase must use 1-2 fast actions only; avoid long scans or commands over 2 minutes.
7) If blocked by human-only requirements, continue non-blocked work and emit [HUMAN_TASK:...].
8) HUMAN_TASK must be async-friendly: no tight deadlines, avoid "reply in 10 minutes", prefer one-time durable setup/actions.
9) decision=halt only when no meaningful progress path exists.
10) Autonomy-first rule: when a choice can be made safely with available tools/resources, decide and execute directly without asking human.
11) Emit [HUMAN_TASK:...] only for truly human-exclusive resources (e.g., OTP/device/real-world approvals) after exhausting practical alternatives.
12) When repeated_human_blocker_count >= 2, increase divergent thinking (>=5 options) and execute at least one non-human workaround attempt.
13) When repeated_human_blocker_count >= 3 for the same blocker, set decision=halt, summarize blocker clearly, and request manager escalation to notify human.
"""

PHASE_PROMPTS = {
    "PLAN": """PLAN framework (infinite-task mode):
- RECALL: Summarize durable context from prior iterations (what worked, what failed, constraints).
- DIVERGE: Generate multiple candidate paths (>=3), including conservative, aggressive, and fallback routes.
- EVALUATE: Score options by expected impact, cost, risk, dependency on humans, and reversibility.
- CONVERGE: Pick 1 primary path + 1 backup path with explicit acceptance checks.
- CYCLE: Define short-loop actions that can finish in this iteration and feed the next phase.

PLAN output expectations in phase_payload:
- objective_slice: this-iteration objective slice
- candidates: compact list of evaluated plans
- chosen_plan: main plan + backup plan
- acceptance_checks: measurable checks for CHECK phase
- blocked_by_human: true/false + reason
- if repeated_human_blocker_count >= 2, include expanded_candidates (>=5) focused on non-human workarounds
""",
    "EXECUTE": """EXECUTE framework (infinite-task mode):
- Execute the chosen plan with minimal, high-signal actions.
- Prefer smallest verifiable step over broad exploratory work.
- Prioritize reusing existing tools/scripts/assets before creating new ones.
- Capture evidence and artifacts (paths, outputs, key facts).
- If partial failure occurs, degrade gracefully and continue with backup path.
- Keep loop momentum: never stall waiting for ideal conditions.

EXECUTE output expectations in phase_payload:
- actions_run: list of concrete actions executed
- artifacts: created/updated outputs or observations
- blockers: encountered blockers + mitigation done
- residual_tasks: what remains for later
""",
    "CHECK": """CHECK framework (infinite-task mode):
- Validate outcomes against acceptance checks from PLAN.
- Measure objective delta (how much closer vs previous iteration).
- Distinguish signal from noise; avoid self-congratulation.
- Classify failures: data gap / tool failure / strategy mismatch / human dependency.
- Recalibrate confidence based on evidence quality.

CHECK output expectations in phase_payload:
- acceptance_results: pass/fail per check
- objective_delta: qualitative + compact quantitative estimate
- failure_taxonomy: categorized issues
- carry_forward: facts or assets to preserve for next cycle
""",
    "OPTIMIZE": """OPTIMIZE framework (infinite-task mode):
- Identify bottlenecks across strategy, tooling, and workflow.
- Convert repeatable work into reusable assets (scripts/templates/playbooks).
- Reduce future cost and latency without sacrificing safety.
- Improve robustness (fallbacks, retries, clearer checkpoints).
- Select one leverage improvement to apply next cycle.

OPTIMIZE output expectations in phase_payload:
- bottlenecks: ranked bottlenecks
- leverage_changes: practical optimizations with expected gain
- automation_candidates: tasks to script/templatize
- next_cycle_policy: one policy to enforce next PLAN
""",
}


class LoopError(Exception):
    pass


class AgentCallError(LoopError):
    pass


class ParseError(LoopError):
    pass


@dataclass
class ParsedResponse:
    phase: str
    next_phase: str
    decision: str
    confidence: float
    summary: str
    human_task: str
    phase_payload: Dict[str, Any]
    risks: List[Any]
    raw_json: Dict[str, Any]


@dataclass
class LoopState:
    objective: str
    iteration: int = 0
    phase: str = "PLAN"
    session: str = ""
    halted: bool = False
    consecutive_failures: int = 0
    repeated_signature_count: int = 0
    last_signature: str = ""
    last_phase_summary: str = ""
    last_human_task: str = ""
    last_human_task_signature: str = ""
    repeated_human_blocker_count: int = 0
    last_response_excerpt: str = ""
    updated_at: str = ""


class FeishuSync:
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        app_token: str,
        progress_table_id: str,
        human_table_id: str,
        base_url: str,
        timeout: int,
        logger: logging.Logger,
    ) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token
        self.progress_table_id = progress_table_id
        self.human_table_id = human_table_id
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = logger
        self._tenant_access_token = ""
        self._tenant_expire_at = 0.0
        self._progress_field_map: Dict[str, str] = {}
        self._human_field_map: Dict[str, str] = {}
        self._consumed_ids: set[str] = set()

    def _as_text(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            parts = [self._as_text(item) for item in value]
            parts = [item for item in parts if item]
            return ", ".join(parts)
        if isinstance(value, dict):
            for key in ("text", "name", "label", "content", "value"):
                if key in value:
                    text = self._as_text(value.get(key))
                    if text:
                        return text
            return json.dumps(value, ensure_ascii=False)
        return str(value).strip()

    def _as_bool(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        text = self._as_text(value).lower()
        return text in {"true", "1", "yes", "y", "是", "已读取", "已读", "checked"}

    def _pick_field(
        self, available: List[str], env_key: str, candidates: List[str]
    ) -> str:
        preferred = os.environ.get(env_key, "").strip()
        lower_map = {name.lower(): name for name in available}
        if preferred:
            if preferred in available:
                return preferred
            if preferred.lower() in lower_map:
                return lower_map[preferred.lower()]

        for candidate in candidates:
            if candidate in available:
                return candidate
            if candidate.lower() in lower_map:
                return lower_map[candidate.lower()]

        merged = [preferred] if preferred else []
        merged.extend(candidates)
        for candidate in merged:
            if not candidate:
                continue
            candidate_lower = candidate.lower()
            for name in available:
                name_lower = name.lower()
                if candidate_lower in name_lower or name_lower in candidate_lower:
                    return name
        return ""

    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        auth: bool = True,
        retries: int = 2,
    ) -> Dict[str, Any]:
        query = ""
        if params:
            cleaned = {
                key: value for key, value in params.items() if value not in (None, "")
            }
            if cleaned:
                query = "?" + urlparse.urlencode(cleaned)
        url = f"{self.base_url}{path}{query}"

        headers = {"Content-Type": "application/json; charset=utf-8"}
        if auth:
            headers["Authorization"] = f"Bearer {self._ensure_token()}"
        data = None
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        last_error = ""
        for attempt in range(retries + 1):
            req = urlrequest.Request(url, data=data, headers=headers, method=method)
            try:
                with urlrequest.urlopen(req, timeout=self.timeout) as resp:
                    text = resp.read().decode("utf-8")
                result = json.loads(text)
                if result.get("code", 0) != 0:
                    code = result.get("code")
                    msg = result.get("msg")
                    raise RuntimeError(f"Feishu API error code={code} msg={msg}")
                return result
            except Exception as exc:
                last_error = str(exc)
                if attempt < retries:
                    time.sleep(1 + attempt)
                    continue
                break
        raise RuntimeError(last_error or "Unknown Feishu request error")

    def _ensure_token(self) -> str:
        now = time.time()
        if self._tenant_access_token and now < self._tenant_expire_at - 60:
            return self._tenant_access_token

        result = self._request(
            method="POST",
            path="/open-apis/auth/v3/tenant_access_token/internal",
            payload={"app_id": self.app_id, "app_secret": self.app_secret},
            auth=False,
            retries=2,
        )
        token = result.get("tenant_access_token", "")
        expire = int(result.get("expire", 7200))
        if not token:
            raise RuntimeError("Feishu tenant_access_token missing")
        self._tenant_access_token = token
        self._tenant_expire_at = time.time() + expire
        return token

    def _list_table_fields(self, table_id: str) -> List[str]:
        names: List[str] = []
        page_token = ""
        while True:
            result = self._request(
                method="GET",
                path=f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/fields",
                params={"page_size": 200, "page_token": page_token},
                auth=True,
                retries=2,
            )
            data = result.get("data", {})
            items = data.get("items", []) or []
            for item in items:
                field_name = item.get("field_name")
                if isinstance(field_name, str) and field_name:
                    names.append(field_name)
            if not data.get("has_more"):
                break
            page_token = data.get("page_token", "")
            if not page_token:
                break
        return names

    def _ensure_field_maps(self) -> None:
        if not self._progress_field_map:
            available = self._list_table_fields(self.progress_table_id)
            self._progress_field_map = {
                "session": self._pick_field(
                    available,
                    "FEISHU_PROGRESS_FIELD_SESSION",
                    ["Session", "session", "会话", "会话ID", "session_id"],
                ),
                "iteration": self._pick_field(
                    available,
                    "FEISHU_PROGRESS_FIELD_ITERATION",
                    ["Iteration", "iteration", "轮次", "迭代"],
                ),
                "phase": self._pick_field(
                    available,
                    "FEISHU_PROGRESS_FIELD_PHASE",
                    ["Phase", "phase", "阶段"],
                ),
                "summary": self._pick_field(
                    available,
                    "FEISHU_PROGRESS_FIELD_SUMMARY",
                    ["Summary", "summary", "摘要", "结论", "结果"],
                ),
                "status": self._pick_field(
                    available,
                    "FEISHU_PROGRESS_FIELD_STATUS",
                    ["Status", "status", "状态"],
                ),
                "timestamp": self._pick_field(
                    available,
                    "FEISHU_PROGRESS_FIELD_TIMESTAMP",
                    ["Timestamp", "timestamp", "时间", "时间戳", "创建时间"],
                ),
            }

        if not self._human_field_map:
            available = self._list_table_fields(self.human_table_id)
            desc = self._pick_field(
                available,
                "FEISHU_HUMAN_FIELD_DESC",
                ["问题描述", "任务描述", "需求", "描述", "问题", "内容", "HumanTask"],
            )
            status = self._pick_field(
                available,
                "FEISHU_HUMAN_FIELD_STATUS",
                ["状态", "Status", "status"],
            )
            read_flag = self._pick_field(
                available,
                "FEISHU_HUMAN_FIELD_READ",
                ["Agent已读取", "AgentRead", "Agent Read", "已读取", "机器人已读取"],
            )
            resolution = self._pick_field(
                available,
                "FEISHU_HUMAN_FIELD_RESOLUTION",
                ["解决方案", "处理结果", "回复", "备注", "完成说明", "解决内容"],
            )

            if not desc:
                protected = {
                    field for field in [status, read_flag, resolution] if field
                }
                for name in available:
                    if name not in protected:
                        desc = name
                        break

            self._human_field_map = {
                "desc": desc,
                "status": status,
                "read": read_flag,
                "resolution": resolution,
                "timestamp": self._pick_field(
                    available,
                    "FEISHU_HUMAN_FIELD_TIMESTAMP",
                    [
                        "时间",
                        "时间戳",
                        "创建时间",
                        "提出时间",
                        "Timestamp",
                        "timestamp",
                    ],
                ),
            }

    def _create_record(self, table_id: str, fields: Dict[str, Any]) -> bool:
        if not fields:
            return False
        try:
            self._request(
                method="POST",
                path=f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records",
                payload={"fields": fields},
                auth=True,
                retries=2,
            )
            return True
        except Exception as exc:
            self.logger.warning("Feishu create record failed: %s", exc)
            return False

    def _update_record(
        self, table_id: str, record_id: str, fields: Dict[str, Any]
    ) -> bool:
        if not fields:
            return False
        try:
            self._request(
                method="PUT",
                path=f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}",
                payload={"fields": fields},
                auth=True,
                retries=2,
            )
            return True
        except Exception as exc:
            self.logger.warning("Feishu update record failed: %s", exc)
            return False

    def _list_records(
        self, table_id: str, page_size: int = 200
    ) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        page_token = ""
        while True:
            result = self._request(
                method="GET",
                path=f"/open-apis/bitable/v1/apps/{self.app_token}/tables/{table_id}/records",
                params={"page_size": page_size, "page_token": page_token},
                auth=True,
                retries=2,
            )
            data = result.get("data", {})
            items = data.get("items", []) or []
            records.extend(items)
            if not data.get("has_more"):
                break
            page_token = data.get("page_token", "")
            if not page_token:
                break
        return records

    def append_progress(
        self,
        session: str,
        iteration: int,
        phase: str,
        summary: str,
        status: str,
    ) -> bool:
        try:
            self._ensure_field_maps()
            mapping = self._progress_field_map
            fields: Dict[str, Any] = {}
            if mapping.get("session"):
                fields[mapping["session"]] = session
            if mapping.get("iteration"):
                fields[mapping["iteration"]] = iteration
            if mapping.get("phase"):
                fields[mapping["phase"]] = phase
            if mapping.get("summary"):
                fields[mapping["summary"]] = summary[:1000]
            if mapping.get("status"):
                fields[mapping["status"]] = status
            if mapping.get("timestamp"):
                fields[mapping["timestamp"]] = int(time.time() * 1000)

            if not fields and mapping.get("summary"):
                fields[mapping["summary"]] = f"[{phase}/{status}] {summary[:900]}"
            if not fields:
                self.logger.warning("Feishu progress mapping empty; skip append")
                return False
            return self._create_record(self.progress_table_id, fields)
        except Exception as exc:
            self.logger.warning("Feishu append_progress failed: %s", exc)
            return False

    def append_human_task(self, desc: str) -> bool:
        human_desc = desc.strip()
        if not human_desc:
            return False
        try:
            human_signature = normalize_human_task(human_desc)
            if self.has_human_task(human_signature):
                self.logger.info(
                    "Skip duplicated Feishu human task: %s", human_desc[:200]
                )
                return False

            self._ensure_field_maps()
            mapping = self._human_field_map
            fields: Dict[str, Any] = {}
            if mapping.get("desc"):
                fields[mapping["desc"]] = human_desc[:1500]
            if mapping.get("status"):
                fields[mapping["status"]] = "待处理"
            if mapping.get("read"):
                fields[mapping["read"]] = False
            if mapping.get("timestamp"):
                fields[mapping["timestamp"]] = int(time.time() * 1000)
            if not fields:
                self.logger.warning("Feishu human task mapping empty; skip append")
                return False
            return self._create_record(self.human_table_id, fields)
        except Exception as exc:
            self.logger.warning("Feishu append_human_task failed: %s", exc)
            return False

    def has_human_task(self, task_signature: str) -> bool:
        if not task_signature:
            return False

        try:
            self._ensure_field_maps()
            desc_field = self._human_field_map.get("desc", "")
            if not desc_field:
                return False

            records = self._list_records(self.human_table_id)
            for record in records:
                fields = record.get("fields", {})
                if not isinstance(fields, dict):
                    continue
                existing_desc = self._as_text(fields.get(desc_field))
                if normalize_human_task(existing_desc) == task_signature:
                    return True
        except Exception as exc:
            self.logger.warning("Feishu has_human_task check failed: %s", exc)
        return False

    def fetch_and_consume_resolved_tasks(self) -> str:
        try:
            self._ensure_field_maps()
            mapping = self._human_field_map
            status_field = mapping.get("status", "")
            read_field = mapping.get("read", "")
            desc_field = mapping.get("desc", "")
            resolution_field = mapping.get("resolution", "")
            records = self._list_records(self.human_table_id)
            lines: List[str] = []
            resolved_ids: List[str] = []

            for record in records:
                record_id = self._as_text(record.get("record_id"))
                if not record_id:
                    continue

                fields = record.get("fields", {})
                if not isinstance(fields, dict):
                    continue

                status_text = (
                    self._as_text(fields.get(status_field)).lower()
                    if status_field
                    else ""
                )
                is_resolved = status_text in {
                    "已解决",
                    "已完成",
                    "完成",
                    "done",
                    "resolved",
                }
                if not is_resolved:
                    continue

                already_read = (
                    self._as_bool(fields.get(read_field))
                    if read_field
                    else (record_id in self._consumed_ids)
                )
                if already_read:
                    continue

                desc_text = self._as_text(fields.get(desc_field)) if desc_field else ""
                resolution_text = (
                    self._as_text(fields.get(resolution_field))
                    if resolution_field
                    else ""
                )
                if not resolution_text:
                    resolution_text = self._as_text(fields)

                line = f"- 人类已解决[{record_id}]"
                if desc_text:
                    line += f" 问题: {desc_text}"
                line += f" | 方案: {resolution_text[:1200]}"
                lines.append(line)
                resolved_ids.append(record_id)

            if not lines:
                return ""

            for record_id in resolved_ids:
                updated = False
                if read_field:
                    updated = self._update_record(
                        table_id=self.human_table_id,
                        record_id=record_id,
                        fields={read_field: True},
                    )
                if updated or not read_field:
                    self._consumed_ids.add(record_id)

            return "\n".join(lines)
        except Exception as exc:
            self.logger.warning(
                "Feishu fetch_and_consume_resolved_tasks failed: %s", exc
            )
            return ""


def load_feishu_config(logger: logging.Logger) -> Optional[FeishuSync]:
    enabled_text = os.environ.get("FEISHU_ENABLED", "1").strip().lower()
    if enabled_text in {"0", "false", "no", "off"}:
        logger.info("Feishu sync disabled by FEISHU_ENABLED=%s", enabled_text)
        return None

    app_id = os.environ.get("FEISHU_APP_ID", "").strip()
    app_secret = os.environ.get("FEISHU_APP_SECRET", "").strip()
    if not app_id or not app_secret:
        logger.warning(
            "Feishu sync disabled: FEISHU_APP_ID or FEISHU_APP_SECRET missing"
        )
        return None

    app_token = os.environ.get("FEISHU_APP_TOKEN", FEISHU_DEFAULT_APP_TOKEN).strip()
    progress_table_id = os.environ.get(
        "FEISHU_PROGRESS_TABLE_ID", FEISHU_DEFAULT_PROGRESS_TABLE_ID
    ).strip()
    human_table_id = os.environ.get(
        "FEISHU_HUMAN_TABLE_ID", FEISHU_DEFAULT_HUMAN_TABLE_ID
    ).strip()
    base_url = os.environ.get("FEISHU_BASE_URL", "https://open.feishu.cn").strip()
    timeout = int(os.environ.get("FEISHU_HTTP_TIMEOUT", "10") or "10")

    sync = FeishuSync(
        app_id=app_id,
        app_secret=app_secret,
        app_token=app_token,
        progress_table_id=progress_table_id,
        human_table_id=human_table_id,
        base_url=base_url,
        timeout=timeout,
        logger=logger,
    )
    try:
        sync._ensure_token()
        logger.info(
            "Feishu sync enabled | app_token=%s progress_table=%s human_table=%s",
            app_token,
            progress_table_id,
            human_table_id,
        )
    except Exception as exc:
        logger.warning("Feishu sync initialization warning: %s", exc)
    return sync


class FeishuNotifier:
    def __init__(self, webhook_url: str, timeout: int, logger: logging.Logger) -> None:
        self.webhook_url = webhook_url.strip()
        self.timeout = timeout
        self.logger = logger

    def notify(self, title: str, body: Dict[str, Any]) -> None:
        payload_text = f"{title}\n" + json.dumps(body, ensure_ascii=False)
        if not self.webhook_url:
            self.logger.info("[MOCK_FEISHU] %s", payload_text)
            return

        payload = {
            "msg_type": "text",
            "content": {"text": payload_text[:3800]},
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urlrequest.Request(
            self.webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlrequest.urlopen(req, timeout=self.timeout) as resp:
                resp.read()
            self.logger.info("Feishu notification sent: %s", title)
        except urlerror.URLError as exc:
            self.logger.warning("Feishu notification failed (%s): %s", title, exc)
        except Exception as exc:
            self.logger.warning(
                "Unexpected Feishu notification error (%s): %s", title, exc
            )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_human_task(task: str) -> str:
    return re.sub(r"\s+", " ", task).strip().casefold()


def backlog_has_human_task(backlog_file: Path, task_signature: str) -> bool:
    if not task_signature or not backlog_file.exists():
        return False

    try:
        lines = backlog_file.read_text(encoding="utf-8").splitlines()
    except Exception:
        return False

    for line in lines:
        match = BACKLOG_TASK_RE.search(line)
        if not match:
            continue
        existing_signature = normalize_human_task(match.group(1))
        if existing_signature == task_signature:
            return True
    return False


def setup_logger(log_file: Path, level: str) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("peco_loop")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    tmp_path.replace(path)


def load_state(path: Path, objective: str, session_prefix: str) -> LoopState:
    if not path.exists():
        return LoopState(objective=objective, session=session_prefix)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return LoopState(objective=objective, session=session_prefix)

    state = LoopState(
        objective=data.get("objective") or objective,
        iteration=int(data.get("iteration", 0)),
        phase=str(data.get("phase", "PLAN")).upper(),
        session=str(data.get("session", "")),
        halted=bool(data.get("halted", False)),
        consecutive_failures=int(data.get("consecutive_failures", 0)),
        repeated_signature_count=int(data.get("repeated_signature_count", 0)),
        last_signature=str(data.get("last_signature", "")),
        last_phase_summary=str(data.get("last_phase_summary", "")),
        last_human_task=str(data.get("last_human_task", "")),
        last_human_task_signature=str(data.get("last_human_task_signature", "")),
        repeated_human_blocker_count=int(data.get("repeated_human_blocker_count", 0)),
        last_response_excerpt=str(data.get("last_response_excerpt", "")),
        updated_at=str(data.get("updated_at", "")),
    )

    if state.phase not in PHASES:
        state.phase = "PLAN"
    if not state.session:
        state.session = session_prefix
    return state


def save_state(path: Path, state: LoopState) -> None:
    state.updated_at = utc_now()
    atomic_write_json(path, asdict(state))


def read_and_clear_override(override_file: Path, logger: logging.Logger) -> str:
    if not override_file.exists():
        override_file.parent.mkdir(parents=True, exist_ok=True)
        override_file.write_text("", encoding="utf-8")
        return ""

    try:
        content = override_file.read_text(encoding="utf-8").strip()
    except Exception as exc:
        logger.warning("Failed reading override file: %s", exc)
        return ""

    if not content:
        return ""

    try:
        override_file.write_text("", encoding="utf-8")
    except Exception as exc:
        logger.warning("Failed clearing override file: %s", exc)

    logger.info("Loaded override instruction (%d chars)", len(content))
    return content


def _strip_json5_noise(raw: str) -> str:
    without_block_comments = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)
    without_line_comments = re.sub(
        r"(^|\s)//.*?$", "", without_block_comments, flags=re.MULTILINE
    )
    no_trailing_commas = re.sub(r",\s*([}\]])", r"\1", without_line_comments)
    return no_trailing_commas


def _extract_token_from_obj(data: Any) -> str:
    if not isinstance(data, dict):
        return ""
    gateway = data.get("gateway")
    if isinstance(gateway, dict):
        auth = gateway.get("auth")
        if isinstance(auth, dict):
            token = auth.get("token")
            if isinstance(token, str) and token.strip():
                return token.strip()
    token = data.get("token")
    if isinstance(token, str) and token.strip():
        return token.strip()
    return ""


def load_gateway_token() -> str:
    env_token = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "").strip()
    if env_token:
        return env_token

    for candidate in GATEWAY_CONFIG_CANDIDATES:
        if not candidate.exists():
            continue
        try:
            raw = candidate.read_text(encoding="utf-8")
        except Exception:
            continue

        try:
            parsed = json.loads(raw)
            token = _extract_token_from_obj(parsed)
            if token:
                return token
        except Exception:
            pass

        try:
            parsed = json.loads(_strip_json5_noise(raw))
            token = _extract_token_from_obj(parsed)
            if token:
                return token
        except Exception:
            pass

        match = re.search(r'"token"\s*:\s*"([^"\\]+)"', raw)
        if match and match.group(1).strip():
            return match.group(1).strip()

    raise AgentCallError(
        "Gateway token not found. Set OPENCLAW_GATEWAY_TOKEN or configure gateway.auth.token in ~/.openclaw/openclaw.json"
    )


def _extract_chat_content(response_obj: Dict[str, Any]) -> str:
    choices = response_obj.get("choices")
    if not isinstance(choices, list) or not choices:
        raise AgentCallError(
            f"Gateway response missing choices: {json.dumps(response_obj)[:400]}"
        )

    message = choices[0].get("message", {})
    if not isinstance(message, dict):
        raise AgentCallError("Gateway response message is malformed")

    content = message.get("content", "")
    if isinstance(content, str):
        text = content.strip()
        if text:
            return text
    elif isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, dict):
                text_part = item.get("text")
                if isinstance(text_part, str) and text_part.strip():
                    parts.append(text_part.strip())
            elif isinstance(item, str) and item.strip():
                parts.append(item.strip())
        text = "\n".join(parts).strip()
        if text:
            return text

    raise AgentCallError("Gateway returned empty message content")


def call_gateway_api(
    session_id: str,
    prompt: str,
    agent_id: str,
    timeout: int,
    logger: logging.Logger,
) -> str:
    token = load_gateway_token()
    url = f"{GATEWAY_BASE_URL}/v1/chat/completions"
    body = {
        "model": f"openclaw:{agent_id}",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urlrequest.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "x-openclaw-session-key": session_id,
        },
        method="POST",
    )

    logger.debug(
        "Calling gateway chat completions | agent=%s session=%s", agent_id, session_id
    )
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urlerror.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise AgentCallError(f"Gateway HTTP {exc.code}: {error_body[:500]}") from exc
    except urlerror.URLError as exc:
        raise AgentCallError(f"Gateway unreachable: {exc.reason}") from exc
    except TimeoutError as exc:
        raise AgentCallError(f"Gateway request timed out after {timeout}s") from exc
    except Exception as exc:
        raise AgentCallError(f"Gateway request failed: {exc}") from exc

    try:
        payload = json.loads(raw)
    except Exception as exc:
        raise AgentCallError(f"Invalid gateway JSON response: {raw[:400]}") from exc

    return _extract_chat_content(payload)


def parse_structured_output(raw_text: str, expected_phase: str) -> ParsedResponse:
    phase_match = PHASE_TAG_RE.search(raw_text)
    if not phase_match:
        raise ParseError("Missing [PHASE:...] tag")
    phase = phase_match.group(1).upper()
    if phase not in PHASES:
        raise ParseError(f"Unknown phase tag: {phase}")
    if phase != expected_phase:
        raise ParseError(f"Phase mismatch: expected {expected_phase}, got {phase}")

    json_match = JSON_BLOCK_RE.search(raw_text)
    if not json_match:
        raise ParseError("Missing ```json block")

    json_blob = json_match.group(1)
    try:
        data = json.loads(json_blob)
    except json.JSONDecodeError as exc:
        raise ParseError(f"Invalid JSON block: {exc}") from exc

    required_keys = {
        "phase",
        "next_phase",
        "decision",
        "confidence",
        "summary",
        "phase_payload",
        "risks",
    }
    missing = [key for key in required_keys if key not in data]
    if missing:
        raise ParseError(f"Missing required keys: {', '.join(missing)}")

    json_phase = str(data.get("phase", "")).upper()
    if json_phase != phase:
        raise ParseError(f"JSON phase mismatch: {json_phase} vs tag {phase}")

    next_phase = str(data.get("next_phase", "")).upper()
    if next_phase not in PHASES:
        raise ParseError(f"Invalid next_phase: {next_phase}")

    decision = str(data.get("decision", "")).lower()
    if decision not in DECISIONS:
        raise ParseError(f"Invalid decision: {decision}")

    try:
        confidence = float(data.get("confidence"))
    except Exception as exc:
        raise ParseError(f"Invalid confidence value: {data.get('confidence')}") from exc
    if confidence < 0 or confidence > 1:
        raise ParseError(f"Confidence out of range: {confidence}")

    summary = str(data.get("summary", "")).strip()
    if not summary:
        raise ParseError("Summary must not be empty")

    phase_payload = data.get("phase_payload")
    if not isinstance(phase_payload, dict):
        raise ParseError("phase_payload must be an object")

    risks = data.get("risks")
    if not isinstance(risks, list):
        raise ParseError("risks must be an array")

    human_task_match = HUMAN_TASK_TAG_RE.search(raw_text)
    human_task = ""
    if human_task_match:
        human_task = re.sub(r"\s+", " ", human_task_match.group(1)).strip()

    return ParsedResponse(
        phase=phase,
        next_phase=next_phase,
        decision=decision,
        confidence=confidence,
        summary=summary,
        human_task=human_task,
        phase_payload=phase_payload,
        risks=risks,
        raw_json=data,
    )


def append_human_task_backlog(
    backlog_file: Path,
    state: LoopState,
    parsed: ParsedResponse,
    logger: logging.Logger,
    notifier: FeishuNotifier,
    feishu_sync: Optional[FeishuSync],
) -> int:
    human_task = parsed.human_task.strip()
    if not human_task:
        state.last_human_task = ""
        state.last_human_task_signature = ""
        state.repeated_human_blocker_count = 0
        return 0

    task_signature = normalize_human_task(human_task)
    if task_signature == state.last_human_task_signature:
        state.repeated_human_blocker_count += 1
    else:
        state.repeated_human_blocker_count = 1
    state.last_human_task_signature = task_signature
    state.last_human_task = human_task

    if backlog_has_human_task(backlog_file, task_signature):
        logger.info("Skip duplicated local human task: %s", human_task[:200])
        return state.repeated_human_blocker_count

    alert = f"🚨 【系统求助】 Agent 遇到了能力瓶颈，请求人类协助：{human_task}"
    logger.warning(alert)
    notifier.notify(
        "PECO human assistance request",
        {
            "alert": alert,
            "session": state.session,
            "iteration": state.iteration,
            "phase": parsed.phase,
        },
    )

    backlog_file.parent.mkdir(parents=True, exist_ok=True)
    line = (
        f"[{utc_now()}] session={state.session} iteration={state.iteration} "
        f"phase={parsed.phase} task={human_task}\n"
    )
    with backlog_file.open("a", encoding="utf-8") as backlog:
        backlog.write(line)

    if feishu_sync:
        feishu_sync.append_human_task(human_task)

    return state.repeated_human_blocker_count


def merge_override_text(local_override: str, feishu_override: str) -> str:
    parts: List[str] = []
    if local_override.strip():
        parts.append(local_override.strip())
    if feishu_override.strip():
        parts.append("[FEISHU_RESOLVED_TASKS]\n" + feishu_override.strip())
    return "\n\n".join(parts)


def normalize_next_phase(
    current_phase: str, requested_next: str, logger: logging.Logger
) -> str:
    if requested_next in ALLOWED_TRANSITIONS[current_phase]:
        return requested_next
    fallback = DEFAULT_NEXT[current_phase]
    logger.warning(
        "Invalid transition %s -> %s, fallback to %s",
        current_phase,
        requested_next,
        fallback,
    )
    return fallback


def build_loop_prompt(state: LoopState, override_text: str) -> str:
    override_block = override_text if override_text else "(none)"
    phase_hint = PHASE_PROMPTS[state.phase]

    return f"""[SYSTEM CONTRACT]
{SYSTEM_PROMPT_TEMPLATE}

[LOOP CONTEXT]
- objective: {state.objective}
- iteration: {state.iteration}
- session: {state.session}
- current_phase: {state.phase}
- last_phase_summary: {state.last_phase_summary or "(none)"}
- repeated_human_blocker_count: {state.repeated_human_blocker_count}
- last_human_blocker: {state.last_human_task or "(none)"}

[OVERRIDE - HIGHEST PRIORITY]
{override_block}

[PHASE GUIDANCE]
{phase_hint}

Now execute phase {state.phase} and output strictly in the contract format.
"""


def append_manager_notification_file(
    manager_notify_file: Path, payload: Dict[str, Any], logger: logging.Logger
) -> None:
    try:
        manager_notify_file.parent.mkdir(parents=True, exist_ok=True)
        record = dict(payload)
        record["timestamp"] = utc_now()
        with manager_notify_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as exc:
        logger.warning("Failed writing manager notification file: %s", exc)


def notify_manager_about_pause(
    state: LoopState,
    args: argparse.Namespace,
    logger: logging.Logger,
    notifier: FeishuNotifier,
    manager_notify_file: Path,
    reason: str,
    source: str,
    details: str,
) -> None:
    payload = {
        "reason": reason,
        "source": source,
        "session": state.session,
        "iteration": state.iteration,
        "phase": state.phase,
        "details": details[:2000],
    }

    manager_prompt = (
        "[PAUSE REPORT]\n"
        f"source={source}\n"
        f"reason={reason}\n"
        f"session={state.session}\n"
        f"iteration={state.iteration}\n"
        f"phase={state.phase}\n"
        f"details={details}\n\n"
        "Please notify the human operator why PECO paused and what input/action is required."
    )

    append_manager_notification_file(manager_notify_file, payload, logger)

    try:
        manager_session = f"{args.manager_session_prefix}:{state.session}"
        manager_reply = call_gateway_api(
            session_id=manager_session,
            prompt=manager_prompt,
            agent_id=args.manager_agent_id,
            timeout=args.agent_timeout,
            logger=logger,
        )
        logger.info(
            "Manager notified for pause | reason=%s | source=%s | manager_agent=%s",
            reason,
            source,
            args.manager_agent_id,
        )
        notifier.notify(
            "PECO manager notified",
            {
                "reason": reason,
                "source": source,
                "session": state.session,
                "iteration": state.iteration,
                "manager_agent": args.manager_agent_id,
                "manager_reply": manager_reply[:500],
            },
        )
    except AgentCallError as exc:
        logger.error(
            "Failed notifying manager agent | reason=%s | error=%s",
            reason,
            exc,
        )
        notifier.notify(
            "PECO manager notify failed",
            {
                "reason": reason,
                "source": source,
                "session": state.session,
                "iteration": state.iteration,
                "error": str(exc)[:500],
                "details": details[:500],
            },
        )


def run_iteration(
    state: LoopState,
    args: argparse.Namespace,
    override_text: str,
    logger: logging.Logger,
) -> ParsedResponse:
    prompt = build_loop_prompt(state, override_text)
    raw_output = call_gateway_api(
        session_id=state.session,
        prompt=prompt,
        agent_id=args.agent_id,
        timeout=args.agent_timeout,
        logger=logger,
    )
    parsed = parse_structured_output(raw_output, expected_phase=state.phase)
    state.last_response_excerpt = raw_output[-3000:]
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PECO infinite loop daemon")
    parser.add_argument(
        "--objective",
        default="Drive an autonomous PECO loop and continuously improve output quality.",
        help="Primary loop objective.",
    )
    parser.add_argument(
        "--agent-id",
        default="main",
        help="OpenClaw agent id for loop execution",
    )
    parser.add_argument(
        "--manager-agent-id",
        default="main",
        help="OpenClaw manager agent id for pause notifications",
    )
    parser.add_argument(
        "--manager-session-prefix",
        default="peco-manager",
        help="Session prefix for manager notifications",
    )
    parser.add_argument(
        "--agent",
        dest="agent_id_legacy",
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--session-prefix", default="peco-zifang", help="Session id prefix"
    )
    parser.add_argument(
        "--state-file",
        default="/root/.openclaw/peco_loop_state.json",
        help="State file path",
    )
    parser.add_argument(
        "--override-file",
        default="/root/.openclaw/peco_override.txt",
        help="Override instruction file path",
    )
    parser.add_argument(
        "--sleep-seconds", type=int, default=15, help="Sleep between iterations"
    )
    parser.add_argument(
        "--agent-timeout", type=int, default=600, help="Gateway API timeout seconds"
    )
    parser.add_argument(
        "--max-failures",
        type=int,
        default=3,
        help="Circuit breaker threshold for consecutive failures",
    )
    parser.add_argument(
        "--max-repeat-signature",
        type=int,
        default=3,
        help="Repeated signature threshold before forced OPTIMIZE",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Stop after N iterations (for controlled runs)",
    )
    parser.add_argument(
        "--stop-on-halt",
        action="store_true",
        help="Exit process when decision=halt or breaker trips",
    )
    parser.add_argument(
        "--feishu-webhook",
        default="",
        help="Feishu bot webhook URL (optional)",
    )
    parser.add_argument(
        "--feishu-timeout",
        type=int,
        default=6,
        help="Feishu webhook timeout seconds",
    )
    parser.add_argument(
        "--human-task-backlog",
        default="/root/.openclaw/human_tasks_backlog.txt",
        help="Backlog file path for HUMAN_TASK items",
    )
    parser.add_argument(
        "--log-file",
        default="/root/.openclaw/peco_loop.log",
        help="Log file path",
    )
    parser.add_argument(
        "--manager-notify-file",
        default="/root/.openclaw/peco_manager_notifications.log",
        help="Local fallback log file for manager notifications",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.agent_id_legacy:
        args.agent_id = args.agent_id_legacy
    logger = setup_logger(Path(args.log_file), args.log_level)

    state_file = Path(args.state_file)
    override_file = Path(args.override_file)
    backlog_file = Path(args.human_task_backlog)
    manager_notify_file = Path(args.manager_notify_file)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    override_file.parent.mkdir(parents=True, exist_ok=True)
    backlog_file.parent.mkdir(parents=True, exist_ok=True)
    manager_notify_file.parent.mkdir(parents=True, exist_ok=True)
    if not override_file.exists():
        override_file.write_text("", encoding="utf-8")

    webhook = args.feishu_webhook or ""
    notifier = FeishuNotifier(
        webhook_url=webhook, timeout=args.feishu_timeout, logger=logger
    )
    feishu_sync = load_feishu_config(logger)

    state = load_state(
        state_file, objective=args.objective, session_prefix=args.session_prefix
    )
    save_state(state_file, state)

    logger.info(
        "PECO loop started | objective=%s | session=%s | phase=%s | agent=%s",
        state.objective,
        state.session,
        state.phase,
        args.agent_id,
    )
    notifier.notify(
        "PECO loop started",
        {
            "objective": state.objective,
            "session": state.session,
            "phase": state.phase,
            "iteration": state.iteration,
            "agent_id": args.agent_id,
        },
    )

    while True:
        if args.max_iterations is not None and state.iteration >= args.max_iterations:
            logger.info("Reached max iterations=%s, exiting", args.max_iterations)
            break

        local_override = read_and_clear_override(override_file, logger)
        feishu_override = ""
        if feishu_sync:
            feishu_override = feishu_sync.fetch_and_consume_resolved_tasks()
            if feishu_override:
                logger.info(
                    "Loaded resolved human tasks from Feishu (%d chars)",
                    len(feishu_override),
                )
        override_text = merge_override_text(local_override, feishu_override)

        if state.halted and not override_text:
            logger.warning("Loop halted. Waiting for override in %s", override_file)
            time.sleep(max(args.sleep_seconds, 3))
            continue
        if state.halted and override_text:
            logger.warning("Override received while halted. Resuming loop.")
            state.halted = False
            state.phase = "PLAN"
            state.last_phase_summary = "Resumed by manual override"

        state.iteration += 1
        current_phase = state.phase
        logger.info(
            "Iteration=%s phase=%s session=%s",
            state.iteration,
            state.phase,
            state.session,
        )

        try:
            parsed = run_iteration(state, args, override_text, logger)
            repeated_human_blocker_count = append_human_task_backlog(
                backlog_file,
                state,
                parsed,
                logger,
                notifier,
                feishu_sync,
            )

            if repeated_human_blocker_count >= 3:
                escalation_summary = "Repeated human blocker detected 3 times; halting loop and requesting manager escalation"
                state.halted = True
                state.phase = "PLAN"
                state.last_phase_summary = escalation_summary
                notify_manager_about_pause(
                    state=state,
                    args=args,
                    logger=logger,
                    notifier=notifier,
                    manager_notify_file=manager_notify_file,
                    reason="repeated_human_blocker",
                    source="model",
                    details=(
                        f"model_summary={parsed.summary}; "
                        f"human_blocker={state.last_human_task}; "
                        f"repeated_count={repeated_human_blocker_count}"
                    ),
                )
                logger.error(
                    "Human blocker escalated (count=%s): %s",
                    repeated_human_blocker_count,
                    state.last_human_task,
                )
                notifier.notify(
                    "PECO manager escalation required",
                    {
                        "iteration": state.iteration,
                        "session": state.session,
                        "blocker": state.last_human_task,
                        "repeated_human_blocker_count": repeated_human_blocker_count,
                        "required_action": "Notify human of blocker and provide missing resource",
                        "status": "Loop paused until override/human support",
                    },
                )
                continue

            if repeated_human_blocker_count >= 2:
                logger.warning(
                    "Repeated human blocker detected (count=%s), forcing PLAN for divergent solutions",
                    repeated_human_blocker_count,
                )

            next_phase = normalize_next_phase(current_phase, parsed.next_phase, logger)
            if repeated_human_blocker_count >= 2:
                next_phase = "PLAN"

            signature = (
                f"{parsed.phase}|{next_phase}|{parsed.decision}|{parsed.summary[:120]}"
            )
            if signature == state.last_signature:
                state.repeated_signature_count += 1
            else:
                state.repeated_signature_count = 0
            state.last_signature = signature

            if state.repeated_signature_count >= args.max_repeat_signature:
                logger.warning(
                    "Detected repeated loop signature (%s times), forcing OPTIMIZE",
                    state.repeated_signature_count,
                )
                next_phase = "OPTIMIZE"
                notifier.notify(
                    "PECO anti-loop trigger",
                    {
                        "iteration": state.iteration,
                        "session": state.session,
                        "forced_next_phase": next_phase,
                    },
                )

            state.last_phase_summary = parsed.summary
            state.phase = next_phase
            state.consecutive_failures = 0

            if feishu_sync:
                phase_status = "HALT" if parsed.decision == "halt" else "OK"
                feishu_sync.append_progress(
                    session=state.session,
                    iteration=state.iteration,
                    phase=parsed.phase,
                    summary=parsed.summary,
                    status=phase_status,
                )

            logger.info(
                "Phase transition %s -> %s | decision=%s | confidence=%.2f",
                current_phase,
                state.phase,
                parsed.decision,
                parsed.confidence,
            )
            notifier.notify(
                "PECO phase transition",
                {
                    "iteration": state.iteration,
                    "session": state.session,
                    "from": current_phase,
                    "to": state.phase,
                    "decision": parsed.decision,
                    "confidence": parsed.confidence,
                    "summary": parsed.summary[:300],
                },
            )

            if parsed.decision == "halt":
                state.halted = True
                notify_manager_about_pause(
                    state=state,
                    args=args,
                    logger=logger,
                    notifier=notifier,
                    manager_notify_file=manager_notify_file,
                    reason="agent_requested_halt",
                    source="model",
                    details=(
                        f"model_summary={parsed.summary}; "
                        f"decision={parsed.decision}; "
                        f"phase={parsed.phase}"
                    ),
                )
                logger.warning("Agent requested halt at iteration=%s", state.iteration)
                notifier.notify(
                    "PECO halt requested",
                    {
                        "iteration": state.iteration,
                        "session": state.session,
                        "summary": parsed.summary[:300],
                    },
                )

        except (AgentCallError, ParseError, LoopError, ValueError) as exc:
            state.consecutive_failures += 1
            state.last_phase_summary = f"Error: {exc}"
            state.phase = "OPTIMIZE"

            if feishu_sync:
                feishu_sync.append_progress(
                    session=state.session,
                    iteration=state.iteration,
                    phase=current_phase,
                    summary=str(exc),
                    status="ERROR",
                )
            logger.exception(
                "Iteration failed (%s/%s): %s",
                state.consecutive_failures,
                args.max_failures,
                exc,
            )
            notifier.notify(
                "PECO iteration error",
                {
                    "iteration": state.iteration,
                    "session": state.session,
                    "phase": current_phase,
                    "consecutive_failures": state.consecutive_failures,
                    "error": str(exc)[:500],
                },
            )

            if state.consecutive_failures >= args.max_failures:
                state.halted = True
                pause_source = "code" if isinstance(exc, AgentCallError) else "model"
                notify_manager_about_pause(
                    state=state,
                    args=args,
                    logger=logger,
                    notifier=notifier,
                    manager_notify_file=manager_notify_file,
                    reason="circuit_breaker_open",
                    source=pause_source,
                    details=(
                        f"error={exc}; "
                        f"consecutive_failures={state.consecutive_failures}; "
                        f"max_failures={args.max_failures}"
                    ),
                )
                logger.error(
                    "Circuit breaker opened after %s failures",
                    state.consecutive_failures,
                )
                notifier.notify(
                    "PECO circuit breaker OPEN",
                    {
                        "iteration": state.iteration,
                        "session": state.session,
                        "failures": state.consecutive_failures,
                    },
                )

        finally:
            save_state(state_file, state)

        if state.halted and args.stop_on_halt:
            logger.warning("Stopping process because --stop-on-halt is enabled")
            break

        time.sleep(max(args.sleep_seconds, 1))

    logger.info("PECO loop exited")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
