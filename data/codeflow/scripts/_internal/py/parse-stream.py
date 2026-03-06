#!/usr/bin/env python3
"""Parse coding agent stream output and post to a chat platform.

Reads JSON lines from stdin — supports Claude Code's --output-format stream-json
and Codex CLI's --json (JSONL events) — formats them into human-readable messages,
and posts via a platform adapter.

Features:
  - Multi-agent parsing (Claude Code stream-json, Codex --json)
  - Platform abstraction (discord by default, extensible)
  - File content previews (suppressed in safe mode)
  - Bash command stdout capture
  - Adapter-managed splitting (no silent truncation)
  - Discord Markdown safety: split long code-fenced messages into self-contained fences
  - Cumulative cost tracking
  - Noise filtering (--skip-reads via SKIP_READS env)
  - End-of-session summary
  - Raw stream logging for session resume
"""

import json
import io
import os
import re
import shlex
import sys
import time
from dataclasses import dataclass
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Platform setup — load the appropriate adapter (discord, slack, etc.)
# ---------------------------------------------------------------------------
# Add scripts/ dir to path so platforms package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from py_compat import require_python310

require_python310(prog="codeflow")

# Prevent UnicodeEncodeError on surrogate characters in agent output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, errors="replace")

from platforms import get_platform
from delivery_governor import DeliveryGovernor
from message_split import split_markdown_code_fence_safe
from redaction import redact_text

platform = get_platform()  # reads PLATFORM env var, defaults to "discord"

# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------
skip_reads = os.environ.get("SKIP_READS", "false").lower() == "true"
relay_dir = os.environ.get("RELAY_DIR", "")

def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


# Safety mode: suppress high-risk content (file previews, command output bodies).
# Default is OFF to preserve existing behavior.
safe_mode = _env_flag("CODEFLOW_SAFE_MODE", False)

# Output mode: controls how chatty relay output is.
#
# - minimal: warning/error/final only
# - balanced: key progress + warning/error/final (default)
# - verbose: near-full (debug)
output_mode = (os.environ.get("CODEFLOW_OUTPUT_MODE") or "balanced").strip().lower()
if output_mode not in {"minimal", "balanced", "verbose"}:
    output_mode = "balanced"


# Compact mode for Codex sessions on platforms that support edit (Telegram).
# Behavior: per turn, keep exactly two rolling messages (thinking + cmd/result),
# then send one turn-complete message. Next turn creates a new pair.
compact_codex_updates = os.environ.get("CODEFLOW_COMPACT", "auto").lower()
platform_name = os.environ.get("PLATFORM", "discord").lower()
if compact_codex_updates == "auto":
    compact_codex_updates = "true" if platform_name == "telegram" else "false"
compact_codex_updates = compact_codex_updates == "true"
platform_supports_edit = bool(getattr(platform, "SUPPORTS_EDIT", False) and hasattr(platform, "edit"))

def post(msg, name=None):
    """Enqueue a non-final message (event channel)."""
    return _emit(msg, name=name, level="progress", channel="event")


def post_warning(msg, name=None):
    return _emit(msg, name=name, level="warning", channel="event")


def post_debug(msg, name=None):
    return _emit(msg, name=name, level="debug", channel="event")


def post_error(msg, name=None):
    return _emit(msg, name=name, level="error", channel="event")


def post_final(msg, name=None):
    """Enqueue a final/high-priority message (final channel)."""
    return _emit(msg, name=name, level="final", channel="final")


def _should_emit(level: str) -> bool:
    lvl = (level or "").strip().lower()
    if output_mode == "minimal":
        return lvl in {"warning", "error", "final"}
    if output_mode == "balanced":
        return lvl in {"progress", "milestone", "warning", "error", "final", "state"}
    return True  # verbose


def _emit(msg, *, name=None, level: str, channel: str):
    if not _should_emit(level):
        return
    msg = redact_text(msg or "", strict=safe_mode)
    if name:
        name = redact_text(name, strict=safe_mode)

    # Discord-specific: keep code-fenced content self-contained when splitting.
    chunks = [msg]
    if platform_name == "discord":
        limit = _platform_max_text()
        if limit and len(msg) > limit and "```" in msg:
            try:
                chunks = split_markdown_code_fence_safe(msg, limit)
            except Exception:
                chunks = [msg]

    for chunk in chunks:
        if not chunk:
            continue
        if channel == "final":
            governor.submit_final(chunk, name=name)
        else:
            governor.submit_event(chunk, name=name)

    governor.tick(max_ops=8)


_SHELL_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

@dataclass(frozen=True)
class _ExpectedNonZeroExitRule:
    exit_codes: set[int]
    require_empty_output: bool = True
    argv_predicate: Optional[Callable[[list[str], str], bool]] = None


def _argv_is_git_diff_quiet(argv: list[str], _segment: str) -> bool:
    idx = _argv_program_index(argv)
    if idx is None:
        return False
    if os.path.basename(argv[idx]).lower() != "git":
        return False
    return len(argv) >= idx + 2 and argv[idx + 1] == "diff" and "--quiet" in argv[idx + 1 :]


def _argv_is_sed_exit_1_probe(argv: list[str], segment: str) -> bool:
    # sed itself does not use exit=1 for "no match", but scripts sometimes do:
    #   sed -n '...; $q1' file
    hay = " ".join(argv) + " " + (segment or "")
    return bool(re.search(r"\bq\s*1\b", hay))


_FIND_PROBE_FLAGS = {"-name", "-iname", "-path", "-ipath", "-regex", "-iregex"}
_FIND_STDERR_SILENCED_RE = re.compile(r"(^|\\s)2>\\s*/dev/null(\\s|$)")


def _argv_is_find_silenced_probe(argv: list[str], segment: str) -> bool:
    idx = _argv_program_index(argv)
    if idx is None:
        return False
    if os.path.basename(argv[idx]).lower() != "find":
        return False
    if not any(flag in argv[idx + 1 :] for flag in _FIND_PROBE_FLAGS):
        return False
    # Only treat exit=1 as "expected" when stderr is explicitly silenced.
    return bool(_FIND_STDERR_SILENCED_RE.search(segment or ""))


# Commands that commonly use exit status as a probe/comparison result, not an execution failure.
# Keep this small and semantic: "exit 1 means 'no result / false / different'".
_EXPECTED_NONZERO_EXIT_RULES: dict[str, _ExpectedNonZeroExitRule] = {
    # search/no-match
    "rg": _ExpectedNonZeroExitRule({1}, require_empty_output=True),
    "grep": _ExpectedNonZeroExitRule({1}, require_empty_output=True),
    "egrep": _ExpectedNonZeroExitRule({1}, require_empty_output=True),
    "fgrep": _ExpectedNonZeroExitRule({1}, require_empty_output=True),
    # boolean predicates
    "test": _ExpectedNonZeroExitRule({1}, require_empty_output=True),
    "[": _ExpectedNonZeroExitRule({1}, require_empty_output=True),
    "[[": _ExpectedNonZeroExitRule({1}, require_empty_output=True),
    # comparisons/diffs
    "diff": _ExpectedNonZeroExitRule({1}, require_empty_output=False),
    "cmp": _ExpectedNonZeroExitRule({1}, require_empty_output=False),
    # structured tools
    "git": _ExpectedNonZeroExitRule({1}, require_empty_output=False, argv_predicate=_argv_is_git_diff_quiet),
    "sed": _ExpectedNonZeroExitRule({1}, require_empty_output=True, argv_predicate=_argv_is_sed_exit_1_probe),
    "find": _ExpectedNonZeroExitRule({1}, require_empty_output=True, argv_predicate=_argv_is_find_silenced_probe),
}


def _shell_tail_command(cmd: str) -> str:
    """Return the last top-level command segment (after &&, ||, ;, |)."""
    s = cmd or ""
    last = 0
    in_single = False
    in_double = False
    esc = False
    i = 0
    while i < len(s):
        ch = s[i]
        if esc:
            esc = False
            i += 1
            continue
        if ch == "\\" and not in_single:
            esc = True
            i += 1
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            i += 1
            continue
        if not in_single and not in_double:
            if s.startswith("&&", i) or s.startswith("||", i):
                last = i + 2
                i += 2
                continue
            if ch in {";", "|", "\n"}:
                last = i + 1
                i += 1
                continue
        i += 1
    return s[last:].strip()


def _argv_program_index(argv: list[str]) -> Optional[int]:
    """Best-effort program index extraction for simple shell-ish argv."""
    if not argv:
        return None
    i = 0
    while i < len(argv) and _SHELL_ASSIGNMENT_RE.match(argv[i]):
        i += 1
    if i < len(argv) and argv[i] == "env":
        i += 1
        while i < len(argv) and _SHELL_ASSIGNMENT_RE.match(argv[i]):
            i += 1
    if i < len(argv) and argv[i] in {"command"}:
        i += 1
    if i < len(argv) and argv[i] == "sudo":
        i += 1
        while i < len(argv) and argv[i].startswith("-"):
            flag = argv[i]
            i += 1
            if flag in {"-u", "--user"} and i < len(argv):
                i += 1
    if i >= len(argv):
        return None
    return i


def _argv_program(argv: list[str]) -> Optional[str]:
    idx = _argv_program_index(argv)
    if idx is None:
        return None
    return os.path.basename(argv[idx]).lower()


_SHELL_C_WRAPPERS = {"bash", "sh", "dash"}


def _shell_wrapper_c_string(argv: list[str]) -> Optional[str]:
    idx = _argv_program_index(argv)
    if idx is None:
        return None
    prog = os.path.basename(argv[idx]).lower()
    if prog not in _SHELL_C_WRAPPERS:
        return None

    i = idx + 1
    while i < len(argv):
        a = argv[i]
        if a == "--":
            break
        if a == "-c":
            return argv[i + 1] if i + 1 < len(argv) else None
        # bash -lc / sh -c style short-flag clusters.
        if a.startswith("-") and not a.startswith("--") and a != "-" and "c" in a[1:]:
            return argv[i + 1] if i + 1 < len(argv) else None
        i += 1
    return None


def _unwrap_shell_wrapped_command(segment: str, *, max_depth: int = 3) -> str:
    seg = (segment or "").strip()
    for _ in range(max_depth):
        if not seg:
            return seg
        try:
            argv = shlex.split(seg, posix=True)
        except ValueError:
            return seg
        inner = _shell_wrapper_c_string(argv)
        if not inner:
            return seg
        seg = _shell_tail_command(inner)
    return seg


def _should_downgrade_exit_code_to_debug(cmd: str, *, exit_code: int, output: str) -> bool:
    """Downgrade expected nonzero exits for probe-style commands.

    Key case: wrapped shell execution (bash/sh -c) around commands like rg/grep/test/diff.
    """
    if exit_code == 0:
        return False
    tail = _shell_tail_command(cmd)
    if not tail:
        return False
    tail = _unwrap_shell_wrapped_command(tail)
    if not tail:
        return False
    try:
        argv = shlex.split(tail, posix=True)
    except ValueError:
        return False
    prog = _argv_program(argv)
    if not prog:
        return False
    rule = _EXPECTED_NONZERO_EXIT_RULES.get(prog)
    if not rule:
        return False
    if exit_code not in rule.exit_codes:
        return False
    if rule.require_empty_output and (output or "").strip():
        return False
    if rule.argv_predicate and not rule.argv_predicate(argv, tail):
        return False
    return True


# ---------------------------------------------------------------------------
# Cost tracking — accumulate across all tool calls
# ---------------------------------------------------------------------------
cumulative_cost = 0.0

# ---------------------------------------------------------------------------
# Session stats — for end summary
# ---------------------------------------------------------------------------
files_created = []
files_edited = []
bash_commands = []
tools_used = {}  # tool_name -> count

# ---------------------------------------------------------------------------
# Stream logging for session resume
# ---------------------------------------------------------------------------
stream_log = None
is_replay = os.environ.get("REPLAY_MODE", "false").lower() == "true"
_stream_log_default = "redacted" if safe_mode else "full"
_stream_log_raw = os.environ.get("CODEFLOW_STREAM_LOG")
stream_log_mode = (_stream_log_raw if _stream_log_raw is not None else _stream_log_default).strip().lower()
if stream_log_mode not in {"full", "redacted", "off"}:
    stream_log_mode = _stream_log_default
if relay_dir and not is_replay:
    stream_path = os.path.join(relay_dir, "stream.jsonl")
    try:
        stream_log = open(stream_path, "a", encoding="utf-8", errors="replace")
    except OSError:
        stream_log = None

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def format_file_preview(content):
    """Return file content as-is (no truncation/chunking in parser)."""
    lines = content.split("\n")
    total = len(lines)
    return content, total


def _redact_obj(obj):
    if isinstance(obj, str):
        return redact_text(obj, strict=True)
    if isinstance(obj, list):
        return [_redact_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _redact_obj(v) for k, v in obj.items()}
    return obj

def _delivery_stats() -> dict:
    stats = getattr(platform, "DELIVERY_STATS", None)
    return stats if isinstance(stats, dict) else {}


def _delivery_summary_lines() -> list[str]:
    stats = _delivery_stats()
    ok = int(stats.get("http_ok", 0) or 0)
    fail = int(stats.get("http_fail", 0) or 0)
    retries = int(stats.get("http_retries", 0) or 0)
    drops = int(stats.get("drops", 0) or 0)
    rate_limits = int(stats.get("rate_limit_count", 0) or 0)
    last_error = str(stats.get("last_error", "") or "").strip()

    lines: list[str] = []
    if ok or fail or retries or drops or rate_limits:
        extra: list[str] = []
        if drops:
            extra.append(f"drops={drops}")
        if rate_limits:
            extra.append(f"429={rate_limits}")
        suffix = f" ({' '.join(extra)})" if extra else ""
        lines.append(f"  📮 Delivery: ok={ok} fail={fail} retries={retries}{suffix}")
    if last_error:
        lines.append("  📮 Last error: " + redact_text(last_error, strict=True))
    return lines


def _write_delivery_summary_local():
    if not relay_dir or is_replay:
        return
    try:
        payload = {
            "platform": platform_name,
            "safeMode": bool(safe_mode),
            "streamLogMode": stream_log_mode,
            "delivery": _delivery_stats(),
        }
        path = os.path.join(relay_dir, "delivery-summary.json")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
        os.replace(tmp, path)
    except Exception:
        pass

if not isinstance(getattr(platform, "DELIVERY_STATS", None), dict):
    try:
        platform.DELIVERY_STATS = {}
    except Exception:
        pass

governor = DeliveryGovernor(
    platform,
    platform_name=platform_name,
    stream_log=stream_log,
    delivery_stats=getattr(platform, "DELIVERY_STATS", {}) if isinstance(getattr(platform, "DELIVERY_STATS", None), dict) else {},
    flush_delivery_summary=_write_delivery_summary_local,
    replay_delay_sec=0.5 if is_replay else 0.0,
)

# ---------------------------------------------------------------------------
# Codex compact-rollup state (Telegram-friendly anti-spam mode)
# ---------------------------------------------------------------------------
codex_turn_idx = 0
codex_think_header = ""
codex_cmd_header = ""
codex_last_agent_text = ""


def _compact_enabled() -> bool:
    return compact_codex_updates and platform_supports_edit and not is_replay


def _platform_max_text() -> Optional[int]:
    v = getattr(platform, "MAX_TEXT", None)
    if isinstance(v, int) and v > 0:
        return v
    return None


def _start_codex_turn():
    global codex_turn_idx, codex_last_agent_text
    global codex_think_header, codex_cmd_header

    codex_turn_idx += 1
    codex_last_agent_text = ""
    codex_think_header = f"🧠 Round {codex_turn_idx} thinking…"
    codex_cmd_header = f"🖥️ Round {codex_turn_idx} commands / results"

    if _compact_enabled() and _should_emit("state"):
        governor.start_turn()
        governor.submit_state("think", codex_think_header)
        governor.submit_state("cmd", codex_cmd_header)
        governor.tick(max_ops=8)


def _compact_update(kind: str, line: str):
    global codex_think_header, codex_cmd_header

    line = redact_text((line or ""), strict=safe_mode).strip()
    if not line:
        return

    if codex_turn_idx <= 0:
        _start_codex_turn()

    if kind == "think":
        if _compact_enabled() and _should_emit("state"):
            governor.submit_state("think", codex_think_header + "\n" + line)
            governor.tick(max_ops=4)
            if output_mode == "verbose":
                post(line)
        else:
            post(line)
        return

    if _compact_enabled() and _should_emit("state"):
        governor.submit_state("cmd", codex_cmd_header + "\n" + line)
        governor.tick(max_ops=4)
        if output_mode == "verbose":
            post(line)
    else:
        post(line)


# ---------------------------------------------------------------------------
# Codex event handlers (--json JSONL format)
# ---------------------------------------------------------------------------
# Codex events: thread.started, turn.started, turn.completed, turn.failed,
#               item.started, item.completed, error

def handle_codex_event(evt):
    """Process a single Codex --json event and post formatted messages."""
    global cumulative_cost

    etype = evt.get("type", "")

    if etype == "thread.started":
        thread_id = evt.get("thread_id", "?")
        post(f"⚙️ Codex session `{thread_id[:12]}…`")

    elif etype == "turn.started":
        _start_codex_turn()

    elif etype == "item.started":
        item = evt.get("item", {})
        _handle_codex_item(item, started=True)

    elif etype == "item.completed":
        item = evt.get("item", {})
        _handle_codex_item(item, started=False)

    elif etype == "turn.completed":
        usage = evt.get("usage", {})
        inp = usage.get("input_tokens", 0) if isinstance(usage, dict) else 0
        cached = usage.get("cached_input_tokens", 0) if isinstance(usage, dict) else 0
        out = usage.get("output_tokens", 0) if isinstance(usage, dict) else 0

        # Codex pricing: o3/o4-mini varies; approximate with $2/M in, $8/M out
        cost = inp * 0.000002 + out * 0.000008
        cumulative_cost += cost

        summary = f"✅ Round {max(codex_turn_idx, 1)} done — {inp:,} in ({cached:,} cached) / {out:,} out"
        if codex_last_agent_text:
            summary += "\n\n" + codex_last_agent_text
        post_final(summary)

    elif etype == "turn.failed":
        error = evt.get("error", {})
        msg = error.get("message", "Unknown error") if isinstance(error, dict) else str(error)
        post_final(f"❌ Round {max(codex_turn_idx, 1)} failed: {msg}")

    elif etype == "error":
        msg = evt.get("message", evt.get("error", "Unknown error"))
        post_error(f"❌ **Error:** {str(msg)}")


def _handle_codex_item(item, started=False):
    """Format a Codex item event (command, message, file change, etc.)."""
    global codex_last_agent_text

    itype = item.get("type", "")

    if itype == "command_execution":
        cmd = item.get("command", "?")
        if started:
            _compact_update("cmd", f"🖥️ Exec: `{cmd}`")
            bash_commands.append(cmd)
            tools_used["command_execution"] = tools_used.get("command_execution", 0) + 1
        else:
            output = item.get("output")
            if output is None or output == "":
                output = item.get("aggregated_output")
            if not isinstance(output, str):
                output = "" if output is None else str(output)
            exit_code = item.get("exit_code")
            try:
                exit_code = None if exit_code is None else int(exit_code)
            except Exception:
                exit_code = None
            if output:
                if safe_mode:
                    _compact_update(
                        "cmd",
                        f"📤 Output: 🔒 suppressed by CODEFLOW_SAFE_MODE ({len(output)} chars)",
                    )
                else:
                    output = output.strip()
                    _compact_update("cmd", f"📤 Output: {output}")
            if exit_code is not None and exit_code != 0:
                if _should_downgrade_exit_code_to_debug(cmd, exit_code=exit_code, output=output):
                    post_debug(f"🔎 probe cmd: `{cmd}`\nexit code: {exit_code}")
                else:
                    warn = f"⚠️cmd: `{cmd}`\n⚠️Exit code: {exit_code}"
                    _compact_update("cmd", warn)
                    post_warning(warn)

    elif itype == "agent_message":
        text = item.get("text", "").strip()
        if text and not started:
            codex_last_agent_text = text
            _compact_update("think", f"💬 {text}")

    elif itype == "file_change":
        fp = item.get("file_path", item.get("path", "?"))
        change = item.get("change_type", item.get("status", "modified"))
        if not started:
            if change in ("created", "create"):
                files_created.append(fp)
                _compact_update("cmd", f"📝 Created `{fp}`")
            else:
                files_edited.append(fp)
                _compact_update("cmd", f"✏️ Modified `{fp}`")
            tools_used["file_change"] = tools_used.get("file_change", 0) + 1

    elif itype == "reasoning":
        text = item.get("text", "").strip()
        if text and not started:
            _compact_update("think", f"🧠 {text}")

    elif itype == "mcp_tool_call":
        name = item.get("name", item.get("tool", "?"))
        if started:
            _compact_update("cmd", f"🔧 MCP `{name}`")
            tools_used[f"mcp:{name}"] = tools_used.get(f"mcp:{name}", 0) + 1

    elif itype == "web_search":
        query = item.get("query", "?")
        if started:
            _compact_update("cmd", f"🔍 Search `{query}`")
            tools_used["web_search"] = tools_used.get("web_search", 0) + 1

    elif itype == "plan_update":
        if not started:
            text = item.get("text", "").strip()
            if text:
                _compact_update("think", f"📋 Plan: {text}")


# ---------------------------------------------------------------------------
# Stream format auto-detection
# ---------------------------------------------------------------------------
# Detect whether we're reading Claude Code stream-json or Codex --json
# based on the first JSON event's type field.
_stream_format = None  # "claude" or "codex", auto-detected on first event

CODEX_EVENT_TYPES = {
    "thread.started", "turn.started", "turn.completed", "turn.failed",
    "item.started", "item.completed", "error",
}


def detect_format(evt):
    """Detect stream format from first event."""
    global _stream_format
    etype = evt.get("type", "")
    if etype in CODEX_EVENT_TYPES:
        _stream_format = "codex"
    else:
        _stream_format = "claude"
    return _stream_format


# ---------------------------------------------------------------------------
# Main event loop
# ---------------------------------------------------------------------------
# Track the last tool_use name so we can correlate tool_results with their tool
_last_tool_name = None
# Track Codex session start for final summary
_codex_start_time = None

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    # Skip non-JSON lines (ANSI artifacts from unbuffer)
    if not line.startswith("{"):
        continue

    # Stream logging (for resume/debugging). Default: full raw lines.
    if stream_log and stream_log_mode == "full":
        try:
            stream_log.write(line + "\n")
            stream_log.flush()
        except Exception:
            pass

    try:
        evt = json.loads(line)
    except json.JSONDecodeError:
        continue

    if stream_log and stream_log_mode != "full":
        try:
            if stream_log_mode == "redacted":
                stream_log.write(json.dumps(_redact_obj(evt), ensure_ascii=False) + "\n")
            else:  # off: minimal metadata only
                meta = {"type": evt.get("type", "?")}
                subtype = evt.get("subtype")
                if subtype:
                    meta["subtype"] = subtype
                stream_log.write(json.dumps(meta, ensure_ascii=False) + "\n")
            stream_log.flush()
        except Exception:
            pass

    etype = evt.get("type", "")

    # Internal delivery anomaly events (appended into stream.jsonl by the delivery governor).
    # They must be safely ignored on resume and must not affect stream format detection.
    if isinstance(etype, str) and etype.startswith("codeflow.delivery."):
        continue

    # --- Auto-detect stream format on first event ---
    if _stream_format is None:
        detect_format(evt)
        if _stream_format == "codex":
            _codex_start_time = time.time()

    # --- Codex events ---
    if _stream_format == "codex":
        handle_codex_event(evt)
        continue

    # --- Claude Code: System init ---
    if etype == "system" and evt.get("subtype") == "init":
        model = evt.get("model", "unknown")
        mode = evt.get("permissionMode", "default")
        post(f"⚙️ Model: `{model}` | Mode: `{mode}`")

    # --- Assistant messages (tool calls + text) ---
    elif etype == "assistant":
        msg = evt.get("message", {})

        # Track cost from usage metadata if present
        usage = msg.get("usage", {})
        if usage:
            input_cost = usage.get("input_tokens", 0) * 0.000003   # $3/M input
            output_cost = usage.get("output_tokens", 0) * 0.000015  # $15/M output
            cumulative_cost += input_cost + output_cost

        for block in msg.get("content", []):
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                text = block["text"].strip()
                if text:
                    post(f"💬 {text}")

            elif block.get("type") == "tool_use":
                tool = block.get("name", "?")
                inp = block.get("input", {})

                # Track tool usage counts
                tools_used[tool] = tools_used.get(tool, 0) + 1
                _last_tool_name = tool

                if tool == "Write":
                    fp = inp.get("file_path", "?")
                    content = inp.get("content", "")
                    preview, total = format_file_preview(content)
                    if safe_mode:
                        post(f"📝 **Write** `{fp}` ({total} lines) — 🔒 preview suppressed (CODEFLOW_SAFE_MODE)")
                    else:
                        preview = redact_text(preview, strict=False)
                        post(f"📝 **Write** `{fp}` ({total} lines)\n```\n{preview}\n```")

                elif tool in ("Edit", "MultiEdit"):
                    fp = inp.get("file_path", "?")
                    post(f"✏️ **{tool}** `{fp}`")

                elif tool == "Bash":
                    cmd = inp.get("command", "?")
                    post(f"🖥️ **Bash** `{cmd}`")
                    bash_commands.append(cmd)

                elif tool == "Read":
                    fp = inp.get("file_path", "?")
                    if not skip_reads:
                        post(f"👁️ **Read** `{fp}`")

                elif tool == "WebSearch":
                    query = inp.get("query", "?")
                    post(f"🔍 **Search** `{query}`")

                elif tool == "WebFetch":
                    url = inp.get("url", "?")
                    post(f"🌐 **Fetch** `{url}`")

                else:
                    post(f"🔧 **{tool}**")

    # --- User events (tool results, bash output) ---
    elif etype == "user":
        # Handle tool_use_result (file create/update confirmations)
        result = evt.get("tool_use_result", {})
        if result and isinstance(result, dict):
            rtype = result.get("type", "")
            fp = result.get("filePath", "")
            if rtype == "create" and fp:
                files_created.append(fp)
                post(f"✅ Created `{fp}`")
            elif rtype == "update" and fp:
                files_edited.append(fp)
                post(f"✅ Updated `{fp}`")

        # Handle bash command output from tool_result content blocks
        msg = evt.get("message", {})
        for block in msg.get("content", []):
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_result":
                tool_failed = False
                try:
                    tool_failed = bool(block.get("is_error") is True or block.get("isError") is True)
                except Exception:
                    tool_failed = False
                try:
                    status = (block.get("status") or "").strip().lower()
                    if status in {"error", "failed", "failure"}:
                        tool_failed = True
                except Exception:
                    pass

                if not tool_failed:
                    err_obj = block.get("error")
                    if err_obj:
                        tool_failed = True

                tool_name = _last_tool_name or "Tool"

                if tool_failed:
                    if safe_mode:
                        post_error(f"❌ **{tool_name} failed** — 🔒 details suppressed (CODEFLOW_SAFE_MODE)")
                    else:
                        # Best-effort: extract a short reason from tool_result content.
                        reason = ""
                        try:
                            content = block.get("content")
                            if isinstance(content, str):
                                reason = content.strip()
                            elif isinstance(content, list):
                                parts: list[str] = []
                                for sub in content:
                                    if isinstance(sub, dict) and sub.get("type") == "text":
                                        t = (sub.get("text") or "").strip()
                                        if t:
                                            parts.append(t)
                                    if sum(len(p) for p in parts) >= 300:
                                        break
                                reason = "\n".join(parts).strip()
                        except Exception:
                            reason = ""

                        if not reason:
                            try:
                                reason = str(block.get("error") or "").strip()
                            except Exception:
                                reason = ""

                        if reason:
                            reason = redact_text(reason, strict=False)
                            if len(reason) > 300:
                                reason = reason[:299] + "…"
                            post_error(f"❌ **{tool_name} failed**\n{reason}")
                        else:
                            post_error(f"❌ **{tool_name} failed**")

                for sub in block.get("content", []):
                    if not isinstance(sub, dict):
                        continue
                    if sub.get("type") == "text" and _last_tool_name == "Bash":
                        stdout = sub.get("text", "").strip()
                        if stdout:
                            if safe_mode:
                                post(f"📤 **Output** — 🔒 suppressed (CODEFLOW_SAFE_MODE, {len(stdout)} chars)")
                            else:
                                stdout = redact_text(stdout, strict=False)
                                post(f"📤 **Output** ```\n{stdout}\n```")

    # --- Result (session complete) ---
    elif etype == "result":
        success = not evt.get("is_error", False)
        duration = evt.get("duration_ms", 0) / 1000
        cost = evt.get("total_cost_usd", 0)
        # Use the authoritative cost from the result if available, else our estimate
        final_cost = cost if cost else cumulative_cost
        result_text = evt.get("result", "")
        if not isinstance(result_text, str):
            result_text = "" if result_text is None else str(result_text)
        turns = evt.get("num_turns", 0)

        icon = "✅" if success else "❌"
        status = "Completed" if success else "Failed"

        # --- End summary block ---
        summary_parts = [f"{icon} **{status}** | {turns} turns | {duration:.1f}s | ${final_cost:.4f}"]

        if result_text:
            summary_parts.append(f"> {result_text}")

        summary_parts.append("")  # blank line before summary
        summary_parts.append("📊 **Session Summary**")

        if files_created:
            unique_created = sorted(set(files_created))
            summary_parts.append(f"  📝 Created: {len(unique_created)} file(s)")
            for f in unique_created[:10]:
                summary_parts.append(f"    • `{f}`")
            if len(unique_created) > 10:
                summary_parts.append(f"    • ... and {len(unique_created) - 10} more")

        if files_edited:
            unique_edited = sorted(set(files_edited))
            summary_parts.append(f"  ✏️ Edited: {len(unique_edited)} file(s)")
            for f in unique_edited[:10]:
                summary_parts.append(f"    • `{f}`")
            if len(unique_edited) > 10:
                summary_parts.append(f"    • ... and {len(unique_edited) - 10} more")

        if bash_commands:
            summary_parts.append(f"  🖥️ Bash commands: {len(bash_commands)}")

        if tools_used:
            tool_summary = ", ".join(f"{k}: {v}" for k, v in sorted(tools_used.items()))
            summary_parts.append(f"  🔧 Tools: {tool_summary}")

        for line in _delivery_summary_lines():
            summary_parts.append(line)

        summary_parts.append(f"  💰 Total cost: ${final_cost:.4f}")

        post_final("\n".join(summary_parts))

# --- Codex end-of-session summary ---
if _stream_format == "codex" and _codex_start_time:
    duration = time.time() - _codex_start_time
    summary_parts = [f"✅ **Codex Session Complete** | {duration:.1f}s | ${cumulative_cost:.4f}"]
    summary_parts.append("")
    summary_parts.append("📊 **Session Summary**")
    if files_created:
        unique_created = sorted(set(files_created))
        summary_parts.append(f"  📝 Created: {len(unique_created)} file(s)")
        for f in unique_created[:10]:
            summary_parts.append(f"    • `{f}`")
    if files_edited:
        unique_edited = sorted(set(files_edited))
        summary_parts.append(f"  ✏️ Edited: {len(unique_edited)} file(s)")
        for f in unique_edited[:10]:
            summary_parts.append(f"    • `{f}`")
    if bash_commands:
        summary_parts.append(f"  🖥️ Commands: {len(bash_commands)}")
    if tools_used:
        tool_summary = ", ".join(f"{k}: {v}" for k, v in sorted(tools_used.items()))
        summary_parts.append(f"  🔧 Tools: {tool_summary}")
    for line in _delivery_summary_lines():
        summary_parts.append(line)
    summary_parts.append(f"  💰 Total cost: ${cumulative_cost:.4f}")
    post_final("\n".join(summary_parts))

# Drain pending delivery (may wait for rate-limit windows).
governor.flush()

# Close stream log
if stream_log:
    stream_log.close()

_write_delivery_summary_local()

print("RELAY_DONE", flush=True)
