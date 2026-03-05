#!/usr/bin/env python3
"""Model Council — Multi-model consensus system via OpenRouter."""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_MODELS = [
    "anthropic/claude-sonnet-4",
    "openai/gpt-4o",
    "google/gemini-2.0-flash-001",
]
DEFAULT_JUDGE = "anthropic/claude-opus-4-6"


def get_api_key():
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("ERROR: OPENROUTER_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    return key


def call_model(api_key, model, prompt, max_tokens=1024, timeout=60):
    """Call a single model via OpenRouter. Returns dict with response, cost, timing."""
    start = time.time()
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }).encode()

    req = Request(
        OPENROUTER_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agxntsix.ai",
            "X-Title": "Model Council",
        },
    )

    try:
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {
            "model": model,
            "response": None,
            "error": f"HTTP {e.code}: {body[:200]}",
            "cost": 0,
            "duration": time.time() - start,
        }
    except (URLError, TimeoutError) as e:
        return {
            "model": model,
            "response": None,
            "error": str(e),
            "cost": 0,
            "duration": time.time() - start,
        }

    content = ""
    if data.get("choices"):
        content = data["choices"][0].get("message", {}).get("content", "")

    usage = data.get("usage", {})
    # OpenRouter returns cost in the response headers or usage
    # Estimate from token counts and known pricing
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_cost = data.get("usage", {}).get("cost", 0)
    # If cost not in response, try to get from generation stats
    if not total_cost and "id" in data:
        try:
            gen_req = Request(
                f"https://openrouter.ai/api/v1/generation?id={data['id']}",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            with urlopen(gen_req, timeout=10) as gen_resp:
                gen_data = json.loads(gen_resp.read().decode())
                total_cost = gen_data.get("data", {}).get("total_cost", 0)
        except Exception:
            total_cost = 0

    return {
        "model": model,
        "response": content,
        "error": None,
        "cost": total_cost or 0,
        "duration": time.time() - start,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


def judge_responses(api_key, judge_model, question, responses, max_tokens=2048, timeout=90):
    """Have the judge model evaluate all council responses."""
    resp_text = ""
    for i, r in enumerate(responses, 1):
        if r["error"]:
            resp_text += f"\n--- Response {i} ({r['model']}) ---\n[ERROR: {r['error']}]\n"
        else:
            resp_text += f"\n--- Response {i} ({r['model']}) ---\n{r['response']}\n"

    judge_prompt = f"""You are an expert judge evaluating multiple AI model responses to a question.

QUESTION:
{question}

RESPONSES:
{resp_text}

Evaluate each response for accuracy, completeness, clarity, and usefulness.

Provide your verdict in this EXACT format:

WINNER: [model name that gave the best response]
REASONING: [2-3 sentences explaining why this response won]
SYNTHESIZED ANSWER: [Your synthesized best answer combining the strongest elements from all responses. Be thorough.]"""

    result = call_model(api_key, judge_model, judge_prompt, max_tokens, timeout)
    return result


def parse_judge_verdict(text):
    """Parse the judge's structured response."""
    verdict = {"winner": "", "reasoning": "", "synthesized": ""}
    if not text:
        return verdict

    lines = text.split("\n")
    current = None
    for line in lines:
        upper = line.strip().upper()
        if upper.startswith("WINNER:"):
            verdict["winner"] = line.split(":", 1)[1].strip()
            current = "winner"
        elif upper.startswith("REASONING:"):
            verdict["reasoning"] = line.split(":", 1)[1].strip()
            current = "reasoning"
        elif upper.startswith("SYNTHESIZED ANSWER:"):
            verdict["synthesized"] = line.split(":", 1)[1].strip()
            current = "synthesized"
        elif current == "reasoning" and line.strip():
            verdict["reasoning"] += " " + line.strip()
        elif current == "synthesized" and line.strip():
            verdict["synthesized"] += "\n" + line.strip()

    return verdict


def print_human(question, responses, judge_result, verdict):
    """Print human-readable output."""
    print("\n" + "═" * 50)
    print("  MODEL COUNCIL RESULTS")
    print("═" * 50)
    print(f"\nQuestion: {question}\n")
    print("── Council Member Responses ──\n")

    for r in responses:
        cost_str = f"${r['cost']:.4f}" if r['cost'] else "N/A"
        dur_str = f"{r['duration']:.1f}s"
        print(f"🤖 {r['model']} ({cost_str}, {dur_str})")
        if r["error"]:
            print(f"   ❌ Error: {r['error']}")
        else:
            # Truncate for display
            text = r["response"] or ""
            if len(text) > 500:
                text = text[:500] + "..."
            for line in text.split("\n"):
                print(f"   {line}")
        print()

    judge_cost = f"${judge_result['cost']:.4f}" if judge_result['cost'] else "N/A"
    print(f"── Judge Verdict ({judge_result['model']}, {judge_cost}) ──\n")

    if verdict["winner"]:
        print(f"🏆 Winner: {verdict['winner']}")
    if verdict["reasoning"]:
        print(f"💭 Reasoning: {verdict['reasoning']}")
    if verdict["synthesized"]:
        print(f"\n📝 Synthesized Answer:\n{verdict['synthesized']}")

    total_cost = sum(r["cost"] for r in responses) + (judge_result["cost"] or 0)
    print(f"\n💰 Total Cost: ${total_cost:.4f}")
    print("═" * 50)


def main():
    parser = argparse.ArgumentParser(description="Model Council — Multi-model consensus")
    parser.add_argument("question", help="Question to ask the council")
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS),
                        help="Comma-separated list of models")
    parser.add_argument("--judge", default=DEFAULT_JUDGE, help="Judge model")
    parser.add_argument("--max-tokens", type=int, default=1024, help="Max tokens per response")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per model (seconds)")
    parser.add_argument("--json", action="store_true", dest="json_output", help="JSON output")
    args = parser.parse_args()

    api_key = get_api_key()
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    if not args.json_output:
        print(f"🏛️  Convening council with {len(models)} models...")
        for m in models:
            print(f"   • {m}")
        print(f"   Judge: {args.judge}\n")

    # Query all models in parallel
    responses = []
    with ThreadPoolExecutor(max_workers=len(models)) as executor:
        futures = {
            executor.submit(call_model, api_key, m, args.question, args.max_tokens, args.timeout): m
            for m in models
        }
        for future in as_completed(futures):
            result = future.result()
            responses.append(result)
            if not args.json_output:
                status = "✓" if not result["error"] else f"✗ {result['error'][:50]}"
                print(f"   [{status}] {result['model']} ({result['duration']:.1f}s)")

    # Sort by original model order
    model_order = {m: i for i, m in enumerate(models)}
    responses.sort(key=lambda r: model_order.get(r["model"], 99))

    # Filter successful responses for judging
    valid = [r for r in responses if not r["error"]]
    if not valid:
        print("ERROR: All models failed. No consensus possible.", file=sys.stderr)
        sys.exit(1)

    if not args.json_output:
        print("\n⚖️  Judge evaluating responses...")

    judge_result = judge_responses(api_key, args.judge, args.question, responses,
                                   args.max_tokens * 2, args.timeout + 30)

    if judge_result["error"]:
        print(f"ERROR: Judge failed: {judge_result['error']}", file=sys.stderr)
        sys.exit(1)

    verdict = parse_judge_verdict(judge_result["response"])

    if args.json_output:
        output = {
            "question": args.question,
            "models": models,
            "judge": args.judge,
            "responses": [
                {
                    "model": r["model"],
                    "response": r["response"],
                    "error": r["error"],
                    "cost": r["cost"],
                    "duration": r["duration"],
                    "prompt_tokens": r.get("prompt_tokens", 0),
                    "completion_tokens": r.get("completion_tokens", 0),
                }
                for r in responses
            ],
            "verdict": verdict,
            "judge_cost": judge_result["cost"],
            "total_cost": sum(r["cost"] for r in responses) + (judge_result["cost"] or 0),
        }
        print(json.dumps(output, indent=2))
    else:
        print_human(args.question, responses, judge_result, verdict)


if __name__ == "__main__":
    main()
