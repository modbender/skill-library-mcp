# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Embeddings

Generate vector embeddings using Venice's /embeddings endpoint.
API docs: https://docs.venice.ai
"""

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

VENICE_BASE_URL = "https://api.venice.ai/api/v1"

AVAILABLE_MODELS = [
    "text-embedding-3-small",
    "text-embedding-3-large",
    "text-embedding-ada-002",
]


def get_api_key() -> str:
    """Get Venice API key from environment."""
    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable is not set", file=sys.stderr)
        print("Get your API key at https://venice.ai → Settings → API Keys", file=sys.stderr)
        sys.exit(1)
    return api_key


def generate_embeddings(
    text: str | None = None,
    file_path: str | None = None,
    output: str | None = None,
    model: str = "text-embedding-3-small",
) -> list[float]:
    """Generate embeddings using Venice AI."""
    api_key = get_api_key()

    # Get text from file if specified
    if file_path:
        try:
            text = Path(file_path).read_text(encoding="utf-8")
            print(f"Read {len(text)} characters from {file_path}", file=sys.stderr)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    
    if not text:
        print("Error: Either --text or --file must be provided", file=sys.stderr)
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "input": text,
    }

    print(f"Generating embeddings with {model}...", file=sys.stderr)
    print(f"Text length: {len(text)} characters", file=sys.stderr)

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{VENICE_BASE_URL}/embeddings",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "data" not in data or len(data["data"]) == 0:
                print("Error: No embedding data in response", file=sys.stderr)
                sys.exit(1)
            
            embedding = data["data"][0]["embedding"]
            dimensions = len(embedding)
            
            print(f"Generated embedding with {dimensions} dimensions", file=sys.stderr)
            
            result = {
                "model": model,
                "dimensions": dimensions,
                "embedding": embedding,
                "text_length": len(text),
            }
            
            if output:
                output_path = Path(output).resolve()
                output_path.write_text(json.dumps(result, indent=2))
                print(f"Embeddings saved to: {output_path}", file=sys.stderr)
            else:
                # Print just the embedding array for piping
                print(json.dumps(embedding))
            
            return embedding

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        try:
            error_data = e.response.json()
            print(f"Details: {error_data}", file=sys.stderr)
        except Exception:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Request Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate vector embeddings using Venice AI"
    )
    parser.add_argument(
        "--text", "-t",
        help="Text to embed (use this OR --file)"
    )
    parser.add_argument(
        "--file", "-f",
        dest="file_path",
        help="File to read text from"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file for embeddings (prints to stdout if not set)"
    )
    parser.add_argument(
        "--model", "-m",
        default="text-embedding-3-small",
        choices=AVAILABLE_MODELS,
        help="Embedding model (default: text-embedding-3-small)"
    )

    args = parser.parse_args()
    
    if not args.text and not args.file_path:
        parser.error("Either --text or --file must be provided")
    
    generate_embeddings(
        text=args.text,
        file_path=args.file_path,
        output=args.output,
        model=args.model,
    )


if __name__ == "__main__":
    main()
