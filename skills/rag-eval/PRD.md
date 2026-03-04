# PRD: Ragas Evaluation Skill for OpenClaw

## Overview
An OpenClaw skill that brings LLM evaluation (Ragas + DeepEval) directly into the agent workflow. Lets you measure answer quality, hallucination rate, and context relevance — without leaving OpenClaw.

## Problem
- OpenClaw agents produce outputs but there's no built-in way to evaluate quality
- ClawHub has 0 Ragas/DeepEval integration skills
- Enterprise customers need measurable AI reliability metrics (Jony's "AI Reliability Architect" positioning)
- Developers building RAG pipelines can't test quality without external tooling

## Target Users
1. OpenClaw power users building RAG / Q&A systems
2. Enterprise deployers who need audit-ready quality reports
3. Jony (portfolio demo for Reliability Architect job applications)

## Core Features

### v1.0 (MVP)
- **Evaluate a single response**: Given a question, answer, and retrieved context → run Ragas metrics
  - Faithfulness (did the answer hallucinate?)
  - Answer Relevancy (did it answer the question?)
  - Context Precision (was the retrieved context relevant?)
- **Output**: Structured JSON to stdout + human-readable summary
- **Storage**: Save results to `memory/eval-results/YYYY-MM-DD.jsonl`
- **No Python required**: Wrap Ragas via subprocess (pip install ragas if needed)

### v1.1
- **Batch evaluation**: Evaluate a golden dataset (CSV/JSONL of Q&A pairs)
- **Notion sync** _(future)_: Write eval reports to Notion database
- **Trend tracking**: Compare scores over time, alert if faithfulness drops below threshold

### v2.0
- **Demographic bias testing**: Evaluate performance across different user language styles (MIT paper insight)
- **DeepEval integration**: Add G-Eval, hallucination detector, toxicity checks
- **CI/CD hook**: Trigger eval on every model config change

## Technical Design

### Skill Trigger
Agent invokes this skill when user says:
- "evaluate this response"
- "run eval on [question/answer/context]"
- "check hallucination"
- "quality check"

### Implementation
```
eval_request:
  question: str
  answer: str       # LLM output to evaluate
  contexts: list    # Retrieved chunks used to generate answer
  metrics: list     # ["faithfulness", "answer_relevancy", "context_precision"]
```

Script: `scripts/run_eval.py`
- Uses `ragas` Python package
- Accepts JSON input via stdin
- Outputs JSON scores to stdout

### Dependencies
- Python 3.10+
- `pip install ragas datasets`
- OpenAI or Anthropic key (Ragas uses LLM-as-judge internally)

## Success Metrics
- Time to first eval: < 30 seconds
- Faithfulness score accuracy: matches manual human review within 10%
- ClawHub installs: 100+ in first month

## Files to Create
- `SKILL.md` — agent instructions
- `scripts/run_eval.py` — Python evaluation runner
- `scripts/setup.sh` — dependency installer
- `scripts/batch_eval.py` — batch mode runner
- `references/sample_dataset.jsonl` — example golden dataset
- `README.md` — user-facing docs
