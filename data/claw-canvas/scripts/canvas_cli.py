#!/usr/bin/env python3

import argparse
import json
import sys
from openclaw import default_api

def display_markdown(content: str, json_output: bool) -> None:
    try:
        # The canvas tool expects JSONL format for content
        # Each line in JSONL can be a JSON object with 'markdown' or 'html' key
        jsonl_content = json.dumps({"markdown": content})
        
        result = default_api.canvas(action="present", jsonl=jsonl_content)

        if json_output:
            print(json.dumps({"status": "success", "message": "Content displayed on canvas", "result": result}))
        else:
            print(f"Content displayed on canvas: {result}")
    except Exception as e:
        error_message = f"Error displaying content on canvas: {e}"
        if json_output:
            print(json.dumps({"status": "error", "message": error_message}))
        else:
            print(error_message, file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Claw Canvas CLI for OpenClaw")
    parser.add_argument("--json", action="store_true", help="Output JSON results")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Display Markdown Command
    parser_display_markdown = subparsers.add_parser("display_markdown", help="Display markdown content on the canvas")
    parser_display_markdown.add_argument("--content", type=str, required=True, help="Markdown content to display")

    args = parser.parse_args()

    if args.command == "display_markdown":
        display_markdown(args.content, args.json)

if __name__ == "__main__":
    main()
