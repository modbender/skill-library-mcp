#!/usr/bin/env bash
# OpenClaw Auto-Update Checker & Applier
# Usage: check_update.sh [--apply] [--json]

set -euo pipefail

OPENCLAW_REPO="${OPENCLAW_REPO:-/host/openclaw}"
COMPOSE_FILE="${OPENCLAW_REPO}/docker-compose.yml"
JSON_OUTPUT=false
APPLY=false

for arg in "$@"; do
    case "$arg" in
        --json) JSON_OUTPUT=true ;;
        --apply) APPLY=true ;;
        --help|-h)
            echo "Usage: check_update.sh [--apply] [--json]"
            echo "  --apply  Apply update if available"
            echo "  --json   Output as JSON"
            exit 0
            ;;
    esac
done

log() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo "$@"
    fi
}

error_exit() {
    if [ "$JSON_OUTPUT" = true ]; then
        echo "{\"error\": \"$1\"}"
    else
        echo "ERROR: $1" >&2
    fi
    exit 1
}

# Check repo exists
if [ ! -d "$OPENCLAW_REPO/.git" ]; then
    error_exit "OpenClaw repo not found at $OPENCLAW_REPO"
fi

cd "$OPENCLAW_REPO"

# Get current version
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "unknown")

# Fetch latest tags
git fetch --tags --quiet 2>/dev/null || error_exit "Failed to fetch tags"

# Get latest tag (semver sorted)
LATEST_TAG=$(git tag --sort=-v:refname | head -1)

if [ -z "$LATEST_TAG" ]; then
    error_exit "No tags found in repository"
fi

# Compare
if [ "$CURRENT_TAG" = "$LATEST_TAG" ]; then
    UPDATE_AVAILABLE=false
else
    UPDATE_AVAILABLE=true
fi

# Get changes between versions
CHANGES=""
CHANGES_JSON="[]"
if [ "$UPDATE_AVAILABLE" = true ] && [ "$CURRENT_TAG" != "unknown" ]; then
    CHANGES=$(git log --oneline "${CURRENT_TAG}..${LATEST_TAG}" 2>/dev/null || echo "")
    if [ -n "$CHANGES" ]; then
        # Build JSON array of changes
        CHANGES_JSON=$(echo "$CHANGES" | while IFS= read -r line; do
            # Extract just the message (after short hash)
            msg=$(echo "$line" | sed 's/^[a-f0-9]* //')
            printf '%s\n' "$msg"
        done | python3 -c "
import sys, json
lines = [l.strip() for l in sys.stdin if l.strip()]
print(json.dumps(lines))
" 2>/dev/null || echo "[]")
    fi
fi

# Check for changelog
CHANGELOG=""
if [ "$UPDATE_AVAILABLE" = true ]; then
    if [ -f "CHANGELOG.md" ]; then
        # Extract section for latest version
        CHANGELOG=$(sed -n "/^## .*${LATEST_TAG}/,/^## /p" CHANGELOG.md 2>/dev/null | head -30 || echo "")
    fi
fi

# Output results (check only)
if [ "$JSON_OUTPUT" = true ] && [ "$APPLY" = false ]; then
    cat <<EOF
{
  "current": "$CURRENT_TAG",
  "latest": "$LATEST_TAG",
  "update_available": $UPDATE_AVAILABLE,
  "changes": $CHANGES_JSON,
  "applied": false
}
EOF
    exit 0
fi

if [ "$APPLY" = false ]; then
    echo ""
    echo "═══ OpenClaw Update Check ═══"
    echo "Current version: $CURRENT_TAG"
    echo "Latest version:  $LATEST_TAG"
    if [ "$UPDATE_AVAILABLE" = true ]; then
        echo "Status: ⬆️  UPDATE AVAILABLE"
        echo ""
        if [ -n "$CHANGES" ]; then
            echo "Changes ($CURRENT_TAG → $LATEST_TAG):"
            echo "$CHANGES" | while IFS= read -r line; do
                echo "  - $(echo "$line" | sed 's/^[a-f0-9]* //')"
            done
        fi
        if [ -n "$CHANGELOG" ]; then
            echo ""
            echo "Changelog:"
            echo "$CHANGELOG"
        fi
        echo ""
        echo "Run with --apply to update."
    else
        echo "Status: ✅ Up to date"
    fi
    echo "═════════════════════════════"
    exit 0
fi

# Apply update
if [ "$UPDATE_AVAILABLE" = false ]; then
    log "Already up to date ($CURRENT_TAG)."
    if [ "$JSON_OUTPUT" = true ]; then
        echo "{\"current\": \"$CURRENT_TAG\", \"latest\": \"$LATEST_TAG\", \"update_available\": false, \"applied\": false}"
    fi
    exit 0
fi

log "Applying update: $CURRENT_TAG → $LATEST_TAG"
ROLLBACK_TAG="$CURRENT_TAG"

# Step 1: Checkout new tag
log "  [1/4] Checking out $LATEST_TAG..."
git checkout "$LATEST_TAG" 2>/dev/null || error_exit "Failed to checkout $LATEST_TAG"

# Step 2: Install dependencies
log "  [2/4] Installing dependencies..."
if command -v pnpm &>/dev/null; then
    pnpm install --frozen-lockfile 2>/dev/null || pnpm install 2>/dev/null || error_exit "pnpm install failed"
elif command -v npm &>/dev/null; then
    npm ci 2>/dev/null || npm install 2>/dev/null || error_exit "npm install failed"
else
    error_exit "Neither pnpm nor npm found"
fi

# Step 3: Build
log "  [3/4] Building..."
if command -v pnpm &>/dev/null; then
    pnpm build 2>/dev/null || error_exit "Build failed"
else
    npm run build 2>/dev/null || error_exit "Build failed"
fi

# Step 4: Docker rebuild
log "  [4/4] Rebuilding Docker image..."
if command -v docker &>/dev/null; then
    docker build -t openclaw:latest "$OPENCLAW_REPO" 2>/dev/null || error_exit "Docker build failed"
    if [ -f "$COMPOSE_FILE" ]; then
        docker compose -f "$COMPOSE_FILE" up -d 2>/dev/null || error_exit "Docker compose up failed"
    fi
fi

# Verify
sleep 5
HEALTHY=true
if command -v docker &>/dev/null && [ -f "$COMPOSE_FILE" ]; then
    if ! docker compose -f "$COMPOSE_FILE" ps 2>/dev/null | grep -q "Up"; then
        HEALTHY=false
    fi
fi

if [ "$JSON_OUTPUT" = true ]; then
    cat <<EOF
{
  "current": "$ROLLBACK_TAG",
  "latest": "$LATEST_TAG",
  "update_available": true,
  "applied": true,
  "healthy": $HEALTHY,
  "rollback_tag": "$ROLLBACK_TAG",
  "changes": $CHANGES_JSON
}
EOF
else
    echo ""
    echo "═══ Update Applied ═══"
    echo "Updated: $ROLLBACK_TAG → $LATEST_TAG"
    if [ "$HEALTHY" = true ]; then
        echo "Status: ✅ Healthy"
    else
        echo "Status: ⚠️  Health check inconclusive — verify manually"
    fi
    echo ""
    echo "Rollback instructions (if needed):"
    echo "  cd $OPENCLAW_REPO"
    echo "  git checkout $ROLLBACK_TAG"
    echo "  pnpm install && pnpm build"
    echo "  docker build -t openclaw:latest ."
    echo "  docker compose up -d"
    echo "═══════════════════════"
fi
