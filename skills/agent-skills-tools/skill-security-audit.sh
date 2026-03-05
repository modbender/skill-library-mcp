#!/bin/bash
# 技能安全审计脚本
# 检查技能包中的常见安全隐患

SKILL_DIR="${1:-.}"
echo "🔒 技能安全审计报告：$SKILL_DIR"
echo "=========================================="
echo ""

# 检查1: 凭据泄露
echo "📋 检查1: 凭据泄露（API key, password, secret, token）"
echo "----------------------------------------"
CREDENTIAL_LEAKS=$(find "$SKILL_DIR" \( -name "*.sh" -o -name "*.js" -o -name "*.py" \) \
    -exec grep -l -i "api[_-]key.*['\"][^'\"]*['\"]" {} \; 2>/dev/null | \
    while read file; do
        grep -n "api[_-]key.*['\"][^'\"]*['\"]" "$file" | head -3
    done)

if [ -z "$CREDENTIAL_LEAKS" ]; then
    echo "✅ 未发现凭据泄露"
else
    echo "❌ 发现潜在凭据泄露："
    echo "$CREDENTIAL_LEAKS"
fi
echo ""

# 检查2: 文件访问权限
echo "📋 检查2: 危险的文件操作（~/.ssh, ~/.aws, ~/.config）"
echo "----------------------------------------"
DANGEROUS_ACCESS=$(find "$SKILL_DIR" \( -name "*.sh" -o -name "*.js" -o -name "*.py" \) \
    -exec grep -l -E "\.(ssh|aws|config)" {} \; 2>/dev/null)

if [ -z "$DANGEROUS_ACCESS" ]; then
    echo "✅ 未发现危险的文件访问"
else
    echo "⚠️  发现文件访问："
    echo "$DANGEROUS_ACCESS"
fi
echo ""

# 检查3: 网络请求
echo "📋 检查3: 外部网络请求"
echo "----------------------------------------"
NETWORK_REQUESTS=$(find "$SKILL_DIR" \( -name "*.sh" -o -name "*.js" -o -name "*.py" \) \
    -exec grep -l -E "(curl|wget|fetch|axios|http\.get)" {} \; 2>/dev/null)

if [ -z "$NETWORK_REQUESTS" ]; then
    echo "✅ 未发现网络请求"
else
    echo "⚠️  发现网络请求文件："
    echo "$NETWORK_REQUESTS"
fi
echo ""

# 检查4: 环境变量使用
echo "📋 检查4: 环境变量使用（推荐做法）"
echo "----------------------------------------"
ENV_USAGE=$(find "$SKILL_DIR" \( -name "*.sh" -o -name "*.js" -o -name "*.py" \) \
    -exec grep -l -E "(process\.env|ENV\[)" {} \; 2>/dev/null)

if [ -z "$ENV_USAGE" ]; then
    echo "⚠️  未发现环境变量使用（建议使用环境变量存储敏感信息）"
else
    echo "✅ 发现安全的环境变量使用："
    echo "$ENV_USAGE"
fi
echo ""

# 检查5: 文件权限
echo "📋 检查5: 权限检查（credentials.json）"
echo "----------------------------------------"
CREDS_FILES=$(find "$SKILL_DIR" -name "credentials.json" 2>/dev/null)

if [ -z "$CREDS_FILES" ]; then
    echo "ℹ️  未发现credentials.json文件"
else
    echo "📁 发现credentials.json文件："
    echo "$CREDS_FILES"
    echo ""
    for file in $CREDS_FILES; do
        if [ -r "$file" ]; then
            echo "  ✅ $file 可读（正常）"
        else
            echo "  ❌ $file 权限异常"
        fi
    done
fi
echo ""

# 检查6: Git history检查
echo "📋 检查6: 是否为Git仓库（检查历史记录）"
echo "----------------------------------------"
if [ -d "$SKILL_DIR/.git" ]; then
    echo "⚠️  这是一个Git仓库"
    echo "   建议：检查历史记录中是否有凭据被提交"
    echo "   命令: git log -S 'api_key'
"

    # 检查是否有敏感信息提交
    SENSITIVE_COMMITS=$(git -C "$SKILL_DIR" log --all -S "api_key" --oneline 2>/dev/null | head -3)
    if [ -n "$SENSITIVE_COMMITS" ]; then
        echo "   ⚠️  历史记录中发现包含'api_key'的提交："
        echo "$SENSITIVE_COMMITS"
    fi
else
    echo "✅ 不是Git仓库"
fi
echo ""

echo "=========================================="
echo "🎯 安全审计完成"
echo ""
echo "💡 建议："
echo "- 使用环境变量存储敏感信息"
echo "- 将credentials.json添加到.gitignore"
echo "- 定期检查Git历史记录"
echo "- 使用git-secrets等工具防止凭据提交"
