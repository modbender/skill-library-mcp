#!/bin/bash
# OKX Exchange Skill — Cron job manager (openclaw cron)
#
# Usage:
#   bash cron_setup.sh setup [sl_tp_interval] [scan_interval]
#   bash cron_setup.sh teardown
#   bash cron_setup.sh status
#
# Examples:
#   bash cron_setup.sh setup          # defaults: sl-tp=5m, scan=30m
#   bash cron_setup.sh setup 1m       # sl-tp=1m, scan=30m
#   bash cron_setup.sh setup 10m 1h   # sl-tp=10m, scan=1h

CMD=${1:-"setup"}
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "$CMD" = "setup" ]; then
    SLTP_INTERVAL=${2:-"5m"}
    SCAN_INTERVAL=${3:-"30m"}

    echo "Setting up OKX trading cron jobs..."
    echo "  okx-sl-tp : every ${SLTP_INTERVAL}"
    echo "  okx-scan  : every ${SCAN_INTERVAL}"

    # Job 1: Snapshot + Stop-loss / Take-profit check
    openclaw cron add \
      --every "${SLTP_INTERVAL}" \
      --name "okx-sl-tp" \
      --target isolated \
      --message "你是 OKX 交易监控 Agent。执行以下命令并将输出原文发送，不要增删任何内容：

source ~/.openclaw/workspace/.env
cd ${SCRIPTS_DIR}
python3 okx.py snapshot
python3 okx.py monitor sl-tp

将两条命令的实际输出合并后发送。如果命令报错，直接报告错误原文。不要主动调用任何发送工具。"

    # Job 2: Strategy scan
    openclaw cron add \
      --every "${SCAN_INTERVAL}" \
      --name "okx-scan" \
      --target isolated \
      --message "你是 OKX 策略扫描 Agent。执行以下命令并将输出原文发送：

source ~/.openclaw/workspace/.env
cd ${SCRIPTS_DIR}
python3 okx.py monitor scan

将命令的实际输出发送。如果没有信号则发送'无交易信号'。如果命令报错，直接报告错误原文。不要主动调用任何发送工具。"

    echo ""
    echo "✅ Cron jobs added:"
    openclaw cron list 2>/dev/null | grep okx

elif [ "$CMD" = "teardown" ]; then
    echo "Removing OKX cron jobs..."
    openclaw cron list 2>/dev/null | grep okx | awk '{print $1}' | while read id; do
        openclaw cron rm "$id" 2>/dev/null && echo "  Removed: $id"
    done
    echo "✅ Done."

elif [ "$CMD" = "status" ]; then
    echo "Active OKX cron jobs:"
    openclaw cron list 2>/dev/null | grep -E "okx|ID" || echo "  (none)"

else
    echo "Usage: $0 [setup|teardown|status] [sl_tp_interval] [scan_interval]"
    echo ""
    echo "Examples:"
    echo "  $0 setup           # defaults: sl-tp=5m, scan=30m"
    echo "  $0 setup 1m        # sl-tp=1m, scan=30m"
    echo "  $0 setup 10m 1h    # sl-tp=10m, scan=1h"
fi
