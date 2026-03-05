#!/usr/bin/env bash
set -euo pipefail

RUNTIME_DIR="${RUNTIME_DIR:-/Users/lijunsheng/.openclaw/workspace-jun-invest-option-master-agent}"
SYNC_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/sync-runtime-to-artifact.sh"

if [[ ! -d "${RUNTIME_DIR}" ]]; then
  echo "FAIL: runtime workspace not found: ${RUNTIME_DIR}" >&2
  exit 1
fi

command -v git >/dev/null 2>&1 || { echo "FAIL: git not found" >&2; exit 1; }

cd "${RUNTIME_DIR}"

if [[ ! -f .gitignore ]]; then
  cat > .gitignore <<'EOF'
# Runtime-local derived files
.openclaw/
logs/
tmp/

# Python
**/__pycache__/
**/*.pyc
**/*.pyo
**/.venv/

# macOS
.DS_Store
EOF
fi

if [[ ! -d .git ]]; then
  git init >/dev/null
fi

mkdir -p .git/hooks
cat > .git/hooks/post-commit <<EOF
#!/usr/bin/env bash
set -euo pipefail
bash "${SYNC_SCRIPT}"
EOF
chmod +x .git/hooks/post-commit

if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  git add -A >/dev/null 2>&1 || true
  git commit -m "bootstrap: runtime workspace" >/dev/null 2>&1 || true
fi

echo "OK: runtime git initialized and post-commit hook installed."
