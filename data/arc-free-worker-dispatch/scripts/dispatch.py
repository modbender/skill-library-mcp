#!/usr/bin/env python3
"""Free Worker Dispatch for OpenClaw agents.

Route tasks to free AI models via OpenRouter.
Save money by delegating grunt work to free models.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model routing table — optimized by task type
MODEL_MAP = {
    "research": "stepfun/step-3.5-flash:free",
    "content": "arcee-ai/trinity-large-preview:free",
    "code": "qwen/qwen3-coder:free",
    "analysis": "qwen/qwen3-next-80b-a3b-instruct:free",
    "general": "openrouter/free",
}

AVAILABLE_FREE_MODELS = [
    {"id": "stepfun/step-3.5-flash:free", "name": "Step 3.5 Flash", "ctx": 256000, "best_for": "Research, analysis, brainstorming"},
    {"id": "arcee-ai/trinity-large-preview:free", "name": "Arcee Trinity Large", "ctx": 131000, "best_for": "SEO copy, blog posts, marketing"},
    {"id": "qwen/qwen3-coder:free", "name": "Qwen3 Coder 480B", "ctx": 262000, "best_for": "Code generation, large context coding"},
    {"id": "qwen/qwen3-next-80b-a3b-instruct:free", "name": "Qwen3 Next 80B", "ctx": 262144, "best_for": "Complex analysis, reasoning, instructions"},
    {"id": "openai/gpt-oss-120b:free", "name": "GPT-OSS 120B", "ctx": 131072, "best_for": "General purpose, broad capability"},
    {"id": "nvidia/nemotron-3-nano-30b-a3b:free", "name": "Nemotron 3 Nano 30B", "ctx": 256000, "best_for": "Fast responses, large context"},
    {"id": "upstage/solar-pro-3:free", "name": "Solar Pro 3", "ctx": 128000, "best_for": "Multilingual, general tasks"},
    {"id": "openrouter/free", "name": "OpenRouter Auto (Free)", "ctx": 0, "best_for": "Auto-routes to best available free model"},
]


def call_openrouter(prompt, model, system_prompt=None, max_tokens=4096):
    """Call OpenRouter API with a prompt and model."""
    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not set. Set it in env or credentials.txt", file=sys.stderr)
        sys.exit(1)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }).encode("utf-8")

    req = urllib.request.Request(
        OPENROUTER_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://arcself.com",
            "X-Title": "Arc Self Worker Dispatch",
        },
    )

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - start
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            return {
                "content": content,
                "model": result.get("model", model),
                "tokens_in": usage.get("prompt_tokens", 0),
                "tokens_out": usage.get("completion_tokens", 0),
                "elapsed_seconds": round(elapsed, 2),
            }
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        print(f"ERROR: HTTP {e.code} from OpenRouter: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


ALLOWED_MODELS = {m["id"] for m in AVAILABLE_FREE_MODELS}


def _validate_model(model):
    """Ensure only free models are used — prevent paid model abuse."""
    if model not in ALLOWED_MODELS:
        print(f"ERROR: Model '{model}' is not in the allowed free models list.", file=sys.stderr)
        print(f"Allowed: {', '.join(sorted(ALLOWED_MODELS))}", file=sys.stderr)
        sys.exit(1)
    return model


def _validate_output_path(path):
    """Prevent arbitrary file write via --output path traversal."""
    real = os.path.realpath(path)
    home = os.path.expanduser("~")
    # Must be within home directory and not a dotfile/sensitive location
    if not real.startswith(os.path.realpath(home)):
        print(f"ERROR: Output path must be within home directory", file=sys.stderr)
        sys.exit(1)
    sensitive = ['.ssh', '.aws', '.env', '.bashrc', '.profile', '.gitconfig', 'credentials']
    for s in sensitive:
        if s in real:
            print(f"ERROR: Cannot write to sensitive path containing '{s}'", file=sys.stderr)
            sys.exit(1)
    return path


def cmd_task(args):
    model = args.model or MODEL_MAP.get(args.type or "general", "openrouter/free")
    _validate_model(model)
    result = call_openrouter(args.prompt, model, system_prompt=args.system)

    if args.json_output:
        output = json.dumps(result, indent=2)
    else:
        output = result["content"]

    if args.output:
        _validate_output_path(args.output)
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Output saved to {args.output}")
        print(f"Model: {result['model']} | Tokens: {result['tokens_in']}→{result['tokens_out']} | Time: {result['elapsed_seconds']}s")
    else:
        print(output)
        if not args.json_output:
            print(f"\n---\nModel: {result['model']} | Tokens: {result['tokens_in']}→{result['tokens_out']} | Time: {result['elapsed_seconds']}s", file=sys.stderr)


def cmd_models(args):
    print("Available Free Models:")
    for m in AVAILABLE_FREE_MODELS:
        print(f"  {m['id']}")
        print(f"    Name: {m['name']}")
        print(f"    Best for: {m['best_for']}")
        print()

    print("Task Type → Model Routing:")
    for task_type, model in MODEL_MAP.items():
        print(f"  --type {task_type} → {model}")


def cmd_status(args):
    model = args.model or "openrouter/free"
    print(f"Checking {model}...")
    try:
        result = call_openrouter("Say 'OK' and nothing else.", model, max_tokens=10)
        print(f"✅ {model} is UP")
        print(f"   Response: {result['content'][:50]}")
        print(f"   Latency: {result['elapsed_seconds']}s")
    except SystemExit:
        print(f"🚨 {model} is DOWN or erroring")


def cmd_batch(args):
    if not os.path.exists(args.file):
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    with open(args.file) as f:
        tasks = json.load(f)

    results = []
    for i, task in enumerate(tasks):
        prompt = task.get("prompt", "")
        task_type = task.get("type", "general")
        model = task.get("model") or MODEL_MAP.get(task_type, "openrouter/free")

        print(f"[{i+1}/{len(tasks)}] Dispatching to {model}...", file=sys.stderr)
        result = call_openrouter(prompt, model)
        result["task_index"] = i
        result["task_type"] = task_type
        results.append(result)
        print(f"  Done in {result['elapsed_seconds']}s ({result['tokens_out']} tokens)", file=sys.stderr)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Batch results saved to {args.output}")
    else:
        for r in results:
            print(f"\n=== Task {r['task_index'] + 1} ({r['task_type']}) ===")
            print(r["content"])
            print(f"--- Model: {r['model']} | Tokens: {r['tokens_in']}→{r['tokens_out']} ---")


def main():
    parser = argparse.ArgumentParser(description="Free Worker Dispatch for OpenClaw")
    sub = parser.add_subparsers(dest="command")

    p_task = sub.add_parser("task", help="Dispatch a task to a free model")
    p_task.add_argument("--prompt", required=True, help="The task prompt")
    p_task.add_argument("--model", help="Specific model to use (overrides --type)")
    p_task.add_argument("--type", choices=["research", "content", "code", "general"], default="general", help="Task type for auto model selection")
    p_task.add_argument("--system", help="Optional system prompt")
    p_task.add_argument("--output", help="Save output to file")
    p_task.add_argument("--json", dest="json_output", action="store_true", help="Output as JSON with metadata")

    sub.add_parser("models", help="List available free models")

    p_status = sub.add_parser("status", help="Check if a model is up")
    p_status.add_argument("--model", help="Model to check (default: openrouter/free)")

    p_batch = sub.add_parser("batch", help="Batch dispatch from a JSON file")
    p_batch.add_argument("--file", required=True, help="JSON file with tasks")
    p_batch.add_argument("--output", help="Save results to file")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "task": cmd_task,
        "models": cmd_models,
        "status": cmd_status,
        "batch": cmd_batch,
    }

    cmds[args.command](args)


if __name__ == "__main__":
    main()
