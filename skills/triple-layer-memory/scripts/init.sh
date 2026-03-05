#!/bin/bash
# 初始化三层记忆系统

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)"

echo "初始化三层记忆系统..."
echo "工作空间: $WORKSPACE_ROOT"

# 创建 memory 目录
mkdir -p "$WORKSPACE_ROOT/memory/.archive"

# 创建 MEMORY.md（如果不存在）
if [ ! -f "$WORKSPACE_ROOT/MEMORY.md" ]; then
    cat > "$WORKSPACE_ROOT/MEMORY.md" << 'EOF'
# MEMORY.md

## 长期认知（持续生效）

1. **提醒类任务先执行后汇报**：遇到"复盘/检查/整理"这类提醒，优先产出实际结果（文件或结论），再给用户状态更新。
2. **长文本先做完整性校验**：对榜单、日志、抓取结果等长输入，先判断是否被截断；若不完整，必须显式声明并提供补全路径。
3. **承诺即闭环，杜绝"只回复不落地"**：说"我来做"后必须在同一轮工具调用中完成产出（文件/结果），不得留到下一轮 session。
4. **Session 自动压缩**：token 使用量达到 150k 时自动触发压缩，总结关键信息并写入记忆文件，保留最近 50k tokens 原始对话。
5. **关键时机自动写入记忆**：完成任务、做出决策、变更配置、解决问题时立即写入记忆，不等 session 结束。
6. **新 session 智能加载记忆**：启动时根据频道和任务自动加载相关记忆，避免重复询问已知信息。

## 配置记录

_待补充_
EOF
    echo "✓ 创建 MEMORY.md"
else
    echo "✓ MEMORY.md 已存在"
fi

# 创建 memory/projects.md（如果不存在）
if [ ! -f "$WORKSPACE_ROOT/memory/projects.md" ]; then
    cat > "$WORKSPACE_ROOT/memory/projects.md" << 'EOF'
# Projects - 项目状态追踪

## 活跃项目

_待添加_

## 已完成项目

_待添加_

## 归档项目

_待添加_

---

**更新规则**：
- 项目状态变更时立即更新
- 每周检查一次，归档已完成超过 30 天的项目
- 重要项目永久保留在"已完成项目"区
EOF
    echo "✓ 创建 memory/projects.md"
else
    echo "✓ memory/projects.md 已存在"
fi

# 创建 memory/lessons.md（如果不存在）
if [ ! -f "$WORKSPACE_ROOT/memory/lessons.md" ]; then
    cat > "$WORKSPACE_ROOT/memory/lessons.md" << 'EOF'
# Lessons - 经验教训库

## 高优先级（importance >= 8）

_待添加_

## 中优先级（importance 5-7）

_待添加_

## 低优先级（importance < 5）

_待添加_

---

**更新规则**：
- 遇到新问题时立即记录
- 每月检查一次，归档已过时的经验
- importance >= 8 的经验永久保留
EOF
    echo "✓ 创建 memory/lessons.md"
else
    echo "✓ memory/lessons.md 已存在"
fi

# 创建今天的日志文件（如果不存在）
TODAY=$(date +%Y-%m-%d)
if [ ! -f "$WORKSPACE_ROOT/memory/$TODAY.md" ]; then
    cat > "$WORKSPACE_ROOT/memory/$TODAY.md" << EOF
# $TODAY

_今日记录_
EOF
    echo "✓ 创建 memory/$TODAY.md"
else
    echo "✓ memory/$TODAY.md 已存在"
fi

# 创建 heartbeat-state.json（如果不存在）
if [ ! -f "$WORKSPACE_ROOT/memory/heartbeat-state.json" ]; then
    cat > "$WORKSPACE_ROOT/memory/heartbeat-state.json" << EOF
{
  "lastMemoryMaintenance": "$TODAY"
}
EOF
    echo "✓ 创建 memory/heartbeat-state.json"
else
    echo "✓ memory/heartbeat-state.json 已存在"
fi

# 创建 pinned.json（如果不存在）
if [ ! -f "$WORKSPACE_ROOT/memory/pinned.json" ]; then
    cat > "$WORKSPACE_ROOT/memory/pinned.json" << 'EOF'
{
  "pinned": [],
  "updatedAt": ""
}
EOF
    echo "✓ 创建 memory/pinned.json"
else
    echo "✓ memory/pinned.json 已存在"
fi

# 复制架构文档
cp "$(dirname "${BASH_SOURCE[0]}")/../templates/MEMORY_ARCHITECTURE.md" "$WORKSPACE_ROOT/" 2>/dev/null || echo "⚠ MEMORY_ARCHITECTURE.md 模板不存在，跳过"

echo ""
echo "✅ 初始化完成！"
echo ""
echo "下一步："
echo "1. 编辑 MEMORY.md 添加你的长期认知和配置"
echo "2. 更新 AGENTS.md 添加 Session 启动流程"
echo "3. 更新 HEARTBEAT.md 添加 token 检查逻辑"
echo "4. 如果使用 Mem0，配置频道级命名空间隔离"
echo ""
echo "详细文档: skills/triple-layer-memory/SKILL.md"
