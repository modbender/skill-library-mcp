---
name: Compress
description: Compress text semantically with iterative validation, anchor checksums, and verified information preservation.
---

## ⚠️ Important Limitations

**This is SEMANTIC compression, not bit-perfect lossless.**
- L1-L2: Verified reconstruction, production-ready
- L3-L4: Experimental, may lose subtle information
- **Never use for:** Medical dosages, legal text, financial figures, safety-critical data

---

## The Validation Loop

```
1. Compress original O → compressed C
2. Extract anchors from O (entities, numbers, dates)
3. Reconstruct C → R (without seeing O)
4. Verify: anchors match + semantic diff
5. If mismatch → refine C with missing info
6. Repeat until validated (max 3 iterations)
```

**Convergence = verified. No convergence after 3 rounds = level too aggressive.**

---

## Quick Reference

| Task | Load |
|------|------|
| Compression levels (L1-L4) | `levels.md` |
| Validation algorithm details | `validation.md` |
| Format-specific strategies | `formats.md` |
| Token budgeting and metrics | `metrics.md` |

---

## Compression Levels

| Level | Ratio | Reliability | Use Case |
|-------|-------|-------------|----------|
| L1 | ~0.8x | ✅ High | Production, human-readable |
| L2 | ~0.5x | ✅ Good | System prompts, repeated use |
| L3 | ~0.3x | ⚠️ Moderate | Experimental, review output |
| L4 | ~0.15x | ⚠️ Low | Research only, expect losses |

---

## Anchor Checksum System

Before compression, extract critical facts:
```
[ANCHORS: 3 people, $42,000, 2024-03-15, "Project Alpha"]
```

Reconstruction MUST reproduce these exactly. If anchors mismatch → compression failed.

---

## Core Rules

1. **Always validate** — Never trust compression without reconstruction test
2. **Use anchors** — Extract numbers, names, dates before compressing
3. **Cap at L2 for production** — L3-L4 are experimental
4. **Report confidence** — Include iteration count and anchor match rate
5. **Independent verification** — Consider different model for reconstruction

---

## Cost-Benefit Reality

Each compression costs 3-4 LLM calls. Break-even calculation:
```
break_even_retrievals = compression_tokens / saved_tokens_per_use
```

**Only cost-effective if:** You'll retrieve the compressed content 6-8+ times.

For one-time use → just use the original text.

---

## Before Compressing

- [ ] Content type is NOT safety-critical
- [ ] Target level chosen (L1-L2 recommended)
- [ ] Anchors identified (numbers, names, dates)
- [ ] ROI makes sense (multiple retrievals expected)
