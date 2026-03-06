#!/bin/bash
# Uninstall script for TriCore architecture

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(pwd)"

echo "[TriCore] Uninstalling TriCore Architecture / 正在卸载 TriCore 架构..."

# 1. Clean POLICY.md
POLICY_FILE="$WORKSPACE_ROOT/POLICY.md"
if [ -f "$POLICY_FILE" ]; then
    echo "  - Removing TriCore rules from POLICY.md / 从 POLICY.md 中移除 TriCore 规则..."
    # Python script to safely remove the injected block without deleting other parts
    python3 -c "
import re
import os
path = '$POLICY_FILE'
if os.path.exists(path):
    with open(path, 'r') as f: content = f.read()
    # Replace English compliance block
    content = re.sub(r'\n### Memory Management \(TriCore Compliance\).*?(?=\n\n|\Z)', '', content, flags=re.DOTALL)
    # Replace old Chinese compliance block (if any)
    content = re.sub(r'\n### 4\. 记忆管理 \(TriCore 架构合规要求\).*?(?=\n\n|\Z)', '', content, flags=re.DOTALL)
    with open(path, 'w') as f: f.write(content.strip() + '\n')
"
    echo "  - ✅ POLICY.md cleaned."
fi

# 2. Remove memctl.py engine
if [ -f "$WORKSPACE_ROOT/tools/memctl.py" ]; then
    rm -f "$WORKSPACE_ROOT/tools/memctl.py"
    echo "  - ✅ Removed memctl engine / 移除了 memctl 引擎"
fi

# 3. Remove Cognitive Skills
for skill in planning-with-files react-agent self-evolution; do
    if [ -d "$WORKSPACE_ROOT/skills/${skill}" ]; then
        rm -rf "$WORKSPACE_ROOT/skills/${skill}"
        echo "  - ✅ Removed cognitive skill / 移除了认知技能: ${skill}"
    fi
done

# 4. Clean OpenClaw Config Overrides
echo "  - Restoring OpenClaw pre-compaction prompt / 恢复系统原版 Token 压缩提示词..."
openclaw config unset agents.defaults.compaction.memoryFlush.prompt > /dev/null || true
echo "  - ✅ Config restored."

# 5. Prompt about Data Recovery
echo ""
echo "=================================================="
echo "[TriCore] Uninstallation Complete! / 卸载完成！"
echo ""
echo "⚠️ IMPORTANT / 重要提示:"
echo "Your original MEMORY.md was NOT automatically restored to prevent data loss."
echo "If you need your old massive MEMORY.md, you can find it in:"
echo "  -> memory/archive/legacy-MEMORY-<date>.md"
echo "You can manually rename it back to MEMORY.md if needed."
echo ""
echo "您的原始 MEMORY.md 并未自动恢复（为防止数据覆盖）。"
echo "如果您需要找回安装 TriCore 前那个庞大的旧版 MEMORY.md，请前往："
echo "  -> memory/archive/legacy-MEMORY-<date>.md"
echo "您可以手动将其重命名回项目根目录的 MEMORY.md。"
echo "=================================================="