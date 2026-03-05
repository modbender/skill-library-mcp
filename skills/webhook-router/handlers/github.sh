#!/bin/bash
#
# GitHub Webhook Handler
# Processes GitHub webhook events and triggers appropriate actions
#

set -euo pipefail

# Arguments
PAYLOAD="$1"
SOURCE="$2"
EVENT_TYPE="${3:-unknown}"

# Configuration
GITHUB_USERNAME="${GITHUB_USERNAME:-}"
ALERT_CHANNEL="${WEBHOOK_ALERT_CHANNEL:-telegram}"
VAULT_SECTION="webhooks/github"

# Ensure jq is available
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required" >&2
    exit 1
fi

# Helper: Send alert via message tool
send_alert() {
    local title="$1"
    local body="$2"
    local priority="${3:-normal}"
    
    # Use OpenClaw's message tool if available
    if command -v message &> /dev/null; then
        message send "$ALERT_CHANNEL" "$title" <<< "$body" 2>/dev/null || true
    fi
    
    # Also log to stdout for capture
    echo "ALERT: $title - $body"
}

# Helper: Write to vault (using obsidian-cli or similar)
write_to_vault() {
    local path="$1"
    local content="$2"
    local tags="$3"
    
    # Try to use vault command if available
    if command -v vault &> /dev/null; then
        vault write "$path" --data "$content" --tags "$tags" 2>/dev/null || true
    fi
}

# Extract common fields
REPO_FULLNAME=$(echo "$PAYLOAD" | jq -r '.repository.full_name // "unknown"')
REPO_NAME=$(echo "$PAYLOAD" | jq -r '.repository.name // "unknown"')
REPO_URL=$(echo "$PAYLOAD" | jq -r '.repository.html_url // ""')
SENDER=$(echo "$PAYLOAD" | jq -r '.sender.login // "unknown"')
SENDER_URL=$(echo "$PAYLOAD" | jq -r '.sender.html_url // ""')

# Generate vault entry timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VAULT_PATH="${VAULT_SECTION}/${REPO_FULLNAME//\//-}/${EVENT_TYPE}"

# Process based on event type
case "$EVENT_TYPE" in
    push)
        REF=$(echo "$PAYLOAD" | jq -r '.ref // "unknown"')
        BRANCH="${REF#refs/heads/}"
        COMMIT_COUNT=$(echo "$PAYLOAD" | jq '.commits | length')
        PUSHER=$(echo "$PAYLOAD" | jq -r '.pusher.name // "unknown"')
        
        # Get commit messages
        COMMIT_MSGS=$(echo "$PAYLOAD" | jq -r '.commits[].message' 2>/dev/null | head -3 | sed 's/^/  - /')
        
        # Log to vault
        VAULT_CONTENT=$(jq -n \
            --arg ts "$TIMESTAMP" \
            --arg repo "$REPO_FULLNAME" \
            --arg branch "$BRANCH" \
            --arg pusher "$PUSHER" \
            --argjson count "$COMMIT_COUNT" \
            --arg commits "$COMMIT_MSGS" \
            '{
                timestamp: $ts,
                event: "push",
                repository: $repo,
                branch: $branch,
                pusher: $pusher,
                commit_count: $count,
                commit_messages: $commits
            }')
        
        write_to_vault "$VAULT_PATH/$TIMESTAMP" "$VAULT_CONTENT" "github,push,${REPO_NAME}"
        
        # Alert on force push or main branch
        FORCED=$(echo "$PAYLOAD" | jq -r '.forced // false')
        if [[ "$FORCED" == "true" ]] || [[ "$BRANCH" == "main" ]] || [[ "$BRANCH" == "master" ]]; then
            send_alert "🔄 Push to $REPO_FULLNAME:$BRANCH" \
                "**$PUSHER** pushed $COMMIT_COUNT commit(s) to \`$BRANCH\`\n\n$COMMIT_MSGS" \
                "${FORCED:+high}"
        fi
        
        echo "Processed push event: $REPO_FULLNAME:$BRANCH ($COMMIT_COUNT commits)"
        ;;
        
    pull_request)
        ACTION=$(echo "$PAYLOAD" | jq -r '.action // "unknown"')
        PR_NUMBER=$(echo "$PAYLOAD" | jq -r '.number // "unknown"')
        PR_TITLE=$(echo "$PAYLOAD" | jq -r '.pull_request.title // "unknown"')
        PR_URL=$(echo "$PAYLOAD" | jq -r '.pull_request.html_url // ""')
        PR_USER=$(echo "$PAYLOAD" | jq -r '.pull_request.user.login // "unknown"')
        PR_STATE=$(echo "$PAYLOAD" | jq -r '.pull_request.state // "unknown"')
        MERGED=$(echo "$PAYLOAD" | jq -r '.pull_request.merged // false')
        BASE_BRANCH=$(echo "$PAYLOAD" | jq -r '.pull_request.base.ref // "unknown"')
        HEAD_BRANCH=$(echo "$PAYLOAD" | jq -r '.pull_request.head.ref // "unknown"')
        
        # Determine if this is important
        IS_IMPORTANT=false
        ALERT_PRIORITY="normal"
        
        # PR merged to main/master
        if [[ "$ACTION" == "closed" && "$MERGED" == "true" ]]; then
            IS_IMPORTANT=true
            ALERT_PRIORITY="high"
            ACTION="merged"
        # PR opened
        elif [[ "$ACTION" == "opened" ]]; then
            IS_IMPORTANT=true
        # Assigned to configured user
        elif [[ "$ACTION" == "assigned" ]]; then
            ASSIGNEE=$(echo "$PAYLOAD" | jq -r '.assignee.login // ""')
            if [[ -n "$GITHUB_USERNAME" && "$ASSIGNEE" == "$GITHUB_USERNAME" ]]; then
                IS_IMPORTANT=true
                ALERT_PRIORITY="high"
            fi
        fi
        
        # Log to vault
        VAULT_CONTENT=$(jq -n \
            --arg ts "$TIMESTAMP" \
            --arg repo "$REPO_FULLNAME" \
            --arg action "$ACTION" \
            --arg number "$PR_NUMBER" \
            --arg title "$PR_TITLE" \
            --arg user "$PR_USER" \
            --arg base "$BASE_BRANCH" \
            --arg head "$HEAD_BRANCH" \
            --argjson merged "$MERGED" \
            '{
                timestamp: $ts,
                event: "pull_request",
                repository: $repo,
                action: $action,
                pr_number: $number,
                pr_title: $title,
                pr_user: $user,
                base_branch: $base,
                head_branch: $head,
                merged: $merged
            }')
        
        write_to_vault "$VAULT_PATH/$TIMESTAMP" "$VAULT_CONTENT" "github,pr,${REPO_NAME}"
        
        # Send alert if important
        if [[ "$IS_IMPORTANT" == "true" ]]; then
            EMOJI="🔀"
            [[ "$ACTION" == "merged" ]] && EMOJI="✅"
            [[ "$ACTION" == "opened" ]] && EMOJI="📥"
            [[ "$ACTION" == "assigned" ]] && EMOJI="👤"
            
            send_alert "$EMOJI PR #$PR_NUMBER $ACTION: $PR_TITLE" \
                "**$PR_USER** $ACTION a pull request in **$REPO_FULLNAME**\n\n" \
                "$EMOJI **#$PR_NUMBER**: $PR_TITLE\n" \
                "\`$HEAD_BRANCH\` → \`$BASE_BRANCH\`\n" \
                "🔗 $PR_URL" \
                "$ALERT_PRIORITY"
        fi
        
        echo "Processed PR event: #$PR_NUMBER $ACTION in $REPO_FULLNAME"
        ;;
        
    issues)
        ACTION=$(echo "$PAYLOAD" | jq -r '.action // "unknown"')
        ISSUE_NUMBER=$(echo "$PAYLOAD" | jq -r '.issue.number // "unknown"')
        ISSUE_TITLE=$(echo "$PAYLOAD" | jq -r '.issue.title // "unknown"')
        ISSUE_URL=$(echo "$PAYLOAD" | jq -r '.issue.html_url // ""')
        ISSUE_USER=$(echo "$PAYLOAD" | jq -r '.issue.user.login // "unknown"')
        ISSUE_STATE=$(echo "$PAYLOAD" | jq -r '.issue.state // "unknown"')
        LABELS=$(echo "$PAYLOAD" | jq -r '.issue.labels[].name // empty' | tr '\n' ', ' | sed 's/, $//')
        
        # Check if assigned to configured user
        IS_ASSIGNED_TO_ME=false
        if [[ -n "$GITHUB_USERNAME" ]]; then
            ASSIGNEES=$(echo "$PAYLOAD" | jq -r '.issue.assignees[].login // empty')
            if echo "$ASSIGNEES" | grep -q "^${GITHUB_USERNAME}$"; then
                IS_ASSIGNED_TO_ME=true
            fi
        fi
        
        # Determine importance
        IS_IMPORTANT=false
        ALERT_PRIORITY="normal"
        
        # Issue assigned to me
        if [[ "$ACTION" == "assigned" && "$IS_ASSIGNED_TO_ME" == "true" ]]; then
            IS_IMPORTANT=true
            ALERT_PRIORITY="high"
        # Issue closed
        elif [[ "$ACTION" == "closed" ]]; then
            IS_IMPORTANT=true
        # Issue opened with certain labels
        elif [[ "$ACTION" == "opened" ]] && [[ "$LABELS" =~ (bug|critical|urgent|security) ]]; then
            IS_IMPORTANT=true
            ALERT_PRIORITY="high"
        fi
        
        # Log to vault
        VAULT_CONTENT=$(jq -n \
            --arg ts "$TIMESTAMP" \
            --arg repo "$REPO_FULLNAME" \
            --arg action "$ACTION" \
            --arg number "$ISSUE_NUMBER" \
            --arg title "$ISSUE_TITLE" \
            --arg user "$ISSUE_USER" \
            --arg labels "$LABELS" \
            --arg state "$ISSUE_STATE" \
            '{
                timestamp: $ts,
                event: "issues",
                repository: $repo,
                action: $action,
                issue_number: $number,
                issue_title: $title,
                issue_user: $user,
                labels: $labels,
                state: $state
            }')
        
        write_to_vault "$VAULT_PATH/$TIMESTAMP" "$VAULT_CONTENT" "github,issue,${REPO_NAME}"
        
        # Send alert if important
        if [[ "$IS_IMPORTANT" == "true" ]]; then
            EMOJI="📝"
            [[ "$ACTION" == "closed" ]] && EMOJI="✅"
            [[ "$ACTION" == "assigned" ]] && EMOJI="👤"
            [[ "$LABELS" =~ (bug|critical) ]] && EMOJI="🐛"
            [[ "$LABELS" =~ security ]] && EMOJI="🔒"
            
            LABELS_STR=""
            [[ -n "$LABELS" ]] && LABELS_STR="\n🏷️ Labels: $LABELS"
            
            send_alert "$EMOJI Issue #$ISSUE_NUMBER $ACTION: $ISSUE_TITLE" \
                "**$ISSUE_USER** $ACTION an issue in **$REPO_FULLNAME**$LABELS_STR\n\n" \
                "$EMOJI **#$ISSUE_NUMBER**: $ISSUE_TITLE\n" \
                "🔗 $ISSUE_URL" \
                "$ALERT_PRIORITY"
        fi
        
        echo "Processed issue event: #$ISSUE_NUMBER $ACTION in $REPO_FULLNAME"
        ;;
        
    release)
        ACTION=$(echo "$PAYLOAD" | jq -r '.action // "unknown"')
        
        if [[ "$ACTION" == "published" ]]; then
            RELEASE_TAG=$(echo "$PAYLOAD" | jq -r '.release.tag_name // "unknown"')
            RELEASE_NAME=$(echo "$PAYLOAD" | jq -r '.release.name // "unknown"')
            RELEASE_URL=$(echo "$PAYLOAD" | jq -r '.release.html_url // ""')
            RELEASE_BODY=$(echo "$PAYLOAD" | jq -r '.release.body // ""' | head -c 500)
            IS_PRERELEASE=$(echo "$PAYLOAD" | jq -r '.release.prerelease // false')
            
            EMOJI="🚀"
            [[ "$IS_PRERELEASE" == "true" ]] && EMOJI="⚗️"
            
            # Log to vault
            VAULT_CONTENT=$(jq -n \
                --arg ts "$TIMESTAMP" \
                --arg repo "$REPO_FULLNAME" \
                --arg tag "$RELEASE_TAG" \
                --arg name "$RELEASE_NAME" \
                --argjson prerelease "$IS_PRERELEASE" \
                '{
                    timestamp: $ts,
                    event: "release",
                    repository: $repo,
                    tag: $tag,
                    name: $name,
                    prerelease: $prerelease
                }')
            
            write_to_vault "$VAULT_PATH/$TIMESTAMP" "$VAULT_CONTENT" "github,release,${REPO_NAME}"
            
            # Always alert on releases
            PRERELEASE_STR=""
            [[ "$IS_PRERELEASE" == "true" ]] && PRERELEASE_STR=" (pre-release)"
            
            send_alert "$EMOJI Release $RELEASE_TAG$PRERELEASE_STR: $REPO_FULLNAME" \
                "New release published in **$REPO_FULLNAME**\n\n" \
                "$EMOJI **$RELEASE_TAG**: $RELEASE_NAME$PRERELEASE_STR\n" \
                "🔗 $RELEASE_URL" \
                "normal"
            
            echo "Processed release event: $RELEASE_TAG in $REPO_FULLNAME"
        fi
        ;;
        
    ping)
        # GitHub webhook test ping
        ZEN=$(echo "$PAYLOAD" | jq -r '.zen // "Keep it logically awesome."')
        HOOK_ID=$(echo "$PAYLOAD" | jq -r '.hook_id // "unknown"')
        
        echo "Received ping from GitHub (hook: $HOOK_ID): $ZEN"
        ;;
        
    *)
        # Unknown event type - log generically
        VAULT_CONTENT=$(jq -n \
            --arg ts "$TIMESTAMP" \
            --arg repo "$REPO_FULLNAME" \
            --arg event "$EVENT_TYPE" \
            --arg sender "$SENDER" \
            '{
                timestamp: $ts,
                event: $event,
                repository: $repo,
                sender: $sender,
                note: "Unhandled event type"
            }')
        
        write_to_vault "$VAULT_PATH/$TIMESTAMP" "$VAULT_CONTENT" "github,unhandled,${REPO_NAME}"
        
        echo "Received unhandled event: $EVENT_TYPE from $REPO_FULLNAME"
        ;;
esac

exit 0
