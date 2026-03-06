#!/bin/bash
# recommend-agent.sh - Recommend the best subagent for a task
# Skill: dev-team

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh" 2>/dev/null || true

DESCRIPTION=""
PROMPT=""
PROMPT_FILE=""
FORMAT="text"
PHASE="build"

usage() {
    echo "Usage: $0 --description <text> [--prompt <text> | --prompt-file <file>] [--phase build|review|fixup] [--format text|json]"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --description) DESCRIPTION="$2"; shift 2 ;;
        --prompt) PROMPT="$2"; shift 2 ;;
        --prompt-file) PROMPT_FILE="$2"; shift 2 ;;
        --phase) PHASE="$2"; shift 2 ;;
        --format) FORMAT="$2"; shift 2 ;;
        *) usage ;;
    esac
done

if [[ -z "$DESCRIPTION" ]]; then
    usage
fi

if [[ -n "$PROMPT_FILE" ]]; then
    if [[ ! -f "$PROMPT_FILE" ]]; then
        echo "Prompt file not found: $PROMPT_FILE" >&2
        exit 1
    fi
    PROMPT="$(cat "$PROMPT_FILE")"
fi

TASKS_FILE="$(get_tasks_file 2>/dev/null || echo "$(cd "$SCRIPT_DIR/.." && pwd)/assets/active-tasks.json")"
AGENTS_CONFIG="$(get_agent_config 2>/dev/null || echo "$(cd "$SCRIPT_DIR/.." && pwd)/config/agents.json")"
USER_CONFIG="$(get_user_config 2>/dev/null || echo "$(cd "$SCRIPT_DIR/.." && pwd)/config/user.json")"

DESC_B64=$(printf '%s' "$DESCRIPTION" | base64 | tr -d '\n')
PROMPT_B64=$(printf '%s' "$PROMPT" | base64 | tr -d '\n')

python3 <<PYEOF
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
import shlex
from pathlib import Path

desc = base64.b64decode("$DESC_B64").decode("utf-8")
prompt = base64.b64decode("$PROMPT_B64").decode("utf-8")
fmt = "$FORMAT"
phase = "$PHASE"
tasks_file = Path("$TASKS_FILE")
agents_config_path = Path("$AGENTS_CONFIG")
user_config_path = Path("$USER_CONFIG")

config = {}
if agents_config_path.exists():
    with agents_config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

agent_defs = (config.get("agents") or {})
routing = (config.get("routing") or {})
user_config = {}
if user_config_path.exists():
    try:
        user_config = json.loads(user_config_path.read_text(encoding="utf-8"))
    except Exception:
        user_config = {}
agent_policy = (user_config.get("agentPolicy") or {})
enabled_agents_cfg = agent_policy.get("enabledAgents")
phase_allowed_cfg = (agent_policy.get("phaseAllowedAgents") or {})
enabled_agents = set(enabled_agents_cfg) if isinstance(enabled_agents_cfg, list) and enabled_agents_cfg else set(agent_defs.keys() or ["codex","claude","gemini","cursor"])
phase_allowed = phase_allowed_cfg.get(phase)
if not isinstance(phase_allowed, list) or not phase_allowed:
    phase_allowed = list(enabled_agents)
phase_allowed = [a for a in phase_allowed if a in enabled_agents]

text = f"{desc}\n{prompt}".lower()

keyword_weights = {
    "frontend": {"claude": 4, "cursor": 4, "gemini": 2},
    "ui": {"claude": 4, "cursor": 4, "gemini": 3},
    "ux": {"claude": 3, "cursor": 4, "gemini": 4},
    "product": {"cursor": 4, "claude": 3, "gemini": 3},
    "css": {"claude": 4, "cursor": 4, "gemini": 1},
    "html": {"claude": 4, "cursor": 3},
    "mobile": {"claude": 3, "cursor": 3, "gemini": 2},
    "日志": {"codex": 2, "claude": 1},
    "看板": {"cursor": 2, "claude": 2, "codex": 1},
    "backend": {"codex": 5, "claude": 2},
    "api": {"codex": 5, "claude": 2},
    "server": {"codex": 4, "claude": 1},
    "db": {"codex": 4},
    "sql": {"codex": 5},
    "bug": {"codex": 4, "claude": 2},
    "debug": {"codex": 4, "claude": 2},
    "refactor": {"codex": 4, "claude": 2},
    "test": {"codex": 3, "claude": 2},
    "spec": {"gemini": 4, "claude": 2, "cursor": 2},
    "设计": {"gemini": 4, "cursor": 3, "claude": 2},
    "原型": {"gemini": 4, "cursor": 3},
}

scores = {name: 0 for name in ["codex", "claude", "gemini", "cursor"]}
reasons = {name: [] for name in scores}

for kw, weights in keyword_weights.items():
    if kw in text:
        for agent, delta in weights.items():
            scores[agent] += delta
            reasons[agent].append(f"关键词:{kw}(+{delta})")

# Heuristic from file extensions in prompt/description
if re.search(r"\.(css|scss|html|tsx|jsx)\b", text):
    for agent, delta in [("claude", 2), ("cursor", 2)]:
        scores[agent] += delta
        reasons[agent].append(f"前端文件信号(+{delta})")
if re.search(r"\.(py|go|rs|java|kt|sql)\b", text):
    scores["codex"] += 2
    reasons["codex"].append("后端/系统文件信号(+2)")

# Running-load penalty
running_counts = {name: 0 for name in scores}
if tasks_file.exists():
    try:
        data = json.loads(tasks_file.read_text(encoding="utf-8"))
        for item in data.get("agents", []):
            if item.get("status") == "running":
                ag = item.get("agent")
                if ag in running_counts:
                    running_counts[ag] += 1
    except Exception:
        pass

for agent, cnt in running_counts.items():
    if cnt:
        penalty = min(4, cnt)
        scores[agent] -= penalty
        reasons[agent].append(f"当前负载-{penalty} (running={cnt})")

def probe(agent: str):
    cmd = agent_defs.get(agent, {}).get("command") or agent
    if shutil.which(cmd) is None:
        return {"ok": False, "status": "missing_cli", "detail": f"{cmd} not found"}

    try:
        if agent == "cursor":
            proc = subprocess.run(
                [cmd, "agent", "status"],
                capture_output=True, text=True, timeout=4
            )
            out = (proc.stdout or "") + (proc.stderr or "")
            if "Not logged in" in out:
                # Fallback: probe inside tmux because dev-team runs subagents in tmux and
                # some environments cannot read Keychain auth in non-interactive shells.
                if shutil.which("tmux"):
                    probe_session = f"teamdev-cursor-probe-{os.getpid()}"
                    probe_file = f"/tmp/{probe_session}.txt"
                    try:
                        subprocess.run(
                            ["tmux", "new-session", "-d", "-s", probe_session, f"cursor agent status > {shlex.quote(probe_file)} 2>&1"],
                            capture_output=True, text=True, timeout=4
                        )
                        time.sleep(2)
                        tmux_out = ""
                        if os.path.exists(probe_file):
                            with open(probe_file, "r", encoding="utf-8", errors="ignore") as f:
                                tmux_out = f.read()
                        subprocess.run(["tmux", "kill-session", "-t", probe_session], capture_output=True, text=True, timeout=2)
                        try:
                            os.remove(probe_file)
                        except OSError:
                            pass
                        if "Not logged in" not in tmux_out:
                            return {"ok": True, "status": "ok_tmux", "detail": "cursor status ok in tmux"}
                    except Exception:
                        pass
                return {"ok": False, "status": "not_logged_in", "detail": "cursor agent login required"}
            return {"ok": True, "status": "ok", "detail": "cursor status ok"}
        if agent in ("codex", "claude"):
            proc = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=4)
            if proc.returncode == 0:
                return {"ok": True, "status": "ok", "detail": (proc.stdout or proc.stderr).strip().splitlines()[:1][0] if (proc.stdout or proc.stderr).strip() else "ok"}
            return {"ok": False, "status": "version_failed", "detail": (proc.stderr or proc.stdout).strip() or "version check failed"}
        # Gemini CLI appears unstable on some machines for --help/--version, treat command presence as soft-ok.
        return {"ok": True, "status": "soft_ok", "detail": "command found (auth/runtime not verified)"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "status": "timeout", "detail": "health probe timeout"}
    except Exception as e:
        return {"ok": False, "status": "probe_error", "detail": str(e)}

health = {a: probe(a) for a in scores}

ranked = []
for agent in scores:
    if agent not in enabled_agents:
        continue
    if phase_allowed and agent not in phase_allowed:
        continue
    score = scores[agent]
    h = health[agent]
    if h["ok"]:
        score += 2
        reasons[agent].append(f"健康检查:{h['status']}(+2)")
    else:
        score -= 100
        reasons[agent].append(f"健康检查:{h['status']}(-100)")
    agent_cfg = agent_defs.get(agent, {})
    ranked.append({
        "agent": agent,
        "score": score,
        "health": h,
        "defaultModel": agent_cfg.get("defaultModel"),
        "capabilities": agent_cfg.get("capabilities") or [],
        "reasons": reasons[agent],
    })

ranked.sort(key=lambda x: x["score"], reverse=True)

fallback = routing.get("defaultAgent", "codex")
if fallback not in enabled_agents or (phase_allowed and fallback not in phase_allowed):
    fallback = next(iter(phase_allowed or enabled_agents or ["codex"]), "codex")
recommended = ranked[0]["agent"] if ranked else fallback
if ranked and ranked[0]["score"] < -50:
    recommended = fallback

result = {
    "recommendedAgent": recommended,
    "recommendedModel": (agent_defs.get(recommended, {}) or {}).get("defaultModel"),
    "fallbackAgent": fallback,
    "ranking": ranked,
    "summary": {
        "description": desc,
        "runningCounts": running_counts,
        "phase": phase,
        "enabledAgents": sorted(enabled_agents),
        "phaseAllowedAgents": phase_allowed,
    }
}

if fmt == "json":
    print(json.dumps(result, ensure_ascii=False, indent=2))
else:
    print(f"Recommended: {result['recommendedAgent']} model={result['recommendedModel'] or '-'}")
    for item in ranked:
        health_tag = item["health"]["status"]
        print(f"- {item['agent']}: score={item['score']} health={health_tag}")
        if item["reasons"]:
            print(f"  reasons: {', '.join(item['reasons'][:6])}")
        if item.get("defaultModel"):
            print(f"  defaultModel: {item['defaultModel']}")
PYEOF
