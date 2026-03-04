#!/usr/bin/env bash
set -euo pipefail

NAME=""
TRACKER=""
PROJECT=""
REPO=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --name) NAME="$2"; shift 2 ;;
    --tracker) TRACKER="$2"; shift 2 ;;
    --project) PROJECT="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    *) shift ;;
  esac
done

[ -z "$NAME" ] && { echo "Usage: add-program.sh --name <slug> [--tracker jira|linear] [--project KEY] [--repo owner/repo]"; exit 1; }

BASE_DIR="${TPM_DIR:-$HOME/.openclaw/workspace/tpm}"
PROG_DIR="$BASE_DIR/programs/$NAME"

mkdir -p "$PROG_DIR"/{reports,risks,dependencies}

if [ ! -f "$PROG_DIR/config.json" ]; then
  DISPLAY_NAME=$(echo "$NAME" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2));}1')
  cat > "$PROG_DIR/config.json" << EOF
{
  "name": "$DISPLAY_NAME",
  "slug": "$NAME",
  "tracker": "${TRACKER:-jira}",
  "workstreams": [
    {
      "name": "Main",
      "jira_project": "${PROJECT:-}",
      "jira_board_id": "",
      "linear_team_id": "",
      "github_repos": [$([ -n "$REPO" ] && echo "\"$REPO\"" || echo "")],
      "team_lead": ""
    }
  ],
  "milestones": [],
  "stakeholders": {
    "exec": [],
    "eng": [],
    "full": []
  },
  "settings": {
    "stale_ticket_days": 5,
    "pr_review_threshold_hours": 48,
    "sprint_length_weeks": 2
  }
}
EOF
fi

echo "✅ Program added: $NAME"
echo "   Directory: $PROG_DIR"
echo "   Edit $PROG_DIR/config.json to configure workstreams, repos, and milestones"
