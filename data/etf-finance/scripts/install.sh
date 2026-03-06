#!/bin/bash
# Install etf-investor skill

set -e

echo "Installing etf-investor skill..."

# Create the data directory
mkdir -p ~/.clawdbot/etf_investor

# Create empty files if they don't exist
DATA_DIR="$HOME/.clawdbot/etf_investor"

if [ ! -f "$DATA_DIR/positions.json" ]; then
    echo "[]" > "$DATA_DIR/positions.json"
    echo "Created empty positions file: $DATA_DIR/positions.json"
fi

if [ ! -f "$DATA_DIR/alerts.json" ]; then
    echo "[]" > "$DATA_DIR/alerts.json"
    echo "Created empty alerts file: $DATA_DIR/alerts.json"
fi

# Check if yfinance is installed
if ! python3 -c "import yfinance" 2>/dev/null; then
    echo ""
    echo "Installing yfinance package..."
    pip3 install --user yfinance || pip3 install --break-system-packages yfinance
fi

# Make scripts executable
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
chmod +x "$SCRIPT_DIR"/*.py

echo ""
echo "ETF Investor skill installed successfully!"
echo ""
echo "Data directory: $DATA_DIR"
echo ""
echo "Quick start:"
echo "  Add a position:   python3 scripts/add_position.py SPY 150.50 100"
echo "  View portfolio:   python3 scripts/portfolio_summary.py"
echo "  Add alert:        python3 scripts/add_alert.py SPY 160.00 price_up"
echo ""
echo "For more commands, see SKILL.md"
