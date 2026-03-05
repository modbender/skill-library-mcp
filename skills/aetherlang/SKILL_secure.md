# AetherLang Ω — AI Workflow Orchestration

> Production-grade DSL for building AI workflows with 28 node types and enterprise security.

## Overview

AetherLang Ω is a visual programming language for AI that orchestrates multi-model workflows with built-in safety, debugging, and real-time collaboration. It processes natural language queries through specialized AI engines.

## Domains

| Domain | Description | Output |
|--------|-------------|--------|
| Chef Omega | Michelin-grade recipes with HACCP, costs, MacYuFBI flavor system | Full recipe with financials |
| APEX Strategy | Nobel-level business analysis (McKinsey/HBR quality) | 9-section strategic report |
| Grand Assembly | 26 legendary AI archetypes with Gandalf Safety Veto | Multi-perspective analysis |
| Consulting | SWOT, roadmaps, KPIs with implementation phases | Strategic consulting report |
| Lab | Scientific analysis across 50 domains | Research report with risk matrix |
| Marketing | Viral campaign generation with content calendars | Campaign strategy |
| OPAP Oracle | Live Greek lottery statistics and analysis | Statistical analysis with numbers |
| Cyber | Threat assessment with defense strategies | Security intelligence report |
| Academic | Multi-source research (arXiv, PubMed, OpenAlex) | Research synthesis |

## Security Features

AetherLang Ω includes enterprise-grade security:

- **Input Validation**: All inputs are validated server-side (length limits, character filtering)
- **Injection Prevention**: Pattern detection blocks code injection, SQL injection, XSS, and prompt manipulation
- **Rate Limiting**: 100 requests/hour per client with burst protection (10/10s)
- **Safety Guards**: Built-in GUARD node with STRICT/MODERATE/PERMISSIVE modes
- **Gandalf Veto**: AI safety review on Assembly outputs
- **Request Size Limits**: Max 5KB query, 10KB code, 50KB body
- **Audit Logging**: All blocked/sanitized requests are logged
- **Security Headers**: X-Content-Type-Options, X-Frame-Options on all responses

## API Usage

All API interactions are handled internally by OpenClaw with proper validation. The API validates:

1. **Field whitelist** — Only recognized fields are accepted
2. **Length enforcement** — Query ≤5000 chars, Code ≤10000 chars  
3. **Pattern detection** — Dangerous patterns are blocked before processing
4. **Type validation** — All fields are type-checked
5. **Sanitization** — Warning-level patterns are neutralized

### Blocked Patterns

The following are automatically blocked:
- Code execution attempts (`eval()`, `exec()`, `__import__`)
- SQL injection (`;DROP`, `;DELETE`)
- XSS (`<script>`)
- Template injection (`{{config}}`)
- OS command injection (`os.system`)

### Sanitized Patterns

The following are neutralized but allowed:
- Prompt override attempts ("ignore instructions")
- System prompt injection
- Jailbreak keywords

## Response Structure

```json
{
  "status": "success",
  "flow": "FlowName",
  "result": "...",
  "safe": true,
  "nodes_executed": 3,
  "execution_time": "32.1s"
}
```

## Error Responses

```json
{
  "error": "Input validation failed",
  "detail": "Specific reason",
  "status": 400
}
```

| Code | Meaning |
|------|---------|
| 400 | Invalid input or injection detected |
| 413 | Request too large |
| 429 | Rate limit exceeded (Retry-After header included) |
| 500 | Server error |

## Rate Limits

| Tier | Limit | Burst |
|------|-------|-------|
| Free | 100 req/hour | 10 req/10s |
| BYOK | 200 req/hour | 20 req/10s |
| Enterprise | Custom | Custom |

## Languages

AetherLang supports bilingual output:
- **English** (default)
- **Greek** (Ελληνικά) — full native support including Greeklish detection

## Technology

- **Backend**: FastAPI + Python 3.12
- **AI Models**: GPT-4o via OpenRouter
- **Hosting**: Hetzner EU (GDPR compliant)
- **Security**: Enterprise middleware with audit logging

## Links

- **Platform**: [aetherlang.neurodoc.app](https://aetherlang.neurodoc.app)
- **Documentation**: [docs.neurodoc.app](https://docs.neurodoc.app)
- **Status**: Production ✅

---

*Built by NeuroAether — From Kitchen to Code* 🧠
