#!/usr/bin/env python3
"""
arXiv Paper Reviews - Command Line Client

Usage:
    python paper_client.py list --date 2026-02-04 --categories cs.AI --limit 5
    python paper_client.py show <paper_key>
    python paper_client.py comments <paper_key>
    python paper_client.py comment <paper_key> "This is a great paper"
    python paper_client.py search --query "transformer" --limit 10
    python paper_client.py import --url "https://arxiv.org/abs/2602.09012"
"""

import argparse
import json
import sys
from pathlib import Path
import requests


def load_config():
    """Load configuration file"""
    config_path = Path(__file__).parent / "config.json"
    if not config_path.exists():
        print(f"Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path, 'r') as f:
        return json.load(f)


def get_headers(config):
    """Get request headers (including API Key if configured)"""
    headers = {}
    if config.get("apiKey"):
        headers["X-API-Key"] = config["apiKey"]
    return headers


def get_api_base(config):
    """Get API base URL without trailing slash"""
    base = config['apiBaseUrl'].rstrip('/')
    return base


def cmd_list(args):
    """Fetch paper list"""
    config = load_config()
    url = f"{get_api_base(config)}/v1/papers"

    params = {"limit": args.limit}
    if args.date:
        params["date"] = args.date
    if args.interest:
        params["interest"] = args.interest
    if args.categories:
        params["categories"] = args.categories
    if args.offset:
        params["offset"] = args.offset

    headers = get_headers(config)

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)

    papers = response.json()

    if not papers:
        print("No papers found")
        return

    print(f"Found {len(papers)} papers:\n")

    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   Paper ID: {paper['paper_key']}")
        print(f"   Categories: {paper['categories']}")
        print(f"   Authors: {paper['authors'][:80]}{'...' if len(paper['authors']) > 80 else ''}")
        print(f"   Abstract: {paper['abstract'][:150]}{'...' if len(paper['abstract']) > 150 else ''}")
        print(f"   Submitted: {paper['first_submitted_date']}")
        print(f"   Announced: {paper['first_announced_date']}")
        print(f"   Interest: {paper.get('interest', 'N/A')}")
        print()


def cmd_show(args):
    """Show paper details"""
    config = load_config()
    url = f"{get_api_base(config)}/v1/papers/{args.paper_key}"
    headers = get_headers(config)

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)

    paper = response.json()

    print(f"Title: {paper['title']}")
    print(f"Paper ID: {paper['paper_key']}")
    print(f"Categories: {paper['categories']}")
    print(f"Authors: {paper['authors']}")
    print(f"Submitted: {paper['first_submitted_date']}")
    print(f"Announced: {paper['first_announced_date']}")
    print(f"Interest: {paper.get('interest', 'N/A')}")
    print(f"\nAbstract:")
    print(paper['abstract'])

    if paper.get('comments'):
        print(f"\nComments ({len(paper['comments'])}):")
        for comment in paper['comments']:
            print(f"- {comment['source_name']} ({comment['created_at']}):")
            print(f"  {comment['content']}")


def cmd_comments(args):
    """Fetch paper comments list"""
    config = load_config()
    url = f"{get_api_base(config)}/public/papers/{args.paper_key}/comments"

    params = {"limit": args.limit}
    if args.offset:
        params["offset"] = args.offset

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)

    comments = response.json()

    if not comments:
        print("No comments")
        return

    print(f"Total {len(comments)} comments:\n")

    for comment in comments:
        print(f"- {comment['source_name']} ({comment['created_at']}):")
        print(f"  {comment['content']}")
        print()


def cmd_comment(args):
    """Add comment"""
    config = load_config()
    url = f"{get_api_base(config)}/public/papers/{args.paper_key}/comments"

    # If author name not specified, use default from config
    author_name = args.author_name or config.get("defaultAuthorName", "Anonymous")

    data = {
        "content": args.content,
        "author_name": author_name
    }

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=data
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)

    result = response.json()
    print("Comment added successfully!")
    print(f"Comment ID: {result['id']}")
    print(f"Author: {result['source_name']}")
    print(f"Content: {result['content']}")
    print(f"Time: {result['created_at']}")


def cmd_search(args):
    """Search papers"""
    config = load_config()
    url = f"{get_api_base(config)}/public/papers/search"

    params = {
        "q": args.query,
        "limit": args.limit
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)

    result = response.json()

    if not result.get('papers'):
        print("No papers found")
        return

    print(f"Search query: {result['query']}")
    print(f"Found {result['total']} papers:\n")

    for i, paper in enumerate(result['papers'], 1):
        print(f"{i}. {paper['title']}")
        print(f"   Paper ID: {paper['paper_key']}")
        print(f"   Categories: {paper['categories']}")
        print(f"   Authors: {paper['authors'][:80]}{'...' if len(paper['authors']) > 80 else ''}")
        print(f"   Abstract: {paper['abstract'][:150]}{'...' if len(paper['abstract']) > 150 else ''}")
        print(f"   Submitted: {paper['first_submitted_date']}")
        print(f"   Announced: {paper['first_announced_date']}")
        print()


def cmd_import(args):
    """Import paper"""
    config = load_config()
    url = f"{get_api_base(config)}/public/papers/import"

    params = {
        "arxiv_url": args.url
    }

    response = requests.post(url, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)

    result = response.json()
    print("Paper imported successfully!")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Paper ID: {result['paper']['paper_key']}")
    print(f"Title: {result['paper']['title']}")


def main():
    parser = argparse.ArgumentParser(
        description="arXiv Paper Reviews Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get today's paper list
  python paper_client.py list --date 2026-02-04 --categories cs.AI --limit 5

  # View paper details
  python paper_client.py show 4711d67c242a5ecba2751e6b

  # Get paper comments
  python paper_client.py comments 4711d67c242a5ecba2751e6b

  # Add comment
  python paper_client.py comment 4711d67c242a5ecba2751e6b "This paper is very valuable"

  # Search papers
  python paper_client.py search --query "transformer" --limit 10

  # Import paper
  python paper_client.py import --url "https://arxiv.org/abs/2602.09012"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # list command
    list_parser = subparsers.add_parser('list', help='Fetch paper list')
    list_parser.add_argument('--date', help='Filter by release date (YYYY-MM-DD)')
    list_parser.add_argument('--interest', help='Filter by interest (e.g., chosen)')
    list_parser.add_argument('--categories', help='Filter by category (e.g., cs.AI,cs.LG)')
    list_parser.add_argument('--limit', type=int, default=50, help='Limit returned items (1-100)')
    list_parser.add_argument('--offset', type=int, default=0, help='Offset')
    list_parser.set_defaults(func=cmd_list)

    # show command
    show_parser = subparsers.add_parser('show', help='Show paper details')
    show_parser.add_argument('paper_key', help='Paper unique identifier')
    show_parser.set_defaults(func=cmd_show)

    # comments command
    comments_parser = subparsers.add_parser('comments', help='Fetch paper comments list')
    comments_parser.add_argument('paper_key', help='Paper unique identifier')
    comments_parser.add_argument('--limit', type=int, default=50, help='Limit returned items (1-100)')
    comments_parser.add_argument('--offset', type=int, default=0, help='Offset')
    comments_parser.set_defaults(func=cmd_comments)

    # comment command
    comment_parser = subparsers.add_parser('comment', help='Add paper review')
    comment_parser.add_argument('paper_key', help='Paper unique identifier')
    comment_parser.add_argument('content', help='Comment content')
    comment_parser.add_argument('--author-name', help='Author name')
    comment_parser.set_defaults(func=cmd_comment)

    # search command
    search_parser = subparsers.add_parser('search', help='Search papers')
    search_parser.add_argument('--query', required=True, help='Search keywords')
    search_parser.add_argument('--limit', type=int, default=20, help='Limit returned items (1-50)')
    search_parser.set_defaults(func=cmd_search)

    # import command
    import_parser = subparsers.add_parser('import', help='Import paper')
    import_parser.add_argument('--url', required=True, help='arXiv paper link')
    import_parser.set_defaults(func=cmd_import)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
