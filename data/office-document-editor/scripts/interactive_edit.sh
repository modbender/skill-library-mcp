#!/bin/bash
# Interactive Document Editor - Guides user through the editing process
# Usage: bash scripts/interactive_edit.sh

set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/office-document-editor"
cd "$SKILL_DIR"

echo ""
echo "📝 Universal Document Editor"
echo "============================"
echo ""

# Step 1: File Source
echo "Step 1: File Source"
echo "━━━━━━━━━━━━━━━━━━━━"
echo "Where is your file located?"
echo ""
echo "[1] 📎 Uploaded file (latest attachment)"
echo "[2] 📁 Local path (on your computer)"
echo "[3] 🌐 URL (web link)"
echo "[4] 🔌 SFTP (remote server)"
echo ""
read -p "Enter choice [1-4]: " SOURCE_CHOICE

case $SOURCE_CHOICE in
    1)
        SOURCE="upload"
        ;;
    2)
        read -p "Enter file path: " SOURCE
        ;;
    3)
        read -p "Enter URL: " SOURCE
        ;;
    4)
        read -p "Enter SFTP path (e.g., sftp://user@host:/path/file.docx): " SOURCE
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Detect file type
if [[ "$SOURCE" == *.pptx ]]; then
    FILE_TYPE="pptx"
elif [[ "$SOURCE" == *.docx ]]; then
    FILE_TYPE="docx"
else
    # Try to detect from content or ask
    echo ""
    echo "What type of file is this?"
    echo "[1] DOCX (Word document)"
    echo "[2] PPTX (PowerPoint presentation)"
    read -p "Enter choice [1-2]: " TYPE_CHOICE
    if [ "$TYPE_CHOICE" = "1" ]; then
        FILE_TYPE="docx"
    else
        FILE_TYPE="pptx"
    fi
fi

# Fetch file
echo ""
bash scripts/fetch_file.sh "$SOURCE" "input.$FILE_TYPE"

if [ ! -f "input.$FILE_TYPE" ]; then
    echo "❌ Failed to fetch file"
    exit 1
fi

# Step 2: Edit Type
echo ""
echo "Step 2: Edit Type"
echo "━━━━━━━━━━━━━━━━━━━━"
echo "What edits would you like to make?"
echo ""
echo "[1] 🔤 Text replacement"
echo "[2] ➕ Add text after specific content"
echo "[3] 🎨 Apply formatting (bold/italic/underline)"
echo "[4] 📊 Rearrange slides (PPTX only)"
echo "[5] ✏️  Multiple edits (advanced)"
echo ""
read -p "Enter choice [1-5]: " EDIT_CHOICE

# Generate edits.json
cat > edits.json << 'EOF'
{
  "description": "User-requested edits",
  "replacements": [],
  "additions": []
}
EOF

case $EDIT_CHOICE in
    1)
        read -p "Text to search: " SEARCH_TEXT
        read -p "Replacement text: " REPLACE_TEXT
        echo "Style: [1] Normal [2] Highlight [3] Bold [4] Delete"
        read -p "Choose style [1-4]: " STYLE
        case $STYLE in
            2) STYLE_JSON="highlight" ;;
            3) STYLE_JSON="bold" ;;
            4) STYLE_JSON="delete" ;;
            *) STYLE_JSON="replace" ;;
        esac
        
        # Update JSON (simple approach)
        cat > edits.json << EOF
{
  "description": "Text replacement",
  "replacements": [
    {
      "search": "$SEARCH_TEXT",
      "replace": "$REPLACE_TEXT",
      "style": "$STYLE_JSON"
    }
  ]
}
EOF
        ;;
    2)
        read -p "After what text: " AFTER_TEXT
        read -p "Text to add: " ADD_TEXT
        echo "Style: [1] Highlight [2] Bold [3] Normal"
        read -p "Choose style [1-3]: " STYLE
        case $STYLE in
            2) STYLE_JSON="bold" ;;
            3) STYLE_JSON="replace" ;;
            *) STYLE_JSON="highlight" ;;
        esac
        
        cat > edits.json << EOF
{
  "description": "Add text",
  "additions": [
    {
      "after": "$AFTER_TEXT",
      "text": "$ADD_TEXT",
      "style": "$STYLE_JSON"
    }
  ]
}
EOF
        ;;
    3)
        read -p "Text to format: " FORMAT_TEXT
        echo "Format: [1] Bold [2] Italic [3] Underline [4] Highlight"
        read -p "Choose format [1-4]: " FORMAT
        case $FORMAT in
            2) STYLE_JSON="italic" ;;  # Note: italic may not be supported
            3) STYLE_JSON="underline" ;;
            4) STYLE_JSON="highlight" ;;
            *) STYLE_JSON="bold" ;;
        esac
        
        cat > edits.json << EOF
{
  "description": "Apply formatting",
  "replacements": [
    {
      "search": "$FORMAT_TEXT",
      "replace": "$FORMAT_TEXT",
      "style": "$STYLE_JSON"
    }
  ]
}
EOF
        ;;
    5)
        echo "Advanced mode: Create your own edits.json"
        echo "Opening editor..."
        ${EDITOR:-nano} edits.json
        ;;
    *)
        echo "❌ Edit type not implemented yet"
        exit 1
        ;;
esac

echo ""
echo "✅ Edit rules created: edits.json"
cat edits.json
echo ""

# Step 3: Execute Edit
echo "Step 3: Execute Edit"
echo "━━━━━━━━━━━━━━━━━━━━"
read -p "Proceed with edit? [Y/n]: " PROCEED

if [ "$PROCEED" = "n" ] || [ "$PROCEED" = "N" ]; then
    echo "❌ Edit cancelled"
    exit 0
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="output_${TIMESTAMP}.$FILE_TYPE"

echo ""
echo "Executing edit..."
if [ "$FILE_TYPE" = "docx" ]; then
    uv run python scripts/docx_editor.py "input.$FILE_TYPE" "$OUTPUT_FILE" edits.json
else
    uv run python scripts/pptx_editor.py "input.$FILE_TYPE" "$OUTPUT_FILE" edits.json
fi

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "❌ Edit failed"
    exit 1
fi

echo "✅ Edit complete: $OUTPUT_FILE"

# Step 4: Generate Reports
echo ""
echo "Step 4: Generate Reports"
echo "━━━━━━━━━━━━━━━━━━━━"
if [ "$FILE_TYPE" = "docx" ]; then
    read -p "Generate diff report? [Y/n]: " GEN_DIFF
    if [ "$GEN_DIFF" != "n" ] && [ "$GEN_DIFF" != "N" ]; then
        DIFF_FILE="diff_${TIMESTAMP}.md"
        uv run python scripts/generate_diff.py "input.$FILE_TYPE" "$OUTPUT_FILE" "$DIFF_FILE"
        echo "✅ Diff report: $DIFF_FILE"
        echo ""
        echo "Preview:"
        head -20 "$DIFF_FILE"
    fi
fi

# Step 5: Output
echo ""
echo "Step 5: Output"
echo "━━━━━━━━━━━━━━━━━━━━"
echo "Where should I save the edited file?"
echo ""
echo "[1] 📁 Current directory ($SKILL_DIR)"
echo "[2] 📂 Specific path"
echo "[3] ☁️ Upload to server (SFTP)"
echo "[4] 📎 Copy to workspace media folder"
read -p "Enter choice [1-4]: " OUTPUT_CHOICE

case $OUTPUT_CHOICE in
    1)
        echo "✅ File saved: $SKILL_DIR/$OUTPUT_FILE"
        ;;
    2)
        read -p "Enter destination path: " DEST_PATH
        cp "$OUTPUT_FILE" "$DEST_PATH"
        echo "✅ File saved: $DEST_PATH"
        ;;
    3)
        read -p "Enter SFTP destination (e.g., sftp://user@host:/path/): " SFTP_DEST
        SFTP_PATH="${SFTP_DEST#sftp://}"
        USER_HOST="${SFTP_PATH%%:*}"
        REMOTE_PATH="${SFTP_PATH#*:}"
        
        sftp "$USER_HOST" << EOF
put $OUTPUT_FILE $REMOTE_PATH
EOF
        echo "✅ File uploaded to: $SFTP_DEST"
        ;;
    4)
        cp "$OUTPUT_FILE" ~/.openclaw/workspace/media/inbound/
        echo "✅ File copied to: ~/.openclaw/workspace/media/inbound/$OUTPUT_FILE"
        ;;
esac

# Summary
echo ""
echo "============================"
echo "✅ Edit Complete!"
echo "============================"
echo ""
echo "Files created:"
echo "  - $OUTPUT_FILE (edited document)"
[ -f "$DIFF_FILE" ] && echo "  - $DIFF_FILE (diff report)"
echo "  - edits.json (edit rules)"
echo ""
echo "To review changes:"
echo "  cat $DIFF_FILE"
echo "  open $OUTPUT_FILE"
echo ""
