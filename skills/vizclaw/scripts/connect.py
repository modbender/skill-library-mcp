# /// script
# requires-python = ">=3.10"
# dependencies = ["websockets"]
# ///
"""
VizClaw Connect - stream OpenClaw-style events to VizClaw.

Quick start:
  uv run https://vizclaw.com/skills/vizclaw/scripts/connect.py
  uv run https://vizclaw.com/skills/vizclaw/scripts/connect.py --mode overview

Native OpenClaw Gateway subscription (replaces vizclaw_bridge.sh):
  uv run connect.py --openclaw-gateway ws://127.0.0.1:18789 --openclaw-token open
  uv run connect.py --openclaw-gateway ws://127.0.0.1:18789 --openclaw-token open --run-id abc123

Tail local OpenClaw JSONL logs:
  uv run connect.py --openclaw-log-tail /var/log/openclaw/events.jsonl

Bridge OpenClaw JSONL events from stdin (legacy):
  openclaw run ... --json | uv run connect.py --openclaw-jsonl

Bridge OpenClaw websocket broadcasts (legacy):
  uv run connect.py --openclaw-ws ws://localhost:9000/events

Interactive commands:
  query <text>
  human <text>
  cron <text>
  heartbeat [message]
  spawn <agent-id> <model> [work-type]
  task <agent-id> <work-type> <description>
  skill <agent-id> <skill name>
  tool <agent-id> <tool name>
  report <agent-id> [message]
  complete <agent-id>
  done [summary]
  mode <detailed|overview|hidden>
  config-skills <skill1,skill2,...>
  config-models <model1,model2,...>
  config-reminders <json array>
  config-heartbeat <interval-seconds | off>
  end
  quit
"""

import argparse
import asyncio
import json
import os
import shlex
import signal
import sys
from datetime import datetime, timezone
from collections import deque
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from uuid import uuid4

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

WARNED_EVENT_TYPES: deque[str] = deque(maxlen=200)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_mode(mode: str) -> str:
    mode = (mode or "detailed").strip().lower()
    if mode == "hidden":
        return "overview"
    if mode in {"detailed", "overview"}:
        return mode
    return "detailed"


def normalize_trigger_source(source: str | None) -> str:
    s = (source or "human").strip().lower()
    if s in {"human", "cron", "heartbeat"}:
        return s
    return "human"


def maybe_text(text: str | None, mode: str) -> str | None:
    if not text:
        return None
    return text if mode == "detailed" else None


def parse_skills(skills_str: str | None) -> list[dict] | None:
    if not skills_str:
        return None
    return [{"name": s.strip()} for s in skills_str.split(",") if s.strip()]


def parse_available_models(models_str: str | None) -> list[dict] | None:
    if not models_str:
        return None
    models = []
    for m in models_str.split(","):
        m = m.strip()
        if not m:
            continue
        models.append({"id": m, "label": m})
    return models


def parse_reminders(reminders_json: str | None) -> list[dict] | None:
    if not reminders_json:
        return None
    try:
        parsed = json.loads(reminders_json)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    return None


def build_config_update(
    session_id: str,
    skills: list[dict] | None = None,
    available_models: list[dict] | None = None,
    reminders: list[dict] | None = None,
    heartbeat_interval: int | None = None,
    room_code: str | None = None,
) -> dict | None:
    payload: dict = {
        "type": "config_update",
        "sessionId": session_id,
        "timestamp": now_iso(),
    }
    has_config = False
    if skills is not None:
        payload["skills"] = skills
        has_config = True
    if available_models is not None:
        payload["availableModels"] = available_models
        has_config = True
    if reminders is not None:
        payload["reminders"] = reminders
        has_config = True
    if heartbeat_interval is not None:
        payload["heartbeatConfig"] = {
            "enabled": heartbeat_interval > 0,
            "intervalSeconds": heartbeat_interval if heartbeat_interval > 0 else None,
        }
        has_config = True
    if room_code:
        payload["roomCode"] = room_code
    return payload if has_config else None


def http_report(api_url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        api_url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "VizClaw-Connect/1.3"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(body)
        except Exception:
            return {"error": f"HTTP {e.code}: {body}"}
    except URLError as e:
        return {"error": str(e.reason)}


def resolve_openclaw_type(evt: dict) -> str:
    for key in ("type", "event", "name", "event_type"):
        val = evt.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip().lower()
    return ""


def first_str(evt: dict, *keys: str) -> str | None:
    for key in keys:
        val = evt.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def coerce_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        for key in ("text", "message", "content", "error"):
            nested = value.get(key)
            if isinstance(nested, str) and nested.strip():
                return nested.strip()
    try:
        rendered = json.dumps(value, ensure_ascii=False)
    except Exception:
        return None
    rendered = rendered.strip()
    if not rendered:
        return None
    return rendered[:500]


def parse_openclaw_input_line(raw: str) -> list[dict]:
    line = raw.strip()
    if not line:
        return []
    if line.startswith("data:"):
        line = line[5:].strip()
    if not line or line == "[DONE]":
        return []
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return []
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def map_openclaw_gateway_agent_event(
    payload: dict, session_id: str, default_model: str, mode: str, quiet_mode: bool = False
) -> list[dict]:
    out: list[dict] = []
    stream = first_str(payload, "stream") or ""
    run_id = first_str(payload, "runId", "run_id", "agentId", "agent_id", "id")
    agent_id = run_id or session_id
    model = first_str(payload, "model", "model_name") or default_model
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    phase = first_str(data, "phase", "state", "status")
    tool_name = first_str(data, "name", "toolName", "tool_name")
    query_text = first_str(data, "query", "prompt", "message")
    message_text = (
        first_str(data, "message", "text", "delta")
        or coerce_text(data.get("partialResult"))
        or coerce_text(data.get("result"))
        or coerce_text(data.get("error"))
    )

    if stream == "lifecycle":
        if phase == "start":
            out.append(
                {
                    "type": "agent_spawn",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "runId": run_id,
                    "model": model,
                    "workType": "coding",
                }
            )
            if query_text:
                out.append(
                    {
                        "type": "query_received",
                        "sessionId": session_id,
                        "runId": run_id,
                        "triggerSource": "human",
                        "query": maybe_text(query_text, mode),
                    }
                )
        elif phase == "error":
            if message_text and not quiet_mode:
                out.append(
                    {
                        "type": "agent_reporting",
                        "sessionId": session_id,
                        "agentId": agent_id,
                        "runId": run_id,
                        "message": maybe_text(message_text, mode),
                    }
                )
            out.append(
                {
                    "type": "agent_complete",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "runId": run_id,
                }
            )
        elif phase == "end":
            out.append(
                {
                    "type": "agent_complete",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "runId": run_id,
                }
            )
        return out

    if stream == "tool":
        if phase == "start":
            task_description = f"Using tool: {tool_name or 'tool'}"
            out.append(
                {
                    "type": "task_assigned",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "runId": run_id,
                    "workType": "coding",
                    "taskDescription": maybe_text(task_description, mode),
                    "tool": tool_name if mode == "detailed" else None,
                }
            )
            out.append(
                {
                    "type": "tool_used",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "runId": run_id,
                    "tool": tool_name,
                    "workType": "coding",
                }
            )
        elif phase == "result":
            out.append(
                {
                    "type": "tool_used",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "runId": run_id,
                    "tool": tool_name,
                    "workType": "coding",
                }
            )
            if message_text and not quiet_mode:
                out.append(
                    {
                        "type": "agent_reporting",
                        "sessionId": session_id,
                        "agentId": agent_id,
                        "runId": run_id,
                        "message": maybe_text(message_text, mode),
                    }
                )
        elif phase == "update" and message_text and not quiet_mode:
            out.append(
                {
                    "type": "agent_reporting",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "runId": run_id,
                    "message": maybe_text(message_text, mode),
                }
            )
        return out

    if stream == "assistant":
        if message_text and not quiet_mode:
            out.append(
                {
                    "type": "agent_reporting",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "runId": run_id,
                    "message": maybe_text(message_text, mode),
                }
            )
        return out

    if stream == "error":
        if message_text and not quiet_mode:
            out.append(
                {
                    "type": "agent_reporting",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "runId": run_id,
                    "message": maybe_text(message_text, mode),
                }
            )
        out.append(
            {
                "type": "agent_complete",
                "sessionId": session_id,
                "agentId": agent_id,
                "runId": run_id,
            }
        )
        return out

    return out


def map_openclaw_gateway_chat_event(
    payload: dict, session_id: str, mode: str, quiet_mode: bool = False
) -> list[dict]:
    out: list[dict] = []
    run_id = first_str(payload, "runId", "run_id", "agentId", "agent_id")
    agent_id = run_id or session_id
    state = first_str(payload, "state", "phase", "status")
    text = (
        first_str(payload, "message", "text", "delta", "content")
        or coerce_text(payload.get("payload"))
    )

    if state in {"start", "started", "running"} and text:
        out.append(
            {
                "type": "query_received",
                "sessionId": session_id,
                "runId": run_id,
                "triggerSource": "human",
                "query": maybe_text(text, mode),
            }
        )
    elif state in {"final", "end", "completed", "done"}:
        out.append(
            {
                "type": "query_completed",
                "sessionId": session_id,
                "runId": run_id,
                "message": maybe_text(text, mode),
            }
        )
    elif state == "error":
        out.append(
            {
                "type": "query_completed",
                "sessionId": session_id,
                "runId": run_id,
                "message": maybe_text(text or "Agent run error", mode),
            }
        )
    elif text and not quiet_mode:
        out.append(
            {
                "type": "agent_reporting",
                "sessionId": session_id,
                "agentId": agent_id,
                "runId": run_id,
                "message": maybe_text(text, mode),
            }
        )

    return out


def map_openclaw_event(
    evt: dict, session_id: str, default_model: str, mode: str, quiet_mode: bool = False
) -> list[dict]:
    event_name = first_str(evt, "event")
    payload = evt.get("payload")
    if event_name == "agent" and isinstance(payload, dict):
        mapped = map_openclaw_gateway_agent_event(payload, session_id, default_model, mode, quiet_mode)
        if mapped:
            return mapped
    if event_name == "chat" and isinstance(payload, dict):
        mapped = map_openclaw_gateway_chat_event(payload, session_id, mode, quiet_mode)
        if mapped:
            return mapped
    if isinstance(evt.get("stream"), str) and (
        first_str(evt, "runId", "run_id", "agentId", "agent_id", "id")
    ):
        mapped = map_openclaw_gateway_agent_event(evt, session_id, default_model, mode, quiet_mode)
        if mapped:
            return mapped

    etype = resolve_openclaw_type(evt)
    out: list[dict] = []

    run_id = first_str(evt, "runId", "run_id", "trace_id")
    agent_id = first_str(evt, "agentId", "agent_id", "worker_id", "id")
    model = first_str(evt, "model", "model_name") or default_model
    work_type = first_str(evt, "workType", "work_type", "task_type")
    text = first_str(evt, "text", "message", "query", "prompt", "content", "description")
    skill = first_str(evt, "skill", "skill_name")
    tool = first_str(evt, "tool", "tool_name")

    if etype in {"heartbeat", "agent_heartbeat", "main_heartbeat"}:
        out.append({"type": "heartbeat", "sessionId": session_id})
        if text:
            out.append({
                "type": "query_received",
                "sessionId": session_id,
                "runId": run_id,
                "triggerSource": "heartbeat",
                "query": maybe_text(text, mode),
            })
        return out

    if etype in {"cron", "cron_tick", "cron_trigger", "scheduled_run", "scheduler_triggered"}:
        out.append({
            "type": "query_received",
            "sessionId": session_id,
            "runId": run_id,
            "triggerSource": "cron",
            "query": maybe_text(text or "Cron-triggered task", mode),
        })
        return out

    if etype in {"query_received", "user_message", "human_request", "request_received", "task_received"}:
        out.append({
            "type": "query_received",
            "sessionId": session_id,
            "runId": run_id,
            "triggerSource": "human",
            "query": maybe_text(text, mode),
        })
        return out

    if etype in {"agent_spawn", "agent_spawned", "agent_started", "subagent_spawned"}:
        out.append({
            "type": "agent_spawn",
            "sessionId": session_id,
            "agentId": agent_id,
            "runId": run_id,
            "model": model,
            "workType": work_type,
            "taskDescription": maybe_text(text, mode),
        })
        return out

    if etype in {"task_assigned", "agent_task", "task_started", "delegated_task"}:
        out.append({
            "type": "task_assigned",
            "sessionId": session_id,
            "agentId": agent_id,
            "runId": run_id,
            "workType": work_type,
            "taskDescription": maybe_text(text, mode),
            "skill": skill if mode == "detailed" else None,
            "tool": tool if mode == "detailed" else None,
        })
        return out

    if etype in {"tool_used", "tool_call", "tool_invoked"}:
        out.append({
            "type": "tool_used",
            "sessionId": session_id,
            "agentId": agent_id,
            "runId": run_id,
            "tool": tool or text,
            "workType": work_type,
        })
        return out

    if etype in {"skill_used", "skill_applied", "skill_selected"}:
        out.append({
            "type": "skill_used",
            "sessionId": session_id,
            "agentId": agent_id,
            "runId": run_id,
            "skill": skill or text,
            "workType": work_type,
        })
        return out

    if etype in {"agent_report", "agent_reporting", "partial_result", "progress"}:
        if not quiet_mode:
            out.append({
                "type": "agent_reporting",
                "sessionId": session_id,
                "agentId": agent_id,
                "runId": run_id,
                "message": maybe_text(text, mode),
            })
        return out

    if etype in {"agent_complete", "agent_completed", "task_complete", "subagent_done"}:
        out.append({
            "type": "agent_complete",
            "sessionId": session_id,
            "agentId": agent_id,
            "runId": run_id,
        })
        return out

    if etype in {"query_completed", "final_result", "run_complete"}:
        out.append({
            "type": "query_completed",
            "sessionId": session_id,
            "runId": run_id,
            "message": maybe_text(text, mode),
        })
        return out

    if etype in {"session_end", "run_end"}:
        out.append({"type": "session_end", "sessionId": session_id})
        return out

    # Config events from OpenClaw
    if etype in {"config_loaded", "skills_loaded", "config_update", "plugin_loaded"}:
        config: dict = {"type": "config_update", "sessionId": session_id}
        skills_raw = evt.get("skills") or evt.get("plugins")
        if isinstance(skills_raw, list):
            config["skills"] = [
                {"name": s.get("name", s) if isinstance(s, dict) else str(s)}
                for s in skills_raw
            ]
        models_raw = evt.get("availableModels") or evt.get("models")
        if isinstance(models_raw, list):
            config["availableModels"] = [
                {"id": m.get("id", m) if isinstance(m, dict) else str(m),
                 "label": m.get("label", m.get("id", m)) if isinstance(m, dict) else str(m)}
                for m in models_raw
            ]
        reminders_raw = evt.get("reminders") or evt.get("scheduled_tasks")
        if isinstance(reminders_raw, list):
            config["reminders"] = reminders_raw
        hb = evt.get("heartbeatConfig") or evt.get("heartbeat_config")
        if isinstance(hb, dict):
            config["heartbeatConfig"] = hb
        out.append(config)
        return out

    if etype in {"reminder_triggered", "scheduled_task_fired"}:
        title = first_str(evt, "title", "reminder", "task_name") or "Scheduled task"
        out.append({
            "type": "query_received",
            "sessionId": session_id,
            "runId": run_id,
            "triggerSource": "cron",
            "query": maybe_text(text or title, mode),
        })
        return out

    # Fallback: if there's free text, treat it as human trigger query.
    if text:
        out.append({
            "type": "query_received",
            "sessionId": session_id,
            "runId": run_id,
            "triggerSource": "human",
            "query": maybe_text(text, mode),
        })

    if not out:
        unknown_key = event_name or etype or "unknown"
        if unknown_key not in WARNED_EVENT_TYPES:
            WARNED_EVENT_TYPES.append(unknown_key)
            print(
                f"[vizclaw] unmapped OpenClaw event shape: {unknown_key}",
                file=sys.stderr,
            )

    return out


async def read_stdin_lines():
    loop = asyncio.get_event_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        yield line.strip()


async def read_openclaw_ws_events(openclaw_ws: str):
    async with websockets.connect(openclaw_ws) as source_ws:
        async for raw in source_ws:
            if not isinstance(raw, str):
                continue
            for parsed in parse_openclaw_input_line(raw):
                yield parsed


async def read_openclaw_gateway_events(
    gateway_url: str,
    token: str | None = None,
):
    """Connect to OpenClaw Gateway WebSocket with auth and auto-reconnect.

    Yields parsed event dicts. Reconnects automatically on connection loss
    with exponential backoff (1s -> 30s cap).
    """
    parts = urlsplit(gateway_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    if token:
        query["token"] = token
    target = urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
    )

    extra_headers = {}
    if token:
        extra_headers["Authorization"] = f"Bearer {token}"

    delay = 1.0
    while True:
        try:
            async with websockets.connect(
                target,
                additional_headers=extra_headers,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=5,
            ) as source_ws:
                delay = 1.0  # reset backoff on successful connect
                print(
                    f"[vizclaw] connected to OpenClaw Gateway: {gateway_url}",
                    file=sys.stderr,
                )
                async for raw in source_ws:
                    if not isinstance(raw, str):
                        continue
                    for parsed in parse_openclaw_input_line(raw):
                        yield parsed
        except asyncio.CancelledError:
            raise
        except Exception as err:
            print(
                f"[vizclaw] gateway connection lost ({err}), "
                f"reconnecting in {delay:.0f}s...",
                file=sys.stderr,
            )
            await asyncio.sleep(delay)
            delay = min(delay * 2, 30.0)


async def tail_jsonl_file(path: str):
    """Tail a JSONL log file (like ``tail -f``), yielding parsed event dicts.

    Waits for the file to appear, seeks to the end, then polls for new lines.
    Handles log rotation (file truncation) automatically.
    """
    while not os.path.exists(path):
        print(f"[vizclaw] waiting for log file: {path}", file=sys.stderr)
        await asyncio.sleep(2.0)

    with open(path, "r") as f:
        f.seek(0, 2)  # seek to end - only process new events
        print(f"[vizclaw] tailing log file: {path}", file=sys.stderr)

        while True:
            line = f.readline()
            if not line:
                # Check for file truncation / rotation
                try:
                    if os.path.getsize(path) < f.tell():
                        print(
                            "[vizclaw] log file rotated, re-reading",
                            file=sys.stderr,
                        )
                        f.seek(0)
                        continue
                except OSError:
                    pass
                await asyncio.sleep(0.2)
                continue

            line = line.strip()
            if not line:
                continue

            for parsed in parse_openclaw_input_line(line):
                yield parsed


def add_room_to_hub_url(hub: str, room_code: str | None) -> str:
    if not room_code:
        return hub
    parts = urlsplit(hub)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["room"] = room_code
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


class HubReporterClient:
    def __init__(
        self,
        hub: str,
        session_id: str,
        model: str,
        mode: str,
        skills: list[dict] | None,
        available_models: list[dict] | None,
        reminders: list[dict] | None,
        heartbeat_interval: int | None,
    ):
        self.hub = hub
        self.session_id = session_id
        self.model = model
        self.mode = mode
        self.skills = skills
        self.available_models = available_models
        self.reminders = reminders
        self.heartbeat_interval = heartbeat_interval
        self.ws = None
        self.room_code: str | None = None
        self.viewer_url: str | None = None
        self.client_event_seq = 0
        self.replay_buffer: deque[dict] = deque(maxlen=400)

    def next_client_event_id(self) -> str:
        self.client_event_seq += 1
        return f"{self.session_id}:{self.client_event_seq}"

    async def ensure_connected(self):
        if self.ws is not None:
            return
        await self.connect(resume=bool(self.room_code))

    async def connect(self, resume: bool):
        target_hub = add_room_to_hub_url(self.hub, self.room_code if resume else None)
        self.ws = await websockets.connect(target_hub)

        if not resume:
            start_msg = {
                "type": "session_start",
                "sessionId": self.session_id,
                "model": self.model,
                "mode": self.mode,
                "timestamp": now_iso(),
                "clientEventId": self.next_client_event_id(),
            }
            await self._send_and_wait_ack(start_msg, timeout_seconds=10)
            if not self.room_code:
                raise RuntimeError("Connected but room was not created")
            print("Connected")
            print(f"room_code={self.room_code}")
            print(f"session_id={self.session_id}")
            print(f"viewer_url={self.viewer_url}")

            config_msg = build_config_update(
                self.session_id,
                self.skills,
                self.available_models,
                self.reminders,
                self.heartbeat_interval,
            )
            if config_msg:
                await self.send(config_msg, reliable=True, remember=True)
                print("config_update sent")
        else:
            # Re-send session_start to re-register with the Durable Object
            # in case it was evicted, preventing "Session not found" errors.
            start_msg = {
                "type": "session_start",
                "sessionId": self.session_id,
                "model": self.model,
                "mode": self.mode,
                "timestamp": now_iso(),
                "clientEventId": self.next_client_event_id(),
            }
            try:
                await self._send_and_wait_ack(start_msg, timeout_seconds=10)
            except Exception:
                pass  # best-effort session re-registration
            print(f"Reconnected room_code={self.room_code}")
            await self.replay_recent()

    async def close(self):
        if self.ws is not None:
            try:
                await self.ws.close()
            except Exception:
                pass
            self.ws = None

    async def reconnect(self):
        await self.close()
        delay = 1.0
        last_err: Exception | None = None
        for _ in range(6):
            try:
                await self.connect(resume=True)
                return
            except Exception as err:  # pragma: no cover - defensive retry loop
                last_err = err
                await asyncio.sleep(delay)
                delay = min(delay * 2, 8.0)
        if last_err:
            raise last_err
        raise RuntimeError("Unable to reconnect to hub")

    async def _consume_non_ack_message(self, msg: dict):
        mtype = msg.get("type")
        if mtype == "room_created":
            self.room_code = msg.get("roomCode") or self.room_code
            viewer = msg.get("viewerUrl")
            if isinstance(viewer, str) and viewer.strip():
                self.viewer_url = viewer
            elif self.room_code:
                self.viewer_url = f"https://vizclaw.com/room/{self.room_code}"
        elif mtype == "error":
            error_msg = msg.get("message", "unknown")
            print(f"[vizclaw] hub error: {error_msg}", file=sys.stderr)
            if "session not found" in error_msg.lower():
                # Trigger immediate reconnect instead of waiting for ack timeout
                raise ConnectionError(f"Hub session lost: {error_msg}")

    async def _wait_for_ack(self, client_event_id: str, timeout_seconds: float):
        if self.ws is None:
            raise RuntimeError("WebSocket is not connected")
        while True:
            raw = await asyncio.wait_for(self.ws.recv(), timeout=timeout_seconds)
            msg = json.loads(raw)
            if (
                isinstance(msg, dict)
                and msg.get("type") == "ack"
                and msg.get("clientEventId") == client_event_id
            ):
                return
            if isinstance(msg, dict):
                await self._consume_non_ack_message(msg)

    async def _send_and_wait_ack(self, payload: dict, timeout_seconds: float):
        if self.ws is None:
            raise RuntimeError("WebSocket is not connected")
        await self.ws.send(json.dumps(payload))
        client_event_id = payload.get("clientEventId")
        if isinstance(client_event_id, str) and client_event_id:
            await self._wait_for_ack(client_event_id, timeout_seconds)

    async def replay_recent(self):
        if not self.replay_buffer:
            return
        cached = list(self.replay_buffer)
        print(f"[vizclaw] replaying {len(cached)} buffered events...")
        for payload in cached:
            await self._send_and_wait_ack(payload, timeout_seconds=6)

    async def send(self, payload: dict, reliable: bool = True, remember: bool = True):
        data = dict(payload)
        if reliable and not data.get("clientEventId"):
            data["clientEventId"] = self.next_client_event_id()
        if remember and reliable and data.get("type") != "heartbeat":
            self.replay_buffer.append(data)

        attempts = 0
        while True:
            attempts += 1
            try:
                await self.ensure_connected()
                await self._send_and_wait_ack(data, timeout_seconds=6 if reliable else 3)
                return
            except Exception as err:
                if attempts >= 5:
                    raise err
                print(f"[vizclaw] send failed (attempt {attempts}), reconnecting...", file=sys.stderr)
                await self.reconnect()


async def connect_interactive(
    hub: str,
    model: str,
    mode: str,
    session_id: str,
    openclaw_jsonl: bool,
    openclaw_ws: str | None,
    skills: list[dict] | None = None,
    available_models: list[dict] | None = None,
    reminders: list[dict] | None = None,
    heartbeat_interval: int | None = None,
    quiet_mode: bool = False,
    openclaw_gateway: str | None = None,
    openclaw_token: str | None = None,
    openclaw_log_tail: str | None = None,
    run_id: str | None = None,
):
    if not HAS_WEBSOCKETS:
        print("Error: websockets package not found. Install with: pip install websockets", file=sys.stderr)
        sys.exit(1)

    mode = normalize_mode(mode)
    print(f"VizClaw Connect: connecting to {hub}")

    client = HubReporterClient(
        hub=hub,
        session_id=session_id,
        model=model,
        mode=mode,
        skills=skills,
        available_models=available_models,
        reminders=reminders,
        heartbeat_interval=heartbeat_interval,
    )
    await client.connect(resume=False)

    is_streaming = openclaw_gateway or openclaw_log_tail or openclaw_jsonl or openclaw_ws
    if openclaw_gateway:
        print(f"Subscribing to OpenClaw Gateway: {openclaw_gateway}")
    elif openclaw_log_tail:
        print(f"Tailing OpenClaw log file: {openclaw_log_tail}")
    elif openclaw_jsonl:
        print("Reading OpenClaw JSON events from stdin...")
    elif openclaw_ws:
        print(f"Subscribing to OpenClaw event websocket: {openclaw_ws}")
    else:
        print("Type 'help' for commands.")

    async def send_heartbeats():
        while True:
            await asyncio.sleep(30)
            await client.send(
                {
                    "type": "heartbeat",
                    "sessionId": session_id,
                    "timestamp": now_iso(),
                },
                reliable=False,
                remember=False,
            )

    def print_help():
        print("Commands:")
        print("  query <text>")
        print("  human <text>")
        print("  cron <text>")
        print("  heartbeat [message]")
        print("  spawn <agent-id> <model> [work-type]")
        print("  task <agent-id> <work-type> <description>")
        print("  skill <agent-id> <skill>")
        print("  tool <agent-id> <tool>")
        print("  report <agent-id> [message]")
        print("  complete <agent-id>")
        print("  done [summary]")
        print("  mode <detailed|overview|hidden>")
        print("  config-skills <skill1,skill2,...>")
        print("  config-models <model1,model2,...>")
        print("  config-reminders <json array>")
        print("  config-heartbeat <seconds | off>")
        print("  end")
        print("  quit")

    heartbeat_task = asyncio.create_task(send_heartbeats())

    try:
        if is_streaming:
            if openclaw_gateway:
                event_iter = read_openclaw_gateway_events(
                    openclaw_gateway, token=openclaw_token,
                )
            elif openclaw_log_tail:
                event_iter = tail_jsonl_file(openclaw_log_tail)
            elif openclaw_ws:
                event_iter = read_openclaw_ws_events(openclaw_ws)
            else:
                async def _stdin_events():
                    async for line in read_stdin_lines():
                        for evt in parse_openclaw_input_line(line):
                            yield evt
                event_iter = _stdin_events()

            async for evt in event_iter:
                # Filter by run_id if specified
                if run_id:
                    evt_run = first_str(
                        evt, "runId", "run_id", "agentId", "agent_id", "id",
                    )
                    inner = evt.get("payload")
                    if isinstance(inner, dict):
                        evt_run = evt_run or first_str(
                            inner, "runId", "run_id", "agentId", "agent_id",
                        )
                    if evt_run and evt_run != run_id:
                        continue

                mapped = map_openclaw_event(
                    evt, session_id, model, mode, quiet_mode=quiet_mode
                )
                for payload in mapped:
                    payload["timestamp"] = now_iso()
                    await client.send(payload, reliable=True, remember=True)

            await client.send(
                {
                    "type": "session_end",
                    "sessionId": session_id,
                    "timestamp": now_iso(),
                },
                reliable=True,
                remember=True,
            )
            return

        async for cmd in read_stdin_lines():
            if not cmd:
                continue

            try:
                parts = shlex.split(cmd)
            except ValueError as err:
                print(f"Invalid command: {err}")
                continue

            action = parts[0].lower()

            if action in {"quit", "exit", "q"}:
                break
            if action == "help":
                print_help()
                continue
            if action in {"query", "human", "cron"} and len(parts) >= 2:
                source = "human" if action == "query" else action
                query = " ".join(parts[1:])
                await client.send(
                    {
                        "type": "query_received",
                        "sessionId": session_id,
                        "triggerSource": source,
                        "query": maybe_text(query, mode),
                        "timestamp": now_iso(),
                    },
                    reliable=True,
                    remember=True,
                )
                print(f"query[{source}]={query}")
                continue
            if action == "heartbeat":
                note = " ".join(parts[1:]) if len(parts) >= 2 else None
                await client.send(
                    {
                        "type": "heartbeat",
                        "sessionId": session_id,
                        "timestamp": now_iso(),
                    },
                    reliable=False,
                    remember=False,
                )
                if note:
                    await client.send(
                        {
                            "type": "query_received",
                            "sessionId": session_id,
                            "triggerSource": "heartbeat",
                            "query": maybe_text(note, mode),
                            "timestamp": now_iso(),
                        },
                        reliable=True,
                        remember=True,
                    )
                print("heartbeat")
                continue
            if action == "spawn" and len(parts) >= 3:
                payload = {
                    "type": "agent_spawn",
                    "sessionId": session_id,
                    "agentId": parts[1],
                    "model": parts[2],
                    "timestamp": now_iso(),
                }
                if len(parts) >= 4:
                    payload["workType"] = parts[3]
                await client.send(payload, reliable=True, remember=True)
                print(f"spawned={parts[1]}")
                continue
            if action == "task" and len(parts) >= 4:
                agent_id = parts[1]
                work_type = parts[2]
                description = " ".join(parts[3:])
                await client.send(
                    {
                        "type": "task_assigned",
                        "sessionId": session_id,
                        "agentId": agent_id,
                        "workType": work_type,
                        "taskDescription": maybe_text(description, mode),
                        "timestamp": now_iso(),
                    },
                    reliable=True,
                    remember=True,
                )
                print(f"task={agent_id}:{work_type}")
                continue
            if action == "skill" and len(parts) >= 3:
                await client.send(
                    {
                        "type": "skill_used",
                        "sessionId": session_id,
                        "agentId": parts[1],
                        "skill": " ".join(parts[2:]) if mode == "detailed" else None,
                        "timestamp": now_iso(),
                    },
                    reliable=True,
                    remember=True,
                )
                print(f"skill={parts[1]}")
                continue
            if action == "tool" and len(parts) >= 3:
                await client.send(
                    {
                        "type": "tool_used",
                        "sessionId": session_id,
                        "agentId": parts[1],
                        "tool": " ".join(parts[2:]) if mode == "detailed" else None,
                        "timestamp": now_iso(),
                    },
                    reliable=True,
                    remember=True,
                )
                print(f"tool={parts[1]}")
                continue
            if action == "report" and len(parts) >= 2:
                await client.send(
                    {
                        "type": "agent_reporting",
                        "sessionId": session_id,
                        "agentId": parts[1],
                        "message": maybe_text(" ".join(parts[2:]) if len(parts) >= 3 else None, mode),
                        "timestamp": now_iso(),
                    },
                    reliable=True,
                    remember=True,
                )
                print(f"report={parts[1]}")
                continue
            if action == "complete" and len(parts) >= 2:
                await client.send(
                    {
                        "type": "agent_complete",
                        "sessionId": session_id,
                        "agentId": parts[1],
                        "timestamp": now_iso(),
                    },
                    reliable=True,
                    remember=True,
                )
                print(f"complete={parts[1]}")
                continue
            if action == "done":
                await client.send(
                    {
                        "type": "query_completed",
                        "sessionId": session_id,
                        "message": maybe_text(" ".join(parts[1:]) if len(parts) >= 2 else None, mode),
                        "timestamp": now_iso(),
                    },
                    reliable=True,
                    remember=True,
                )
                print("query_completed")
                continue
            if action == "mode" and len(parts) >= 2:
                next_mode = normalize_mode(parts[1])
                mode = next_mode
                await client.send(
                    {
                        "type": "set_mode",
                        "sessionId": session_id,
                        "mode": next_mode,
                        "timestamp": now_iso(),
                    },
                    reliable=True,
                    remember=True,
                )
                print(f"mode={next_mode}")
                continue
            if action == "config-skills" and len(parts) >= 2:
                skills_list = parse_skills(" ".join(parts[1:]))
                msg = build_config_update(session_id, skills=skills_list)
                if msg:
                    await client.send(msg, reliable=True, remember=True)
                    print(f"config-skills={','.join(s['name'] for s in (skills_list or []))}")
                continue
            if action == "config-models" and len(parts) >= 2:
                models_list = parse_available_models(" ".join(parts[1:]))
                msg = build_config_update(session_id, available_models=models_list)
                if msg:
                    await client.send(msg, reliable=True, remember=True)
                    print(f"config-models={','.join(m['id'] for m in (models_list or []))}")
                continue
            if action == "config-reminders" and len(parts) >= 2:
                reminders_list = parse_reminders(" ".join(parts[1:]))
                msg = build_config_update(session_id, reminders=reminders_list)
                if msg:
                    await client.send(msg, reliable=True, remember=True)
                    print(f"config-reminders={len(reminders_list or [])} items")
                else:
                    print("Invalid JSON for reminders")
                continue
            if action == "config-heartbeat" and len(parts) >= 2:
                val = parts[1].strip().lower()
                interval = 0 if val == "off" else int(val)
                msg = build_config_update(session_id, heartbeat_interval=interval)
                if msg:
                    await client.send(msg, reliable=True, remember=True)
                    print(f"config-heartbeat={'off' if interval == 0 else f'{interval}s'}")
                continue
            if action == "end":
                await client.send(
                    {
                        "type": "session_end",
                        "sessionId": session_id,
                        "timestamp": now_iso(),
                    },
                    reliable=True,
                    remember=True,
                )
                print("session_end")
                break

            print(f"Unknown command: {cmd}")
            print("Type 'help' for supported commands.")
    finally:
        heartbeat_task.cancel()
        await client.close()


def run_oneshot(args, session_id: str):
    action = args.action
    mode = normalize_mode(args.mode)
    payload = {
        "sessionId": session_id,
        "timestamp": now_iso(),
    }

    if action == "start":
        payload.update({
            "type": "session_start",
            "model": args.model,
            "mode": mode,
            "triggerSource": normalize_trigger_source(args.trigger_source),
            "query": maybe_text(args.text or None, mode),
        })

    elif action == "query":
        payload.update({
            "type": "query_received",
            "roomCode": args.room_code,
            "triggerSource": normalize_trigger_source(args.trigger_source),
            "query": maybe_text(args.text or "", mode),
        })

    elif action == "spawn":
        payload.update({
            "type": "agent_spawn",
            "roomCode": args.room_code,
            "agentId": args.agent_id,
            "model": args.model,
            "workType": args.work_type,
            "taskDescription": maybe_text(args.text, mode),
        })

    elif action == "task":
        payload.update({
            "type": "task_assigned",
            "roomCode": args.room_code,
            "agentId": args.agent_id,
            "workType": args.work_type,
            "taskDescription": maybe_text(args.text, mode),
        })

    elif action == "skill":
        payload.update({
            "type": "skill_used",
            "roomCode": args.room_code,
            "agentId": args.agent_id,
            "skill": args.text if mode == "detailed" else None,
            "workType": args.work_type,
        })

    elif action == "tool":
        payload.update({
            "type": "tool_used",
            "roomCode": args.room_code,
            "agentId": args.agent_id,
            "tool": args.text if mode == "detailed" else None,
            "workType": args.work_type,
        })

    elif action == "report":
        payload.update({
            "type": "agent_reporting",
            "roomCode": args.room_code,
            "agentId": args.agent_id,
            "message": maybe_text(args.text, mode),
        })

    elif action == "complete":
        payload.update({"type": "agent_complete", "roomCode": args.room_code, "agentId": args.agent_id})

    elif action == "done":
        payload.update({"type": "query_completed", "roomCode": args.room_code, "message": maybe_text(args.text, mode)})

    elif action == "mode":
        payload.update({"type": "set_mode", "roomCode": args.room_code, "mode": mode})

    elif action == "end":
        payload.update({"type": "session_end", "roomCode": args.room_code})

    elif action == "heartbeat":
        payload.update({"type": "heartbeat", "roomCode": args.room_code})

    elif action == "config":
        config = build_config_update(
            session_id,
            skills=parse_skills(getattr(args, "skills", None)),
            available_models=parse_available_models(getattr(args, "available_models", None)),
            reminders=parse_reminders(getattr(args, "reminders_json", None)),
            heartbeat_interval=getattr(args, "heartbeat_interval", None),
            room_code=args.room_code,
        )
        if not config:
            print("Error: at least one config flag is required (--skills, --available-models, --reminders-json, --heartbeat-interval)", file=sys.stderr)
            sys.exit(1)
        payload = config

    else:
        print(f"Unsupported action: {action}", file=sys.stderr)
        sys.exit(2)

    if action != "start" and not args.room_code:
        print("Error: --room-code is required for this action", file=sys.stderr)
        sys.exit(1)

    result = http_report(args.api, payload)
    if not result.get("ok"):
        print(f"Error: {result.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    if action == "start":
        room_code = result.get("roomCode", "")
        viewer_url = result.get("viewerUrl", f"https://vizclaw.com/room/{room_code}")
        print(room_code)
        print(f"session_id={session_id}", file=sys.stderr)
        print(f"viewer_url={viewer_url}", file=sys.stderr)
    else:
        print("ok")


def main():
    # Handle SIGPIPE gracefully (e.g. stdout piped to head)
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    parser = argparse.ArgumentParser(description="VizClaw Connect")
    parser.add_argument("--hub", default="wss://api.vizclaw.com/ws/report", help="WebSocket hub URL")
    parser.add_argument("--api", default="https://api.vizclaw.com/api/report", help="HTTP API URL")
    parser.add_argument("--model", default="opus", help="Model name")
    parser.add_argument("--mode", default="detailed", help="detailed | overview | hidden")
    parser.add_argument("--trigger-source", default="human", help="human | cron | heartbeat")
    parser.add_argument("--openclaw-jsonl", action="store_true", help="Read OpenClaw-style JSON events from stdin")
    parser.add_argument("--openclaw-ws", default=None, help="Subscribe to OpenClaw websocket event stream")
    parser.add_argument("--session-id", default=None, help="Session ID (auto-generated if omitted)")
    parser.add_argument(
        "--action",
        choices=["start", "query", "spawn", "task", "skill", "tool", "report", "complete", "done", "mode", "end", "heartbeat", "config"],
        help="One-shot action via HTTP API",
    )
    parser.add_argument("--agent-id", default=None, help="Agent ID")
    parser.add_argument("--room-code", default=None, help="Room code")
    parser.add_argument("--work-type", default=None, help="Work type (coding, research, testing, etc.)")
    parser.add_argument("--text", default=None, help="Free text payload (query, description, summary, skill or tool)")
    parser.add_argument("--skills", default=None, help="Comma-separated skill names (e.g. ez-google,ez-unifi,claude-code)")
    parser.add_argument("--available-models", default=None, help="Comma-separated model names (e.g. sonnet,haiku,gpt-4o)")
    parser.add_argument("--heartbeat-interval", type=int, default=None, help="Heartbeat interval in seconds (0 to disable)")
    parser.add_argument("--reminders-json", default=None, help='JSON array of reminders, e.g. \'[{"title":"Check email","schedule":"every 30min"}]\'')
    parser.add_argument("--quiet-mode", action="store_true", help="Suppress verbose agent report events; keep structural lifecycle/task/tool events")
    parser.add_argument("--openclaw-gateway", default=None, help="OpenClaw Gateway WebSocket URL (e.g. ws://127.0.0.1:18789)")
    parser.add_argument("--openclaw-token", default=None, help="Auth token for OpenClaw Gateway")
    parser.add_argument("--openclaw-log-tail", default=None, help="Path to OpenClaw JSONL log file to tail")
    parser.add_argument("--run-id", default=None, help="Only forward events matching this run ID")

    args = parser.parse_args()
    session_id = args.session_id or str(uuid4())

    if args.action:
        run_oneshot(args, session_id)
        return

    try:
        asyncio.run(
            connect_interactive(
                args.hub,
                args.model,
                args.mode,
                session_id,
                args.openclaw_jsonl,
                args.openclaw_ws,
                skills=parse_skills(args.skills),
                available_models=parse_available_models(args.available_models),
                reminders=parse_reminders(args.reminders_json),
                heartbeat_interval=args.heartbeat_interval,
                quiet_mode=args.quiet_mode,
                openclaw_gateway=args.openclaw_gateway,
                openclaw_token=args.openclaw_token,
                openclaw_log_tail=args.openclaw_log_tail,
                run_id=args.run_id,
            )
        )
    except BrokenPipeError:
        pass  # stdout closed, exit cleanly


if __name__ == "__main__":
    main()
