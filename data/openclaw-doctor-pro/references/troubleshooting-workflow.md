# Troubleshooting Workflow

Decision trees and diagnostic flows for common OpenClaw issues.

## Quick Diagnostic Decision Tree

```
OpenClaw Issue?
├─ Gateway won't start → See: Gateway Startup Flow
├─ Gateway unreachable → See: Gateway Connectivity Flow
├─ Channel not working → See: Channel Troubleshooting Flow
├─ AI provider errors → See: Provider Error Flow
├─ Sandbox failures → See: Sandbox Diagnostic Flow
└─ General slowness → See: Performance Diagnostic Flow
```

## 1. Gateway Startup Flow

**Problem: Gateway won't start**

```
1. Check if already running
   ├─ openclaw status
   ├─ If running → See: Gateway Connectivity Flow
   └─ If not running → Continue

2. Check port availability
   ├─ lsof -i :18789
   ├─ If port in use → Kill process or change port
   │  ├─ Auto-fix: python3 scripts/error-fixer.py --error EADDRINUSE --auto-fix
   │  └─ Manual: openclaw config set gateway.port 18790
   └─ If port free → Continue

3. Check Node.js version
   ├─ node --version
   ├─ If < 22 → Install Node.js 22+
   │  └─ See: Installation Errors > NODE_VERSION_OLD
   └─ If >= 22 → Continue

4. Validate configuration
   ├─ openclaw config validate
   ├─ If invalid → Fix config errors
   │  └─ Auto-fix: python3 scripts/error-fixer.py --category configuration --auto-fix
   └─ If valid → Continue

5. Check logs for errors
   ├─ openclaw logs --level error --last 10m
   ├─ If auth errors → See: Authentication Flow
   ├─ If config errors → See: Configuration Flow
   └─ If unknown → Run full diagnostic

6. Run full diagnostic
   └─ openclaw doctor --full
      └─ Follow recommendations

7. Last resort
   ├─ openclaw rebuild
   └─ openclaw start --verbose --foreground
```

**Common Resolutions:**
- 70% Port conflict (EADDRINUSE)
- 15% Configuration errors
- 10% Missing dependencies
- 5% Permission issues

---

## 2. Gateway Connectivity Flow

**Problem: Gateway running but unreachable**

```
1. Verify gateway is running
   ├─ openclaw status
   └─ If stopped → See: Gateway Startup Flow

2. Test local connectivity
   ├─ curl http://localhost:18789/health
   ├─ If fails → Check binding
   │  ├─ netstat -tulpn | grep 18789
   │  ├─ If bound to 127.0.0.1 only:
   │  │  ├─ openclaw config set gateway.host "0.0.0.0"
   │  │  └─ openclaw restart
   │  └─ If not listening → Check logs
   └─ If succeeds → Continue

3. Test from external IP
   ├─ curl http://<server-ip>:18789/health
   ├─ If fails → Check firewall
   │  ├─ sudo ufw allow 18789/tcp
   │  ├─ sudo firewall-cmd --add-port=18789/tcp --permanent
   │  └─ Check cloud security groups
   └─ If succeeds → Channel-specific issue

4. Check channel connections
   ├─ openclaw channels status --all
   └─ If channel fails → See: Channel Troubleshooting Flow

5. Test with verbose logging
   └─ openclaw logs --follow --level debug
```

**Common Resolutions:**
- 50% Firewall blocking port
- 30% Wrong host binding (127.0.0.1 vs 0.0.0.0)
- 15% Cloud security group rules
- 5% Network routing issues

---

## 3. Channel Troubleshooting Flow

**Problem: Channel not working**

```
1. Check channel status
   ├─ openclaw channels status <channel>
   ├─ If disabled → openclaw channels enable <channel>
   └─ If enabled → Continue

2. Check configuration
   ├─ openclaw config get channels.<channel>
   ├─ If missing token → Set token
   │  └─ openclaw config set channels.<channel>.token "..."
   └─ If configured → Continue

3. Test channel connection
   ├─ openclaw channels test <channel>
   └─ Branch by result:
      ├─ WhatsApp → See: WhatsApp Flow
      ├─ Telegram → See: Telegram Flow
      ├─ Discord → See: Discord Flow
      ├─ Slack → See: Slack Flow
      └─ Signal → See: Signal Flow

4. Check channel logs
   └─ openclaw logs --channel <channel> --last 30m
```

### WhatsApp Flow
```
1. Check link status
   ├─ openclaw whatsapp session-info
   └─ If not linked → openclaw whatsapp link

2. Check session validity
   ├─ If "Session invalid" → Re-link
   │  ├─ openclaw whatsapp logout
   │  ├─ rm -rf .openclaw/whatsapp-session
   │  └─ openclaw whatsapp link
   └─ If valid → Continue

3. Check phone connectivity
   ├─ Ensure phone has internet
   ├─ Check WhatsApp on phone is active
   └─ Verify not at 4-device limit

4. Test message send
   └─ Send test message from phone
```

### Telegram Flow
```
1. Verify bot token
   ├─ curl "https://api.telegram.org/bot<TOKEN>/getMe"
   └─ If fails → Get new token from @BotFather

2. Check webhook/polling mode
   ├─ openclaw config get channels.telegram.mode
   └─ If webhook:
      ├─ openclaw telegram webhook-info
      ├─ If failed → openclaw telegram set-webhook
      └─ If HTTPS error → Use polling mode
         └─ openclaw config set channels.telegram.mode polling

3. Test bot commands
   └─ Send /start to bot
```

### Discord Flow
```
1. Check bot permissions
   ├─ openclaw discord check-permissions
   └─ If missing → Regenerate invite
      └─ openclaw discord generate-invite

2. Verify intents
   ├─ Check Discord Developer Portal → Bot → Intents
   ├─ Enable: MESSAGE_CONTENT, GUILD_MESSAGES
   └─ Update config
      └─ openclaw config set channels.discord.intents '["GUILDS","GUILD_MESSAGES","MESSAGE_CONTENT"]'

3. Check bot online status
   └─ If offline → Check token + restart
```

### Slack Flow
```
1. Verify signing secret
   └─ openclaw slack verify-signing-secret

2. Check OAuth scopes
   ├─ View Slack App → OAuth & Permissions
   └─ Ensure: chat:write, channels:history, users:read

3. Refresh token
   └─ openclaw slack refresh-token

4. Check event subscriptions
   └─ Slack App → Event Subscriptions → Request URL
```

### Signal Flow
```
1. Check Signal CLI installed
   ├─ which signal-cli
   └─ If not found → Install
      └─ Auto-fix: python3 scripts/error-fixer.py --error SIGNAL_CLI_MISSING --auto-fix

2. Check registration
   ├─ signal-cli -u <phone> listIdentities
   └─ If not registered → Register
      ├─ signal-cli -u <phone> register
      └─ signal-cli -u <phone> verify <code>

3. Test send
   └─ signal-cli -u <phone> send -m "test" <recipient>
```

---

## 4. Provider Error Flow

**Problem: AI provider errors (401, 429, 502)**

```
1. Identify error code
   └─ Check logs: openclaw logs --filter "error" --last 1h

2. Branch by error:
   ├─ 401/403 → See: Authentication Flow
   ├─ 429 → See: Rate Limiting Flow
   ├─ 500/502/503 → See: Provider Outage Flow
   └─ Timeout → See: Timeout Flow

Authentication Flow (401/403):
├─ Check API key set
│  └─ openclaw config get ai.providers.<provider>.apiKey
├─ Validate key format
│  └─ Auto-fix: python3 scripts/error-fixer.py --error 401 --auto-fix
├─ Test provider directly
│  └─ openclaw providers test <provider>
└─ Check provider dashboard for key status

Rate Limiting Flow (429):
├─ Check current limits
│  └─ openclaw status --rate-limits
├─ Enable retry strategy
│  └─ Auto-fix: python3 scripts/error-fixer.py --error 429 --auto-fix
├─ Reduce request rate
│  └─ openclaw config set ai.rateLimiting.requestsPerMinute 30
└─ Enable fallback provider
   └─ openclaw config set ai.fallback.enabled true

Provider Outage Flow (500/502/503):
├─ Check provider status
│  └─ openclaw status --provider-health
├─ Check status page
│  ├─ OpenAI: status.openai.com
│  ├─ Anthropic: status.anthropic.com
│  └─ Google: status.cloud.google.com
└─ Enable fallback
   └─ openclaw config set ai.fallback.enabled true

Timeout Flow:
├─ Increase timeout
│  └─ openclaw config set ai.timeout.requestMs 90000
├─ Check network latency
│  └─ openclaw benchmark --provider <provider>
└─ Test with smaller request
```

---

## 5. Sandbox Diagnostic Flow

**Problem: Sandbox execution failures**

```
1. Check Docker running
   ├─ docker info
   └─ If not running → Start Docker
      ├─ systemctl start docker (Linux)
      └─ Launch Docker Desktop (macOS/Windows)

2. Check container status
   ├─ docker ps -a | grep openclaw
   └─ If exited:
      ├─ Check exit code
      │  ├─ 137 → OOM (out of memory)
      │  ├─ 143 → Timeout
      │  └─ Other → Check logs
      └─ View logs: docker logs <container>

3. Branch by error:
   ├─ OOM (137) → Increase memory
   │  └─ Auto-fix: python3 scripts/error-fixer.py --error CONTAINER_OOM --auto-fix
   ├─ Timeout (143) → Increase timeout
   │  └─ openclaw config set sandbox.timeout.execution 600000
   ├─ Permission denied → Fix workspace
   │  └─ Auto-fix: python3 scripts/error-fixer.py --error WORKSPACE_MOUNT_FAIL --auto-fix
   └─ Network error → Enable network
      └─ openclaw config set sandbox.network.enabled true

4. Test sandbox
   └─ openclaw sandbox exec -- python -c "print('test')"
```

---

## 6. Performance Diagnostic Flow

**Problem: Slow responses or high resource usage**

```
1. Check system metrics
   ├─ openclaw status --metrics
   └─ Identify bottleneck:
      ├─ High CPU → See: CPU Flow
      ├─ High Memory → See: Memory Flow
      └─ High I/O → See: I/O Flow

CPU Flow:
├─ Check active requests
│  └─ openclaw requests --status running
├─ Reduce concurrency
│  └─ openclaw config set gateway.concurrency.max 20
└─ Profile with verbose logging
   └─ openclaw logs --follow --level debug

Memory Flow:
├─ Check for memory leaks
│  └─ openclaw status --watch --interval 5
├─ Reduce sandbox memory
│  └─ openclaw config set sandbox.memory.limit "1GB"
└─ Clear caches
   └─ openclaw cache clear

I/O Flow:
├─ Check disk space
│  └─ df -h
├─ Clear old logs
│  └─ rm -rf ~/.openclaw/logs/*.old
└─ Optimize workspace
   └─ docker system prune -a

2. Benchmark providers
   └─ openclaw benchmark --provider openai --samples 10

3. Check network latency
   └─ ping api.openai.com

4. Enable request queuing
   └─ openclaw config set gateway.queueing.enabled true
```

---

## Priority Matrix

Use this to prioritize which issues to fix first:

| Priority | Issues | Fix Order |
|----------|--------|-----------|
| **Critical** | Gateway won't start, All channels down, Auth failed | Fix immediately |
| **High** | One channel down, Rate limits hit, Sandbox failing | Fix within 1 hour |
| **Medium** | Slow responses, Warnings in logs, Config deprecated | Fix within 1 day |
| **Low** | Minor optimizations, Non-critical warnings | Fix when convenient |

## Escalation Path

```
1. Self-Service
   ├─ Use error-fixer.py --auto-fix
   ├─ Follow decision trees above
   └─ Check references/*.md files

2. Automated Diagnosis
   ├─ python3 scripts/enhanced-doctor.py --deep
   └─ Review generated report

3. Community Support
   ├─ Search GitHub issues
   ├─ Check Discord/Slack community
   └─ Post issue with diagnostic report

4. Professional Support
   └─ Contact OpenClaw support with:
      ├─ openclaw doctor --full output
      ├─ Enhanced doctor report
      └─ Relevant logs
```

## Diagnostic Report Generation

```bash
# Generate comprehensive diagnostic report
cat > /tmp/openclaw-diagnostic.sh << 'EOF'
#!/bin/bash
echo "=== OpenClaw Diagnostic Report ===" > diagnostic-report.txt
echo "Generated: $(date)" >> diagnostic-report.txt
echo "" >> diagnostic-report.txt

echo "--- System Info ---" >> diagnostic-report.txt
uname -a >> diagnostic-report.txt
node --version >> diagnostic-report.txt
docker --version >> diagnostic-report.txt
echo "" >> diagnostic-report.txt

echo "--- OpenClaw Status ---" >> diagnostic-report.txt
openclaw status --detailed >> diagnostic-report.txt
echo "" >> diagnostic-report.txt

echo "--- Health Check ---" >> diagnostic-report.txt
openclaw doctor --full >> diagnostic-report.txt
echo "" >> diagnostic-report.txt

echo "--- Configuration ---" >> diagnostic-report.txt
openclaw config show >> diagnostic-report.txt
echo "" >> diagnostic-report.txt

echo "--- Recent Errors ---" >> diagnostic-report.txt
openclaw logs --level error --last 1h >> diagnostic-report.txt
echo "" >> diagnostic-report.txt

echo "--- Channel Status ---" >> diagnostic-report.txt
openclaw channels status --all >> diagnostic-report.txt
echo "" >> diagnostic-report.txt

echo "Report saved to: diagnostic-report.txt"
EOF

chmod +x /tmp/openclaw-diagnostic.sh
/tmp/openclaw-diagnostic.sh
```

## Related Files

- [Error Catalog](error-catalog.md) - All error types
- [Auto-Fix Capabilities](auto-fix-capabilities.md) - What can be auto-fixed
- [Diagnostic Commands](diagnostic-commands.md) - All CLI commands
- [Authentication Errors](authentication-errors.md) - Auth-specific flow
- [Gateway Errors](gateway-errors.md) - Gateway-specific flow
- [Channel Errors](channel-errors.md) - Channel-specific flows
