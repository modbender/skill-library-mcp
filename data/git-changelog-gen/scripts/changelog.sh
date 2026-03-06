#!/opt/homebrew/bin/bash
# git-changelog — Generate a changelog from git commits
# Usage: changelog.sh [options]
#   --since <date>     Start date (default: last tag or 30 days ago)
#   --until <date>     End date (default: now)
#   --format <fmt>     Output format: markdown (default), plain, json
#   --group            Group by conventional commit type (feat/fix/chore/etc)
#   --repo <path>      Repository path (default: current directory)
#   -h, --help         Show help

set -euo pipefail

FORMAT="markdown"
GROUP=false
REPO="."
SINCE=""
UNTIL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --since) SINCE="$2"; shift 2 ;;
    --until) UNTIL="$2"; shift 2 ;;
    --format) FORMAT="$2"; shift 2 ;;
    --group) GROUP=true; shift ;;
    --repo) REPO="$2"; shift 2 ;;
    -h|--help)
      head -8 "$0" | tail -7 | sed 's/^# //'
      exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

cd "$REPO"

if ! git rev-parse --git-dir &>/dev/null; then
  echo "Error: not a git repository" >&2
  exit 1
fi

# Determine --since
if [[ -z "$SINCE" ]]; then
  LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
  if [[ -n "$LAST_TAG" ]]; then
    SINCE="$LAST_TAG"
    RANGE="${LAST_TAG}..HEAD"
  else
    SINCE="$(date -v-30d '+%Y-%m-%d' 2>/dev/null || date -d '30 days ago' '+%Y-%m-%d')"
    RANGE=""
  fi
else
  RANGE=""
fi

# Build git log command
GIT_ARGS=(log --pretty=format:"%H|%h|%s|%an|%ai" --no-merges)
if [[ -n "$RANGE" ]]; then
  GIT_ARGS+=("$RANGE")
else
  GIT_ARGS+=(--since="$SINCE")
fi
[[ -n "$UNTIL" ]] && GIT_ARGS+=(--until="$UNTIL")

COMMITS=$(git "${GIT_ARGS[@]}" 2>/dev/null || echo "")

if [[ -z "$COMMITS" ]]; then
  echo "No commits found."
  exit 0
fi

REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")

# Output based on format
case "$FORMAT" in
  json)
    echo "["
    FIRST=true
    while IFS='|' read -r hash short subject author date; do
      [[ "$FIRST" == "true" ]] && FIRST=false || echo ","
      # Extract type from conventional commit
      TYPE=""
      if [[ "$subject" =~ ^([a-z]+)\(?.*\)?:\ (.+) ]]; then
        TYPE="${BASH_REMATCH[1]}"
      fi
      printf '  {"hash":"%s","short":"%s","subject":"%s","author":"%s","date":"%s","type":"%s"}' \
        "$hash" "$short" "$(echo "$subject" | sed 's/"/\\"/g')" "$author" "${date%% *}" "$TYPE"
    done <<< "$COMMITS"
    echo ""
    echo "]"
    ;;
  plain)
    while IFS='|' read -r hash short subject author date; do
      echo "* ${short} ${subject} (${author}, ${date%% *})"
    done <<< "$COMMITS"
    ;;
  markdown)
    echo "# Changelog — ${REPO_NAME}"
    echo ""
    if [[ -n "${RANGE:-}" ]]; then
      echo "Changes since \`${LAST_TAG}\`:"
    else
      echo "Changes since ${SINCE}:"
    fi
    echo ""

    if [[ "$GROUP" == "true" ]]; then
      # Group by conventional commit type
      declare -A GROUPS
      declare -a ORDER
      while IFS='|' read -r hash short subject author date; do
        TYPE="other"
        if [[ "$subject" =~ ^([a-z]+)(\(.*\))?:\ (.+) ]]; then
          TYPE="${BASH_REMATCH[1]}"
        fi
        GROUPS["$TYPE"]+="- \`${short}\` ${subject} — *${author}* (${date%% *})\n"
        if [[ ! " ${ORDER[*]:-} " =~ " ${TYPE} " ]]; then
          ORDER+=("$TYPE")
        fi
      done <<< "$COMMITS"

      # Nice headers for known types
      declare -A HEADERS=(
        [feat]="✨ Features"
        [fix]="🐛 Bug Fixes"
        [docs]="📝 Documentation"
        [refactor]="♻️ Refactoring"
        [test]="✅ Tests"
        [chore]="🔧 Chores"
        [perf]="⚡ Performance"
        [ci]="🔄 CI/CD"
        [style]="💄 Style"
        [build]="📦 Build"
        [other]="📋 Other"
      )

      for TYPE in "${ORDER[@]}"; do
        HEADER="${HEADERS[$TYPE]:-📋 ${TYPE^}}"
        echo "## ${HEADER}"
        echo ""
        echo -e "${GROUPS[$TYPE]}"
      done
    else
      while IFS='|' read -r hash short subject author date; do
        echo "- \`${short}\` ${subject} — *${author}* (${date%% *})"
      done <<< "$COMMITS"
      echo ""
    fi
    ;;
esac
