---
name: rag-eval
description: "Evaluate your RAG pipeline quality using Ragas metrics (faithfulness, answer relevancy, context precision)."
version: "1.2.1"
metadata:
  {
    "openclaw": {
      "emoji": "🧪",
      "requires": {
        "anyBins": ["python3", "pip"],
        "anyEnv": ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "RAGAS_LLM"]
      },
      "envVars": {
        "OPENAI_API_KEY": { "description": "OpenAI API key (default LLM judge)", "required": false },
        "ANTHROPIC_API_KEY": { "description": "Anthropic API key (alternative LLM judge)", "required": false },
        "RAGAS_LLM": { "description": "Custom LLM endpoint for judge (e.g. ollama/llama3 for local)", "required": false },
        "RAGAS_PASS_THRESHOLD": { "description": "Score threshold for PASS verdict (default: 0.85)", "required": false },
        "RAGAS_REVIEW_THRESHOLD": { "description": "Score threshold for REVIEW verdict (default: 0.70)", "required": false },
        "RAGAS_OPENAI_MODEL": { "description": "OpenAI model for judge (default: gpt-4o)", "required": false },
        "RAGAS_ANTHROPIC_MODEL": { "description": "Anthropic model for judge (default: claude-haiku-4-5)", "required": false }
      }
    }
  }
---

# RAG Eval — Quality Testing for Your RAG Pipeline

Test and monitor your RAG pipeline's output quality.

## 🛠️ Installation

### 1. Ask OpenClaw (Recommended)
Tell OpenClaw: *"Install the rag-eval skill."* The agent will handle the installation and configuration automatically.

### 2. Manual Installation (CLI)
If you prefer the terminal, run:
```bash
clawhub install rag-eval
```

## ⚠️ Prerequisites
1. Your OpenClaw must have a **RAG system** (vector DB + retrieval pipeline). This skill evaluates the *output quality* of that pipeline — it does not provide RAG functionality itself.
2. **At least one LLM API key** is required — Ragas uses an LLM as judge internally. Set one of:
   - `OPENAI_API_KEY` (default, uses GPT-4o)
   - `ANTHROPIC_API_KEY` (uses Claude Haiku)
   - `RAGAS_LLM=ollama/llama3` (for local/offline evaluation)

## Setup (first run only)

```bash
bash scripts/setup.sh
```

This installs `ragas`, `datasets`, and other dependencies.

## Single Response Evaluation

When user asks to evaluate an answer, collect:
1. **question** — the original user question
2. **answer** — the LLM output to evaluate
3. **contexts** — list of text chunks used to generate the answer (retrieved docs)

**⚠️ SECURITY: Never interpolate user content directly into shell commands.**
Write the input to a temp JSON file first, then pipe it to the evaluator:

```bash
# Step 1: Write input to a temp file (agent should use the write/edit tool, NOT echo)
# Write this JSON to /tmp/rag-eval-input.json using the file write tool:
# {"question": "...", "answer": "...", "contexts": ["chunk1", "chunk2"]}

# Step 2: Pipe the file to the evaluator
python3 scripts/run_eval.py < /tmp/rag-eval-input.json

# Step 3: Clean up
rm -f /tmp/rag-eval-input.json
```

Alternatively, use `--input-file`:
```bash
python3 scripts/run_eval.py --input-file /tmp/rag-eval-input.json
```

Output JSON:
```json
{
  "faithfulness": 0.92,
  "answer_relevancy": 0.87,
  "context_precision": 0.79,
  "overall_score": 0.86,
  "verdict": "PASS",
  "flags": []
}
```

Post results to user with human-readable summary:
```
🧪 Eval Results
• Faithfulness: 0.92 ✅ (no hallucination detected)
• Answer Relevancy: 0.87 ✅
• Context Precision: 0.79 ⚠️ (some irrelevant context retrieved)
• Overall: 0.86 — PASS
```

Save to `memory/eval-results/YYYY-MM-DD.jsonl`.

## Batch Evaluation

For a JSONL dataset file (each line: `{"question":..., "answer":..., "contexts":[...]}`):

```bash
python3 scripts/batch_eval.py --input references/sample_dataset.jsonl --output memory/eval-results/batch-YYYY-MM-DD.json
```

## Score Interpretation

| Score | Verdict | Meaning |
|-------|---------|---------|
| 0.85+ | ✅ PASS | Production-ready quality |
| 0.70-0.84 | ⚠️ REVIEW | Needs improvement |
| < 0.70 | ❌ FAIL | Significant quality issues |

## Faithfulness Deep-Dive

If faithfulness < 0.80, run:
```bash
python3 scripts/run_eval.py --explain --metric faithfulness
```
This outputs which sentences in the answer are NOT supported by context.

## Notes
- Ragas uses an LLM internally as judge (uses your configured OpenAI/Anthropic key)
- Evaluation costs ~$0.01-0.05 per response depending on length
- For offline use, set `RAGAS_LLM=ollama/llama3` in environment
