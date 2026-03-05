#!/usr/bin/env bash
set -euo pipefail

LABEL=""
NAMESPACE=""
WORKDIR=""
PROMPT_FILE=""
TASK=""
LINT_CMD="npm run lint"
BUILD_CMD="npm run build"

TARGET="local"            # local | ssh
SSH_HOST=""               # required when TARGET=ssh
MINI_HOST="mini"          # ssh alias for the Mac mini (used for scp + wake callback)
SOCKET_OVERRIDE=""        # optional custom socket path (mostly for local)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --label) LABEL="$2"; shift 2 ;;
    --namespace) NAMESPACE="$2"; shift 2 ;;
    --workdir) WORKDIR="$2"; shift 2 ;;
    --prompt-file) PROMPT_FILE="$2"; shift 2 ;;
    --task) TASK="$2"; shift 2 ;;

    --target) TARGET="$2"; shift 2 ;;
    --ssh-host) SSH_HOST="$2"; shift 2 ;;
    --mini-host) MINI_HOST="$2"; shift 2 ;;
    --socket) SOCKET_OVERRIDE="$2"; shift 2 ;;
    --lint-cmd) LINT_CMD="$2"; shift 2 ;;
    --build-cmd) BUILD_CMD="$2"; shift 2 ;;

    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

[[ -n "$LABEL" && -n "$WORKDIR" && -n "$PROMPT_FILE" && -n "$TASK" ]] || {
  echo "Usage: $0 --label <label> [--namespace <ns>] --workdir <dir> --prompt-file <file> --task <text> [--target local|ssh --ssh-host <alias> --mini-host <alias>]"
  exit 1
}

if [[ "$TARGET" == "ssh" && -z "$SSH_HOST" ]]; then
  echo "ERROR: --target ssh requires --ssh-host <alias>"
  exit 2
fi

SOCKET_DIR="${TMPDIR:-/tmp}/clawdbot-tmux-sockets"
SOCKET_DEFAULT="$SOCKET_DIR/clawdbot.sock"
SOCKET="${SOCKET_OVERRIDE:-$SOCKET_DEFAULT}"
SESSION="cc-${LABEL}"
if [[ -n "$NAMESPACE" ]]; then
  SESSION="cc-${NAMESPACE}-${LABEL}"
fi
mkdir -p "$SOCKET_DIR"

PROMPT_TMP="/tmp/${SESSION}-prompt.txt"
REPORT_JSON="/tmp/${SESSION}-completion-report.json"
REPORT_MD="/tmp/${SESSION}-completion-report.md"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAKE_SCRIPT="$SCRIPT_DIR/wake.sh"

# Wake instructions differ for local vs remote execution.
WAKE_INSTRUCTIONS="bash \"$WAKE_SCRIPT\" \"Claude Code done (${LABEL}) report=$REPORT_JSON\" now"
if [[ "$TARGET" == "ssh" ]]; then
  WAKE_INSTRUCTIONS=$(cat <<EOF
# 1) 把报告文件复制回 Mac mini（本机）
scp -q "$REPORT_JSON" "${MINI_HOST}:$REPORT_JSON"
scp -q "$REPORT_MD" "${MINI_HOST}:$REPORT_MD"

# 2) 在 Mac mini 上触发 wake（只允许最后一步做）
ssh "$MINI_HOST" 'bash "$WAKE_SCRIPT" "Claude Code done (${LABEL}) report=$REPORT_JSON" now'
EOF
)
fi

# Guardrail: fail fast if old wake syntax appears
if rg -n "openclaw\s+gateway\s+wake\s+--text" "$PROMPT_FILE" >/dev/null 2>&1 || echo "$TASK" | rg -n "openclaw\s+gateway\s+wake\s+--text" >/dev/null 2>&1; then
  echo "ERROR: Detected deprecated wake command: 'openclaw gateway wake --text ...'"
  echo "Use: bash $WAKE_SCRIPT \"...\" now"
  exit 2
fi

tmux_cmd() {
  if [[ "$TARGET" == "ssh" ]]; then
    ssh -o BatchMode=yes "$SSH_HOST" "$@"
  else
    bash -lc "$*"
  fi
}

tmux_capture() {
  if [[ "$TARGET" == "ssh" ]]; then
    ssh -o BatchMode=yes "$SSH_HOST" "$@"
  else
    bash -lc "$*"
  fi
}

# Ensure socket dir exists on target
if [[ "$TARGET" == "ssh" ]]; then
  ssh -o BatchMode=yes "$SSH_HOST" "mkdir -p '$SOCKET_DIR'"
fi

# Kill old session if exists
if [[ "$TARGET" == "ssh" ]]; then
  if ssh -o BatchMode=yes "$SSH_HOST" "tmux -S '$SOCKET' has-session -t '$SESSION'" >/dev/null 2>&1; then
    ssh -o BatchMode=yes "$SSH_HOST" "tmux -S '$SOCKET' kill-session -t '$SESSION'"
  fi
else
  if tmux -S "$SOCKET" has-session -t "$SESSION" 2>/dev/null; then
    tmux -S "$SOCKET" kill-session -t "$SESSION"
  fi
fi

# If running remotely, copy the reference doc to remote /tmp so Claude can access it.
REF_PATH="$PROMPT_FILE"
REMOTE_REF="/tmp/${SESSION}-reference-$(basename "$PROMPT_FILE" | sed 's/[^a-zA-Z0-9._-]/_/g')"

if [[ "$TARGET" == "ssh" ]]; then
  scp -q "$PROMPT_FILE" "${SSH_HOST}:${REMOTE_REF}"
  REF_PATH="$REMOTE_REF"
fi

# Build dynamic quality gates
QUALITY_GATES="1) git status --short
2) git diff --name-only
3) git diff --stat"
GATE_NUM=4

if [[ -n "$LINT_CMD" ]]; then
  QUALITY_GATES="${QUALITY_GATES}
${GATE_NUM}) ${LINT_CMD}"
  GATE_NUM=$((GATE_NUM + 1))
fi

if [[ -n "$BUILD_CMD" ]]; then
  QUALITY_GATES="${QUALITY_GATES}
${GATE_NUM}) ${BUILD_CMD}"
fi

# Build lint/build JSON hints for the prompt
if [[ -n "$LINT_CMD" ]]; then
  LINT_JSON_HINT='"lint": {"ok": true/false, "summary": "..."}'
else
  LINT_JSON_HINT='"lint": {"ok": true, "summary": "skipped"}'
fi

if [[ -n "$BUILD_CMD" ]]; then
  BUILD_JSON_HINT='"build": {"ok": true/false, "summary": "..."}'
else
  BUILD_JSON_HINT='"build": {"ok": true, "summary": "skipped"}'
fi

cat > "$PROMPT_TMP" <<EOF
请在当前项目执行以下任务：
参考文档：$REF_PATH
任务要求：$TASK

【强制交付协议（必须逐条执行）】
A. 完成开发后，立刻执行并收集结果：
$QUALITY_GATES

B. 将交付报告写入以下两个文件：
- JSON: $REPORT_JSON
- Markdown: $REPORT_MD

JSON 结构必须包含：
{
  "label": "${LABEL}",
  "workdir": "${WORKDIR}",
  "changedFiles": [...],
  "diffStat": "...",
  $LINT_JSON_HINT,
  $BUILD_JSON_HINT,
  "risk": "low|medium|high",
  "scopeDrift": true/false,
  "recommendation": "keep|partial_rollback|rollback",
  "notes": "..."
}

C. 最后一步才允许发 wake（必须使用封装脚本，不要直接写 gateway 子命令）：
$WAKE_INSTRUCTIONS

禁止只发 wake 不产出报告。wake 是交付触发器，不是交付本身。
EOF

# Put prompt file on target (so we can paste it reliably)
if [[ "$TARGET" == "ssh" ]]; then
  scp -q "$PROMPT_TMP" "${SSH_HOST}:${PROMPT_TMP}"
fi

# Start tmux + claude interactive
if [[ "$TARGET" == "ssh" ]]; then
  ssh -o BatchMode=yes "$SSH_HOST" "tmux -S '$SOCKET' new -d -s '$SESSION' -n shell"
  ssh -o BatchMode=yes "$SSH_HOST" "tmux -S '$SOCKET' send-keys -t '$SESSION':0.0 -l -- 'cd $WORKDIR && export https_proxy=http://127.0.0.1:6152 http_proxy=http://127.0.0.1:6152 all_proxy=socks5://127.0.0.1:6153 && claude --dangerously-skip-permissions'"
  ssh -o BatchMode=yes "$SSH_HOST" "tmux -S '$SOCKET' send-keys -t '$SESSION':0.0 Enter"
else
  tmux -S "$SOCKET" new -d -s "$SESSION" -n shell
  tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -l -- "cd $WORKDIR && export https_proxy=http://127.0.0.1:6152 http_proxy=http://127.0.0.1:6152 all_proxy=socks5://127.0.0.1:6153 && claude --dangerously-skip-permissions"
  tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 Enter
fi

# Wait until Claude UI is ready before paste
ready=false
for _ in {1..30}; do
  if [[ "$TARGET" == "ssh" ]]; then
    pane="$(ssh -o BatchMode=yes "$SSH_HOST" "tmux -S '$SOCKET' capture-pane -p -J -t '$SESSION':0.0 -S -60" || true)"
  else
    pane="$(tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -60 || true)"
  fi
  if echo "$pane" | rg -q "bypass permissions on|Try \"fix lint errors\"|Welcome back"; then
    ready=true
    break
  fi
  sleep 1
done

if [[ "$ready" != true ]]; then
  echo "WARN: Claude UI not confirmed ready in 30s; still trying prompt submit"
fi

# Paste prompt
if [[ "$TARGET" == "ssh" ]]; then
  prompt_text="$(cat "$PROMPT_TMP")"
  ssh -o BatchMode=yes "$SSH_HOST" "tmux -S '$SOCKET' send-keys -t '$SESSION':0.0 -l -- $(python3 - <<'PY'
import shlex,sys
s=sys.stdin.read()
print(shlex.quote(s))
PY
<<<"$prompt_text")"
else
  prompt_text="$(cat "$PROMPT_TMP")"
  tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -l -- "$prompt_text"
fi

# Robust submit: enter once, then verify execution state; retry enter if needed
submitted=false
for _ in {1..4}; do
  if [[ "$TARGET" == "ssh" ]]; then
    ssh -o BatchMode=yes "$SSH_HOST" "tmux -S '$SOCKET' send-keys -t '$SESSION':0.0 Enter"
    sleep 1
    pane_after="$(ssh -o BatchMode=yes "$SSH_HOST" "tmux -S '$SOCKET' capture-pane -p -J -t '$SESSION':0.0 -S -120" || true)"
  else
    tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 Enter
    sleep 1
    pane_after="$(tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -120 || true)"
  fi

  if echo "$pane_after" | rg -q "Envisioning|Thinking|Running|✽|Mustering|Read [0-9]+ file|Bash\("; then
    submitted=true
    break
  fi
  if echo "$pane_after" | rg -q "Pasted text|^❯"; then
    continue
  fi
done

if [[ "$submitted" != true ]]; then
  echo "WARN: prompt submit not confidently detected; session may need manual Enter once"
fi

if [[ "$TARGET" == "ssh" ]]; then
  echo "TARGET=ssh"
  echo "SSH_HOST=$SSH_HOST"
  echo "SOCKET=$SOCKET (on remote host)"
  echo "SESSION=$SESSION"
  echo "ATTACH: ssh $SSH_HOST 'tmux -S "$SOCKET" attach -t "$SESSION"'"
else
  echo "TARGET=local"
  echo "SOCKET=$SOCKET"
  echo "SESSION=$SESSION"
  echo "ATTACH: tmux -S \"$SOCKET\" attach -t \"$SESSION\""
fi
