#!/usr/bin/env python3
"""
Test script for external AI integration functions.

This script demonstrates how to use the external_ai_integration module.
It can be run manually to verify the basic functionality (simulated browser calls,
Hugging Face API if token available).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from external_ai_integration import (
        ask_chatgpt,
        ask_claude,
        ask_gemini,
        hf_inference,
        get_hf_token,
        external_ai_assist,
        log_external_failure
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you are in the skills/external-ai-integration directory.")
    sys.exit(1)

def test_browser_functions():
    """Test simulated browser calls."""
    print("=== Simulated browser calls ===")
    prompt = "What is the capital of France?"
    for name, func in [("ChatGPT", ask_chatgpt), ("Claude", ask_claude), ("Gemini", ask_gemini)]:
        resp = func(prompt)
        print(f"{name}: {resp}")
    print()

def test_hugging_face():
    """Test Hugging Face API if token available."""
    print("=== Hugging Face API ===")
    token = get_hf_token()
    if token:
        print(f"Token found ({token[:10]}...). Testing with a small model.")
        try:
            # Use a small, fast model for testing
            resp = hf_inference("google/flan-t5-small", "Translate English to German: Hello world!")
            print(f"Response: {resp}")
        except Exception as e:
            print(f"HF inference failed: {e}")
            log_external_failure("Hugging Face", str(e), "test_hugging_face")
    else:
        print("No Hugging Face token found. Skipping real API call.")
        # Demonstrate error handling
        try:
            hf_inference("dummy/model", "test")
        except ValueError as e:
            print(f"Expected error: {e}")
    print()

def test_orchestration():
    """Test the routing function."""
    print("=== Orchestration (external_ai_assist) ===")
    tasks = [
        ("translation", "Translate English to German: Good morning."),
        ("code_review", "def add(a,b): return a+b"),
        ("creative_writing", "Write a haiku about AI."),
    ]
    for task_type, prompt in tasks:
        result = external_ai_assist(task_type, prompt)
        print(f"{task_type}: {result}")
    print()

def test_failure_logging():
    """Test logging of failures (writes to memory/YYYY‑MM‑DD.md)."""
    print("=== Failure logging ===")
    log_external_failure("ChatGPT", "Simulated timeout", "test_failure_logging")
    print("Logged failure (check memory/YYYY‑MM‑DD.md).")
    print()

if __name__ == "__main__":
    print("Running external AI integration tests...\n")
    test_browser_functions()
    test_hugging_face()
    test_orchestration()
    test_failure_logging()
    print("Tests completed (browser calls are simulated; real calls require Chrome Relay and HF token).")