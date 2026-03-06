#!/bin/bash
# Install OpenClaw Advanced Memory
# Run as: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

echo "⚡ Installing OpenClaw Advanced Memory"
echo "================================"

# 1. Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install --user qdrant-client redis requests 2>/dev/null || true

# 2. Create Qdrant collections
echo ""
echo "🗄️  Setting up Qdrant collections..."
python3 "$SCRIPT_DIR/setup_collections.py"

# 3. Install systemd service for mem-capture
echo ""
echo "🔧 Installing mem-capture systemd service..."
mkdir -p ~/.config/systemd/user/
cp "$PARENT_DIR/mem-capture.service" ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable mem-capture.service
systemctl --user start mem-capture.service
echo "   ✅ mem-capture service installed and started"

# 4. Install cron jobs
echo ""
echo "⏰ Installing cron jobs..."

# mem-warm: every 30 minutes
WARM_CRON="*/30 * * * * /usr/bin/python3 $SCRIPT_DIR/mem_warm.py >> /tmp/mem-warm.log 2>&1"
# mem-curate: daily at 2 AM (9 AM UTC, which is 2 AM MST)
CURATE_CRON="0 9 * * * /usr/bin/python3 $SCRIPT_DIR/mem_curate.py >> /tmp/mem-curate.log 2>&1"

# Add to crontab (idempotent)
(crontab -l 2>/dev/null | grep -v "mem_warm.py" | grep -v "mem_curate.py"; echo "$WARM_CRON"; echo "$CURATE_CRON") | crontab -
echo "   ✅ Cron jobs installed"
echo "      - mem-warm: every 30 minutes"
echo "      - mem-curate: daily at 2 AM MST (9 AM UTC)"

# 5. Create convenience scripts
echo ""
echo "📝 Creating convenience scripts..."

cat > "$SCRIPT_DIR/../recall" << 'EOF'
#!/bin/bash
python3 $(cd "$(dirname "$0")/.." && pwd)/scripts/mem_recall.py "$@"
EOF
chmod +x "$SCRIPT_DIR/../recall"

cat > "$SCRIPT_DIR/../warm-now" << 'EOF'
#!/bin/bash
echo "⚡ Running mem-warm manually..."
python3 $(cd "$(dirname "$0")/.." && pwd)/scripts/mem_warm.py
EOF
chmod +x "$SCRIPT_DIR/../warm-now"

cat > "$SCRIPT_DIR/../curate-now" << 'EOF'
#!/bin/bash
DATE=${1:-$(date -u -d "yesterday" +%Y-%m-%d)}
echo "⚡ Running mem-curate for $DATE..."
python3 $(cd "$(dirname "$0")/.." && pwd)/scripts/mem_curate.py "$DATE"
EOF
chmod +x "$SCRIPT_DIR/../curate-now"

cat > "$SCRIPT_DIR/../mem-status" << 'EOF'
#!/bin/bash
echo "⚡ Watts Memory V2 Status"
echo "========================="
echo ""
echo "📡 Capture Service:"
systemctl --user status mem-capture.service --no-pager 2>/dev/null | head -5
echo ""
echo "📊 Collections:"
python3 -c "
from qdrant_client import QdrantClient
import redis
c = QdrantClient(host='localhost', port=6333)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
buf = r.llen('mem:watts:turns')
for name in ['watts_warm', 'watts_cold', 'watts_memories']:
    if c.collection_exists(name):
        info = c.get_collection(name)
        print(f'  {name}: {info.points_count} points ({info.status})')
    else:
        print(f'  {name}: not found')
print(f'  Redis buffer: {buf} turns pending')
"
echo ""
echo "📋 Recent Logs:"
echo "  Warm: $(tail -1 /tmp/mem-warm.log 2>/dev/null || echo 'no logs yet')"
echo "  Curate: $(tail -1 /tmp/mem-curate.log 2>/dev/null || echo 'no logs yet')"
EOF
chmod +x "$SCRIPT_DIR/../mem-status"

echo ""
echo "================================"
echo "✅ OpenClaw Advanced Memory installed!"
echo ""
echo "Commands:"
echo "  skills/memory-v2/recall \"query\"     — Search memory"
echo "  skills/memory-v2/mem-status          — System status"
echo "  skills/memory-v2/warm-now            — Force warm flush"
echo "  skills/memory-v2/curate-now [date]   — Force curation"
echo ""
echo "Collections:"
echo "  watts_warm  — Mid-term (7 days, auto-updated every 30 min)"
echo "  watts_cold  — Long-term (forever, curated nightly)"
echo "  watts_memories — Archive (existing 29K points, read-only)"
