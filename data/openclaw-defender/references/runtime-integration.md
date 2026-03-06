# Runtime Protection Integration Guide

**Version:** 1.1.0  
**Date:** 2026-02-07

---

## Overview

openclaw-defender v1.1.0 adds **runtime protection** to complement pre-installation auditing and file integrity monitoring. This guide explains how OpenClaw core should integrate with the runtime monitor.

---

## Architecture

### Before (v1.0): 2 Layers
1. Pre-installation auditing (audit-skills.sh)
2. File integrity monitoring (check-integrity.sh via cron)

### After (v1.1): 7 Layers
1. Pre-installation auditing
2. File integrity monitoring
3. **Runtime network monitoring** ⬅️ NEW
4. **Runtime file access control** ⬅️ NEW
5. **Runtime command validation** ⬅️ NEW
6. **RAG operation blocking** ⬅️ NEW
7. **Kill switch + analytics** ⬅️ NEW

---

## Integration Points

### 1. Skill Execution Lifecycle

**OpenClaw should call runtime-monitor.sh at these points:**

```javascript
// Before skill execution
async function executeSkill(skillName, taskInput) {
  // 1. Check kill switch
  const killSwitchActive = await exec(
    `~/.openclaw/workspace/skills/openclaw-defender/scripts/runtime-monitor.sh kill-switch check`
  );
  if (killSwitchActive.exitCode !== 0) {
    throw new Error("Kill switch active - all operations blocked");
  }
  
  // 2. Log skill start
  await exec(
    `~/.openclaw/workspace/skills/openclaw-defender/scripts/runtime-monitor.sh start "${skillName}"`
  );
  
  try {
    // 3. Execute skill with monitoring
    const result = await runSkillWithMonitoring(skillName, taskInput);
    
    // 4. Sanitize output
    const sanitizedOutput = await sanitizeOutput(result.output);
    
    // 5. Log skill end (success)
    await exec(
      `~/.openclaw/workspace/skills/openclaw-defender/scripts/runtime-monitor.sh end "${skillName}" 0`
    );
    
    return sanitizedOutput;
  } catch (error) {
    // 6. Log skill end (failure)
    await exec(
      `~/.openclaw/workspace/skills/openclaw-defender/scripts/runtime-monitor.sh end "${skillName}" 1`
    );
    throw error;
  }
}
```

### 2. Network Request Interception

**Before any web_search, web_fetch, browser, or external HTTP:**

```javascript
async function validateNetworkRequest(url, skillName) {
  const result = await exec(
    `~/.openclaw/workspace/skills/openclaw-defender/scripts/runtime-monitor.sh check-network "${url}" "${skillName}"`
  );
  
  if (result.exitCode !== 0) {
    // Blocked by runtime monitor
    throw new Error(`Network request blocked: ${url}`);
  }
  
  // Proceed with request
  return fetch(url);
}
```

### 3. File Access Interception

**Before read/write/exec tool calls:**

```javascript
async function validateFileAccess(filePath, operation, skillName) {
  // operation: "read", "write", "delete"
  const result = await exec(
    `~/.openclaw/workspace/skills/openclaw-defender/scripts/runtime-monitor.sh check-file "${filePath}" "${operation}" "${skillName}"`
  );
  
  if (result.exitCode !== 0) {
    // Blocked by runtime monitor (credential file or critical file)
    throw new Error(`File access blocked: ${operation} ${filePath}`);
  }
  
  // Proceed with file operation
}
```

### 4. Command Execution Validation

**Before exec tool calls:**

```javascript
async function validateCommand(command, skillName) {
  const result = await exec(
    `~/.openclaw/workspace/skills/openclaw-defender/scripts/runtime-monitor.sh check-command "${command}" "${skillName}"`
  );
  
  if (result.exitCode !== 0) {
    // Dangerous command blocked
    throw new Error(`Command execution blocked: ${command}`);
  }
  
  // Proceed with command
}
```

### 5. RAG Operation Blocking

**Before any embedding/retrieval operations:**

```javascript
async function validateRAGOperation(operation, skillName) {
  const result = await exec(
    `~/.openclaw/workspace/skills/openclaw-defender/scripts/runtime-monitor.sh check-rag "${operation}" "${skillName}"`
  );
  
  if (result.exitCode !== 0) {
    // RAG blocked (EchoLeak/GeminiJack vector)
    throw new Error(`RAG operation blocked: ${operation}`);
  }
  
  // Proceed (but we don't support RAG anyway)
}
```

### 6. Output Sanitization

**After skill execution, before returning to user:**

```javascript
async function sanitizeOutput(output) {
  const result = await exec(
    `echo "${output}" | ~/.openclaw/workspace/skills/openclaw-defender/scripts/runtime-monitor.sh sanitize`
  );
  
  return result.stdout;
  // Redacts: keys, emails, phones, base64 blobs, suspicious URLs
}
```

---

## Fallback Behavior

**If runtime-monitor.sh is not available:**

```javascript
function isRuntimeMonitorAvailable() {
  return fs.existsSync(
    path.join(process.env.HOME, '.openclaw/workspace/skills/openclaw-defender/scripts/runtime-monitor.sh')
  );
}

// In tool calls:
if (isRuntimeMonitorAvailable()) {
  await validateNetworkRequest(url, skillName);
}
// If not available, proceed without validation (backward compatibility)
```

---

## Configuration

**Environment variables:**

```bash
# Optional: Override workspace location
export OPENCLAW_WORKSPACE="/custom/path"

# Optional: Override log location
export OPENCLAW_LOGS="/custom/logs"
```

**Defaults:**
- Workspace: `$HOME/.openclaw/workspace`
- Logs: `$WORKSPACE/logs`

---

## Performance Considerations

**Overhead per skill execution:**
- Kill switch check: ~1ms (file read)
- Network validation: ~5ms (pattern matching)
- File access check: ~5ms (pattern matching)
- Command validation: ~5ms (pattern matching)
- Start/end logging: ~10ms (JSON append)

**Total: ~30ms overhead per skill (negligible)**

**Log rotation:**
```bash
# Add to monthly audit script
if [ $(stat -c%s ~/.openclaw/workspace/logs/runtime-security.jsonl) -gt 10485760 ]; then
  # Rotate if > 10MB
  mv runtime-security.jsonl runtime-security-$(date +%Y-%m-%d).jsonl.gz
  gzip runtime-security-$(date +%Y-%m-%d).jsonl
fi
```

---

## Testing

**Verify integration:**

```bash
# 1. Test kill switch check
./runtime-monitor.sh kill-switch check
# Should exit 0 (no kill switch)

# 2. Activate kill switch
./runtime-monitor.sh kill-switch activate "Test"

# 3. Test skill execution (should fail)
./runtime-monitor.sh start test-skill
# Should exit 1 (kill switch active)

# 4. Disable kill switch
./runtime-monitor.sh kill-switch disable

# 5. Test network validation
./runtime-monitor.sh check-network "https://coinglass.com" test-skill
# Should exit 0 (whitelisted)

./runtime-monitor.sh check-network "http://91.92.242.30/malware" test-skill
# Should exit 1 (blocked) and activate kill switch

# 6. Reset for next test
./runtime-monitor.sh kill-switch disable

# 7. Test file access
./runtime-monitor.sh check-file "$HOME/.env" read test-skill
# Should exit 1 (credential file blocked)

./runtime-monitor.sh check-file "$HOME/test.txt" read test-skill
# Should exit 0 (allowed)

# 8. Test command validation
./runtime-monitor.sh check-command "ls -la" test-skill
# Should exit 0 (safe command)

./runtime-monitor.sh check-command "rm -rf /" test-skill
# Should exit 1 (dangerous command)

# 9. Test RAG blocking
./runtime-monitor.sh check-rag "embedding_operation" test-skill
# Should exit 1 (RAG blocked)

# 10. Test output sanitization
echo "API_KEY=0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef" | ./runtime-monitor.sh sanitize
# Should output: API_KEY=[REDACTED_KEY]
```

---

## Monitoring & Alerting

**Check security status:**

```bash
# Daily: Analyze security events
./scripts/analyze-security.sh

# Weekly: Review security reports
ls -lh memory/security-report-*.md

# Monthly: Full audit
# (see main README.md)
```

**Set up alerts (optional):**

```bash
# Cron job for daily security check
0 9 * * * /path/to/analyze-security.sh && [ $(grep -c '"level":"CRITICAL"' /path/to/runtime-security.jsonl) -gt 0 ] && mail -s "OpenClaw Security Alert" admin@example.com < /path/to/security-report-$(date +\%Y-\%m-\%d).md
```

---

## Migration Path

### Phase 1: Install openclaw-defender v1.1.0 ✅
- Copy skill to workspace
- Run generate-baseline.sh
- Add integrity monitoring cron

### Phase 2: Core Integration (OpenClaw maintainers)
- Add runtime-monitor.sh calls to tool execution
- Test with existing skills
- Deploy to beta users

### Phase 3: Community Rollout
- Announce v1.1.0 on Discord/GitHub
- Update docs.openclaw.ai
- Encourage all agents to upgrade

---

## Backward Compatibility

**v1.0 skills work without changes.**

Runtime monitoring is **opt-in by OpenClaw core** (not enforced by skills themselves).

Skills don't need to know about runtime-monitor.sh - OpenClaw intercepts tool calls transparently.

---

## Security Guarantees

### What v1.1.0 Protects:
✅ Pre-installation vetting (audit-skills.sh)
✅ File integrity (check-integrity.sh)
✅ Network exfiltration (runtime-monitor.sh)
✅ Credential theft (runtime-monitor.sh)
✅ Dangerous commands (runtime-monitor.sh)
✅ RAG poisoning (runtime-monitor.sh)
✅ Memory poisoning (check-integrity.sh + runtime-monitor.sh)
✅ Kill switch on attack (runtime-monitor.sh)

### What it DOESN'T protect:
❌ Zero-day exploits in OpenClaw core
❌ Hardware-level attacks
❌ Social engineering (humans bypassing policies)
❌ Compromised npm dependencies (supply chain above skills)

**Defense in depth required. No single tool is sufficient.**

---

## FAQ

**Q: Does this slow down skill execution?**
A: ~30ms overhead per skill (negligible). Network/file/command validation is fast pattern matching.

**Q: What if runtime-monitor.sh is deleted by malware?**
A: File integrity monitoring (check-integrity.sh) will detect this and alert. Also, kill switch activations are logged before the script completes, so evidence remains.

**Q: Can skills bypass runtime-monitor.sh?**
A: Only if OpenClaw core doesn't enforce it. Integration is key. Skills themselves can't bypass if core validates all tool calls.

**Q: What's the false positive rate?**
A: Very low. Whitelists cover legitimate operations. Unknown patterns trigger WARN (not CRITICAL), requiring human review.

**Q: How do I add to whitelist?**
A: Edit runtime-monitor.sh `whitelist` arrays. Document why. Commit to git. Share with community if generally applicable.

---

**For questions, open an issue at: github.com/nightfullstar/openclaw-defender**

**Stay clawed. 🦞**
