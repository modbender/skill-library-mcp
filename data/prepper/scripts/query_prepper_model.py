#!/usr/bin/env python3
"""
Query the ollama dolphin-llama3 model for prepper/survival questions.
Usage: python3 query_prepper_model.py "Your question here"
Optional: python3 query_prepper_model.py --json "Your question here"  (returns JSON for programmatic use)
"""

import requests
import sys
import json

OLLAMA_HOST = "http://localhost:11434"
MODEL = "dolphin-llama3"
TIMEOUT = 120  # 2 minutes for model response


def query_prepper_model(question):
    """
    Query the dolphin-llama3 model with a prepper/survival question.
    
    Args:
        question (str): The prepper/survival question to ask
        
    Returns:
        str: The model's response
        
    Raises:
        ConnectionError: If ollama is not reachable
        Exception: For other API errors
    """
    
    url = f"{OLLAMA_HOST}/api/generate"
    
    # Prepare the payload
    payload = {
        "model": MODEL,
        "prompt": question,
        "stream": False,  # Get full response at once
        "temperature": 0.7,  # Balanced creativity/accuracy
    }
    
    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Cannot connect to ollama at {OLLAMA_HOST}.\n"
            f"Is ollama running? Start with: ollama serve"
        )
    except requests.exceptions.Timeout:
        raise TimeoutError(
            f"Request to ollama timed out after {TIMEOUT}s. "
            f"The model may be slow or not responding."
        )
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise Exception(
                f"Model '{MODEL}' not found in ollama.\n"
                f"Pull it with: ollama pull {MODEL}"
            )
        raise Exception(f"Ollama API error: {response.status_code} {response.text}")
    
    # Parse response
    data = response.json()
    return data.get("response", "").strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 query_prepper_model.py 'Your question here'")
        print("       python3 query_prepper_model.py --json 'Your question here'")
        print("\nExample:")
        print("  python3 query_prepper_model.py 'How do I purify water?'")
        print("  python3 query_prepper_model.py --json 'How do I purify water?'")
        sys.exit(1)
    
    # Check for --json flag
    output_json = False
    start_idx = 1
    if sys.argv[1] == "--json":
        output_json = True
        start_idx = 2
    
    if len(sys.argv) <= start_idx:
        print("Error: No question provided", file=sys.stderr)
        sys.exit(1)
    
    question = " ".join(sys.argv[start_idx:])
    
    try:
        answer = query_prepper_model(question)
        
        if output_json:
            # Return as JSON for programmatic use (e.g., integration with Claude)
            result = {
                "success": True,
                "source": "dolphin-llama3-ollama",
                "question": question,
                "answer": answer
            }
            print(json.dumps(result))
        else:
            # Return as human-readable text
            print(f"Querying dolphin-llama3 model for: {question}\n")
            print("-" * 60)
            print(answer)
            print("-" * 60)
            
    except (ConnectionError, TimeoutError, Exception) as e:
        error_msg = str(e)
        if output_json:
            result = {
                "success": False,
                "source": "dolphin-llama3-ollama",
                "question": question,
                "error": error_msg
            }
            print(json.dumps(result))
        else:
            print(f"❌ Error: {error_msg}", file=sys.stderr)
        sys.exit(1)
