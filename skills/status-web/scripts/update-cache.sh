#!/bin/bash
# 小雨 Bot 状态监测页面缓存更新脚本

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
ASSETS_DIR="$SKILL_DIR/assets"

echo "正在获取最新状态数据..."

# 使用 Python 脚本获取状态数据并保存到缓存文件
python3 << EOF
import json
import requests
import datetime
import sys
import os

# 添加 OpenClaw 工作目录到 Python 路径
sys.path.insert(0, '/home/admin/openclaw/workspace')

try:
    # 从本地 API 获取数据
    response = requests.get('http://localhost:18789/api/status', timeout=10)
    response.raise_for_status()
    data = response.json()
    
    # 添加最后更新时间
    data['last_updated'] = datetime.datetime.now().isoformat()
    
    # 保存到缓存文件
    cache_file = os.path.join('$ASSETS_DIR', 'status-cache.json')
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"缓存更新成功: {datetime.datetime.now().strftime('%c')}")
    
except Exception as e:
    print(f"缓存更新失败: {e}", file=sys.stderr)
    sys.exit(1)
EOF