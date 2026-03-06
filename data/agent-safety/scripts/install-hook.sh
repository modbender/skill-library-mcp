#!/usr/bin/env bash
# Install pre-commit hook that runs pre-publish-scan.sh
# Usage: install-hook.sh <repo-path>
# Installs a git pre-commit hook that blocks commits containing secrets or PII.

set -euo pipefail

REPO="${1:-.}"
HOOK_DIR="$REPO/.git/hooks"
HOOK="$HOOK_DIR/pre-commit"
SCAN_SCRIPT="$(cd "$(dirname "$0")" && pwd)/pre-publish-scan.sh"

if [ ! -d "$REPO/.git" ]; then
  echo "Error: $REPO is not a git repository"
  exit 1
fi

if [ ! -f "$SCAN_SCRIPT" ]; then
  echo "Error: pre-publish-scan.sh not found at $SCAN_SCRIPT"
  exit 1
fi

mkdir -p "$HOOK_DIR"

# Write hook — scans only staged files
cat > "$HOOK" << 'HOOKEOF'
#!/usr/bin/env bash
# Auto-installed by github-publish skill
# Scans staged files for secrets and PII before allowing commit

set -euo pipefail

SCAN_SCRIPT="__SCAN_SCRIPT__"

if [ ! -f "$SCAN_SCRIPT" ]; then
  echo "⚠ pre-publish-scan.sh not found at $SCAN_SCRIPT"
  echo "  Blocking commit as a safety measure."
  echo "  Reinstall hook: bash <skill-dir>/scripts/install-hook.sh <repo>"
  exit 1
fi

# Get staged files (added/modified, not deleted)
STAGED=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED" ]; then
  exit 0
fi

# Create temp dir with staged content (scan what's being committed, not working tree)
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

FAIL=0
for f in $STAGED; do
  mkdir -p "$TMPDIR/$(dirname "$f")"
  git show ":$f" > "$TMPDIR/$f" 2>/dev/null || continue
done

echo "🔒 Pre-commit security scan..."
if ! bash "$SCAN_SCRIPT" "$TMPDIR"; then
  echo ""
  echo "❌ Commit blocked. Fix issues above before committing."
  echo "   To bypass (emergencies only): git commit --no-verify"
  exit 1
fi

echo "✅ Security scan passed."
HOOKEOF

# Inject actual path (portable across macOS and Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s|__SCAN_SCRIPT__|$SCAN_SCRIPT|g" "$HOOK"
else
  sed -i "s|__SCAN_SCRIPT__|$SCAN_SCRIPT|g" "$HOOK"
fi
chmod +x "$HOOK"

echo "✅ Pre-commit hook installed at $HOOK"
echo "   Scans staged files using: $SCAN_SCRIPT"
echo "   Bypass (emergencies): git commit --no-verify"
