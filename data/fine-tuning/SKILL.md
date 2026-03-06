---
name: Fine-Tuning
slug: fine-tuning
description: Fine-tune LLMs with data preparation, provider selection, cost estimation, evaluation, and compliance checks.
---

## When to Use

User wants to fine-tune a language model, evaluate if fine-tuning is worth it, or debug training issues.

## Quick Reference

| Topic | File |
|-------|------|
| Provider comparison & pricing | `providers.md` |
| Data preparation & validation | `data-prep.md` |
| Training configuration | `training.md` |
| Evaluation & debugging | `evaluation.md` |
| Cost estimation & ROI | `costs.md` |
| Compliance & security | `compliance.md` |

## Core Capabilities

1. **Decide fit** — Analyze if fine-tuning beats prompting for the use case
2. **Prepare data** — Convert raw data to JSONL, deduplicate, validate format
3. **Select provider** — Compare OpenAI, Anthropic (Bedrock), Google, open source based on constraints
4. **Estimate costs** — Calculate training cost, inference savings, break-even point
5. **Configure training** — Set hyperparameters (learning rate, epochs, LoRA rank)
6. **Run evaluation** — Compare fine-tuned vs base model on task-specific metrics
7. **Debug failures** — Diagnose loss curves, overfitting, catastrophic forgetting
8. **Handle compliance** — Scan for PII, configure on-premise training, generate audit logs

## Decision Checklist

Before recommending fine-tuning, ask:
- [ ] What's the failure mode with prompting? (format, style, knowledge, cost)
- [ ] How many training examples available? (minimum 50-100)
- [ ] Expected inference volume? (affects ROI calculation)
- [ ] Privacy constraints? (determines provider options)
- [ ] Budget for training + ongoing inference?

## Fine-Tune vs Prompt Decision

| Signal | Recommendation |
|--------|----------------|
| Format/style inconsistency | Fine-tune ✓ |
| Missing domain knowledge | RAG first, then fine-tune if needed |
| High inference volume (>100K/mo) | Fine-tune for cost savings |
| Requirements change frequently | Stick with prompting |
| <50 quality examples | Prompting + few-shot |

## Critical Rules

- **Data quality > quantity** — 100 great examples beat 1000 noisy ones
- **LoRA first** — Never jump to full fine-tuning; LoRA is 10-100x cheaper
- **Hold out eval set** — Always 80/10/10 split; never peek at test data
- **Same precision** — Train and serve at identical precision (4-bit, 16-bit)
- **Baseline first** — Run eval on base model before training to measure actual improvement
- **Expect iteration** — First attempt rarely optimal; plan for 2-3 cycles

## Common Pitfalls

| Mistake | Fix |
|---------|-----|
| Training on inconsistent data | Manual review of 100+ samples before training |
| Learning rate too high | Start with 2e-4 for SFT, 5e-6 for RLHF |
| Expecting new knowledge | Fine-tuning adjusts behavior, not knowledge — use RAG |
| No baseline comparison | Always test base model on same eval set |
| Ignoring forgetting | Mix 20% general data to preserve capabilities |
