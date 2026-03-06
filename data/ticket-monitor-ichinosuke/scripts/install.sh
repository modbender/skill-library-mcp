#!/usr/bin/env bash
set -euo pipefail

echo "Installing ticket-monitor-ichinosuke dependencies..."
pip install requests beautifulsoup4 python-dotenv --break-system-packages || pip install requests beautifulsoup4 python-dotenv

echo "Dependencies installed successfully."
