#!/usr/bin/env python3
"""
LiteLLM call helper - quickly call any LLM model.

Usage:
    python llm_call.py "Your prompt here"
    python llm_call.py "Your prompt" --model gpt-4o
    python llm_call.py "Your prompt" --model claude-sonnet-4-20250514 --json
    
Environment:
    LITELLM_API_BASE - LiteLLM proxy URL (optional)
    LITELLM_API_KEY - API key for proxy (optional)
    OPENAI_API_KEY - Direct OpenAI key
    ANTHROPIC_API_KEY - Direct Anthropic key
"""

import argparse
import json
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Call any LLM via LiteLLM")
    parser.add_argument("prompt", help="The prompt to send")
    parser.add_argument("--model", "-m", default="gpt-4o", help="Model to use (default: gpt-4o)")
    parser.add_argument("--system", "-s", help="System message")
    parser.add_argument("--json", action="store_true", help="Output raw JSON response")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature (default: 0.7)")
    parser.add_argument("--max-tokens", type=int, help="Max output tokens")
    args = parser.parse_args()

    try:
        import litellm
    except ImportError:
        print("Error: litellm not installed. Run: pip install litellm", file=sys.stderr)
        sys.exit(1)

    # Configure proxy if set
    if os.environ.get("LITELLM_API_BASE"):
        litellm.api_base = os.environ["LITELLM_API_BASE"]
    if os.environ.get("LITELLM_API_KEY"):
        litellm.api_key = os.environ["LITELLM_API_KEY"]

    # Build messages
    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": args.prompt})

    # Build kwargs
    kwargs = {
        "model": args.model,
        "messages": messages,
        "temperature": args.temperature,
    }
    if args.max_tokens:
        kwargs["max_tokens"] = args.max_tokens

    try:
        response = litellm.completion(**kwargs)
        
        if args.json:
            print(json.dumps(response.model_dump(), indent=2))
        else:
            print(response.choices[0].message.content)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
