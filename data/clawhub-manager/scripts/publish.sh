#!/bin/bash
# ClawHub 技能发布脚本
# 用法: ./publish.sh <skill-path> [options]

set -e

SKILL_PATH="$1"
shift

# 解析参数
VERSION=""
SLUG=""
NAME=""
CHANGELOG=""
SKIP_SECURITY=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --version)
      VERSION="$2"
      shift 2
      ;;
    --slug)
      SLUG="$2"
      shift 2
      ;;
    --name)
      NAME="$2"
      shift 2
      ;;
    --changelog)
      CHANGELOG="$2"
      shift 2
      ;;
    --skip-security)
      SKIP_SECURITY="yes"
      shift
      ;;
    *)
      echo "❌ 未知选项: $1"
      exit 1
      ;;
  esac
done

if [ -z "$SKILL_PATH" ]; then
  echo "❌ 错误：缺少技能路径"
  echo ""
  echo "用法: $0 <skill-path> [options]"
  echo ""
  echo "选项："
  echo "  --version <version>    版本号（必需）"
  echo "  --slug <slug>         技能 slug（可选）"
  echo "  --name <name>         显示名称（可选）"
  echo "  --changelog <text>    更新日志（可选）"
  echo "  --skip-security       跳过安全扫描（不推荐）"
  echo ""
  echo "示例："
  echo "  $0 /path/to/skill --version 1.0.0"
  echo "  $0 /path/to/skill --version 1.0.0 --changelog \"首次发布\""
  echo "  $0 /path/to/skill --slug my-skill --name \"My Skill\" --version 1.0.0"
  exit 1
fi

if [ -z "$VERSION" ]; then
  echo "❌ 错误：缺少版本号"
  echo "请使用 --version 参数指定版本号"
  exit 1
fi

if [ ! -d "$SKILL_PATH" ]; then
  echo "❌ 错误：技能路径不存在: $SKILL_PATH"
  exit 1
fi

echo "📦 发布技能到 ClawHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📂 路径: $SKILL_PATH"
echo "🏷️  版本: $VERSION"
[ -n "$SLUG" ] && echo "🔖 Slug: $SLUG"
[ -n "$NAME" ] && echo "📝 名称: $NAME"
[ -n "$CHANGELOG" ] && echo "📋 更新: $CHANGELOG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 安全扫描函数
security_scan() {
  local skill_path="$1"
  local found_issues=0
  
  echo "🔒 执行安全扫描..."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  # 定义占位符模式 - 包含所有常见的占位符
  local placeholder_filter='YOUR_|YOUR-|your_|your-|PLACEHOLDER|placeholder|EXAMPLE|example|XXX|xxx|REPLACEME|replaceme'
  
  # 1. 检查硬编码的 API 密钥（常见格式）
  echo "🔍 检查硬编码密钥..."
  
  # Tavily API Key - 更智能的检测
  local tavily_results=$(grep -rn "tvly-[A-Za-z0-9]" "$skill_path" \
    --include="*.md" --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
    grep -vE "$placeholder_filter" || true)
  
  if [ -n "$tavily_results" ]; then
    # 进一步过滤：检查是否看起来像真实的密钥（长度和格式）
    if echo "$tavily_results" | grep -vE "tvly-(YOUR_|YOUR-|your_|your-|XXX|PLACE|EXAMPLE)" | grep -qE "tvly-[a-zA-Z0-9]{20,}"; then
      echo "❌ 发现 Tavily API 密钥"
      found_issues=1
    fi
  fi
  
  # OpenAI API Key
  local openai_results=$(grep -rn "sk-[a-zA-Z0-9]" "$skill_path" \
    --include="*.md" --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
    grep -vE "$placeholder_filter" || true)
  
  if [ -n "$openai_results" ]; then
    if echo "$openai_results" | grep -qE "sk-[a-zA-Z0-9]{48}"; then
      echo "❌ 发现 OpenAI API 密钥"
      found_issues=1
    fi
  fi
  
  # GitHub Tokens (多种类型)
  local github_results=$(grep -rn "gh[puos]_[a-zA-Z0-9]" "$skill_path" \
    --include="*.md" --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
    grep -vE "$placeholder_filter" || true)
  
  if [ -n "$github_results" ]; then
    if echo "$github_results" | grep -qE "gh[puos]_[a-zA-Z0-9]{36}"; then
      echo "❌ 发现 GitHub Token"
      found_issues=1
    fi
  fi
  
  # Perplexity API Key
  local perplexity_results=$(grep -rn "pplx-[a-zA-Z0-9]" "$skill_path" \
    --include="*.md" --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
    grep -vE "$placeholder_filter" || true)
  
  if [ -n "$perplexity_results" ]; then
    if echo "$perplexity_results" | grep -qE "pplx-[a-zA-Z0-9]{43}"; then
      echo "❌ 发现 Perplexity API 密钥"
      found_issues=1
    fi
  fi
  
  # Exa AI API Key
  local exa_results=$(grep -rn "exa_[a-zA-Z0-9]" "$skill_path" \
    --include="*.md" --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
    grep -vE "$placeholder_filter" || true)
  
  if [ -n "$exa_results" ]; then
    if echo "$exa_results" | grep -qE "exa_[a-zA-Z0-9]{32}"; then
      echo "❌ 发现 Exa AI API 密钥"
      found_issues=1
    fi
  fi
  
  # 通用 API Key 模式 - 更严格的检测
  local generic_key_results=$(grep -rni "api[_-]?key\s*[=:]\s*['\"]?[a-zA-Z0-9/_-]{20,}" "$skill_path" \
    --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
    grep -vEi "$placeholder_filter" || true)
  
  if [ -n "$generic_key_results" ]; then
    # 排除明显的占位符和示例
    if echo "$generic_key_results" | grep -vEi "(YOUR_|your_|PLACEHOLDER|EXAMPLE|xxx|REPLACEME)" | grep -qE "[a-zA-Z0-9/_-]{30,}"; then
      echo "❌ 发现疑似 API Key（通用模式）"
      found_issues=1
    fi
  fi
  
  # 2. 检查 App Secret
  echo "🔍 检查 App Secret..."
  
  local secret_results=$(grep -rni "app[_-]?secret\s*[=:]\s*['\"]?[a-zA-Z0-9]{20,}" "$skill_path" \
    --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
    grep -vEi "$placeholder_filter" || true)
  
  if [ -n "$secret_results" ]; then
    if echo "$secret_results" | grep -vEi "(YOUR_|your_|PLACEHOLDER|EXAMPLE|xxx)" | grep -qE "[a-zA-Z0-9]{30,}"; then
      echo "❌ 发现疑似 App Secret"
      found_issues=1
    fi
  fi
  
  # 3. 检查 Access Token
  echo "🔍 检查 Access Token..."
  
  local token_results=$(grep -rni "access[_-]?token\s*[=:]\s*['\"]?[a-zA-Z0-9]{20,}" "$skill_path" \
    --include="*.sh" --include="*.py" --include="*.js" 2>/dev/null | \
    grep -vEi "$placeholder_filter" || true)
  
  if [ -n "$token_results" ]; then
    if echo "$token_results" | grep -vEi "(YOUR_|your_|PLACEHOLDER|EXAMPLE|xxx)" | grep -qE "[a-zA-Z0-9]{30,}"; then
      echo "❌ 发现疑似 Access Token"
      found_issues=1
    fi
  fi
  
  # 4. 检查敏感文件
  echo "🔍 检查敏感文件..."
  
  if [ -f "$skill_path/.env" ]; then
    if ! grep -q "^\.env$" "$skill_path/.gitignore" 2>/dev/null; then
      echo "⚠️  警告：发现 .env 文件，但未在 .gitignore 中"
      found_issues=1
    fi
  fi
  
  if [ -f "$skill_path/.secrets" ]; then
    echo "❌ 发现敏感文件：.secrets"
    found_issues=1
  fi
  
  if ls "$skill_path"/*.key "$skill_path"/*.pem 2>/dev/null | grep -q .; then
    echo "❌ 发现密钥文件（.key 或 .pem）"
    found_issues=1
  fi
  
  # 5. 检查环境变量硬编码
  echo "🔍 检查环境变量硬编码..."
  
  local export_results=$(grep -rn "export.*API_KEY\s*=\s*['\"]" "$skill_path" \
    --include="*.sh" 2>/dev/null | grep -vEi "$placeholder_filter" || true)
  
  if [ -n "$export_results" ]; then
    # 检查是否是真实的密钥（长字符串）
    if echo "$export_results" | grep -vEi "(YOUR_|your_|PLACEHOLDER|EXAMPLE|xxx|REPLACEME)" | grep -qE "[a-zA-Z0-9]{30,}"; then
      echo "❌ 发现硬编码的环境变量（export API_KEY=）"
      found_issues=1
    fi
  fi
  
  local export_secret=$(grep -rn "export.*SECRET\s*=\s*['\"]" "$skill_path" \
    --include="*.sh" 2>/dev/null | grep -vEi "$placeholder_filter" || true)
  
  if [ -n "$export_secret" ]; then
    if echo "$export_secret" | grep -vEi "(YOUR_|your_|PLACEHOLDER|EXAMPLE|xxx)" | grep -qE "[a-zA-Z0-9]{30,}"; then
      echo "❌ 发现硬编码的环境变量（export SECRET=）"
      found_issues=1
    fi
  fi
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if [ $found_issues -eq 0 ]; then
    echo "✅ 安全扫描通过"
    echo ""
    return 0
  else
    echo ""
    echo "❌ 安全扫描失败！发现潜在的安全问题"
    echo ""
    echo "请修复以下问题后重试："
    echo "  1. 将硬编码的密钥替换为环境变量"
    echo "  2. 使用占位符（如 YOUR_API_KEY_HERE, YOUR-TOKEN-HERE）"
    echo "  3. 确保敏感文件在 .gitignore 中"
    echo "  4. 撤销已泄露的密钥并重新生成"
    echo ""
    echo "如需跳过安全扫描（不推荐），使用 --skip-security 参数"
    return 1
  fi
}

# 执行安全扫描（除非显式跳过）
if [ "$SKIP_SECURITY" != "yes" ]; then
  if ! security_scan "$SKILL_PATH"; then
    echo "⚠️  发布已取消"
    exit 1
  fi
else
  echo "⚠️  警告：已跳过安全扫描（--skip-security）"
  echo ""
fi

# 构建发布命令
PUBLISH_CMD=(clawhub publish "$SKILL_PATH" --version "$VERSION")
[ -n "$SLUG" ] && PUBLISH_CMD+=(--slug "$SLUG")
[ -n "$NAME" ] && PUBLISH_CMD+=(--name "$NAME")
[ -n "$CHANGELOG" ] && PUBLISH_CMD+=(--changelog "$CHANGELOG")

# 执行发布
"${PUBLISH_CMD[@]}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 发布成功！"
echo ""
echo "💡 提示："
echo "  - 使用 inspect.sh 查看技能信息"
echo "  - 技能可能需要几分钟才能在搜索结果中出现"
