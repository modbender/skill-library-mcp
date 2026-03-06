#!/bin/bash
# Polymarket Auto-Trader VPS Setup
# Run on a non-US VPS (e.g., DigitalOcean Amsterdam, Hetzner Finland)
set -e

echo "=== Polymarket Auto-Trader Setup ==="

# Install Python
apt update && apt install -y python3 python3-venv python3-pip

# Create virtual environment
python3 -m venv /opt/trader
/opt/trader/bin/pip install --upgrade pip
/opt/trader/bin/pip install py-clob-client==0.9.2 python-dotenv==1.0.1 web3==7.6.0 requests==2.32.3

# Create app directory
mkdir -p /opt/trader/app

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "1. Create /opt/trader/app/.env with:"
echo "   PRIVATE_KEY=<your-polygon-wallet-private-key>"
echo "   LLM_API_KEY=<your-anthropic-api-key>"
echo ""
echo "2. Run approval script:"
echo "   /opt/trader/bin/python3 approve_contracts.py"
echo ""
echo "3. Copy trading scripts to /opt/trader/app/"
echo ""
echo "4. Set up cron:"
echo "   crontab -e"
echo "   */10 * * * * cd /opt/trader/app && /opt/trader/bin/python3 run_trade.py >> cron.log 2>&1"
