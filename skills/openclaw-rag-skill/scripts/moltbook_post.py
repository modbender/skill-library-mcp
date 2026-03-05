#!/usr/bin/env python3
"""
Moltbook Post Tool - Post to Moltbook from the RAG skill

Usage:
    python3 moltbook_post.py "Title" "Content"
    python3 moltbook_post.py --file post.md
"""

import os
import sys
import json
import requests
from pathlib import Path

# Configuration
API_BASE = "https://www.moltbook.com/api/v1"
CONFIG_PATH = os.path.expanduser("~/.config/moltbook/credentials.json")


def load_api_key():
    """Load API key from config file or environment variable"""
    # Try environment variable first
    api_key = os.environ.get('MOLTBOOK_API_KEY')
    if api_key:
        return api_key

    # Try config file
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            return config.get('api_key')

    # No key configured
    return None


def create_post(title, content, submolt="general", url=None):
    """Create a post to Moltbook"""
    api_key = load_api_key()

    if not api_key:
        print("❌ Error: No Moltbook API key found")
        print(f"   Set environment variable MOLTBOOK_API_KEY or create {CONFIG_PATH}")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "submolt": submolt,
        "title": title,
        "content": content
    }

    if url:
        data["url"] = url

    try:
        response = requests.post(
            f"{API_BASE}/posts",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 201:
            result = response.json()
            post_id = result.get('data', {}).get('id')

            print(f"✅ Post created successfully!")
            print(f"   Post ID: {post_id}")
            print(f"   URL: https://moltbook.com/posts/{post_id}")

            if 'data' in result and 'author' in result['data']:
                print(f"   Author: {result['data']['author']['name']}")

            return True
        elif response.status_code == 429:
            error = response.json()
            retry = error.get('hint', {}).get('retry_after_minutes', 'unknown')
            print(f"⏸️  Rate limited. Wait {retry} minutes before posting again.")
            return False
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False


def post_from_file(file_path, submolt="general"):
    """Read post from markdown file and publish"""
    path = Path(file_path)

    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    content = path.read_text()

    # Extract title from first heading or use filename
    lines = content.split('\n')
    title = "RAG Skill Announcement"

    for line in lines:
        if line.startswith('#'):
            title = line.lstrip('#').strip()
            break

    # Remove title from content
    if content.startswith('#'):
        parts = content.split('\n', 1)
        if len(parts) > 1:
            content = parts[1].strip()

    return create_post(title, content, submolt)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 moltbook_post.py \"Title\" \"Content\"")
        print("  python3 moltbook_post.py --file post.md")
        print("  python3 moltbook_post.py --file post.md --submolt general")
        sys.exit(1)

    # Check for file mode
    if sys.argv[1] == '--file':
        file_path = sys.argv[2]
        submolt = sys.argv[3] if len(sys.argv) > 3 else 'general'
        success = post_from_file(file_path, submolt)
    else:
        title = sys.argv[1]
        content = sys.argv[2] if len(sys.argv) > 2 else ""
        submolt = sys.argv[3] if len(sys.argv) > 3 else 'general'
        success = create_post(title, content, submolt)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()