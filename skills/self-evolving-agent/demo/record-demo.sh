#!/usr/bin/env bash
# ============================================================
# record-demo.sh — Self-Evolving Agent v4.0 Demo Recorder
#
# 사용법:
#   bash demo/record-demo.sh           # GIF 생성 (vhs 필요)
#   bash demo/record-demo.sh --text    # 텍스트 출력만
#
# 출력:
#   demo/demo.gif       — 터미널 GIF (vhs 필요)
#   demo/demo-output.txt — 실제 파이프라인 raw 출력
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

MODE="${1:-}"

echo "🧠 Self-Evolving Agent v4.0 — Demo Recorder"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Step 1: Check dependencies ──────────────────────────────
if [[ "$MODE" != "--text" ]]; then
  if command -v vhs &>/dev/null; then
    echo "✅ vhs found: $(vhs --version 2>/dev/null || echo 'installed')"
    USE_VHS=true
  else
    echo "⚠️  vhs not found. Install with: brew install vhs"
    echo "   Falling back to text output only."
    USE_VHS=false
  fi
else
  USE_VHS=false
fi

# ── Step 2: Run pipeline and capture output ──────────────────
echo ""
echo "📡 Running v4.0 pipeline (DRY_RUN=true, VERBOSE=true)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$SKILL_DIR"

DRY_RUN=true VERBOSE=true bash scripts/v4/orchestrator.sh 2>&1 \
  | tee "$SCRIPT_DIR/demo-output.txt"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Raw output saved: demo/demo-output.txt"

# ── Step 3: Generate GIF ────────────────────────────────────
if [[ "$USE_VHS" == "true" ]]; then
  echo ""
  echo "🎬 Generating GIF with vhs..."
  cd "$SCRIPT_DIR"
  vhs demo.tape && echo "✅ GIF saved: demo/demo.gif" \
    || echo "⚠️  GIF generation failed. Check demo.tape and vhs installation."
fi

echo ""
echo "🏁 Done!"
