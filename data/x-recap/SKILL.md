---
name: x-recap
description: Monitor and recap official X (Twitter) updates using actionbook-rs screenshots. Use when the user asks to track/recap X posts (especially official accounts like @AnthropicAI/@claudeai), set up or fix cron-based X monitoring, troubleshoot X login/spinner blank timelines, or standardize the “fetch → screenshot → recap” workflow.
---

# X Recap (actionbook-rs)

Use **actionbook-rs** (`/Users/daboluo/.openclaw/workspace/bin/actionbook`) with `--profile x` to open X pages and save screenshots, then read screenshots to produce a recap.

## Canonical workflow (keep cron + scripts consistent)

### 0) Ensure X login (profile=x)
If timeline screenshots are blank/spinner-only, re-login:

```bash
cd /Users/daboluo/.openclaw/workspace
./bin/actionbook --profile x browser open https://x.com/home
```

### 1) Fetch (single source of truth)
- **Breaking (full-page)**: run `skills/x-recap/scripts/fetch_official_breaking.sh`
- **Daily (lightweight)**: run `skills/x-recap/scripts/fetch_official_daily.sh`

Do not re-implement fetch logic inside cron payloads; cron should only call these scripts.

### 2) Recap from screenshots
Output rules (suggested):
- If “major update”: emit 【快报】 + <=5 bullets + impacted **software stock categories** (no tickers) + 1–2 trading-framework ideas.
- If not major: either one-liner “无重大官方更新” or stay silent (depending on user preference).

## Resources
- Runbook (login + common failure modes): `references/runbook.md`
