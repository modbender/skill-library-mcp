#!/usr/bin/env python3
"""
libby-book-monitor - Track book availability on Libby/OverDrive libraries.

Search library catalogues, maintain a watchlist, and get notified
when books are added to your library's collection.

Uses the OverDrive Thunder API (no authentication required).
"""

__version__ = "1.0.0"

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# --- Configuration ---

DEFAULT_DATA_DIR = Path.home() / ".libby-book-monitor"
API_BASE = "https://thunder.api.overdrive.com/v2/libraries"
USER_AGENT = f"libby-book-monitor/{__version__}"
REQUEST_TIMEOUT = 10
RATE_LIMIT_SECONDS = 1


def get_data_dir(args_data_dir=None):
    """Resolve data directory from flag, env var, or default."""
    if args_data_dir:
        return Path(args_data_dir)
    env = os.environ.get("LIBBY_BOOK_MONITOR_DATA")
    if env:
        return Path(env)
    return DEFAULT_DATA_DIR


def get_watchlist_path(data_dir, profile=None):
    """Get watchlist file path for the given profile."""
    if profile:
        return data_dir / f"watchlist-{profile}.json"
    return data_dir / "watchlist.json"


def load_config(data_dir):
    """Load or create default configuration."""
    data_dir.mkdir(parents=True, exist_ok=True)
    config_path = data_dir / "config.json"

    if not config_path.exists():
        default_config = {
            "default_library": "telaviv",
            "libraries": {
                "telaviv": "Israel Digital",
            },
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        return default_config

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_watchlist(data_dir, profile=None):
    """Load watchlist for the given profile."""
    data_dir.mkdir(parents=True, exist_ok=True)
    path = get_watchlist_path(data_dir, profile)
    if not path.exists():
        return {"books": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_watchlist(data_dir, watchlist, profile=None):
    """Save watchlist for the given profile."""
    data_dir.mkdir(parents=True, exist_ok=True)
    path = get_watchlist_path(data_dir, profile)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(watchlist, f, indent=2, ensure_ascii=False)


# --- API ---


def search_library(library_code, query):
    """Search a library catalogue via the Thunder API.

    Returns the parsed JSON response, or None on error.
    """
    encoded_query = urllib.parse.quote(query, safe="")
    url = f"{API_BASE}/{library_code}/media?query={encoded_query}"

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"Error: HTTP {e.code} - {e.reason}", file=sys.stderr)
    except urllib.error.URLError as e:
        print(f"Error: {e.reason}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    return None


def title_matches(search_title, result_title):
    """Case-insensitive substring match in either direction.

    Good enough for matching catalogue results to watchlist entries.
    May false-positive on very short titles.
    """
    a = search_title.lower().strip()
    b = result_title.lower().strip()
    return a in b or b in a


# --- Commands ---


def cmd_search(args, data_dir):
    """Search for a book in a library catalogue."""
    library_code = args.library_code
    query = args.query

    print(f'Searching "{query}" in {library_code}...\n')

    data = search_library(library_code, query)
    if data is None:
        return 1

    total = data.get("totalItems", 0)
    items = data.get("items", [])

    if total == 0:
        print("No results found.")
        return 0

    for idx, item in enumerate(items, 1):
        title = item.get("title", "Unknown")
        author = item.get("firstCreatorName", "Unknown")
        is_owned = item.get("isOwned", False)
        owned_copies = item.get("ownedCopies", 0)
        is_available = item.get("isAvailable", False)
        available_copies = item.get("availableCopies", 0)

        status = "In catalogue" if is_owned else "Not owned"
        avail = f"Yes ({available_copies})" if is_available else "No"

        print(f"  {idx}. {title} - {author}")
        print(f"     {status} | Copies: {owned_copies} | Available: {avail}")
        print()

    print(f"{total} result(s) total")
    return 0


def cmd_watch(args, data_dir):
    """Add a book to the watchlist."""
    config = load_config(data_dir)
    watchlist = load_watchlist(data_dir, args.profile)

    library = args.library or config.get("default_library", "telaviv")
    title = args.title
    author = args.author or ""

    for book in watchlist["books"]:
        if book["title"].lower() == title.lower():
            print(f"Already watching: {title}")
            return 0

    watchlist["books"].append(
        {
            "title": title,
            "author": author,
            "library": library,
            "added": datetime.now().strftime("%Y-%m-%d"),
            "last_status": "not_found",
            "last_checked": None,
            "found_date": None,
        }
    )
    save_watchlist(data_dir, watchlist, args.profile)

    print(f"Added to watchlist: {title}")
    if author:
        print(f"  Author: {author}")
    print(f"  Library: {library}")
    return 0


def cmd_unwatch(args, data_dir):
    """Remove a book from the watchlist."""
    watchlist = load_watchlist(data_dir, args.profile)
    title = args.title

    before = len(watchlist["books"])
    watchlist["books"] = [
        b for b in watchlist["books"] if b["title"].lower() != title.lower()
    ]

    if len(watchlist["books"]) < before:
        save_watchlist(data_dir, watchlist, args.profile)
        print(f"Removed: {title}")
        return 0

    print(f"Not found in watchlist: {title}")
    return 1


def cmd_list(args, data_dir):
    """Show all books in the watchlist."""
    watchlist = load_watchlist(data_dir, args.profile)

    if not watchlist["books"]:
        print("Watchlist is empty.")
        return 0

    count = len(watchlist["books"])
    label = f"Watchlist ({count} book{'s' if count != 1 else ''}):"
    if args.profile:
        label = f"Watchlist [{args.profile}] ({count} book{'s' if count != 1 else ''}):"
    print(label)
    print()

    for idx, book in enumerate(watchlist["books"], 1):
        title = book["title"]
        author = book.get("author", "")
        library = book["library"]
        status = book["last_status"]
        last_checked = book.get("last_checked", "never")
        found_date = book.get("found_date")

        marker = "*" if status == "found" else " "
        print(f"  {marker} {idx}. {title}")
        if author:
            print(f"       Author: {author}")
        print(f"       Library: {library} | Status: {status} | Checked: {last_checked}")
        if found_date:
            print(f"       Found on: {found_date}")
        print()

    return 0


def cmd_check(args, data_dir):
    """Check all watchlist items against the API."""
    watchlist = load_watchlist(data_dir, args.profile)
    notify_only = args.notify

    if not watchlist["books"]:
        if not notify_only:
            print("Watchlist is empty.")
        return 0

    new_finds = []
    total = len(watchlist["books"])

    for idx, book in enumerate(watchlist["books"]):
        title = book["title"]
        author = book.get("author", "")
        library = book["library"]
        prev_status = book["last_status"]

        query = f"{title} {author}".strip()
        data = search_library(library, query)

        if data is None:
            continue

        found = False
        matched_item = None
        for item in data.get("items", []):
            if title_matches(title, item.get("title", "")) and item.get(
                "isOwned", False
            ):
                found = True
                matched_item = item
                break

        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        book["last_checked"] = now

        if found and prev_status == "not_found":
            book["last_status"] = "found"
            book["found_date"] = datetime.now().strftime("%Y-%m-%d")
            new_finds.append((book, matched_item))
        elif found:
            book["last_status"] = "found"
        else:
            book["last_status"] = "not_found"

        if idx < total - 1:
            time.sleep(RATE_LIMIT_SECONDS)

    save_watchlist(data_dir, watchlist, args.profile)

    # Output
    if notify_only:
        if new_finds:
            print("New on Libby:\n")
            for book, item in new_finds:
                t = item.get("title", book["title"]) if item else book["title"]
                a = (
                    item.get("firstCreatorName", book.get("author", ""))
                    if item
                    else book.get("author", "")
                )
                copies = item.get("ownedCopies", 0) if item else "?"
                avail = "Yes" if (item and item.get("isAvailable")) else "No"
                print(f"  {t} - {a}")
                print(f"    Library: {book['library']} | Copies: {copies} | Available: {avail}")
                print()
        # Exit silently if nothing new (useful for cron)
    else:
        print(f"Checked {total} book(s).")
        if new_finds:
            print(f"{len(new_finds)} new addition(s) found!")

    # Remind about found books
    found_books = [b for b in watchlist["books"] if b["last_status"] == "found"]
    if found_books:
        print(f"\n{len(found_books)} book(s) already in catalogue:")
        for b in found_books:
            print(f"  - {b['title']}")
        print("Consider removing them with 'unwatch'.")

    return 0


# --- CLI ---


def main():
    parser = argparse.ArgumentParser(
        prog="libby-book-monitor",
        description="Track book availability on Libby/OverDrive libraries.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("--profile", help="User profile for separate watchlists")
    parser.add_argument(
        "--data-dir",
        help=f"Data directory (default: {DEFAULT_DATA_DIR}, or $LIBBY_BOOK_MONITOR_DATA)",
    )

    subparsers = parser.add_subparsers(dest="command")

    # search
    sp = subparsers.add_parser("search", help="Search a library catalogue")
    sp.add_argument("library_code", help="Library code (e.g. telaviv, nypl, lapl)")
    sp.add_argument("query", help="Search query (title, author, etc.)")

    # watch
    sp = subparsers.add_parser("watch", help="Add a book to the watchlist")
    sp.add_argument("title", help="Book title")
    sp.add_argument("--author", help="Book author")
    sp.add_argument("--library", help="Library code (default: from config)")

    # unwatch
    sp = subparsers.add_parser("unwatch", help="Remove a book from the watchlist")
    sp.add_argument("title", help="Book title")

    # list
    subparsers.add_parser("list", help="Show the watchlist")

    # check
    sp = subparsers.add_parser("check", help="Check all watchlist books against API")
    sp.add_argument(
        "--notify",
        action="store_true",
        help="Only print newly found books (for cron/automation)",
    )

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    data_dir = get_data_dir(args.data_dir)
    return {
        "search": cmd_search,
        "watch": cmd_watch,
        "unwatch": cmd_unwatch,
        "list": cmd_list,
        "check": cmd_check,
    }[args.command](args, data_dir)


if __name__ == "__main__":
    sys.exit(main())
