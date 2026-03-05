#!/usr/bin/env python3
import requests
import os

# Production API URL
# This is managed by the extension maintainers.
API_URL = "https://api.trunkate.ai"

def optimize_prompt(prompt: str, budget: int = 1000, model: str = "gpt-4o") -> str:
    """
    Optimizes a prompt using the private Trunkate AI API.
    
    Args:
        prompt (str): The text to optimize.
        budget (int): Maximum token budget.
        model (str): Target LLM model (default: "gpt-4o").
        
    Returns:
        str: The optimized prompt text.
    """
    # Allow developer override for testing, otherwise use production URL
    api_url = os.environ.get("TRUNKATE_API_URL", API_URL).rstrip("/")
    api_key = os.environ.get("TRUNKATE_API_KEY")
    
    if not api_key:
        print("Error: TRUNKATE_API_KEY environment variable is required to use this skill.")
        return prompt
    
    payload = {
        "text": prompt,
        "budget": budget,
        "model": model
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{api_url}/optimize", json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # We can return just the text, or a formatted string with stats
        optimized_text = data.get("optimized_text", prompt)
        reduction = data.get("reduction_percent", 0)
        
        # Optional: Append stats for debugging?
        # return f"{optimized_text}\n\n[Optimization: -{reduction}%]"
        return optimized_text
        
    except Exception as e:
        # Fail gracefully: return original prompt
        print(f"Error optimizing prompt: {e}")
        return prompt

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Trunkate AI CLI")
    parser.add_argument("--text", required=True, help="The text to optimize")
    parser.add_argument("--budget", type=int, default=1000, help="Max token budget")
    parser.add_argument("--model", default="gpt-4o", help="Target model")
    
    args = parser.parse_args()
    
    # The 'budget' argument always has a default value, so args.budget will always be set.
    # The original call already passed args.model.
    # The requested change simplifies the call to use keyword arguments for clarity.
    result = optimize_prompt(args.text, budget=args.budget, model=args.model)
    print(result)
