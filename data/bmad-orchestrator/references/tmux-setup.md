# tmux Setup & Interaction Patterns

## Session Initialization

```bash
VM_HOST="10.0.0.189"
VM_USER="hrexed"
SOCKET="/tmp/openclaw-tmux-sockets/openclaw.sock"
SESSION="bmad-<project-name>"
PROJECT_PATH="/mnt/nas/project/<project-name>"

# Create socket dir and session
ssh ${VM_USER}@${VM_HOST} "mkdir -p /tmp/openclaw-tmux-sockets && tmux -S ${SOCKET} new -d -s ${SESSION} -n shell -c ${PROJECT_PATH}"

# Launch Claude Code
ssh ${VM_USER}@${VM_HOST} "tmux -S ${SOCKET} send-keys -t ${SESSION}:0.0 'npx @anthropic-ai/claude-code --dangerously-skip-permissions' Enter"

# Accept permissions (select option 2)
sleep 10
ssh ${VM_USER}@${VM_HOST} "tmux -S ${SOCKET} send-keys -t ${SESSION}:0.0 Down && sleep 0.2 && tmux -S ${SOCKET} send-keys -t ${SESSION}:0.0 Enter"
```

## Sending Commands

Always split text and Enter for Claude Code TUI:

```bash
# Send a slash command
ssh ${VM_USER}@${VM_HOST} "tmux -S ${SOCKET} send-keys -t ${SESSION}:0.0 -l -- '/bmad-bmm-create-prd'" && \
sleep 0.3 && \
ssh ${VM_USER}@${VM_HOST} "tmux -S ${SOCKET} send-keys -t ${SESSION}:0.0 Enter"
```

For multi-line prompts, write to a temp file and use `cat`:

```bash
scp /tmp/prompt.txt ${VM_USER}@${VM_HOST}:/tmp/prompt.txt
ssh ${VM_USER}@${VM_HOST} "tmux -S ${SOCKET} send-keys -t ${SESSION}:0.0 -l -- \"\$(cat /tmp/prompt.txt)\"" && \
sleep 0.3 && \
ssh ${VM_USER}@${VM_HOST} "tmux -S ${SOCKET} send-keys -t ${SESSION}:0.0 Enter"
```

## Reading Output

```bash
# Last 200 lines
ssh ${VM_USER}@${VM_HOST} "tmux -S ${SOCKET} capture-pane -p -J -t ${SESSION}:0.0 -S -200"

# Check if idle (prompt visible)
ssh ${VM_USER}@${VM_HOST} "tmux -S ${SOCKET} capture-pane -p -J -t ${SESSION}:0.0 -S -5" | grep -q "❯"
```

## Interrupting

```bash
ssh ${VM_USER}@${VM_HOST} "tmux -S ${SOCKET} send-keys -t ${SESSION}:0.0 C-c"
```

## Reading Generated Files

```bash
ssh ${VM_USER}@${VM_HOST} "cat ${PROJECT_PATH}/_bmad-output/planning-artifacts/prd.md"
```

## Monitoring Cron Pattern

Set up a cron job every 15 minutes to:
1. Capture pane output
2. Check if Claude Code is idle or working
3. Report status to user
4. Auto-remove cron when task completes
