---
name: astrai-code-review
description: AI-powered code review with intelligent model routing — saves 40%+ vs always using the most expensive model
version: 1.0.0
homepage: https://github.com/beee003/astrai-openclaw
metadata:
  clawdbot:
    emoji: "🔍"
    requires:
      env: ["ASTRAI_API_KEY"]
    primaryEnv: "ASTRAI_API_KEY"
    files: ["plugin.py", "config.example.toml"]
tags: [code-review, inference, routing, cost-optimization, pr-review, diff, quality]
---

# Astrai Code Review

AI-powered code review with intelligent model routing.
Complex logic goes to powerful models. Formatting and style goes to fast, cheap ones. You save 40%+ without sacrificing quality.

## What it does

- **Smart routing for reviews**: Astrai analyzes the diff complexity and routes to the optimal model. A gnarly concurrency bug gets Opus. A missing semicolon gets Haiku. You only pay for the intelligence you need.
- **Structured output**: Every review returns typed issues with file, line number, severity (critical/warning/info), message, and a concrete suggestion.
- **Strictness modes**: Standard catches bugs and logic errors. Strict adds style and best-practice checks. Security mode focuses on vulnerabilities, injection, auth, and data exposure.
- **BYOK (Bring Your Own Keys)**: Your provider API keys stay with you. Astrai decides which model to use, then calls the provider using YOUR key. You pay providers directly.
- **Cost tracking**: Every review response includes the cost and how much you saved vs always using the most expensive model.
- **Local-only mode**: If you only set `ASTRAI_API_KEY` without provider keys, Astrai uses its own hosted models. Still routed intelligently, still cheap.

## Setup

1. Get a free API key at [as-trai.com](https://as-trai.com)
2. Set `ASTRAI_API_KEY` in your environment or skill config
3. Optionally add provider API keys for BYOK routing (e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`)
4. Run `/review` on any diff or PR

## Usage

```
/review                     Review the current diff (staged changes)
/review --strict            Strict mode: bugs + style + best practices
/review --focus security    Security-focused review (vulns, injection, auth)
/review --file src/auth.py  Review a specific file
```

### Examples

**Basic review of staged changes:**
```
/review
```
Returns issues found in the current diff with severity levels and suggestions.

**Strict review for a PR:**
```
/review --strict
```
Catches not just bugs but also style violations, naming issues, and missed best practices.

**Security audit:**
```
/review --focus security
```
Focuses on SQL injection, XSS, auth bypass, hardcoded secrets, insecure deserialization, and other vulnerability classes.

## Environment Variables

| Variable | Required | Description | Default |
|---|---|---|---|
| `ASTRAI_API_KEY` | Yes | Your API key from as-trai.com | -- |
| `ANTHROPIC_API_KEY` | No | Anthropic key for BYOK routing | -- |
| `OPENAI_API_KEY` | No | OpenAI key for BYOK routing | -- |
| `GOOGLE_API_KEY` | No | Google key for BYOK routing | -- |
| `DEEPSEEK_API_KEY` | No | DeepSeek key for BYOK routing | -- |
| `MISTRAL_API_KEY` | No | Mistral key for BYOK routing | -- |
| `GROQ_API_KEY` | No | Groq key for BYOK routing | -- |
| `TOGETHER_API_KEY` | No | Together key for BYOK routing | -- |
| `FIREWORKS_API_KEY` | No | Fireworks key for BYOK routing | -- |
| `COHERE_API_KEY` | No | Cohere key for BYOK routing | -- |
| `PERPLEXITY_API_KEY` | No | Perplexity key for BYOK routing | -- |
| `REVIEW_STRICTNESS` | No | standard, strict, or security | standard |

## External Endpoints

| Endpoint | Purpose | Data Sent |
|---|---|---|
| `https://as-trai.com/v1/chat/completions` | Code review inference via intelligent routing | Diff content, file context, review instructions |

## Security & Privacy

- All requests authenticated via API key in the Authorization header
- Diffs are sent to the Astrai routing API, which forwards to the selected provider
- In BYOK mode, provider keys are sent via encrypted header (`X-Astrai-Provider-Keys`) and never stored
- No diffs, code, or review results are retained by Astrai after the request completes
- Source code is fully open: [github.com/beee003/astrai-openclaw](https://github.com/beee003/astrai-openclaw)

## Model Invocation

This skill sends code diffs to the Astrai routing API. The router classifies the review complexity and selects the best model:

- **High complexity** (concurrency, security, architecture): Routes to Claude Opus, GPT-4o, or Gemini Pro
- **Medium complexity** (logic errors, missing edge cases): Routes to Claude Sonnet, GPT-4o-mini, or Gemini Flash
- **Low complexity** (formatting, typos, naming): Routes to Claude Haiku, GPT-4o-mini, or Gemini Flash

Your prompts are processed by third-party LLM providers according to the routing decision. In BYOK mode, calls are made using your own provider API keys.

## Pricing

Same as Astrai platform pricing:

- **Free**: 1,000 requests/day, smart routing, all strictness modes
- **Pro** ($49/mo): Unlimited requests, priority routing, analytics dashboard
- **Business** ($199/mo): Team dashboards, compliance exports, SLA guarantee
