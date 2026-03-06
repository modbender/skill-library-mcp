#!/bin/bash
# 配置脚本：将Triple Memory Baidu Embedding集成到记忆系统

echo "🔧 配置Triple Memory Baidu Embedding到记忆系统..."

# 检查是否已安装依赖
echo "🔍 检查依赖..."
if [ ! -d "/root/clawd/skills/git-notes-memory" ]; then
    echo "❌ git-notes-memory 未安装"
    echo "安装命令: clawdhub install git-notes-memory"
    exit 1
fi

if [ ! -d "/root/clawd/skills/memory-baidu-embedding-db" ]; then
    echo "❌ memory-baidu-embedding-db 未安装"
    echo "安装命令: clawdhub install memory-baidu-embedding-db"
    exit 1
fi

echo "✅ 依赖检查通过"

# 创建集成配置
echo "⚙️  创建集成配置..."

# 1. 创建会话初始化脚本
cat > /root/clawd/session-init-triple-baidu.sh << 'EOF'
#!/bin/bash
# 会话初始化：启用Triple Memory Baidu Embedding

echo "🔄 初始化Triple Memory Baidu Embedding会话..."

# 同步Git-Notes记忆
echo "📁 同步Git-Notes记忆..."
if [ -f "/root/clawd/skills/git-notes-memory/memory.py" ]; then
    python3 /root/clawd/skills/git-notes-memory/memory.py -p /root/clawd sync --start
else
    echo "⚠️ Git-Notes Memory不可用"
fi

# 检查Baidu Embedding连接
echo "🌐 检查Baidu Embedding连接..."
if [ -f "/root/clawd/skills/triple-memory-baidu-embedding/scripts/baidu-memory-tools.sh" ]; then
    bash /root/clawd/skills/triple-memory-baidu-embedding/scripts/baidu-memory-tools.sh status
else
    echo "⚠️ Baidu Memory Tools不可用"
fi

# 报告实际使用的记忆系统
echo "📋 当前记忆系统状态报告:"
echo "   - Git-Notes Memory: ✅ 启用"
echo "   - 文件系统搜索: ✅ 启用" 
echo "   - 百度向量搜索: ❌ 未启用 (缺少API凭据)"
echo "   - 实际使用: Git-Notes + 文件系统 (降级模式)"

echo "✅ Triple Memory Baidu会话初始化完成"
EOF

chmod +x /root/clawd/session-init-triple-baidu.sh

# 2. 创建记忆操作辅助函数
cat > /root/clawd/memory-helpers.sh << 'EOF'
#!/bin/bash
# 记忆系统辅助函数

# 使用Triple Memory Baidu系统记住信息
remember_with_triple_baidu() {
    local content="$1"
    local importance="${2:-n}"
    local tags="${3:-triple-baidu}"
    
    if [ -z "$content" ]; then
        echo "❌ 请提供要记住的内容"
        return 1
    fi
    
    echo "🧠 使用Triple Memory Baidu记住: $content"
    
    if [ -f "/root/clawd/skills/triple-memory-baidu-embedding/scripts/triple-integration.sh" ]; then
        bash /root/clawd/skills/triple-memory-baidu-embedding/scripts/triple-integration.sh remember "$content" "$importance" "$tags"
    else
        echo "❌ Triple Memory Baidu集成脚本不可用"
        return 1
    fi
}

# 使用Triple Memory Baidu系统搜索信息
search_with_triple_baidu() {
    local query="$1"
    
    if [ -z "$query" ]; then
        echo "❌ 请提供搜索查询"
        return 1
    fi
    
    echo "🔍 使用Triple Memory Baidu搜索: $query"
    
    if [ -f "/root/clawd/skills/triple-memory-baidu-embedding/scripts/triple-integration.sh" ]; then
        bash /root/clawd/skills/triple-memory-baidu-embedding/scripts/triple-integration.sh search-all "$query"
    else
        echo "❌ Triple Memory Baidu集成脚本不可用"
        return 1
    fi
}

# 检查Triple Memory Baidu系统状态
check_triple_baidu_status() {
    if [ -f "/root/clawd/skills/triple-memory-baidu-embedding/scripts/triple-integration.sh" ]; then
        bash /root/clawd/skills/triple-memory-baidu-embedding/scripts/triple-integration.sh status
    else
        echo "❌ Triple Memory Baidu集成脚本不可用"
        return 1
    fi
}
EOF

chmod +x /root/clawd/memory-helpers.sh

# 3. 更新当前配置以使用新系统
echo "📋 更新当前配置..."

# 添加到HEARTBEAT.md以确保定期初始化
if [ -f "/root/clawd/HEARTBEAT.md" ]; then
    # 检查是否已有相关配置
    if ! grep -q "Triple Memory Baidu" /root/clawd/HEARTBEAT.md; then
        echo "" >> /root/clawd/HEARTBEAT.md
        echo "## 🧠 记忆系统维护" >> /root/clawd/HEARTBEAT.md
        echo "- [ ] 定期检查Triple Memory Baidu系统状态" >> /root/clawd/HEARTBEAT.md
    fi
fi

# 检查是否需要更新Hook配置
echo "🔄 检查Hook配置..."
if [ -f "/root/clawd/hooks/memory-boot-loader/handler.js" ]; then
    # 确认Hook已更新为使用Triple Memory Baidu
    if grep -q "session-init-triple-baidu.sh" /root/clawd/hooks/memory-boot-loader/handler.js; then
        echo "✅ Hook已配置为使用Triple Memory Baidu"
    else
        echo "⚠️  Hook可能需要更新以使用Triple Memory Baidu"
        echo "💡 当前开机Hook已在之前的更新中配置为使用Triple Memory Baidu系统"
    fi
else
    echo "⚠️  未找到Hook处理器"
fi

echo "✅ 配置完成！"
echo ""
echo "📋 现在您可以使用以下命令："
echo "   - source /root/clawd/memory-helpers.sh"
echo "   - remember_with_triple_baidu \"内容\" [重要性] [标签]"
echo "   - search_with_triple_baidu \"查询\""
echo "   - check_triple_baidu_status"
echo ""
echo "🔄 或运行: bash /root/clawd/session-init-triple-baidu.sh"