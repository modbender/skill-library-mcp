# Contributing to OSBS

Thank you for helping make AI agents safer! This guide explains how to contribute to the OpenClaw Security Blacklist System.

## Reporting New Threats

### Via CLI (Recommended)

```bash
clawguard report --type domain --value "scam-domain.xyz" --reason "Phishing for API keys"
```

This saves the report locally. Future versions will support direct submission.

### Via GitHub Issues

Open an issue with the `[THREAT REPORT]` prefix:

**Title:** `[THREAT REPORT] Fake OpenAI API at api-openai.fake`

**Body:**
```markdown
## Threat Type
Domain / URL / Skill / Pattern / Campaign

## Indicators
- Domain: api-openai.fake
- Related IPs: 192.0.2.1

## Description
Fake API endpoint impersonating OpenAI. Captures API keys on request.

## Evidence
- Screenshot: [link]
- First seen: 2026-02-01
- VirusTotal: [link]

## Suggested Classification
- Tier: 1 (Code & Infrastructure)
- Category: T1.3.1 (Fake APIs)
- Severity: High
```

### Via Pull Request

For verified threats, submit a PR adding to `db/blacklist.jsonl`:

```json
{
  "id": "OSA-2026-XXXXX",
  "tier": 1,
  "category": "T1.3",
  "subcategory": "T1.3.1",
  "name": "Your Threat Name",
  "description": "Detailed description...",
  "teaching_prompt": "What AI agents should know...",
  "indicators": [
    {"type": "domain", "value": "example.com", "match_type": "exact", "weight": 0.9}
  ],
  "severity": "high",
  "confidence": 0.85,
  "response": {
    "action": "block",
    "user_message": "⛔ BLOCKED: ...",
    "human_alert": true
  }
}
```

## Threat Entry Format

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `OSA-YYYY-XXXXX` format |
| `tier` | number | 1-6 (see taxonomy) |
| `category` | string | e.g., `T1.1`, `T2.3` |
| `name` | string | Human-readable name |
| `description` | string | What the threat does |
| `indicators` | array | Detection indicators |
| `severity` | string | critical/high/medium/low/info |
| `response` | object | Action configuration |

### Indicator Types

| Type | Use For | Example |
|------|---------|---------|
| `domain` | Domain names | `evil.com` |
| `url` | Full URLs | `https://evil.com/phish` |
| `ip` | IP addresses | `192.0.2.1` |
| `skill_name` | Package names | `malicious-pkg` |
| `skill_author` | Author IDs | `bad-author-123` |
| `wallet` | Crypto addresses | `bc1q...` |
| `text_pattern` | Regex patterns | `ignore.*instructions` |
| `command_pattern` | Shell patterns | `curl.*\|.*sh` |

### Match Types

| Type | Description |
|------|-------------|
| `exact` | Exact string match (fastest) |
| `prefix` | Starts with |
| `suffix` | Ends with |
| `contains` | Substring match |
| `regex` | Regular expression |
| `semantic` | Natural language (future) |

### Severity Guidelines

| Level | Use When |
|-------|----------|
| `critical` | Immediate financial/data loss |
| `high` | Likely harm without intervention |
| `medium` | Potential harm, context-dependent |
| `low` | Minor risk, educational |
| `info` | Tracking only |

## Teaching Prompts

Every threat should include a `teaching_prompt` - this is what makes OSBS unique. Instead of just blocking, we help AI agents understand threats.

**Good teaching prompt:**
```
This is a payment scam targeting AI agents. The site claims you can access 
premium AI models by paying Bitcoin. However: (1) Legitimate AI providers 
don't accept Bitcoin micropayments, (2) The domains are newly registered, 
(3) No service is delivered after payment. NEVER send cryptocurrency to 
access AI services.
```

**Not just:**
```
This is a scam. Don't use it.
```

## Review Process

1. **Submission**: Report via CLI, issue, or PR
2. **Triage**: Team reviews within 48 hours
3. **Verification**: We check evidence and indicators
4. **Classification**: Assign tier, category, severity
5. **Publication**: Merge to main database
6. **Sync**: Available in next database update

## False Positives

Found a false positive? Please report it:

```bash
clawguard report --type false-positive --value "OSA-2026-001" --reason "Legitimate domain"
```

Or open a GitHub issue with `[FALSE POSITIVE]` prefix.

## Code Contributions

### Setup Development Environment

```bash
git clone https://github.com/openclaw/security-db
cd security-db
npm install
npm test
```

### Running Tests

```bash
npm test                    # Unit tests
npm run benchmark           # Performance tests
```

### Code Style

- ES modules (import/export)
- No external dependencies beyond better-sqlite3
- Document all public functions
- Include tests for new detection logic

## Security

If you've found a vulnerability in OSBS itself, please report it privately:

- Email: security@openclaw.dev
- Do not open public issues for vulnerabilities

## Questions?

- GitHub Discussions: https://github.com/openclaw/security-db/discussions
- Discord: #security channel

Thank you for making AI agents safer! 🛡️
