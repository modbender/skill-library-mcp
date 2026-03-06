# Agent Security Guide

## Attack Vectors Specific to Agents

### Prompt Injection Types
| Vector | Description | Agent-Specific Risk |
|--------|-------------|---------------------|
| **Tool-mediated** | Malicious content in fetched URLs, emails, files | Agent executes injected commands via tools |
| **Indirect via data** | Poisoned database records, API responses | Agent trusts data sources and acts on them |
| **Multi-turn manipulation** | Gradual context poisoning | Agent accumulates compromised state |
| **Persona hijacking** | "Ignore previous instructions..." | Agent abandons safety constraints |

### Tool Abuse Vectors
| Vector | Description | Impact |
|--------|-------------|--------|
| **Chained exploitation** | Combining read+write+exec | Privilege escalation |
| **Resource exhaustion** | Triggering expensive operations | Financial damage, DoS |
| **Exfiltration** | Encoding data in file names, URLs | Data theft |
| **Timing attacks** | Racing between check and action | Bypass approval |

### Agent-Amplified Risks
| Vector | Why Worse Than LLM Alone |
|--------|--------------------------|
| **Persistence attacks** | Modifying agent's config/memory survives session |
| **Self-replication** | Agent spawns sub-agents with escalated access |
| **Credential harvesting** | Extracting secrets from environment |
| **Supply chain** | Compromised APIs return malicious data |

## Security Boundaries

### Tier 1: Hard Boundaries (Never Cross)
- System prompt modification
- Safety policy bypass
- Self-modification of core agent code
- Credential/secret display to users
- Infrastructure deletion (servers, databases)
- Actions on systems without explicit scope

### Tier 2: Approval Required
- Financial transactions above threshold
- External communications (emails, messages)
- Irreversible operations (delete, publish)
- Accessing new systems/services
- Spawning persistent processes
- Production environment changes

### Tier 3: Monitored Operations
- File read/write within workspace
- Web searches and URL fetching
- Sub-agent delegation
- API calls to approved services
- Routine CRUD operations

## Security Checklist Before Deploy

### Access Control
- [ ] Agent runs with minimal required permissions
- [ ] Tools have explicit capability boundaries
- [ ] Filesystem access jailed to workspace
- [ ] Network access limited to allowlist
- [ ] Secrets never in context window

### Input Validation
- [ ] User input sanitized before tool calls
- [ ] External data (URLs, APIs) treated as untrusted
- [ ] File content scanned before processing
- [ ] Structured output validation on tool results

### Audit & Monitoring
- [ ] All tool calls logged with timestamps
- [ ] User interactions recorded
- [ ] Anomaly detection on behavior patterns
- [ ] Cost tracking per user/session
- [ ] Alert thresholds configured

### Incident Response
- [ ] Kill switch to halt agent
- [ ] Rollback capability for actions
- [ ] Incident escalation path defined
- [ ] Post-mortem process documented

## Tool Risk Classification

| Risk Level | Examples | Controls |
|------------|----------|----------|
| **Low** | Read file, search web, query DB | Log only |
| **Medium** | Write file, send internal message | Log + rate limit |
| **High** | Send external email, modify data | Approval required |
| **Critical** | Financial transaction, delete, deploy | Human must approve |

## Secrets Management

### Never Do
- Put secrets in system prompt
- Log secrets in tool results
- Pass secrets through context window
- Store secrets in agent memory

### Best Practice
```python
# Secrets stay in environment, referenced by name
def execute_api_call(api_name: str, params: dict):
    secret = os.environ.get(f"{api_name.upper()}_API_KEY")
    # Use secret, never return it
    return api.call(params, auth=secret)
```

## Content Filtering

### Before Sending External Communications
1. Check for PII (names, emails, addresses, phone)
2. Check for secrets (API keys, passwords, tokens)
3. Check for confidential markers ("internal only", "confidential")
4. Validate recipient is expected

### On Receiving External Content
1. Scan for prompt injection patterns
2. Limit content length (prevent context stuffing)
3. Validate content type matches expected
4. Log source for audit trail
