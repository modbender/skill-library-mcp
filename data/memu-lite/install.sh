#!/bin/bash
# memU-lite 安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$HOME/.openclaw/workspace"

echo "🧠 安装 memU-lite 记忆系统..."

# 检查是否已存在记忆系统
if [ -f "$WORKSPACE_DIR/memory/MEMORY.md" ]; then
    echo "⚠️  检测到已有记忆系统，跳过初始化"
    echo ""
    echo "如需查看示例文件，请检查:"
    echo "  $SCRIPT_DIR/memory/MEMORY.md"
    echo "  $SCRIPT_DIR/memory/TEMPLATE.md"
    echo ""
    echo "如需强制重新初始化，请先备份并删除:"
    echo "  rm -rf $WORKSPACE_DIR/memory/"
    echo "  然后重新运行此脚本"
    exit 0
fi

# 创建目录结构
echo "📁 创建记忆目录结构..."
mkdir -p "$WORKSPACE_DIR/memory/raw"
mkdir -p "$WORKSPACE_DIR/memory/items/preferences"
mkdir -p "$WORKSPACE_DIR/memory/items/knowledge"
mkdir -p "$WORKSPACE_DIR/memory/items/relationships"
mkdir -p "$WORKSPACE_DIR/memory/items/tasks"
mkdir -p "$WORKSPACE_DIR/memory/items/skills"
mkdir -p "$WORKSPACE_DIR/memory/indexes"
mkdir -p "$WORKSPACE_DIR/memory/archive"  # 新增归档目录

# 复制模板文件
echo "📄 复制模板文件..."
cp "$SCRIPT_DIR/memory/TEMPLATE.md" "$WORKSPACE_DIR/memory/items/TEMPLATE.md" 2>/dev/null || true
cp "$SCRIPT_DIR/memory/MEMORY.md" "$WORKSPACE_DIR/memory/MEMORY.md" 2>/dev/null || true
cp "$SCRIPT_DIR/memory/tags.md" "$WORKSPACE_DIR/memory/indexes/tags.md" 2>/dev/null || true

# 创建示例记忆
echo "📝 创建示例记忆..."

cat > "$WORKSPACE_DIR/memory/items/preferences/P-20260302-001-开发偏好.md" << 'EOF'
## P-20260302-001 开发偏好

- **类型**: preference
- **来源**: 示例记忆
- **日期**: 2026-03-02
- **置信度**: high
- **标签**: #偏好 #开发 #示例
- **内容**: 
  1. 偏好 Python 和 JavaScript
  2. 代码风格简洁、可读性强
  3. 重视测试和文档
  4. 喜欢使用开源工具
- **关联**: [[R-20260302-001]]
EOF

cat > "$WORKSPACE_DIR/memory/items/relationships/R-20260302-001-用户信息.md" << 'EOF'
## R-20260302-001 用户信息

- **类型**: relationship
- **来源**: 示例记忆
- **日期**: 2026-03-02
- **置信度**: high
- **标签**: #用户 #示例
- **内容**: 
  - 时区：Asia/Shanghai
  - 位置：中国大陆
  - 语言：简体中文
  - 角色：开发者
- **关联**: [[P-20260302-001]]
EOF

# 创建 MEMORY.md 索引
cat > "$WORKSPACE_DIR/memory/MEMORY.md" << 'EOF'
# MEMORY.md - 长期记忆

**最后更新**: 2026-03-02  
**记忆总数**: 2

---

## 📌 快速概览

### 用户偏好 (Preferences)
- 📝 开发偏好：Python/JavaScript，简洁代码风格

### 关键知识 (Knowledge)
_暂无记录_

### 人际关系 (Relationships)
- 👤 用户信息 - 开发者

### 进行中的事 (Active Tasks)
_暂无_

### 技能/方法 (Skills)
_暂无_

---

## 🗂️ 记忆索引

| ID | 类型 | 标题 | 日期 | 标签 |
|----|------|------|------|------|
| P-20260302-001 | preference | 开发偏好 | 2026-03-02 | #偏好 #开发 |
| R-20260302-001 | relationship | 用户信息 | 2026-03-02 | #用户 #示例 |

---

*此文件由 memU-lite 自动维护*
EOF

# 创建标签索引
cat > "$WORKSPACE_DIR/memory/indexes/tags.md" << 'EOF'
# 标签索引

## #偏好
- P-20260302-001 开发偏好

## #用户
- R-20260302-001 用户信息

EOF

echo "✅ memU-lite 安装完成!"
echo ""
echo "📂 记忆目录：$WORKSPACE_DIR/memory/"
echo "📖 使用指南：查看 SKILL.md 或 memory/memu-lite-guide.md"
echo ""
echo "下一步:"
echo "  1. 编辑 MEMORY.md 添加你的记忆"
echo "  2. 在 items/ 目录下创建原子记忆文件"
echo "  3. 使用 memory_search/memory_get 工具检索记忆"
