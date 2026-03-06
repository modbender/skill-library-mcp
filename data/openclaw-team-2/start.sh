#!/bin/bash

# OpenClaw Team 启动脚本

echo "🚀 正在启动 OpenClaw Team..."

# 检查是否有虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "✅ 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -q -r requirements.txt

# 加载环境变量（如果存在 .env 文件）
if [ -f .env ]; then
    echo "🔧 加载环境变量..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# 启动服务器
echo "🌐 启动服务器..."
cd scripts
python3 main.py
