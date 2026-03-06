#!/bin/bash
# 大哥的记忆恢复脚本
# 用途：Session启动时自动恢复所有记忆

echo "🧠 大哥的记忆恢复系统启动..."

# 1. 读取今日记忆
echo "📅 读取今日记忆..."
TODAY=$(date +%Y-%m-%d)
if [ -f "memory/$TODAY.md" ]; then
    echo "--- 今日记忆 ($TODAY) ---"
    cat memory/$TODAY.md
    echo ""
fi

# 2. 读取永久记忆
echo "♾️ 读取永久记忆..."
if [ -f "memory/permanent/identity.md" ]; then
    echo "--- 身份与偏好 ---"
    cat memory/permanent/identity.md
    echo ""
fi

if [ -f "memory/permanent/technical-stack.md" ]; then
    echo "--- 技术栈 ---"
    cat memory/permanent/technical-stack.md
    echo ""
fi

if [ -f "memory/permanent/working-directory.md" ]; then
    echo "--- 工作目录与习惯 ---"
    cat memory/permanent/working-directory.md
    echo ""
fi

if [ -f "memory/permanent/key-decisions.md" ]; then
    echo "--- 关键决策与教训 ---"
    cat memory/permanent/key-decisions.md
    echo ""
fi

# 3. 搜索相关记忆（如果memory_search可用）
echo "🔍 搜索相关记忆..."
if command -v memory_search &> /dev/null; then
    echo "正在搜索与当前任务相关的记忆..."
    # 这里可以添加具体的搜索命令
    # memory_search "当前任务关键词"
fi

echo ""
echo "✅ 记忆恢复完成！"
echo "💡 提示：你现在拥有完整的工作上下文和决策历史。"
