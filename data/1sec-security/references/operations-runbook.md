# 1-SEC Operations Runbook

Day-to-day operations guide for monitoring, investigating, and responding
to security events after 1-SEC is installed and running.

## Checking What's Happening

```bash
1sec status                    # Quick health check
1sec alerts                    # Recent alerts (default: last 20)
1sec alerts --severity HIGH    # Only HIGH and CRITICAL
1sec alerts --module llm_firewall  # Filter by module
1sec enforce status            # Is enforcement active? Dry-run?
1sec enforce history           # What actions were taken?
```

## Investigating an Alert

```bash
# Get alert details
1sec alerts get <alert-id>

# See what enforcement did about it
1sec enforce history --module <module-name>

# Check if the source IP was blocked
1sec threats --blocked

# See cross-module correlation
1sec correlator
```

## Handling False Positives

```bash
# Mark an alert as false positive
1sec alerts false-positive <alert-id>

# If an IP was wrongly blocked, disable enforcement temporarily
1sec enforce disable <module-name>

# Or switch to dry-run to stop all enforcement while you investigate
1sec enforce dry-run on

# Re-enable when done
1sec enforce dry-run off
1sec enforce enable <module-name>
```

## Tuning a Noisy Module

If a module generates too many alerts, you have several options:

```bash
# Option 1: Raise the severity threshold for that module
1sec config set enforcement.policies.<module>.min_severity HIGH

# Option 2: Disable enforcement for that module (still detects, won't act)
1sec enforce disable <module-name>

# Option 3: Switch to a less aggressive preset
1sec enforce preset safe
```

## Changing Presets After Install

```bash
# Preview what a preset does before applying
1sec enforce preset balanced --show

# Apply a new preset
1sec enforce preset balanced

# Apply with dry-run safety net
1sec enforce preset strict --dry-run
```

## Viewing Logs and Exporting Data

```bash
1sec logs --tail 100           # Recent engine logs
1sec logs --follow             # Live tail (like tail -f)
1sec export --format json      # Export all alerts as JSON
1sec export --format csv --output report.csv  # CSV for spreadsheets
1sec export --format sarif     # SARIF for GitHub/GitLab security tabs
```

## Managing Webhooks and Notifications

1-SEC supports native notification templates for Slack, Discord, Telegram,
PagerDuty, and Microsoft Teams.

```bash
# Check webhook delivery status
1sec enforce webhooks stats

# See failed deliveries
1sec enforce webhooks dead-letters

# Retry a failed delivery
1sec enforce webhooks retry <dead-letter-id>
```

### Configuring Webhook Templates

```yaml
# In enforcement policy webhook actions:
# Slack
params:
  url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  template: "slack"

# Discord
params:
  url: "https://discord.com/api/webhooks/YOUR/WEBHOOK"
  template: "discord"

# Telegram
params:
  url: "https://api.telegram.org/botYOUR_TOKEN/sendMessage"
  template: "telegram"
  chat_id: "-1001234567890"

# PagerDuty
params:
  url: "https://events.pagerduty.com/v2/enqueue"
  template: "pagerduty"
  routing_key: "YOUR_PD_ROUTING_KEY"

# Microsoft Teams
params:
  url: "https://outlook.office.com/webhook/YOUR/WEBHOOK"
  template: "teams"
```

Supported template names: `pagerduty` (or `pd`), `slack`, `teams` (or `msteams`),
`discord`, `telegram` (or `tg`), `generic`.

## Escalation and Approval Management

```bash
# See unacknowledged alerts with escalation timers
1sec enforce escalations

# See pending approval gates (if enabled)
1sec enforce approvals pending

# Approve or reject a pending action
1sec enforce approvals approve <id>
1sec enforce approvals reject <id>

# View approval history
1sec enforce approvals history
```

## Alert Batching and Action Chains

```bash
# View alert batcher stats (storm deduplication)
1sec enforce batching

# List action chain definitions
1sec enforce chains list

# View chain execution records
1sec enforce chains records
```

## Stopping and Restarting

```bash
1sec stop                      # Graceful shutdown
1sec up                        # Start again
1sec up --dry-run              # Validate config without starting
```

## Upgrading 1-SEC

```bash
# The binary checks for updates once per day on launch.
# To force an update check:
1sec selfupdate --check

# To update now:
1sec selfupdate

# Or download and verify manually from GitHub Releases:
VERSION="0.5.0"  # replace with target version
wget https://github.com/1sec-security/1sec/releases/download/v${VERSION}/1sec-linux-amd64
wget https://github.com/1sec-security/1sec/releases/download/v${VERSION}/checksums.txt
sha256sum -c checksums.txt 2>&1 | grep 1sec-linux-amd64
chmod +x 1sec-linux-amd64
sudo mv 1sec-linux-amd64 /usr/local/bin/1sec

# Restart after update:
1sec stop
1sec up
```

## Troubleshooting

```bash
1sec check          # Pre-flight validation
1sec doctor         # Health check with suggestions
1sec status --json  # Detailed engine state
1sec logs --tail 50 # Recent log entries
```

Common issues:
- "Port already in use" → another 1sec instance is running. Run `1sec stop` first.
- "Config not found" → run `1sec init` to generate a config, or use `--config <path>`.
- "API key invalid" → set `ONESEC_API_KEY` env var or use `--api-key`.
- Alerts firing but no enforcement → check `1sec enforce status`. Likely in dry-run
  mode. Run `1sec enforce dry-run off`.
- Module not detecting anything → verify it's enabled with `1sec modules`. Check
  `1sec logs` for errors.

## Command Quick Reference

| Task | Command |
|------|---------|
| Start engine | `1sec up` |
| Stop engine | `1sec stop` |
| Engine status | `1sec status` |
| View alerts | `1sec alerts` |
| Acknowledge alert | `1sec alerts ack <id>` |
| Resolve alert | `1sec alerts resolve <id>` |
| Mark false positive | `1sec alerts false-positive <id>` |
| List modules | `1sec modules` |
| Module details | `1sec modules info <name>` |
| Apply preset | `1sec enforce preset <name>` |
| Enforcement status | `1sec enforce status` |
| Action history | `1sec enforce history` |
| Toggle dry-run | `1sec enforce dry-run on\|off` |
| Blocked IPs | `1sec threats --blocked` |
| Webhook stats | `1sec enforce webhooks stats` |
| Escalation timers | `1sec enforce escalations` |
| Health check | `1sec doctor` |
| Pre-flight check | `1sec check` |
| Export alerts | `1sec export --format json` |
| Live dashboard | `1sec dashboard` |
| Help for command | `1sec help <command>` |
