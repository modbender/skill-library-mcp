#!/bin/bash
# Free Search Aggregator - 默认搜索入口
# 用法: fsearch "查询内容"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

export PYTHONPATH="${ROOT_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}"

# 从环境变量读取 API Keys
export BRAVE_API_KEY="${BRAVE_API_KEY:-}"
export TAVILY_API_KEY="${TAVILY_API_KEY:-}"
export SERPER_API_KEY="${SERPER_API_KEY:-}"
export SEARCHAPI_API_KEY="${SEARCHAPI_API_KEY:-}"

exec python3 -m free_search "$@"
