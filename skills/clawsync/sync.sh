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

# === Explicit Exclusions (Hardcoded) ===
# These files are NEVER backed up - contains secrets/sensitive data
EXCLUDE_FILES=("SITES.md" "MEMORY.md" ".env" "credentials" "node_modules" ".git" "venv" "__pycache__")

# === Helper: Check if file should be excluded ===
should_exclude() {
    local file="$1"
    for excl in "${EXCLUDE_FILES[@]}"; do
        if [[ "$file" == *"$excl"* ]]; then
            return 0
        fi
    done
    return 1
}

# === Strict Whitelist: Identity Files ===
WHITELIST=("AGENTS.md" "SOUL.md" "USER.md" "TOOLS.md" "IDENTITY.md" "HEARTBEAT.md")

for file in "${WHITELIST[@]}"; do
    if [[ -f "$WORKSPACE/$file" ]]; then
        cp "$WORKSPACE/$file" "$BACKUP_DIR/"
    fi
done

# === Safe Copy: Skills (with explicit exclusion) ===
if [[ -d "$WORKSPACE/skills" ]]; then
    rm -rf "$BACKUP_DIR/skills"
    mkdir -p "$BACKUP_DIR/skills"
    
    for skill in "$WORKSPACE/skills"/*; do
        if [[ ! -d "$skill" ]]; then
            continue
        fi
        
        if should_exclude "$skill"; then
            continue
        fi
        
        # Copy, excluding .git directories
        rsync -a --exclude='.git' --exclude='node_modules' "$skill/" "$BACKUP_DIR/skills/$(basename "$skill")/" 2>/dev/null || \
            cp -r "$skill" "$BACKUP_DIR/skills/" 2>/dev/null || true
    done
fi

# === Safe Copy: Scripts (with explicit exclusion) ===
if [[ -d "$WORKSPACE/scripts" ]]; then
    rm -rf "$BACKUP_DIR/scripts"
    mkdir -p "$BACKUP_DIR/scripts"
    
    for script in "$WORKSPACE/scripts"/*; do
        if [[ ! -f "$script" ]]; then
            continue
        fi
        
        if should_exclude "$script"; then
            continue
        fi
        
        cp -r "$script" "$BACKUP_DIR/scripts/"
    done
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
