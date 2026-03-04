#!/usr/bin/env bash
set -euo pipefail

# Create a private GitHub repo under the currently-authenticated gh account.
# Usage:
#   create_private_repo.sh <repo-name>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=bootstrap.sh
source "$SCRIPT_DIR/bootstrap.sh"
openclaw_github_sync_load_env \
  WORKSPACE_DIR SYNC_REPO_DIR SYNC_REMOTE

REPO_NAME="${1:-}"
if [[ -z "$REPO_NAME" ]]; then
  echo "Usage: $0 <repo-name>" >&2
  exit 2
fi

gh repo create "$REPO_NAME" --private --confirm

echo "Created: $(gh repo view "$REPO_NAME" --json url -q .url)"
