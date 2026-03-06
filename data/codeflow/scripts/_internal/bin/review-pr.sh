#!/bin/bash
# review-pr.sh — Checkout a PR and run a coding agent review, streamed via Codeflow
#
# Usage: ./review-pr.sh [options] <PR_URL>
#
# Options:
#   -a <agent>   Agent command: claude (default), codex
#   -p <prompt>  Custom review prompt (default: standard code review)
#   -c           Post review as gh pr comment after completion
#   -w <dir>     Working directory (default: temp clone)
#   -t <sec>     Timeout for agent (default: 1800)
#   -P <platform> Platform: auto (default), discord, or telegram
#   --thread     Post into Discord thread
#   --tg-chat <id> Telegram chat id (when -P telegram)
#   --tg-thread <id> Telegram message_thread_id (optional)
#   --skip-reads Hide Read tool events
#
# Requires: gh CLI (authenticated), git

set -euo pipefail

AGENT="claude"
CUSTOM_PROMPT=""
POST_COMMENT=false
WORKDIR=""
TIMEOUT=1800
THREAD_MODE=false
SKIP_READS=false
PLATFORM="${CODEFLOW_DEFAULT_PLATFORM:-${CODEFLOW_PLATFORM:-auto}}"
TG_CHAT_ID=""
TG_THREAD_ID=""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PY_DIR="$(cd "$SCRIPT_DIR/../py" && pwd)"

source "$SCRIPT_DIR/lib.sh"
codeflow_init_default_paths "$ROOT_DIR"
CODEFLOW_SCRIPT_DIR="$PY_DIR"
codeflow_require_python310

STATE_FILE="${CODEFLOW_STATE_FILE:-$CODEFLOW_STATE_FILE_DEFAULT}"
STATE_FILE_READ="$STATE_FILE"

state_get() {
  local key="$1"
  codeflow_state_get "$STATE_FILE_READ" "$key"
}

# Parse options
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --thread)      THREAD_MODE=true; shift ;;
    --skip-reads)  SKIP_READS=true; shift ;;
    --tg-chat)     TG_CHAT_ID="$2"; shift 2 ;;
    --tg-thread)   TG_THREAD_ID="$2"; shift 2 ;;
    -a) AGENT="$2"; shift 2 ;;
    -p) CUSTOM_PROMPT="$2"; shift 2 ;;
    -c) POST_COMMENT=true; shift ;;
    -w) WORKDIR="$2"; shift 2 ;;
    -t) TIMEOUT="$2"; shift 2 ;;
    -P) PLATFORM="$2"; shift 2 ;;
    -*) echo "Unknown option: $1" >&2; exit 1 ;;
    *)  ARGS+=("$1"); shift ;;
  esac
done

PR_URL="${ARGS[0]:-}"
[ -z "$PR_URL" ] && { echo "Usage: review-pr.sh [options] <PR_URL>" >&2; exit 1; }

# Validate gh CLI
command -v gh &>/dev/null || { echo "❌ Error: 'gh' CLI not found" >&2; exit 1; }
command -v git &>/dev/null || { echo "❌ Error: 'git' not found" >&2; exit 1; }

# Parse PR URL → owner/repo and PR number
# Supports: https://github.com/owner/repo/pull/123 or owner/repo#123
if [[ "$PR_URL" =~ github\.com/([^/]+/[^/]+)/pull/([0-9]+) ]]; then
  REPO="${BASH_REMATCH[1]}"
  PR_NUM="${BASH_REMATCH[2]}"
elif [[ "$PR_URL" =~ ^([^/]+/[^#]+)#([0-9]+)$ ]]; then
  REPO="${BASH_REMATCH[1]}"
  PR_NUM="${BASH_REMATCH[2]}"
else
  echo "❌ Error: Cannot parse PR URL: $PR_URL" >&2
  echo "  Expected: https://github.com/owner/repo/pull/123 or owner/repo#123" >&2
  exit 1
fi

echo "📋 Reviewing PR #${PR_NUM} on ${REPO}"

# Fetch PR metadata
if ! PR_JSON="$(gh pr view "$PR_NUM" --repo "$REPO" --json title,body,headRefName,baseRefName,files,additions,deletions 2>/dev/null)"; then
  echo "❌ Error: Failed to fetch PR metadata — check gh auth and repo access" >&2
  exit 1
fi
if [ -z "$PR_JSON" ]; then
  echo "❌ Error: Failed to fetch PR metadata — check gh auth and repo access" >&2
  exit 1
fi

PR_TITLE=$(echo "$PR_JSON" | python3 -c "import json,sys;print(json.load(sys.stdin).get('title',''))")
PR_BRANCH=$(echo "$PR_JSON" | python3 -c "import json,sys;print(json.load(sys.stdin).get('headRefName',''))")
PR_BASE=$(echo "$PR_JSON" | python3 -c "import json,sys;print(json.load(sys.stdin).get('baseRefName','main'))")
PR_BODY=$(echo "$PR_JSON" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('body','')[:500])")
PR_ADDITIONS=$(echo "$PR_JSON" | python3 -c "import json,sys;print(json.load(sys.stdin).get('additions',0))")
PR_DELETIONS=$(echo "$PR_JSON" | python3 -c "import json,sys;print(json.load(sys.stdin).get('deletions',0))")

echo "  Title: $PR_TITLE"
echo "  Branch: $PR_BRANCH → $PR_BASE"
echo "  Changes: +${PR_ADDITIONS} -${PR_DELETIONS}"

# Clone or use worktree
CLEANUP_CLONE=false
if [ -z "$WORKDIR" ]; then
  WORKDIR=$(mktemp -d /tmp/pr-review.XXXXXX)
  CLEANUP_CLONE=true
  echo "📂 Cloning to $WORKDIR..."
  if ! gh repo clone "$REPO" "$WORKDIR" -- --depth=50 -b "$PR_BRANCH" 2>/dev/null; then
    echo "❌ Error: Failed to clone repo" >&2
    rm -rf "$WORKDIR"
    exit 1
  fi
else
  echo "📂 Using working directory: $WORKDIR"
  cd "$WORKDIR"
  git fetch origin "$PR_BRANCH" 2>/dev/null
  git checkout "$PR_BRANCH" 2>/dev/null || { echo "❌ Error: Cannot checkout $PR_BRANCH" >&2; exit 1; }
fi

# Build review prompt
if [ -n "$CUSTOM_PROMPT" ]; then
  REVIEW_PROMPT="$CUSTOM_PROMPT"
else
  REVIEW_PROMPT="Review this pull request thoroughly.

PR #${PR_NUM}: ${PR_TITLE}
Branch: ${PR_BRANCH} → ${PR_BASE}
Changes: +${PR_ADDITIONS} -${PR_DELETIONS}

${PR_BODY:+Description: ${PR_BODY}}

Review guidelines:
1. Check for bugs, logic errors, and edge cases
2. Review code style and consistency
3. Look for security vulnerabilities
4. Check test coverage
5. Evaluate naming and documentation
6. Note any performance concerns

Read the changed files, understand the context, and provide a structured review with:
- Summary of changes
- Issues found (critical, major, minor)
- Suggestions for improvement
- Overall assessment (approve, request changes, or comment)

Write your final review to /tmp/pr-review-${PR_NUM}.md

When completely finished, run: openclaw system event --text 'Done: PR #${PR_NUM} review complete' --mode now"
fi

# Build agent command
REVIEW_OUTPUT="/tmp/pr-review-${PR_NUM}.md"
AGENT_ARGS=()
case "$AGENT" in
  claude*)
    AGENT_ARGS=(claude -p --dangerously-skip-permissions --output-format stream-json --verbose "$REVIEW_PROMPT")
    ;;
  codex*)
    AGENT_ARGS=(codex exec --json --full-auto "$REVIEW_PROMPT")
    ;;
  *)
    read -r -a AGENT_WORDS <<< "$AGENT"
    AGENT_ARGS=("${AGENT_WORDS[@]}" "$REVIEW_PROMPT")
    ;;
esac

echo "🚀 Starting review with ${AGENT}..."

PLATFORM="$(codeflow_infer_platform "$ROOT_DIR" "$PLATFORM" "$STATE_FILE_READ" "$TG_CHAT_ID" "$TG_THREAD_ID")"

# Build relay flags
RELAY_ARGS=(-w "$WORKDIR" -t "$TIMEOUT" -P "$PLATFORM" -n "${AGENT} Review")
[ "$THREAD_MODE" = true ] && RELAY_ARGS+=(--thread)
[ "$SKIP_READS" = true ] && RELAY_ARGS+=(--skip-reads)
[ -n "$TG_CHAT_ID" ] && RELAY_ARGS+=(--tg-chat "$TG_CHAT_ID")
[ -n "$TG_THREAD_ID" ] && RELAY_ARGS+=(--tg-thread "$TG_THREAD_ID")

# Run through dev-relay.sh
bash "$SCRIPT_DIR/dev-relay.sh" "${RELAY_ARGS[@]}" -- "${AGENT_ARGS[@]}"

# Post review as gh pr comment if requested
if [ "$POST_COMMENT" = true ] && [ -f "$REVIEW_OUTPUT" ]; then
  echo "💬 Posting review comment to PR #${PR_NUM}..."
  REVIEW_CONTENT=$(cat "$REVIEW_OUTPUT")
  if [ -n "$REVIEW_CONTENT" ]; then
    if gh pr comment "$PR_NUM" --repo "$REPO" --body "## Automated Code Review

${REVIEW_CONTENT}

---
*Generated by Codeflow review mode*" 2>/dev/null
    then
      echo "✅ Review posted to PR #${PR_NUM}"
    else
      echo "⚠️  Failed to post review comment (check gh auth)" >&2
    fi
  else
    echo "⚠️  Review file is empty — skipping comment" >&2
  fi
elif [ "$POST_COMMENT" = true ]; then
  echo "⚠️  Review file not found at $REVIEW_OUTPUT — agent may not have written it" >&2
fi

# Cleanup temp clone
if [ "$CLEANUP_CLONE" = true ]; then
  rm -rf "$WORKDIR"
fi

echo "Done."
