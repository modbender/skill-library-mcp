#!/bin/bash
# 🧠 Intrusive Thoughts Installation Script
# Sets up the system for any AI agent to use

set -e

echo "🧠 Intrusive Thoughts - Installation & Setup"
echo "=========================================="

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$INSTALL_DIR"

# Check Python dependencies
echo "📦 Checking Python dependencies..."
python3 -c "import json, re, pathlib, datetime, collections, statistics, http.server" 2>/dev/null || {
    echo "❌ Missing Python standard library modules. Please install Python 3.7+"
    exit 1
}

# Check for config file
if [[ ! -f "config.json" ]]; then
    echo "⚙️  Creating config.json from template..."
    if [[ -f "config.example.json" ]]; then
        cp config.example.json config.json
        echo "✅ config.json created - please customize it!"
        echo ""
        echo "📝 IMPORTANT: Edit config.json with your details:"
        echo "   - human.name: Your human's name"
        echo "   - human.telegram_target: @their_username"
        echo "   - agent.name: Your agent name"
        echo "   - agent.emoji: Your preferred emoji"
        echo "   - system.data_dir: Where to store data (default: current directory)"
        echo ""
    else
        echo "❌ config.example.json not found!"
        exit 1
    fi
fi

# Create required directories
echo "📁 Creating directory structure..."
mkdir -p log journal

# Initialize data files if they don't exist
echo "🔧 Initializing data files..."

[[ ! -f "mood_history.json" ]] && echo '{"version": 1, "history": []}' > mood_history.json
[[ ! -f "history.json" ]] && echo '[]' > history.json
[[ ! -f "achievements_earned.json" ]] && echo '{"version": 1, "earned": [], "total_points": 0}' > achievements_earned.json
[[ ! -f "human_mood.json" ]] && echo '{"version": 1, "current": null, "history": []}' > human_mood.json

# Initialize streaks.json with default weights
if [[ ! -f "streaks.json" ]]; then
    cat > streaks.json << 'EOF'
{
  "version": 1,
  "current_streaks": {
    "activity_type": [],
    "mood": [],
    "time_slot": []
  },
  "recent_activities": [],
  "anti_rut_weights": {
    "build-tool": 1.0,
    "upgrade-project": 1.0,
    "install-explore": 1.0,
    "moltbook-night": 1.0,
    "system-tinker": 1.0,
    "learn": 1.0,
    "memory-review": 1.0,
    "creative-chaos": 1.0,
    "moltbook-social": 1.0,
    "share-discovery": 1.0,
    "moltbook-post": 1.0,
    "check-projects": 1.0,
    "random-thought": 1.0,
    "ask-opinion": 1.0,
    "ask-preference": 1.0,
    "pitch-idea": 1.0,
    "ask-feedback": 1.0
  },
  "streak_history": []
}
EOF
fi

# Make scripts executable
echo "🔑 Making scripts executable..."
chmod +x *.py *.sh

# Test configuration loading
echo "🧪 Testing configuration..."
python3 config.py || {
    echo "❌ Configuration test failed!"
    exit 1
}

# Test core functionality
echo "🧪 Testing core scripts..."
python3 mood_memory.py suggest > /dev/null || {
    echo "❌ mood_memory.py test failed!"
    exit 1
}

python3 analyze.py --json > /dev/null || {
    echo "❌ analyze.py test failed!"
    exit 1
}

python3 check_achievements.py > /dev/null || {
    echo "❌ check_achievements.py test failed!"
    exit 1
}

echo "✅ All tests passed!"
echo ""
echo "🎉 Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit config.json with your specific settings"
echo "2. Test the system: ./intrusive.sh night"
echo "3. Set up cron jobs for automatic scheduling:"
echo "   # Morning mood setting"
echo "   0 7 * * * cd $INSTALL_DIR && ./set_mood.sh"
echo "   # Night sessions"
echo "   0 3,30 4,45 5,15 6,17 7 * * * cd $INSTALL_DIR && ./intrusive.sh night"
echo "   # Day sessions" 
echo "   0 11,16,20 * * * cd $INSTALL_DIR && ./intrusive.sh day"
echo ""
echo "4. Start the dashboard: python3 dashboard.py"
echo "5. Begin your intrusive thoughts journey! 🧠"
echo ""
echo "🔗 Dashboard will be available at: http://localhost:$(python3 -c 'from config import get_dashboard_port; print(get_dashboard_port())')"