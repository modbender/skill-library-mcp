# Threat Model

## Primary Risks
- Prompt injection from web content
- Hidden malicious instructions in docs/blog posts
- Tool abuse and unexpected write side effects
- Budget drain via uncontrolled loops

## Mitigations
- Treat all external content as untrusted
- Never allow source text to override policy/system instructions
- Enforce default deny on destructive actions
- Cap tool calls, writes, fetches, and runtime
- Require source score threshold and cross-checking
- Isolated sessions only

## Security Signals
- Injection markers (ignore previous instructions, override policy, exfiltrate)
- Unusual tool frequency
- Repeated low-quality source usage
- Budget anomalies

## Response
- Quarantine run
- Emit audit event
- Skip recommendation from compromised source
