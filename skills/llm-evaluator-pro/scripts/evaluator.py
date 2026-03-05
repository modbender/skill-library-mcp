#!/usr/bin/env python3
"""
AgxntSix Evaluator — LLM-as-a-Judge via Langfuse.

Uses GPT-5-nano via OpenRouter as a cheap, fast judge to evaluate traces.
Scores are saved directly to Langfuse for dashboard visibility.

Usage:
  evaluator.py test                              # Run a quick test
  evaluator.py score <trace_id>                  # Score a specific trace
  evaluator.py backfill [--limit 10]             # Score recent unscored traces
  evaluator.py experiment [--name "run name"]    # Run experiment on dataset
"""
import argparse
import json
import os
import sys
import time
import requests
from datetime import datetime

# Langfuse config
os.environ.setdefault("LANGFUSE_SECRET_KEY", "sk-lf-115cb6b4-7153-4fe6-9255-bf28f8b115de")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "pk-lf-8a9322b9-5eb1-4e8b-815e-b3428dc69bc4")
os.environ.setdefault("LANGFUSE_HOST", "http://langfuse-web:3000")

LF_AUTH = ("pk-lf-8a9322b9-5eb1-4e8b-815e-b3428dc69bc4", "sk-lf-115cb6b4-7153-4fe6-9255-bf28f8b115de")
LF_API = "http://langfuse-web:3000/api/public"

from openai import OpenAI

# OpenRouter key
OR_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OR_KEY:
    try:
        with open(os.path.expanduser("~/.openclaw/workspace/.env")) as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    OR_KEY = line.strip().split("=", 1)[1]
    except:
        pass

JUDGE_MODEL = "openai/gpt-5-nano"


def get_judge():
    return OpenAI(api_key=OR_KEY, base_url="https://openrouter.ai/api/v1")


def llm_judge(prompt: str) -> dict:
    """Call the judge LLM and parse score + reasoning."""
    judge = get_judge()
    resp = judge.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    text = resp.choices[0].message.content.strip()
    try:
        result = json.loads(text)
        return {"score": float(result.get("score", 0.5)), "reasoning": result.get("reasoning", text)}
    except:
        import re
        match = re.search(r'(\d+\.?\d*)\s*/\s*(\d+)', text)
        if match:
            return {"score": float(match.group(1)) / float(match.group(2)), "reasoning": text}
        return {"score": 0.5, "reasoning": text}


def save_score(trace_id: str, name: str, value: float, comment: str = ""):
    """Save a score to Langfuse via API."""
    requests.post(
        f"{LF_API}/scores",
        auth=LF_AUTH,
        json={"traceId": trace_id, "name": name, "value": value, "comment": comment},
    )


# === EVALUATORS ===

def eval_relevance(input_text: str, output_text: str) -> dict:
    return llm_judge(
        f'Rate the relevance of this AI response to the query (0.0-1.0). '
        f'Respond JSON only: {{"score": <float>, "reasoning": "<brief>"}}\n\n'
        f'Query: {input_text}\nResponse: {output_text}'
    )

def eval_accuracy(input_text: str, output_text: str, expected: str = "") -> dict:
    ctx = f"\nExpected: {expected}" if expected else ""
    return llm_judge(
        f'Rate the factual accuracy of this response (0.0-1.0).{ctx} '
        f'Respond JSON only: {{"score": <float>, "reasoning": "<brief>"}}\n\n'
        f'Query: {input_text}\nResponse: {output_text}'
    )

def eval_hallucination(input_text: str, output_text: str) -> dict:
    return llm_judge(
        f'Rate whether this response is free of hallucinations (0.0=severe hallucinations, 1.0=fully grounded). '
        f'Respond JSON only: {{"score": <float>, "reasoning": "<brief>"}}\n\n'
        f'Query: {input_text}\nResponse: {output_text}'
    )

def eval_helpfulness(input_text: str, output_text: str) -> dict:
    return llm_judge(
        f'Rate how helpful this response is to the user (0.0=not helpful, 1.0=extremely helpful). '
        f'Respond JSON only: {{"score": <float>, "reasoning": "<brief>"}}\n\n'
        f'Query: {input_text}\nResponse: {output_text}'
    )

EVALUATORS = {
    "relevance": eval_relevance,
    "accuracy": eval_accuracy,
    "hallucination": eval_hallucination,
    "helpfulness": eval_helpfulness,
}


# === COMMANDS ===

def cmd_test(args):
    """Quick test of the judge pipeline."""
    from langfuse import get_client
    lf = get_client()
    
    test_cases = [
        {"input": "What is the capital of France?", "output": "The capital of France is Paris.", "expected": "Paris"},
        {"input": "What is 2+2?", "output": "2+2 equals 4.", "expected": "4"},
        {"input": "Tell me about quantum computing", "output": "Quantum computing uses qubits that can exist in superposition, enabling parallel computation. It's useful for optimization and cryptography.", "expected": ""},
    ]
    
    print(f"Running LLM-as-a-Judge on {len(test_cases)} test cases...\n")
    
    for i, tc in enumerate(test_cases):
        # Create a trace for this test
        with lf.start_as_current_observation(
            as_type="span",
            name=f"judge-test-{i+1}",
            input=tc["input"],
        ) as span:
            span.update(output=tc["output"])
        
        lf.flush()
        time.sleep(0.5)
        
        # Get trace ID from recent traces
        resp = requests.get(f"{LF_API}/traces", params={"limit": 1, "orderBy": "timestamp.desc"}, auth=LF_AUTH)
        traces = resp.json().get("data", [])
        if not traces:
            print(f"  ❌ Could not find trace for test {i+1}")
            continue
        
        trace_id = traces[0]["id"]
        print(f"Test {i+1}: {tc['input'][:50]}")
        
        # Run all evaluators
        for name, evaluator in EVALUATORS.items():
            if name == "accuracy":
                result = evaluator(tc["input"], tc["output"], tc.get("expected", ""))
            else:
                result = evaluator(tc["input"], tc["output"])
            
            save_score(trace_id, name, result["score"], result["reasoning"])
            print(f"  {name}: {result['score']:.2f} — {result['reasoning'][:80]}")
        
        print()
    
    print("✅ All test scores saved to Langfuse")


def cmd_score(args):
    """Score a specific trace."""
    resp = requests.get(f"{LF_API}/traces/{args.trace_id}", auth=LF_AUTH)
    if resp.status_code != 200:
        print(f"❌ Trace not found: {args.trace_id}")
        return
    
    trace = resp.json()
    input_text = str(trace.get("input", ""))
    output_text = str(trace.get("output", ""))
    
    if not input_text or not output_text:
        print("⚠️ Trace has no input/output to evaluate")
        return
    
    print(f"Scoring trace: {args.trace_id}")
    print(f"  Input: {input_text[:100]}...")
    print(f"  Output: {output_text[:100]}...")
    
    evals = EVALUATORS if args.evaluators == "all" else {args.evaluators: EVALUATORS[args.evaluators]}
    
    for name, evaluator in evals.items():
        result = evaluator(input_text, output_text)
        save_score(args.trace_id, name, result["score"], result["reasoning"])
        print(f"  {name}: {result['score']:.2f} — {result['reasoning'][:80]}")
    
    print("✅ Scores saved")


def cmd_backfill(args):
    """Score recent unscored traces."""
    resp = requests.get(f"{LF_API}/traces", params={"limit": args.limit, "orderBy": "timestamp.desc"}, auth=LF_AUTH)
    traces = resp.json().get("data", [])
    
    scored = 0
    for trace in traces:
        input_text = str(trace.get("input", ""))
        output_text = str(trace.get("output", ""))
        
        if not input_text or not output_text or len(output_text) < 10:
            continue
        
        # Check if already scored
        score_resp = requests.get(f"{LF_API}/scores", params={"traceId": trace["id"], "limit": 1}, auth=LF_AUTH)
        if score_resp.json().get("data", []):
            continue
        
        print(f"Scoring: {trace.get('name', 'unnamed')} ({trace['id'][:12]}...)")
        
        for name in ["relevance", "accuracy"]:
            result = EVALUATORS[name](input_text, output_text)
            save_score(trace["id"], name, result["score"], result["reasoning"])
            print(f"  {name}: {result['score']:.2f}")
        
        scored += 1
    
    print(f"\n✅ Scored {scored} traces")


def cmd_experiment(args):
    """Run experiment using Langfuse datasets."""
    from langfuse import get_client, Evaluation
    lf = get_client()
    
    dataset_name = args.dataset or "search-quality"
    
    try:
        dataset = lf.get_dataset(dataset_name)
    except:
        print(f"❌ Dataset '{dataset_name}' not found")
        return
    
    def task(*, item, **kwargs):
        judge = get_judge()
        resp = judge.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[{"role": "user", "content": str(item.input)}],
            temperature=0,
        )
        return resp.choices[0].message.content
    
    def simple_accuracy(*, input, output, expected_output=None, **kwargs):
        if expected_output and str(expected_output).lower() in str(output).lower():
            return Evaluation(name="accuracy", value=1.0, comment="Expected output found in response")
        return Evaluation(name="accuracy", value=0.0, comment="Expected output not found")
    
    run_name = args.name or f"Experiment {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    print(f"Running experiment '{run_name}' on dataset '{dataset_name}'...")
    result = lf.run_experiment(
        name=run_name,
        dataset=dataset,
        task=task,
        evaluators=[simple_accuracy],
    )
    print(result.format())
    lf.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgxntSix Evaluator (LLM-as-a-Judge)")
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("test", help="Run test evaluation")
    
    p = sub.add_parser("score", help="Score a specific trace")
    p.add_argument("trace_id")
    p.add_argument("--evaluators", default="all", choices=["all", "relevance", "accuracy", "hallucination", "helpfulness"])
    
    p = sub.add_parser("backfill", help="Score recent unscored traces")
    p.add_argument("--limit", type=int, default=10)
    
    p = sub.add_parser("experiment", help="Run experiment on dataset")
    p.add_argument("--dataset", default="search-quality")
    p.add_argument("--name", help="Experiment run name")
    
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
    else:
        globals()[f"cmd_{args.cmd}"](args)
