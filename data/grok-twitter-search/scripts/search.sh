#!/bin/bash
# Grok Twitter Search - OpenClaw 包装脚本
# 自动检测代理并执行搜索

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 加载环境（自动检测 WARP）
eval "$($SCRIPT_DIR/setup_env.sh)"

# 执行搜索
uv run "$SCRIPT_DIR/search_twitter.py" "$@"
