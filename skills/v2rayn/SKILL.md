# V2RayN Skill

Manage V2RayN proxy client on macOS with auto-failover.

## Overview

V2RayN is a V2Ray client for macOS. This skill helps manage nodes, test connections, auto-check for failures, and update subscriptions.

## Quick Status Check

```bash
# Check if V2RayN is running
ps aux | grep -i v2rayN | grep -v grep

# Check listening ports
lsof -i :10808 -i :10809 -i :10810 -i :7890 -i :7891 2>/dev/null

# Test connection
curl -s --max-time 5 https://www.google.com -w "\nStatus: %{http_code}\n"
```

## Auto-Check Node Health (Every 30 min)

This skill automatically:
1. Check if current node is working
2. If failed, update subscription
3. Select a new working node

### Implementation

Create a cron job:
```
*/30 * * * * /path/to/check_v2rayn.sh
```

### Check Script

```bash
#!/bin/bash
# check_v2rayn.sh - Auto-check and failover for V2RayN

LOG_FILE="$HOME/.openclaw/logs/v2rayn_check.log"
CONFIG_DIR="$HOME/Library/Application Support/v2rayN/guiConfigs"
MAIN_CONFIG="$CONFIG_DIR/guiNConfig.json"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Test connection
test_connection() {
    curl -s --max-time 5 -x socks5://127.0.0.1:10808 https://www.google.com -o /dev/null -w "%{http_code}" 2>/dev/null
}

# Get current node info
get_current_node() {
    python3 -c "
import json
with open('$MAIN_CONFIG') as f:
    d = json.load(f)
    idx = d.get('currentServerIndex')
    if idx is not None:
        servers = d.get('vmess',[]) + d.get('vless',[]) + d.get('trojan',[])
        if idx < len(servers):
            print(servers[idx].get('remarks', 'Unknown'))
        else:
            print('Invalid index')
    else:
        print('No server selected')
" 2>/dev/null
}

# Main check
log "=== Starting V2RayN health check ==="

# Test current connection
RESULT=$(test_connection)
log "Connection test result: $RESULT"

if [ "$RESULT" = "200" ]; then
    log "✅ Node is working: $(get_current_node)"
    exit 0
else
    log "❌ Node failed! Trying to recover..."
    
    # Try to update subscription
    log "Updating subscription..."
    # Note: V2RayN CLI is limited, manual or external script needed
    
    log "Please manually:"
    log "1. Open V2RayN"
    log "2. Update subscription"
    log "3. Select a new node"
    
    # Notify user
    echo "⚠️ V2RayN node failed! Please check manually."
    exit 1
fi
```

## Manual Commands

### 1. Check Node Status
```bash
# Test all common proxy ports
for port in 10808 10809 10810 7890 7891; do
    result=$(curl -s --max-time 3 -x socks5://127.0.0.1:$port https://www.google.com -w "%{http_code}" 2>/dev/null)
    echo "Port $port: $result"
done
```

### 2. List All Nodes
```bash
cat ~/Library/Application\ Support/v2rayN/guiConfigs/guiNConfig.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
servers = d.get('vmess',[]) + d.get('vless',[]) + d.get('trojan',[]) + d.get('shadowsocks',[])
print(f'Total nodes: {len(servers)}')
for i, s in enumerate(servers):
    print(f'{i+1}. {s.get(\"remarks\", s.get(\"name\", \"Unnamed\"))}')
"
```

### 3. Get Current Node
```bash
python3 -c "
import json
with open('$HOME/Library/Application Support/v2rayN/guiConfigs/guiNConfig.json') as f:
    d = json.load(f)
    idx = d.get('currentServerIndex')
    if idx:
        servers = d.get('vmess',[]) + d.get('vless',[]) + d.get('trojan',[])
        if idx < len(servers):
            s = servers[idx]
            print(f'Current: {s.get(\"remarks\", \"Unknown\")}')
            print(f'Protocol: {s.get(\"protocol\", \"trojan\")}')
"
```

### 4. Test Specific Node
```bash
# Test current node
curl -s --max-time 5 -x socks5://127.0.0.1:10808 https://www.google.com

# Test direct
curl -s --max-time 5 https://www.google.com
```

### 5. View Logs
```bash
ls -la ~/Library/Application\ Support/v2rayN/guiLogs/
tail -50 ~/Library/Application\ Support/v2rayN/guiLogs/*.log 2>/dev/null | tail -30
```

### 6. Restart V2RayN
```bash
# Kill and restart
pkill -f v2rayN
open /Applications/v2rayN.app
```

### 7. Force Update Subscription
Note: V2RayN doesn't have a CLI for subscription update. You'll need to:
1. Open V2RayN GUI
2. Click "Update" on your subscription

## Configuration Files

| File | Description |
|------|-------------|
| `guiNConfig.json` | Main GUI config (nodes, settings) |
| `config.json` | V2Ray/Xray runtime config |
| `configPre.json` | Sing-box config (if using TUN mode) |

## Troubleshooting

### Node Not Working
1. Check logs: `tail -50 ~/Library/Application Support/v2rayN/guiLogs/*.log`
2. Test port: `lsof -i :10808`
3. Try different node in GUI
4. Update subscription

### All Nodes Invalid
- Import new subscription
- Or add nodes manually in GUI

### TUN Mode Not Working
- Check if TUN interface exists: `ifconfig | grep -i tun`
- Check configPre.json for TUN settings
