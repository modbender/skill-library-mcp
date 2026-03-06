#!/bin/bash
set -e

# --- Configuration ---
SKILL_DIR="$HOME/.openclaw/skills/memory-pro"
SOURCE_DIR="$(dirname "$(realpath "$0")")"
PORT=8001

echo "📦 Installing Memory Pro Skill..."

# 1. Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: 'uv' is not installed. Please install 'uv' first."
    exit 1
fi

# 2. Copy files to ~/.openclaw/skills/memory-pro
if [ "$SOURCE_DIR" != "$SKILL_DIR" ]; then
    echo "📂 Copying files to $SKILL_DIR..."
    mkdir -p "$SKILL_DIR"
    cp -r "$SOURCE_DIR"/* "$SKILL_DIR"/
fi

# 3. Setup Python Environment
echo "🐍 Setting up Python environment with uv..."
cd "$SKILL_DIR/engine"
# Install dependencies into a local venv managed by uv or just rely on uv run
if [ -f "requirements.txt" ]; then
    uv pip install -r requirements.txt --system || uv venv && uv pip install -r requirements.txt
else
    # Create requirements.txt if missing
    cat << 'REQ' > requirements.txt
fastapi
uvicorn
sentence-transformers
faiss-cpu
pydantic
nltk
requests
REQ
    uv venv
    uv pip install -r requirements.txt
fi

# 4. Create systemd service
SERVICE_NAME="memory-pro.service"
SERVICE_PATH="$HOME/.config/systemd/user/$SERVICE_NAME"
echo "⚙️  Configuring systemd service at $SERVICE_PATH..."

mkdir -p "$HOME/.config/systemd/user"

cat << SYSTEMD > "$SERVICE_PATH"
[Unit]
Description=Memory Pro Semantic Search Service
After=network.target

[Service]
Type=simple
WorkingDirectory=$SKILL_DIR/engine
Environment=MEMORY_PRO_WORKSPACE_DIR=$HOME/.openclaw/workspace/
Environment=MEMORY_PRO_DATA_DIR=$HOME/.openclaw/workspace/memory/
Environment=MEMORY_PRO_CORE_FILES=MEMORY.md,SOUL.md,STATUS.md,AGENTS.md,USER.md
Environment=MEMORY_PRO_PORT=$PORT
Environment=MEMORY_PRO_INDEX_DIR=$SKILL_DIR/engine
Environment=MEMORY_PRO_INDEX_PATH=$SKILL_DIR/engine/memory.index
ExecStart=/bin/bash -c "source .venv/bin/activate && ./start.sh"
Restart=always
RestartSec=5s

[Install]
WantedBy=default.target
SYSTEMD

# 5. Enable and start service
echo "🚀 Starting service..."
systemctl --user daemon-reload
systemctl --user enable $SERVICE_NAME
systemctl --user restart $SERVICE_NAME

echo "✅ Memory Pro Skill installed successfully!"
echo "You can check the status with: systemctl --user status memory-pro.service"
