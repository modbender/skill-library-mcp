#!/usr/bin/env bash
# coda.sh — Coda API helper for common operations
# Usage: bash coda.sh <command> [args...]
#
# Requires: CODA_API_TOKEN environment variable
# Base URL: https://coda.io/apis/v1

set -euo pipefail

BASE="https://coda.io/apis/v1"

if [[ -z "${CODA_API_TOKEN:-}" ]]; then
  echo "Error: CODA_API_TOKEN not set." >&2
  echo "Get your token at: https://coda.io/account → API settings" >&2
  exit 1
fi

AUTH="Authorization: Bearer ${CODA_API_TOKEN}"

_get()  { curl -sf -H "$AUTH" "$@"; }
_post() { curl -sf -H "$AUTH" -H "Content-Type: application/json" -X POST "$@"; }
_put()  { curl -sf -H "$AUTH" -H "Content-Type: application/json" -X PUT "$@"; }
_patch(){ curl -sf -H "$AUTH" -H "Content-Type: application/json" -X PATCH "$@"; }
_del()  { curl -sf -H "$AUTH" -X DELETE "$@"; }

cmd="${1:-help}"
shift || true

case "$cmd" in

  # ── Account ──
  whoami)
    _get "$BASE/whoami"
    ;;

  # ── Docs ──
  list-docs)
    _get "$BASE/docs?limit=${1:-25}"
    ;;

  get-doc)
    [[ -z "${1:-}" ]] && { echo "Usage: coda.sh get-doc <docId>" >&2; exit 1; }
    _get "$BASE/docs/$1"
    ;;

  create-doc)
    [[ -z "${1:-}" ]] && { echo "Usage: coda.sh create-doc <title> [folderId]" >&2; exit 1; }
    body="{\"title\":\"$1\"}"
    [[ -n "${2:-}" ]] && body="{\"title\":\"$1\",\"folderId\":\"$2\"}"
    _post -d "$body" "$BASE/docs"
    ;;

  delete-doc)
    [[ -z "${1:-}" ]] && { echo "Usage: coda.sh delete-doc <docId>" >&2; exit 1; }
    _del "$BASE/docs/$1"
    ;;

  # ── Pages ──
  list-pages)
    [[ -z "${1:-}" ]] && { echo "Usage: coda.sh list-pages <docId>" >&2; exit 1; }
    _get "$BASE/docs/$1/pages"
    ;;

  get-page)
    [[ -z "${2:-}" ]] && { echo "Usage: coda.sh get-page <docId> <pageId>" >&2; exit 1; }
    _get "$BASE/docs/$1/pages/$2"
    ;;

  # ── Tables ──
  list-tables)
    [[ -z "${1:-}" ]] && { echo "Usage: coda.sh list-tables <docId>" >&2; exit 1; }
    _get "$BASE/docs/$1/tables"
    ;;

  # ── Columns ──
  list-columns)
    [[ -z "${2:-}" ]] && { echo "Usage: coda.sh list-columns <docId> <tableId>" >&2; exit 1; }
    _get "$BASE/docs/$1/tables/$2/columns"
    ;;

  # ── Rows ──
  list-rows)
    [[ -z "${2:-}" ]] && { echo "Usage: coda.sh list-rows <docId> <tableId> [limit] [useColumnNames]" >&2; exit 1; }
    params="limit=${3:-25}"
    [[ "${4:-}" == "true" ]] && params="$params&useColumnNames=true"
    _get "$BASE/docs/$1/tables/$2/rows?$params"
    ;;

  get-row)
    [[ -z "${3:-}" ]] && { echo "Usage: coda.sh get-row <docId> <tableId> <rowId>" >&2; exit 1; }
    _get "$BASE/docs/$1/tables/$2/rows/$3?useColumnNames=true"
    ;;

  insert-rows)
    # Reads JSON body from stdin
    [[ -z "${2:-}" ]] && { echo "Usage: echo '{\"rows\":[...]}' | coda.sh insert-rows <docId> <tableId>" >&2; exit 1; }
    _post -d @- "$BASE/docs/$1/tables/$2/rows"
    ;;

  upsert-rows)
    # Reads JSON body from stdin (must include keyColumns)
    [[ -z "${2:-}" ]] && { echo "Usage: echo '{\"rows\":[...],\"keyColumns\":[...]}' | coda.sh upsert-rows <docId> <tableId>" >&2; exit 1; }
    _post -d @- "$BASE/docs/$1/tables/$2/rows"
    ;;

  update-row)
    # Reads JSON body from stdin
    [[ -z "${3:-}" ]] && { echo "Usage: echo '{\"row\":{\"cells\":[...]}}' | coda.sh update-row <docId> <tableId> <rowId>" >&2; exit 1; }
    _put -d @- "$BASE/docs/$1/tables/$2/rows/$3"
    ;;

  delete-row)
    [[ -z "${3:-}" ]] && { echo "Usage: coda.sh delete-row <docId> <tableId> <rowId>" >&2; exit 1; }
    _del "$BASE/docs/$1/tables/$2/rows/$3"
    ;;

  delete-rows)
    # Reads JSON body from stdin: {"rowIds":["i-...","i-..."]}
    [[ -z "${2:-}" ]] && { echo "Usage: echo '{\"rowIds\":[...]}' | coda.sh delete-rows <docId> <tableId>" >&2; exit 1; }
    _del -d @- "$BASE/docs/$1/tables/$2/rows" -H "Content-Type: application/json"
    ;;

  # ── Formulas ──
  list-formulas)
    [[ -z "${1:-}" ]] && { echo "Usage: coda.sh list-formulas <docId>" >&2; exit 1; }
    _get "$BASE/docs/$1/formulas"
    ;;

  # ── Controls ──
  list-controls)
    [[ -z "${1:-}" ]] && { echo "Usage: coda.sh list-controls <docId>" >&2; exit 1; }
    _get "$BASE/docs/$1/controls"
    ;;

  # ── Mutation Status ──
  mutation-status)
    [[ -z "${1:-}" ]] && { echo "Usage: coda.sh mutation-status <requestId>" >&2; exit 1; }
    _get "$BASE/mutationStatus/$1"
    ;;

  # ── Folders ──
  list-folders)
    _get "$BASE/folders?limit=${1:-25}"
    ;;

  create-folder)
    [[ -z "${2:-}" ]] && { echo "Usage: coda.sh create-folder <name> <workspaceId>" >&2; exit 1; }
    _post -d "{\"name\":\"$1\",\"workspaceId\":\"$2\"}" "$BASE/folders"
    ;;

  # ── Permissions ──
  share-doc)
    [[ -z "${3:-}" ]] && { echo "Usage: coda.sh share-doc <docId> <email> <access:readonly|write|comment>" >&2; exit 1; }
    _post -d "{\"access\":\"$3\",\"principal\":{\"type\":\"email\",\"email\":\"$2\"}}" "$BASE/docs/$1/acl/permissions"
    ;;

  # ── Automations ──
  trigger-automation)
    [[ -z "${2:-}" ]] && { echo "Usage: coda.sh trigger-automation <docId> <ruleId> [payloadJson]" >&2; exit 1; }
    body="${3:-{}}"
    _post -d "$body" "$BASE/docs/$1/hooks/automation/$2"
    ;;

  help|*)
    cat <<EOF
Coda API Helper — Usage: coda.sh <command> [args...]

Account:
  whoami                                    Get current user info

Docs:
  list-docs [limit]                         List accessible docs
  get-doc <docId>                           Get doc metadata
  create-doc <title> [folderId]             Create new doc
  delete-doc <docId>                        Delete doc

Pages:
  list-pages <docId>                        List pages in doc
  get-page <docId> <pageId>                 Get page details

Tables:
  list-tables <docId>                       List tables/views

Columns:
  list-columns <docId> <tableId>            List columns

Rows:
  list-rows <docId> <tableId> [limit] [useColumnNames]
  get-row <docId> <tableId> <rowId>
  insert-rows <docId> <tableId>             (reads JSON from stdin)
  upsert-rows <docId> <tableId>             (reads JSON from stdin)
  update-row <docId> <tableId> <rowId>      (reads JSON from stdin)
  delete-row <docId> <tableId> <rowId>
  delete-rows <docId> <tableId>             (reads JSON from stdin)

Formulas & Controls:
  list-formulas <docId>
  list-controls <docId>

Folders:
  list-folders [limit]
  create-folder <name> <workspaceId>

Permissions:
  share-doc <docId> <email> <access>

Automations:
  trigger-automation <docId> <ruleId> [payloadJson]

Misc:
  mutation-status <requestId>

Env: CODA_API_TOKEN (required) — get at https://coda.io/account
EOF
    ;;
esac
