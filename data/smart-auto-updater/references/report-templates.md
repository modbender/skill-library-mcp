# Report Templates

## Short Report (Brief)

### Auto-Update Success
```
🟢 Updated: {old} → {new}
Skills: {updated}/{total}
Errors: {errors}
```

### Update Skipped
```
🟡 Update Available: {new}
Risk: {risk}
Action: Skipped
Reason: {reason}
```

## Medium Report (Detailed)

### Auto-Update Success
```
🟢 Smart Auto-Updater

✅ Updated: {old} → {new}

📊 Summary:
- OpenClaw: {old} → {new}
- Skills updated: {updated_count}
- Skills unchanged: {unchanged_count}
- Errors: {error_count}

📋 Key Changes:
{changes_summary}

🏗️ Impact: {impact_summary}

⏱️ Next check: {next_check}
```

### Update Skipped - LOW Risk Override
```
🟡 Smart Auto-Updater

Update Available: {new}

✅ Risk Assessment: LOW

📋 Changes:
{changes_summary}

🏗️ Impact: {impact_summary}

⚠️ Note: Auto-update enabled, but skipped due to configuration

💡 To auto-update LOW risk, set:
SMART_UPDATER_AUTO_UPDATE="LOW"

⏱️ Next check: {next_check}
```

### Update Skipped - MEDIUM Risk
```
🟠 Smart Auto-Updater

⚠️ Update Available: {new}

🚫 Risk Level: MEDIUM

📋 Changes:
{changes_summary}

🏗️ Impact Assessment:
- Architecture: {arch_impact}
- Performance: {perf_impact}
- Compatibility: {compat_impact}
- Security: {sec_impact}

🚫 Decision: SKIPPED

💡 Recommendations:
1. Review changelog manually
2. Test in staging environment
3. Update during maintenance window

⏱️ Next check: {next_check}
```

### Update Skipped - HIGH Risk
```
🔴 Smart Auto-Updater

🛑 Update Available: {new}

⚠️ Risk Level: HIGH

📋 Changes:
{changes_summary}

🏗️ Impact Assessment:
- Architecture: {arch_impact}
- Performance: {perf_impact}
- Compatibility: {compat_impact}
- Security: {sec_impact}

🛑 Decision: SKIPPED (CRITICAL)

🚨 Warnings:
{warnings}

💡 Required Actions:
1. Manual review REQUIRED
2. Backup current state
3. Plan maintenance window
4. Test thoroughly before production

📄 Full Changelog:
{full_changelog}

⏱️ Next check: {next_check}
```

## Full Report (Complete)

### Complete Auto-Update Report
```
🔄 Smart Auto-Updater - Complete Report

═══════════════════════════════════════
SYSTEM STATUS
═══════════════════════════════════════

OpenClaw:
  Current: {current_version}
  Latest:  {latest_version}
  Status:  {status}

Skills:
  Total:   {total_skills}
  Updated: {updated_skills}
  Current: {current_skills}
  Failed:  {failed_skills}

═══════════════════════════════════════
UPDATE DETAILS
═══════════════════════════════════════

Changelog:
{changelog}

═══════════════════════════════════════
RISK ASSESSMENT
═══════════════════════════════════════

Overall Risk: {risk_level}
Confidence:   {confidence}%

Breakdown:
  Architecture: {arch_score}/3 ({arch_impact})
  Performance:  {perf_score}/3 ({perf_impact})
  Compatibility:{compat_score}/3 ({compat_impact})
  Security:     {sec_score}/3 ({sec_impact})

Calculation:
  Score = ({arch_score} × 0.4) + ({perf_score} × 0.2) + ({compat_score} × 0.3) + ({sec_score} × 0.1)
  Score = {total_score}
  Risk = {risk_level}

═══════════════════════════════════════
IMPACT ANALYSIS
═══════════════════════════════════════

{impact_analysis}

═══════════════════════════════════════
DECISION
═══════════════════════════════════════

Action: {decision}
Reason: {decision_reason}

═══════════════════════════════════════
PERFORMANCE METRICS
═══════════════════════════════════════

Check Duration: {duration}ms
AI Analysis:    {ai_duration}ms
Total Time:     {total_duration}ms

═══════════════════════════════════════
NEXT STEPS
═══════════════════════════════════════

{next_steps}

═══════════════════════════════════════
Generated: {timestamp}
ID: {report_id}
═══════════════════════════════════════
```

## Emoji Indicators

| Risk Level | Emoji | Color | Auto-Update |
|------------|-------|-------|-------------|
| LOW | 🟢 | Green | ✅ Yes |
| MEDIUM | 🟡 | Yellow | ⚠️ No |
| HIGH | 🔴 | Red | 🚫 No |

## Channel Formatting

### Discord
```markdown
**Smart Auto-Updater Report**

**Status:** {status}
**Version:** {old} → {new}
**Risk:** {risk_level}

{summary}
```

### Slack
```markdown
🟢 *Smart Auto-Updater*
_Updated: {old} → {new}_
Risk: *{risk_level}*
{summary}
```

### Feishu
```markdown
**智能自动更新报告**

状态：{status}
版本：{old} → {new}
风险等级：{risk_level}

{summary}
```
