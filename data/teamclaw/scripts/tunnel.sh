#!/bin/bash
# Cloudflare Tunnel 公网部署（独立使用）
# 用法: bash scripts/tunnel.sh

PROJECT_ROOT="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
cd "$PROJECT_ROOT"

# 激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

python scripts/tunnel.py
