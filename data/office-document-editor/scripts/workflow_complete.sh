#!/bin/bash
# Office Document Editor - Complete Workflow
# Usage: bash scripts/workflow_complete.sh <input.docx|input.pptx> <edits.json>

set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/office-document-editor"
cd "$SKILL_DIR"

echo "📝 Office Document Editor - Complete Workflow"
echo "=============================================="
echo ""

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <input.file> <edits.json>"
    echo ""
    echo "Examples:"
    echo "  $0 document.docx examples/irb-response-example.json"
    echo "  $0 presentation.pptx examples/presentation-update-example.json"
    exit 1
fi

INPUT_FILE="$1"
EDITS_JSON="$2"

# Check files exist
if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ Error: File not found: $INPUT_FILE"
    exit 1
fi

if [ ! -f "$EDITS_JSON" ]; then
    echo "❌ Error: Edits file not found: $EDITS_JSON"
    exit 1
fi

# Detect file type
EXTENSION="${INPUT_FILE##*.}"
BASENAME=$(basename "$INPUT_FILE" .$EXTENSION)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "📄 Input: $INPUT_FILE"
echo "📝 Edits: $EDITS_JSON"
echo ""

# Step 1: Convert to Markdown
echo "📄 Step 1: Convert to Markdown (for Git tracking)..."
MARKDOWN_FILE="${BASENAME}_original.md"
uv run markitdown "$INPUT_FILE" > "$MARKDOWN_FILE" 2>/dev/null || {
    echo "⚠️  Markitdown failed, trying mammoth..."
    uv run mammoth --output-format=markdown "$INPUT_FILE" > "$MARKDOWN_FILE"
}
echo "  ✅ Markdown: $MARKDOWN_FILE"

# Step 2: Edit document
echo ""
echo "✏️  Step 2: Edit document..."
if [ "$EXTENSION" = "docx" ]; then
    OUTPUT_FILE="${BASENAME}_edited_${TIMESTAMP}.docx"
    uv run python scripts/docx_editor.py "$INPUT_FILE" "$OUTPUT_FILE" "$EDITS_JSON"
elif [ "$EXTENSION" = "pptx" ]; then
    OUTPUT_FILE="${BASENAME}_edited_${TIMESTAMP}.pptx"
    uv run python scripts/pptx_editor.py "$INPUT_FILE" "$OUTPUT_FILE" "$EDITS_JSON"
else
    echo "❌ Error: Unsupported file type: $EXTENSION"
    echo "   Supported: docx, pptx"
    exit 1
fi

# Step 3: Generate diff report
echo ""
echo "📊 Step 3: Generate Unified Diff report..."
DIFF_REPORT="${BASENAME}_diff_${TIMESTAMP}.md"
if [ "$EXTENSION" = "docx" ]; then
    uv run python scripts/generate_diff.py "$INPUT_FILE" "$OUTPUT_FILE" "$DIFF_REPORT"
    echo "  ✅ Diff report: $DIFF_REPORT"
else
    echo "  ⚠️  Diff generation for PPTX not yet implemented"
    touch "$DIFF_REPORT"
fi

# Step 4: Git commit
echo ""
echo "💾 Step 4: Commit to Git..."
if [ -d ".git" ]; then
    git add "$MARKDOWN_FILE" "$OUTPUT_FILE" "$DIFF_REPORT" 2>/dev/null || true
    git commit -m "Edit $BASENAME - $(date +%Y-%m-%d)" || echo "  (No changes to commit)"
    echo "  ✅ Git commit complete"
else
    echo "  ⚠️  Git not initialized, skipping commit"
fi

# Summary
echo ""
echo "=============================================="
echo "✅ Workflow Complete!"
echo "=============================================="
echo ""
echo "📁 Generated files:"
echo "  - $MARKDOWN_FILE (Markdown version)"
echo "  - $OUTPUT_FILE (Edited document)"
echo "  - $DIFF_REPORT (Diff report)"
echo ""
echo "📊 View diff:"
echo "  cat $DIFF_REPORT"
echo ""
echo "🔍 View Git history:"
echo "  git log --oneline"
echo "  git diff HEAD~1"
echo ""
echo "📝 Next steps:"
echo "  1. Review the edited document in Word/PowerPoint"
echo "  2. Make manual adjustments if needed"
echo "  3. Submit to IRB or share with stakeholders"
echo ""
