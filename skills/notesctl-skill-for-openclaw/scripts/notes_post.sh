#!/usr/bin/env bash
set -euo pipefail

# Read a JSON payload from stdin and create a new Apple Note.
# JSON schema:
#   {"title":"...","body":"...","folder":"Notes"}
# Usage:
#   echo '{"title":"T","body":"Line1\nLine2","folder":"Notes"}' | scripts/notes_post.sh

payload="$(cat)"

export NOTES_PAYLOAD="$payload"

# Extract fields (title required)
TITLE=$(python3 - <<'PY'
import json, os
obj=json.loads(os.environ.get('NOTES_PAYLOAD','') or '{}')
print(obj.get('title',''))
PY
)

if [[ -z "$TITLE" ]]; then
  echo "ERROR: title is required in JSON stdin" >&2
  exit 1
fi

BODY=$(python3 - <<'PY'
import json, os
obj=json.loads(os.environ.get('NOTES_PAYLOAD','') or '{}')
print(obj.get('body',''))
PY
)

FOLDER=$(python3 - <<'PY'
import json, os
obj=json.loads(os.environ.get('NOTES_PAYLOAD','') or '{}')
print(obj.get('folder','Notes'))
PY
)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/notes_new.sh" "$TITLE" "$BODY" "$FOLDER" >/dev/null

echo "OK: wrote note -> $FOLDER / $TITLE"