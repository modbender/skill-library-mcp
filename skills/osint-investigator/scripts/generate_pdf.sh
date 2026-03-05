#!/usr/bin/env bash
# OSINT Investigator — PDF Report Generator wrapper
# Self-installs fpdf2 if missing, then runs generate_pdf.py
# Usage: bash generate_pdf.sh --input report.md --target "Name" --output ~/Desktop

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure fpdf2 is available
if ! python3 -c "import fpdf" 2>/dev/null; then
  echo "📦 Installing fpdf2..."
  pip3 install fpdf2 -q --break-system-packages 2>/dev/null \
    || pip3 install fpdf2 -q \
    || pip3 install fpdf2 -q --user
fi

# Verify install succeeded
if ! python3 -c "import fpdf" 2>/dev/null; then
  echo "❌ ERROR: Could not install fpdf2. Try manually: pip3 install fpdf2"
  exit 1
fi

python3 "$SCRIPT_DIR/generate_pdf.py" "$@"
