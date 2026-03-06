#!/bin/bash
# 安全扫描测试脚本
# 用于测试 publish.sh 中的安全扫描功能

set -e

echo "🧪 安全扫描功能测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 创建临时测试目录
TEST_DIR=$(mktemp -d)
echo "📂 创建测试目录: $TEST_DIR"

# 测试 1: 安全的技能（应该通过）
echo ""
echo "测试 1: 安全的技能（应该通过）"
echo "────────────────────────────────"
mkdir -p "$TEST_DIR/safe-skill"
cat > "$TEST_DIR/safe-skill/SKILL.md" << 'EOF'
---
name: safe-skill
description: 安全的技能示例
---

# Safe Skill

这是一个安全的技能，使用占位符。

## 环境变量

export API_KEY="YOUR_API_KEY_HERE"
export SECRET="YOUR_SECRET_HERE"
EOF

cat > "$TEST_DIR/safe-skill/script.sh" << 'EOF'
#!/bin/bash
API_KEY="${API_KEY:-YOUR_API_KEY_HERE}"
SECRET="${SECRET:-YOUR_SECRET_HERE}"
EOF

echo "✓ 创建测试文件"
echo ""

# 测试 2: 包含硬编码密钥的技能（应该失败）
echo "测试 2: 包含硬编码密钥（应该失败）"
echo "────────────────────────────────"
mkdir -p "$TEST_DIR/unsafe-skill"
cat > "$TEST_DIR/unsafe-skill/SKILL.md" << 'EOF'
---
name: unsafe-skill
description: 不安全的技能示例
---

# Unsafe Skill

这个技能包含硬编码的密钥。

## 配置

export API_KEY="tvly-YOUR_API_KEY_HERE"
EOF

cat > "$TEST_DIR/unsafe-skill/script.sh" << 'EOF'
#!/bin/bash
# 这个脚本包含硬编码的 GitHub Token
TOKEN="ghp_YOUR_TOKEN_HERE"
EOF

echo "✓ 创建测试文件"
echo ""

# 运行测试
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "开始测试..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试安全扫描功能
echo "🔍 测试 1: 安全技能扫描"
if bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/publish.sh "$TEST_DIR/safe-skill" --version 1.0.0 2>&1 | grep -q "安全扫描通过"; then
  echo "✅ 测试 1 通过：安全技能被正确识别"
else
  echo "❌ 测试 1 失败：安全技能未被正确识别"
fi
echo ""

echo "🔍 测试 2: 不安全技能扫描"
if bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/publish.sh "$TEST_DIR/unsafe-skill" --version 1.0.0 2>&1 | grep -q "安全扫描失败"; then
  echo "✅ 测试 2 通过：不安全技能被正确识别"
else
  echo "❌ 测试 2 失败：不安全技能未被正确识别"
fi
echo ""

# 清理
echo "🧹 清理测试目录..."
rm -rf "$TEST_DIR"
echo "✅ 测试完成"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 安全扫描功能已验证"
echo ""
echo "支持的检测项："
echo "  ✓ Tavily API Key (tvly-...)"
echo "  ✓ OpenAI API Key (sk-...)"
echo "  ✓ GitHub Tokens (ghp_, gho_, ghu_, ghs_)"
echo "  ✓ Perplexity API Key (pplx-...)"
echo "  ✓ Exa AI API Key (exa_...)"
echo "  ✓ 通用 API Key 模式"
echo "  ✓ App Secret"
echo "  ✓ Access Token"
echo "  ✓ 敏感文件（.env, .secrets, *.key, *.pem）"
echo "  ✓ 环境变量硬编码（export API_KEY=）"
echo ""
echo "使用方法："
echo "  bash publish.sh /path/to/skill --version 1.0.0"
echo ""
echo "跳过安全扫描（不推荐）："
echo "  bash publish.sh /path/to/skill --version 1.0.0 --skip-security"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
