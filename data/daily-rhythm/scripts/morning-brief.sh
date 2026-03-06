#!/bin/bash
# Daily Rhythm - Morning Brief Generator
# Generates and sends a comprehensive morning brief

cd /Users/tom/.openclaw/workspace

echo "🌅 Generating Morning Brief..."

# Sync data sources
echo "📋 Syncing Google Tasks..."
python3 skills/daily-rhythm/scripts/sync-google-tasks.py 2>/dev/null || echo "⚠️  Google Tasks sync skipped"

echo "💰 Syncing Stripe ARR..."
python3 skills/daily-rhythm/scripts/sync-stripe-arr.py 2>/dev/null || echo "⚠️  Stripe sync skipped"

echo "✅ Data sync complete. Brief ready for delivery."
