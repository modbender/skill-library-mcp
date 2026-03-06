#!/bin/bash
# Auto-install and configure NadirClaw for OpenClaw
set -e

echo "Installing NadirClaw..."
pip install nadirclaw 2>/dev/null || pip3 install nadirclaw

echo "Running OpenClaw onboarding..."
nadirclaw openclaw onboard

echo "Starting NadirClaw in background..."
nohup nadirclaw serve > /tmp/nadirclaw.log 2>&1 &
echo "NadirClaw running on http://localhost:8856 (PID: $!)"
echo "Done! Your OpenClaw is now routing through NadirClaw."
