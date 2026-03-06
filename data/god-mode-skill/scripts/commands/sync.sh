#!/usr/bin/env bash
# god sync - Fetch/update data from repositories
# Usage: god sync [project] [--force]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/../lib"

# Source libraries
source "$LIB_DIR/output.sh"
source "$LIB_DIR/config.sh"
source "$LIB_DIR/db.sh"
source "$LIB_DIR/logging.sh"
source "$LIB_DIR/providers/github.sh"
source "$LIB_DIR/providers/azure.sh"

# Parse arguments
PROJECT_FILTER=""
FORCE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force|-f)
            FORCE=true
            shift
            ;;
        -h|--help)
            cat << 'EOF'
Usage: god sync [project] [options]

Fetch and update data from configured repositories.

Arguments:
  project         Optional: sync only this project (by name or ID)

Options:
  -f, --force     Force full refresh (ignore cache)
  -h, --help      Show this help

Examples:
  god sync                    # Sync all projects
  god sync myproject          # Sync one project
  god sync --force            # Full refresh, all projects
EOF
            exit 0
            ;;
        -*)
            error "Unknown option: $1"
            exit 1
            ;;
        *)
            PROJECT_FILTER="$1"
            shift
            ;;
    esac
done

# Initialize database
db_init

# Get sync settings
SYNC_CONFIG=$(config_get_sync)
INITIAL_DAYS=$(echo "$SYNC_CONFIG" | jq -r '.initialDays // 90')
COMMITS_CACHE_MIN=$(echo "$SYNC_CONFIG" | jq -r '.commitsCacheMinutes // 60')
PRS_CACHE_MIN=$(echo "$SYNC_CONFIG" | jq -r '.prsCacheMinutes // 15')

# Get projects to sync
if [[ -n "$PROJECT_FILTER" ]]; then
    PROJECT=$(config_get_project "$PROJECT_FILTER")
    if [[ -z "$PROJECT" || "$PROJECT" == "null" ]]; then
        error "Project not found: $PROJECT_FILTER"
        exit 1
    fi
    PROJECTS="[$PROJECT]"
else
    PROJECTS=$(config_get_projects)
fi

PROJECT_COUNT=$(echo "$PROJECTS" | jq 'length')

if [[ "$PROJECT_COUNT" -eq 0 ]]; then
    warn "No projects configured."
    info "Add a project with: god projects add github:user/repo"
    exit 0
fi

header "Syncing Projects"

# Log sync command
if [[ -n "$PROJECT_FILTER" ]]; then
    log_command "sync" "$PROJECT_FILTER"
else
    log_command "sync" "all projects"
fi

SYNCED=0
COMMITS_TOTAL=0
PRS_TOTAL=0
ISSUES_TOTAL=0
ERRORS=0

# Sync each project
echo "$PROJECTS" | jq -c '.[]' | while read -r project; do
    PROJECT_ID=$(echo "$project" | jq -r '.id')
    PROJECT_NAME=$(echo "$project" | jq -r '.name // .id')
    PROVIDER=$(config_parse_provider "$PROJECT_ID")
    REPO=$(config_parse_repo "$PROJECT_ID")

    echo -e "${BOLD}${PROJECT_NAME}${RESET}"
    
    # Log sync start
    log_sync_start "$PROJECT_ID"

    # Check provider support
    if [[ "$PROVIDER" != "github" && "$PROVIDER" != "azure" ]]; then
        warn "  Provider '$PROVIDER' not yet supported, skipping"
        continue
    fi

    # Check auth for provider
    if [[ "$PROVIDER" == "github" ]]; then
        AUTH=$(github_check_auth)
        if [[ $(echo "$AUTH" | jq -r '.authenticated') != "true" ]]; then
            error "  Not authenticated to GitHub. Run: gh auth login"
            ((ERRORS++)) || true
            continue
        fi
    elif [[ "$PROVIDER" == "azure" ]]; then
        AUTH=$(azure_check_auth)
        if [[ $(echo "$AUTH" | jq -r '.authenticated') != "true" ]]; then
            error "  Not authenticated to Azure. Run: az login"
            ((ERRORS++)) || true
            continue
        fi
    fi

    # Calculate since date
    SYNC_STATE=$(db_get_sync_state "$PROJECT_ID")
    LAST_COMMITS_SYNC=$(echo "$SYNC_STATE" | jq -r '.commits_synced_at // 0')
    NOW=$(date +%s)

    if [[ "$FORCE" == true ]] || [[ "$LAST_COMMITS_SYNC" == "0" ]] || [[ "$LAST_COMMITS_SYNC" == "null" ]]; then
        # Initial or forced sync - go back N days
        SINCE_DATE=$(date -u -d "@$((NOW - INITIAL_DAYS * 86400))" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
                     date -u -r $((NOW - INITIAL_DAYS * 86400)) +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
                     echo "")
        echo -e "  ${DIM}Full sync (${INITIAL_DAYS} days)${RESET}"
    else
        # Incremental sync - check cache validity
        CACHE_AGE_MIN=$(( (NOW - LAST_COMMITS_SYNC) / 60 ))
        if [[ "$CACHE_AGE_MIN" -lt "$COMMITS_CACHE_MIN" ]]; then
            echo -e "  ${DIM}Cache valid (${CACHE_AGE_MIN}m old), skipping${RESET}"
            echo ""
            continue
        fi
        SINCE_DATE=$(date -u -d "@$LAST_COMMITS_SYNC" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
                     date -u -r "$LAST_COMMITS_SYNC" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
                     echo "")
        echo -e "  ${DIM}Incremental since $(relative_time "$LAST_COMMITS_SYNC")${RESET}"
    fi

    # Ensure project is in database
    PRIORITY=$(echo "$project" | jq -r '.priority // "medium"')
    TAGS=$(echo "$project" | jq -c '.tags // []')
    LOCAL_PATH=$(echo "$project" | jq -r '.local // ""')
    db_upsert_project "$PROJECT_ID" "$PROVIDER" "$PROJECT_NAME" "$PRIORITY" "$TAGS" "$LOCAL_PATH"

    # Fetch commits
    echo -n "  Fetching commits... "
    if [[ "$PROVIDER" == "github" ]]; then
        COMMITS=$(github_fetch_commits "$REPO" "$SINCE_DATE" 2>/dev/null || echo "[]")
    elif [[ "$PROVIDER" == "azure" ]]; then
        COMMITS=$(azure_fetch_commits "$REPO" "$SINCE_DATE" 2>/dev/null || echo "[]")
    else
        COMMITS="[]"
    fi
    COMMIT_COUNT=$(echo "$COMMITS" | jq 'length')
    echo -e "${GREEN}${COMMIT_COUNT}${RESET}"

    if [[ "$COMMIT_COUNT" -gt 0 ]]; then
        echo "$COMMITS" | db_upsert_commits "$PROJECT_ID"
        COMMITS_TOTAL=$((COMMITS_TOTAL + COMMIT_COUNT))
    fi

    # Fetch PRs
    echo -n "  Fetching PRs... "
    if [[ "$PROVIDER" == "github" ]]; then
        PRS=$(github_fetch_prs "$REPO" "all" 2>/dev/null || echo "[]")
    elif [[ "$PROVIDER" == "azure" ]]; then
        PRS=$(azure_fetch_prs "$REPO" "all" 2>/dev/null || echo "[]")
    else
        PRS="[]"
    fi
    PR_COUNT=$(echo "$PRS" | jq 'length')
    OPEN_PRS=$(echo "$PRS" | jq '[.[] | select(.state == "OPEN" or .state == "active")] | length')
    echo -e "${GREEN}${PR_COUNT}${RESET} (${OPEN_PRS} open)"

    # Store PRs
    echo "$PRS" | jq -c '.[]' | while read -r pr; do
        PR_NUM=$(echo "$pr" | jq -r '.number')
        PR_TITLE=$(echo "$pr" | jq -r '.title' | sed "s/'/''/g")
        PR_STATE=$(echo "$pr" | jq -r '.state' | tr '[:upper:]' '[:lower:]')
        PR_AUTHOR=$(echo "$pr" | jq -r '.author // "unknown"')
        PR_CREATED=$(echo "$pr" | jq -r '.created_at')
        PR_UPDATED=$(echo "$pr" | jq -r '.updated_at')
        PR_MERGED=$(echo "$pr" | jq -r '.merged_at // "null"')
        PR_LABELS=$(echo "$pr" | jq -c '.labels // []')
        
        # Convert ISO timestamps to Unix epoch
        if [[ "$PR_CREATED" =~ ^[0-9]{4}- ]]; then
            PR_CREATED=$(date -d "$PR_CREATED" +%s 2>/dev/null || echo "NULL")
        elif [[ "$PR_CREATED" == "null" ]]; then
            PR_CREATED="NULL"
        fi
        
        if [[ "$PR_UPDATED" =~ ^[0-9]{4}- ]]; then
            PR_UPDATED=$(date -d "$PR_UPDATED" +%s 2>/dev/null || echo "NULL")
        elif [[ "$PR_UPDATED" == "null" ]]; then
            PR_UPDATED="NULL"
        fi
        
        if [[ "$PR_MERGED" =~ ^[0-9]{4}- ]]; then
            PR_MERGED=$(date -d "$PR_MERGED" +%s 2>/dev/null || echo "NULL")
        else
            PR_MERGED="NULL"
        fi

        db_exec "INSERT OR REPLACE INTO pull_requests
                 (id, project_id, number, title, state, author, created_at, updated_at, merged_at, labels)
                 VALUES ('${PROJECT_ID}:pr:${PR_NUM}', '$PROJECT_ID', $PR_NUM, '$PR_TITLE',
                         '$PR_STATE', '$PR_AUTHOR', $PR_CREATED, $PR_UPDATED, $PR_MERGED, '$PR_LABELS');"
    done
    PRS_TOTAL=$((PRS_TOTAL + PR_COUNT))

    # Fetch issues
    echo -n "  Fetching issues... "
    if [[ "$PROVIDER" == "github" ]]; then
        ISSUES=$(github_fetch_issues "$REPO" "all" 2>/dev/null || echo "[]")
    elif [[ "$PROVIDER" == "azure" ]]; then
        ISSUES=$(azure_fetch_issues "$REPO" "all" 2>/dev/null || echo "[]")
    else
        ISSUES="[]"
    fi
    ISSUE_COUNT=$(echo "$ISSUES" | jq 'length')
    OPEN_ISSUES=$(echo "$ISSUES" | jq '[.[] | select(.state == "OPEN" or .state == "open")] | length')
    echo -e "${GREEN}${ISSUE_COUNT}${RESET} (${OPEN_ISSUES} open)"

    # Store issues
    echo "$ISSUES" | jq -c '.[]' | while read -r issue; do
        ISSUE_NUM=$(echo "$issue" | jq -r '.number')
        ISSUE_TITLE=$(echo "$issue" | jq -r '.title' | sed "s/'/''/g")
        ISSUE_STATE=$(echo "$issue" | jq -r '.state' | tr '[:upper:]' '[:lower:]')
        ISSUE_AUTHOR=$(echo "$issue" | jq -r '.author // "unknown"')
        ISSUE_ASSIGNEE=$(echo "$issue" | jq -r '.assignee // ""')
        ISSUE_CREATED=$(echo "$issue" | jq -r '.created_at')
        ISSUE_UPDATED=$(echo "$issue" | jq -r '.updated_at')
        ISSUE_LABELS=$(echo "$issue" | jq -c '.labels // []')
        
        # Convert ISO timestamps to Unix epoch
        if [[ "$ISSUE_CREATED" =~ ^[0-9]{4}- ]]; then
            ISSUE_CREATED=$(date -d "$ISSUE_CREATED" +%s 2>/dev/null || echo "NULL")
        elif [[ "$ISSUE_CREATED" == "null" ]]; then
            ISSUE_CREATED="NULL"
        fi
        
        if [[ "$ISSUE_UPDATED" =~ ^[0-9]{4}- ]]; then
            ISSUE_UPDATED=$(date -d "$ISSUE_UPDATED" +%s 2>/dev/null || echo "NULL")
        elif [[ "$ISSUE_UPDATED" == "null" ]]; then
            ISSUE_UPDATED="NULL"
        fi

        db_exec "INSERT OR REPLACE INTO issues
                 (id, project_id, number, title, state, author, assignee, created_at, updated_at, labels)
                 VALUES ('${PROJECT_ID}:issue:${ISSUE_NUM}', '$PROJECT_ID', $ISSUE_NUM, '$ISSUE_TITLE',
                         '$ISSUE_STATE', '$ISSUE_AUTHOR', '$ISSUE_ASSIGNEE', $ISSUE_CREATED, $ISSUE_UPDATED, '$ISSUE_LABELS');"
    done
    ISSUES_TOTAL=$((ISSUES_TOTAL + ISSUE_COUNT))

    # Update sync state
    db_set_sync_state "$PROJECT_ID" "commits_synced_at" "$NOW"
    db_set_sync_state "$PROJECT_ID" "prs_synced_at" "$NOW"
    db_set_sync_state "$PROJECT_ID" "issues_synced_at" "$NOW"
    
    # Log sync complete
    log_sync_complete "$PROJECT_ID" "$COMMIT_COUNT" "$PR_COUNT" "$ISSUE_COUNT"

    ((SYNCED++)) || true
    echo ""
done

# Summary
divider
if [[ "$ERRORS" -gt 0 ]]; then
    warn "Synced with errors"
else
    success "Sync complete"
fi
echo -e "  ${DIM}Projects:${RESET} ${SYNCED}"
echo -e "  ${DIM}Commits:${RESET} ${COMMITS_TOTAL}"
echo -e "  ${DIM}PRs:${RESET} ${PRS_TOTAL}"
echo -e "  ${DIM}Issues:${RESET} ${ISSUES_TOTAL}"
