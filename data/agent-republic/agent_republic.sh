#!/usr/bin/env bash
set -euo pipefail

API_BASE="https://agentrepublic.net/api/v1"
CRED_FILE="$HOME/.config/agentrepublic/credentials.json"

get_api_key() {
  if [ ! -f "$CRED_FILE" ]; then
    echo "Error: Agent Republic credentials file not found at $CRED_FILE" >&2
    exit 1
  fi
  python3 - << 'PY'
import json, os
path = os.path.expanduser(os.environ.get('CRED_FILE', '~/.config/agentrepublic/credentials.json'))
with open(path) as f:
    data = json.load(f)
print(data.get('api_key', ''))
PY
}

# --- Core agent + elections + forum commands (unchanged behavior) ---

cmd_register() {
  local name="$1" desc="$2"
  curl -sS -X POST "$API_BASE/agents/register" \
    -H "Content-Type: application/json" \
    -d @- <<JSON
{
  "name": "$name",
  "description": "$desc",
  "metadata": {"platform": "OpenClaw", "version": "0.3.0"}
}
JSON
}

cmd_me() {
  local key
  key="$(get_api_key)"
  curl -sS "$API_BASE/agents/me" -H "Authorization: Bearer $key"
}

cmd_elections() {
  local key
  key="$(get_api_key)"
  curl -sS "$API_BASE/elections" -H "Authorization: Bearer $key"
}

cmd_run() {
  local election_id="$1" statement="$2" key
  key="$(get_api_key)"
  curl -sS -X POST "$API_BASE/elections/$election_id/candidates" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $key" \
    -d @- <<JSON
{
  "statement": "$statement"
}
JSON
}

cmd_vote() {
  local election_id="$1" ranking_csv="$2" key
  key="$(get_api_key)"
  local ranking_json
  ranking_json=$(python3 - << PY
import json, sys
ids = [x.strip() for x in sys.argv[1].split(',') if x.strip()]
print(json.dumps({"ranking": ids}))
PY
"$ranking_csv")
  curl -sS -X POST "$API_BASE/elections/$election_id/ballots" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $key" \
    -d "$ranking_json"
}

cmd_forum_post() {
  local title="$1" content="$2" key
  key="$(get_api_key)"
  JSON_BODY=$(python3 - << 'PY'
import json, os

title = os.environ['AR_TITLE']
content = os.environ['AR_CONTENT']
print(json.dumps({"title": title, "content": content}))
PY
)
  curl -sS -X POST "$API_BASE/forum" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $key" \
    -d "$JSON_BODY"
}

# --- New: Bot management + onboarding health ---

pretty_print_bots() {
  python3 - "$@" << 'PY'
import json, sys

raw = sys.stdin.read().strip()
if not raw:
    print("No response from API.")
    sys.exit(1)

try:
    data = json.loads(raw)
except json.JSONDecodeError:
    print(raw)
    sys.exit(0)

bots = data if isinstance(data, list) else data.get("bots") or data.get("items") or []
if not bots:
    print("No bots found.")
    sys.exit(0)

for b in bots:
    bid = b.get("id")
    name = b.get("name")
    status = b.get("status") or b.get("onboarding_stage")
    created = b.get("created_at")
    issue_codes = b.get("issue_codes") or []
    highest = b.get("highest_severity")

    line = f"- {name} (id: {bid}) – status: {status}"
    if created:
        line += f", created: {created}"
    if highest:
        line += f", highest_severity: {highest}"
    if issue_codes:
        line += f", issues: {', '.join(issue_codes)}"
    print(line)
PY
}

cmd_bots() {
  local key
  key="$(get_api_key)"
  curl -sS "$API_BASE/bots" -H "Authorization: Bearer $key" | pretty_print_bots
}

pretty_print_bot_status() {
  python3 - << 'PY'
import json, sys

raw = sys.stdin.read().strip()
if not raw:
    print("No response from API.")
    sys.exit(1)

try:
    b = json.loads(raw)
except json.JSONDecodeError:
    print(raw)
    sys.exit(0)

bid = b.get("id")
name = b.get("name")
status = b.get("status") or b.get("onboarding_stage")
created = b.get("created_at")
has_issues = b.get("has_issues")
highest = b.get("highest_severity")

print(f"Bot: {name} (id: {bid})")
print(f"Status: {status}")
if created:
    print(f"Created: {created}")
print(f"Has issues: {has_issues}")
if highest:
    print(f"Highest severity: {highest}")

issues = b.get("issues") or []
if not issues:
    print("Issues: none")
    sys.exit(0)

print("Issues:")
for i in issues:
    code = i.get("code")
    severity = i.get("severity")
    msg = i.get("message")
    next_steps = i.get("next_steps")
    line = f"- [{severity}] {code}: {msg}"
    if next_steps:
        line += f" | Next: {next_steps}"
    print(line)
PY
}

cmd_bot_status() {
  local ident="$1" key
  key="$(get_api_key)"

  # If ident is not a UUID-like id, you could optionally resolve by name.
  # For now, assume caller passes an id that API accepts.
  curl -sS "$API_BASE/bots/$ident" -H "Authorization: Bearer $key" | pretty_print_bot_status
}

cmd_bot_verify() {
  local ident="$1" key
  key="$(get_api_key)"
  curl -sS -X POST "$API_BASE/bots/$ident/verify" \
    -H "Authorization: Bearer $key" \
    -H "Content-Type: application/json" \
    -d '{}' 
}

pretty_print_bots_health() {
  python3 - << 'PY'
import json, sys

raw = sys.stdin.read().strip()
if not raw:
    print("No response from API.")
    sys.exit(1)

try:
    h = json.loads(raw)
except json.JSONDecodeError:
    print(raw)
    sys.exit(0)

status = h.get("status") or h.get("state")
print(f"Onboarding health: {status}")

for key in ("total_bots", "verified_count", "verification_rate", "pending_count"):
    if key in h:
        print(f"{key}: {h[key]}")
PY
}

cmd_bots_health() {
  curl -sS "$API_BASE/bots/health" | pretty_print_bots_health
}

# --- Usage and dispatch ---

if [ "$#" -lt 1 ]; then
  cat >&2 << 'USAGE'
Usage: agent_republic.sh <command> [args]

Core:
  register <name> <description>
  me
  elections
  run <election_id> <statement>
  vote <election_id> <agent_id_1,agent_id_2,...>
  forum-post <title> <content>

Bots:
  bots
  bot-status <bot_id>
  bot-verify <bot_id>
  bots-health
USAGE
  exit 1
fi

cmd="$1"; shift

case "$cmd" in
  register)
    if [ "$#" -lt 2 ]; then echo "Usage: $0 register <name> <description>" >&2; exit 1; fi
    cmd_register "$1" "$2" ;;
  me)
    cmd_me ;;
  elections)
    cmd_elections ;;
  run)
    if [ "$#" -lt 2 ]; then echo "Usage: $0 run <election_id> <statement>" >&2; exit 1; fi
    cmd_run "$1" "$2" ;;
  vote)
    if [ "$#" -lt 2 ]; then echo "Usage: $0 vote <election_id> <agent_id_1,agent_id_2,...>" >&2; exit 1; fi
    cmd_vote "$1" "$2" ;;
  forum-post)
    if [ "$#" -lt 2 ]; then echo "Usage: $0 forum-post <title> <content>" >&2; exit 1; fi
    export AR_TITLE="$1" AR_CONTENT="$2"
    cmd_forum_post ;;
  bots)
    cmd_bots ;;
  bot-status)
    if [ "$#" -lt 1 ]; then echo "Usage: $0 bot-status <bot_id>" >&2; exit 1; fi
    cmd_bot_status "$1" ;;
  bot-verify)
    if [ "$#" -lt 1 ]; then echo "Usage: $0 bot-verify <bot_id>" >&2; exit 1; fi
    cmd_bot_verify "$1" ;;
  bots-health)
    cmd_bots_health ;;
  *)
    echo "Unknown command: $cmd" >&2; exit 1 ;;
esac
