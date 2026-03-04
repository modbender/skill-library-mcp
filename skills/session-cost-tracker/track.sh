#!/bin/bash
# Session Cost Tracker - Track your cost-to-value ratio
# Usage: ./track.sh [log|quick|stats] [args]

set -e

DATA_FILE="${SESSION_COST_FILE:-$HOME/.clawdbot/session-costs.json}"
mkdir -p "$(dirname "$DATA_FILE")"

# Initialize if doesn't exist
if [[ ! -f "$DATA_FILE" ]]; then
    echo '{"sessions":[],"created":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"}' > "$DATA_FILE"
fi

# Model pricing (per 1M tokens, input/output average estimate)
get_cost() {
    local model="$1"
    local tokens="$2"
    case "$model" in
        *opus*) echo "scale=4; $tokens * 0.000030" | bc ;;  # ~$30/M avg
        *sonnet*) echo "scale=4; $tokens * 0.000006" | bc ;; # ~$6/M avg
        *haiku*) echo "scale=4; $tokens * 0.000001" | bc ;;  # ~$1/M avg
        *gpt-4*) echo "scale=4; $tokens * 0.000020" | bc ;;  # ~$20/M avg
        *) echo "scale=4; $tokens * 0.000010" | bc ;;        # default ~$10/M
    esac
}

cmd_log() {
    local task="" outcome="" value="" tokens=0 model="claude-opus-4.5" notes=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --task) task="$2"; shift 2 ;;
            --outcome) outcome="$2"; shift 2 ;;
            --value) value="$2"; shift 2 ;;
            --tokens) tokens="$2"; shift 2 ;;
            --model) model="$2"; shift 2 ;;
            --notes) notes="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    if [[ -z "$task" || -z "$value" ]]; then
        echo "Usage: track.sh log --task 'description' --value [high|medium|low|zero] [--tokens N] [--model M] [--outcome O]"
        exit 1
    fi
    
    local cost=$(get_cost "$model" "$tokens")
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local date_only=$(date +%Y-%m-%d)
    
    # Create session entry
    local entry=$(cat <<EOF
{
  "id": "$(uuidgen | tr '[:upper:]' '[:lower:]' 2>/dev/null || echo "sess-$(date +%s)")",
  "timestamp": "$timestamp",
  "date": "$date_only",
  "task": "$task",
  "outcome": "$outcome",
  "value": "$value",
  "tokens": $tokens,
  "model": "$model",
  "cost_usd": $cost,
  "notes": "$notes"
}
EOF
)
    
    # Append to JSON array using jq if available, else python
    if command -v jq &> /dev/null; then
        jq --argjson entry "$entry" '.sessions += [$entry]' "$DATA_FILE" > "${DATA_FILE}.tmp" && mv "${DATA_FILE}.tmp" "$DATA_FILE"
    else
        python3 -c "
import json, sys
entry = json.loads('''$entry''')
with open('$DATA_FILE', 'r') as f:
    data = json.load(f)
data['sessions'].append(entry)
with open('$DATA_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
    fi
    
    echo "✅ Logged: $task (value: $value, cost: \$$cost)"
}

cmd_quick() {
    # Quick log: ./track.sh quick "task description" value tokens
    local task="$1"
    local value="${2:-medium}"
    local tokens="${3:-5000}"
    local model="${4:-claude-opus-4.5}"
    
    if [[ -z "$task" ]]; then
        echo "Usage: track.sh quick 'task' [value] [tokens] [model]"
        echo "Example: track.sh quick 'fixed bug in auth' high 3000"
        exit 1
    fi
    
    cmd_log --task "$task" --value "$value" --tokens "$tokens" --model "$model"
}

cmd_stats() {
    local filter="all"
    local groupby=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --week) filter="week"; shift ;;
            --today) filter="today"; shift ;;
            --by-task) groupby="task"; shift ;;
            --by-value) groupby="value"; shift ;;
            *) shift ;;
        esac
    done
    
    if command -v jq &> /dev/null; then
        local today=$(date +%Y-%m-%d)
        local week_ago=$(date -v-7d +%Y-%m-%d 2>/dev/null || date -d '7 days ago' +%Y-%m-%d 2>/dev/null || echo "2020-01-01")
        
        echo "📊 Session Cost Tracker Stats"
        echo "=============================="
        echo ""
        
        # Total sessions
        local total=$(jq '.sessions | length' "$DATA_FILE")
        echo "Total sessions logged: $total"
        
        if [[ "$total" -eq 0 ]]; then
            echo "No sessions logged yet. Start with: ./track.sh quick 'task' value tokens"
            exit 0
        fi
        
        # By value
        echo ""
        echo "By Value:"
        jq -r '.sessions | group_by(.value) | .[] | "  " + .[0].value + ": " + (length | tostring) + " sessions"' "$DATA_FILE" 2>/dev/null || echo "  (stats require jq)"
        
        # Total cost
        local total_cost=$(jq '[.sessions[].cost_usd] | add // 0' "$DATA_FILE")
        echo ""
        echo "Total cost: \$${total_cost}"
        
        # Cost by value
        echo ""
        echo "Cost by Value:"
        jq -r '.sessions | group_by(.value) | .[] | "  " + .[0].value + ": $" + ([.[].cost_usd] | add | tostring)' "$DATA_FILE" 2>/dev/null || true
        
        # High value sessions
        echo ""
        echo "Recent High-Value Sessions:"
        jq -r '.sessions | map(select(.value == "high")) | .[-5:][] | "  • " + .task + " ($" + (.cost_usd | tostring) + ")"' "$DATA_FILE" 2>/dev/null || echo "  (none)"
        
        # Efficiency ratio
        local high_count=$(jq '[.sessions[] | select(.value == "high")] | length' "$DATA_FILE")
        local low_zero_count=$(jq '[.sessions[] | select(.value == "low" or .value == "zero")] | length' "$DATA_FILE")
        echo ""
        echo "Efficiency: $high_count high-value vs $low_zero_count low/zero-value sessions"
        
    else
        echo "Install jq for detailed stats, or use Python:"
        python3 -c "
import json
with open('$DATA_FILE') as f:
    data = json.load(f)
sessions = data.get('sessions', [])
print(f'Total sessions: {len(sessions)}')
total_cost = sum(s.get('cost_usd', 0) for s in sessions)
print(f'Total cost: \${total_cost:.2f}')
by_value = {}
for s in sessions:
    v = s.get('value', 'unknown')
    by_value[v] = by_value.get(v, 0) + 1
print('By value:', by_value)
"
    fi
}

cmd_export() {
    cat "$DATA_FILE"
}

# Main dispatch
case "${1:-}" in
    log) shift; cmd_log "$@" ;;
    quick) shift; cmd_quick "$@" ;;
    stats) shift; cmd_stats "$@" ;;
    export) cmd_export ;;
    *)
        echo "Session Cost Tracker ⚡"
        echo ""
        echo "Commands:"
        echo "  log     Log a session with full details"
        echo "  quick   Quick log: track.sh quick 'task' value tokens"
        echo "  stats   View statistics"
        echo "  export  Export raw JSON"
        echo ""
        echo "Examples:"
        echo "  ./track.sh quick 'fixed auth bug' high 3000"
        echo "  ./track.sh quick 'researched competitors' medium 8000"
        echo "  ./track.sh quick 'went down rabbit hole' zero 5000"
        echo "  ./track.sh stats"
        ;;
esac
