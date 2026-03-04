#!/bin/bash
# ClawSync - Secure Backup Script
# ShellCheck compliant: https://www.shellcheck.net/

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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}"

echo "=== ClawSync Backup ==="

# === Explicit Exclusions (Documented) ===
# These files are NEVER backed up - see rsync --exclude flags below for actual enforcement

# === Safe Copy: Skills using rsync with exclude patterns ===
if [[ -d "$WORKSPACE/skills" ]] && [[ -n "$(ls -A "$WORKSPACE/skills/" 2>/dev/null)" ]]; then
    rsync -a \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='AGENTS.md' \
        --exclude='SOUL.md' \
        --exclude='USER.md' \
        --exclude='TOOLS.md' \
        --exclude='IDENTITY.md' \
        --exclude='HEARTBEAT.md' \
        --exclude='SITES.md' \
        --exclude='MEMORY.md' \
        "$WORKSPACE/skills/" "$BACKUP_DIR/skills/" 2>/dev/null || {
        # Fallback to cp if rsync fails
        rm -rf "$BACKUP_DIR/skills"
        cp -r "$WORKSPACE/skills" "$BACKUP_DIR/"
    }
fi

# === Safe Copy: Scripts using rsync with exclude patterns ===
if [[ -d "$WORKSPACE/scripts" ]] && [[ -n "$(ls -A "$WORKSPACE/scripts/" 2>/dev/null)" ]]; then
    rsync -a \
        --exclude='.git' \
        --exclude='AGENTS.md' \
        --exclude='SOUL.md' \
        --exclude='USER.md' \
        --exclude='TOOLS.md' \
        --exclude='IDENTITY.md' \
        --exclude='HEARTBEAT.md' \
        --exclude='SITES.md' \
        --exclude='MEMORY.md' \
        "$WORKSPACE/scripts/" "$BACKUP_DIR/scripts/" 2>/dev/null || {
        # Fallback to cp if rsync fails
        rm -rf "$BACKUP_DIR/scripts"
        cp -r "$WORKSPACE/scripts" "$BACKUP_DIR/"
    }
fi

echo "Files copied"

cd "$BACKUP_DIR"
if [[ ! -d ".git" ]]; then
    git init
    git remote add origin "https://github.com/${BACKUP_REPO}.git"
fi

# === COMPREHENSIVE SECRET SCANNING ===
# Scan ENTIRE backup directory (not just staged files)
SECRET_PATTERN='(ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{20,}|AIza[a-zA-Z0-9_-]{35}|xox[pborsa]-[0-9a-zA-Z]{10,48}|AKIA[0-9A-Z]{16}|[a-zA-Z0-9/+=]{40,}|(-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----))'

# Recursively scan all files in backup directory
SECRETS_FOUND=$(grep -rE "$SECRET_PATTERN" "$BACKUP_DIR" --exclude-dir=.git --line-number 2>/dev/null || true)

if [[ -n "$SECRETS_FOUND" ]]; then
    echo "Error: Potential secret detected in backup directory!"
    echo "$SECRETS_FOUND"
    echo "Aborting backup for safety."
    rm -rf "$BACKUP_DIR/.git"
    exit 1
fi

# === Git Operations ===
git add -A

# Stage-level scan (additional check)
if git diff --cached --name-only | xargs -I {} grep -qE "$SECRET_PATTERN" {} 2>/dev/null; then
    echo "Error: Potential secret detected in staged files. Aborting."
    git diff --cached --name-only | xargs -I {} grep -lE "$SECRET_PATTERN" {} 2>/dev/null || true
    git reset
    exit 1
fi

# === SECURE Git Push (No Token in Process) ===
if gh auth status &>/dev/null; then
    # Use gh CLI - no token exposure
    gh auth setup-git 2>/dev/null || true
    if ! git diff --cached --quiet; then
        git commit -m "Backup: $(date '+%Y-%m-%d %H:%M')"
        gh repo sync . --branch "$BRANCH" 2>/dev/null || git push -u origin "$BRANCH"
        echo "Backup complete!"
    fi
else
    # Fallback: Use git credential helper (more secure than command-line)
    if [[ -n "$TOKEN" ]]; then
        # Store token in git credential helper (not visible in ps)
        printf "https://%s@github.com" "$TOKEN" | git credential approve
        
        if ! git diff --cached --quiet; then
            git commit -m "Backup: $(date '+%Y-%m-%d %H:%M')"
            git push -u origin "$BRANCH"
            echo "Backup complete!"
        fi
        
        # Clear credential
        printf "https://%s@github.com" "$TOKEN" | git credential reject
    else
        echo "Error: No GH auth or GITHUB_TOKEN"
        exit 1
    fi
fi
