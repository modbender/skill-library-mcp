#!/usr/bin/env python3
"""
Save a memo/note to Cubox using the Open API.

Usage:
    python save_memo.py <content> [--title "Title"] [--description "Desc"] [--tags "tag1,tag2"] [--folder "Folder"]

Environment:
    CUBOX_API_URL: Your personal Cubox API URL (required)
"""

import os
import sys
import json
import argparse
import requests


def save_memo(content: str, title: str = None, description: str = None,
              tags: list = None, folder: str = None) -> dict:
    """
    Save a memo to Cubox.
    
    Args:
        content: The memo text content
        title: Optional title for the memo
        description: Optional description
        tags: Optional list of tags
        folder: Optional folder name (defaults to Inbox)
    
    Returns:
        API response as dict
    """
    api_url = os.environ.get("CUBOX_API_URL")
    if not api_url:
        raise ValueError("CUBOX_API_URL environment variable is not set")
    
    payload = {
        "type": "memo",
        "content": content
    }
    
    if title:
        payload["title"] = title
    if description:
        payload["description"] = description
    if tags:
        payload["tags"] = tags
    if folder:
        payload["folder"] = folder
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(api_url, json=payload, headers=headers)
    response.raise_for_status()
    
    return response.json() if response.text else {"status": "success"}


def main():
    parser = argparse.ArgumentParser(description="Save a memo to Cubox")
    parser.add_argument("content", help="The memo text content")
    parser.add_argument("--title", "-t", help="Title for the memo")
    parser.add_argument("--description", "-d", help="Description for the memo")
    parser.add_argument("--tags", help="Comma-separated list of tags")
    parser.add_argument("--folder", "-f", help="Target folder name")
    
    args = parser.parse_args()
    
    tags_list = None
    if args.tags:
        tags_list = [tag.strip() for tag in args.tags.split(",")]
    
    try:
        result = save_memo(
            content=args.content,
            title=args.title,
            description=args.description,
            tags=tags_list,
            folder=args.folder
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to save memo - {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
