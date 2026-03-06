# Discord Connect Troubleshooting Guide

Quick reference for diagnosing and resolving Discord integration issues.

## Diagnostic Commands

```bash
# Run health check
./scripts/health-check.py --token YOUR_TOKEN

# Test token only
./scripts/test-token.py YOUR_TOKEN

# Check gateway logs
clawdbot logs | grep -i discord

# Check connection status via RPC
clawdbot rpc discord.status
```

## Common Issues

### Token Issues

#### "Invalid token" error
- **Symptom**: Health check shows token invalid
- **Causes**:
  - Token was copied incorrectly (missing characters)
  - Token was reset in Developer Portal
  - Using user token instead of bot token
- **Fix**:
  1. Go to Developer Portal → Your App → Bot
  2. Click **Reset Token**
  3. Copy the complete new token
  4. Update in Clawdbot config

#### "401 Unauthorized" API errors
- **Symptom**: API calls fail with 401
- **Cause**: Token expired or invalid
- **Fix**: Reset and update token

### Connection Issues

#### Bot shows as offline
- **Symptom**: Bot appears offline in Discord
- **Possible causes**:
  1. Gateway not connected
  2. Token invalid
  3. Rate limited
  4. Network issues
- **Debug steps**:
  ```bash
  # Check gateway status
  clawdbot rpc discord.status
  
  # Check for errors in logs
  clawdbot logs | grep -i "discord.*error"
  ```

#### Frequent disconnections
- **Symptom**: Bot connects then disconnects repeatedly
- **Possible causes**:
  1. Network instability
  2. Rate limiting
  3. Multiple bot instances with same token
- **Fix**:
  - Ensure only one instance is running
  - Check network connectivity
  - Review rate limit logs

### Message Issues

#### Bot not responding to messages
- **Checklist**:
  1. ✅ Message Content Intent enabled?
  2. ✅ Bot can see the channel?
  3. ✅ `requireMention` setting correct?
  4. ✅ Channel not muted/disabled in config?
  5. ✅ User not blocked/filtered?

#### "Missing Message Content Intent"
- **Symptom**: Error in logs about missing intent
- **Fix**:
  1. Go to Developer Portal → Bot
  2. Enable **Message Content Intent** under Privileged Gateway Intents
  3. Save changes
  4. Restart gateway: `clawdbot gateway restart`

#### Messages truncated
- **Symptom**: Long messages are cut off
- **Cause**: Discord has 2000 character limit
- **Fix**: Clawdbot should auto-split; check `messageChunking` setting

### Permission Issues

#### "Missing Access" errors
- **Symptom**: Bot can't perform action
- **Causes**:
  - Missing bot permissions
  - Channel permission overwrites
  - Role hierarchy issues
- **Debug**:
  ```bash
  # Check bot permissions
  clawdbot rpc discord.permissions --guild-id GUILD_ID
  ```

#### Can't send messages in channel
- **Checklist**:
  1. Bot has Send Messages permission
  2. No channel-level deny for Send Messages
  3. Channel is not read-only (announcement channels)
  4. Bot is not timed out

#### Can't add reactions
- **Required permission**: Add Reactions
- **Also check**: External Emojis (for emojis from other servers)

### UI Issues

#### Discord tab not showing
- **Symptom**: Tab missing from dashboard
- **Possible causes**:
  1. UI components not installed
  2. Navigation not updated
  3. Build failed
- **Fix**:
  ```bash
  # Verify files exist
  ls ui/src/ui/views/discord.ts
  
  # Check navigation.ts has discord entry
  grep discord ui/src/ui/navigation.ts
  
  # Rebuild
  pnpm build && pnpm ui:build
  clawdbot gateway restart
  ```

#### Dashboard shows "Disconnected"
- **Check**: `clawdbot rpc discord.status`
- **If token missing**: Add token in dashboard or config
- **If token invalid**: Reset token in Developer Portal

#### Health check shows warnings
- **Common warnings**:
  - "Bot not in any servers" → Use invite URL to add bot
  - "Could not verify intents" → Manual check in Developer Portal

### Rate Limiting

#### "Rate limited" errors
- **Symptom**: Actions fail with rate limit error
- **Cause**: Too many requests to Discord API
- **Fix**: Clawdbot handles this automatically; wait and retry
- **Prevention**: Avoid rapid-fire commands

#### Session limit reached
- **Symptom**: Can't connect to gateway
- **Cause**: Too many identify attempts
- **Fix**: Wait (usually 24 hours for reset)

## Log Analysis

### Key log patterns

```bash
# Connection established
grep "discord.*connected" clawdbot.log

# Errors
grep -i "discord.*error" clawdbot.log

# Message handling
grep "discord.*message" clawdbot.log

# Rate limits
grep -i "rate.?limit" clawdbot.log
```

### Log levels

Set Discord-specific log level:
```yaml
logging:
  subsystems:
    discord: debug  # trace, debug, info, warn, error
```

## Recovery Procedures

### Complete reset

If all else fails:

```bash
# 1. Stop gateway
clawdbot gateway stop

# 2. Remove discord config temporarily
# Edit ~/.clawdbot/config.yaml - comment out discord section

# 3. Restart without discord
clawdbot gateway start

# 4. Reset token in Developer Portal

# 5. Re-add discord config with new token

# 6. Restart
clawdbot gateway restart
```

### Re-invite bot

If permissions are broken:

1. Kick bot from server
2. Generate new invite URL with correct permissions
3. Re-invite bot

### Database issues

If channel/guild data is corrupted:

```bash
# Reset discord state (if applicable)
rm ~/.clawdbot/data/discord-*.json

# Restart to rebuild state
clawdbot gateway restart
```

## Getting Help

1. Check logs: `clawdbot logs | tail -100`
2. Run health check: `./scripts/health-check.py`
3. Search docs: https://docs.clawd.bot
4. Community Discord: https://discord.com/invite/clawd
5. GitHub Issues: https://github.com/clawdbot/clawdbot/issues
