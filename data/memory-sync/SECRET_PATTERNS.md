# Secret Pattern Detection Strategy

This document describes the regex patterns used for secret detection in the memory-sync sanitization module.

## Pattern Ordering

**Order matters!** More specific patterns must come before generic ones to ensure correct redaction types.

The patterns are organized into three tiers:
1. **Explicit Key Patterns** - Service-specific formats with known prefixes
2. **Structural Patterns** - Format-based detection (JWT, SSH, hex, base64)
3. **Generic Patterns** - Catch-all for unknown key assignments

## Explicit Key Patterns

### LLM Providers

| Service | Pattern | Example | Redaction Type |
|---------|---------|---------|----------------|
| OpenAI | `sk-(?:proj-)?[a-zA-Z0-9]{30,}` | `sk-proj-abc123...` | `OPENAI-API-KEY` |
| Anthropic | `sk-ant-[a-zA-Z0-9\-_]{32,}` | `sk-ant-abc123...` | `ANTHROPIC-API-KEY` |
| OpenRouter | `sk-or-[a-zA-Z0-9]{32,}` | `sk-or-abc123...` | `OPENROUTER-API-KEY` |
| Composio | `ak-[a-zA-Z0-9]{20,}` | `ak-abc123...` | `COMPOSIO-API-KEY` |

### GitHub / Git

| Service | Pattern | Example | Redaction Type |
|---------|---------|---------|----------------|
| GitHub Token | `gh[pousr]_[A-Za-z0-9]{20,}` | `ghp_abc123...` | `GITHUB-TOKEN` |
| GitHub PAT | `github_pat_[A-Za-z0-9_]{22,}` | `github_pat_abc...` | `GITHUB-PAT` |

### AWS

| Service | Pattern | Example | Redaction Type |
|---------|---------|---------|----------------|
| Access Key | `AKIA[A-Z0-9]{16}` | `AKIAIOSFODNN7EXAMPLE` | `AWS-ACCESS-KEY` |
| Session Key | `ASIA[A-Z0-9]{16}` | `ASIAXYZ...` | `AWS-SESSION-KEY` |

### Communication / Channels

| Service | Pattern | Example | Redaction Type |
|---------|---------|---------|----------------|
| Telegram | `\d{9,10}:[A-Za-z0-9_-]{35}` | `123456789:ABC...` | `TELEGRAM-BOT-TOKEN` |
| Discord | `[A-Za-z0-9_-]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27}` | `MTIz...` | `DISCORD-BOT-TOKEN` |
| Slack | `xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*` | `xoxb-123...` | `SLACK-TOKEN` |

### Productivity / Integrations

| Service | Pattern | Example | Redaction Type |
|---------|---------|---------|----------------|
| Notion | `secret_[A-Za-z0-9]{32,}` | `secret_abc123...` | `NOTION-SECRET` |
| Google | `AIza[0-9A-Za-z_-]{35}` | `AIzaSyAbc...` | `GOOGLE-API-KEY` |

### Payment

| Service | Pattern | Example | Redaction Type |
|---------|---------|---------|----------------|
| Stripe Live | `sk_live_[0-9a-zA-Z]{24,}` | `sk_live_...` | `STRIPE-LIVE-KEY` |
| Stripe Test | `sk_test_[0-9a-zA-Z]{24,}` | `sk_test_...` | `STRIPE-TEST-KEY` |
| Stripe Pub | `pk_live_[0-9a-zA-Z]{24,}` | `pk_live_...` | `STRIPE-PUBLISHABLE-KEY` |

> **Note**: Stripe patterns are implemented but not unit tested. GitHub's Push Protection
> aggressively flags any string matching Stripe's format, even obviously fake test values.
> The patterns work correctly - verify manually with `sanitize_content("sk_live_...")`.

### Search / Data

| Service | Pattern | Example | Redaction Type |
|---------|---------|---------|----------------|
| Brave | `BSA[0-9a-zA-Z_-]{32,}` | `BSAabc123...` | `BRAVE-API-KEY` |
| Tavily | `tvly-[A-Za-z0-9]{32,}` | `tvly-abc...` | `TAVILY-API-KEY` |
| SerpAPI | `serp-[0-9a-z]{32,}` | `serp-abc...` | `SERPAPI-KEY` |

### Storage / Database

> **Removed patterns**: UUID and HEX-32 patterns were removed due to excessive false positives:
> - UUID pattern matched session IDs, message IDs, and other non-sensitive identifiers
> - HEX-32 pattern matched git commit hashes and MD5 checksums

## Structural Patterns

These detect secrets by their format rather than a known prefix.

| Type | Pattern | Notes | Redaction Type |
|------|---------|-------|----------------|
| JWT | `eyJ[a-zA-Z0-9_-]{5,}\.[a-zA-Z0-9_-]{5,}\.[a-zA-Z0-9_-]{5,}` | Base64 header.payload.signature | `JWT` |
| SSH Private | `-----BEGIN (?:RSA\|DSA\|EC\|OPENSSH )?PRIVATE KEY-----` | PEM format | `SSH-PRIVATE-KEY` |
| SSH Public | `ssh-(?:rsa\|dss\|ed25519\|ecdsa)\s+[A-Za-z0-9+/]{30,}` | OpenSSH format | `SSH-PUBLIC-KEY` |
| Connection | `(?:postgresql\|mysql\|mongodb\|redis)://...` | With embedded creds | `CONNECTION-STRING` |
| Hex 64 | `\b[0-9a-f]{64}\b` | Trello tokens, etc. | `HEX-TOKEN-64` |
| Base64 | `\b[A-Za-z0-9+/]{40,}={0,2}\b` | High-entropy strings | `BASE64` |

> **Removed**: HEX-32 pattern (`\b[0-9a-f]{32}\b`) was removed because it matches git commit hashes and MD5 checksums.

**Important:** Hex-64 pattern must come BEFORE base64 since hex characters are a subset of base64 characters.

## Generic Patterns

These catch unknown key/token assignments using flexible lengths (16+):

| Pattern Type | Example Match | Redaction Type |
|--------------|---------------|----------------|
| `api_key=VALUE` | `MY_API_KEY=abc123...` | `API-KEY` |
| `secret_key=VALUE` | `AWS_SECRET_KEY=xyz...` | `SECRET` |
| `access_token=VALUE` | `ACCESS_TOKEN=bearer...` | `ACCESS-TOKEN` |
| `auth_token=VALUE` | `AUTH_TOKEN=token...` | `AUTH-TOKEN` |
| `bearer TOKEN` | `Bearer eyJhbG...` | `BEARER-TOKEN` |
| `token=VALUE` | `user_token=abc...` | `TOKEN` |
| `password=VALUE` | `password=secret` | `PASSWORD` |
| `private_key=VALUE` | `privkey=base64...` | `PRIVATE-KEY` |
| `$ENV_VAR` | `$API_KEY`, `${SECRET}` | `ENV-VAR` |

## Known Environment Variables

The module also maintains a list of known sensitive environment variable names for classification:

```
OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENROUTER_API_KEY,
COMPOSIO_API_KEY, MOONSHOT_API_KEY, KIMI_API_KEY,
GITHUB_TOKEN, GH_TOKEN, GITHUB_PAT,
TELEGRAM_BOT_TOKEN, DISCORD_BOT_TOKEN, SLACK_BOT_TOKEN,
NOTION_API_KEY, NOTION_TOKEN, NOTION_SECRET,
TRELLO_API_KEY, TRELLO_TOKEN, GOOGLE_API_KEY,
STRIPE_API_KEY, STRIPE_SECRET_KEY, BRAVE_API_KEY,
TAVILY_API_KEY, SERPAPI_KEY, PINECONE_API_KEY,
SUPABASE_KEY, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY,
ELEVENLABS_API_KEY, OURA_PAT, AWS_ACCESS_KEY_ID,
AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, ...
```

## Design Rationale

### Minimum Lengths

| Pattern Type | Min Length | Rationale |
|--------------|------------|-----------|
| OpenAI keys | 30+ chars | Real keys are ~48-64 chars |
| Anthropic keys | 32+ chars | Real keys are ~100 chars |
| GitHub tokens | 20-40 chars | Standard is 36-40 |
| AWS keys | Exactly 20 | Fixed format: prefix + 16 |
| Generic assignments | 16+ chars | Catch variations, avoid false positives |
| Passwords | 8+ chars | Common minimum password length |

### False Positive Prevention

1. **Generic patterns use negative lookahead** (`(?!\[REDACTED)`) to avoid re-matching already-redacted content
2. **Hex patterns match before base64** since hex chars are subset of base64
3. **Specific patterns match before generic** to get correct redaction types
4. **Word boundaries (`\b`)** prevent matching substrings of larger words

## Testing

Run the security tests:

```bash
make test-security
```

This runs 50+ unit tests covering most pattern types, edge cases, and integration scenarios.

### Testing Limitations

Some patterns cannot be unit tested due to GitHub Push Protection:
- **Stripe keys**: GitHub flags any `sk_live_*`, `sk_test_*`, `pk_live_*`, `pk_test_*` pattern,
  even with obviously fake values like `sk_live_XXXXXXXX` or `sk_test_aaaa...`

These patterns are implemented and functional - verify manually:
```python
from memory_sync.sanitize import sanitize_content
sanitize_content("sk_live_abc123def456...")  # Returns [REDACTED-STRIPE-LIVE-KEY]
```
