#!/bin/bash
# Inkdrop CLI helper — wraps the local HTTP server API
# Usage: inkdrop.sh <command> [args...]
#
# Environment variables:
#   INKDROP_URL  — Base URL (default: http://localhost:19840)
#   INKDROP_AUTH — user:password for Basic auth (required)

BASE="${INKDROP_URL:-http://localhost:19840}"
AUTH="${INKDROP_AUTH:?Set INKDROP_AUTH=user:password}"

cmd="$1"; shift

case "$cmd" in
  notes)
    curl -s -u "$AUTH" "$BASE/notes?$1"
    ;;
  search)
    curl -s -u "$AUTH" "$BASE/notes?keyword=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$*'))")"
    ;;
  get)
    curl -s -u "$AUTH" "$BASE/$1"
    ;;
  create)
    # args: title bookId [body]
    TITLE="$1"; BOOK="${2:-book:inbox}"; BODY="${3:-}"
    python3 -c "
import json, sys
print(json.dumps({'doctype':'markdown','title':'$TITLE','body':'''$BODY''','bookId':'$BOOK','status':'none','tags':[]}))" | \
    curl -s -u "$AUTH" -X POST "$BASE/notes" -H "Content-Type: application/json" -d @-
    ;;
  update)
    # args: noteId body
    NOTE_ID="$1"; BODY="$2"
    REV=$(curl -s -u "$AUTH" "$BASE/$NOTE_ID" | python3 -c "import sys,json; print(json.load(sys.stdin)['_rev'])")
    NOTE=$(curl -s -u "$AUTH" "$BASE/$NOTE_ID")
    python3 -c "
import json, sys
note = json.loads('''$NOTE''')
note['_rev'] = '$REV'
note['body'] = '''$BODY'''
print(json.dumps(note))" | \
    curl -s -u "$AUTH" -X POST "$BASE/notes" -H "Content-Type: application/json" -d @-
    ;;
  delete)
    curl -s -u "$AUTH" -X DELETE "$BASE/$1"
    ;;
  books)
    curl -s -u "$AUTH" "$BASE/books"
    ;;
  tags)
    curl -s -u "$AUTH" "$BASE/tags"
    ;;
  *)
    echo "Usage: inkdrop.sh <notes|search|get|create|update|delete|books|tags> [args...]"
    echo "Set INKDROP_AUTH=user:password before running."
    exit 1
    ;;
esac
