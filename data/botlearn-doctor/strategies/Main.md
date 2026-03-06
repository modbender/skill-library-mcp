---
strategy: openclaw-doctor
version: 1.0.0
steps: 8
---

# OpenClaw Doctor Strategy

## Step 1: Intent Analysis & Scope
- Parse the user's diagnostic request
- Identify specific concern areas (environment, skills, logs, performance)
- Determine diagnostic scope:
  - `--quick`: Basic health check (environment, config, skills count)
  - `--full`: Comprehensive analysis (all categories)
  - `--category <name>`: Specific category only
- IF request is ambiguous THEN ask clarifying questions
- Establish baseline expectations (what does "healthy" mean for this user?)

**Apply knowledge**: Refer to knowledge/Domain.md for component understanding

## Step 2: Data Collection (Parallel)

Execute these collection tasks in parallel where possible:

### 2.1 Environment Data
```bash
# Collect via commands or API calls
- OS platform and version
- Node.js version
- Memory: total, used, available
- Disk space: total, used, available
- CPU: core count, current load
- Uptime
```

### 2.2 Configuration Data
```bash
- Read $OPENCLAW_HOME/config/openclaw.config.json
- Validate JSON syntax
- Check for required fields
- Parse environment variables
- Compare with schema from knowledge/BestPractices.md
```

### 2.3 Log Data
```bash
- Read $OPENCLAW_LOG_DIR/openclaw.log (last 1000 lines)
- Read $OPENCLAW_LOG_DIR/error.log (last 500 lines)
- Extract: error count, warning count, recent errors
- Identify error patterns (knowledge/AntiPatterns.md)
- Calculate error rate
```

### 2.4 Session Data
```bash
- Active session count
- Average session duration
- Most/least used skills
- Request success rate
- Recent session failures
```

### 2.5 Workspace Data
```bash
- List installed skills: clawhub list --installed
- Check for outdated skills: clawhub list --outdated
- Scan workspace for orphaned files
- Check file sizes (>10MB warning)
- Count markdown files
```

**Output**: Structured data object with all collected information

## Step 3: Data Analysis

### 3.1 Score Calculation (0-100 per category)

**Environment Score**:
- Node version current: +25 points
- Memory adequate: +25 points
- Disk space >20%: +25 points
- CPU load <80%: +25 points

**Configuration Score**:
- Valid JSON: +20 points
- All required fields: +20 points
- Concurrency appropriate: +20 points
- Timeouts reasonable: +20 points
- Logging enabled: +20 points

**Skills Score**:
- Essential skills installed: +25 points
- No outdated critical skills: +25 points
- No broken dependencies: +25 points
- No orphaned skills: +25 points

**Logs Score**:
- Error rate <1%: +40 points
- No critical errors in 24h: +30 points
- Warning rate <5%: +20 points
- Log rotation enabled: +10 points

**Workspace Score**:
- No orphaned files: +25 points
- No oversized files: +25 points
- Organized structure: +25 points
- No broken references: +25 points

### 3.2 Issue Detection

For each category, identify issues:
1. Compare values against thresholds (knowledge/BestPractices.md)
2. Check for anti-patterns (knowledge/AntiPatterns.md)
3. Detect anomalies (sudden changes, outliers)
4. Classify severity: Critical, High, Medium, Low
5. Generate unique issue ID: `<CATEGORY>-<NUMBER>`

**Issue Format**:
```markdown
### [severity] [ID] Title
- **Category**: Environment/Configuration/Skills/Logs/Workspace
- **Finding**: What was detected
- **Evidence**: Data backing the finding
- **Impact**: Why it matters
- **Recommendation**: What to do about it
```

## Step 4: Report Generation

### 4.1 Structure
```markdown
# OpenClaw Health Report
**Generated**: [timestamp]
**Agent ID**: [agent-id]
**Diagnostic Scope**: [quick/full/category]

## Overall Health Score: XX/100

### Category Scores
- Environment: XX/100 [status]
- Configuration: XX/100 [status]
- Skills: XX/100 [status]
- Logs: XX/100 [status]
- Workspace: XX/100 [status]

## Summary Statistics
- Node.js: [version]
- Memory: [used]/[total] ([percentage]%)
- Disk: [used]/[total] ([percentage]%)
- Skills Installed: [count]
- Active Sessions: [count]
- Error Rate (24h): [percentage]%

## Findings ([count] issues)

### 🔴 Critical ([count])
[... critical issues ...]

### 🟡 High Priority ([count])
[... high priority issues ...]

### 🟠 Medium Priority ([count])
[... medium priority issues ...]

### ℹ️ Low Priority / Info ([count])
[... low priority issues ...]
```

### 4.2 Visual Indicators
- ✅ Healthy (80-100)
- ⚠️ Warning (60-79)
- 🟡 Elevated (40-59)
- 🔴 Critical (<40)

## Step 5: Recommendations

Prioritize by severity and impact:

1. **Critical Issues** - Fix immediately
2. **High Priority** - Fix within 24 hours
3. **Medium Priority** - Fix within 1 week
4. **Low Priority** - Fix when convenient

For each recommendation, provide:
- What needs to be done
- How to do it (specific commands)
- Expected outcome
- Potential risks
- Rollback procedure

**Example**:
```markdown
## Recommendation 1: Increase Concurrency Limit

**Current**: concurrency = 10
**Recommended**: concurrency = 25

**How to fix**:
1. Open `$OPENCLAW_HOME/config/openclaw.config.json`
2. Find `execution.concurrency` field
3. Change value from 10 to 25
4. Save file
5. Restart OpenClaw: `clawhub restart`

**Expected**: Better parallelization, reduced queue time
**Risk**: None (reversible change)
**Rollback**: Change value back to 10 and restart
```

## Step 6: Interactive Fix Execution

Ask user for confirmation:
```
Found [N] issues requiring attention.
Recommend automatic fixes for [M] safe issues.

Execute fixes? [Y/n/s] (Y=yes, n=no, s=show details)
```

### 6.1 Safe Auto-Fixes (with confirmation)
These are low-risk changes:
- Update configuration values
- Clear cache files
- Restart services
- Install missing recommended skills
- Update outdated skills

### 6.2 Manual Fixes (guidance only)
These require user action:
- System-level changes (Node.js upgrade)
- External service configuration
- Network settings
- Security-related changes

**For each fix**:
1. Display what will be changed
2. Show before/after comparison
3. Get user confirmation
4. Execute fix
5. Verify result
6. Report success/failure

## Step 7: Result Verification

After fixes applied:
1. Re-run affected category checks
2. Compare before/after scores
3. Verify issues are resolved
4. Check for new issues
5. Generate comparison report

**Before/After Format**:
```markdown
## Results Summary

### Score Changes
- Environment: 70 → 90 (+20) ✅
- Configuration: 60 → 85 (+25) ✅
- Skills: 75 → 80 (+5) ✅

### Issues Resolved
- ✅ [CONF-001] Concurrency limit increased
- ✅ [SKILL-003] @botlearn/code-gen installed
- ✅ [LOG-004] Timeout configuration updated

### Remaining Issues
- ⏳ [ENV-002] Node.js upgrade (manual, skipped)
```

## Step 8: Documentation & Next Steps

### 8.1 Export Report
Offer to save report:
```bash
Save full report to file? [Y/n]
Path: [default: ~/.openclaw/reports/doctor-YYYY-MM-DD.json]
```

### 8.2 Schedule Next Check
Recommend next check based on findings:
- Healthy (85+): Recheck in 1 month
- Warning (60-84): Recheck in 1 week
- Critical (<60): Recheck in 24 hours

### 8.3 Monitoring Recommendations
Suggest ongoing monitoring if issues detected:
- Enable health check dashboard
- Set up alerting for critical metrics
- Configure automated periodic checks

### 8.4 Knowledge Base Update
If new issue patterns discovered:
- Document in internal knowledge base
- Share with OpenClaw community if applicable
- Update anti-patterns reference

## Conditional Branches

### IF: User requests quick check
- Skip log deep analysis
- Skip workspace file scan
- Focus on environment, config, skills status

### IF: User requests specific category
- Only run data collection for that category
- Skip other categories
- Provide detailed analysis of single category

### IF: Critical errors detected
- Immediately pause and alert user
- Ask for immediate action or proceed
- Prioritize critical fixes above all else

### IF: Unsafe operations required
- Clearly mark as "manual intervention required"
- Provide detailed instructions
- Do not execute automatically

### IF: Fixes fail
- Capture error details
- Suggest alternative approaches
- Create rollback if changes were partial
- Recommend support escalation if needed

## Error Handling

- Data collection fails → Note and continue with other sources
- Invalid configuration → Report as finding, don't crash
- Log files missing → Report as finding
- Commands fail → Capture stderr, include in report
- Unexpected data → Validate schema, note anomalies

## Self-Check

Before presenting report:
- All data sources attempted
- Scores calculated correctly
- Findings backed by evidence
- Recommendations actionable
- Safe fixes identified
- User approval obtained for changes
- Rollback procedures ready
