#!/bin/bash
# Dropbox KB Auto - Interactive Installer

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_FILE="$SCRIPT_DIR/user-config.json"
OPENCLAW_ENV="$HOME/.openclaw/.env"

echo "╔════════════════════════════════════════════════╗"
echo "║   Dropbox KB Auto - Interactive Setup         ║"
echo "╔════════════════════════════════════════════════╗"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v openclaw &> /dev/null; then
    echo "❌ OpenClaw not found. Install from: https://openclaw.ai"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

echo "✅ OpenClaw found"
echo "✅ Python 3 found"
echo ""

# Run dependency installer
echo "📦 Installing dependencies..."
bash "$SCRIPT_DIR/setup.sh" || {
    echo "❌ Dependency installation failed"
    exit 1
}
echo ""

# Interactive configuration
echo "⚙️  Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Folders to index
echo "📁 Which Dropbox folders should be indexed?"
echo "   Enter folder paths (one per line, empty line when done)"
echo "   Examples: /Documents, /Work, /Research"
echo ""

FOLDERS=()
while true; do
    read -p "Folder (or press Enter to finish): " folder
    if [ -z "$folder" ]; then
        if [ ${#FOLDERS[@]} -eq 0 ]; then
            echo "   ⚠️  At least one folder required. Adding /Documents as default."
            FOLDERS+=("/Documents")
        fi
        break
    fi
    # Add leading slash if missing
    [[ "$folder" != /* ]] && folder="/$folder"
    FOLDERS+=("$folder")
    echo "   ✓ Added: $folder"
done
echo ""

# Paths to skip
echo "🚫 Which paths should be EXCLUDED?"
echo "   Enter paths to skip (one per line, empty line when done)"
echo "   Examples: /Archive, /Backups, /Photos"
echo ""

SKIP_PATHS=()
while true; do
    read -p "Skip path (or press Enter to finish): " skip
    [ -z "$skip" ] && break
    [[ "$skip" != /* ]] && skip="/$skip"
    SKIP_PATHS+=("$skip")
    echo "   ✓ Will skip: $skip"
done
echo ""

# File types
echo "📄 File types to index:"
echo "   Default: pdf, docx, xlsx, pptx, jpg, png, txt, md"
read -p "   Use defaults? [Y/n]: " use_default_types
if [[ "$use_default_types" =~ ^[Nn]$ ]]; then
    echo "   Enter file extensions (comma-separated, e.g., pdf,docx,jpg):"
    read -p "   Extensions: " custom_types
    IFS=',' read -ra FILE_TYPES <<< "$custom_types"
else
    FILE_TYPES=(pdf docx doc xlsx xls pptx ppt jpg jpeg png txt md csv json)
fi
echo ""

# Max file size
read -p "📏 Maximum file size in MB [default: 20]: " max_size
max_size=${max_size:-20}
echo ""

# OCR languages
echo "🌐 OCR languages (for images and scanned PDFs):"
echo "   Default: eng,deu (English + German)"
read -p "   Languages (comma-separated, e.g., eng,fra,spa): " ocr_langs
ocr_langs=${ocr_langs:-"eng,deu"}
IFS=',' read -ra OCR_LANGS <<< "$ocr_langs"
echo ""

# Generate config
echo "💾 Generating configuration..."

# Create JSON config
cat > "$CONFIG_FILE" << EOF
{
  "folders": [$(printf '"%s",' "${FOLDERS[@]}" | sed 's/,$//')],
  "skip_paths": [$(printf '"%s",' "${SKIP_PATHS[@]}" | sed 's/,$//')],
  "file_types": [$(printf '"%s",' "${FILE_TYPES[@]}" | sed 's/,$//')],
  "max_file_size_mb": $max_size,
  "ocr_languages": [$(printf '"%s",' "${OCR_LANGS[@]}" | sed 's/,$//')],
  "max_text_chars": 12000
}
EOF

echo "✅ Config saved to $CONFIG_FILE"
echo ""

# Update dropbox-sync.py with user config
echo "📝 Updating indexer script..."
python3 << PYEOF
import json, sys
with open('$CONFIG_FILE') as f:
    config = json.load(f)

with open('$SCRIPT_DIR/dropbox-sync.py') as f:
    script = f.read()

# Replace FOLDERS line
folders_str = str(config['folders'])
script = script.replace(
    'FOLDERS = ["/Documents", "/Work", "/Research"]',
    f'FOLDERS = {folders_str}'
)

# Replace SKIP_PATHS line
skip_str = str(config['skip_paths']) if config['skip_paths'] else '[]'
script = script.replace(
    'SKIP_PATHS = ["/Archive", "/Backups", "/Photos"]',
    f'SKIP_PATHS = {skip_str}'
)

# Replace INDEX_EXTS
exts_str = '{' + ', '.join(f'"{ext}"' for ext in config['file_types']) + '}'
import re
script = re.sub(
    r'INDEX_EXTS = \{[^}]+\}',
    f'INDEX_EXTS = {exts_str}',
    script
)

with open('$SCRIPT_DIR/dropbox-sync.py', 'w') as f:
    f.write(script)

print("✅ Indexer updated with your settings")
PYEOF
echo ""

# Dropbox credentials
echo "🔑 Dropbox API Credentials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Create app at: https://www.dropbox.com/developers/apps"
echo "   Permissions needed: files.metadata.read, files.content.read"
echo ""

if grep -q "DROPBOX_FULL_APP_KEY=" "$OPENCLAW_ENV" 2>/dev/null; then
    echo "✅ Dropbox credentials already configured in $OPENCLAW_ENV"
    echo ""
else
    echo "   Credentials not found. Please add to $OPENCLAW_ENV:"
    echo ""
    cat "$SCRIPT_DIR/.env.example"
    echo ""
    read -p "Press Enter after adding credentials to continue..."
    echo ""
fi

# Create cron job
echo "⏰ Automated Sync Schedule"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Create cron job for automatic syncing? [Y/n]: " create_cron
if [[ ! "$create_cron" =~ ^[Nn]$ ]]; then
    echo "   How often should indexing run?"
    echo "   1) Every 6 hours (recommended)"
    echo "   2) Every 12 hours"
    echo "   3) Daily at midnight"
    echo "   4) Custom cron expression"
    read -p "   Choice [1-4]: " cron_choice
    
    case $cron_choice in
        1) cron_expr="0 */6 * * *" ;;
        2) cron_expr="0 */12 * * *" ;;
        3) cron_expr="0 0 * * *" ;;
        4)
            echo "   Enter cron expression (e.g., '0 8 * * *' for 8am daily):"
            read -p "   Expression: " cron_expr
            ;;
        *) cron_expr="0 */6 * * *" ;;
    esac
    
    echo "   Creating cron job..."
    openclaw cron create \
        --name "Dropbox KB Sync" \
        --cron "$cron_expr" \
        --tz "$(timedatectl show -p Timezone --value 2>/dev/null || echo UTC)" \
        --timeout-seconds 14400 \
        --session isolated \
        --message "cd $SCRIPT_DIR && python3 dropbox-sync.py" \
        --no-deliver || {
        echo "   ⚠️  Failed to create cron job. You can create it manually later."
    }
    echo "   ✅ Cron job created"
    echo ""
fi

# Initial sync option
echo "🚀 Ready to Index!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Run initial sync now? [Y/n]: " run_now
if [[ ! "$run_now" =~ ^[Nn]$ ]]; then
    echo ""
    echo "Starting initial sync (this may take a while on first run)..."
    cd "$SCRIPT_DIR" && python3 dropbox-sync.py
fi

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║   ✅ Installation Complete!                    ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "  • Folders indexed: ${FOLDERS[@]}"
echo "  • Paths skipped: ${#SKIP_PATHS[@]} pattern(s)"
echo "  • File types: ${#FILE_TYPES[@]} type(s)"
echo "  • Max file size: ${max_size}MB"
echo "  • OCR languages: $ocr_langs"
echo ""
echo "What's next?"
echo "  • Files will sync automatically via cron"
echo "  • Ask your agent: 'Search my Dropbox for...'"
echo "  • Manual sync: cd $SCRIPT_DIR && python3 dropbox-sync.py"
echo "  • Config file: $CONFIG_FILE"
echo ""
echo "Need help? https://github.com/ferreirafabio/dropbox-kb-auto"
