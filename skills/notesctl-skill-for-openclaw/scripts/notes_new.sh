#!/usr/bin/env bash
set -euo pipefail

# Create a new Apple Note with explicit title/body (stable; avoids "New Note" placeholder).
# Usage:
#   notes_new.sh "TITLE" "BODY" [FOLDER]
# Example:
#   notes_new.sh "My title" $'Line1\nLine2' "Notes"

TITLE="${1:-}"
BODY="${2:-}"
FOLDER="${3:-Notes}"

if [[ -z "$TITLE" ]]; then
  echo "ERROR: TITLE is required" >&2
  exit 1
fi

# Notes body is HTML-ish: escape + convert newlines to <br>
export TITLE BODY
BODY_HTML=$(python3 - <<'PY'
import html, os
s = os.environ.get('BODY','')
print(html.escape(s).replace('\n','<br>'))
PY
)

# Escape for AppleScript string literal
export BODY_HTML
BODY_AS=$(python3 - <<'PY'
import os
s=os.environ['BODY_HTML']
print(s.replace('\\','\\\\').replace('"','\\"'))
PY
)

TITLE_AS=$(python3 - <<'PY'
import os
s=os.environ['TITLE']
print(s.replace('\\','\\\\').replace('"','\\"'))
PY
)

osascript -e "tell application \"Notes\" to make new note at folder \"$FOLDER\" with properties {name:\"$TITLE_AS\", body:\"$BODY_AS\"}"