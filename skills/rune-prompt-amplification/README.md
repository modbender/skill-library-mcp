# 🪄 RUNE — Prompt Amplification Skill for OpenClaw

> *"Every prompt is a spell."*

RUNE transforms flat, ambiguous prompts into structured 8-layer XML prompts — resulting in dramatically better AI responses.

## What It Does

```
Input:  "Write a blog post about AI"
Output: <RUNE version="v4.3" domain="WRITING">
          <L0>Expert tech blogger persona...</L0>
          <L1>Domain context, target audience...</L1>
          <L2>Task definition, format...</L2>
          <L3>Constraints, ethics...</L3>
          <L4>CoT thinking strategy...</L4>
          <L5>Tools, integrations...</L5>
          <L6>QA validation criteria...</L6>
          <L7>Output format, style, length...</L7>
        </RUNE>
```

## The 8 Layers

| Layer | Name | Purpose |
|-------|------|---------|
| L0 | System Core | Role, persona, behavioral rules |
| L1 | Context Identity | Domain knowledge, target audience |
| L2 | Intent Scope | Task definition, output format |
| L3 | Governance | Constraints, ethical boundaries |
| L4 | Cognitive Engine | Thinking strategy (CoT, ToT) |
| L5 | Capabilities Domain | Tools, integrations, capabilities |
| L6 | QA | Validation criteria, quality control |
| L7 | Output Meta | Format, style, length, language |

## Install

```bash
npx clawhub@latest install neurabytelabs/rune-skill
```

## Requirements

- Python 3.11+
- RUNE repo cloned locally
- `RUNE_API_KEY` in `~/.secrets`

## Usage

```bash
# Simple
echo "Explain quantum computing" | bash main.sh

# As argument
bash main.sh "Write a marketing email for my SaaS"

# Pipe into your AI
ENHANCED=$(echo "Analyze this code" | bash main.sh)
```

## Why RUNE?

Most people give AI a flat prompt and get mediocre output.

RUNE applies prompt engineering best practices automatically — in under 2 seconds. ~45% higher quality outputs. Same effort.

Built on Spinoza's philosophical framework by NeuraByte Labs.

## Author

[Mustafa Saraç](https://mustafasarac.com) · [NeuraByte Labs](https://neurabytelabs.com)

## Related

- **RUNE Framework** → [github.com/neurabytelabs/rune](https://github.com/neurabytelabs/rune) — Core engine, wand.py, full docs
- **RUNE Playground** → [github.com/neurabytelabs/rune-playground](https://github.com/neurabytelabs/rune-playground) — Browser demo
