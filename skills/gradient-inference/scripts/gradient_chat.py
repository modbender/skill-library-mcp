#!/usr/bin/env python3
"""
🦞 Gradient AI — Chat & Inference

Call LLMs via DigitalOcean's Gradient Serverless Inference API.
Supports both the Chat Completions API (OpenAI-compatible) and the
newer Responses API with prompt caching.

Usage:
    python3 gradient_chat.py --prompt "Hello!" --model openai-gpt-oss-120b
    python3 gradient_chat.py --prompt "Explain RAG" --responses-api --cache
    python3 gradient_chat.py --system "You are a pirate." --prompt "Ahoy?"

Docs: https://docs.digitalocean.com/products/gradient-ai-platform/how-to/use-serverless-inference/
"""

import argparse
import json
import os
import sys
from typing import Optional

import requests

INFERENCE_BASE_URL = "https://inference.do-ai.run/v1"
CHAT_COMPLETIONS_URL = f"{INFERENCE_BASE_URL}/chat/completions"
RESPONSES_URL = f"{INFERENCE_BASE_URL}/responses"


def chat_completion(
    messages: list[dict],
    model: str = "openai-gpt-oss-120b",
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    stream: bool = False,
) -> dict:
    """Call the Gradient Chat Completions API.

    OpenAI-compatible endpoint for structured conversations.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.
        model: Model identifier (e.g., 'openai-gpt-oss-120b').
        api_key: Gradient Model Access Key. Falls back to GRADIENT_API_KEY.
        temperature: Sampling temperature (0.0–2.0).
        max_tokens: Maximum tokens in the response.
        stream: Whether to stream the response (not implemented in this version).

    Returns:
        dict with 'success', 'content' (response text), 'usage', and 'message'.
    """
    api_key = api_key or os.environ.get("GRADIENT_API_KEY", "")

    if not api_key:
        return {"success": False, "content": "", "usage": {}, "message": "No GRADIENT_API_KEY configured."}

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        resp = requests.post(CHAT_COMPLETIONS_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        return {
            "success": True,
            "content": content,
            "usage": usage,
            "model": model,
            "api": "chat/completions",
            "message": "OK",
        }
    except requests.RequestException as e:
        return {"success": False, "content": "", "usage": {}, "message": f"API request failed: {str(e)}"}
    except (KeyError, IndexError) as e:
        return {"success": False, "content": "", "usage": {}, "message": f"Unexpected response format: {str(e)}"}


def responses_api(
    input_text: str,
    model: str = "openai-gpt-oss-120b",
    api_key: Optional[str] = None,
    store: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> dict:
    """Call the Gradient Responses API.

    The Responses API is DigitalOcean's recommended endpoint for new
    integrations. Simpler request format and supports prompt caching
    via store=True.

    Args:
        input_text: The prompt text.
        model: Model identifier.
        api_key: Gradient Model Access Key. Falls back to GRADIENT_API_KEY.
        store: If True, enables prompt caching for cost savings across turns.
        temperature: Sampling temperature.
        max_tokens: Maximum output tokens.

    Returns:
        dict with 'success', 'content', 'usage', and 'message'.
    """
    api_key = api_key or os.environ.get("GRADIENT_API_KEY", "")

    if not api_key:
        return {"success": False, "content": "", "usage": {}, "message": "No GRADIENT_API_KEY configured."}

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "input": input_text,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        if store:
            payload["store"] = True

        resp = requests.post(RESPONSES_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        data = resp.json()

        # Responses API returns output in various formats — handle both
        if "output" in data:
            # May be a list of output items
            if isinstance(data["output"], list):
                content = "\n".join(
                    item.get("content", [{}])[0].get("text", "")
                    if isinstance(item.get("content"), list)
                    else str(item.get("content", ""))
                    for item in data["output"]
                    if item.get("type") == "message"
                )
            else:
                content = str(data["output"])
        elif "choices" in data:
            # Fallback: some models may return chat-completions format
            content = data["choices"][0]["message"]["content"]
        else:
            content = json.dumps(data)

        usage = data.get("usage", {})

        return {
            "success": True,
            "content": content,
            "usage": usage,
            "model": model,
            "api": "responses",
            "cached": store,
            "message": "OK",
        }
    except requests.RequestException as e:
        return {"success": False, "content": "", "usage": {}, "message": f"API request failed: {str(e)}"}
    except (KeyError, IndexError) as e:
        return {"success": False, "content": "", "usage": {}, "message": f"Unexpected response format: {str(e)}"}


def pick_api(use_responses_api: bool) -> str:
    """Return the appropriate API URL based on the flag.

    Args:
        use_responses_api: If True, return Responses API URL.

    Returns:
        The endpoint URL string.
    """
    return RESPONSES_URL if use_responses_api else CHAT_COMPLETIONS_URL


# ─── CLI Interface ────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="🦞 Call Gradient AI LLMs"
    )
    parser.add_argument("--prompt", required=True, help="The prompt to send")
    parser.add_argument("--system", default=None, help="System message (chat completions only)")
    parser.add_argument("--model", default="openai-gpt-oss-120b", help="Model ID")
    parser.add_argument("--responses-api", action="store_true", help="Use the Responses API instead of Chat Completions")
    parser.add_argument("--cache", action="store_true", help="Enable prompt caching (Responses API only)")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    parser.add_argument("--max-tokens", type=int, default=1000, help="Max output tokens")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.responses_api:
        result = responses_api(
            input_text=args.prompt,
            model=args.model,
            store=args.cache,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
    else:
        messages = []
        if args.system:
            messages.append({"role": "system", "content": args.system})
        messages.append({"role": "user", "content": args.prompt})

        result = chat_completion(
            messages=messages,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )

    if not result["success"]:
        print(f"Error: {result['message']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["content"])

        # Print usage stats to stderr
        usage = result.get("usage", {})
        if usage:
            prompt_tokens = usage.get("prompt_tokens", "?")
            completion_tokens = usage.get("completion_tokens", "?")
            print(f"\n📊 Tokens: {prompt_tokens} in / {completion_tokens} out | Model: {result.get('model', '?')} | API: {result.get('api', '?')}", file=sys.stderr)


if __name__ == "__main__":
    main()
