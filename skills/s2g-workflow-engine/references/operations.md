# Deployment & Operations

## Running the Bridge as a Service

### systemd (Linux)

Create `/etc/systemd/system/s2g-bridge.service` (or `~/.config/systemd/user/s2g-bridge.service` for user-level):

```ini
[Unit]
Description=S2G WebSocket Bridge
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/YOUR_USER/.openclaw/workspace
ExecStart=/usr/bin/node s2g-bridge.js --s2g wss://s2g.run --node-id YOUR_NODE_UUID --port 18792
Restart=always
RestartSec=5
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
systemctl --user daemon-reload
systemctl --user enable s2g-bridge
systemctl --user start s2g-bridge

# Check status
systemctl --user status s2g-bridge

# View logs
journalctl --user -u s2g-bridge -f
```

### Process manager (pm2)

```bash
npm install -g pm2
pm2 start s2g-bridge.js -- --s2g wss://s2g.run --node-id YOUR_NODE_UUID
pm2 save
pm2 startup  # auto-start on boot
```

### Background with nohup

```bash
nohup node s2g-bridge.js --s2g wss://s2g.run --node-id YOUR_NODE_UUID > /dev/null 2>&1 &
```

> The bridge writes its own logs to `logs/s2g-bridge.log` — no need to capture stdout.

---

## Connection Lifecycle

### Auto-Reconnect

The bridge automatically reconnects on disconnect with a 5-second delay. No manual intervention needed for:
- Network blips
- S2G restarts
- Temporary outages

### Workflow Must Be Running

S2G returns **HTTP 409** on WebSocket connect if the workflow isn't running. The bridge handles this gracefully — it logs `Workflow not running (409) — will retry...` and keeps retrying every 5 seconds.

**To start a workflow:**
```bash
# Via API
curl -X POST "https://s2g.run/api/v1/workflows/YOUR_WORKFLOW_ID/start" \
  -H "X-API-Key: $KEY"

# Or use the ▶ Start button in the S2G designer
```

### Keepalive Ping

The bridge sends `{"type":"ping"}` every 30 seconds. S2G responds with `{"type":"pong"}`. If the ping fails (WebSocket closed), the bridge cleans up and reconnects.

### Connection States

| State | `/health` | `/status` connected | What's happening |
|-------|-----------|---------------------|------------------|
| Connected | 200 | `true` | Normal operation |
| Reconnecting | 503 | `false` | Auto-retry in progress |
| Workflow stopped | 503 | `false` | 409 loop — start the workflow |
| Auth failed | 503 | `false` | Wrong secret — fix and restart |
| Host unreachable | 503 | `false` | Network issue — auto-retry |

---

## Monitoring

### Health Check

```bash
curl -s http://localhost:18792/health
# {"healthy":true,"uptime":3600.5}     ← connected
# {"healthy":false,"uptime":3600.5}    ← disconnected
```

### Full Status

```bash
curl -s http://localhost:18792/status | python3 -m json.tool
```

Returns: `connected`, `s2gHost`, `nodeId`, `lastConnected`, `lastError`, `stats` (connects, executions, errors), `pendingRequests`, and full `nodes` list.

### OpenClaw HEARTBEAT.md Integration

Add to your HEARTBEAT.md for automatic monitoring:

```markdown
## S2G Bridge (keep alive)
Check S2G bridge health:
1. `curl -s http://localhost:18792/health`
2. If unhealthy or unreachable:
   - Check if process is running: `pgrep -f s2g-bridge`
   - If down, restart: `cd ~/.openclaw/workspace && node s2g-bridge.js --s2g wss://s2g.run --node-id UUID &`
   - If running but disconnected, check `/status` for `lastError`
   - If 409 (workflow not running): start workflow via API
3. Log restart in daily memory
```

---

## Handling S2G Restarts

When S2G restarts (deployment, update, crash):

1. WebSocket closes → bridge detects disconnect
2. Bridge waits 5 seconds → attempts reconnect
3. If workflow auto-starts on S2G (🚀 Auto-Start enabled): bridge reconnects and re-discovers nodes
4. If workflow doesn't auto-start: bridge gets 409, keeps retrying until you start it

**Recommendation:** Enable Auto-Start (🚀 rocket icon in S2G toolbar) on your workflow so the bridge always recovers automatically.

---

## Handling OpenClaw Restarts

When OpenClaw/the bridge host restarts:

1. Bridge process dies
2. If running via systemd/pm2: auto-restarts
3. If running via nohup/background: must be restarted manually or via HEARTBEAT.md
4. On connect: S2G sends full node list — no state to recover

The bridge is **stateless** — all it needs is the S2G host URL and node ID. No session tokens, no state files. Just restart and it's back.

---

## Logging

**Log file:** `logs/s2g-bridge.log` (relative to working directory)
**Rotation:** Automatic at 5MB — old log renamed to `.log.1`
**Override:** Set `S2G_LOG_DIR` environment variable

Log entries include:
- Connection/disconnection events
- Node discovery on connect
- Execute requests and results
- Incoming data pushes (`📨 Received [type]: ...`)
- Errors with timestamps

```bash
# Tail live
tail -f logs/s2g-bridge.log

# Search for errors
grep ERROR logs/s2g-bridge.log

# Search for data pushes
grep "📨" logs/s2g-bridge.log
```

---

## Force Reconnect

If the bridge is connected but stale (e.g., node list changed after adding nodes in S2G):

```bash
# Reconnect (drops and re-establishes WebSocket)
curl -X POST http://localhost:18792/reconnect

# Or just refresh node list without reconnecting
curl -X POST http://localhost:18792/refresh
```

After adding/removing nodes in S2G, always stop → start the workflow, then `/reconnect` on the bridge.

---

## Multiple Bridges

You can run multiple bridge instances connecting to different workflows:

```bash
# Bridge 1: Utility tools workflow
node s2g-bridge.js --s2g wss://s2g.run --node-id UUID_1 --port 18792 &

# Bridge 2: Database workflow
node s2g-bridge.js --s2g wss://s2g.run --node-id UUID_2 --port 18793 &
```

Each bridge gets its own port, log directory, and node discovery.

---

## Security

### Auth Secret

Set an auth secret on the OpenClaw node in S2G (node properties → Auth Secret). When set, the bridge **must** send `{"type":"auth","secret":"..."}` as its **first message** after connecting — before any other communication.

```bash
node s2g-bridge.js --s2g wss://s2g.run --node-id UUID --secret YOUR_SECRET
# Or: S2G_SECRET=YOUR_SECRET node s2g-bridge.js ...
```

- If the secret is wrong → `auth_failed`, connection closed, bridge does **not** auto-retry (prevents brute-force)
- If no secret sent when required → `auth_required` error
- If Auth Secret field is blank → open/unauthenticated connection

### Network

- **Public S2G (`wss://s2g.run`):** TLS encrypted, auth secret recommended
- **Self-hosted (`ws://host:5184`):** Consider running behind a reverse proxy with TLS, or within a private network/VPN
- **Bridge HTTP API (`localhost:18792`):** Binds to `0.0.0.0` — restrict with firewall if needed
