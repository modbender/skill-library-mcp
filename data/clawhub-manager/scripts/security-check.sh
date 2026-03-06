#!/bin/bash
# ClawHub 技能安全检查脚本
# 用法: ./security-check.sh <skill-path>

set -e

SKILL_PATH="$1"

if [ -z "$SKILL_PATH" ]; then
  echo "❌ 错误：缺少技能路径"
  echo ""
  echo "用法: $0 <skill-path>"
  echo ""
  echo "示例："
  echo "  $0 /root/.openclaw/workspace/skills/my-skill"
  exit 1
fi

if [ ! -d "$SKILL_PATH" ]; then
  echo "❌ 错误：技能路径不存在: $SKILL_PATH"
  exit 1
fi

echo "🔒 ClawHub 技能安全检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📂 技能路径: $SKILL_PATH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 定义占位符模式
PLACEHOLDER_FILTER='YOUR_|YOUR-|your_|your-|PLACEHOLDER|placeholder|EXAMPLE|example|XXX|xxx|REPLACEME|replaceme'

FOUND_ISSUES=0

# 1. 检查硬编码的 API 密钥
echo "🔍 检查硬编码密钥..."
echo ""

# Tavily API Key
echo -n "  Tavily API Key (tvly-)... "
TAVILY_RESULTS=$(grep -rn "tvly-[A-Za-z0-9]" "$SKILL_PATH" \
  --include="*.md" --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
  grep -vE "$PLACEHOLDER_FILTER" || true)

if [ -n "$TAVILY_RESULTS" ]; then
  if echo "$TAVILY_RESULTS" | grep -vE "tvly-(YOUR_|YOUR-|your_|your-|XXX|PLACE|EXAMPLE)" | grep -qE "tvly-[a-zA-Z0-9]{20,}"; then
    echo "❌ 发现"
    FOUND_ISSUES=1
  else
    echo "✅ 未发现"
  fi
else
  echo "✅ 未发现"
fi

# OpenAI API Key
echo -n "  OpenAI API Key (sk-)... "
OPENAI_RESULTS=$(grep -rn "sk-[a-zA-Z0-9]" "$SKILL_PATH" \
  --include="*.md" --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
  grep -vE "$PLACEHOLDER_FILTER" || true)

if [ -n "$OPENAI_RESULTS" ]; then
  if echo "$OPENAI_RESULTS" | grep -qE "sk-[a-zA-Z0-9]{48}"; then
    echo "❌ 发现"
    FOUND_ISSUES=1
  else
    echo "✅ 未发现"
  fi
else
  echo "✅ 未发现"
fi

# GitHub Tokens
echo -n "  GitHub Tokens (ghp_, gho_, ghu_, ghs_)... "
GITHUB_RESULTS=$(grep -rn "gh[puos]_[a-zA-Z0-9]" "$SKILL_PATH" \
  --include="*.md" --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
  grep -vE "$PLACEHOLDER_FILTER" || true)

if [ -n "$GITHUB_RESULTS" ]; then
  if echo "$GITHUB_RESULTS" | grep -qE "gh[puos]_[a-zA-Z0-9]{36}"; then
    echo "❌ 发现"
    FOUND_ISSUES=1
  else
    echo "✅ 未发现"
  fi
else
  echo "✅ 未发现"
fi

# Perplexity API Key
echo -n "  Perplexity API Key (pplx-)... "
PERPLEXITY_RESULTS=$(grep -rn "pplx-[a-zA-Z0-9]" "$SKILL_PATH" \
  --include="*.md" --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
  grep -vE "$PLACEHOLDER_FILTER" || true)

if [ -n "$PERPLEXITY_RESULTS" ]; then
  if echo "$PERPLEXITY_RESULTS" | grep -qE "pplx-[a-zA-Z0-9]{43}"; then
    echo "❌ 发现"
    FOUND_ISSUES=1
  else
    echo "✅ 未发现"
  fi
else
  echo "✅ 未发现"
fi

# Exa AI API Key
echo -n "  Exa AI API Key (exa_)... "
EXA_RESULTS=$(grep -rn "exa_[a-zA-Z0-9]" "$SKILL_PATH" \
  --include="*.md" --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
  grep -vE "$PLACEHOLDER_FILTER" || true)

if [ -n "$EXA_RESULTS" ]; then
  if echo "$EXA_RESULTS" | grep -qE "exa_[a-zA-Z0-9]{32}"; then
    echo "❌ 发现"
    FOUND_ISSUES=1
  else
    echo "✅ 未发现"
  fi
else
  echo "✅ 未发现"
fi

echo ""

# 2. 检查 App Secret
echo "🔍 检查 App Secret..."
echo -n "  通用模式 (app_secret=)... "
SECRET_RESULTS=$(grep -rni "app[_-]?secret\s*[=:]\s*['\"]?[a-zA-Z0-9]{20,}" "$SKILL_PATH" \
  --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
  grep -vEi "$PLACEHOLDER_FILTER" || true)

if [ -n "$SECRET_RESULTS" ]; then
  if echo "$SECRET_RESULTS" | grep -vEi "(YOUR_|your_|PLACEHOLDER|EXAMPLE|xxx)" | grep -qE "[a-zA-Z0-9]{30,}"; then
    echo "❌ 发现"
    FOUND_ISSUES=1
  else
    echo "✅ 未发现"
  fi
else
  echo "✅ 未发现"
fi

echo ""

# 3. 检查 Access Token
echo "🔍 检查 Access Token..."
echo -n "  通用模式 (access_token=)... "
TOKEN_RESULTS=$(grep -rni "access[_-]?token\s*[=:]\s*['\"]?[a-zA-Z0-9]{20,}" "$SKILL_PATH" \
  --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
  grep -vEi "$PLACEHOLDER_FILTER" || true)

if [ -n "$TOKEN_RESULTS" ]; then
  if echo "$TOKEN_RESULTS" | grep -vEi "(YOUR_|your_|PLACEHOLDER|EXAMPLE|xxx)" | grep -qE "[a-zA-Z0-9]{30,}"; then
    echo "❌ 发现"
    FOUND_ISSUES=1
  else
    echo "✅ 未发现"
  fi
else
  echo "✅ 未发现"
fi

echo ""

# 4. 检查敏感文件
echo "🔍 检查敏感文件..."
SENSITIVE_FILES=0

if [ -f "$SKILL_PATH/.env" ]; then
  echo "  ⚠️  发现 .env 文件"
  if ! grep -q "^\.env$" "$SKILL_PATH/.gitignore" 2>/dev/null; then
    echo "    ❌ .env 未在 .gitignore 中"
    SENSITIVE_FILES=1
  else
    echo "    ✅ .env 已在 .gitignore 中"
  fi
fi

if [ -f "$SKILL_PATH/.secrets" ]; then
  echo "  ❌ 发现敏感文件：.secrets"
  SENSITIVE_FILES=1
fi

if ls "$SKILL_PATH"/*.key "$SKILL_PATH"/*.pem 2>/dev/null | grep -q .; then
  echo "  ❌ 发现密钥文件（.key 或 .pem）"
  SENSITIVE_FILES=1
fi

if [ $SENSITIVE_FILES -eq 0 ]; then
  echo "  ✅ 未发现敏感文件"
else
  FOUND_ISSUES=1
fi

echo ""

# 5. 检查环境变量硬编码
echo "🔍 检查环境变量硬编码..."
HARDCODED_VARS=0

EXPORT_RESULTS=$(grep -rn "export.*API_KEY\s*=\s*['\"]" "$SKILL_PATH" \
  --include="*.sh" 2>/dev/null | grep -vEi "$PLACEHOLDER_FILTER" || true)

if [ -n "$EXPORT_RESULTS" ]; then
  if echo "$EXPORT_RESULTS" | grep -vEi "(YOUR_|your_|PLACEHOLDER|EXAMPLE|xxx|REPLACEME)" | grep -qE "[a-zA-Z0-9]{30,}"; then
    echo "  ❌ 发现 export API_KEY=..."
    HARDCODED_VARS=1
  fi
fi

EXPORT_SECRET=$(grep -rn "export.*SECRET\s*=\s*['\"]" "$SKILL_PATH" \
  --include="*.sh" 2>/dev/null | grep -vEi "$PLACEHOLDER_FILTER" || true)

if [ -n "$EXPORT_SECRET" ]; then
  if echo "$EXPORT_SECRET" | grep -vEi "(YOUR_|your_|PLACEHOLDER|EXAMPLE|xxx)" | grep -qE "[a-zA-Z0-9]{30,}"; then
    echo "  ❌ 发现 export SECRET=..."
    HARDCODED_VARS=1
  fi
fi

if [ $HARDCODED_VARS -eq 0 ]; then
  echo "  ✅ 未发现硬编码的环境变量"
else
  FOUND_ISSUES=1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $FOUND_ISSUES -eq 0 ]; then
  echo "✅ 安全检查通过！"
  echo ""
  echo "该技能可以安全发布。"
  exit 0
else
  echo "❌ 安全检查失败！"
  echo ""
  echo "发现潜在的安全问题，请修复后重试："
  echo ""
  echo "  1. 将硬编码的密钥替换为环境变量"
  echo "  2. 使用占位符（如 YOUR_API_KEY_HERE, YOUR-TOKEN-HERE）"
  echo "  3. 确保敏感文件在 .gitignore 中"
  echo "  4. 撤销已泄露的密钥并重新生成"
  echo ""
  echo "示例："
  echo "  # ❌ 错误"
  echo "  export API_KEY=\"tvly-dev-4DmSfh-UaxhkHi4yxgNBVPyss1\""
  echo ""
  echo "  # ✅ 正确"
  echo "  API_KEY=\"\${API_KEY:-YOUR_API_KEY_HERE}\""
  echo ""
  exit 1
fi
