#!/bin/bash
# Mini TimeBot 启动脚本（直接启动服务，跳过环境配置）
# 实际启动逻辑统一由 launcher.py 管理

cd "$(dirname "$0")/.."

# 激活虚拟环境（如果存在）
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
fi

# 调用 Python 启动器
exec python scripts/launcher.py
