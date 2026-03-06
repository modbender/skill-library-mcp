---
name: strava-training-coach
description: |
  AI running coach that prevents injuries by monitoring your Strava training load daily.
  Detects dangerous mileage spikes, intensity imbalances, and recovery gaps using evidence-based
  sports science (80/20 rule, acute:chronic workload ratio), then sends smart alerts to Discord
  or Slack before problems become injuries.

  Use when:
  - "Am I overtraining?" — Analyze weekly mileage and intensity for injury risk
  - "Check my training load" — Run a daily analysis of your Strava activities
  - "Send me a training report" — Generate a weekly summary with 4-week trends
  - "Is my running mileage safe?" — Calculate acute:chronic workload ratio (ACWR)
  - "Set up automated training alerts" — Schedule daily checks via cron
  - Monitoring heart rate to ensure easy days are actually easy (80/20 compliance)
  - Tracking recovery gaps and consistency streaks
  - Optional Oura ring integration for sleep and readiness scores

  Unlike basic Strava data skills, this coach actively monitors your patterns daily and alerts
  you before problems become injuries — backed by research from Seiler (2010), Gabbett (2016),
  and Stoggl & Sperlich (2014).

  Security: No hardcoded secrets, input validation, log redaction, webhook URL validation,
  secure token storage (XDG, 0600 permissions), rate limiting, 30s request timeouts.
homepage: https://developers.strava.com/docs/reference/
metadata: {"clawdbot":{"emoji":"🏃","tags":["fitness","strava","running","injury-prevention","training","alerts","discord","slack","health","marathon","overtraining","recovery","80-20-rule","heart-rate","coaching","endurance"],"requires":{"env":["STRAVA_CLIENT_ID","STRAVA_CLIENT_SECRET","DISCORD_WEBHOOK_URL or SLACK_WEBHOOK_URL"]}}}
---

# Strava Training Coach

Evidence-based AI training partner that catches injury risk before you feel it.

## Why This Matters

Most running injuries follow the same pattern: too much, too soon. Nielsen et al. (2014) found that runners who increase weekly distance by more than 30% have significantly higher injury rates. By the time you feel pain, the damage is weeks old.

This coach watches your Strava data daily and alerts you **before** problems become injuries — so you stay consistent instead of sidelined.

Built on the **80/20 polarized training model** (Seiler, 2010; Stoggl & Sperlich, 2014) — the same approach used by elite endurance coaches to build durable athletes who train smarter, not just harder.

## What You Get

- **ACWR Monitoring** — Tracks your acute:chronic workload ratio (Gabbett, 2016). ACWR > 1.5 = high injury risk
- **Acute Load Alerts** — Weekly mileage up 30%+? You'll know before your knees do
- **80/20 Intensity Checks** — Too many hard days eroding recovery? Get evidence-based recommendations
- **Recovery Nudges** — Extended gaps that might affect your training adaptations
- **Weekly Reports** — Sunday summaries with 4-week trends, ACWR, and intensity distribution
- **Oura Integration** — Optional sleep/readiness scores to inform training decisions

## Quick Start

### 1. Connect Strava

```bash
# Set your Strava API credentials (required)
export STRAVA_CLIENT_ID=your_id
export STRAVA_CLIENT_SECRET=your_secret

# Authenticate (opens browser for OAuth)
python3 scripts/auth.py
```

Tokens are stored in `~/.config/strava-training-coach/strava_tokens.json` with 0600 permissions.

### 2. Set Up Notifications (Required)

**Discord:**
```bash
export DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
export NOTIFICATION_CHANNEL=discord
```

**Slack:**
```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
export NOTIFICATION_CHANNEL=slack
```

⚠️ **Security:** Webhook URLs must be set via environment variables. No hardcoded URLs allowed.

### 3. Optional: Enable Oura Integration

```bash
export OURA_ENABLED=true
```

Requires Oura CLI authentication.

### 4. Run

```bash
# Daily training check + alerts
python3 scripts/coach_check.py

# Weekly summary report  
python3 scripts/weekly_report.py
```

Optional: schedule with cron for hands-off monitoring:

```json
{
  "name": "Training Coach - Daily Check",
  "schedule": {"kind": "every", "everyMs": 86400000},
  "command": "python3 scripts/coach_check.py"
}
```

## Security Features

This skill is designed with security in mind for ClawHub publication:

### Credential Handling
- **No hardcoded secrets** — All credentials via environment variables
- **Secure token storage** — Tokens saved with 0600 permissions
- **XDG compliance** — Config stored in `~/.config/strava-training-coach/`
- **Token validation** — Structure validation before use

### Input Validation
- **Date format validation** — ISO8601 format checking
- **Numeric range validation** — All thresholds bounded
- **Type checking** — Safe type conversion with defaults
- **Webhook URL validation** — Pattern matching for Discord/Slack

### Data Protection
- **Log redaction** — Sensitive data masked in logs
- **Secure temp files** — Proper permissions on state files
- **No data leakage** — Safe error messages
- **Rate limiting** — Max 1 alert per hour per type

### Network Security
- **HTTPS only** — All API calls use TLS
- **Timeout handling** — 30-second timeouts on all requests
- **Retry logic** — 3 attempts with exponential backoff
- **Certificate validation** — Standard SSL verification

## Configuration

All thresholds are optional — sensible defaults with validation.

```bash
# Training thresholds (validated ranges)
MAX_WEEKLY_MILEAGE_JUMP=30     # 5-100%, default: 30
MAX_HARD_DAY_PERCENTAGE=25     # 5-100%, default: 25
MIN_EASY_RUN_HEART_RATE=145    # 100-200 bpm, default: 145

# Feature flags
OURA_ENABLED=false             # Enable Oura integration
VERBOSE=false                  # Enable debug logging
```

## Example Alerts

### Injury Risk

> "Weekly mileage up 45% (18 -> 26 mi). ACWR: 1.62. Nielsen et al. (2014) found >30% weekly increases significantly raise injury risk. Your acute:chronic workload ratio is in the high-risk zone (>1.5). Reduce next week's volume by 20-30%."

> "60% of runs were moderate/high effort (HR >145). Seiler (2010) found elite athletes keep ~80% of sessions below VT1. Polarized training produces better VO2max gains than moderate-intensity training (Stoggl & Sperlich, 2014)."

> "5 days since last activity. Mujika & Padilla (2000) found VO2max begins declining after ~10 days of inactivity. A gentle 20-min walk or easy jog can maintain adaptations."

### Achievements

> "30-Day Streak! Consistency beats intensity. Holloszy & Coyle (1984) showed mitochondrial density increases with repeated aerobic stimulus."

### Weekly Reports (Sunday)

- Weekly mileage with week-over-week change %
- Acute:Chronic Workload Ratio (ACWR) with risk zone
- Intensity distribution (easy/moderate/hard) vs. 80/20 target
- 4-week trend visualization
- Evidence-based recommendations for next week

## Training Philosophy (Evidence-Based)

1. **Polarized Training** — 80% easy, 20% hard (Seiler & Kjerland, 2006; Stoggl & Sperlich, 2014)
2. **ACWR Sweet Spot** — Keep acute:chronic workload ratio between 0.8-1.3 (Gabbett, 2016)
3. **Progressive Overload** — Gradual increases; >30% weekly spikes raise injury risk (Nielsen et al., 2014)
4. **Consistency > Intensity** — Frequency drives mitochondrial and capillary adaptation (Holloszy & Coyle, 1984)
5. **Strength Training** — Reduces sports injuries by 68% and overuse injuries by ~50% (Lauersen et al., 2014)

See `references/training-principles.md` for the full guide with 30+ scientific references.

## Files

- `scripts/auth.py` — Strava OAuth setup (tokens stored in XDG config dir)
- `scripts/coach_check.py` — Daily training analysis and alerts (security-hardened)
- `scripts/weekly_report.py` — Sunday summary reports (security-hardened)
- `references/training-principles.md` — Evidence-based injury prevention guide

## Smart, Not Spammy

Alerts fire only when something matters:
- Mileage spike detected
- Intensity pattern concerning
- Meaningful PR achieved
- Weekly summary ready

Not every workout. That's what Strava is for.

## Rate Limits

- 1-2 API calls per check
- Strava allows 100 req/15 min, 1000/day
- Daily checks use ~30 requests/month
