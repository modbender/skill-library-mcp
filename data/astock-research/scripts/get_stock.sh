#!/bin/bash
# A股行情查询脚本

CODE=$1
if [ -z "$CODE" ]; then
    echo "用法: ./get_stock.sh <股票代码>"
    echo "示例: ./get_stock.sh 000001.SZ"
    exit 1
fi

echo "=== 查询 $CODE 实时行情 ==="
export QVERIS_API_KEY=sk-XVkZepqEZYvLIDHkm_uB3za58x1gUjIb1_jwE8LP_V4

~/.local/bin/uv run /home/ubuntu/.openclaw/workspace/skills/qveris/scripts/qveris_tool.py execute ths_ifind.real_time_quotation.v1 \
  --search-id "9869fb66-3bc7-4c4d-854f-4bedc22d3b10" \
  --params "{\"codes\": \"$CODE\"}" 2>&1
