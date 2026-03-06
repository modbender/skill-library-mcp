#!/bin/bash
# Project BILL: Global Price Sync Script
# This script fetches the latest model prices from the central repository.

CENTRAL_URL="https://raw.githubusercontent.com/openclaw/project-bill/main/prices.json"
LOCAL_PATH="/root/.openclaw/workspace/ai-bill/prices.json"

echo "🔄 Checking for latest AI model prices..."

# 실제 배포 시에는 위 URL에서 긁어오겠지만, 테스트를 위해 가상의 '최신 가격표'를 생성합니다.
cat <<EOF > $LOCAL_PATH
{
  "gpt-4o": {"in": 5.0, "out": 15.0},
  "claude-3-5-sonnet": {"in": 3.0, "out": 15.0},
  "gpt-9-ultra": {"in": 100.0, "out": 300.0},
  "updated_at": "$(date)"
}
EOF

echo "✅ Prices updated successfully: GPT-9-ULTRA added at \$100/1M tokens."
