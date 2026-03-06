# Security Policy — log-dive

## Scope

log-dive is a **read-only** log search tool. It queries Loki, Elasticsearch, and CloudWatch for log data and returns results to the agent for analysis.

## Threat Model

### Data Sensitivity

**Logs are sensitive by nature.** They commonly contain:
- PII (usernames, emails, IP addresses, user agents)
- Authentication tokens and API keys (accidentally logged)
- Database queries with user data
- Internal service URLs and infrastructure details
- Request/response bodies with customer data

### Design Principles

1. **Read-only** — No write, delete, or admin API calls. Scripts explicitly use only search/read endpoints.
2. **No caching** — Log output is never written to disk, temp files, or persistent storage.
3. **No exfiltration** — Scripts output to stdout only. No network calls except to configured backends.
4. **Minimal auth surface** — Credentials are read from environment variables, never from files or user input.
5. **Input sanitization** — All JSON construction uses `jq --arg` to prevent injection. URL schemes are validated.

### What We Protect Against

| Threat | Mitigation |
|--------|-----------|
| Log data written to disk | Scripts never write files; output is stdout only |
| Query injection | All variables passed via `jq --arg`, never string interpolation into JSON |
| SSRF via backend URLs | URL scheme validation (http/https only) |
| Credential leakage | Env vars only; scripts never echo credentials |
| Accidental data modification | Only GET/POST-search endpoints used; no DELETE/PUT/admin APIs |
| Excessive data retrieval | Default --limit=200; scripts enforce maximum limits |

### What Is NOT In Scope

- **Backend authentication security** — We use whatever credentials the user provides. We don't validate token strength or rotation.
- **Network encryption** — We recommend HTTPS but don't enforce it (internal Loki instances often use HTTP).
- **LLM data retention** — Log data sent to the LLM is subject to the LLM provider's data policy. Users should be aware of this.

## Reporting Vulnerabilities

If you find a security issue in log-dive, please report it to: **security@cacheforge.dev**

Do not open a public issue for security vulnerabilities.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Current |

---

*Powered by Anvil AI 🤿*
