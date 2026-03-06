#!/bin/bash
# 🦞 启动所有 Agent 的 adapter + connector
# 用法: ./start-agents.sh [start|stop|status]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="/tmp/lobster-agents"
PROMPT_DIR="${AGENT_PROMPT_DIR:-/root/agent-prompts}"

mkdir -p "$PID_DIR"

# Agent 配置: role → port（UUID 从 API 动态获取）
# 可通过 LOBSTER_HOST 环境变量指定平台地址
LOBSTER_API="${LOBSTER_API:-https://mindcore8.com/api/v1}"

# role → adapter_port 映射
declare -A AGENT_PORTS
AGENT_PORTS[product]=8900
AGENT_PORTS[backend]=8901
AGENT_PORTS[frontend]=8902
AGENT_PORTS[tester]=8903
AGENT_PORTS[reviewer]=8904
AGENT_PORTS[pmo]=8905

# role → agent name in DB（用于 API 查询匹配）
declare -A AGENT_NAMES
AGENT_NAMES[product]="产品官"
AGENT_NAMES[backend]="后端大师"
AGENT_NAMES[frontend]="前端大师"
AGENT_NAMES[tester]="测试官"
AGENT_NAMES[reviewer]="审查官"
AGENT_NAMES[pmo]="PMO"

# 从 API 获取 agent UUID，按 name 匹配
fetch_agent_uuids() {
    echo "🔍 Fetching agent UUIDs from $LOBSTER_API/agents/discover ..."
    DISCOVER_JSON=$(curl -sf "$LOBSTER_API/agents/discover" 2>/dev/null || echo "")
    # 优先检查环境变量
    declare -gA AGENT_UUIDS
    local env_count=0
    for role in "${!AGENT_NAMES[@]}"; do
        env_var="AGENT_UUID_${role}"
        if [ -n "${!env_var:-}" ]; then
            AGENT_UUIDS[$role]="${!env_var}"
            env_count=$((env_count + 1))
        fi
    done
    if [ "$env_count" -gt 0 ]; then
        echo "✅ 从环境变量加载 $env_count 个 Agent UUID"
    fi

    if [ -z "$DISCOVER_JSON" ]; then
        if [ "$env_count" -gt 0 ]; then
            return 0
        fi
        echo "⚠️  API 不可用，尝试从缓存文件加载..."
        if [ -f "$PID_DIR/agent-uuids.cache" ]; then
            source "$PID_DIR/agent-uuids.cache"
            echo "✅ 从缓存加载成功"
            return 0
        fi
        echo "❌ 无法获取 Agent UUID（API 不可用且无缓存）"
        echo "   手动指定: export AGENT_UUID_product=xxx AGENT_UUID_backend=xxx ..."
        return 1
    fi

    # 从 API 补充未通过环境变量指定的 UUID
    for role in "${!AGENT_NAMES[@]}"; do
        [ -n "${AGENT_UUIDS[$role]:-}" ] && continue
        agent_name="${AGENT_NAMES[$role]}"
        # 从 API 响应中匹配
        uuid=$(echo "$DISCOVER_JSON" | python3 -c "
import sys, json
data = json.load(sys.stdin)
agents = data if isinstance(data, list) else data.get('agents', data.get('items', []))
for a in agents:
    name = a.get('name', '')
    if '$agent_name' in name:
        print(a['id'])
        break
" 2>/dev/null || echo "")
        if [ -n "$uuid" ]; then
            AGENT_UUIDS[$role]="$uuid"
        else
            echo "⚠️  未找到 $role ($agent_name) 的 UUID"
        fi
    done

    # 写入缓存
    {
        echo "declare -gA AGENT_UUIDS"
        for role in "${!AGENT_UUIDS[@]}"; do
            echo "AGENT_UUIDS[$role]=\"${AGENT_UUIDS[$role]}\""
        done
    } > "$PID_DIR/agent-uuids.cache"
    echo "✅ 已获取 ${#AGENT_UUIDS[@]} 个 Agent UUID"
}

start_agents() {
    echo "🦞 Starting all agents..."
    fetch_agent_uuids || exit 1

    for role in "${!AGENT_PORTS[@]}"; do
        port="${AGENT_PORTS[$role]}"
        full_id="${AGENT_UUIDS[$role]:-}"

        if [ -z "$full_id" ]; then
            echo "  ⏭ $role — skipped (no UUID)"
            continue
        fi

        echo "  ▸ $role (port $port, agent ${full_id:0:8}...)"

        # Start adapter
        PYTHONUNBUFFERED=1 python3 -u "$SCRIPT_DIR/adapters/llm_adapter.py" \
            --port "$port" \
            --system-prompt "$PROMPT_DIR/$role.md" \
            > "$PID_DIR/$role-adapter.log" 2>&1 &
        echo $! > "$PID_DIR/$role-adapter.pid"

        # Wait briefly for adapter to bind
        sleep 1

        # Verify adapter is alive
        if ! kill -0 $(cat "$PID_DIR/$role-adapter.pid") 2>/dev/null; then
            echo "  ❌ $role adapter failed to start. Check $PID_DIR/$role-adapter.log"
            continue
        fi

        # Start connector
        PYTHONUNBUFFERED=1 python3 -u "$SCRIPT_DIR/market-connect.py" \
            --agent-id "$full_id" \
            --local-endpoint "http://localhost:$port/execute" \
            > "$PID_DIR/$role-connect.log" 2>&1 &
        echo $! > "$PID_DIR/$role-connect.pid"
    done
    echo "✅ All agents started. Logs in $PID_DIR/"
}

stop_agents() {
    echo "🛑 Stopping all agents..."
    for pidfile in "$PID_DIR"/*.pid; do
        [ -f "$pidfile" ] || continue
        pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "  ▸ Killed PID $pid ($(basename "$pidfile" .pid))"
        fi
        rm -f "$pidfile"
    done
    echo "✅ All agents stopped."
}

status_agents() {
    echo "📊 Agent status:"
    for role in "${!AGENT_PORTS[@]}"; do
        port="${AGENT_PORTS[$role]}"
        adapt_pid=""
        conn_pid=""
        [ -f "$PID_DIR/$role-adapter.pid" ] && adapt_pid=$(cat "$PID_DIR/$role-adapter.pid")
        [ -f "$PID_DIR/$role-connect.pid" ] && conn_pid=$(cat "$PID_DIR/$role-connect.pid")

        adapt_status="⏹ stopped"
        conn_status="⏹ stopped"
        [ -n "$adapt_pid" ] && kill -0 "$adapt_pid" 2>/dev/null && adapt_status="▶ running ($adapt_pid)"
        [ -n "$conn_pid" ] && kill -0 "$conn_pid" 2>/dev/null && conn_status="▶ running ($conn_pid)"

        # Health check adapter
        health=""
        if [ -n "$adapt_pid" ] && kill -0 "$adapt_pid" 2>/dev/null; then
            health=$(curl -sf "http://localhost:$port/health" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('adapter','?'))" 2>/dev/null || echo "unhealthy")
        fi

        echo "  $role: adapter=$adapt_status  connector=$conn_status  port=$port  health=$health"
    done
}

case "${1:-start}" in
    start)  start_agents ;;
    stop)   stop_agents ;;
    status) status_agents ;;
    restart) stop_agents; sleep 2; start_agents ;;
    *)
        echo "Usage: $0 [start|stop|status|restart]"
        exit 1
        ;;
esac
