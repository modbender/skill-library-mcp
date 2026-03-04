---
name: rune-prompt-amplification
description: "Transforms any flat prompt into a structured 8-layer XML prompt using RUNE's semantic engine — delivering ~45% higher quality AI responses. Built on Spinoza's philosophical framework by NeuraByte Labs."
version: "1.0.0"
author: "Mustafa Saraç <mustafa@neurabytelabs.com>"
license: MIT
homepage: https://github.com/neurabytelabs/rune-skill
compatibility: Requires Python 3.11+, RUNE repo cloned locally, RUNE_API_KEY in ~/.secrets
---

# RUNE — Prompt Amplification Framework

RUNE transforms flat, ambiguous prompts into structured XML prompts validated by Spinoza's philosophical framework — resulting in outputs that are ~45% higher quality than raw prompting.

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

## Requirements

- Python 3.11+
- RUNE repo cloned locally
- `RUNE_API_KEY` in `~/.secrets`

## Usage

```bash
# Pipe a prompt
echo "Write a blog post about AI" | bash main.sh

# Pass as argument
bash main.sh "Explain quantum entanglement to a 12-year-old"
```

## Setup

```bash
# 1. Clone RUNE repo
git clone https://github.com/mrsarac/master-prompts ~/Documents/GitHub/rune

# 2. Add API key to ~/.secrets
echo "export RUNE_API_KEY=your_key" >> ~/.secrets

# 3. Test
echo "Hello" | bash main.sh
```

## Source

- **Author:** NeuraByte Labs
- **Version:** RUNE v4.3 / WAND v1.5.0
- **Repo:** https://github.com/neurabytelabs/rune-skill
