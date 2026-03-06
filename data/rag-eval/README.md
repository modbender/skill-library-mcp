# 🧪 RAG Eval

**Quality testing suite for your OpenClaw RAG pipeline.**

Measures three core metrics using [Ragas](https://docs.ragas.io/):
- **Faithfulness** — Is the answer grounded in retrieved context? (hallucination detection)
- **Answer Relevancy** — Does the answer actually address the question?
- **Context Precision** — Did retrieval return the right chunks?

## 🛠️ Installation

### 1. Ask OpenClaw (Recommended)
Tell OpenClaw: *"Install the rag-eval skill."* The agent will handle the installation and configuration automatically.

### 2. Manual Installation (CLI)
If you prefer the terminal, run:
```bash
clawhub install rag-eval
```

## ⚠️ Prerequisites

1. **RAG system** — You need a RAG pipeline integrated with OpenClaw (vector DB + retrieval). This skill evaluates *output quality*, not RAG itself.
2. **LLM API key** — Ragas uses an LLM as judge. You need **at least one** of:
   - `OPENAI_API_KEY` (default — uses GPT-4o)
   - `ANTHROPIC_API_KEY` (uses Claude Haiku)
   - `RAGAS_LLM=ollama/llama3` (local, no API key needed)

If neither condition is met, this skill won't work.

## Use Cases

1. **Post-config regression** — Changed your embedding model, chunk size, or retrieval k? Run eval to see if quality improved or degraded
2. **Hallucination audit** — Spot-check whether your RAG answers are fabricating information not present in the retrieved context
3. **Golden Dataset CI** — Maintain a set of known Q&A pairs, run batch eval on schedule to track quality over time
4. **A/B model comparison** — Same questions, different models → compare faithfulness scores

## Quick Start

```bash
# Setup (once)
bash scripts/setup.sh

# Single eval
echo '{"question":"What is X?","answer":"X is...","contexts":["doc chunk 1","doc chunk 2"]}' \
  | python3 scripts/run_eval.py

# Batch eval
python3 scripts/batch_eval.py --input golden_set.jsonl --output report.json
```

## Score Guide

| Score | Verdict | Meaning |
|-------|---------|---------|
| 0.85+ | ✅ PASS | Production-ready |
| 0.70-0.84 | ⚠️ REVIEW | Needs tuning |
| < 0.70 | ❌ FAIL | Significant issues |

## Requirements

- Python 3.10+
- **At least one LLM API key** (see Prerequisites above)
- A working RAG pipeline producing question + answer + contexts

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RAGAS_PASS_THRESHOLD` | `0.85` | Score ≥ this → PASS |
| `RAGAS_REVIEW_THRESHOLD` | `0.70` | Score ≥ this → REVIEW (below → FAIL) |
| `RAGAS_OPENAI_MODEL` | `gpt-4o` | OpenAI model for LLM judge |
| `RAGAS_ANTHROPIC_MODEL` | `claude-haiku-4-5` | Anthropic model for LLM judge |
| `RAGAS_LLM` | _(none)_ | Custom LLM endpoint (e.g. `ollama/llama3`) |

## Cost

~$0.01-0.05 per evaluation (LLM judge calls). Batch of 100 ≈ $1-5.

## License

MIT