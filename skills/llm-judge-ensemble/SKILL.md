---
name: llm-judge-ensemble
description: Build a cost-efficient LLM evaluation ensemble with sampling, tiebreakers, and deterministic validators. Learned from 600+ production runs judging local Ollama models.
homepage: https://github.com/reddinft/skill-llm-as-judge
metadata:
  {"openclaw": {"emoji": "⚖️", "requires": {"env": ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]}}}
---

# LLM-as-Judge

Build a cost-efficient LLM evaluation ensemble for comparing and scoring generative AI outputs at scale.

## When to Use

- Evaluating generative AI outputs across multiple models at scale (100+ runs)
- Comparing local/OSS models against cloud baselines in shadow-testing pipelines
- Building promotion gates where models must prove quality before serving production traffic
- Any scenario where deterministic tests alone can't capture output quality

## When NOT to Use

- One-off evaluations (just read the output yourself)
- Tasks with deterministic correct answers (use exact-match or unit tests)
- When you can't afford any external API calls (this pattern uses Claude/GPT as judges)

## Architecture: Three-Layer Evaluation

### Layer 1: Deterministic Validators (Free, Instant)

Run on 100% of outputs. Zero cost. Catches obvious failures before burning judge tokens.

- **JSON schema validation** — does the output parse? Does it match the expected schema?
- **Regex checks** — required fields present, format constraints met
- **Length bounds** — output within acceptable min/max character count
- **Entity presence** — do required entities from the input appear in the output?

If Layer 1 fails, score is 0.0 — no need to invoke expensive judges.

### Layer 2: Heuristic Drift Detection (Cheap, Fast)

Run on 100% of outputs that pass Layer 1. Minimal cost (local computation only).

- **Entity overlap** — what fraction of entities in the ground truth appear in the candidate?
- **Numerical consistency** — do numbers in the output match source data?
- **Novel fact detection** — does the output introduce facts not present in the input/context? Novel facts suggest hallucination.
- **Structural similarity** — does the output follow the same structural pattern as ground truth?

Layer 2 produces heuristic scores (0.0–1.0) that contribute to the final weighted score.

### Layer 3: LLM Judges (Expensive, High Quality)

**Sampled at 15% of runs** to control cost. Forced to 100% during promotion gates.

Two independent judges (e.g., Claude + GPT-4o) score the output. Each judge evaluates all 6 dimensions independently.

**Tiebreaker pattern:** When primary judges disagree by Δ ≥ 0.20 on any dimension, a third judge is invoked. The tiebreaker score replaces the outlier. This reduced score variance by 34% at only 8% additional cost.

## The 6 Scoring Dimensions

| Dimension | Weight | What It Measures |
|---|---|---|
| Structural accuracy | 0.20 | Format compliance, schema adherence |
| Semantic similarity | 0.25 | Meaning preservation vs ground truth |
| Factual accuracy | 0.25 | Correctness of facts, numbers, entities |
| Task completion | 0.15 | Does it actually answer the question? |
| Tool use correctness | 0.05 | Valid tool calls (when applicable) |
| Latency | 0.10 | Response time within acceptable bounds |

Weights are configurable per task type. Tool use weight is redistributed when not applicable.

## Critical Lesson: None ≠ 0.0

When a dimension is not sampled (LLM judge not invoked on this run), record the score as **null**, not 0.0. Unsampled dimensions must be **excluded from the weighted average**, not treated as failures.

Early bug: recording unsampled dimensions as 0.0 created a systematic 0.03–0.08 downward bias across all models. The fix: null means "not measured", which is fundamentally different from "scored zero".

```python
# WRONG — penalises unsampled dimensions
weighted = sum(s * w for s, w in zip(scores, weights)) / sum(weights)

# RIGHT — exclude null dimensions
pairs = [(s, w) for s, w in zip(scores, weights) if s is not None]
weighted = sum(s * w for s, w in pairs) / sum(w for _, w in pairs)
```

## Cost Estimate

With 15% LLM sampling, average cost per evaluated run: **~$0.003**

- Layer 1 + Layer 2: $0.00 (local computation)
- Layer 3 (15% of runs): ~$0.02 per judged run × 0.15 = ~$0.003
- Tiebreaker (fires ~12% of judged runs): adds ~$0.0003

At 200 runs for promotion: total judge cost ≈ $0.60 per model per task type.

## Worked Example: Summarisation Evaluation

```python
from evaluation import JudgeEnsemble, DeterministicValidator, HeuristicScorer

# Layer 1: must be valid text, 50-500 chars
validator = DeterministicValidator(
    min_length=50,
    max_length=500,
    required_format="text",
)

# Layer 2: check entity overlap with source
heuristic = HeuristicScorer(
    check_entity_overlap=True,
    check_novel_facts=True,
    check_numerical_consistency=True,
)

# Layer 3: LLM judges (sampled)
ensemble = JudgeEnsemble(
    judges=["claude-sonnet-4-20250514", "gpt-4o"],
    tiebreaker="claude-sonnet-4-20250514",
    sample_rate=0.15,
    tiebreaker_threshold=0.20,
    dimensions=["structural", "semantic", "factual", "completion", "latency"],
)

# Evaluate
result = ensemble.evaluate(
    task_type="summarize",
    ground_truth=gt_response,
    candidate=candidate_response,
    source_text=original_text,
    validator=validator,
    heuristic=heuristic,
)

print(f"Weighted score: {result.weighted_score:.3f}")
print(f"Dimensions: {result.scores}")  # {semantic: 0.95, factual: 0.88, ...}
# None values for unsampled dimensions
```

## Tips

- **Start with Layer 1** — you'd be surprised how many outputs fail basic validation
- **Log everything** — store raw judge responses for debugging score disputes
- **Calibrate on 50 runs** — before trusting the ensemble, manually review 50 outputs against judge scores
- **Watch for judge drift** — LLM judges can be inconsistent across API versions; pin model versions
- **Force judges at gates** — 15% sampling is fine for monitoring, but promotion decisions need 100% coverage on the final batch
