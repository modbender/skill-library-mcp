#!/usr/bin/env python3
"""
API_TKS — Multi-target API Token Speed Benchmark
Usage: python3 main.py run --label <target-label>
       python3 main.py --targets
"""

import argparse
import json
import os
import random
import sys
import time
import statistics
import requests
from dataclasses import dataclass

# Configuration
OPENCLAW_CFG = os.environ.get("OPENCLAW_CONFIG", os.path.expanduser("~/.openclaw/openclaw.json"))
VALID_FORMATS = {"anthropic-messages", "openai-completions", "openai-responses"}
DEFAULT_RUNS = 1
DEFAULT_MAX_TOKENS = 512
DEFAULT_TIMEOUT = 120
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 2

# Prompt bank - 12 unique prompts per category to prevent caching
PROMPT_BANK = {
    "short": [
        "Define what an API endpoint is in one sentence.",
        "Explain what JSON data format means briefly.",
        "What does HTTP GET request do?",
        "Describe what REST stands for.",
        "What is a web service?",
        "Explain what an API key is used for.",
        "What does authentication mean in APIs?",
        "Define what a request header is.",
        "What is a status code in HTTP?",
        "Explain what a query parameter does.",
        "What does POST method do in APIs?",
        "Define what a webhook is in simple terms.",
    ],
    "medium": [
        "Explain the difference between SQL and NoSQL databases, including when you would choose each one for a project.",
        "Describe how OAuth 2.0 authentication works, including the roles of client, server, and resource owner.",
        "What are the main principles of RESTful API design and why do they matter for maintainability?",
        "Explain the concept of database indexing and how it affects query performance in large applications.",
        "Describe the microservices architecture pattern and discuss its advantages and challenges compared to monoliths.",
        "What is the purpose of caching in distributed systems and what are common caching strategies?",
        "Explain how load balancing works and describe several algorithms used for distributing traffic.",
        "What are the key differences between synchronous and asynchronous communication patterns in APIs?",
        "Describe the CAP theorem and its implications for designing distributed data systems.",
        "What is rate limiting in APIs and what algorithms are commonly used to implement it?",
        "Explain how JWT tokens work for authentication and what security considerations exist.",
        "What are the main causes of API latency and how can they be diagnosed and reduced?",
    ],
    "long": [
        "You are a senior software architect. Design a complete e-commerce platform handling 10,000 orders per hour. Cover: database schema design, payment processing integration, inventory management, order fulfillment workflows, caching strategy for product catalogs, search functionality with Elasticsearch, and how you would handle flash sales with traffic spikes. Include technology choices with justifications and trade-offs.",
        "You are a DevOps engineer. Write a comprehensive guide to building a CI/CD pipeline for a containerized microservices application. Include: Docker image optimization strategies, Kubernetes deployment patterns, blue-green and canary releases, automated testing at each stage, secrets management, monitoring and alerting setup, and rollback procedures. Address both performance and security considerations.",
        "You are a data engineer. Design a real-time analytics pipeline that processes 1 million events per minute. Cover: event ingestion with Kafka, stream processing with Apache Flink or similar, data enrichment from multiple sources, time-windowed aggregations, building a dashboard-ready data warehouse, handling late-arriving data, and ensuring exactly-once processing semantics. Include cost optimization strategies.",
        "You are a security engineer. Create a comprehensive API security framework covering: authentication methods (OAuth, API keys, JWT), authorization patterns (RBAC, ABAC), input validation and sanitization, rate limiting strategies, encryption requirements, logging and audit trails, common vulnerability mitigation (SQL injection, XSS, CSRF), and security testing methodologies. Include code examples where relevant.",
        "You are a platform engineer. Design a multi-tenant SaaS platform that serves 500+ customers with isolated data and resources. Cover: database architecture for tenant isolation, container orchestration for tenant-specific workloads, billing and usage tracking, custom domain handling, SSO integration options, tenant onboarding automation, and how you would handle a tenant requesting dedicated infrastructure.",
        "You are a machine learning engineer. Design an ML ops pipeline for deploying and monitoring models in production. Cover: experiment tracking and model versioning, CI/CD for ML models, A/B testing frameworks, feature store architecture, model monitoring for drift detection, retraining triggers, inference optimization for low latency, and handling edge cases where models fail.",
        "You are a backend architect. Design a scalable chat application supporting 100,000 concurrent users. Cover: WebSocket handling and connection management, message persistence and delivery guarantees, presence detection, group messaging with read receipts, push notification integration, message search functionality, and how you would handle emoji and multimedia content.",
        "You are a systems architect. Create a disaster recovery plan for a mission-critical system with 99.99% uptime requirements. Cover: multi-region deployment strategies, data replication approaches, automatic failover mechanisms, backup and restore procedures, chaos engineering practices, RTO and RPO targets, and how you would test disaster recovery readiness without disrupting production.",
        "You are a performance engineer. Design a caching strategy for a high-traffic news website with 1 million daily visitors. Cover: CDN configuration, browser caching rules, application-level caching with Redis, cache invalidation strategies, handling personalized content, dealing with cache stampede scenarios, and measuring cache hit rates to optimize performance.",
        "You are an API designer. Create a comprehensive versioning strategy for a public API used by thousands of developers. Cover: URL versioning vs header versioning, deprecation timelines and communication, maintaining backward compatibility, handling breaking changes gracefully, documentation strategy, rate limit tiers, and how you would migrate major versions without disrupting existing integrations.",
        "You are a reliability engineer. Design a monitoring and observability stack for a distributed system with 50+ microservices. Cover: centralized logging with correlation IDs, metrics collection and aggregation, distributed tracing implementation, alerting configuration with SLO definitions, on-call rotation and incident response procedures, post-mortem analysis process, and how you would set up a dashboard for different stakeholder personas.",
        "You are a mobile backend engineer. Design an API that supports both a web and mobile application with 5 million users. Cover: stateless authentication with refresh tokens, push notification infrastructure, handling poor network connectivity, optimizing payloads for mobile bandwidth, implementing offline-first sync capabilities, API rate limiting by platform, and managing feature flags for gradual rollouts.",
    ],
}

# Token estimation: varies by model, 4 is a reasonable default for English
_CHARS_PER_TOKEN = 4
_TOKEN_ESTIMATION_NOTE = "Note: Token count estimated at 4 chars/token. Actual may vary by model."


@dataclass
class Target:
    label: str
    base_url: str
    api_key: str
    model: str
    api_format: str


def _resolve_api_key(api_key: str) -> str:
    if api_key.startswith("${") and api_key.endswith("}"):
        return os.environ.get(api_key[2:-1], "")
    return api_key


def load_targets():
    """Load all configured providers and models from openclaw.json."""
    if not os.path.exists(OPENCLAW_CFG):
        print(f"Error: OpenCLAW config not found at {OPENCLAW_CFG}")
        sys.exit(1)

    try:
        with open(OPENCLAW_CFG) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse openclaw.json: {e}")
        sys.exit(1)

    providers = config.get("models", {}).get("providers", {})
    if not providers:
        print("Error: No providers configured in openclaw.json")
        sys.exit(1)

    targets = []
    for provider_id, provider in providers.items():
        base_url = provider.get("baseUrl", "")
        api_key = _resolve_api_key(provider.get("apiKey", ""))
        api_format = provider.get("api", "openai-completions")

        if api_format not in VALID_FORMATS:
            continue
        if not base_url or not api_key:
            continue

        models = provider.get("models", [])
        if not models:
            targets.append(Target(provider_id, base_url, api_key, provider_id, api_format))
        else:
            for model in models:
                model_id = model.get("id", "")
                if not model_id:
                    continue
                model_api = model.get("api", api_format)
                if model_api not in VALID_FORMATS:
                    continue
                targets.append(Target(f"{provider_id}/{model_id}", base_url, api_key, model_id, model_api))

    if not targets:
        print("Error: No valid targets found in openclaw.json")
        sys.exit(1)

    return targets


def preflight_check(target: Target) -> tuple:
    """Send a minimal request and verify we get real content back."""
    TEST_PROMPT = "Reply with exactly the word: OK"
    try:
        if target.api_format == "anthropic-messages":
            return _preflight_anthropic(target, TEST_PROMPT)
        else:
            return _preflight_openai(target, TEST_PROMPT)
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {e}"
    except requests.exceptions.Timeout:
        return False, "Timed out after 20s"
    except Exception as e:
        return False, str(e)


def _preflight_anthropic(target: Target, prompt: str) -> tuple:
    headers = {"x-api-key": target.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    payload = {"model": target.model, "max_tokens": 256, "stream": False, "messages": [{"role": "user", "content": prompt}]}
    r = requests.post(f"{target.base_url}/v1/messages", headers=headers, json=payload, timeout=30)
    if r.status_code != 200:
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    data = r.json()
    blocks = data.get("content", [])
    text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    thinking = "".join(b.get("thinking", "") for b in blocks if b.get("type") == "thinking")
    if text.strip():
        return True, f"OK — got {len(text)} chars"
    if thinking.strip():
        return True, f"OK — thinking block received ({len(thinking)} chars)"
    return False, "Empty response body"


def _preflight_openai(target: Target, prompt: str) -> tuple:
    headers = {"Authorization": f"Bearer {target.api_key}", "content-type": "application/json"}
    payload = {"model": target.model, "max_tokens": 32, "stream": False, "messages": [{"role": "user", "content": prompt}]}
    r = requests.post(f"{target.base_url}/chat/completions", headers=headers, json=payload, timeout=20)
    if r.status_code != 200:
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    data = r.json()
    choices = data.get("choices", [])
    if not choices:
        return False, "No choices in response"
    content = choices[0].get("message", {}).get("content", "") or ""
    if not content.strip():
        return False, "Empty content in response"
    return True, f"OK — got {len(content)} chars"


def _is_retryable_error(e: Exception) -> bool:
    """Determine if an error is worth retrying."""
    # Check for HTTP status code in exception message
    msg = str(e)
    if msg.startswith("HTTP "):
        try:
            code = int(msg.split()[1])
            # Retry on rate limit (429) and server errors (5xx)
            return code == 429 or (500 <= code < 600)
        except (IndexError, ValueError):
            pass
    # Retry on timeouts and connection errors
    return isinstance(e, (requests.exceptions.Timeout, requests.exceptions.ConnectionError))


def call_target(target: Target, prompt: str, max_tokens: int, timeout: int = DEFAULT_TIMEOUT, verbose: bool = False) -> dict:
    """Call target API with retry logic."""
    last_error = None
    for attempt in range(1, DEFAULT_RETRY_ATTEMPTS + 1):
        try:
            if target.api_format == "anthropic-messages":
                return _call_anthropic(target, prompt, max_tokens, timeout)
            else:
                return _call_openai(target, prompt, max_tokens, timeout)
        except Exception as e:
            last_error = e
            if attempt < DEFAULT_RETRY_ATTEMPTS and _is_retryable_error(e):
                delay = DEFAULT_RETRY_DELAY * (2 ** (attempt - 1))  # exponential backoff
                if verbose:
                    print(f"    Retry {attempt}/{DEFAULT_RETRY_ATTEMPTS} after {delay}s: {e}")
                time.sleep(delay)
            elif not _is_retryable_error(e):
                # Don't retry non-retryable errors
                break
    raise last_error


def _call_anthropic(target: Target, prompt: str, max_tokens: int, timeout: int = DEFAULT_TIMEOUT) -> dict:
    headers = {"x-api-key": target.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    payload = {"model": target.model, "max_tokens": max_tokens, "stream": True, "messages": [{"role": "user", "content": prompt}]}

    t_start = time.perf_counter()
    t_first = None
    input_tokens = output_tokens = 0
    char_count = 0
    partial = False

    try:
        with requests.post(f"{target.base_url}/v1/messages", headers=headers, json=payload, stream=True, timeout=timeout) as resp:
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:400]}")

            for raw in resp.iter_lines():
                if not raw:
                    continue
                line = raw.decode() if isinstance(raw, bytes) else raw
                if not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if data_str in ("", "[DONE]"):
                    continue
                try:
                    ev = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                etype = ev.get("type", "")
                if etype == "content_block_delta":
                    delta = ev.get("delta", {})
                    text = delta.get("text", "")
                    thinking = delta.get("thinking", "")
                    if text:
                        char_count += len(text)
                        if t_first is None:
                            t_first = time.perf_counter()
                    if thinking:
                        char_count += len(thinking)
                        if t_first is None:
                            t_first = time.perf_counter()
                elif etype == "message_start":
                    input_tokens = ev.get("message", {}).get("usage", {}).get("input_tokens", 0)
                elif etype == "message_delta":
                    output_tokens = ev.get("usage", {}).get("output_tokens", output_tokens)

    except requests.exceptions.Timeout:
        partial = True

    if output_tokens == 0 and char_count > 0:
        output_tokens = max(1, char_count // _CHARS_PER_TOKEN)

    result = _build_result(t_start, t_first, input_tokens, output_tokens)
    if partial:
        result["partial"] = True
        result["note"] = "Timeout occurred - results may be incomplete"
    return result


def _call_openai(target: Target, prompt: str, max_tokens: int, timeout: int = DEFAULT_TIMEOUT) -> dict:
    headers = {"Authorization": f"Bearer {target.api_key}", "content-type": "application/json"}
    payload = {"model": target.model, "max_tokens": max_tokens, "stream": True, "messages": [{"role": "user", "content": prompt}]}

    t_start = time.perf_counter()
    t_first = None
    input_tokens = output_tokens = 0
    char_count = 0
    partial = False

    try:
        with requests.post(f"{target.base_url}/chat/completions", headers=headers, json=payload, stream=True, timeout=timeout) as resp:
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:400]}")

            for raw in resp.iter_lines():
                if not raw:
                    continue
                line = raw.decode() if isinstance(raw, bytes) else raw
                if not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if data_str in ("", "[DONE]"):
                    continue
                try:
                    ev = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                choices = ev.get("choices", [])
                if choices:
                    delta = choices[0].get("delta", {})
                    content = delta.get("content") or ""
                    if content:
                        char_count += len(content)
                        if t_first is None:
                            t_first = time.perf_counter()

                usage = ev.get("usage") or {}
                if usage:
                    input_tokens = usage.get("prompt_tokens", input_tokens)
                    output_tokens = usage.get("completion_tokens", output_tokens)

    except requests.exceptions.Timeout:
        partial = True

    if output_tokens == 0 and char_count > 0:
        output_tokens = max(1, char_count // _CHARS_PER_TOKEN)

    result = _build_result(t_start, t_first, input_tokens, output_tokens)
    if partial:
        result["partial"] = True
        result["note"] = "Timeout occurred - results may be incomplete"
    return result


def _build_result(t_start, t_first, input_tokens, output_tokens):
    total_s = time.perf_counter() - t_start
    ttft_s = (t_first - t_start) if t_first else None
    gen_s = (t_first - t_start) if t_first else total_s
    tps = output_tokens / gen_s if gen_s > 0 else 0
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "ttft_s": round(ttft_s, 4) if ttft_s is not None else None,
        "total_s": round(total_s, 4),
        "tps": round(tps, 2),
    }


def run_benchmark(target: Target, runs_per_prompt: int, max_tokens: int, timeout: int = DEFAULT_TIMEOUT,
                  verbose: bool = False, quiet: bool = False, categories: list = None,
                  custom_prompt: str = None) -> dict:
    """Run benchmark with optional category filter."""
    if categories is None:
        categories = list(PROMPT_BANK.keys())

    raw = {}

    # Handle custom prompt mode
    if custom_prompt:
        raw["custom"] = []
        for run in range(1, runs_per_prompt + 1):
            try:
                result = call_target(target, custom_prompt, max_tokens, timeout, verbose)
                raw["custom"].append({"run": run, "status": "ok", **result})
                if verbose:
                    status_note = " (partial)" if result.get("partial") else ""
                    print(f"  Custom run {run}: {result['output_tokens']} tok, {result['tps']:.1f} tok/s{status_note}")
                elif not quiet:
                    pct = (run / runs_per_prompt) * 100
                    print(f"\r  Progress: {run}/{runs_per_prompt} ({pct:.0f}%)", end="", flush=True, file=sys.stderr)
            except Exception as e:
                raw["custom"].append({"run": run, "status": "error", "error": str(e)})
                if verbose:
                    print(f"  Custom run {run}: ERROR - {e}")
        if not quiet:
            print()
        return raw

    total_ops = len(categories) * runs_per_prompt
    op_count = 0

    for key in categories:
        if key not in PROMPT_BANK:
            continue
        raw[key] = []
        label = key.capitalize()
        # Shuffle prompts to ensure uniqueness across runs
        prompts = random.sample(PROMPT_BANK[key], k=len(PROMPT_BANK[key]))
        for run_idx, run in enumerate(range(1, runs_per_prompt + 1)):
            op_count += 1
            prompt = prompts[run_idx % len(prompts)]  # Cycle if runs > bank size
            try:
                result = call_target(target, prompt, max_tokens, timeout, verbose)
                raw[key].append({"run": run, "status": "ok", **result})
                if verbose:
                    status_note = " (partial)" if result.get("partial") else ""
                    print(f"  {label} run {run}: {result['output_tokens']} tok, {result['tps']:.1f} tok/s{status_note}")
                elif not quiet:
                    # Progress indicator
                    pct = (op_count / total_ops) * 100
                    print(f"\r  Progress: {op_count}/{total_ops} ({pct:.0f}%)", end="", flush=True, file=sys.stderr)
            except Exception as e:
                raw[key].append({"run": run, "status": "error", "error": str(e)})
                if verbose:
                    print(f"  {label} run {run}: ERROR - {e}")

    if not quiet:
        print()  # newline after progress
    return raw


def action_check(label: str | None = None, check_all: bool = False, table_output: bool = False, quiet: bool = False):
    """Run preflight check on one or all targets."""
    targets = load_targets()

    # Determine which targets to check
    targets_to_check = []
    if check_all:
        targets_to_check = targets
    elif label:
        for t in targets:
            if t.label == label:
                targets_to_check = [t]
                break
        if not targets_to_check:
            print(json.dumps({"ok": False, "error": f"Target '{label}' not found", "available": [t.label for t in targets]}))
            sys.exit(1)
    elif len(targets) == 1:
        targets_to_check = [targets[0]]
    else:
        print(json.dumps({"ok": False, "error": "Specify target with --label or use --all", "available": [t.label for t in targets]}))
        sys.exit(1)

    results = []
    for target in targets_to_check:
        ok, msg = preflight_check(target)
        results.append({
            "target": target.label,
            "model": target.model,
            "api_format": target.api_format,
            "ok": ok,
            "message": msg if ok else None,
            "error": msg if not ok else None,
        })

    if table_output:
        # Human-readable output
        if not quiet:
            print(f"\n{'Target':<45} {'Model':<30} {'Status':<8} {'Error':<30}")
            print("-" * 115)
        for r in results:
            status = "OK" if r["ok"] else "FAIL"
            error = r.get("error", "")[:30] if not r["ok"] else ""
            if not quiet:
                print(f"{r['target']:<45} {r['model']:<30} {status:<8} {error:<30}")
        if not quiet:
            print()
            failed = sum(1 for r in results if not r["ok"])
            if failed:
                print(f"Failed: {failed}/{len(results)}")
    else:
        # JSON output - consistent format
        output = {
            "ok": all(r["ok"] for r in results),
            "results": results
        }
        print(json.dumps(output, indent=2))


def action_run(label: str | None = None, runs: int = DEFAULT_RUNS, run_all: bool = False,
               table_output: bool = False, quiet: bool = False, timeout: int = DEFAULT_TIMEOUT,
               categories: list = None, max_tokens: int = DEFAULT_MAX_TOKENS, dry_run: bool = False,
               custom_prompt: str = None):
    targets = load_targets()

    # Determine which targets to run
    targets_to_run = []
    if run_all:
        targets_to_run = targets
    elif label:
        for t in targets:
            if t.label == label:
                targets_to_run = [t]
                break
        if not targets_to_run:
            print(f"Error: Target '{label}' not found.")
            available = ", ".join(t.label for t in targets)
            print(f"Available targets: {available}")
            sys.exit(1)
    elif len(targets) == 1:
        targets_to_run = [targets[0]]
    else:
        print("Available targets:")
        for i, t in enumerate(targets, 1):
            print(f"  {i}. {t.label}")
        print("\nUse --label to specify a target or --all to run all")
        sys.exit(1)

    all_results = []

    for target in targets_to_run:
        if len(targets_to_run) > 1 and not quiet:
            print(f"\n=== {target.label} ===")

        if not quiet:
            print(f"Target: {target.label}")
            print(f"Model: {target.model}")
            print(f"Runs: {runs}")
            if categories:
                print(f"Categories: {', '.join(categories)}")
            print()

        # Pre-flight
        if not quiet:
            print("Pre-flight check...", end=" ", flush=True)
        ok, msg = preflight_check(target)
        if ok:
            if not quiet:
                print(f"OK")
        else:
            if not quiet:
                print(f"FAILED: {msg}")
            if not table_output:
                all_results.append({
                    "target": target.label,
                    "model": target.model,
                    "api_format": target.api_format,
                    "ok": False,
                    "error": msg,
                })
                continue
            else:
                sys.exit(1)

        # Dry-run mode - just verify config
        if dry_run:
            if not quiet:
                print(f"Dry-run: configuration verified for {target.label}")
            all_results.append({
                "target": target.label,
                "model": target.model,
                "api_format": target.api_format,
                "ok": True,
                "dry_run": True,
            })
            continue

        # Run benchmark
        if not quiet:
            print("\nRunning benchmark...")

        raw = run_benchmark(target, runs, max_tokens, timeout=timeout,
                           verbose=table_output, quiet=quiet, categories=categories,
                           custom_prompt=custom_prompt)

        # Process results
        summary_rows = []
        has_partial = False
        for key, runs_data in raw.items():
            label_name = key.capitalize()
            valid = [r for r in runs_data if r.get("status") == "ok"]

            if valid:
                avg_tps = statistics.mean(r["tps"] for r in valid)
                avg_ttft = statistics.mean(r["ttft_s"] for r in valid if r.get("ttft_s") is not None) if any(r.get("ttft_s") for r in valid) else None
                avg_out = statistics.mean(r["output_tokens"] for r in valid)

                row = {
                    "prompt": label_name,
                    "avg_tps": round(avg_tps, 2),
                    "avg_ttft": round(avg_ttft, 3) if avg_ttft else None,
                    "avg_output_tokens": round(avg_out, 1),
                }

                # Check for partial results
                if any(r.get("partial") for r in valid):
                    row["partial"] = True
                    has_partial = True

                summary_rows.append(row)

        overall_tps = statistics.mean(r["avg_tps"] for r in summary_rows) if summary_rows else 0

        if not table_output:
            # JSON output
            result = {
                "target": target.label,
                "model": target.model,
                "api_format": target.api_format,
                "runs": runs,
                "summary": summary_rows,
                "overall_avg_tps": round(overall_tps, 2),
                "token_estimation": _TOKEN_ESTIMATION_NOTE,
            }
            if has_partial:
                result["warning"] = "Some runs timed out - results may be incomplete"
            all_results.append(result)
        elif not quiet:
            # Human output
            print("\n=== Results ===")
            print(f"{'Prompt':<10} {'Tok/s':>8} {'TTFT':>10} {'Avg Out':>10}")
            print("-" * 40)
            for r in summary_rows:
                ttft = f"{r['avg_ttft']:.2f}s" if r['avg_ttft'] else "n/a"
                partial = " *" if r.get("partial") else ""
                print(f"{r['prompt']:<10} {r['avg_tps']:>8.1f} {ttft:>10} {r['avg_output_tokens']:>10.0f}{partial}")
            print("-" * 40)
            print(f"{'Overall':<10} {overall_tps:>8.1f}")
            if has_partial:
                print("* partial (timeout)")
            print()

    # Output final results
    if not table_output:
        if len(all_results) == 1:
            print(json.dumps(all_results[0], indent=2))
        else:
            print(json.dumps(all_results, indent=2))


def main():
    parser = argparse.ArgumentParser(description="API Token Speed Benchmark")
    parser.add_argument("command", nargs="?", default=None, choices=["run", "check", "help"])
    parser.add_argument("-l", "--label", type=str, help="Target label to benchmark")
    parser.add_argument("-t", "--targets", action="store_true", help="List all available targets")
    parser.add_argument("-a", "--all", action="store_true", help="Run on all targets")
    parser.add_argument("-r", "--repeat", type=int, default=DEFAULT_RUNS, help="Number of runs per prompt level")
    parser.add_argument("--table", action="store_true", help="Output as formatted table (default: JSON)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode - suppress progress output")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("-c", "--category", type=str, action="append", dest="categories",
                       help="Prompt category to run (can be repeated: -c short -c medium). Options: short, medium, long. Default: all")
    parser.add_argument("-m", "--max-tokens", type=int, default=DEFAULT_MAX_TOKENS,
                       help=f"Maximum tokens to generate (default: {DEFAULT_MAX_TOKENS})")
    parser.add_argument("-v", "--version", action="store_true", help="Show version and exit")
    parser.add_argument("--dry-run", action="store_true", help="Verify configuration without making API calls")
    parser.add_argument("-p", "--prompt", type=str,
                       help="Custom prompt to use instead of built-in prompts")

    args = parser.parse_args()

    # Validate numeric arguments
    if args.repeat is not None and args.repeat < 1:
        print("Error: --repeat must be at least 1")
        sys.exit(1)
    if args.timeout is not None and args.timeout < 1:
        print("Error: --timeout must be at least 1")
        sys.exit(1)
    if args.max_tokens is not None and args.max_tokens < 1:
        print("Error: --max-tokens must be at least 1")
        sys.exit(1)

    if args.targets:
        for t in load_targets():
            print(t.label)
        return

    if args.version:
        print("api-benchmark v1.0.2")
        return

    if args.command == "run":
        action_run(args.label, runs=args.repeat, run_all=args.all, table_output=args.table,
                   quiet=args.quiet, timeout=args.timeout, categories=args.categories,
                   max_tokens=args.max_tokens, dry_run=args.dry_run, custom_prompt=args.prompt)
    elif args.command == "check":
        action_check(args.label, check_all=args.all, table_output=args.table, quiet=args.quiet)
    elif args.command == "help":
        print("Usage:")
        print("  python3 main.py check --label <target>")
        print("  python3 main.py check --all")
        print("  python3 main.py run --label <target>")
        print("  python3 main.py run --all")
        print("  python3 main.py --targets")
        print()
        print("Options:")
        print("  -r, --repeat N      Number of runs per prompt level (default: 1)")
        print("  -c, --category     Run specific prompt category (short/medium/long)")
        print("  -q, --quiet        Quiet mode - suppress progress output")
        print("  --timeout N        Request timeout in seconds (default: 120)")
        print("  --table            Output as formatted table")
    else:
        print("Usage: python3 main.py run --label <target>")
        print("       python3 main.py check --label <target>")
        print("       python3 main.py --targets")
        print()
        print("Options:")
        print("  -r, --repeat N      Number of runs per prompt level")
        print("  -c, --category     Run specific prompt category")
        print("  -q, --quiet        Quiet mode")
        print("  --timeout N        Request timeout in seconds")
        print("  --table            Output as formatted table")
        sys.exit(1)


if __name__ == "__main__":
    main()
