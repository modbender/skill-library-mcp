---
name: peer-review
description: |
  Multi-model peer review layer using local LLMs via Ollama to catch errors in cloud model output.
  Fan-out critiques to 2-3 local models, aggregate flags, synthesize consensus.

  Use when: validating trade analyses, reviewing agent output quality, testing local model accuracy,
  checking any high-stakes Claude output before publishing or acting on it.

  Don't use when: simple fact-checking (just search the web), tasks that don't benefit from
  multi-model consensus, time-critical decisions where 60s latency is unacceptable,
  reviewing trivial or low-stakes content.

  Negative examples:
  - "Check if this date is correct" → No. Just web search it.
  - "Review my grocery list" → No. Not worth multi-model inference.
  - "I need this answer in 5 seconds" → No. Peer review adds 30-60s latency.

  Edge cases:
  - Short text (<50 words) → Models may not find meaningful issues. Consider skipping.
  - Highly technical domain → Local models may lack domain knowledge. Weight flags lower.
  - Creative writing → Factual review doesn't apply well. Use only for logical consistency.
version: "1.0"
---

# Peer Review — Local LLM Critique Layer

> **Hypothesis:** Local LLMs can catch ≥30% of real errors in cloud output with <50% false positive rate.

---

## Architecture

```
Cloud Model (Claude) produces analysis
        │
        ▼
┌────────────────────────┐
│   Peer Review Fan-Out  │
├────────────────────────┤
│  Drift (Mistral 7B)   │──► Critique A
│  Pip (TinyLlama 1.1B) │──► Critique B
│  Lume (Llama 3.1 8B)  │──► Critique C
└────────────────────────┘
        │
        ▼
  Aggregator (consensus logic)
        │
        ▼
  Final: original + flagged issues
```

---

## Swarm Bot Roles

| Bot | Model | Role | Strengths |
|-----|-------|------|-----------|
| **Drift** 🌊 | Mistral 7B | Methodical analyst | Structured reasoning, catches logical gaps |
| **Pip** 🐣 | TinyLlama 1.1B | Fast checker | Quick sanity checks, low latency |
| **Lume** 💡 | Llama 3.1 8B | Deep thinker | Nuanced analysis, catches subtle issues |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/peer-review.sh` | Send single input to all models, collect critiques |
| `scripts/peer-review-batch.sh` | Run peer review across a corpus of samples |
| `scripts/seed-test-corpus.sh` | Generate seeded error corpus for testing |

### Usage

```bash
# Single file review
bash scripts/peer-review.sh <input_file> [output_dir]

# Batch review
bash scripts/peer-review-batch.sh <corpus_dir> [results_dir]

# Generate test corpus
bash scripts/seed-test-corpus.sh [count] [output_dir]
```

Scripts live at `workspace/scripts/` — not bundled in skill to avoid duplication.

---

## Critique Prompt Template

```
You are a skeptical reviewer. Analyze the following text for errors.

For each issue found, output JSON:
{"category": "factual|logical|missing|overconfidence|hallucinated_source",
 "quote": "...", "issue": "...", "confidence": 0-100}

If no issues found, output: {"issues": []}

TEXT:
---
{cloud_output}
---
```

---

## Error Categories

| Category | Description | Example |
|----------|-------------|---------|
| **factual** | Wrong numbers, dates, names | "Bitcoin launched in 2010" |
| **logical** | Non-sequiturs, unsupported conclusions | "X is rising, therefore Y will fall" |
| **missing** | Important context omitted | Ignoring a major counterargument |
| **overconfidence** | Certainty without justification | "This will definitely happen" on 55% event |
| **hallucinated_source** | Citing nonexistent sources | "According to a 2024 Reuters report..." |

---

## Discord Workflow

1. Post analysis to **#the-deep** (or #swarm-lab)
2. Drift, Pip, and Lume respond with independent critiques
3. Celeste synthesizes: deduplicates flags, weights by model confidence
4. If consensus (≥2 models agree) → flag is high-confidence
5. Final output posted with recommendation: `publish` | `revise` | `flag_for_human`

---

## Success Criteria

| Outcome | TPR | FPR | Decision |
|---------|-----|-----|----------|
| **Strong pass** | ≥50% | <30% | Ship as default layer |
| **Pass** | ≥30% | <50% | Ship as opt-in layer |
| **Marginal** | 20–30% | 50–70% | Iterate on prompts, retest |
| **Fail** | <20% | >70% | Abandon approach |

### Scoring Rules
- Flag = **true positive** if it identifies a real error (even if explanation is imperfect)
- Flag = **false positive** if flagged content is actually correct
- Duplicate flags across models count once for TPR but inform consensus metrics

---

## Dependencies

- Ollama running locally with models pulled: `mistral:7b`, `tinyllama:1.1b`, `llama3.1:8b`
- `jq` and `curl` installed
- Results stored in `experiments/peer-review-results/`

---

## Integration

When peer review passes validation:
- Package as Reef API endpoint: `POST /review`
- Agents call before publishing any analysis
- Configurable: model selection, consensus threshold, categories
- Log all reviews to `#reef-logs` with TPR tracking
