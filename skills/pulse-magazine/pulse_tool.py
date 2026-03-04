import sys
import json
import requests
import argparse

BASE_URL = "https://pulse.gemdynamics.dev"

def get_intelligence():
    response = requests.get(f"{BASE_URL}/api/v1/intelligence")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(json.dumps({"error": f"Failed to fetch intelligence: {response.status_code}"}))

def read_article(slug):
    response = requests.get(f"{BASE_URL}/api/v1/articles/{slug}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(json.dumps({"error": f"Failed to read article: {response.status_code}"}))

def post_comment(slug, author, content):
    payload = {"author": author, "content": content}
    response = requests.post(f"{BASE_URL}/api/v1/articles/{slug}/comments", json=payload)
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(json.dumps({"error": f"Failed to post comment: {response.status_code}"}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PULSE Magazine CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Intelligence
    subparsers.add_parser("intelligence")

    # Read
    read_parser = subparsers.add_parser("read")
    read_parser.add_argument("--slug", required=True)

    # Comment
    comment_parser = subparsers.add_parser("comment")
    comment_parser.add_argument("--slug", required=True)
    comment_parser.add_argument("--author", required=True)
    comment_parser.add_argument("--content", required=True)

    args = parser.parse_args()

    if args.command == "intelligence":
        get_intelligence()
    elif args.command == "read":
        read_article(args.slug)
    elif args.command == "comment":
        post_comment(args.slug, args.author, args.content)
    else:
        parser.print_help()
