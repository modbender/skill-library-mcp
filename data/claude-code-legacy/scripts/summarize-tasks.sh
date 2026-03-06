#!/usr/bin/env bash
set -euo pipefail

# summarize-tasks.sh — Human heartbeat summary for cc tasks in a namespace.
# Output is designed to be posted to chat (non-technical, action-oriented).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIST_SCRIPT="$SCRIPT_DIR/list-tasks.sh"

SOCKET="${TMPDIR:-/tmp}/clawdbot-tmux-sockets/clawdbot.sock"
NAMESPACE=""
LINES_N=20

while [[ $# -gt 0 ]]; do
  case "$1" in
    --namespace) NAMESPACE="$2"; shift 2 ;;
    --socket) SOCKET="$2"; shift 2 ;;
    --lines) LINES_N="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

[[ -n "$NAMESPACE" ]] || { echo "Usage: $0 --namespace <chat_id> [--lines 20] [--socket path]"; exit 1; }

json="$({ bash "$LIST_SCRIPT" --json --namespace "$NAMESPACE" --socket "$SOCKET" --lines "$LINES_N"; } 2>/dev/null || echo '[]')"
count="$(echo "$json" | jq 'length')"
now_local="$(date '+%Y-%m-%d %H:%M:%S')"

printf "【Claude Code 巡检心跳】%s（群 %s）\n" "$now_local" "$NAMESPACE"

if [[ "$count" == "0" ]]; then
  echo
  echo "当前没有发现本群 namespace 下的 Claude Code 任务。"
  echo "你可以在启动任务时加：--namespace $NAMESPACE（否则巡检看不到）。"
  exit 0
fi

# Build buckets
running="$(echo "$json" | jq -r '[.[] | select(.status=="running") | .label] | join("\n")')"
idle="$(echo "$json" | jq -r '[.[] | select(.status=="idle") | .label] | join("\n")')"
stuck="$(echo "$json" | jq -r '[.[] | select(.status=="stuck") | .label] | join("\n")')"
doneish="$(echo "$json" | jq -r '[.[] | select(.status=="likely_done" or .status=="done_session_ended") | .label] | join("\n")')"
dead="$(echo "$json" | jq -r '[.[] | select(.status=="dead") | .label] | join("\n")')"

# Helper to print a concise list with 1-line context
print_list() {
  local title="$1"; shift
  local selector="$1"; shift

  echo
  echo "$title"
  echo "$json" | jq -r "$selector" | while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    echo "- $line"
  done
}

# 1) 每个进程在干嘛 + 现状
print_list "1) 进行中（正在跑）" '.[] | select(.status=="running") | "\(.label) — 运行中"'
print_list "2) 等待输入（可能卡在 Claude 提问/确认）" '.[] | select(.status=="idle") | "\(.label) — 等待你确认/继续"'
print_list "3) 已产出结果（待你 review/合并/发布）" '.[] | select(.status=="likely_done" or .status=="done_session_ended") | "\(.label) — 已完成（reportReady=\(.reportExists))"'
print_list "4) 异常/可能卡住" '.[] | select(.status=="stuck" or .status=="dead") | "\(.label) — \(.status)"'

# 3) 需要你做啥（聚合成一句话）
need_you=()
if [[ -n "$idle" ]]; then need_you+=("有任务在等待你输入（idle）"); fi
if [[ -n "$doneish" ]]; then need_you+=("有任务已完成，建议你选择要我先汇总哪个 report"); fi
if [[ -n "$stuck" || -n "$dead" ]]; then need_you+=("有任务疑似卡住/掉线，需要你决定是重跑还是我先拉日志定位"); fi

echo
echo "5) 需要你做的事"
if [[ ${#need_you[@]} -eq 0 ]]; then
  echo "- 暂时不需要你操作。"
else
  for x in "${need_you[@]}"; do echo "- $x"; done
fi

# 4) 关注点（只给非技术提醒）
# Simple heuristics based on status distribution
warn=()
if [[ -n "$stuck" ]]; then warn+=("存在卡住的任务：优先处理，避免无限占用时间"); fi
if [[ -n "$dead" ]]; then warn+=("存在会话已结束但未确认结果的任务：建议补看 report 或重跑"); fi

echo
echo "6) 需要关注的"
if [[ ${#warn[@]} -eq 0 ]]; then
  echo "- 暂无明显风险信号。"
else
  for w in "${warn[@]}"; do echo "- $w"; done
fi

echo
echo "备注：如需查看某个任务细节，回复我任务 label（例如：\"推送 <label>\"）。"
