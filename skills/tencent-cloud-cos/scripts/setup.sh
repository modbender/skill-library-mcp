#!/bin/bash
# 腾讯云 COS Skill 自动设置脚本
# 用法:
#   setup.sh --check-only                    仅检查环境状态
#   setup.sh --secret-id <ID> --secret-key <KEY> --region <REGION> --bucket <BUCKET> [--dataset <NAME>]

set -e

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }

# 获取脚本所在目录（skill baseDir）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ========== 检查函数 ==========

check_node() {
  if command -v node &>/dev/null; then
    ok "Node.js $(node --version)"
    return 0
  else
    fail "Node.js 未安装"
    return 1
  fi
}

check_npm() {
  if command -v npm &>/dev/null; then
    ok "npm $(npm --version)"
    return 0
  else
    fail "npm 未安装"
    return 1
  fi
}

check_mcporter() {
  if command -v mcporter &>/dev/null; then
    ok "mcporter $(mcporter --version 2>/dev/null || echo '已安装')"
    return 0
  else
    fail "mcporter 未安装"
    return 1
  fi
}

check_mcporter_config() {
  if [ -f ~/.mcporter/mcporter.json ]; then
    if grep -q '"cos-mcp"' ~/.mcporter/mcporter.json 2>/dev/null; then
      ok "mcporter 已配置 cos-mcp 服务器"
      return 0
    else
      warn "mcporter.json 存在但未配置 cos-mcp"
      return 1
    fi
  else
    fail "~/.mcporter/mcporter.json 不存在"
    return 1
  fi
}

check_cos_mcp() {
  if command -v npx &>/dev/null && npx cos-mcp --help &>/dev/null 2>&1; then
    ok "cos-mcp 可用"
    return 0
  else
    fail "cos-mcp 未安装或不可用"
    return 1
  fi
}

check_cos_sdk() {
  if node -e "require('cos-nodejs-sdk-v5')" &>/dev/null 2>&1; then
    ok "cos-nodejs-sdk-v5 已安装"
    return 0
  else
    fail "cos-nodejs-sdk-v5 未安装"
    return 1
  fi
}

check_coscmd() {
  if command -v coscmd &>/dev/null; then
    ok "coscmd 可用"
    return 0
  else
    warn "coscmd 未安装（可选）"
    return 1
  fi
}

check_env_vars() {
  local all_set=true
  for var in TENCENT_COS_SECRET_ID TENCENT_COS_SECRET_KEY TENCENT_COS_REGION TENCENT_COS_BUCKET; do
    if [ -n "${!var}" ]; then
      ok "$var 已设置"
    else
      fail "$var 未设置"
      all_set=false
    fi
  done
  $all_set
}

check_cos_conf() {
  if [ -f ~/.cos.conf ]; then
    ok "~/.cos.conf 已存在"
    return 0
  else
    warn "~/.cos.conf 不存在"
    return 1
  fi
}

# ========== 检查模式 ==========

do_check() {
  echo "=== 腾讯云 COS Skill 环境检查 ==="
  echo ""
  echo "--- 基础环境 ---"
  check_node || true
  check_npm || true
  echo ""
  echo "--- 方式一: cos-mcp MCP ---"
  check_mcporter || true
  check_mcporter_config || true
  check_cos_mcp || true
  echo ""
  echo "--- 方式二: Node.js SDK ---"
  check_cos_sdk || true
  check_env_vars || true
  echo ""
  echo "--- 方式三: COSCMD ---"
  check_coscmd || true
  check_cos_conf || true
  echo ""
  echo "--- Skill 文件 ---"
  [ -f "$BASE_DIR/SKILL.md" ] && ok "SKILL.md" || fail "SKILL.md 不存在"
  [ -f "$BASE_DIR/scripts/cos_node.mjs" ] && ok "scripts/cos_node.mjs" || fail "scripts/cos_node.mjs 不存在"
  [ -f "$BASE_DIR/references/config_template.json" ] && ok "references/config_template.json" || fail "references/config_template.json 不存在"
  echo ""
}

# ========== 设置模式 ==========

do_setup() {
  local SECRET_ID=""
  local SECRET_KEY=""
  local REGION=""
  local BUCKET=""
  local DATASET=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --secret-id)  SECRET_ID="$2"; shift 2;;
      --secret-key) SECRET_KEY="$2"; shift 2;;
      --region)     REGION="$2"; shift 2;;
      --bucket)     BUCKET="$2"; shift 2;;
      --dataset)    DATASET="$2"; shift 2;;
      *) shift;;
    esac
  done

  if [ -z "$SECRET_ID" ] || [ -z "$SECRET_KEY" ] || [ -z "$REGION" ] || [ -z "$BUCKET" ]; then
    echo "错误: 缺少必需参数"
    echo "用法: setup.sh --secret-id <ID> --secret-key <KEY> --region <REGION> --bucket <BUCKET> [--dataset <NAME>]"
    exit 1
  fi

  echo "=== 腾讯云 COS Skill 自动设置 ==="
  echo ""

  # 1. 检查 Node.js
  echo "--- 步骤 1: 检查 Node.js ---"
  if ! check_node; then
    fail "请先安装 Node.js: https://nodejs.org/"
    exit 1
  fi

  # 2. 确保 package.json 存在
  echo ""
  echo "--- 步骤 2: 初始化项目 ---"
  if [ ! -f "$BASE_DIR/package.json" ]; then
    (cd "$BASE_DIR" && npm init -y &>/dev/null)
    ok "已创建 package.json"
  else
    ok "package.json 已存在"
  fi

  # 3. 安装 cos-mcp、cos-nodejs-sdk-v5 和 mcporter
  echo ""
  echo "--- 步骤 3: 安装依赖 ---"
  (cd "$BASE_DIR" && npm install cos-mcp cos-nodejs-sdk-v5 --no-progress 2>&1 | tail -3)
  ok "cos-mcp + cos-nodejs-sdk-v5 安装完成"

  # 安装 mcporter（全局）
  if ! command -v mcporter &>/dev/null; then
    echo "正在安装 mcporter..."
    npm install -g mcporter --no-progress 2>&1 | tail -3
    if command -v mcporter &>/dev/null; then
      ok "mcporter 全局安装完成"
    else
      warn "mcporter 全局安装失败，尝试本地安装..."
      (cd "$BASE_DIR" && npm install mcporter --no-progress 2>&1 | tail -3)
      ok "mcporter 本地安装完成（使用 npx mcporter 调用）"
    fi
  else
    ok "mcporter 已安装"
  fi

  # 4. 写入环境变量到 shell 配置
  echo ""
  echo "--- 步骤 4: 持久化凭证 ---"

  # 判断 shell 配置文件
  local SHELL_RC=""
  if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ]; then
    SHELL_RC="$HOME/.zshrc"
  else
    SHELL_RC="$HOME/.bashrc"
  fi

  # 先清理旧的 COS 配置
  if [ -f "$SHELL_RC" ]; then
    sed -i.bak '/^# --- Tencent COS Skill ---$/,/^# --- End Tencent COS Skill ---$/d' "$SHELL_RC"
    rm -f "${SHELL_RC}.bak"
  fi

  # 写入新配置
  cat >> "$SHELL_RC" << EOF
# --- Tencent COS Skill ---
export TENCENT_COS_SECRET_ID="$SECRET_ID"
export TENCENT_COS_SECRET_KEY="$SECRET_KEY"
export TENCENT_COS_REGION="$REGION"
export TENCENT_COS_BUCKET="$BUCKET"
EOF

  if [ -n "$DATASET" ]; then
    sed -i.bak '/^# --- End Tencent COS Skill ---$/d' "$SHELL_RC"
    rm -f "${SHELL_RC}.bak"
    cat >> "$SHELL_RC" << EOF
export TENCENT_COS_DATASET_NAME="$DATASET"
EOF
  fi

  echo "# --- End Tencent COS Skill ---" >> "$SHELL_RC"

  ok "凭证已写入 $SHELL_RC"

  # 同时导出到当前 session
  export TENCENT_COS_SECRET_ID="$SECRET_ID"
  export TENCENT_COS_SECRET_KEY="$SECRET_KEY"
  export TENCENT_COS_REGION="$REGION"
  export TENCENT_COS_BUCKET="$BUCKET"
  [ -n "$DATASET" ] && export TENCENT_COS_DATASET_NAME="$DATASET"

  # 5. 配置 mcporter
  echo ""
  echo "--- 步骤 5: 配置 mcporter ---"
  local MCPORTER_DIR="$HOME/.mcporter"
  local MCPORTER_CONFIG="$MCPORTER_DIR/mcporter.json"

  mkdir -p "$MCPORTER_DIR"

  # 构建 cos-mcp 的 args 列表
  local COS_MCP_ARGS="\"cos-mcp\", \"--Region=$REGION\", \"--Bucket=$BUCKET\", \"--SecretId=$SECRET_ID\", \"--SecretKey=$SECRET_KEY\", \"--connectType=stdio\""
  if [ -n "$DATASET" ]; then
    COS_MCP_ARGS="\"cos-mcp\", \"--Region=$REGION\", \"--Bucket=$BUCKET\", \"--SecretId=$SECRET_ID\", \"--SecretKey=$SECRET_KEY\", \"--DatasetName=$DATASET\", \"--connectType=stdio\""
  fi

  if [ -f "$MCPORTER_CONFIG" ]; then
    # 已有配置文件，检查是否已配置 cos-mcp
    if grep -q '"cos-mcp"' "$MCPORTER_CONFIG" 2>/dev/null; then
      warn "mcporter.json 中已存在 cos-mcp 配置，将更新"
    fi
    # 使用 node 合并配置（保留其他 MCP 服务器配置）
    node -e "
      const fs = require('fs');
      const configPath = '$MCPORTER_CONFIG';
      let config = {};
      try { config = JSON.parse(fs.readFileSync(configPath, 'utf-8')); } catch(e) {}
      if (!config.mcpServers) config.mcpServers = {};
      config.mcpServers['cos-mcp'] = {
        command: 'npx',
        args: [$COS_MCP_ARGS]
      };
      fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    " 2>/dev/null
    ok "mcporter.json 已更新 cos-mcp 配置"
  else
    # 创建全新的配置文件
    cat > "$MCPORTER_CONFIG" << MCPEOF
{
  "mcpServers": {
    "cos-mcp": {
      "command": "npx",
      "args": [$COS_MCP_ARGS]
    }
  }
}
MCPEOF
    ok "mcporter.json 已创建"
  fi

  # 6. 配置 COSCMD（如果有 Python）
  echo ""
  echo "--- 步骤 6: 配置 COSCMD（可选） ---"
  if command -v pip3 &>/dev/null || command -v pip &>/dev/null; then
    local PIP_CMD
    PIP_CMD=$(command -v pip3 || command -v pip)
    $PIP_CMD install coscmd -q 2>/dev/null && \
    coscmd config -a "$SECRET_ID" -s "$SECRET_KEY" -b "$BUCKET" -r "$REGION" 2>/dev/null && \
    ok "coscmd 已配置" || \
    warn "coscmd 安装/配置失败（非关键）"
  else
    warn "Python/pip 未安装，跳过 coscmd"
  fi

  # 7. 验证
  echo ""
  echo "--- 步骤 7: 验证连接 ---"
  if (cd "$BASE_DIR" && node scripts/cos_node.mjs list --max-keys 1 2>/dev/null | grep -q '"success": true'); then
    ok "COS 连接验证成功"
  else
    warn "COS 连接验证失败，请检查凭证和网络"
  fi

  echo ""
  echo "=== 设置完成 ==="
  echo "现在可以使用以下方式操作 COS："
  echo "  方式一: mcporter call cos-mcp.<tool> --config ~/.mcporter/mcporter.json --output json"
  echo "  方式一(备选): cos-mcp MCP 工具（通过客户端直接调用）"
  echo "  方式二: node $BASE_DIR/scripts/cos_node.mjs <action>"
  echo "  方式三: coscmd <command>"
}

# ========== 主入口 ==========

case "$1" in
  --check-only)
    do_check
    ;;
  --secret-id|--secret-key|--region|--bucket)
    do_setup "$@"
    ;;
  *)
    echo "腾讯云 COS Skill 设置工具"
    echo ""
    echo "用法:"
    echo "  $0 --check-only"
    echo "    仅检查环境状态"
    echo ""
    echo "  $0 --secret-id <ID> --secret-key <KEY> --region <REGION> --bucket <BUCKET> [--dataset <NAME>]"
    echo "    自动设置环境（安装依赖 + 配置凭证 + 验证连接）"
    ;;
esac
