#!/bin/bash
# 添加用户脚本 (Linux / macOS)

cd "$(dirname "$0")/.."

# 激活虚拟环境（如果存在）
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
fi

python tools/gen_password.py
