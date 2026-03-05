#!/usr/bin/env python3
"""Run a prompt against free OpenRouter models with scoring and fallback."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

OPENROUTER_BASE = "https://openrouter.ai/api/v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find a free OpenRouter model and get a response"
    )
    parser.add_argument("--prompt", required=True, help="User prompt text")
    parser.add_argument("--system", default="", help="Optional system instruction")
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=8,
        help="Number of top free models to try",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Sampling temperature",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug information to stderr",
    )
    return parser.parse_args()


def as_decimal(value: Any) -> Optional[Decimal]:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def is_free_model(model: Dict[str, Any]) -> bool:
    pricing = model.get("pricing") or {}
    prompt = as_decimal(pricing.get("prompt"))
    completion = as_decimal(pricing.get("completion"))
    if prompt is None or completion is None:
        return False
    return prompt == Decimal("0") and completion == Decimal("0")


def get_context_score(context_length: Any) -> int:
    try:
        context = int(context_length or 0)
    except (TypeError, ValueError):
        context = 0

    score = 0
    if context > 100_000:
        score += 5
    if context > 50_000:
        score += 3
    if context > 10_000:
        score += 1
    return score


def score_model(model: Dict[str, Any]) -> int:
    params = model.get("supported_parameters") or []
    if not isinstance(params, list):
        params = []

    score = 0
    score += len(params)

    advanced_weights = {
        "structured_outputs": 10,
        "reasoning": 8,
        "response_format": 6,
        "seed": 4,
        "logprobs": 3,
    }
    standard_weights = {
        "temperature": 2,
        "max_tokens": 2,
        "top_p": 2,
        "frequency_penalty": 1,
        "presence_penalty": 1,
    }

    for key, value in advanced_weights.items():
        if key in params:
            score += value

    for key, value in standard_weights.items():
        if key in params:
            score += value

    score += get_context_score(model.get("context_length"))

    model_id = str(model.get("id") or "")
    if ":free" in model_id:
        score += 2

    return score


def openrouter_get(api_key: str, path: str) -> Dict[str, Any]:
    req = urllib.request.Request(
        f"{OPENROUTER_BASE}{path}",
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def openrouter_chat(
    api_key: str,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float,
) -> Dict[str, Any]:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    req = urllib.request.Request(
        f"{OPENROUTER_BASE}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_text(chat_response: Dict[str, Any]) -> str:
    choices = chat_response.get("choices") or []
    if not choices:
        raise RuntimeError("No choices returned by model")

    message = choices[0].get("message") or {}
    content = message.get("content")

    if isinstance(content, str):
        text = content.strip()
        if not text:
            raise RuntimeError("Model returned empty content")
        return text

    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = str(item.get("text") or "").strip()
                if text:
                    parts.append(text)
        joined = "\n".join(parts).strip()
        if joined:
            return joined

    raise RuntimeError("Unsupported response content format")


def ranked_free_models(api_key: str) -> List[Dict[str, Any]]:
    models_payload = openrouter_get(api_key, "/models")
    data = models_payload.get("data") or []
    if not isinstance(data, list):
        return []

    free_models = [m for m in data if isinstance(m, dict) and is_free_model(m)]

    scored = []
    for model in free_models:
        scored.append({"id": model.get("id"), "score": score_model(model), "raw": model})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def debug(msg: str, enabled: bool) -> None:
    if enabled:
        print(msg, file=sys.stderr)


def main() -> int:
    args = parse_args()

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("OPENROUTER_API_KEY is not set", file=sys.stderr)
        return 2

    messages: List[Dict[str, str]] = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": args.prompt})

    try:
        ranked = ranked_free_models(api_key)
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace") if hasattr(err, "read") else ""
        print(f"Failed to fetch models: HTTP {err.code} {detail}".strip(), file=sys.stderr)
        return 1
    except urllib.error.URLError as err:
        print(f"Failed to fetch models: {err}", file=sys.stderr)
        return 1

    if not ranked:
        print("No free OpenRouter models are currently available", file=sys.stderr)
        return 1

    max_attempts = max(1, args.max_attempts)
    candidates = ranked[:max_attempts]

    debug(f"Discovered {len(ranked)} free models", args.debug)
    debug(
        "Top candidates: " + ", ".join(f"{m['id']}[{m['score']}]" for m in candidates),
        args.debug,
    )

    attempted_models: List[str] = []

    for candidate in candidates:
        model_id = candidate.get("id")
        if not model_id:
            continue

        attempted_models.append(str(model_id))
        debug(f"Trying model: {model_id}", args.debug)

        try:
            response = openrouter_chat(api_key, str(model_id), messages, args.temperature)
            text = extract_text(response)
            output = {
                "selected_model": str(model_id),
                "response": text,
                "attempted_models": attempted_models,
                "free_model_candidates": len(ranked),
            }
            print(json.dumps(output, ensure_ascii=True))
            return 0
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", errors="replace") if hasattr(err, "read") else ""
            debug(f"Model failed ({model_id}): HTTP {err.code} {detail}".strip(), args.debug)
        except urllib.error.URLError as err:
            debug(f"Model failed ({model_id}): {err}", args.debug)
        except RuntimeError as err:
            debug(f"Model failed ({model_id}): {err}", args.debug)

    print(
        "No candidate free model produced a valid response. "
        f"Tried: {', '.join(attempted_models) if attempted_models else 'none'}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
