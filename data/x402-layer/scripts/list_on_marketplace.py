#!/usr/bin/env python3
"""
x402 Marketplace Listing Management

List, update, or unlist your endpoint on the x402 marketplace.

Usage:
    # List/Update endpoint on marketplace
    python list_on_marketplace.py my-api --category ai --description "AI analysis"

    # Update with images
    python list_on_marketplace.py my-api --category ai --description "AI analysis" \\
        --logo https://example.com/logo.png --banner https://example.com/banner.jpg

    # Unlist from marketplace
    python list_on_marketplace.py my-api --unlist

Categories: ai, data, finance, utility, social, gaming

Environment Variables:
    X_API_KEY - Your endpoint API key (required)
"""

import os
import sys
import json
import argparse
import requests

API_BASE = "https://api.x402layer.cc"

def load_api_key(args_key=None):
    """Load API Key from argument or environment."""
    if args_key:
        return args_key
    
    api_key = os.getenv("X_API_KEY")
    if not api_key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("X_API_KEY")
        except ImportError:
            pass

    if not api_key:
        print("Error: content of X_API_KEY environment variable or --api-key argument needed")
        print("You received this key when you created your endpoint.")
        sys.exit(1)
    return api_key

def list_endpoint(slug: str, api_key: str, category: str = None, description: str = None,
                  logo_url: str = None, banner_url: str = None, tags: list = None) -> dict:
    """
    List or update an endpoint on the marketplace.
    """
    url = f"{API_BASE}/api/marketplace/list"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    data = {"slug": slug}

    if category:
        data["category"] = category
    if description:
        data["description"] = description
    if logo_url:
        data["logo_url"] = logo_url
    if banner_url:
        data["banner_url"] = banner_url
    if tags:
        data["tags"] = tags

    action = "Updating" if category or description else "Listing"
    print(f"{action} endpoint: {slug}")
    if category:
        print(f"  Category: {category}")
    if description:
        print(f"  Description: {description[:50]}{'...' if len(description) > 50 else ''}")
    if logo_url:
        print(f"  Logo: {logo_url}")
    if banner_url:
        print(f"  Banner: {banner_url}")

    response = requests.post(url, json=data, headers=headers)

    if response.status_code in [200, 201]:
        result = response.json()
        if result.get("success"):
            print(f"\\n✅ Endpoint '{slug}' is now listed on marketplace!")
        else:
            print(f"\\n⚠️ {result.get('message', 'Operation completed')}")
        return result
    else:
        print(f"\\n❌ Error: {response.status_code} - {response.text}")
        return {"error": response.text}

def unlist_endpoint(slug: str, api_key: str) -> dict:
    """Remove an endpoint from the marketplace."""
    url = f"{API_BASE}/api/marketplace/unlist"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {"slug": slug}

    print(f"Unlisting endpoint: {slug} from marketplace...")

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"\\n✅ Endpoint '{slug}' removed from marketplace")
        return result
    else:
        print(f"\\n❌ Error: {response.status_code} - {response.text}")
        return {"error": response.text}

def main():
    parser = argparse.ArgumentParser(
        description="Manage x402 marketplace listing for your endpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List on marketplace (uses X_API_KEY env var)
  python list_on_marketplace.py my-api --category ai --description "My AI API"

  # Pass API key explicitly
  python list_on_marketplace.py my-api --api-key "x402_..." --unlist
        """
    )

    parser.add_argument("slug", help="Endpoint slug")
    parser.add_argument("--api-key", help="Endpoint API Key (or set X_API_KEY env)")
    parser.add_argument("--category", choices=["ai", "data", "finance", "utility", "social", "gaming"],
                        help="Marketplace category")
    parser.add_argument("--description", help="Public description")
    parser.add_argument("--logo", help="Logo image URL")
    parser.add_argument("--banner", help="Banner image URL")
    parser.add_argument("--tags", nargs="+", help="Optional tags")
    parser.add_argument("--unlist", action="store_true", help="Remove from marketplace")

    args = parser.parse_args()
    
    api_key = load_api_key(args.api_key)

    if args.unlist:
        result = unlist_endpoint(args.slug, api_key)
    else:
        # At least category or description should be provided for listing
        if not args.category and not args.description and not args.logo and not args.banner:
            print("Error: At least one of --category, --description, --logo, or --banner is required")
            print("Use --help for usage information")
            sys.exit(1)
        result = list_endpoint(
            args.slug,
            api_key,
            category=args.category,
            description=args.description,
            logo_url=args.logo,
            banner_url=args.banner,
            tags=args.tags
        )

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
