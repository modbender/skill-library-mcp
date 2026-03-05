#!/usr/bin/env python3
"""
External AI Integration – Core implementation.

Provides functions to call external AI models via browser automation (Chrome Relay)
and Hugging Face Inference API.

This module is intended to be used as a reference implementation; adapt the functions
to your specific environment and requirements.
"""

import os
import json
import time
import subprocess
import sys
from typing import Optional, Dict, Any, List

# Browser automation relies on the OpenClaw browser tool (called via CLI or tool call).
# This module assumes you are running within an OpenClaw session where the `browser` tool is available.
# For standalone testing, you would need to mock those calls.

# Hugging Face API – optional import
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    requests = None
    HAS_REQUESTS = False

# ------------------------------------------------------------------------------
# Browser Automation (Chrome Relay) for Web‑Based LLMs
# ------------------------------------------------------------------------------

def ask_chatgpt(prompt: str, timeout_sec: int = 30) -> Optional[str]:
    """
    Send a prompt to ChatGPT via Chrome Relay and return the response.

    Assumes:
    - Chrome Relay extension is installed and a tab is attached.
    - ChatGPT website (chatgpt.com) is open and logged in.
    - The assistant has access to the `browser` tool.

    This is a conceptual implementation; actual tool calls would be made via
    OpenClaw's `browser` tool (not directly from Python). Adapt accordingly.

    Returns:
        Extracted response text, or None if failed.
    """
    # In reality, you would call the browser tool via OpenClaw's tool API.
    # This function outlines the steps; you would replace each step with actual tool calls.

    steps = [
        ("open", {"profile": "chrome", "targetUrl": "https://chatgpt.com"}),
        ("snapshot", {"refs": "aria"}),
        # Assume snapshot returns a reference to the input field and send button
        # This is pseudo‑code; actual references depend on the page structure.
        ("act", {"kind": "type", "ref": "input_ref", "text": prompt}),
        ("act", {"kind": "click", "ref": "send_button_ref"}),
        ("wait", {"timeMs": 10000}),  # wait for response
        ("snapshot", {"refs": "aria"}),
        # Extract response from the last message bubble
    ]

    # For demonstration, we simulate a failure if prompt is empty
    if not prompt.strip():
        return None

    # In a real implementation, you would iterate through steps, calling the browser tool.
    # Since we cannot call OpenClaw tools directly from this Python module,
    # this function serves as a blueprint.

    # Placeholder: simulate a response
    simulated_response = f"[Simulated ChatGPT response to: {prompt[:50]}...]"
    return simulated_response


def ask_claude(prompt: str, timeout_sec: int = 30) -> Optional[str]:
    """Send a prompt to Claude via Chrome Relay and return the response."""
    # Similar to ask_chatgpt but targeting claude.ai
    # Implementation would follow the same pattern.
    if not prompt.strip():
        return None
    simulated_response = f"[Simulated Claude response to: {prompt[:50]}...]"
    return simulated_response


def ask_gemini(prompt: str, timeout_sec: int = 30) -> Optional[str]:
    """Send a prompt to Gemini via Chrome Relay and return the response."""
    # Similar pattern, target gemini.google.com
    if not prompt.strip():
        return None
    simulated_response = f"[Simulated Gemini response to: {prompt[:50]}...]"
    return simulated_response

# ------------------------------------------------------------------------------
# Hugging Face Inference API
# ------------------------------------------------------------------------------

def get_hf_token() -> Optional[str]:
    """
    Retrieve Hugging Face API token from 1Password or environment variable.

    Uses the `op` CLI (1Password) if available, else falls back to HF_TOKEN env var.
    """
    # Try 1Password first
    try:
        token = subprocess.check_output(
            ["op", "read", "op://Personal/HuggingFace/api_token"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        if token:
            return token
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fallback to environment variable
    token = os.getenv("HF_TOKEN")
    if token:
        return token

    # Fallback to file
    token_file = os.path.expanduser("~/.huggingface/token")
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            token = f.read().strip()
            if token:
                return token

    return None


def hf_inference(
    model: str,
    inputs: str,
    parameters: Optional[Dict[str, Any]] = None,
    wait_for_model: bool = True,
    timeout: int = 30
) -> Any:
    """
    Call Hugging Face Inference API.

    Args:
        model: Model identifier (e.g., "google/flan-t5-large").
        inputs: Input text (or list/dict depending on model).
        parameters: Additional generation parameters (temperature, max_length, etc.).
        wait_for_model: If True, add {"options":{"wait_for_model":true}} to payload.
        timeout: Request timeout in seconds.

    Returns:
        API response (usually a list of dicts or strings).

    Raises:
        ValueError: If token is missing or request fails.
    """
    token = get_hf_token()
    if not token:
        raise ValueError("Hugging Face API token not found. Set HF_TOKEN env var or store in 1Password.")

    # Use requests if available, otherwise fall back to curl
    if HAS_REQUESTS:
        url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"inputs": inputs}
        if parameters:
            payload.update(parameters)
        if wait_for_model:
            payload.setdefault("options", {})["wait_for_model"] = True

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Hugging Face API request failed: {e}")
    else:
        # Fallback to curl implementation
        return hf_inference_curl(model, inputs, parameters, wait_for_model)


def hf_inference_curl(
    model: str,
    inputs: str,
    parameters: Optional[Dict[str, Any]] = None,
    wait_for_model: bool = True
) -> Any:
    """
    Alternative implementation using curl (useful if requests module not available).
    """
    token = get_hf_token()
    if not token:
        raise ValueError("Hugging Face API token not found.")

    url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {"inputs": inputs}
    if parameters:
        payload.update(parameters)
    if wait_for_model:
        payload.setdefault("options", {})["wait_for_model"] = True

    cmd = [
        "curl", "-s",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
        url
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        return json.loads(output)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        raise ValueError(f"Curl call failed: {e}")


# ------------------------------------------------------------------------------
# Orchestration & Decision Logic
# ------------------------------------------------------------------------------

def external_ai_assist(
    task_type: str,
    prompt: str,
    preferred_model: Optional[str] = None
) -> Optional[str]:
    """
    Route a task to an appropriate external AI model.

    task_type: One of "code_review", "translation", "creative_writing",
               "summarization", "analysis", "brainstorming", "other".
    preferred_model: If specified, try this model first (e.g., "chatgpt", "claude", "hf:model_id").
    """
    model_map = {
        "code_review": "claude",
        "translation": "hf:Helsinki-NLP/opus-mt-en-de",
        "creative_writing": "chatgpt",
        "summarization": "hf:facebook/bart-large-cnn",
        "analysis": "claude",
        "brainstorming": "chatgpt",
        "other": "chatgpt",
    }

    target = preferred_model or model_map.get(task_type, "chatgpt")

    try:
        if target.startswith("hf:"):
            model_id = target[3:]
            result = hf_inference(model_id, prompt)
            # Extract generated text from common response formats
            if isinstance(result, list) and len(result) > 0:
                first = result[0]
                if isinstance(first, dict) and "generated_text" in first:
                    return first["generated_text"]
                elif isinstance(first, str):
                    return first
            # Fallback: return whole result as string
            return str(result)
        elif target == "chatgpt":
            return ask_chatgpt(prompt)
        elif target == "claude":
            return ask_claude(prompt)
        elif target == "gemini":
            return ask_gemini(prompt)
        else:
            # Unknown target, fallback to ChatGPT
            return ask_chatgpt(prompt)
    except Exception as e:
        # Log error (in a real implementation, write to memory/ file)
        print(f"External AI call failed: {e}", file=sys.stderr)
        return None


# ------------------------------------------------------------------------------
# Utility Functions
# ------------------------------------------------------------------------------

def log_external_failure(service: str, error: str, context: str = ""):
    """
    Log an external AI failure to memory/YYYY‑MM‑DD.md.

    In a real OpenClaw session, you would append to the daily memory file.
    """
    date = time.strftime("%Y-%m-%d")
    memory_file = f"memory/{date}.md"
    entry = (
        f"\n## [external‑ai‑failure] {service} failed\n"
        f"Date: {date}\n"
        f"Tags: external‑ai‑failure, {service}\n"
        f"Error: {error}\n"
        f"Context: {context}\n"
    )
    try:
        with open(memory_file, "a") as f:
            f.write(entry)
    except IOError:
        # fallback to stderr
        print(f"Could not write to {memory_file}", file=sys.stderr)
        print(entry, file=sys.stderr)


# ------------------------------------------------------------------------------
# Example Usage (for testing)
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    # Quick test: Hugging Face inference (requires token)
    if get_hf_token():
        try:
            resp = hf_inference("google/flan-t5-small", "Translate English to German: Hello world!")
            print("HF test:", resp)
        except ValueError as e:
            print("HF test failed:", e)
    else:
        print("No HF token; skipping HF test.")

    # Simulated browser calls
    print("Simulated ChatGPT:", ask_chatgpt("What is 2+2?"))
    print("Simulated Claude:", ask_claude("What is 2+2?"))

    # Orchestration example
    result = external_ai_assist("translation", "Translate English to German: Good morning.")
    print("Orchestration result:", result)