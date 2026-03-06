#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"
STATE_ROOT="${OPENCLAW_STATE_ROOT:-$HOME/.openclaw/state/session-rotator}"
ARCHIVE_ROOT="${OPENCLAW_ARCHIVE_ROOT:-$HOME/.openclaw/knowledge/session-archives}"
THRESHOLD_PERCENT="${SESSION_ROTATE_THRESHOLD_PERCENT:-80}"
COOLDOWN_SECONDS="${SESSION_ROTATE_COOLDOWN_SECONDS:-1800}"
MAX_ITEMS_PER_ROLE="${SESSION_ROTATE_MAX_ITEMS_PER_ROLE:-6}"

LOCK_FILE="$STATE_ROOT/rotator.lock"
MAP_FILE="$STATE_ROOT/active-session-map.json"
COOLDOWN_DIR="$STATE_ROOT/cooldowns"
TMP_SESSIONS_JSON="$STATE_ROOT/sessions.json"
TMP_HOT_TSV="$STATE_ROOT/hot-sessions.tsv"

mkdir -p "$STATE_ROOT" "$COOLDOWN_DIR" "$ARCHIVE_ROOT" "$ARCHIVE_ROOT/latest"

log() { printf '[openclaw-session-rotator] %s\n' "$*"; }

acquire_lock() {
  if ( set -o noclobber; echo "$$" > "$LOCK_FILE" ) 2>/dev/null; then
    trap 'rm -f "$LOCK_FILE"' EXIT
    return 0
  fi
  if [[ -f "$LOCK_FILE" ]]; then
    local lock_pid
    lock_pid="$(cat "$LOCK_FILE" 2>/dev/null || true)"
    if [[ -n "$lock_pid" ]] && ! kill -0 "$lock_pid" 2>/dev/null; then
      rm -f "$LOCK_FILE"
      if ( set -o noclobber; echo "$$" > "$LOCK_FILE" ) 2>/dev/null; then
        trap 'rm -f "$LOCK_FILE"' EXIT
        return 0
      fi
    fi
  fi
  return 1
}

if ! acquire_lock; then
  exit 0
fi

if ! "$OPENCLAW_BIN" sessions --all-agents --json > "$TMP_SESSIONS_JSON" 2>/dev/null; then
  log "sessions list unavailable, skip"
  exit 0
fi

python3 - "$TMP_SESSIONS_JSON" "$THRESHOLD_PERCENT" > "$TMP_HOT_TSV" <<'PY'
import json, sys
path = sys.argv[1]
threshold = int(sys.argv[2])
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
for s in data.get("sessions", []):
    total = int(s.get("totalTokens") or 0)
    context = int(s.get("contextTokens") or 0)
    if context <= 0:
        continue
    pct = int((total * 100) / context)
    if pct < threshold:
        continue
    print("\t".join([
        s.get("key", ""),
        s.get("agentId", ""),
        s.get("sessionId", ""),
        str(pct),
        str(total),
        str(context),
        str(s.get("updatedAt") or 0),
        s.get("kind", ""),
    ]))
PY

if [[ ! -s "$TMP_HOT_TSV" ]]; then
  exit 0
fi

while IFS=$'\t' read -r session_key agent_id session_id pct total context _updated_at _kind; do
  [[ -n "$session_key" && -n "$agent_id" && -n "$session_id" ]] || continue

  case "$session_key" in
    agent:*:main) ;;
    *) continue ;;
  esac
  case "$session_key" in
    *:cron:*|*:run:*) continue ;;
  esac

  safe_key="$(printf '%s' "$session_key" | shasum -a 1 | awk '{print $1}')"
  cooldown_file="$COOLDOWN_DIR/${safe_key}.ts"
  now_ts="$(date +%s)"

  if [[ -f "$cooldown_file" ]]; then
    last_ts="$(cat "$cooldown_file" 2>/dev/null || echo 0)"
    if [[ "$last_ts" =~ ^[0-9]+$ ]] && (( now_ts - last_ts < COOLDOWN_SECONDS )); then
      continue
    fi
  fi

  session_file="$HOME/.openclaw/agents/$agent_id/sessions/${session_id}.jsonl"
  [[ -f "$session_file" ]] || continue

  agent_archive_dir="$ARCHIVE_ROOT/$agent_id"
  mkdir -p "$agent_archive_dir"
  stamp="$(date +%Y%m%d-%H%M%S)"
  archive_file="$agent_archive_dir/${stamp}-${safe_key:0:10}.md"
  handoff_file="$agent_archive_dir/${stamp}-${safe_key:0:10}.handoff.txt"
  latest_file="$ARCHIVE_ROOT/latest/${agent_id}.md"

  python3 - "$session_file" "$archive_file" "$handoff_file" "$session_key" "$agent_id" "$pct" "$total" "$context" "$MAX_ITEMS_PER_ROLE" <<'PY'
import json, sys
from pathlib import Path
session_file = Path(sys.argv[1])
archive_file = Path(sys.argv[2])
handoff_file = Path(sys.argv[3])
session_key, agent_id, pct, total, context = sys.argv[4:9]
max_items = int(sys.argv[9])
user_items, assistant_items = [], []
first_ts, last_ts = None, None

def norm(s: str) -> str:
    s = s.replace("\n", " ").replace("\r", " ").strip()
    return s if len(s) <= 220 else s[:217] + "..."

for raw in session_file.read_text(encoding="utf-8").splitlines():
    if not raw.strip():
        continue
    try:
        row = json.loads(raw)
    except json.JSONDecodeError:
        continue
    if row.get("type") != "message":
        continue
    ts = row.get("timestamp")
    if isinstance(ts, str):
        if first_ts is None:
            first_ts = ts
        last_ts = ts
    msg = row.get("message") or {}
    role = msg.get("role")
    if role not in ("user", "assistant"):
        continue
    parts = msg.get("content") or []
    texts = []
    for part in parts:
        if isinstance(part, dict) and part.get("type") == "text":
            t = (part.get("text") or "").strip()
            if t:
                texts.append(t)
    if not texts:
        continue
    merged = norm(" ".join(texts))
    if role == "user":
        user_items.append(merged)
    else:
        assistant_items.append(merged)

user_items = user_items[-max_items:]
assistant_items = assistant_items[-max_items:]

lines = [
    f"# Session Archive - {session_key}",
    "",
    "## Snapshot",
    f"- Agent: `{agent_id}`",
    f"- Session Key: `{session_key}`",
    f"- Session File: `{session_file}`",
    f"- Context Usage: `{pct}%` ({total}/{context})",
]
if first_ts and last_ts:
    lines.append(f"- Time Range: `{first_ts}` ~ `{last_ts}`")
lines += ["", "## Latest User Messages"]
lines += [f"- {x}" for x in user_items] if user_items else ["- (none)"]
lines += ["", "## Latest Assistant Replies"]
lines += [f"- {x}" for x in assistant_items] if assistant_items else ["- (none)"]
lines += [
    "",
    "## Handoff Prompt (Token-Minimal)",
    "- Continue from this archive only.",
    "- Keep response concise and action-oriented.",
    "- Re-open unresolved user asks first.",
    "",
]
archive_file.write_text("\n".join(lines), encoding="utf-8")

handoff = [
    "你正在接手一个达到上下文阈值后轮换的会话。",
    f"请先读取归档文件：{archive_file}",
    "请用不超过8行完成：",
    "1) 已完成事项",
    "2) 待继续事项",
    "3) 你接下来马上执行的第一步",
]
handoff_file.write_text("\n".join(handoff) + "\n", encoding="utf-8")
PY

  cp "$archive_file" "$latest_file"

  new_session_id="$(python3 - <<'PY'
import uuid
print(uuid.uuid4())
PY
)"
  store_file="$HOME/.openclaw/agents/$agent_id/sessions/sessions.json"

  python3 - "$store_file" "$session_key" "$new_session_id" <<'PY'
import json, os, sys, time
store_file, session_key, new_session_id = sys.argv[1:]
with open(store_file, "r", encoding="utf-8") as f:
    data = json.load(f)
entry = data.get(session_key)
if not isinstance(entry, dict):
    raise SystemExit(1)
session_dir = os.path.dirname(store_file)
entry["sessionId"] = new_session_id
entry["sessionFile"] = os.path.join(session_dir, f"{new_session_id}.jsonl")
entry["updatedAt"] = int(time.time() * 1000)
entry["abortedLastRun"] = False
entry["compactionCount"] = 0
entry["inputTokens"] = 0
entry["outputTokens"] = 0
entry["cacheRead"] = 0
entry["cacheWrite"] = 0
entry["totalTokens"] = 0
entry["totalTokensFresh"] = True
entry["systemSent"] = False
entry["systemPromptReport"] = {}
with open(store_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY

  "$OPENCLAW_BIN" agent --agent "$agent_id" --message "$(cat "$handoff_file")" --json >/dev/null 2>&1 || true

  printf '%s' "$now_ts" > "$cooldown_file"

  python3 - "$MAP_FILE" "$session_key" "$agent_id" "$new_session_id" "$archive_file" "$handoff_file" "$pct" <<'PY'
import json, os, sys
from datetime import datetime, timezone
path, session_key, agent_id, new_session_id, archive_file, handoff_file, pct = sys.argv[1:]
data = {}
if os.path.exists(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
if "sessions" not in data or not isinstance(data["sessions"], dict):
    data["sessions"] = {}
data["sessions"][session_key] = {
    "agentId": agent_id,
    "newSessionId": new_session_id,
    "lastArchiveFile": archive_file,
    "lastHandoffFile": handoff_file,
    "lastTriggerPercent": int(pct),
    "updatedAt": datetime.now(timezone.utc).isoformat(),
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
PY

  log "archived $session_key at ${pct}% -> $archive_file"
done < "$TMP_HOT_TSV"

exit 0
