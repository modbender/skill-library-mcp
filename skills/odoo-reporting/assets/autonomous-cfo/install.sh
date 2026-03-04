#!/bin/bash
# Install script for autonomous-cfo Odoo skill
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Setting up autonomous-cfo..."

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Install dependencies
echo "Installing dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Verify installation
echo "Verifying installation..."
./venv/bin/python -c "import requests, matplotlib, PIL, fpdf; print('All dependencies installed')"

# Test connection (requires .env)
if [ -f ".env" ]; then
    echo "Testing Odoo connection..."
    ./venv/bin/python src/tools/cfo_cli.py doctor
else
    echo "Note: .env file not found. Create one with ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Usage:"
echo "  ./venv/bin/python src/tools/cfo_cli.py <command>"
echo ""
echo "Commands:"
echo "  doctor          - Test connection"
echo "  executive       - Executive summary"
echo "  health          - Financial health"
echo "  revenue         - Revenue analytics"
echo "  aging           - AR/AP aging"
echo "  expenses        - Expense breakdown"
echo "  adhoc           - Custom comparison"
