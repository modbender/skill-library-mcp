#!/usr/bin/env bash
# greptile.sh — Thin wrapper around the Greptile REST API
# Requires: GREPTILE_TOKEN, GITHUB_TOKEN (or GREPTILE_GITHUB_TOKEN)
#
# Usage:
#   greptile.sh index   <owner/repo> [branch] [--remote github|gitlab] [--reload] [--no-notify]
#   greptile.sh status  <owner/repo> [branch] [--remote github|gitlab]
#   greptile.sh query   <owner/repo> [branch] "<question>" [--genius] [--stream] [--remote github|gitlab]
#   greptile.sh search  <owner/repo> [branch] "<query>" [--stream] [--remote github|gitlab]

set -eo pipefail

API="https://api.greptile.com/v2"
TOKEN="${GREPTILE_TOKEN:?Set GREPTILE_TOKEN}"
GH_TOKEN="${GREPTILE_GITHUB_TOKEN:-${GITHUB_TOKEN:-}}"

if [[ -z "$GH_TOKEN" ]]; then
  # Try gh CLI token
  GH_TOKEN="$(gh auth token 2>/dev/null || true)"
  if [[ -z "$GH_TOKEN" ]]; then
    echo "Error: Set GITHUB_TOKEN, GREPTILE_GITHUB_TOKEN, or authenticate with gh CLI" >&2
    exit 1
  fi
fi

cmd="${1:?Usage: greptile.sh <index|status|query|search> ...}"
shift

# Defaults
REMOTE="github"
RELOAD="true"
NOTIFY="true"
GENIUS="false"
STREAM="false"

parse_repo_branch() {
  REPO="${1:?repo required (owner/repo)}"
  shift
  # If next arg exists and doesn't start with --, treat as branch
  if [[ $# -gt 0 && "${1:0:2}" != "--" && "$1" != "" ]]; then
    BRANCH="$1"
    shift
  else
    BRANCH="main"
  fi
  REMAINING_ARGS=("$@")
}

parse_flags() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --remote) REMOTE="$2"; shift 2 ;;
      --reload) RELOAD="true"; shift ;;
      --no-reload) RELOAD="false"; shift ;;
      --no-notify) NOTIFY="false"; shift ;;
      --genius) GENIUS="true"; shift ;;
      --stream) STREAM="true"; shift ;;
      *) shift ;;
    esac
  done
}

case "$cmd" in
  index)
    parse_repo_branch "$@"
    parse_flags "${REMAINING_ARGS[@]}"
    curl -sf -X POST "$API/repositories" \
      -H "Authorization: Bearer $TOKEN" \
      -H "X-GitHub-Token: $GH_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$(jq -n \
        --arg remote "$REMOTE" \
        --arg repo "$REPO" \
        --arg branch "$BRANCH" \
        --argjson reload "$RELOAD" \
        --argjson notify "$NOTIFY" \
        '{remote: $remote, repository: $repo, branch: $branch, reload: $reload, notify: $notify}'
      )"
    ;;

  status)
    parse_repo_branch "$@"
    parse_flags "${REMAINING_ARGS[@]}"
    REPO_ID=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${REMOTE}:${BRANCH}:${REPO}', safe=''))")
    curl -sf "$API/repositories/$REPO_ID" \
      -H "Authorization: Bearer $TOKEN" \
      -H "X-GitHub-Token: $GH_TOKEN"
    ;;

  query)
    parse_repo_branch "$@"
    set -- "${REMAINING_ARGS[@]}"
    # Next non-flag arg is the question
    QUESTION=""
    NEW_ARGS=()
    for arg in "$@"; do
      if [[ -z "$QUESTION" && "${arg:0:2}" != "--" ]]; then
        QUESTION="$arg"
      else
        NEW_ARGS+=("$arg")
      fi
    done
    parse_flags "${NEW_ARGS[@]}"
    [[ -z "$QUESTION" ]] && { echo "Error: question required" >&2; exit 1; }

    curl -sf -X POST "$API/query" \
      -H "Authorization: Bearer $TOKEN" \
      -H "X-GitHub-Token: $GH_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$(jq -n \
        --arg q "$QUESTION" \
        --arg remote "$REMOTE" \
        --arg repo "$REPO" \
        --arg branch "$BRANCH" \
        --argjson genius "$GENIUS" \
        --argjson stream "$STREAM" \
        '{
          messages: [{id: "1", content: $q, role: "user"}],
          repositories: [{remote: $remote, repository: $repo, branch: $branch}],
          genius: $genius,
          stream: $stream
        }'
      )"
    ;;

  search)
    parse_repo_branch "$@"
    set -- "${REMAINING_ARGS[@]}"
    QUERY=""
    NEW_ARGS=()
    for arg in "$@"; do
      if [[ -z "$QUERY" && "${arg:0:2}" != "--" ]]; then
        QUERY="$arg"
      else
        NEW_ARGS+=("$arg")
      fi
    done
    parse_flags "${NEW_ARGS[@]}"
    [[ -z "$QUERY" ]] && { echo "Error: query required" >&2; exit 1; }

    curl -sf -X POST "$API/search" \
      -H "Authorization: Bearer $TOKEN" \
      -H "X-GitHub-Token: $GH_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$(jq -n \
        --arg q "$QUERY" \
        --arg remote "$REMOTE" \
        --arg repo "$REPO" \
        --arg branch "$BRANCH" \
        --argjson stream "$STREAM" \
        '{
          query: $q,
          repositories: [{remote: $remote, repository: $repo, branch: $branch}],
          stream: $stream
        }'
      )"
    ;;

  *)
    echo "Unknown command: $cmd" >&2
    echo "Usage: greptile.sh <index|status|query|search> ..." >&2
    exit 1
    ;;
esac
