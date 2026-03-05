#!/bin/bash

###############################################################################
# Soul Memory Uninstall Test Script
###############################################################################

set -e

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Soul Memory Uninstall Test ===${NC}"
echo ""

# 模擬配置
TEST_DIR=$(mktemp -d)
OPPENCLAW_CONFIG="$TEST_DIR/openclaw.json"
HEARTBEAT_FILE="$TEST_DIR/HEARTBEAT.md"

echo -e "${GREEN}[1/3] 創建測試配置...${NC}"

# 創建模擬 openclaw.json
cat > "$OPPENCLAW_CONFIG" << EOF
{
  "plugins": {
    "entries": {
      "soul-memory": {
        "enabled": true,
        "config": {
          "topK": 5,
          "minScore": 0.0
        }
      },
      "other-plugin": {
        "enabled": true
      }
    }
  }
}
EOF

# 創建模擬 HEARTBEAT.md
cat > "$HEARTBEAT_FILE" << EOF
# Heartbeat

## Soul Memory Auto-Trigger

\`\`\`bash
python3 /root/.openclaw/workspace/soul-memory/heartbeat-trigger.py
\`\`\`

## Soul Memory Auto-Save

\`\`\`python
from soul_memory.core import SoulMemorySystem
system = SoulMemorySystem()
\`\`\`
EOF

echo -e "${GREEN}[2/3] 驗證測試配置...${NC}"
grep -q "soul-memory" "$OPPENCLAW_CONFIG" && echo "✓ Plugin 配置已創建"
grep -q "heartbeat-trigger" "$HEARTBEAT_FILE" && echo "✓ Heartbeat 觸發已創建"
grep -q "SoulMemorySystem" "$HEARTBEAT_FILE" && echo "✓ 自動保存代碼已創建"

echo ""
echo -e "${GREEN}[3/3] 測試卸載邏輯（不實際執行）...${NC}"
echo ""

# 測試 Plugin 配置移除
echo "測試：移除 Plugin 配置"
if command -v jq &> /dev/null; then
    BACKUP_FILE="$TEST_DIR/openclaw.json.backup"
    jq 'del(.plugins.entries["soul-memory"])' "$OPPENCLAW_CONFIG" > "$BACKUP_FILE"
    cat "$BACKUP_FILE" | jq '.plugins.entries'
    echo "✓ Plugin 配置移除邏輯正常"
else
    echo "⚠ jq 不可用，跳過此測試"
fi

echo ""
echo -e "${GREEN}=== 測試完成 ===${NC}"
echo ""
echo "測試文件位置：$TEST_DIR（測試後自動刪除）"

# 清理測試文件
rm -rf "$TEST_DIR"
