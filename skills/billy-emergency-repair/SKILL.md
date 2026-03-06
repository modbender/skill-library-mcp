---
name: Billy Emergency Repair Skill
description: ⚠️ NEILL-ONLY COMMAND ⚠️ Only Neill can authorize emergency repairs
  to Billy. Never run without explicit Neill authorization.
---

# Billy Emergency Repair Skill

## Use When
- Neill explicitly requests Billy system repair
- Neill reports Billy authentication/gateway issues  
- Neill says "fix Billy" or "Billy is down"
- Billy system appears unresponsive to Neill

## Don't Use When
- Billy is working fine
- Issue is not authentication-related
- Anyone other than Neill requests the repair
- Routine maintenance (not emergency)

## AUTHORIZATION REQUIRED
⚠️ **NEILL-ONLY COMMAND** ⚠️
Only Neill can authorize emergency repairs to Billy. Never run without explicit Neill authorization.

## Usage

### Standard Repair (Recommended)
```bash
# Switch to Opus for enhanced diagnostics
export OPENCLAW_MODEL_OVERRIDE="anthropic/claude-opus-4-6"

# Run authorized repair
bash ~/.openclaw/workspace/scripts/emergency-repair/fix-billy-auth.sh --authorized-by Neill
```

### Setup (Run Once)
```bash
# Set up SSH keys first time
bash ~/.openclaw/workspace/scripts/emergency-repair/setup-billy-repair-keys.sh
```

## What It Does
1. **Verifies Neill's authorization** (security check)
2. **SSH into Billy** (EC2 via Tailscale)
3. **Backs up Billy's config** (safety first)
4. **Clears stale authentication tokens** (removes .token, device*.json)
5. **Removes hardcoded tokens** (prevents repeat issues)
6. **Restarts Billy's gateway** (fresh start)
7. **Verifies repair success** (tests authentication)
8. **Logs everything** (full audit trail)
9. **Reports back to Neill** (success/failure)

## Typical Conversation Flow

**Neill:** "SAPCONET, Billy is showing authentication errors again, please fix him"

**SAPCONET Response:**
```
🚨 Emergency repair authorized by Neill
🔧 Switching to Opus model for enhanced diagnostics
🔗 Connecting to Billy via SSH...
📋 Backing up Billy's configuration...
🧹 Clearing stale authentication tokens...
⚠️  Found hardcoded token - removing...
🔄 Restarting Billy's gateway...
⏳ Waiting for startup...
🧪 Testing authentication...
✅ SUCCESS: Billy's authentication restored!
📊 Repair completed in 45 seconds
```

## Error Handling

### SSH Connection Failed
- Check Billy is online
- Verify Tailscale connectivity  
- Confirm SSH key is installed on Billy

### Repair Failed
- Manual intervention required
- Provide Neill with full error logs
- Escalate with specific diagnostic info

### Uncertain Result
- Gateway responds but status unclear
- Recommend Neill verify manually
- Provide repair log for analysis

## Security Features
- **Neill-only authorization** - Script rejects unauthorized use
- **SSH key authentication** - Secure connection to Billy
- **Full audit logging** - Every action is recorded
- **Config backups** - Original settings preserved
- **Non-destructive** - Only removes auth tokens

## Prerequisites
- SSH key must be installed on Billy (one-time setup)
- Tailscale connectivity between SAPCONET and Billy
- Billy must be online and accessible

## Files Created
- `/home/neill/.openclaw/workspace/output/billy-repair-YYYYMMDD-HHMM.log`
- `~/.openclaw/openclaw.json.pre-repair-YYYYMMDD-HHMM` (backup on Billy)

## Testing
```bash
# Test SSH connection
ssh -i ~/.ssh/billy-repair-key ubuntu@100.90.73.34 'echo "Connection works"'

# Dry run (check authorization)
bash ~/.openclaw/workspace/scripts/emergency-repair/fix-billy-auth.sh
# Should show: "UNAUTHORIZED: This repair requires Neill's explicit authorization"
```

## Troubleshooting
If repair consistently fails:
1. Check Billy's system logs
2. Verify OpenClaw installation integrity
3. Consider full OpenClaw reinstall
4. Check for deeper system issues (disk space, permissions, etc.)

Remember: This is for **authentication emergencies only**. Use Opus model for complex diagnostics.