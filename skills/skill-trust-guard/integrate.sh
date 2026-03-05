#!/usr/bin/env bash
set -euo pipefail

GUARD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHIM_DIR="$HOME/.openclaw/bin"
REAL_CLAWHUB="$(command -v clawhub || true)"

if [[ -z "$REAL_CLAWHUB" ]]; then
  echo "clawhub not found in PATH" >&2
  exit 1
fi

mkdir -p "$SHIM_DIR"
cat > "$SHIM_DIR/clawhub" <<EOF
#!/usr/bin/env bash
set -euo pipefail
if [[ \$# -gt 0 && "\$1" == "install" ]]; then
  shift
  exec "$GUARD_DIR/install.sh" "\$@"
fi
exec "$REAL_CLAWHUB" "\$@"
EOF
chmod +x "$SHIM_DIR/clawhub"

echo "Created shim: $SHIM_DIR/clawhub"
echo "Add to PATH (before system dirs):"
echo "  export PATH=\"$SHIM_DIR:\$PATH\""
