#!/bin/bash
# ClawSync - Secure Restore Script
# ShellCheck compliant

set -euo pipefail

# === Pre-flight Check ===
REQUIRED_VARS=("BACKUP_REPO" "OPENCLAW_WORKSPACE")
for var in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo "Error: $var is not set. Please configure in .env"
        exit 1
    fi
done

WORKSPACE="${OPENCLAW_WORKSPACE}"
BACKUP_REPO="${BACKUP_REPO}"
BRANCH="${BACKUP_BRANCH:-main}"
TOKEN="${GITHUB_TOKEN:-}"
FORCE="${1:-}"

BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$WORKSPACE"

echo "=== ClawSync Restore ==="

# === Safe Restore: Require --force or confirmation ===
if [[ "$FORCE" != "--force" ]] && [[ "$FORCE" != "-f" ]]; then
    echo "Warning: This will overwrite existing files in $WORKSPACE"
    echo "Are you sure? (y/n)"
    read -r response
    if [[ "$response" != "y" ]] && [[ "$response" != "Y" ]]; then
        echo "Restore cancelled."
        exit 0
    fi
fi

# === Auth & Clone (Secure) ===
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

if gh auth status &>/dev/null; then
    gh auth setup-git 2>/dev/null || true
    gh repo clone "$BACKUP_REPO" "$TEMP_DIR" -- -b "$BRANCH" 2>/dev/null || \
        git clone -b "$BRANCH" "https://github.com/${BACKUP_REPO}.git" "$TEMP_DIR"
else
    if [[ -n "$TOKEN" ]]; then
        # Use credential helper instead of command-line token
        printf "https://%s@github.com" "$TOKEN" | git credential approve
        git clone -b "$BRANCH" "https://github.com/${BACKUP_REPO}.git" "$TEMP_DIR"
        printf "https://%s@github.com" "$TOKEN" | git credential reject
    else
        echo "Error: No GH auth or GITHUB_TOKEN"
        exit 1
    fi
fi

# === Restore Files (no-clobber by default) ===
EXCLUDE_FILES=("SITES.md" "MEMORY.md" ".env" "credentials")

should_restore() {
    local file="$1"
    for excl in "${EXCLUDE_FILES[@]}"; do
        if [[ "$file" == "$excl" ]]; then
            return 1
        fi
    done
    return 0
}

# Restore skills
if [[ -d "$TEMP_DIR/skills" ]]; then
    mkdir -p "$WORKSPACE/skills"
    for item in "$TEMP_DIR/skills"/*; do
        if [[ -d "$item" ]] && should_restore "$(basename "$item")"; then
            cp -rn "$item" "$WORKSPACE/skills/" 2>/dev/null || true
        fi
    done
fi

# Restore scripts
if [[ -d "$TEMP_DIR/scripts" ]]; then
    mkdir -p "$WORKSPACE/scripts"
    for item in "$TEMP_DIR/scripts"/*; do
        if [[ -f "$item" ]] && should_restore "$(basename "$item")"; then
            cp -rn "$item" "$WORKSPACE/scripts/" 2>/dev/null || true
        fi
    done
fi

# Restore identity files (exclude sensitive ones)
for file in AGENTS.md SOUL.md USER.md TOOLS.md IDENTITY.md HEARTBEAT.md; do
    if [[ -f "$TEMP_DIR/$file" ]]; then
        cp -n "$TEMP_DIR/$file" "$WORKSPACE/" 2>/dev/null || true
    fi
done

echo "Restore complete!"
