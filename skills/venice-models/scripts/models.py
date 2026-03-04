# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Models Explorer

List and explore available Venice AI models.
No API key required - this endpoint is public.
API docs: https://docs.venice.ai
"""

import argparse
import json
import sys
from pathlib import Path

import httpx

VENICE_BASE_URL = "https://api.venice.ai/api/v1"

VALID_TYPES = ["all", "text", "image", "video", "tts", "asr", "embedding", "code", "upscale", "inpaint"]


def list_models(
    model_type: str = "all",
    output_format: str = "table",
    output_file: str | None = None,
) -> list:
    """List available Venice AI models."""

    params = {}
    if model_type != "all":
        params["type"] = model_type

    print(f"Fetching {model_type} models...", file=sys.stderr)

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{VENICE_BASE_URL}/models",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            models = data.get("data", [])
            
            print(f"Found {len(models)} models\n", file=sys.stderr)
            
            # Format output
            if output_format == "json":
                output = json.dumps(data, indent=2)
            elif output_format == "names":
                output = "\n".join(m.get("id", "unknown") for m in models)
            else:  # table
                output = format_table(models)
            
            # Save or print
            if output_file:
                output_path = Path(output_file).resolve()
                output_path.write_text(output)
                print(f"Saved to: {output_path}", file=sys.stderr)
            else:
                print(output)
            
            return models

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        try:
            error_data = e.response.json()
            print(f"Details: {error_data}", file=sys.stderr)
        except Exception:
            print(f"Response: {e.response.text[:500]}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Request Error: {e}", file=sys.stderr)
        sys.exit(1)


def format_table(models: list) -> str:
    """Format models as a readable table."""
    if not models:
        return "No models found."
    
    lines = []
    
    # Header
    lines.append(f"{'MODEL ID':<35} {'TYPE':<10} {'CONTEXT':<10} {'PRICING'}")
    lines.append("-" * 80)
    
    for model in models:
        model_id = model.get("id", "unknown")[:34]
        model_type = model.get("type", "-")[:9]
        
        # Context length
        context = model.get("model_spec", {}).get("context", {})
        ctx_len = context.get("total") or context.get("max") or context.get("input")
        if ctx_len:
            if ctx_len >= 1000:
                ctx_str = f"{ctx_len // 1000}K"
            else:
                ctx_str = str(ctx_len)
        else:
            ctx_str = "-"
        
        # Pricing
        pricing = model.get("pricing", {})
        pricing_str = format_pricing(pricing, model_type)
        
        lines.append(f"{model_id:<35} {model_type:<10} {ctx_str:<10} {pricing_str}")
    
    return "\n".join(lines)


def format_pricing(pricing: dict, model_type: str) -> str:
    """Format pricing info for display."""
    if not pricing:
        return "-"
    
    # Text models: input/output tokens
    input_price = pricing.get("input")
    output_price = pricing.get("output")
    if input_price is not None and output_price is not None:
        return f"${input_price}/M in, ${output_price}/M out"
    
    # Image models: per image
    per_image = pricing.get("perImage")
    if per_image is not None:
        return f"${per_image}/image"
    
    # TTS: per character
    per_char = pricing.get("perCharacter")
    if per_char is not None:
        return f"${per_char}/char"
    
    # ASR: per minute
    per_minute = pricing.get("perMinute")
    if per_minute is not None:
        return f"${per_minute}/minute"
    
    # Video: per second
    per_second = pricing.get("perSecond")
    if per_second is not None:
        return f"${per_second}/second"
    
    return "-"


def main():
    parser = argparse.ArgumentParser(
        description="Explore Venice AI models"
    )
    parser.add_argument(
        "--type", "-t",
        choices=VALID_TYPES,
        default="all",
        help="Filter by model type (default: all)"
    )
    parser.add_argument(
        "--format", "-f",
        dest="output_format",
        choices=["table", "json", "names"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save output to file"
    )

    args = parser.parse_args()
    
    list_models(
        model_type=args.type,
        output_format=args.output_format,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()

