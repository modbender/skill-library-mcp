---
name: openclaw-troubleshooting
description: "When users encounter OpenClaw-related issues or errors, search official docs and GitHub issues first, then provide solutions. Use for: feature malfunctions, error troubleshooting, version upgrade advice, configuration questions, and known issue verification."
---

# OpenClaw Troubleshooting

## Overview

When handling OpenClaw-related issues, follow the workflow of "check official resources first, then determine fix status."

## Workflow

### Step 1: Information Gathering

Confirm the following with the user (if not already provided):
- Current OpenClaw version (`openclaw --version`)
- Channel/platform being used (Feishu/Telegram/Discord/Slack, etc.)
- Specific problem symptoms (error messages, frequency, reproduction steps)
- Recent upgrades or configuration changes

### Step 2: Official Documentation Search

Search the official documentation for relevant content:
- URL: https://docs.openclaw.ai
- Search keywords: core issue terms (e.g., "feishu notification", "typing indicator", "cron job")

### Step 3: GitHub Issue Search

Search GitHub issues to confirm if this is a known problem:
- Issues URL: https://github.com/openclaw/openclaw/issues?q=is%3Aissue
- Search strategy (try in order):
  1. Exact search: issue keywords + channel name (e.g., "feishu reaction notification")
  2. Fuzzy search: channel name + feature module (e.g., "feishu typing")
  3. Error message search: extract key fields from error messages

### Step 4: Analyze Results and Report

Reply to the user using this structure:

```
**Problem Diagnosis**
- Symptom summary: (one sentence)
- Related GitHub issue: #[number] (if any)
- Fix status:
  - Fixed: version number + upgrade recommendation
  - Not fixed: temporary workaround + official fix progress
  - Configuration issue: provide correct configuration example
```

### Step 5: Record and Follow Up

If the issue is a known bug being fixed:
- Inform user of the expected fix version
- Record in todo list, remind user to verify after release

## Key Resources

### Quick Checklist

| Issue Type | Docs Section | GitHub Search Keywords |
|-----------|-------------|----------------------|
| Feishu notification issues | channels/feishu | feishu notification, reaction |
| Cron job problems | cron | cron job, schedule |
| Channel connection failures | onboarding | [channel] connection, webhook |
| Model invocation failures | models | [provider] error, fallback |
| Sandbox/execution issues | sandbox | sandbox, exec, security |

### CHANGELOG Check

- URL: https://raw.githubusercontent.com/openclaw/openclaw/main/CHANGELOG.md
- Purpose: Confirm whether a specific version includes a particular fix
- Search tip: Search for issue numbers (e.g., #28660) or feature keywords in CHANGELOG

## Response Template

Standard reply format for users:

---
Boss, I've checked. Here's the situation:

**Current version**: `x.x.x`
**Latest available version**: `x.x.x`
**GitHub issue**: [#number] title (if any)

**Fix status**:
- Version `x.x.x`: not fixed / fixed
- Version `x.x.x`: includes fix (CHANGELOG reference)

**Recommended solutions**:
1) Temporary workaround: (e.g., disable certain notification settings)
2) Permanent fix: (upgrade recommendation or wait for fix)

Which step would you like me to help with?
---

## Notes

- Prioritize the Fixes section in CHANGELOG to confirm fix versions
- If issue status is open, the fix is still in development
- For configuration issues, prioritize providing on-site verifiable solutions
- Record user wait decisions (e.g., "wait for next version"), follow up proactively
