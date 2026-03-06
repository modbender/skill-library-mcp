#!/usr/bin/env python3
"""
run_eval.py — Ragas single-response evaluator for OpenClaw

Reads JSON from stdin:
    {"question": "...", "answer": "...", "contexts": ["chunk1", "chunk2"]}

Writes JSON scores to stdout:
    {"faithfulness": 0.92, "answer_relevancy": 0.87, "context_precision": 0.79,
     "overall_score": 0.86, "verdict": "PASS", "flags": []}

Flags:
    --metric METRIC [...]   Subset of metrics to run (default: all three)
    --explain               List answer claims NOT supported by context
    --no-save               Skip writing result to memory/eval-results/
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

# ── Metric name constants ─────────────────────────────────────────────────────
METRIC_NAMES = ("faithfulness", "answer_relevancy", "context_precision")

# Verdict thresholds (configurable via env vars)
PASS_THRESHOLD   = float(os.environ.get("RAGAS_PASS_THRESHOLD",   "0.85"))
REVIEW_THRESHOLD = float(os.environ.get("RAGAS_REVIEW_THRESHOLD", "0.70"))


# ── Error helpers ─────────────────────────────────────────────────────────────

def _die(msg: str, fix: str = "") -> None:
    """Print a JSON-formatted error to stderr and exit."""
    payload: dict = {"error": msg}
    if fix:
        payload["fix"] = fix
    print(json.dumps(payload, indent=2), file=sys.stderr)
    sys.exit(1)


def _check_deps() -> None:
    """Verify required packages are installed; exit with actionable hint if not."""
    missing = []
    for pkg in ("ragas", "datasets"):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        _die(
            f"Missing packages: {', '.join(missing)}",
            fix="Run:  bash scripts/setup.sh",
        )


# ── LLM setup ─────────────────────────────────────────────────────────────────

def _get_llm():
    """
    Build a Ragas-compatible LangchainLLMWrapper from environment variables.

    Priority:
      1. ANTHROPIC_API_KEY → Claude Haiku (fast, cheap)
      2. OPENAI_API_KEY    → GPT-4o-mini
      3. RAGAS_LLM=ollama/<model>  → local Ollama (offline)
    """
    ragas_llm_env = os.environ.get("RAGAS_LLM", "")

    # Anthropic — preferred when key present and not overridden by RAGAS_LLM
    if os.environ.get("ANTHROPIC_API_KEY") and not ragas_llm_env.startswith("ollama"):
        try:
            from langchain_anthropic import ChatAnthropic
            from ragas.llms import LangchainLLMWrapper
            model = os.environ.get("RAGAS_ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
            return LangchainLLMWrapper(ChatAnthropic(model=model, temperature=0))
        except ImportError:
            pass  # fall through to OpenAI

    # OpenAI
    if os.environ.get("OPENAI_API_KEY"):
        try:
            from langchain_openai import ChatOpenAI
            from ragas.llms import LangchainLLMWrapper
            model = os.environ.get("RAGAS_OPENAI_MODEL", "gpt-4o-mini")
            return LangchainLLMWrapper(ChatOpenAI(model=model, temperature=0))
        except ImportError:
            pass

    # Ollama (offline, e.g. RAGAS_LLM=ollama/llama3)
    if ragas_llm_env.startswith("ollama/"):
        try:
            from langchain_community.chat_models import ChatOllama
            from ragas.llms import LangchainLLMWrapper
            model_name = ragas_llm_env.split("/", 1)[1]
            return LangchainLLMWrapper(ChatOllama(model=model_name))
        except ImportError:
            _die(
                "Ollama requested but langchain-community not installed.",
                fix="pip install langchain-community",
            )

    _die(
        "No LLM configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.",
        fix=(
            "export OPENAI_API_KEY=sk-...       # OpenAI\n"
            "  export ANTHROPIC_API_KEY=sk-ant-...  # Anthropic (Claude)\n"
            "  RAGAS_LLM=ollama/llama3           # Offline via Ollama"
        ),
    )


def _get_embeddings():
    """
    Build embeddings wrapper for AnswerRelevancy metric.

    Falls back to HuggingFace (free, offline after first download) if
    OpenAI key is unavailable. Returns None if no embeddings can be set up —
    AnswerRelevancy will be skipped in that case.
    """
    # OpenAI embeddings (best quality)
    if os.environ.get("OPENAI_API_KEY"):
        try:
            from langchain_openai import OpenAIEmbeddings
            from ragas.embeddings import LangchainEmbeddingsWrapper
            return LangchainEmbeddingsWrapper(OpenAIEmbeddings())
        except ImportError:
            pass

    # HuggingFace fallback (no API key needed, slower first run)
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        from ragas.embeddings import LangchainEmbeddingsWrapper
        return LangchainEmbeddingsWrapper(
            HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        )
    except ImportError:
        pass

    return None  # caller will skip AnswerRelevancy


# ── Metric instantiation ──────────────────────────────────────────────────────

def _build_metrics(requested: list[str], llm, embeddings) -> tuple[list, list[str]]:
    """
    Instantiate Ragas metric objects for the requested metric names.

    Returns:
        (metric_objects, active_metric_names)

    Silently drops answer_relevancy if embeddings are unavailable.
    """
    try:
        from ragas.metrics import Faithfulness, AnswerRelevancy

        # Context precision: use the reference-free variant when available
        try:
            from ragas.metrics import LLMContextPrecisionWithoutReference as _CtxP
        except ImportError:
            from ragas.metrics import ContextPrecision as _CtxP  # older ragas alias

    except ImportError as exc:
        _die(f"ragas import error: {exc}", fix="bash scripts/setup.sh")

    # Build the pool of available metrics
    pool: dict[str, object] = {
        "faithfulness":      Faithfulness(llm=llm),
        "context_precision": _CtxP(llm=llm),
    }

    if embeddings:
        pool["answer_relevancy"] = AnswerRelevancy(llm=llm, embeddings=embeddings)
    elif "answer_relevancy" in requested:
        print(
            json.dumps({
                "warning": (
                    "answer_relevancy skipped — no embeddings available. "
                    "Set OPENAI_API_KEY or: pip install langchain-huggingface sentence-transformers"
                )
            }),
            file=sys.stderr,
        )
        requested = [m for m in requested if m != "answer_relevancy"]

    active = [m for m in requested if m in pool]
    return [pool[m] for m in active], active


# ── Core evaluation ───────────────────────────────────────────────────────────

def run_eval(
    question: str,
    answer: str,
    contexts: list[str],
    metrics_to_run: list[str],
    llm,
    embeddings,
) -> dict[str, float | None]:
    """
    Evaluate a single Q/A/context triple with Ragas.

    Returns a dict mapping standard metric names to float scores (0–1).
    A None value means the metric could not be computed.
    """
    try:
        from ragas import evaluate
        from ragas.dataset_schema import SingleTurnSample, EvaluationDataset
    except ImportError as exc:
        _die(f"ragas import error: {exc}", fix="bash scripts/setup.sh")

    metric_objs, active = _build_metrics(metrics_to_run, llm, embeddings)
    if not metric_objs:
        _die("No metrics could be initialized — nothing to evaluate.")

    # Build a single-sample Ragas dataset
    sample = SingleTurnSample(
        user_input=question,
        response=answer,
        retrieved_contexts=contexts,
    )
    dataset = EvaluationDataset(samples=[sample])

    try:
        result = evaluate(dataset=dataset, metrics=metric_objs)
    except Exception as exc:
        _die(f"Ragas evaluate() failed: {exc}")

    # Extract scores from the result object
    # metric.name gives the column name ragas uses (may differ from our std name)
    scores: dict[str, float | None] = {}
    for std_name, metric_obj in zip(active, metric_objs):
        ragas_col = metric_obj.name  # e.g. "faithfulness", "llm_context_precision_without_reference"
        try:
            df = result.to_pandas()
            val = df[ragas_col].iloc[0]
            scores[std_name] = round(float(val), 4)
        except Exception:
            # Fallback: try dict-style access on the result object
            try:
                val = result[ragas_col]
                if hasattr(val, "__iter__") and not isinstance(val, str):
                    val = list(val)[0]
                scores[std_name] = round(float(val), 4)
            except Exception:
                scores[std_name] = None

    return scores


# ── Faithfulness deep-dive (--explain) ────────────────────────────────────────

def explain_faithfulness(
    question: str,
    answer: str,
    contexts: list[str],
    llm,
) -> list[str]:
    """
    Ask the judge LLM to identify which answer sentences are NOT supported
    by the retrieved context.

    Returns a list of unsupported claim strings.
    """
    context_block = "\n---\n".join(contexts)
    prompt = (
        "You are a factual accuracy auditor.\n\n"
        "RETRIEVED CONTEXT:\n"
        f"{context_block}\n\n"
        "ANSWER TO EVALUATE:\n"
        f"{answer}\n\n"
        "List every sentence or specific claim in the ANSWER that CANNOT be "
        "directly verified from the CONTEXT above.\n"
        "Return your answer as a JSON array of strings.\n"
        "If every claim is supported, return [].\n"
        "Output ONLY the JSON array — no explanations, no markdown."
    )

    try:
        # Access the underlying LangChain model through the ragas wrapper
        model = getattr(llm, "langchain_llm", llm)
        from langchain_core.messages import HumanMessage
        response = model.invoke([HumanMessage(content=prompt)])
        text = response.content if hasattr(response, "content") else str(response)

        # Extract the JSON array from the response
        start, end = text.find("["), text.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        return []
    except Exception as exc:
        return [f"(explain error: {exc})"]


# ── Scoring helpers ───────────────────────────────────────────────────────────

def compute_verdict(
    scores: dict[str, float | None]
) -> tuple[float, str, list[str]]:
    """
    Compute overall score, verdict string, and flag list from metric scores.

    Returns:
        (overall_score, verdict, flags)
    """
    valid = {k: v for k, v in scores.items() if v is not None}
    overall = round(sum(valid.values()) / len(valid), 4) if valid else 0.0

    flags: list[str] = []
    if valid.get("faithfulness", 1.0) < 0.80:
        flags.append("hallucination_risk")
    if valid.get("context_precision", 1.0) < 0.75:
        flags.append("low_context_precision")
    if valid.get("answer_relevancy", 1.0) < 0.75:
        flags.append("low_answer_relevancy")

    if overall >= PASS_THRESHOLD:
        verdict = "PASS"
    elif overall >= REVIEW_THRESHOLD:
        verdict = "REVIEW"
    else:
        verdict = "FAIL"

    return overall, verdict, flags


# ── Persistence ───────────────────────────────────────────────────────────────

def save_result(result: dict) -> None:
    """Append evaluation result to memory/eval-results/YYYY-MM-DD.jsonl."""
    today = datetime.date.today().isoformat()
    out_dir = Path("memory/eval-results")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / f"{today}.jsonl", "a") as fh:
        fh.write(json.dumps(result) + "\n")


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate a single LLM response with Ragas metrics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 scripts/run_eval.py --input-file input.json\n"
            "  python3 scripts/run_eval.py --explain --metric faithfulness < input.json\n"
            "\n"
            "SECURITY: Prefer --input-file over piping echo with user content.\n"
            "Shell interpolation of user strings can cause command injection."
        ),
    )
    parser.add_argument(
        "--metric",
        nargs="+",
        default=list(METRIC_NAMES),
        choices=list(METRIC_NAMES),
        metavar="METRIC",
        help=f"Metrics to run (default: all). Choices: {', '.join(METRIC_NAMES)}",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help=(
            "After scoring, ask the LLM to identify which answer sentences "
            "are not supported by the retrieved context."
        ),
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not write result to memory/eval-results/YYYY-MM-DD.jsonl",
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default=None,
        help="Read input JSON from file instead of stdin (safer than shell interpolation)",
    )
    args = parser.parse_args()

    # 1. Verify dependencies
    _check_deps()

    # 2. Read JSON input from file or stdin (file is safer — avoids shell injection)
    try:
        if args.input_file:
            with open(args.input_file, 'r') as f:
                data = json.load(f)
        else:
            data = json.loads(sys.stdin.read())
    except FileNotFoundError:
        _die(f"Input file not found: {args.input_file}")
    except json.JSONDecodeError as exc:
        _die(f"Invalid JSON input: {exc}")

    question = data.get("question", "").strip()
    answer   = data.get("answer",   "").strip()
    contexts = data.get("contexts", [])

    if not question or not answer or not contexts:
        _die(
            "Input must contain: question (str), answer (str), contexts (non-empty list)",
            fix=(
                'echo \'{"question":"What is RAG?","answer":"RAG combines retrieval.","contexts":["RAG is..."]}\''
                " | python3 scripts/run_eval.py"
            ),
        )

    # 3. Setup LLM judge + embeddings
    llm        = _get_llm()
    embeddings = _get_embeddings()

    # 4. Run evaluation
    scores = run_eval(question, answer, contexts, args.metric, llm, embeddings)
    overall, verdict, flags = compute_verdict(scores)

    output: dict = {
        **scores,
        "overall_score": overall,
        "verdict": verdict,
        "flags": flags,
    }

    # 5. Faithfulness explain (--explain flag)
    if args.explain and "faithfulness" in scores:
        unsupported = explain_faithfulness(question, answer, contexts, llm)
        output["unsupported_claims"] = unsupported
        output["explain_note"] = (
            f"{len(unsupported)} claim(s) not supported by context "
            f"(faithfulness={scores.get('faithfulness')})"
            if unsupported
            else "All claims appear supported by context."
        )

    # 6. Persist result
    if not args.no_save:
        save_result({
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "input":  {"question": question, "answer": answer, "contexts": contexts},
            "output": output,
        })

    # 7. Print JSON to stdout
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
