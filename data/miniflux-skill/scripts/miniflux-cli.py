#!/usr/bin/env python3
# Miniflux API Client
# Modern minimalist feed reader management

import sys
import json
import os
import argparse
from datetime import datetime
from urllib.parse import urlencode

try:
    import miniflux
except ImportError:
    print("Error: miniflux package not installed.", file=sys.stderr)
    print("Install with: uv pip install miniflux", file=sys.stderr)
    sys.exit(1)


def get_client():
    """Create and return a Miniflux client instance."""
    url = os.environ.get('MINIFLUX_URL')
    token = os.environ.get('MINIFLUX_TOKEN')

    if not url or not token:
        print("Error: MINIFLUX_URL and MINIFLUX_TOKEN environment variables must be set.", file=sys.stderr)
        sys.exit(1)

    return miniflux.Client(url, api_key=token)


def format_entry(entry, full_content=False):
    """Format an entry for display."""
    status_icon = "📖" if entry.get('status') == 'unread' else "✅"
    star_icon = "⭐" if entry.get('starred') else ""

    output = f"\n{status_icon} {entry.get('title', 'No title')}"
    if star_icon:
        output += f" {star_icon}"

    output += f"\n   URL: {entry.get('url', 'N/A')}"

    if entry.get('feed'):
        feed_title = entry.get('feed', {}).get('title', 'Unknown feed')
        output += f"\n   Feed: {feed_title}"

    if entry.get('published_at'):
        pub_date = datetime.fromisoformat(entry['published_at'].replace('Z', '+00:00'))
        output += f"\n   Published: {pub_date.strftime('%Y-%m-%d %H:%M')}"

    if entry.get('reading_time'):
        output += f"\n   Reading time: {entry.get('reading_time')} min"

    if full_content and entry.get('content'):
        # Strip HTML tags for cleaner output
        import re
        content = re.sub(r'<[^>]+>', '', entry['content'])
        content = re.sub(r'\s+', ' ', content).strip()
        if len(content) > 500:
            content = content[:500] + "..."
        output += f"\n   Content: {content}"

    output += f"\n   ID: {entry.get('id')}"

    return output


def cmd_feeds(args):
    """List all feeds."""
    client = get_client()
    feeds = client.get_feeds()

    print(f"\n📰 {len(feeds)} feeds found:\n")

    for feed in feeds:
        print(f"  [{feed['id']}] {feed['title']}")
        print(f"      URL: {feed['site_url']}")
        if feed.get('category'):
            print(f"      Category: {feed['category']['title']} (ID: {feed['category']['id']})")
        if feed.get('parsing_error_message'):
            print(f"      ⚠️  Error: {feed['parsing_error_message']}")
        print()

    return 0


def cmd_categories(args):
    """List all categories."""
    client = get_client()
    categories = client.get_categories()

    print(f"\n📁 {len(categories)} categories:\n")

    for cat in categories:
        print(f"  [{cat['id']}] {cat['title']}")
        if 'feed_count' in cat:
            print(f"      Feeds: {cat['feed_count']}")
        if 'total_unread' in cat:
            print(f"      Unread: {cat['total_unread']}")
        print()

    return 0


def cmd_entries(args):
    """List entries with filters."""
    client = get_client()

    # Build filters
    filters = {}
    if args.status:
        filters['status'] = args.status
    if args.limit:
        filters['limit'] = args.limit
    if args.offset:
        filters['offset'] = args.offset
    if args.direction:
        filters['direction'] = args.direction
    if args.search:
        filters['search'] = args.search
    if args.starred is not None:
        filters['starred'] = args.starred
    if args.before:
        filters['before'] = args.before
    if args.after:
        filters['after'] = args.after

    # Get entries
    if args.feed_id:
        result = client.get_feed_entries(args.feed_id, **filters)
    elif args.category_id:
        result = client.get_category_entries(args.category_id, **filters)
    else:
        result = client.get_entries(**filters)

    total = result.get('total', 0)
    entries = result.get('entries', [])

    print(f"\n📚 {total} entries found (showing {len(entries)})\n")

    for entry in entries:
        print(format_entry(entry, full_content=args.full_content))

    return 0


def cmd_entry(args):
    """Get a specific entry."""
    client = get_client()
    entry = client.get_entry(args.entry_id)

    print(format_entry(entry, full_content=True))

    if entry.get('content'):
        print(f"\n📝 Full Content:\n{entry['content']}")

    return 0


def cmd_create_feed(args):
    """Create a new feed."""
    client = get_client()

    feed_data = {
        'feed_url': args.url
    }

    if args.category:
        feed_data['category_id'] = args.category
    if args.crawler:
        feed_data['crawler'] = True
    if args.user_agent:
        feed_data['user_agent'] = args.user_agent

    feed_id = client.create_feed(**feed_data)
    print(f"\n✅ Feed created successfully! Feed ID: {feed_id}")

    return 0


def cmd_update_feed(args):
    """Update an existing feed."""
    client = get_client()

    update_data = {}
    if args.title:
        update_data['title'] = args.title
    if args.category:
        update_data['category_id'] = args.category
    if args.url:
        update_data['feed_url'] = args.url
    if args.site_url:
        update_data['site_url'] = args.site_url
    if args.crawler is not None:
        update_data['crawler'] = args.crawler
    if args.user_agent:
        update_data['user_agent'] = args.user_agent

    if not update_data:
        print("Error: No update fields provided.", file=sys.stderr)
        return 1

    client.update_feed(args.feed_id, **update_data)
    print(f"\n✅ Feed {args.feed_id} updated successfully!")

    return 0


def cmd_delete_feed(args):
    """Delete a feed."""
    client = get_client()
    client.delete_feed(args.feed_id)
    print(f"\n✅ Feed {args.feed_id} deleted successfully!")

    return 0


def cmd_refresh_all(args):
    """Refresh all feeds."""
    client = get_client()
    client.refresh_feeds()
    print("\n✅ All feeds refresh started (runs in background)")

    return 0


def cmd_refresh_feed(args):
    """Refresh a specific feed."""
    client = get_client()
    client.refresh_feed(args.feed_id)
    print(f"\n✅ Feed {args.feed_id} refresh started")

    return 0


def cmd_mark_read(args):
    """Mark entries as read."""
    client = get_client()

    entry_ids = [int(eid) for eid in args.entry_ids.split(',')]
    client.update_entries(entry_ids, status='read')

    print(f"\n✅ Marked {len(entry_ids)} entries as read")

    return 0


def cmd_mark_unread(args):
    """Mark entries as unread."""
    client = get_client()

    entry_ids = [int(eid) for eid in args.entry_ids.split(',')]
    client.update_entries(entry_ids, status='unread')

    print(f"\n✅ Marked {len(entry_ids)} entries as unread")

    return 0


def cmd_mark_feed_read(args):
    """Mark all entries of a feed as read."""
    client = get_client()

    # Miniflux doesn't have a direct method for this in the Python client
    # We need to get all entries and mark them as read
    result = client.get_feed_entries(args.feed_id, status='unread')
    entry_ids = [e['id'] for e in result.get('entries', [])]

    if entry_ids:
        client.update_entries(entry_ids, status='read')
        print(f"\n✅ Marked {len(entry_ids)} entries as read in feed {args.feed_id}")
    else:
        print(f"\n✅ No unread entries in feed {args.feed_id}")

    return 0


def cmd_discover(args):
    """Discover subscriptions from a URL."""
    client = get_client()
    subscriptions = client.discover(args.url)

    print(f"\n🔍 Discovered {len(subscriptions)} feed(s) from {args.url}:\n")

    for sub in subscriptions:
        print(f"  Type: {sub.get('type', 'unknown')}")
        print(f"  Title: {sub.get('title', 'N/A')}")
        print(f"  URL: {sub.get('url', 'N/A')}")
        print()

    return 0


def cmd_counters(args):
    """Get unread/read counters per feed."""
    client = get_client()
    feeds = client.get_feeds()
    counters = client.get_feed_counters()

    reads = counters.get('reads', {})
    unreads = counters.get('unreads', {})

    print(f"\n📊 Feed counters:\n")

    total_unread = 0
    total_read = 0

    for feed in feeds:
        feed_id = str(feed['id'])
        unread_count = unreads.get(feed_id, 0)
        read_count = reads.get(feed_id, 0)

        print(f"  [{feed['id']}] {feed['title']}")
        print(f"      📖 Unread: {unread_count}")
        print(f"      ✅ Read: {read_count}")
        print()

        total_unread += unread_count
        total_read += read_count

    print(f"  Total: 📖 {total_unread} unread, ✅ {total_read} read\n")

    return 0


def cmd_me(args):
    """Get current user info."""
    client = get_client()
    user = client.me()

    print(f"\n👤 Current User Info:\n")
    print(f"  Username: {user.get('username', 'N/A')}")
    print(f"  ID: {user.get('id', 'N/A')}")
    print(f"  Admin: {user.get('is_admin', False)}")
    print(f"  Theme: {user.get('theme', 'N/A')}")
    print(f"  Language: {user.get('language', 'N/A')}")
    print(f"  Timezone: {user.get('timezone', 'N/A')}")
    print(f"  Entries per page: {user.get('entries_per_page', 'N/A')}")
    print(f"  Last login: {user.get('last_login_at', 'Never')}\n")

    return 0


def cmd_create_category(args):
    """Create a new category."""
    client = get_client()
    category = client.create_category(args.title)

    print(f"\n✅ Category created! ID: {category['id']}, Title: {category['title']}\n")

    return 0


def cmd_toggle_bookmark(args):
    """Toggle bookmark/star status of an entry."""
    client = get_client()
    is_starred = client.toggle_bookmark(args.entry_id)

    status = "⭐ starred" if is_starred else "○ unstarred"
    print(f"\n✅ Entry {args.entry_id} {status}\n")

    return 0


def cmd_delete_category(args):
    """Delete a category."""
    client = get_client()
    client.delete_category(args.category_id)

    print(f"\n✅ Category {args.category_id} deleted successfully!\n")

    return 0


def main():
    parser = argparse.ArgumentParser(description='Miniflux CLI - Feed Reader Management')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Feeds
    subparsers.add_parser('feeds', help='List all feeds').set_defaults(func=cmd_feeds)

    # Categories
    subparsers.add_parser('categories', help='List all categories').set_defaults(func=cmd_categories)

    # Entries
    entries_parser = subparsers.add_parser('entries', help='List entries with filters')
    entries_parser.add_argument('--status', choices=['unread', 'read', 'removed'], help='Filter by status')
    entries_parser.add_argument('--limit', type=int, default=100, help='Number of entries to return')
    entries_parser.add_argument('--offset', type=int, help='Number of entries to skip')
    entries_parser.add_argument('--direction', choices=['asc', 'desc'], help='Sort direction')
    entries_parser.add_argument('--search', help='Search query')
    entries_parser.add_argument('--category-id', type=int, help='Filter by category ID')
    entries_parser.add_argument('--feed-id', type=int, help='Filter by feed ID')
    entries_parser.add_argument('--starred', type=bool, help='Filter starred entries')
    entries_parser.add_argument('--before', type=int, help='Entries before Unix timestamp')
    entries_parser.add_argument('--after', type=int, help='Entries after Unix timestamp')
    entries_parser.add_argument('--full-content', action='store_true', help='Show full content')
    entries_parser.set_defaults(func=cmd_entries)

    # Entry
    entry_parser = subparsers.add_parser('entry', help='Get a specific entry')
    entry_parser.add_argument('--entry-id', type=int, required=True, help='Entry ID')
    entry_parser.set_defaults(func=cmd_entry)

    # Create feed
    create_feed_parser = subparsers.add_parser('create-feed', help='Create a new feed')
    create_feed_parser.add_argument('--url', required=True, help='Feed URL')
    create_feed_parser.add_argument('--category', type=int, help='Category ID')
    create_feed_parser.add_argument('--crawler', action='store_true', help='Enable crawler')
    create_feed_parser.add_argument('--user-agent', help='Custom user agent')
    create_feed_parser.set_defaults(func=cmd_create_feed)

    # Update feed
    update_feed_parser = subparsers.add_parser('update-feed', help='Update a feed')
    update_feed_parser.add_argument('--feed-id', type=int, required=True, help='Feed ID')
    update_feed_parser.add_argument('--title', help='New title')
    update_feed_parser.add_argument('--category', type=int, help='New category ID')
    update_feed_parser.add_argument('--url', help='New feed URL')
    update_feed_parser.add_argument('--site-url', help='New site URL')
    update_feed_parser.add_argument('--crawler', action='store_true', help='Enable crawler')
    update_feed_parser.add_argument('--no-crawler', dest='crawler', action='store_false', help='Disable crawler')
    update_feed_parser.add_argument('--user-agent', help='Custom user agent')
    update_feed_parser.set_defaults(func=cmd_update_feed)

    # Delete feed
    delete_feed_parser = subparsers.add_parser('delete-feed', help='Delete a feed')
    delete_feed_parser.add_argument('--feed-id', type=int, required=True, help='Feed ID')
    delete_feed_parser.set_defaults(func=cmd_delete_feed)

    # Refresh all
    subparsers.add_parser('refresh-all', help='Refresh all feeds').set_defaults(func=cmd_refresh_all)

    # Refresh feed
    refresh_feed_parser = subparsers.add_parser('refresh-feed', help='Refresh a specific feed')
    refresh_feed_parser.add_argument('--feed-id', type=int, required=True, help='Feed ID')
    refresh_feed_parser.set_defaults(func=cmd_refresh_feed)

    # Mark read
    mark_read_parser = subparsers.add_parser('mark-read', help='Mark entries as read')
    mark_read_parser.add_argument('--entry-ids', required=True, help='Comma-separated entry IDs')
    mark_read_parser.set_defaults(func=cmd_mark_read)

    # Mark unread
    mark_unread_parser = subparsers.add_parser('mark-unread', help='Mark entries as unread')
    mark_unread_parser.add_argument('--entry-ids', required=True, help='Comma-separated entry IDs')
    mark_unread_parser.set_defaults(func=cmd_mark_unread)

    # Mark feed read
    mark_feed_read_parser = subparsers.add_parser('mark-feed-read', help='Mark all entries of a feed as read')
    mark_feed_read_parser.add_argument('--feed-id', type=int, required=True, help='Feed ID')
    mark_feed_read_parser.set_defaults(func=cmd_mark_feed_read)

    # Discover
    discover_parser = subparsers.add_parser('discover', help='Discover subscriptions from a URL')
    discover_parser.add_argument('--url', required=True, help='URL to discover feeds from')
    discover_parser.set_defaults(func=cmd_discover)

    # Counters
    subparsers.add_parser('counters', help='Get unread/read counters per feed').set_defaults(func=cmd_counters)

    # Me
    subparsers.add_parser('me', help='Get current user info').set_defaults(func=cmd_me)

    # Create category
    create_category_parser = subparsers.add_parser('create-category', help='Create a new category')
    create_category_parser.add_argument('--title', required=True, help='Category title')
    create_category_parser.set_defaults(func=cmd_create_category)

    # Toggle bookmark
    toggle_bookmark_parser = subparsers.add_parser('toggle-bookmark', help='Toggle bookmark/star status of an entry')
    toggle_bookmark_parser.add_argument('--entry-id', type=int, required=True, help='Entry ID')
    toggle_bookmark_parser.set_defaults(func=cmd_toggle_bookmark)

    # Delete category
    delete_category_parser = subparsers.add_parser('delete-category', help='Delete a category')
    delete_category_parser.add_argument('--category-id', type=int, required=True, help='Category ID')
    delete_category_parser.set_defaults(func=cmd_delete_category)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
