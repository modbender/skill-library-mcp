---
name: email-verifier
description: |
  Verify email address deliverability via SMTP without sending mail. Checks MX records,
  performs RCPT TO verification, and detects catch-all domains. Use when validating email
  lists, checking if an email address exists before sending, cleaning lead lists, or
  verifying contact information. Supports single emails, batch verification, and CSV input.
---

# Email Verifier

Verify whether email addresses are deliverable by connecting to the recipient's mail server and checking if it accepts the address — without actually sending any mail.

## How It Works

1. **MX Lookup** — Resolves the domain's mail exchange server
2. **SMTP Handshake** — Connects to the MX server on port 25
3. **RCPT TO Check** — Asks the server if it would accept mail for the address
4. **Catch-All Detection** — Tests a random address to detect catch-all domains

## Dependencies

```bash
pip3 install dnspython
```

## Usage

### Single or multiple emails
```bash
python3 scripts/verify_email.py user@example.com another@domain.com
```

### From stdin
```bash
echo "user@example.com" | python3 scripts/verify_email.py --stdin
```

### From CSV (e.g., a lead list)
```bash
python3 scripts/verify_email.py --csv leads.csv --email-column "Contact Email"
```

### Options
- `--helo DOMAIN` — HELO domain for SMTP greeting (default: verify.local)
- `--timeout SECONDS` — Connection timeout (default: 10)

## Output

JSON array to stdout. Each result contains:

```json
{
  "email": "user@example.com",
  "domain": "example.com",
  "mx_host": "aspmx.l.google.com",
  "smtp_code": 250,
  "smtp_response": "2.1.5 OK",
  "deliverable": "yes"
}
```

### Deliverability values

| Value | Meaning |
|-------|---------|
| `yes` | Server accepted the recipient |
| `no` | Server rejected the recipient (invalid) |
| `catch-all` | Server accepts all addresses — cannot confirm inbox exists |
| `unknown` | Could not determine (timeout, block, greylisting) |

## Rate Limiting

The script includes built-in rate limiting to protect your IP reputation:

```bash
# Defaults: 1s between checks, max 20 per domain before 30s pause
python3 scripts/verify_email.py --csv leads.csv --email-column "Contact Email"

# Conservative: slower checks, lower burst limit
python3 scripts/verify_email.py --delay 3 --max-per-domain 10 --burst-pause 60 email@example.com

# Aggressive (not recommended from residential IPs)
python3 scripts/verify_email.py --delay 0.5 --max-per-domain 50 email@example.com
```

### Options
- `--delay SECONDS` — Pause between each check (default: 1.0)
- `--max-per-domain N` — Max checks to one domain before pausing (default: 20)
- `--burst-pause SECONDS` — How long to pause after hitting the per-domain limit (default: 30)

### Why rate limiting matters

SMTP verification connects directly to mail servers. Without rate limiting:
- **Your IP gets blacklisted** — Mail servers (especially Gmail, Microsoft) flag IPs that make many rapid RCPT TO requests. Once flagged, your IP may be blocked for hours or permanently.
- **Port 25 gets blocked** — ISPs monitor outbound port 25 traffic. Unusual volume can trigger automatic blocks.
- **Greylisting increases** — Servers that see rapid-fire checks start returning temporary failures, making your results less accurate.
- **It looks like spam reconnaissance** — Because that's exactly what spammers do. Legitimate use requires responsible pacing.

### Guidelines for agents

| Scenario | Recommended settings |
|----------|---------------------|
| Quick spot check (1-5 emails) | Defaults are fine |
| Small lead list (10-50 emails) | `--delay 2 --max-per-domain 15` |
| Larger batch (50-200 emails) | `--delay 3 --max-per-domain 10 --burst-pause 60` |
| Bulk verification (200+) | Use a dedicated service (ZeroBounce, NeverBounce) instead |

**Rule of thumb:** Stay under 50 unique domain checks per day from a residential IP. For repeated checks to the same domain (pattern guessing), stay under 15 per session.

## Limitations

- **Catch-all domains** accept all addresses; a "yes" doesn't guarantee a real inbox
- **Some servers block** SMTP verification (disconnect or timeout) — result will be "unknown"
- **Greylisting** temporarily rejects first attempts by design
- **Rate limiting** — don't bulk-verify hundreds from one IP; use a dedicated service for large lists
- **Port 25 blocked** — some ISPs/networks block outbound port 25; won't work from those environments
- Residential IPs may get flagged if used heavily — for bulk verification, prefer services like ZeroBounce or NeverBounce
