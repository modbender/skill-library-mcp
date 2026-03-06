# OpenClaw Error Diagnostic Report

**Generated:** {TIMESTAMP}
**OpenClaw Version:** {VERSION}
**Report ID:** {REPORT_ID}

---

## System Information

**Operating System:** {OS_NAME} {OS_VERSION}
**Architecture:** {ARCH}
**Node.js Version:** {NODE_VERSION}
**pnpm Version:** {PNPM_VERSION}
**Docker Version:** {DOCKER_VERSION}

**Gateway Status:** {GATEWAY_STATUS}
**Gateway Uptime:** {UPTIME}
**Gateway Port:** {PORT}
**Gateway PID:** {PID}

---

## Errors Detected

### Critical Errors ({CRITICAL_COUNT})

{CRITICAL_ERRORS_LIST}

### High Priority Errors ({HIGH_COUNT})

{HIGH_ERRORS_LIST}

### Medium Priority Errors ({MEDIUM_COUNT})

{MEDIUM_ERRORS_LIST}

### Warnings ({WARNING_COUNT})

{WARNINGS_LIST}

---

## Detailed Diagnosis

### Error 1: {ERROR_CODE}

**Severity:** {SEVERITY}
**Category:** {CATEGORY}
**First Occurred:** {FIRST_OCCURRENCE}
**Last Occurred:** {LAST_OCCURRENCE}
**Occurrence Count:** {COUNT}

**Description:**
{ERROR_DESCRIPTION}

**Root Cause Analysis:**
{ROOT_CAUSE}

**Impact:**
{IMPACT_DESCRIPTION}

**Evidence:**
```
{LOG_EXCERPT}
```

**Recommended Fixes:**
1. {FIX_STEP_1}
2. {FIX_STEP_2}
3. {FIX_STEP_3}

**Auto-Fix Available:** {AUTO_FIX_AVAILABLE}
**Auto-Fix Command:**
```bash
{AUTO_FIX_COMMAND}
```

---

### Error 2: {ERROR_CODE}

**Severity:** {SEVERITY}
**Category:** {CATEGORY}
**First Occurred:** {FIRST_OCCURRENCE}
**Last Occurred:** {LAST_OCCURRENCE}
**Occurrence Count:** {COUNT}

**Description:**
{ERROR_DESCRIPTION}

**Root Cause Analysis:**
{ROOT_CAUSE}

**Impact:**
{IMPACT_DESCRIPTION}

**Evidence:**
```
{LOG_EXCERPT}
```

**Recommended Fixes:**
1. {FIX_STEP_1}
2. {FIX_STEP_2}

**Auto-Fix Available:** {AUTO_FIX_AVAILABLE}
**Auto-Fix Command:**
```bash
{AUTO_FIX_COMMAND}
```

---

## Configuration Analysis

**Config File:** {CONFIG_PATH}
**Config Valid:** {CONFIG_VALID}
**Schema Version:** {SCHEMA_VERSION}

**Issues Found:**
- {CONFIG_ISSUE_1}
- {CONFIG_ISSUE_2}
- {CONFIG_ISSUE_3}

**Deprecated Keys:**
- {DEPRECATED_KEY_1} → {NEW_KEY_1}
- {DEPRECATED_KEY_2} → {NEW_KEY_2}

---

## Component Status

### Gateway
- Status: {GATEWAY_STATUS}
- Port: {GATEWAY_PORT}
- Host: {GATEWAY_HOST}
- Uptime: {GATEWAY_UPTIME}
- Health: {GATEWAY_HEALTH}

### AI Providers
- **OpenAI:** {OPENAI_STATUS} - {OPENAI_DETAILS}
- **Anthropic:** {ANTHROPIC_STATUS} - {ANTHROPIC_DETAILS}
- **Google:** {GOOGLE_STATUS} - {GOOGLE_DETAILS}

### Channels
- **WhatsApp:** {WHATSAPP_STATUS} - {WHATSAPP_DETAILS}
- **Telegram:** {TELEGRAM_STATUS} - {TELEGRAM_DETAILS}
- **Discord:** {DISCORD_STATUS} - {DISCORD_DETAILS}
- **Slack:** {SLACK_STATUS} - {SLACK_DETAILS}
- **Signal:** {SIGNAL_STATUS} - {SIGNAL_DETAILS}

### Sandbox
- Docker: {DOCKER_STATUS}
- Image: {SANDBOX_IMAGE}
- Memory Limit: {MEMORY_LIMIT}
- Timeout: {TIMEOUT}
- Status: {SANDBOX_STATUS}

---

## Performance Metrics

**Resource Usage:**
- CPU: {CPU_USAGE}%
- Memory: {MEMORY_USAGE}MB / {MEMORY_TOTAL}MB ({MEMORY_PERCENT}%)
- Disk: {DISK_USAGE}GB / {DISK_TOTAL}GB ({DISK_PERCENT}%)

**Request Statistics:**
- Active Requests: {ACTIVE_REQUESTS}
- Pending Requests: {PENDING_REQUESTS}
- Failed Requests (1h): {FAILED_REQUESTS}
- Average Response Time: {AVG_RESPONSE_TIME}ms

**Rate Limits:**
- Current RPM: {CURRENT_RPM} / {MAX_RPM}
- Current TPM: {CURRENT_TPM} / {MAX_TPM}
- Quota Used: {QUOTA_USED}% ({QUOTA_REMAINING} remaining)

---

## Recent Logs

### Last 20 Error Lines
```
{ERROR_LOGS}
```

### Last 10 Warning Lines
```
{WARNING_LOGS}
```

---

## Fix Priority Matrix

| Priority | Error | Impact | Auto-Fix | Command |
|----------|-------|--------|----------|---------|
| 1 | {ERROR_1} | {IMPACT_1} | {AUTO_FIX_1} | `{COMMAND_1}` |
| 2 | {ERROR_2} | {IMPACT_2} | {AUTO_FIX_2} | `{COMMAND_2}` |
| 3 | {ERROR_3} | {IMPACT_3} | {AUTO_FIX_3} | `{COMMAND_3}` |
| 4 | {ERROR_4} | {IMPACT_4} | {AUTO_FIX_4} | `{COMMAND_4}` |
| 5 | {ERROR_5} | {IMPACT_5} | {AUTO_FIX_5} | `{COMMAND_5}` |

---

## Recommended Actions

### Immediate (Fix Now)
1. {IMMEDIATE_ACTION_1}
2. {IMMEDIATE_ACTION_2}
3. {IMMEDIATE_ACTION_3}

### Short-term (Fix Within 24h)
1. {SHORT_TERM_ACTION_1}
2. {SHORT_TERM_ACTION_2}

### Long-term (Preventive)
1. {LONG_TERM_ACTION_1}
2. {LONG_TERM_ACTION_2}

---

## Auto-Fix Summary

**Total Auto-Fixable Errors:** {AUTO_FIX_COUNT}
**Safe Auto-Fixes:** {SAFE_COUNT}
**Moderate Auto-Fixes:** {MODERATE_COUNT} (require confirmation)
**Risky Auto-Fixes:** {RISKY_COUNT} (require manual review)

**Batch Fix Commands:**
```bash
# Fix all safe issues
python3 scripts/error-fixer.py --fix-all-safe

# Fix moderate issues with confirmation
python3 scripts/error-fixer.py --auto-fix-moderate --interactive

# View what would be fixed
python3 scripts/error-fixer.py --fix-all-safe --dry-run
```

---

## Next Steps

1. Review errors by priority (Critical → High → Medium)
2. Run auto-fix for safe issues: `python3 scripts/error-fixer.py --fix-all-safe`
3. Address manual fixes following reference guides
4. Re-run diagnostics: `python3 scripts/enhanced-doctor.py`
5. Monitor logs: `openclaw logs --follow --level error`

---

## Additional Resources

- [Error Catalog](../references/error-catalog.md) - All error types
- [Troubleshooting Workflow](../references/troubleshooting-workflow.md) - Decision trees
- [Auto-Fix Capabilities](../references/auto-fix-capabilities.md) - Fix details
- [Diagnostic Commands](../references/diagnostic-commands.md) - CLI reference

**Category-Specific Guides:**
- [Authentication Errors](../references/authentication-errors.md)
- [Rate Limiting Errors](../references/rate-limiting-errors.md)
- [Gateway Errors](../references/gateway-errors.md)
- [Channel Errors](../references/channel-errors.md)
- [Sandbox Errors](../references/sandbox-errors.md)
- [Configuration Errors](../references/configuration-errors.md)
- [Installation Errors](../references/installation-errors.md)

---

## Support Information

**Report Generated By:** OpenClaw Doctor Pro v{DOCTOR_VERSION}
**Report Location:** {REPORT_PATH}

For additional help:
- GitHub Issues: https://github.com/openclaw/openclaw/issues
- Community Discord: https://discord.gg/openclaw
- Documentation: https://docs.openclaw.io

**Share this report when seeking support.**
