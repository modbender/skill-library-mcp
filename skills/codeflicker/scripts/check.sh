#!/bin/bash
# 检查 flickcli 是否已安装

if command -v flickcli &> /dev/null; then
    echo "✅ CodeFlicker CLI 已安装"
    flickcli --version
    echo ""
    echo "位置: $(which flickcli)"
else
    echo "❌ CodeFlicker CLI 未安装"
    echo ""
    echo "安装方法:"
    echo "  npm install -g @ks-codeflicker/cli"
    echo "  或"
    echo "  pnpm add -g @ks-codeflicker/cli"
fi