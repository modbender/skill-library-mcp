#!/usr/bin/env bash
# setup.sh — Install dependencies for skill-trust-auditor
# Run once before using the auditor: bash scripts/setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "==> skill-trust-auditor setup"
echo "    Project: $PROJECT_DIR"
echo ""

# ── Python check ──────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found. Install it via:"
  echo "  macOS:  brew install python3"
  echo "  Ubuntu: sudo apt install python3 python3-pip"
  exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  python3: $PYTHON_VERSION"

# ── pip check ─────────────────────────────────────────────────────────────────
if ! python3 -m pip --version &>/dev/null; then
  echo "ERROR: pip not found. Install python3-pip and retry."
  exit 1
fi

# ── Install Python packages ───────────────────────────────────────────────────
echo ""
echo "==> Installing Python dependencies..."

python3 -m pip install --quiet --upgrade pip

# Core requirements
PACKAGES=(
  "requests>=2.31.0"      # HTTP fetching (skill content download)
  "anthropic>=0.25.0"     # LLM-as-judge analysis (optional but recommended)
)

for pkg in "${PACKAGES[@]}"; do
  pkg_name="${pkg%%[>=]*}"
  if python3 -c "import ${pkg_name//-/_}" &>/dev/null 2>&1; then
    echo "  already installed: $pkg_name"
  else
    echo "  installing: $pkg_name ..."
    python3 -m pip install --quiet "$pkg"
    echo "  installed: $pkg_name"
  fi
done

# ── clawhub CLI check (optional) ──────────────────────────────────────────────
echo ""
echo "==> Checking optional dependencies..."

if command -v clawhub &>/dev/null; then
  CLAWHUB_VERSION=$(clawhub --version 2>&1 || echo "unknown")
  echo "  clawhub CLI: found ($CLAWHUB_VERSION)"
else
  echo "  clawhub CLI: NOT found (optional — auditor will fall back to URL-based fetching)"
  echo "    To install: see https://clawhub.ai/install"
fi

# ── ANTHROPIC_API_KEY check (optional) ────────────────────────────────────────
echo ""
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  echo "  ANTHROPIC_API_KEY: set (LLM-as-judge analysis enabled)"
else
  echo "  ANTHROPIC_API_KEY: not set (LLM-as-judge analysis disabled)"
  echo "    Set it to enable nuanced intent analysis:"
  echo "    export ANTHROPIC_API_KEY=sk-ant-..."
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "==> Setup complete! Run an audit with:"
echo "    bash scripts/audit.sh <skill-name-or-url>"
echo "    bash scripts/audit.sh steipete/git-summary"
echo "    bash scripts/audit.sh https://clawhub.ai/someuser/someskill"
