#!/bin/bash
# Query Sparkle VPN status and current node

API_URL="http://127.0.0.1:9090"

# Check if mihomo is running
if ! pgrep -f "mihomo" > /dev/null; then
    echo "❌ VPN 未运行"
    exit 1
fi

# Get current proxy info
echo "🔍 查询 VPN 状态..."
echo ""

# Get DirectACCESS selector info
curl -s "${API_URL}/proxies/DirectACCESS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    current = data.get('now', '未知')
    all_nodes = data.get('all', [])
    
    print(f'当前策略组: DirectACCESS')
    print(f'当前节点: {current}')
    print(f'可用节点数: {len(all_nodes)}')
    print('')
    print('可选节点列表:')
    for i, node in enumerate(all_nodes[:20], 1):  # 显示前20个
        prefix = '  ▶' if node == current else '   '
        print(f'{prefix} {node}')
    if len(all_nodes) > 20:
        print(f'   ... 还有 {len(all_nodes) - 20} 个节点')
except Exception as e:
    print(f'解析失败: {e}')
"

echo ""
echo "💡 使用 switch-node 工具切换节点"
