# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Characters Browser

Browse and discover Venice AI character personas.
API docs: https://docs.venice.ai
"""

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

VENICE_BASE_URL = "https://api.venice.ai/api/v1"


def get_api_key() -> str:
    """Get Venice API key from environment."""
    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable is not set", file=sys.stderr)
        print("Get your API key at https://venice.ai → Settings → API Keys", file=sys.stderr)
        sys.exit(1)
    return api_key


def list_characters(
    search: str | None = None,
    tag: str | None = None,
    limit: int = 20,
    output_format: str = "table",
    output_file: str | None = None,
) -> list:
    """List available Venice AI characters."""
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    print("Fetching characters...", file=sys.stderr)

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{VENICE_BASE_URL}/characters",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            characters = data.get("data", [])
            
            # Filter by search term
            if search:
                search_lower = search.lower()
                characters = [
                    c for c in characters
                    if search_lower in c.get("name", "").lower()
                    or search_lower in c.get("description", "").lower()
                ]
            
            # Filter by tag
            if tag:
                tag_lower = tag.lower()
                characters = [
                    c for c in characters
                    if any(tag_lower in t.lower() for t in c.get("tags", []))
                ]
            
            # Limit results
            characters = characters[:limit]
            
            print(f"Found {len(characters)} characters\n", file=sys.stderr)
            
            # Format output
            if output_format == "json":
                output = json.dumps({"data": characters, "object": "list"}, indent=2)
            elif output_format == "list":
                output = "\n".join(
                    f"{c.get('name', 'Unknown')} ({c.get('slug', '')})"
                    for c in characters
                )
            else:  # table
                output = format_table(characters)
            
            # Save or print
            if output_file:
                output_path = Path(output_file).resolve()
                output_path.write_text(output)
                print(f"Saved to: {output_path}", file=sys.stderr)
            else:
                print(output)
            
            return characters

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


def format_table(characters: list) -> str:
    """Format characters as a readable table."""
    if not characters:
        return "No characters found."
    
    lines = []
    
    # Header
    lines.append(f"{'NAME':<25} {'SLUG':<25} {'MODEL':<20} {'TAGS'}")
    lines.append("-" * 90)
    
    for char in characters:
        name = char.get("name", "Unknown")[:24]
        slug = char.get("slug", "-")[:24]
        model = char.get("modelId", "-")[:19]
        tags = ", ".join(char.get("tags", [])[:3])
        if len(char.get("tags", [])) > 3:
            tags += "..."
        
        lines.append(f"{name:<25} {slug:<25} {model:<20} {tags}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Browse Venice AI characters"
    )
    parser.add_argument(
        "--search", "-s",
        help="Search by name or description"
    )
    parser.add_argument(
        "--tag", "-t",
        help="Filter by tag"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=20,
        help="Max results (default: 20)"
    )
    parser.add_argument(
        "--format", "-f",
        dest="output_format",
        choices=["table", "json", "list"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save output to file"
    )

    args = parser.parse_args()
    
    list_characters(
        search=args.search,
        tag=args.tag,
        limit=args.limit,
        output_format=args.output_format,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()

