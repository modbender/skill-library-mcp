#!/bin/bash
# sync.sh - Backup workspace memory to git
set -euo pipefail

MSG="${1:-chore: memory backup $(date +'%Y-%m-%d %H:%M')}"
MAX_SIZE_MB=95
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-.}"

# Helper functions for structured logging
log_info() { echo "[INFO] $*"; }
log_success() { echo "[SUCCESS] $*"; }
log_warning() { echo "[WARNING] $*"; }
log_error() { echo "[ERROR] $*" >&2; }

# Step 1: Validate git repository
log_info "Validating git repository..."
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "FAILED: Not inside a git repository. Sync cancelled."
    exit 1
fi

cd "$REPO_ROOT"
log_success "Git repository found and accessible."

# Step 2: Validate git configuration
log_info "Validating git configuration..."
if ! git config user.name > /dev/null 2>&1; then
    log_error "FAILED: Git user.name not configured. Run: git config user.name 'Your Name'"
    exit 1
fi

if ! git config user.email > /dev/null 2>&1; then
    log_error "FAILED: Git user.email not configured. Run: git config user.email 'your@email.com'"
    exit 1
fi
log_success "Git user configuration is valid."

# Step 3: Validate remote configuration
log_info "Validating remote repository..."
if ! git remote get-url origin > /dev/null 2>&1; then
    log_error "FAILED: No 'origin' remote configured. Cannot push without a remote."
    exit 1
fi

REMOTE_URL=$(git remote get-url origin)
log_success "Remote 'origin' configured: $REMOTE_URL"

# Step 4: Ensure .gitignore exists
log_info "Setting up .gitignore..."
touch .gitignore
log_success "Gitignore file is ready."

# Step 5: Scan and handle large files
log_info "Scanning for large files (threshold: ${MAX_SIZE_MB}MB, git limit: 100MB)..."
LARGE_FILES=$(find "$REPO_ROOT" -type f -not -path '*/.git/*' -size +${MAX_SIZE_MB}M 2>/dev/null || true)

if [ -n "$LARGE_FILES" ]; then
    log_warning "Large files detected. These will be added to .gitignore to prevent push failures."
    while IFS= read -r file; do
        clean_file="${file#./}"
        if ! grep -qF "$clean_file" .gitignore 2>/dev/null; then
            log_info "Adding to .gitignore: $clean_file"
            echo "$clean_file" >> .gitignore
            git rm --cached "$clean_file" 2>/dev/null || true
        fi
    done <<< "$LARGE_FILES"
    log_success "Large files processed and added to .gitignore."
else
    log_success "No large files detected. Repository is within size limits."
fi

# Step 6: Check for uncommitted changes
log_info "Checking for uncommitted changes..."
TRACKED_CHANGES=false
UNTRACKED_FILES=false

if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    TRACKED_CHANGES=true
fi

if [ -n "$(git ls-files --others --exclude-standard 2>/dev/null)" ]; then
    UNTRACKED_FILES=true
fi

if [ "$TRACKED_CHANGES" = true ] || [ "$UNTRACKED_FILES" = true ]; then
    log_info "Changes detected. Staging all files..."
    git add .
    log_success "All changes staged successfully."
else
    log_info "No uncommitted changes found."
fi

# Step 7: Final check before commit
log_info "Verifying changes are staged..."
if git diff-index --quiet HEAD -- 2>/dev/null && [ -z "$(git ls-files --others --exclude-standard 2>/dev/null)" ]; then
    log_warning "No changes to commit. Working tree is clean. Sync not needed."
    exit 0
fi

# Step 8: Fetch from remote
log_info "Fetching latest changes from remote..."
if git fetch origin 2>/dev/null; then
    log_success "Successfully fetched from remote."
else
    log_warning "Fetch from remote failed (possible network issue). Continuing with local sync."
fi

# Step 9: Check for conflicts with remote
CURRENT_BRANCH=$(git symbolic-ref --short HEAD)
REMOTE_BRANCH="origin/$CURRENT_BRANCH"
log_info "Current branch: $CURRENT_BRANCH"

if git rev-parse "$REMOTE_BRANCH" > /dev/null 2>&1; then
    if ! git diff-index --quiet HEAD "$REMOTE_BRANCH" 2>/dev/null; then
        log_warning "Remote branch has diverged from local. Attempting to resolve..."
        if git pull --no-edit 2>/dev/null; then
            log_success "Successfully pulled remote changes. Local branch is updated."
        else
            log_error "FAILED: Pull encountered conflicts. Manual resolution required."
            exit 1
        fi
    else
        log_info "Local and remote branches are synchronized."
    fi
else
    log_warning "Remote branch does not exist yet. Will create on first push."
fi

# Step 10: Commit changes
log_info "Creating commit with message: '$MSG'"
if git commit -m "$MSG" 2>/dev/null; then
    log_success "Changes committed successfully."
else
    log_error "FAILED: Commit failed (possible nothing to commit)."
    exit 1
fi

# Step 11: Push to remote
log_info "Pushing changes to remote branch '$CURRENT_BRANCH'..."
if git push origin "$CURRENT_BRANCH" 2>/dev/null; then
    log_success "Successfully pushed to remote."
else
    log_warning "Standard push failed (no upstream set). Attempting to set upstream..."
    if git push --set-upstream origin "$CURRENT_BRANCH" 2>/dev/null; then
        log_success "Successfully pushed with new upstream branch tracking."
    else
        log_error "FAILED: Push failed even after setting upstream. Check network, credentials, and branch permissions."
        exit 1
    fi
fi

# Step 12: Completion
log_success "Sync and backup completed successfully. All changes have been pushed to the remote repository."
