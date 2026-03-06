# Recovery Procedures for Sacred Rule Violations

Each rule violation has specific recovery steps. Follow these procedures when you've broken a rule.

## Table of Contents
- Rule 1: Unverified Backup
- Rule 2: Manual JSON Edit  
- Rule 3: Unverified Config Keys
- Rule 4: Sandbox Without Backup
- Rule 5: Ignored Multi-Provider Failure
- Rule 6: Auth Command Without Environment
- Rule 7: Read auth-profiles.json Directly
- Rule 8: Ignored Session Corruption
- Rule 9: Stale In-Memory Cooldown (NEW!)

---

## Rule 1 Violation: Unverified Backup

**Symptom**: You assumed backup worked but files are missing/corrupted

**Recovery**:
1. Stop all OpenClaw processes immediately
2. Check if ANY valid config files exist:
   ```bash
   python3 -m json.tool ~/.openclaw/openclaw.json
   python3 -m json.tool ~/.openclaw/agents/main/agent/auth-profiles.json
   ```
3. If files are corrupted, restore from oldest known-good backup
4. If no backups exist, start fresh installation

## Rule 2 Violation: Manual JSON Edit

**Symptom**: Gateway won't start, JSON parse errors

**Recovery**:
1. Restore from backup immediately:
   ```bash
   cp backup/openclaw.json ~/.openclaw/
   ```
2. If no backup, validate syntax:
   ```bash
   python3 -m json.tool ~/.openclaw/openclaw.json
   ```
3. Fix JSON errors using proper JSON editor
4. Restart gateway: `openclaw gateway restart`

## Rule 3 Violation: Unverified Config Keys

**Symptom**: Gateway crashes, unknown configuration warnings

**Recovery**:
1. Restore from pre-change backup
2. Remove the unverified keys:
   ```python
   import json
   with open('~/.openclaw/openclaw.json') as f:
       config = json.load(f)
   # Remove the problematic keys
   del config['problematic_key']
   with open('~/.openclaw/openclaw.json', 'w') as f:
       json.dump(config, f, indent=2)
   ```
3. Restart gateway

## Rule 4 Violation: Sandbox Without Backup

**Symptom**: Auth cascade failures, all providers down

**Recovery**:
1. **IMMEDIATE**: Disable sandbox mode
2. If you have pre-sandbox backup, restore it
3. If no backup, manually disable in config:
   ```python
   import json
   with open('~/.openclaw/openclaw.json') as f:
       config = json.load(f)
   if 'agents' in config and 'defaults' in config['agents']:
       if 'sandbox' in config['agents']['defaults']:
           config['agents']['defaults']['sandbox']['mode'] = 'off'
   with open('~/.openclaw/openclaw.json', 'w') as f:
       json.dump(config, f, indent=2)
   ```
4. Restart gateway
5. Check auth status

## Rule 5 Violation: Ignored Multi-Provider Failure

**Symptom**: Assumed provider outage, didn't check recent config changes

**Recovery**:
1. List recent config changes:
   ```bash
   ls -la ~/.openclaw/openclaw.json
   ls -la ~/.openclaw/.env
   ls -la ~/.openclaw/agents/main/agent/auth-profiles.json
   ```
2. Identify what changed recently (check timestamps)
3. Restore from backup before the change
4. Re-apply changes one at a time with testing

## Rule 6 Violation: Auth Command Without Environment

**Symptom**: Auth commands fail, environment variables not found

**Recovery**:
1. Always prefix with environment:
   ```bash
   source ~/.openclaw/.env && openclaw auth <command>
   ```
2. Verify .env file exists and has correct permissions:
   ```bash
   ls -la ~/.openclaw/.env
   ```
3. If .env is missing, recreate with gateway password

## Rule 7 Violation: Read auth-profiles.json Directly

**Symptom**: Auth system corrupted, files modified unexpectedly

**Recovery**:
1. **NEVER READ THIS FILE AGAIN**
2. Restore from backup immediately:
   ```bash
   cp backup/auth-profiles.json ~/.openclaw/agents/main/agent/
   ```
3. Restart gateway
4. If no backup, regenerate auth profiles:
   ```bash
   source ~/.openclaw/.env && openclaw auth regenerate
   ```

## Rule 9 Violation: Stale In-Memory Cooldown (NEW!)

**Symptom**: All providers show "rate limited" or "unavailable" even though:
- Credentials are valid
- Cooldowns have expired in the file
- You just restarted the gateway

**Root Cause**: OpenClaw bug where in-memory cooldown tracking doesn't refresh when `cooldownUntil` timestamps expire in auth-profiles.json.

**Recovery**:
1. Run the cooldown reset script:
   ```bash
   ./scripts/reset_cooldowns.sh
   ```
2. Or manually edit auth-profiles.json:
   ```bash
   # Remove cooldownUntil, errorCount, lastFailureAt, failureCounts
   python3 -c "
   import json
   with open('$HOME/.openclaw/agents/main/agent/auth-profiles.json') as f:
       data = json.load(f)
   for k in data.get('usageStats', {}):
       data['usageStats'][k].pop('cooldownUntil', None)
       data['usageStats'][k]['errorCount'] = 0
       data['usageStats'][k].pop('lastFailureAt', None)
       data['usageStats'][k]['failureCounts'] = {}
   with open('$HOME/.openclaw/agents/main/agent/auth-profiles.json', 'w') as f:
       json.dump(data, f, indent=2)
   "
   ```
3. Restart gateway if issues persist:
   ```bash
   openclaw gateway restart
   ```

**Prevention**: This is a bug in OpenClaw - submit bug report!

**Symptom**: Orphaned tool_use blocks, incomplete responses

**Recovery**:
1. Tell user to `/reset` their session immediately
2. Check for other corrupted sessions:
   ```bash
   ls -la ~/.openclaw/agents/main/sessions/*.jsonl
   ```
3. Look for sessions with recent tool_use without tool_result
4. Archive corrupted sessions:
   ```bash
   mv corrupted-session.jsonl corrupted-session.jsonl.backup
   ```

## Emergency Recovery

If multiple rules are violated and system is unstable:

1. **Stop everything**: Kill all OpenClaw processes
2. **Restore from backup**: Use most recent known-good backup
3. **Fresh start**: If no backup, consider fresh installation
4. **Document**: Record what happened to prevent recurrence

## Prevention Checklist

Before making ANY config changes:

- [ ] Take verified backup using `scripts/safe_backup.sh`
- [ ] Validate current config with `scripts/config_validator.py`
- [ ] Document what you're about to change
- [ ] Have rollback plan ready
- [ ] Test in isolation if possible