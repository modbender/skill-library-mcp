#!/usr/bin/env bash
# collect-logs.sh: example action script
TASK_JSON="$1"
WORKDIR="/var/lib/openclaw/artifacts"
mkdir -p "$WORKDIR"
TASK_ID=$(echo "$TASK_JSON" | /usr/bin/jq -r '.task_id')
OUT="$WORKDIR/${TASK_ID}-logs.txt"
echo "Collected logs for task $TASK_ID" > "$OUT"
exit 0
