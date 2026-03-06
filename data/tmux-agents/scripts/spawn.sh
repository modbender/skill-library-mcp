#!/bin/bash
# Spawn a coding agent in a tmux session

SESSION_NAME="${1:-agent-$(date +%s)}"
TASK="$2"
AGENT="${3:-claude}"

if [ -z "$TASK" ]; then
  echo "Usage: spawn.sh <session-name> <task> [agent]"
  echo ""
  echo "Cloud Agents (uses API credits):"
  echo "  claude        - Claude Code (default)"
  echo "  codex         - OpenAI Codex CLI"
  echo "  gemini        - Google Gemini CLI"
  echo ""
  echo "Local Agents (free, uses Ollama):"
  echo "  ollama-claude - Claude Code + local model"
  echo "  ollama-codex  - Codex + local model"
  echo ""
  echo "Examples:"
  echo "  spawn.sh fix-bug 'Fix login validation' claude"
  echo "  spawn.sh experiment 'Refactor entire codebase' ollama-claude"
  exit 1
fi

# Check if session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "⚠️  Session '$SESSION_NAME' already exists"
  echo "Use: tmux attach -t $SESSION_NAME"
  exit 1
fi

# Determine if using local or cloud
LOCAL_MODE=false
case "$AGENT" in
  ollama-*) LOCAL_MODE=true ;;
esac

# Create new detached session
tmux new-session -d -s "$SESSION_NAME" -x 200 -y 50

# Set up the environment
tmux send-keys -t "$SESSION_NAME" "cd ~/clawd" Enter
tmux send-keys -t "$SESSION_NAME" "clear" Enter
tmux send-keys -t "$SESSION_NAME" "echo '🚀 Agent Session: $SESSION_NAME'" Enter
tmux send-keys -t "$SESSION_NAME" "echo '🤖 Agent: $AGENT'" Enter
if [ "$LOCAL_MODE" = true ]; then
  tmux send-keys -t "$SESSION_NAME" "echo '🦙 Mode: LOCAL (Ollama - free!)'" Enter
else
  tmux send-keys -t "$SESSION_NAME" "echo '☁️  Mode: CLOUD (API credits)'" Enter
fi
tmux send-keys -t "$SESSION_NAME" "echo '📋 Task: $TASK'" Enter
tmux send-keys -t "$SESSION_NAME" "echo '⏰ Started: $(date)'" Enter
tmux send-keys -t "$SESSION_NAME" "echo '-------------------------------------------'" Enter
tmux send-keys -t "$SESSION_NAME" "echo ''" Enter

# Launch the appropriate agent
case "$AGENT" in
  claude)
    # Claude Code with auto-accept permissions (cloud)
    tmux send-keys -t "$SESSION_NAME" "claude --dangerously-skip-permissions \"$TASK\"" Enter
    ;;
  codex)
    # OpenAI Codex CLI with auto-approve (cloud)
    tmux send-keys -t "$SESSION_NAME" "codex --auto-edit --full-auto \"$TASK\"" Enter
    ;;
  gemini)
    # Google Gemini CLI (cloud)
    tmux send-keys -t "$SESSION_NAME" "gemini \"$TASK\"" Enter
    ;;
  ollama-claude)
    # Claude Code with local Ollama model (free!)
    tmux send-keys -t "$SESSION_NAME" "echo 'Launching Claude Code with local Ollama model...'" Enter
    tmux send-keys -t "$SESSION_NAME" "ollama launch claude" Enter
    sleep 2
    tmux send-keys -t "$SESSION_NAME" "\"$TASK\"" Enter
    ;;
  ollama-codex)
    # Codex with local Ollama model (free!)
    tmux send-keys -t "$SESSION_NAME" "echo 'Launching Codex with local Ollama model...'" Enter
    tmux send-keys -t "$SESSION_NAME" "ollama launch codex" Enter
    sleep 2
    tmux send-keys -t "$SESSION_NAME" "\"$TASK\"" Enter
    ;;
  *)
    # Custom command - pass task as argument
    tmux send-keys -t "$SESSION_NAME" "$AGENT \"$TASK\"" Enter
    ;;
esac

echo "✅ Session '$SESSION_NAME' spawned with $AGENT"
if [ "$LOCAL_MODE" = true ]; then
  echo "🦙 Running locally — no API costs!"
else
  echo "☁️  Using cloud API"
fi
echo ""
echo "📋 Task: $TASK"
echo ""
echo "Commands:"
echo "  👀 Watch:   tmux attach -t $SESSION_NAME"
echo "  📊 Check:   ./skills/tmux-agents/scripts/check.sh $SESSION_NAME"
echo "  💬 Send:    tmux send-keys -t $SESSION_NAME 'message' Enter"
echo "  🛑 Kill:    tmux kill-session -t $SESSION_NAME"
