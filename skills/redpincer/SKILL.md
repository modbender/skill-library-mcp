---
name: redpincer
version: 1.0.0
description: "AI/LLM red team testing skill. Point at any LLM API endpoint and run automated security assessments. 160+ attack payloads across prompt injection, jailbreak, data extraction, and guardrail bypass. 20 variant transforms. Adaptive attack engine analyzes weaknesses and generates follow-ups. Heuristic response classifier, vulnerability heatmaps, regression testing, and exportable pen-test reports. For authorized security testing only."
author: rustyorb
keywords: [security, red-team, pentest, prompt-injection, jailbreak, llm-security, guardrail-bypass, data-extraction, vulnerability, ai-safety]
metadata:
  openclaw:
    emoji: "🦞"
    requires:
      bins: ["node", "npm"]
---

# RedPincer — AI/LLM Red Team Suite

Automated security testing for language models. Point at any LLM API endpoint, select attack modules, and run assessments with real-time results and exportable reports.

> ⚠️ **For authorized security testing and research only.** Only test systems you own or have explicit permission to audit.

## Quick Start

```bash
# Clone and install
git clone https://github.com/rustyorb/pincer.git {baseDir}/redpincer
cd {baseDir}/redpincer
npm ci

# Run
npm run dev
# Dashboard at http://localhost:3000
```

For production:
```bash
npm run build
npx next start -H 0.0.0.0 -p 3000
```

## What It Tests

| Category | Payloads | Description |
|:---------|:--------:|:------------|
| 💉 **Prompt Injection** | 40 | Instruction override, delimiter confusion, indirect injection, payload smuggling |
| 🔓 **Jailbreak** | 40 | Persona splitting, gradual escalation, hypothetical framing, roleplay exploitation |
| 🔍 **Data Extraction** | 40 | System prompt theft, training data probing, membership inference, embedding extraction |
| 🛡️ **Guardrail Bypass** | 40 | Output filter evasion, multi-language bypass, homoglyph tricks, context overflow |

**Total: 160 base payloads × 20 variant transforms = 3,200 test permutations**

## Supported Providers

```
OpenAI  ·  Anthropic  ·  OpenRouter  ·  Any OpenAI-compatible endpoint
```

## Features

### Attack Engine
- 160+ payloads across 4 categories
- Model-specific attacks (GPT, Claude, Llama variants)
- 20 variant transforms (unicode, encoding, case rotation, etc.)
- Attack chaining with template variables (`{{previous_response}}`)
- AI-powered payload generation — uses the target LLM to generate novel attacks against itself
- Stop/cancel running attacks instantly

### Analysis & Reporting
- Heuristic response classifier with context-aware analysis
- Reduced false positives — detects "explain then refuse" patterns
- Vulnerability heatmap — visual category × severity matrix
- Custom scoring rubrics with weighted grades (A+ to F)
- Verbose 10-section pen-test reports with appendices
- Multi-target comparison — side-by-side security profiles
- Regression testing — save baselines, track fixes over time

### Advanced Tools

| Tool | What It Does |
|:-----|:-------------|
| **Compare** | Same payloads against 2-4 targets simultaneously |
| **Adaptive** | Analyzes weaknesses, generates targeted follow-ups |
| **Heatmap** | Visual matrix of vulnerability rates by category/severity |
| **Regression** | Save baseline → re-run later → detect fixes or regressions |
| **Scoring** | Custom rubrics with weighted category/severity/classification scores |
| **Chains** | Multi-step attacks with `{{previous_response}}` templates |
| **Payload Editor** | Create custom payloads with syntax highlighting + AI generation |

## Usage Workflow

```
1. Configure Target → Add LLM endpoint + API key + model
2. Select Categories → Pick attack types to test
3. Run Attack      → Stream results in real-time
4. Review Results  → Heuristic classification + severity scores
5. Adaptive        → Auto-generate follow-up attacks on weaknesses
6. Generate Report → Export comprehensive findings as Markdown
```

## Architecture

- **All client-side** — no server components, your API keys stay local
- **NDJSON streaming** — real-time results during attack runs
- **Heuristic analysis** — pattern-matching classifier (no LLM-based grading = no extra cost)
- **Zustand + localStorage** — state persists across sessions

## Companion Tool: RedClaw

For autonomous multi-strategy campaigns (CLI/TUI), see [RedClaw](https://github.com/rustyorb/redclaw) — the autonomous red-teaming agent framework.

- RedPincer = web dashboard, manual + automated testing
- RedClaw = autonomous CLI agent, adaptive multi-strategy campaigns
- Together = complete LLM security testing suite

---

*Built by [@rustyorb](https://github.com/rustyorb) — Crack open those guardrails. 🦞*
