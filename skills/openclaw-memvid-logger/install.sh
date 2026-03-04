#!/bin/bash
# Unified Logger Installation Script
# Usage: ./install.sh

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW_SKILLS="${HOME}/.openclaw/workspace/skills"
TARGET_DIR="${OPENCLAW_SKILLS}/unified-logger"

echo "═══════════════════════════════════════════════════════════"
echo "  Unified Conversation Logger - Installation"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "⚠️  SECURITY NOTICE:"
echo "   This skill captures ALL OpenClaw conversations and events"
echo "   to local files (JSONL + Memvid). Review the code before"
echo "   installing. See: tools/log.py for details."
echo ""
echo "   - Logs: ${HOME}/.openclaw/workspace/conversation_log.jsonl"
echo "   - Memory: ${HOME}/.openclaw/workspace/memory_YYYY-MM.mv2"
echo ""
read -p "Continue with installation? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo "Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✓ Python 3 found"

if ! command -v memvid &> /dev/null; then
    echo ""
    echo "⚠️  Memvid CLI not found."
    echo "   This requires: npm install -g memvid"
    read -p "Install Memvid CLI now? (requires sudo for global install) (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm install -g memvid || {
            echo "❌ Failed to install Memvid CLI. Install manually:"
            echo "   npm install -g memvid"
            exit 1
        }
        echo "✓ Memvid CLI installed"
    else
        echo "⚠️  Memvid CLI required. Install manually before using skill."
    fi
else
    echo "✓ Memvid CLI found"
fi

# Create OpenClaw skills directory if needed
mkdir -p "${OPENCLAW_SKILLS}"

# Copy skill files
echo ""
echo "Installing skill to ${TARGET_DIR}..."
if [ -d "${TARGET_DIR}" ]; then
    echo "⚠️  Skill already exists. Overwrite? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    rm -rf "${TARGET_DIR}"
fi

cp -r "${SKILL_DIR}" "${TARGET_DIR}"
echo "✓ Skill files copied"

# Make log.py executable
chmod +x "${TARGET_DIR}/tools/log.py"

# Initialize memory file if doesn't exist
MEMORY_FILE="${HOME}/.openclaw/workspace/memory_$(date +%Y-%m).mv2"
if [ ! -f "${MEMORY_FILE}" ]; then
    echo ""
    echo "Creating initial memory file..."
    memvid create "${MEMORY_FILE}" 2>/dev/null || {
        echo "⚠️  Could not create memory file. Will create on first use."
        echo "   Manual command: memvid create ${MEMORY_FILE}"
    }
    if [ -f "${MEMORY_FILE}" ]; then
        echo "✓ Memory file created"
    fi
else
    echo "✓ Memory file already exists"
fi

# Set up environment variables - ASK FIRST
BASHRC="${HOME}/.bashrc"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Environment Variables Setup"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "This skill uses environment variables for configuration:"
echo "   - MEMVID_MODE (single/monthly)"
echo "   - JSONL_LOG_PATH (log file location)"
echo "   - MEMVID_PATH (memory file location)"
echo ""
echo "These can be added to ${BASHRC} for persistence."
echo ""
read -p "Add environment variables to ${BASHRC}? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if ! grep -q "MEMVID_MODE" "${BASHRC}" 2>/dev/null; then
        cat >> "${BASHRC}" << 'EOF'

# Unified Logger (MemSync) configuration
export MEMVID_MODE="monthly"  # 'single' for API mode, 'monthly' for sharding
export JSONL_LOG_PATH="${HOME}/.openclaw/workspace/conversation_log.jsonl"
export MEMVID_PATH="${HOME}/.openclaw/workspace/memory.mv2"
export MEMVID_BIN="$(which memvid 2>/dev/null || echo ${HOME}/.npm-global/bin/memvid)"
EOF
        echo "✓ Environment variables added to ${BASHRC}"
        echo "  Run: source ${BASHRC}  (or restart your terminal)"
    else
        echo "✓ Environment variables already configured"
    fi
else
    echo "⚠️  Skipped environment setup. Set manually if needed:"
    echo "   export MEMVID_MODE=monthly"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Installation Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Security reminders:"
echo "   • This skill logs ALL conversations and events"
echo "   • Data stored locally in: ${HOME}/.openclaw/workspace/"
echo "   • API mode requires MEMVID_API_KEY (remote storage)"
echo "   • Review logs regularly and secure sensitive data"
echo ""
echo "Next steps:"
echo "   1. Source your profile: source ${BASHRC}"
echo "   2. Start OpenClaw - logging begins automatically"
echo "   3. Search: memvid ask memory_$(date +%Y-%m).mv2 'your query'"
echo ""
echo "Documentation: ${TARGET_DIR}/README.md"
echo ""
