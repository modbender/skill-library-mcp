---
name: llm-evaluator
version: 1.0.0
description: >
  LLM-as-a-Judge evaluator via Langfuse. Scores traces on relevance, accuracy,
  hallucination, and helpfulness using GPT-5-nano as judge. Supports single trace
  scoring, batch backfill, and test mode. Integrates with Langfuse dashboard for
  observability. Triggers: evaluate trace, score quality, check accuracy, backfill
  scores, test evaluator, LLM judge.
license: MIT
compatibility:
  openclaw: ">=0.10"
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      env: ["OPENROUTER_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
---

# LLM Evaluator ⚖️

LLM-as-a-Judge evaluation system powered by Langfuse. Uses GPT-5-nano to score AI outputs.

## When to Use

- Evaluating quality of search results or AI responses
- Scoring traces for relevance, accuracy, hallucination detection
- Batch scoring recent unscored traces
- Quality assurance on agent outputs

## Usage

```bash
# Test with sample cases
python3 {baseDir}/scripts/evaluator.py test

# Score a specific Langfuse trace
python3 {baseDir}/scripts/evaluator.py score <trace_id>

# Score with specific evaluator only
python3 {baseDir}/scripts/evaluator.py score <trace_id> --evaluators relevance

# Backfill scores on recent unscored traces
python3 {baseDir}/scripts/evaluator.py backfill --limit 20
```

## Evaluators

| Evaluator | Measures | Scale |
|-----------|----------|-------|
| relevance | Response relevance to query | 0–1 |
| accuracy | Factual correctness | 0–1 |
| hallucination | Made-up information detection | 0–1 |
| helpfulness | Overall usefulness | 0–1 |

## Credits

Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
