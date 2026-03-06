#!/usr/bin/env python3
"""
BigCommerce Content Optimizer — Helper Script

Handles all BigCommerce API communication:
  - init:   Discover total products and create progress tracker
  - fetch:  Fetch one page of products
  - update: Push updated titles/descriptions back to BigCommerce
  - report: Generate a summary report of all work done

Usage:
  python bc_optimizer.py init   --store-hash HASH --token TOKEN [--limit 10]
  python bc_optimizer.py fetch  --store-hash HASH --token TOKEN --page N [--limit 10]
  python bc_optimizer.py update --store-hash HASH --token TOKEN --updates-file FILE
  python bc_optimizer.py report
"""

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("ERROR: 'requests' is required. Install with: pip install requests --break-system-packages")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL = "https://api.bigcommerce.com/stores/{store_hash}/v3"
PROGRESS_FILE = "progress.json"
RATE_LIMIT_PAUSE = 3          # seconds to wait when rate-limited
MAX_RETRIES = 5               # max retries per request on rate limit / transient error
REQUEST_TIMEOUT = 30           # seconds


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def headers(token: str) -> dict:
    return {
        "X-Auth-Token": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def api_get(store_hash: str, token: str, endpoint: str, params: dict = None):
    """GET with automatic rate-limit retry."""
    url = BASE_URL.format(store_hash=store_hash) + endpoint
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=headers(token), params=params, timeout=REQUEST_TIMEOUT)
            if r.status_code == 429:
                retry_after = int(r.headers.get("X-Rate-Limit-Time-Reset-Ms", RATE_LIMIT_PAUSE * 1000)) / 1000
                print(f"  ⏳ Rate limited. Waiting {retry_after:.1f}s (attempt {attempt}/{MAX_RETRIES})...")
                time.sleep(retry_after)
                continue
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES:
                raise
            print(f"  ⚠️  Request error (attempt {attempt}/{MAX_RETRIES}): {e}")
            time.sleep(RATE_LIMIT_PAUSE)
    return None


def api_put(store_hash: str, token: str, endpoint: str, payload: dict):
    """PUT with automatic rate-limit retry."""
    url = BASE_URL.format(store_hash=store_hash) + endpoint
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.put(url, headers=headers(token), json=payload, timeout=REQUEST_TIMEOUT)
            if r.status_code == 429:
                retry_after = int(r.headers.get("X-Rate-Limit-Time-Reset-Ms", RATE_LIMIT_PAUSE * 1000)) / 1000
                print(f"  ⏳ Rate limited. Waiting {retry_after:.1f}s (attempt {attempt}/{MAX_RETRIES})...")
                time.sleep(retry_after)
                continue
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES:
                raise
            print(f"  ⚠️  Request error (attempt {attempt}/{MAX_RETRIES}): {e}")
            time.sleep(RATE_LIMIT_PAUSE)
    return None


def load_progress() -> dict:
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_progress(data: dict):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(args):
    """Discover the store and create progress tracker."""
    print(f"🔍 Connecting to BigCommerce store: {args.store_hash}")

    # Fetch page 1 just to get the pagination metadata
    result = api_get(args.store_hash, args.token, "/catalog/products", params={"limit": 1, "page": 1})
    if not result:
        print("❌ Failed to connect to BigCommerce API. Check your store hash and token.")
        sys.exit(1)

    meta = result.get("meta", {}).get("pagination", {})
    total = meta.get("total", 0)
    total_pages = math.ceil(total / args.limit) if total > 0 else 0

    print(f"✅ Connected successfully!")
    print(f"   Total products: {total}")
    print(f"   Pages ({args.limit}/page): {total_pages}")

    # Check for existing progress
    progress = load_progress()
    if progress and progress.get("status") == "in_progress":
        print(f"\n📋 Existing progress found!")
        print(f"   Pages completed: {len(progress.get('pages_completed', []))}/{progress.get('total_pages', '?')}")
        print(f"   Products updated: {len(progress.get('products_updated', []))}")
        print(f"   Resuming from page: {progress.get('current_page', 1)}")
    else:
        progress = {
            "store_hash": args.store_hash,
            "total_products": total,
            "total_pages": total_pages,
            "products_per_page": args.limit,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "pages_completed": [],
            "products_updated": [],
            "products_failed": [],
            "current_page": 1,
            "status": "in_progress",
        }
        save_progress(progress)
        print(f"\n📋 Progress tracker created: {PROGRESS_FILE}")

    # Output as JSON for Claude to parse
    print("\n--- JSON OUTPUT ---")
    print(json.dumps({
        "total_products": total,
        "total_pages": total_pages,
        "products_per_page": args.limit,
        "current_page": progress.get("current_page", 1),
        "pages_completed": progress.get("pages_completed", []),
        "status": progress.get("status", "in_progress"),
    }, indent=2))


def cmd_fetch(args):
    """Fetch one page of products."""
    print(f"📦 Fetching page {args.page} (limit {args.limit})...")

    result = api_get(
        args.store_hash, args.token, "/catalog/products",
        params={
            "limit": args.limit,
            "page": args.page,
            "include": "images",
        }
    )

    if not result or "data" not in result:
        print("❌ Failed to fetch products.")
        sys.exit(1)

    products = result["data"]
    print(f"✅ Fetched {len(products)} products")

    # Extract relevant fields
    simplified = []
    for p in products:
        images = p.get("images", [])
        thumbnail = images[0]["url_thumbnail"] if images else None
        simplified.append({
            "id": p["id"],
            "name": p.get("name", ""),
            "description": p.get("description", ""),
            "sku": p.get("sku", ""),
            "price": p.get("price", 0),
            "categories": p.get("categories", []),
            "brand_id": p.get("brand_id"),
            "type": p.get("type", ""),
            "availability": p.get("availability", ""),
            "condition": p.get("condition", ""),
            "thumbnail": thumbnail,
            "page_title": p.get("page_title", ""),
            "meta_description": p.get("meta_description", ""),
            "search_keywords": p.get("search_keywords", ""),
        })

    outfile = f"page_{args.page}_products.json"
    with open(outfile, "w") as f:
        json.dump(simplified, f, indent=2)

    print(f"💾 Saved to {outfile}")

    # Print summary for Claude
    print("\n--- PRODUCTS SUMMARY ---")
    for p in simplified:
        desc_preview = (p["description"][:80] + "...") if len(p.get("description", "")) > 80 else p.get("description", "(empty)")
        print(f"  [{p['id']}] {p['name']}")
        print(f"       SKU: {p['sku']} | Price: ${p['price']} | Desc: {desc_preview}")

    # Also output full JSON for Claude to read
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(simplified, indent=2))


def cmd_update(args):
    """Push updates back to BigCommerce."""
    if not os.path.exists(args.updates_file):
        print(f"❌ Updates file not found: {args.updates_file}")
        sys.exit(1)

    with open(args.updates_file, "r") as f:
        updates = json.load(f)

    print(f"🚀 Updating {len(updates)} products...")

    progress = load_progress()
    success_count = 0
    fail_count = 0

    for product in updates:
        pid = product["id"]
        payload = {}
        if "name" in product:
            payload["name"] = product["name"]
        if "description" in product:
            payload["description"] = product["description"]
        if "page_title" in product:
            payload["page_title"] = product["page_title"]
        if "meta_description" in product:
            payload["meta_description"] = product["meta_description"]

        try:
            result = api_put(args.store_hash, args.token, f"/catalog/products/{pid}", payload)
            if result:
                print(f"  ✅ [{pid}] {product.get('name', 'Unknown')}")
                success_count += 1
                progress.setdefault("products_updated", []).append({
                    "id": pid,
                    "name": product.get("name", ""),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                })
            else:
                print(f"  ❌ [{pid}] Update returned None")
                fail_count += 1
                progress.setdefault("products_failed", []).append({
                    "id": pid,
                    "error": "API returned None",
                    "at": datetime.now(timezone.utc).isoformat(),
                })
        except Exception as e:
            print(f"  ❌ [{pid}] Error: {e}")
            fail_count += 1
            progress.setdefault("products_failed", []).append({
                "id": pid,
                "error": str(e),
                "at": datetime.now(timezone.utc).isoformat(),
            })

        # Small delay between updates to be kind to the API
        time.sleep(0.3)

    # Update progress
    # Figure out which page this was from the filename
    page_num = None
    basename = os.path.basename(args.updates_file)
    if basename.startswith("page_") and "_updates" in basename:
        try:
            page_num = int(basename.split("_")[1])
        except (ValueError, IndexError):
            pass

    if page_num is not None:
        if page_num not in progress.get("pages_completed", []):
            progress.setdefault("pages_completed", []).append(page_num)
        progress["current_page"] = page_num + 1

    # Check if we're done
    if len(progress.get("pages_completed", [])) >= progress.get("total_pages", 0):
        progress["status"] = "completed"
        progress["completed_at"] = datetime.now(timezone.utc).isoformat()

    save_progress(progress)

    print(f"\n📊 Page update complete: {success_count} success, {fail_count} failed")
    print(f"   Overall progress: {len(progress.get('pages_completed', []))}/{progress.get('total_pages', '?')} pages")

    # JSON output
    print("\n--- JSON OUTPUT ---")
    print(json.dumps({
        "success": success_count,
        "failed": fail_count,
        "pages_completed": len(progress.get("pages_completed", [])),
        "total_pages": progress.get("total_pages", 0),
        "status": progress.get("status", "in_progress"),
        "next_page": progress.get("current_page", 1),
    }, indent=2))


def cmd_report(args):
    """Generate a summary report."""
    progress = load_progress()
    if not progress:
        print("❌ No progress file found. Run 'init' first.")
        sys.exit(1)

    total_updated = len(progress.get("products_updated", []))
    total_failed = len(progress.get("products_failed", []))
    pages_done = len(progress.get("pages_completed", []))
    total_pages = progress.get("total_pages", 0)

    print("=" * 60)
    print("  BigCommerce Content Optimizer — Final Report")
    print("=" * 60)
    print(f"  Store Hash:        {progress.get('store_hash', 'N/A')}")
    print(f"  Status:            {progress.get('status', 'unknown')}")
    print(f"  Started:           {progress.get('started_at', 'N/A')}")
    print(f"  Completed:         {progress.get('completed_at', 'N/A')}")
    print(f"  Total Products:    {progress.get('total_products', 0)}")
    print(f"  Pages Processed:   {pages_done}/{total_pages}")
    print(f"  Products Updated:  {total_updated}")
    print(f"  Products Failed:   {total_failed}")
    print(f"  Success Rate:      {(total_updated/(total_updated+total_failed)*100):.1f}%" if (total_updated + total_failed) > 0 else "  Success Rate:      N/A")
    print("=" * 60)

    if progress.get("products_failed"):
        print("\n⚠️  Failed Products:")
        for item in progress["products_failed"]:
            print(f"  - ID {item['id']}: {item.get('error', 'Unknown error')}")

    # JSON output
    print("\n--- JSON OUTPUT ---")
    print(json.dumps({
        "status": progress.get("status"),
        "total_products": progress.get("total_products", 0),
        "pages_processed": pages_done,
        "total_pages": total_pages,
        "products_updated": total_updated,
        "products_failed": total_failed,
        "failed_ids": [f["id"] for f in progress.get("products_failed", [])],
    }, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="BigCommerce Content Optimizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialize and discover products")
    p_init.add_argument("--store-hash", required=True, help="BigCommerce store hash")
    p_init.add_argument("--token", required=True, help="BigCommerce API token")
    p_init.add_argument("--limit", type=int, default=10, help="Products per page (default: 10)")

    # fetch
    p_fetch = subparsers.add_parser("fetch", help="Fetch one page of products")
    p_fetch.add_argument("--store-hash", required=True, help="BigCommerce store hash")
    p_fetch.add_argument("--token", required=True, help="BigCommerce API token")
    p_fetch.add_argument("--page", type=int, required=True, help="Page number to fetch")
    p_fetch.add_argument("--limit", type=int, default=10, help="Products per page (default: 10)")

    # update
    p_update = subparsers.add_parser("update", help="Push updates to BigCommerce")
    p_update.add_argument("--store-hash", required=True, help="BigCommerce store hash")
    p_update.add_argument("--token", required=True, help="BigCommerce API token")
    p_update.add_argument("--updates-file", required=True, help="JSON file with product updates")

    # report
    subparsers.add_parser("report", help="Generate summary report")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "fetch":
        cmd_fetch(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "report":
        cmd_report(args)


if __name__ == "__main__":
    main()
