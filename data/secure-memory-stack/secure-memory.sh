#!/bin/bash
# 入口点脚本 - 安全记忆系统

# 检查是否提供了命令
if [ $# -eq 0 ]; then
    echo "🛡️  安全记忆系统 (Secure Memory Stack)"
    echo "   一个完全本地化的记忆系统，确保数据隐私和安全"
    echo ""
    echo "用法: secure-memory <command> [options]"
    echo ""
    echo "快速开始:"
    echo "  secure-memory setup          # 初始化系统"
    echo "  secure-memory status         # 检查系统状态"
    echo "  secure-memory search <query> # 搜索记忆"
    echo ""
    echo "更多信息: secure-memory help"
    exit 0
fi

# 调用主脚本
bash /root/clawd/create/secure-memory-stack/scripts/secure-memory.sh "$@"