#!/usr/bin/env bash

# Install or update the baseline social-ops OpenClaw cron jobs.
# Usage:
#   ./scripts/install-cron-jobs.sh
#   ./scripts/install-cron-jobs.sh --base-dir /path/to/skill --tz America/Los_Angeles
#
# This script UPSERTs jobs by name:
# - If a job exists, it is updated via `openclaw cron edit`
# - If it does not exist, it is created via `openclaw cron add`

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_BASE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BASE_DIR="${DEFAULT_BASE_DIR}"
TZ_NAME="America/New_York"
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-dir)
      BASE_DIR="$2"
      shift 2
      ;;
    --tz)
      TZ_NAME="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    -h|--help)
      sed -n '1,20p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if ! command -v openclaw >/dev/null 2>&1; then
  echo "openclaw CLI not found in PATH." >&2
  exit 1
fi

run_cmd() {
  if [[ "${DRY_RUN}" == "true" ]]; then
    echo "+ $*"
  else
    "$@"
  fi
}

get_existing_job_id() {
  local job_name="$1"

  openclaw cron list --all --json 2>/dev/null | python3 - "$job_name" <<'PY'
import json
import sys

needle = sys.argv[1]
raw = sys.stdin.read().strip()
if not raw:
    print("")
    raise SystemExit(0)

try:
    data = json.loads(raw)
except Exception:
    print("")
    raise SystemExit(0)

jobs = []
if isinstance(data, list):
    jobs = data
elif isinstance(data, dict):
    if isinstance(data.get("jobs"), list):
        jobs = data["jobs"]
    elif isinstance(data.get("items"), list):
        jobs = data["items"]

for j in jobs:
    if isinstance(j, dict) and j.get("name") == needle:
        print(j.get("id", ""))
        raise SystemExit(0)

print("")
PY
}

upsert_job() {
  local name="$1"
  local cron_expr="$2"
  local description="$3"
  local message="$4"

  local existing_id
  existing_id="$(get_existing_job_id "$name")"

  if [[ -n "${existing_id}" ]]; then
    echo "Updating existing job: ${name} (${existing_id})"
    run_cmd openclaw cron edit "${existing_id}" \
      --name "${name}" \
      --description "${description}" \
      --cron "${cron_expr}" \
      --tz "${TZ_NAME}" \
      --session isolated \
      --message "${message}" \
      --enable
  else
    echo "Creating new job: ${name}"
    run_cmd openclaw cron add \
      --name "${name}" \
      --description "${description}" \
      --cron "${cron_expr}" \
      --tz "${TZ_NAME}" \
      --session isolated \
      --message "${message}"
  fi
}

poster_msg=$(cat <<EOF
You are executing on a social media plan.

You will use the moltbook skill.

Use social-ops skill now, and figure out what instructions are necessary for your role.

You will adhere to your role, and read the files as instructed.

Run Role: Poster


Constraints:
- Execute Poster scope only.
- Post at most ONE item per run.
- If Todo is empty: clean exit and log.
- No cross-role work.
- No private context leakage.
- Use credentials file auth and complete verification challenge if pending.
EOF
)

responder_msg=$(cat <<EOF
You are executing on a social media plan.

You will use the moltbook skill.
Use social-ops skill now, and figure out what instructions are necessary for your role.

You will adhere to your role, and read the files as instructed.
Run Role: Responder

Constraints:
- Reply/DM hygiene only; meaningful engagement.
- 1-3 sentence replies.
- Max one Scout-sourced insertion.
- If nothing new: quiet pass and log.
- No cross-role work.
- No private context leakage.
- Use credentials file auth and complete verification challenge if pending.
EOF
)

scout_msg=$(cat <<EOF
You are executing on a social media plan.

You will use the moltbook skill.
Use social-ops skill now, and figure out what instructions are necessary for your role.

You will adhere to your role, and read the files as instructed.
Run Role: Scout

Constraints:
- Detect opportunities only (no posting/replying/upvoting).
- Max 3 opportunities per run with routing suggestions.
- Avoid duplicate opportunities.
- No private context leakage.
- Use credentials file auth and complete verification challenge if pending.
EOF
)

content_specialist_msg=$(cat <<EOF
You are executing on a social media plan.

You will use the moltbook skill.
Use social-ops skill now, and figure out what instructions are necessary for your role.

You will adhere to your role, and read the files as instructed.
Run Role: Content Specialist

Constraints:
- Lane clarity + backlog draft generation only.
- No posting, replying, or analytics.
- Keep identity/tone aligned.
- No private context leakage.
EOF
)

researcher_msg=$(cat <<EOF
You are executing on a social media plan.

You will use the moltbook skill.
Use social-ops skill now, and figure out what instructions are necessary for your role.

You will adhere to your role, and read the files as instructed.
Run Role: Researcher

Constraints:
- Complete 1-3 research tasks.
- Add max 0-2 follow-up tasks.
- Evidence-backed guidance only.
- No posting/replying/upvoting/backlog edits.
- Use credentials file auth and complete verification challenge if pending.
EOF
)

analyst_msg=$(cat <<EOF
You are executing on a social media plan.

You will use the moltbook skill.
Use social-ops skill now, and figure out what instructions are necessary for your role.

You will adhere to your role, and read the files as instructed.
Run Role: Analyst

Constraints:
- Weekly pattern analysis only.
- Use logs + done posts + metrics for recommendations.
- No posting/replying/lane edits.
- Avoid overfitting to one-post spikes.
- Use credentials file auth and complete verification challenge if pending.
EOF
)

echo "Installing social-ops baseline cron jobs"
echo "Base dir: ${BASE_DIR}"
echo "Timezone: ${TZ_NAME}"

upsert_job "Moltbook Poster" "0 9,13,17,21 * * *" "Poster role baseline run" "${poster_msg}"
upsert_job "Moltbook Responder" "15 8,11,14,17,20,23 * * *" "Responder role baseline run" "${responder_msg}"
upsert_job "Moltbook Scout" "30 8,19 * * *" "Scout role baseline run" "${scout_msg}"
upsert_job "Moltbook Content Specialist" "0 1 * * *" "Content Specialist role baseline run" "${content_specialist_msg}"
upsert_job "Moltbook Researcher" "0 2 * * 2,5" "Researcher role baseline run" "${researcher_msg}"
upsert_job "Moltbook Analyst" "0 19 * * 0" "Analyst role baseline run" "${analyst_msg}"

echo "Done."
if [[ "${DRY_RUN}" == "true" ]]; then
  echo "(dry-run only; no changes were applied)"
fi
