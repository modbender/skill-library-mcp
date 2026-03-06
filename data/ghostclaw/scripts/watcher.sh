#!/usr/bin/env bash
# Ghostclaw Watcher — cron-based repo monitor

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS_FILE="${GHOSTCLAW_REPOS:-$SCRIPT_DIR/repos.txt}"
GH_TOKEN="${GH_TOKEN:-}"
NOTIFY_CHANNEL="${NOTIFY_CHANNEL:-}"  # e.g. Telegram chat ID

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
}

send_notification() {
    local msg="$1"
    if [[ -n "$NOTIFY_CHANNEL" ]]; then
        openclaw message send --channel telegram --target "$NOTIFY_CHANNEL" --message "$msg" --silent || true
    else
        log "NOTIFY: $msg"
    fi
}

clone_or_pull() {
    local repo_url="$1"
    local dest_dir="$2"

    if [[ -d "$dest_dir/.git" ]]; then
        git -C "$dest_dir" pull --ff-only || return 1
    else
        git clone "$repo_url" "$dest_dir" || return 1
    fi
    return 0
}

analyze_repo() {
    local repo_dir="$1"
    local report
    report="$("$SCRIPT_DIR/ghostclaw.sh" review "$repo_dir" 2>/dev/null || echo '{"vibe_score":0}')"
    echo "$report"
    # Extract vibe score
    echo "$report" | jq -r '.vibe_score // 0'
}

maybe_open_pr() {
    local repo_dir="$1" vibe_score="$2"
    # Only open PR if vibe is low and GH_TOKEN is set
    if (( vibe_score < 60 )) && [[ -n "$GH_TOKEN" ]]; then
        # TODO: actually create patches and open PR
        log "Low vibe ($vibe_score) in $repo_dir — PR would be opened (not implemented)"
    fi
}

main() {
    if [[ ! -f "$REPOS_FILE" ]]; then
        log "Repos file not found: $REPOS_FILE"
        exit 1
    fi

    tmpdir="$(mktemp -d)"
    trap 'rm -rf "$tmpdir"' EXIT

    while IFS= read -r repo_url || [[ -n "$repo_url" ]]; do
        [[ "$repo_url" =~ ^# ]] && continue
        [[ -z "$repo_url" ]] && continue

        repo_name="$(basename "$repo_url" .git)"
        work_dir="$tmpdir/$repo_name"

        log "Processing $repo_url → $work_dir"
        if clone_or_pull "$repo_url" "$work_dir"; then
            score=$(analyze_repo "$work_dir")
            log "Vibe score for $repo_name: $score"

            if (( score < 70 )); then
                send_notification "👻 $repo_name vibe: $score/100 — needs attention"
            fi

            maybe_open_pr "$work_dir" "$score"
        else
            log "Failed to update $repo_url"
        fi
    done < "$REPOS_FILE"

    log "Watcher run complete"
}

main "$@"
