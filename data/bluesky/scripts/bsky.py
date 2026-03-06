#!/usr/bin/env python3
"""Bluesky CLI - bird-like interface for Bluesky/AT Protocol"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

VERSION = "1.6.0"

try:
    from atproto import Client, client_utils, models
except ImportError:
    print("Error: atproto not installed. Run: pip install atproto", file=sys.stderr)
    sys.exit(1)

CONFIG_PATH = Path.home() / ".config" / "bsky" / "config.json"


def normalize_handle(handle):
    """Strip leading @ and append .bsky.social if no domain specified."""
    handle = handle.lstrip("@")
    return handle


def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Write with restrictive permissions from the start
    fd = os.open(str(CONFIG_PATH), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, json.dumps(config, indent=2).encode())
    finally:
        os.close(fd)


def get_client():
    config = load_config()

    # Prefer session string (no password stored)
    if config.get("session"):
        client = Client()
        try:
            client.login(session_string=config["session"])
            # Update session in case it was refreshed
            new_session = client.export_session_string()
            if new_session != config["session"]:
                config["session"] = new_session
                save_config(config)
            return client
        except Exception:
            # Session expired/invalid, need to re-login
            print(
                "Session expired. Run: bsky login --handle your.handle --password your-app-password",
                file=sys.stderr,
            )
            sys.exit(1)

    # Legacy: support old configs with app_password (migrate on use)
    if config.get("handle") and config.get("app_password"):
        client = Client()
        client.login(config["handle"], config["app_password"])
        # Migrate to session-based auth
        config["session"] = client.export_session_string()
        del config["app_password"]
        save_config(config)
        print("(Migrated to session-based auth, app password removed)", file=sys.stderr)
        return client

    print(
        "Not logged in. Run: bsky login --handle your.handle --password your-app-password",
        file=sys.stderr,
    )
    sys.exit(1)


def parse_post_uri(uri_or_url):
    """Convert bsky.app URL or at:// URI to at:// URI format."""
    if uri_or_url.startswith("at://"):
        return uri_or_url

    # Parse bsky.app URL: https://bsky.app/profile/handle/post/id
    match = re.match(r"https?://bsky\.app/profile/([^/]+)/post/([^/\?]+)", uri_or_url)
    if match:
        handle, post_id = match.groups()
        # We need to resolve handle to DID - will do this in the command
        return {"handle": handle, "post_id": post_id}

    # Might just be a post ID
    if "/" not in uri_or_url and not uri_or_url.startswith("at://"):
        return {"post_id": uri_or_url}

    raise ValueError(f"Cannot parse post reference: {uri_or_url}")


def resolve_post(client, uri_or_url):
    """Resolve a post URI/URL to get full post details including CID."""
    parsed = parse_post_uri(uri_or_url)

    if isinstance(parsed, str):
        # Already an at:// URI
        uri = parsed
    elif "handle" in parsed:
        # Need to resolve handle to DID first
        handle = normalize_handle(parsed["handle"])
        profile = client.get_profile(handle)
        uri = f"at://{profile.did}/app.bsky.feed.post/{parsed['post_id']}"
    else:
        # Just post_id, use current user
        uri = f"at://{client.me.did}/app.bsky.feed.post/{parsed['post_id']}"

    # Fetch the post to get CID
    response = client.get_posts([uri])
    if not response.posts:
        raise ValueError(f"Post not found: {uri}")

    return response.posts[0]


def get_thread_root(post):
    """Get the root of a thread from a post."""
    if hasattr(post.record, "reply") and post.record.reply:
        return post.record.reply.root
    # This post is the root
    return models.ComAtprotoRepoStrongRef.Main(uri=post.uri, cid=post.cid)


def cmd_login(args):
    try:
        password = args.password or os.environ.get("BSKY_PASSWORD")
        if not password:
            import getpass

            password = getpass.getpass("App password: ")
        client = Client()
        client.login(args.handle, password)
        # Store session string only - password never saved to disk
        config = {
            "handle": client.me.handle,
            "did": client.me.did,
            "session": client.export_session_string(),
        }
        save_config(config)
        print(f"Logged in as {client.me.handle} ({client.me.did})")
        print("(Password not stored - using session token)")
    except Exception as e:
        print(f"Login failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_logout(args):
    config = load_config()
    if config.get("session"):
        config.pop("session", None)
        config.pop("handle", None)
        config.pop("did", None)
        save_config(config)
        print("Logged out successfully")
    else:
        print("Not logged in")


def cmd_whoami(args):
    config = load_config()
    if config.get("handle"):
        client = get_client()
        if args.json:
            data = {
                "handle": client.me.handle,
                "did": client.me.did,
            }
            print(json.dumps(data, indent=2))
            return
        print(f"Handle: {client.me.handle}")
        print(f"DID: {client.me.did}")
    else:
        print("Not logged in")


def format_post(post, include_link=True):
    """Format a post for display."""
    author = post.author.handle
    text = post.record.text if hasattr(post.record, "text") else ""
    created = post.record.created_at if hasattr(post.record, "created_at") else ""
    likes = post.like_count or 0
    reposts = post.repost_count or 0
    replies = post.reply_count or 0

    try:
        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        time_str = dt.strftime("%b %d %H:%M")
    except Exception:
        time_str = created[:16] if created else ""

    lines = [
        f"@{author} · {time_str}",
        f"  {text[:200]}",
        f"  ❤️ {likes}  🔁 {reposts}  💬 {replies}",
    ]
    if include_link:
        lines.append(
            f"  🔗 https://bsky.app/profile/{author}/post/{post.uri.split('/')[-1]}"
        )

    return "\n".join(lines)


def post_to_dict(post):
    """Convert a post to a dictionary for JSON output."""
    return {
        "uri": post.uri,
        "cid": post.cid,
        "author": {
            "handle": post.author.handle,
            "did": post.author.did,
            "displayName": getattr(post.author, "display_name", None),
        },
        "text": post.record.text if hasattr(post.record, "text") else "",
        "createdAt": post.record.created_at
        if hasattr(post.record, "created_at")
        else "",
        "likes": post.like_count or 0,
        "reposts": post.repost_count or 0,
        "replies": post.reply_count or 0,
        "url": f"https://bsky.app/profile/{post.author.handle}/post/{post.uri.split('/')[-1]}",
    }


def cmd_timeline(args):
    client = get_client()
    response = client.get_timeline(limit=args.count)

    if args.json:
        posts = [post_to_dict(item.post) for item in response.feed]
        print(json.dumps(posts, indent=2))
        return

    for item in response.feed:
        print(format_post(item.post))
        print()


def build_post_with_facets(client, text):
    """Build a post with proper facets for URLs and mentions."""
    url_pattern = r"(https?://[^\s]+)"
    urls = re.findall(url_pattern, text)

    mention_pattern = r"@([a-zA-Z0-9._-]+)"
    mentions = re.findall(mention_pattern, text)

    if not urls and not mentions:
        return text, None

    # Use TextBuilder for proper facets (links and mentions)
    builder = client_utils.TextBuilder()

    # Combined pattern to find both URLs and mentions in order
    combined_pattern = r"(https?://[^\s]+)|(@[a-zA-Z0-9._-]+)"
    last_end = 0

    # Resolve mention handles to DIDs
    mention_dids = {}
    for handle in mentions:
        full_handle = normalize_handle(handle)
        try:
            profile = client.get_profile(full_handle)
            mention_dids[handle] = profile.did
        except Exception:
            print(f"Warning: could not resolve @{handle}", file=sys.stderr)

    for match in re.finditer(combined_pattern, text):
        if match.start() > last_end:
            builder.text(text[last_end : match.start()])

        if match.group(1):  # URL
            url = match.group(1)
            builder.link(url, url)
        elif match.group(2):  # Mention
            mention_text = match.group(2)
            handle = mention_text[1:]
            if handle in mention_dids:
                builder.mention(mention_text, mention_dids[handle])
            else:
                builder.text(mention_text)

        last_end = match.end()

    if last_end < len(text):
        builder.text(text[last_end:])

    return builder


def cmd_post(args):
    text = args.text

    # Validate text
    if not text or not text.strip():
        print("Error: Post text cannot be empty", file=sys.stderr)
        sys.exit(1)

    if len(text) > 300:
        print(f"Error: Post is {len(text)} chars (max 300)", file=sys.stderr)
        sys.exit(1)

    # Validate image args
    if args.image and not args.alt:
        print("Error: --alt is required when using --image", file=sys.stderr)
        sys.exit(1)

    # Load image if provided
    image_data = None
    if args.image:
        image_path = Path(args.image).expanduser()
        if not image_path.exists():
            print(f"Error: Image file not found: {args.image}", file=sys.stderr)
            sys.exit(1)
        image_data = image_path.read_bytes()
        # Check size (max 1MB for Bluesky)
        if len(image_data) > 1_000_000:
            print(
                f"Error: Image too large ({len(image_data) / 1_000_000:.1f}MB, max 1MB)",
                file=sys.stderr,
            )
            sys.exit(1)

    # Dry run - show what would be posted without actually posting
    if args.dry_run:
        print("=== DRY RUN (not posting) ===")
        print(f"Text ({len(text)} chars):")
        print(f"  {text}")

        url_pattern = r"(https?://[^\s]+)"
        urls = re.findall(url_pattern, text)
        if urls:
            print(f"Links detected: {len(urls)}")
            for url in urls:
                print(f"  • {url}")

        if args.image:
            print(f"Image: {args.image}")
            print(f"  Alt: {args.alt}")
            if image_data:
                print(f"  Size: {len(image_data) / 1000:.1f}KB")

        print("=============================")
        return

    client = get_client()

    # Build facets for URLs and mentions
    built = build_post_with_facets(client, text)

    # Post with image
    if image_data:
        if isinstance(built, client_utils.TextBuilder):
            response = client.send_image(
                text=built,
                image=image_data,
                image_alt=args.alt,
            )
        else:
            response = client.send_image(
                text=text,
                image=image_data,
                image_alt=args.alt,
            )
    else:
        if isinstance(built, client_utils.TextBuilder):
            response = client.send_post(built)
        else:
            response = client.send_post(text=text)

    uri = response.uri
    post_id = uri.split("/")[-1]
    url = f"https://bsky.app/profile/{client.me.handle}/post/{post_id}"
    if args.quiet:
        print(url)
    else:
        print(f"Posted: {url}")


def cmd_reply(args):
    text = args.text

    # Validate text
    if not text or not text.strip():
        print("Error: Reply text cannot be empty", file=sys.stderr)
        sys.exit(1)

    if len(text) > 300:
        print(f"Error: Reply is {len(text)} chars (max 300)", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("=== DRY RUN (not replying) ===")
        print(f"Replying to: {args.uri}")
        print(f"Text ({len(text)} chars):")
        print(f"  {text}")
        print("==============================")
        return

    client = get_client()

    # Resolve the parent post
    try:
        parent_post = resolve_post(client, args.uri)
    except Exception as e:
        print(f"Error resolving post: {e}", file=sys.stderr)
        sys.exit(1)

    # Get thread root
    root_ref = get_thread_root(parent_post)
    parent_ref = models.ComAtprotoRepoStrongRef.Main(
        uri=parent_post.uri, cid=parent_post.cid
    )

    # Build reply reference
    reply_ref = models.AppBskyFeedPost.ReplyRef(root=root_ref, parent=parent_ref)

    # Build post with facets
    built = build_post_with_facets(client, text)

    if isinstance(built, client_utils.TextBuilder):
        response = client.send_post(built, reply_to=reply_ref)
    else:
        response = client.send_post(text=text, reply_to=reply_ref)

    uri = response.uri
    post_id = uri.split("/")[-1]
    url = f"https://bsky.app/profile/{client.me.handle}/post/{post_id}"
    if args.quiet:
        print(url)
    else:
        print(f"Replied: {url}")


def cmd_quote(args):
    text = args.text

    # Validate text
    if not text or not text.strip():
        print("Error: Quote text cannot be empty", file=sys.stderr)
        sys.exit(1)

    if len(text) > 300:
        print(f"Error: Quote is {len(text)} chars (max 300)", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("=== DRY RUN (not quoting) ===")
        print(f"Quoting: {args.uri}")
        print(f"Text ({len(text)} chars):")
        print(f"  {text}")
        print("=============================")
        return

    client = get_client()

    # Resolve the quoted post
    try:
        quoted_post = resolve_post(client, args.uri)
    except Exception as e:
        print(f"Error resolving post: {e}", file=sys.stderr)
        sys.exit(1)

    # Create embed for quote
    embed = models.AppBskyEmbedRecord.Main(
        record=models.ComAtprotoRepoStrongRef.Main(
            uri=quoted_post.uri, cid=quoted_post.cid
        )
    )

    # Build post with facets
    built = build_post_with_facets(client, text)

    if isinstance(built, client_utils.TextBuilder):
        response = client.send_post(built, embed=embed)
    else:
        response = client.send_post(text=text, embed=embed)

    uri = response.uri
    post_id = uri.split("/")[-1]
    url = f"https://bsky.app/profile/{client.me.handle}/post/{post_id}"
    if args.quiet:
        print(url)
    else:
        print(f"Quoted: {url}")


def cmd_thread_view(args):
    client = get_client()

    # Resolve the post URI
    try:
        if args.uri.startswith("at://"):
            uri = args.uri
        else:
            post = resolve_post(client, args.uri)
            uri = post.uri
    except Exception as e:
        print(f"Error resolving post: {e}", file=sys.stderr)
        sys.exit(1)

    # Get thread
    response = client.get_post_thread(uri, depth=args.depth)

    if not response.thread:
        print("Thread not found")
        return

    def print_thread_post(thread_item, indent=0):
        """Recursively print thread posts."""
        prefix = "  " * indent

        if hasattr(thread_item, "post"):
            post = thread_item.post
            author = post.author.handle
            text = post.record.text if hasattr(post.record, "text") else ""
            likes = post.like_count or 0
            reposts = post.repost_count or 0
            replies = post.reply_count or 0

            try:
                created = post.record.created_at
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                time_str = dt.strftime("%b %d %H:%M")
            except Exception:
                time_str = ""

            if args.json:
                return post_to_dict(post)

            print(f"{prefix}┌─ @{author} · {time_str}")
            for line in text.split("\n"):
                print(f"{prefix}│  {line[:200]}")
            print(f"{prefix}│  ❤️ {likes}  🔁 {reposts}  💬 {replies}")
            print(
                f"{prefix}└─ 🔗 https://bsky.app/profile/{author}/post/{post.uri.split('/')[-1]}"
            )
            print()

            # Print replies
            if hasattr(thread_item, "replies") and thread_item.replies:
                for reply in thread_item.replies:
                    print_thread_post(reply, indent + 1)

    # Print parent chain first (if exists)
    if hasattr(response.thread, "parent") and response.thread.parent:

        def print_parents(parent, depth=0):
            if depth > 10:  # Safety limit
                return
            if hasattr(parent, "parent") and parent.parent:
                print_parents(parent.parent, depth + 1)
            if hasattr(parent, "post"):
                print("↑ Parent:")
                print_thread_post(parent, 0)

        print_parents(response.thread.parent)
        print("─" * 40)
        print("📍 This post:")
        print()

    if args.json:
        posts = []

        def collect_posts(item):
            if hasattr(item, "post"):
                posts.append(post_to_dict(item.post))
            if hasattr(item, "replies") and item.replies:
                for reply in item.replies:
                    collect_posts(reply)

        collect_posts(response.thread)
        print(json.dumps(posts, indent=2))
        return

    print_thread_post(response.thread)


def cmd_create_thread(args):
    """Create a thread of posts, each replying to the previous."""
    texts = args.texts

    # Validate: need at least 2 posts for a thread
    if len(texts) < 2:
        print("Error: Thread needs at least 2 posts", file=sys.stderr)
        sys.exit(1)

    # Validate lengths
    for i, text in enumerate(texts, 1):
        if not text or not text.strip():
            print(f"Error: Post {i} is empty", file=sys.stderr)
            sys.exit(1)
        if len(text) > 300:
            print(f"Error: Post {i} is {len(text)} chars (max 300)", file=sys.stderr)
            sys.exit(1)

    # Validate image args
    if args.image and not args.alt:
        print("Error: --alt is required when using --image", file=sys.stderr)
        sys.exit(1)

    # Load image if provided (for first post only)
    image_data = None
    if args.image:
        image_path = Path(args.image).expanduser()
        if not image_path.exists():
            print(f"Error: Image file not found: {args.image}", file=sys.stderr)
            sys.exit(1)
        image_data = image_path.read_bytes()
        if len(image_data) > 1_000_000:
            print(
                f"Error: Image too large ({len(image_data) / 1_000_000:.1f}MB, max 1MB)",
                file=sys.stderr,
            )
            sys.exit(1)

    # Dry run
    if args.dry_run:
        print(f"=== DRY RUN: Thread with {len(texts)} posts ===")
        for i, text in enumerate(texts, 1):
            print(f"\n📝 Post {i}/{len(texts)} ({len(text)} chars):")
            print(f"  {text}")

            url_pattern = r"(https?://[^\s]+)"
            urls = re.findall(url_pattern, text)
            if urls:
                print(f"  Links: {', '.join(urls)}")

        if args.image:
            print(f"\n🖼️ Image on post 1: {args.image}")
            print(f"  Alt: {args.alt}")
            if image_data:
                print(f"  Size: {len(image_data) / 1000:.1f}KB")

        print("\n=============================")
        return

    client = get_client()
    total = len(texts)
    posted_urls = []
    root_ref = None
    parent_ref = None

    for i, text in enumerate(texts):
        post_num = i + 1
        try:
            built = build_post_with_facets(client, text)

            # Build reply ref (for posts after the first)
            reply_ref = None
            if i > 0:
                reply_ref = models.AppBskyFeedPost.ReplyRef(
                    root=root_ref, parent=parent_ref
                )

            # First post may have an image
            if i == 0 and image_data:
                if isinstance(built, client_utils.TextBuilder):
                    response = client.send_image(
                        text=built,
                        image=image_data,
                        image_alt=args.alt,
                    )
                else:
                    response = client.send_image(
                        text=text,
                        image=image_data,
                        image_alt=args.alt,
                    )
            else:
                if isinstance(built, client_utils.TextBuilder):
                    response = client.send_post(built, reply_to=reply_ref)
                else:
                    response = client.send_post(text=text, reply_to=reply_ref)

            uri = response.uri
            cid = response.cid
            post_id = uri.split("/")[-1]
            url = f"https://bsky.app/profile/{client.me.handle}/post/{post_id}"
            posted_urls.append(url)

            # Set root ref from first post
            if i == 0:
                root_ref = models.ComAtprotoRepoStrongRef.Main(uri=uri, cid=cid)

            # Parent ref is always the most recent post
            parent_ref = models.ComAtprotoRepoStrongRef.Main(uri=uri, cid=cid)

            print(f"Posted {post_num}/{total}: {url}")

        except Exception as e:
            print(f"\n❌ Failed on post {post_num}/{total}: {e}", file=sys.stderr)
            if posted_urls:
                print(
                    f"\n✅ Successfully posted {len(posted_urls)}/{total}:",
                    file=sys.stderr,
                )
                for url in posted_urls:
                    print(f"  {url}", file=sys.stderr)
            sys.exit(1)

    print(f"\n🧵 Thread complete! ({total} posts)")
    print(f"🔗 {posted_urls[0]}")


def cmd_delete(args):
    client = get_client()
    # Extract post ID from URL or use raw ID
    post_id = args.post_id
    if "bsky.app" in post_id:
        post_id = post_id.rstrip("/").split("/")[-1]

    # Handle at:// URIs
    if post_id.startswith("at://"):
        uri = post_id
    else:
        # Construct the URI
        uri = f"at://{client.me.did}/app.bsky.feed.post/{post_id}"

    try:
        client.delete_post(uri)
        print(f"Deleted post: {post_id}")
    except Exception as e:
        print(f"Delete failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_profile(args):
    client = get_client()
    handle = normalize_handle(args.handle) if args.handle else client.me.handle

    profile = client.get_profile(handle)

    if args.json:
        data = {
            "handle": profile.handle,
            "did": profile.did,
            "displayName": profile.display_name,
            "description": profile.description,
            "followersCount": profile.followers_count,
            "followsCount": profile.follows_count,
            "postsCount": profile.posts_count,
            "avatar": getattr(profile, "avatar", None),
            "banner": getattr(profile, "banner", None),
        }
        print(json.dumps(data, indent=2))
        return

    print(f"@{profile.handle}")
    print(f"  Name: {profile.display_name or '(none)'}")
    print(f"  Bio: {profile.description or '(none)'}")
    print(f"  Followers: {profile.followers_count}")
    print(f"  Following: {profile.follows_count}")
    print(f"  Posts: {profile.posts_count}")
    print(f"  DID: {profile.did}")


def cmd_search(args):
    client = get_client()
    response = client.app.bsky.feed.search_posts({"q": args.query, "limit": args.count})

    if not response.posts:
        print("No results found.")
        return

    if args.json:
        posts = [post_to_dict(post) for post in response.posts]
        print(json.dumps(posts, indent=2))
        return

    for post in response.posts:
        author = post.author.handle
        text = post.record.text if hasattr(post.record, "text") else ""
        likes = post.like_count or 0

        print(f"@{author}: {text[:150]}")
        print(
            f"  ❤️ {likes}  🔗 https://bsky.app/profile/{author}/post/{post.uri.split('/')[-1]}"
        )
        print()


def cmd_notifications(args):
    client = get_client()
    response = client.app.bsky.notification.list_notifications({"limit": args.count})

    if args.json:
        notifs = []
        for notif in response.notifications:
            notifs.append(
                {
                    "reason": notif.reason,
                    "author": {
                        "handle": notif.author.handle,
                        "did": notif.author.did,
                    },
                    "indexedAt": notif.indexed_at,
                    "uri": notif.uri,
                    "isRead": notif.is_read,
                }
            )
        print(json.dumps(notifs, indent=2))
        return

    if not response.notifications:
        print("No notifications yet — go make some noise! 📢")
        return

    for notif in response.notifications:
        reason = notif.reason
        author = notif.author.handle
        time_str = notif.indexed_at[:16] if notif.indexed_at else ""

        icons = {
            "like": "❤️",
            "repost": "🔁",
            "follow": "👤",
            "reply": "💬",
            "mention": "📢",
            "quote": "💭",
        }
        icon = icons.get(reason, "•")

        if reason == "like":
            print(f"{icon} @{author} liked your post · {time_str}")
        elif reason == "repost":
            print(f"{icon} @{author} reposted · {time_str}")
        elif reason == "follow":
            print(f"{icon} @{author} followed you · {time_str}")
        elif reason == "reply":
            print(f"{icon} @{author} replied · {time_str}")
        elif reason == "mention":
            print(f"{icon} @{author} mentioned you · {time_str}")
        elif reason == "quote":
            print(f"{icon} @{author} quoted you · {time_str}")
        else:
            print(f"{icon} {reason} from @{author} · {time_str}")


def cmd_like(args):
    client = get_client()

    try:
        post = resolve_post(client, args.uri)
    except Exception as e:
        print(f"Error resolving post: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        client.like(uri=post.uri, cid=post.cid)
        print(
            f"❤️ Liked: https://bsky.app/profile/{post.author.handle}/post/{post.uri.split('/')[-1]}"
        )
    except Exception as e:
        print(f"Like failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_unlike(args):
    client = get_client()

    try:
        post = resolve_post(client, args.uri)
    except Exception as e:
        print(f"Error resolving post: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # Get the post with viewer state to find like URI
        posts_response = client.get_posts([post.uri])
        if not posts_response.posts:
            print("Post not found", file=sys.stderr)
            sys.exit(1)

        post_data = posts_response.posts[0]
        if (
            not hasattr(post_data, "viewer")
            or not post_data.viewer
            or not post_data.viewer.like
        ):
            print("You haven't liked this post", file=sys.stderr)
            sys.exit(1)

        like_uri = post_data.viewer.like
        rkey = like_uri.split("/")[-1]
        client.app.bsky.feed.like.delete(client.me.did, rkey)
        print(
            f"💔 Unliked: https://bsky.app/profile/{post.author.handle}/post/{post.uri.split('/')[-1]}"
        )
    except Exception as e:
        print(f"Unlike failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_repost(args):
    client = get_client()

    try:
        post = resolve_post(client, args.uri)
    except Exception as e:
        print(f"Error resolving post: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        client.repost(uri=post.uri, cid=post.cid)
        print(
            f"🔁 Reposted: https://bsky.app/profile/{post.author.handle}/post/{post.uri.split('/')[-1]}"
        )
    except Exception as e:
        print(f"Repost failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_unrepost(args):
    client = get_client()

    try:
        post = resolve_post(client, args.uri)
    except Exception as e:
        print(f"Error resolving post: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # Get the repost URI from the post's viewer state
        posts_response = client.get_posts([post.uri])
        if not posts_response.posts:
            print("Post not found", file=sys.stderr)
            sys.exit(1)

        post_data = posts_response.posts[0]
        if (
            not hasattr(post_data, "viewer")
            or not post_data.viewer
            or not post_data.viewer.repost
        ):
            print("You haven't reposted this post", file=sys.stderr)
            sys.exit(1)

        repost_uri = post_data.viewer.repost
        rkey = repost_uri.split("/")[-1]
        client.app.bsky.feed.repost.delete(client.me.did, rkey)
        print(
            f"🔄 Unreposted: https://bsky.app/profile/{post.author.handle}/post/{post.uri.split('/')[-1]}"
        )
    except Exception as e:
        print(f"Unrepost failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_follow(args):
    client = get_client()

    handle = normalize_handle(args.handle)

    try:
        profile = client.get_profile(handle)
        client.follow(profile.did)
        print(f"👤 Following @{profile.handle}")
    except Exception as e:
        print(f"Follow failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_unfollow(args):
    client = get_client()

    handle = normalize_handle(args.handle)

    try:
        profile = client.get_profile(handle)

        # Check if following and get the follow record URI
        if (
            not hasattr(profile, "viewer")
            or not profile.viewer
            or not profile.viewer.following
        ):
            print(f"You're not following @{profile.handle}", file=sys.stderr)
            sys.exit(1)

        follow_uri = profile.viewer.following
        rkey = follow_uri.split("/")[-1]
        client.app.bsky.graph.follow.delete(client.me.did, rkey)
        print(f"👋 Unfollowed @{profile.handle}")
    except Exception as e:
        print(f"Unfollow failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_block(args):
    client = get_client()

    handle = normalize_handle(args.handle)

    try:
        profile = client.get_profile(handle)

        # Check if already blocked
        if hasattr(profile, "viewer") and profile.viewer and profile.viewer.blocking:
            print(f"Already blocking @{profile.handle}", file=sys.stderr)
            sys.exit(1)

        # Create block record
        client.app.bsky.graph.block.create(
            client.me.did,
            models.AppBskyGraphBlock.Record(
                subject=profile.did,
                created_at=client.get_current_time_iso(),
            ),
        )
        print(f"🚫 Blocked @{profile.handle}")
    except Exception as e:
        print(f"Block failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_unblock(args):
    client = get_client()

    handle = normalize_handle(args.handle)

    try:
        profile = client.get_profile(handle)

        # Check if blocking
        if (
            not hasattr(profile, "viewer")
            or not profile.viewer
            or not profile.viewer.blocking
        ):
            print(f"You're not blocking @{profile.handle}", file=sys.stderr)
            sys.exit(1)

        block_uri = profile.viewer.blocking
        rkey = block_uri.split("/")[-1]
        client.app.bsky.graph.block.delete(client.me.did, rkey)
        print(f"✅ Unblocked @{profile.handle}")
    except Exception as e:
        print(f"Unblock failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_mute(args):
    client = get_client()

    handle = normalize_handle(args.handle)

    try:
        profile = client.get_profile(handle)
        client.mute(profile.did)
        print(f"🔇 Muted @{profile.handle}")
    except Exception as e:
        print(f"Mute failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_unmute(args):
    client = get_client()

    handle = normalize_handle(args.handle)

    try:
        profile = client.get_profile(handle)
        client.unmute(profile.did)
        print(f"🔊 Unmuted @{profile.handle}")
    except Exception as e:
        print(f"Unmute failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_stats(args):
    client = get_client()
    handle = normalize_handle(args.handle) if args.handle else client.me.handle

    profile = client.get_profile(handle)

    if args.json:
        data = {
            "handle": profile.handle,
            "postsCount": profile.posts_count,
            "followersCount": profile.followers_count,
            "followsCount": profile.follows_count,
        }
        print(json.dumps(data, indent=2))
        return

    print(f"@{profile.handle}")
    print(f"📝 Posts: {profile.posts_count}")
    print(f"👥 Followers: {profile.followers_count}")
    print(f"👤 Following: {profile.follows_count}")


def main():
    parser = argparse.ArgumentParser(description="Bluesky CLI")
    parser.add_argument("-v", "--version", action="version", version=f"bsky {VERSION}")
    subparsers = parser.add_subparsers(dest="command")

    # login
    login_p = subparsers.add_parser("login", help="Login to Bluesky")
    login_p.add_argument(
        "--handle", required=True, help="Your handle (e.g. user.bsky.social)"
    )
    login_p.add_argument(
        "--password",
        required=False,
        help="App password (or set BSKY_PASSWORD env var, or omit to be prompted)",
    )

    # logout
    subparsers.add_parser("logout", help="Log out and clear session")

    # whoami
    whoami_p = subparsers.add_parser("whoami", help="Show current user")
    whoami_p.add_argument("--json", action="store_true", help="Output as JSON")

    # timeline
    tl_p = subparsers.add_parser(
        "timeline", aliases=["tl", "home"], help="Show home timeline"
    )
    tl_p.add_argument("-n", "--count", type=int, default=10, help="Number of posts")
    tl_p.add_argument("--json", action="store_true", help="Output as JSON")

    # post
    post_p = subparsers.add_parser("post", aliases=["p"], help="Create a post")
    post_p.add_argument("text", help="Post text")
    post_p.add_argument(
        "--image",
        help="Path to image file to attach",
    )
    post_p.add_argument(
        "--alt",
        help="Alt text for image (required with --image)",
    )
    post_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be posted without posting",
    )
    post_p.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only print the post URL",
    )

    # reply
    reply_p = subparsers.add_parser("reply", aliases=["r"], help="Reply to a post")
    reply_p.add_argument("uri", help="Post URI or URL to reply to")
    reply_p.add_argument("text", help="Reply text")
    reply_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be posted without posting",
    )
    reply_p.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only print the post URL",
    )

    # quote
    quote_p = subparsers.add_parser("quote", aliases=["qt"], help="Quote a post")
    quote_p.add_argument("uri", help="Post URI or URL to quote")
    quote_p.add_argument("text", help="Quote text")
    quote_p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be posted without posting",
    )
    quote_p.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only print the post URL",
    )

    # thread (view)
    thread_p = subparsers.add_parser("thread", aliases=["th"], help="View a thread")
    thread_p.add_argument("uri", help="Post URI or URL")
    thread_p.add_argument("--depth", type=int, default=6, help="Reply depth to fetch")
    thread_p.add_argument("--json", action="store_true", help="Output as JSON")

    # create-thread
    cthread_p = subparsers.add_parser(
        "create-thread", aliases=["ct"], help="Create a thread of posts"
    )
    cthread_p.add_argument(
        "texts", nargs="+", help="Post texts (each quoted separately)"
    )
    cthread_p.add_argument("--image", help="Image for first post")
    cthread_p.add_argument("--alt", help="Alt text for image (required with --image)")
    cthread_p.add_argument(
        "--dry-run", action="store_true", help="Preview thread without posting"
    )
    cthread_p.add_argument(
        "--quiet", "-q", action="store_true", help="Only print post URLs"
    )

    # delete
    del_p = subparsers.add_parser("delete", aliases=["del", "rm"], help="Delete a post")
    del_p.add_argument("post_id", help="Post ID or URL")

    # profile
    profile_p = subparsers.add_parser("profile", help="Show profile")
    profile_p.add_argument(
        "handle", nargs="?", help="Handle to look up (default: self)"
    )
    profile_p.add_argument("--json", action="store_true", help="Output as JSON")

    # search
    search_p = subparsers.add_parser("search", aliases=["s"], help="Search posts")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument(
        "-n", "--count", type=int, default=10, help="Number of results"
    )
    search_p.add_argument("--json", action="store_true", help="Output as JSON")

    # notifications
    notif_p = subparsers.add_parser(
        "notifications", aliases=["notif", "n"], help="Show notifications"
    )
    notif_p.add_argument(
        "-n", "--count", type=int, default=20, help="Number of notifications"
    )
    notif_p.add_argument("--json", action="store_true", help="Output as JSON")

    # like
    like_p = subparsers.add_parser("like", help="Like a post")
    like_p.add_argument("uri", help="Post URI or URL to like")

    # unlike
    unlike_p = subparsers.add_parser("unlike", help="Unlike a post")
    unlike_p.add_argument("uri", help="Post URI or URL to unlike")

    # repost
    repost_p = subparsers.add_parser("repost", aliases=["boost", "rt"], help="Repost")
    repost_p.add_argument("uri", help="Post URI or URL to repost")

    # unrepost
    unrepost_p = subparsers.add_parser(
        "unrepost", aliases=["unboost", "unrt"], help="Remove repost"
    )
    unrepost_p.add_argument("uri", help="Post URI or URL to unrepost")

    # follow
    follow_p = subparsers.add_parser("follow", help="Follow a user")
    follow_p.add_argument("handle", help="Handle to follow")

    # unfollow
    unfollow_p = subparsers.add_parser("unfollow", help="Unfollow a user")
    unfollow_p.add_argument("handle", help="Handle to unfollow")

    # block
    block_p = subparsers.add_parser("block", help="Block a user")
    block_p.add_argument("handle", help="Handle to block")

    # unblock
    unblock_p = subparsers.add_parser("unblock", help="Unblock a user")
    unblock_p.add_argument("handle", help="Handle to unblock")

    # mute
    mute_p = subparsers.add_parser("mute", help="Mute a user")
    mute_p.add_argument("handle", help="Handle to mute")

    # unmute
    unmute_p = subparsers.add_parser("unmute", help="Unmute a user")
    unmute_p.add_argument("handle", help="Handle to unmute")

    # stats
    stats_p = subparsers.add_parser("stats", help="Show account stats")
    stats_p.add_argument("handle", nargs="?", help="Handle to look up (default: self)")
    stats_p.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    commands = {
        "login": cmd_login,
        "logout": cmd_logout,
        "whoami": cmd_whoami,
        "timeline": cmd_timeline,
        "tl": cmd_timeline,
        "home": cmd_timeline,
        "post": cmd_post,
        "p": cmd_post,
        "reply": cmd_reply,
        "r": cmd_reply,
        "quote": cmd_quote,
        "qt": cmd_quote,
        "thread": cmd_thread_view,
        "th": cmd_thread_view,
        "create-thread": cmd_create_thread,
        "ct": cmd_create_thread,
        "delete": cmd_delete,
        "del": cmd_delete,
        "rm": cmd_delete,
        "profile": cmd_profile,
        "search": cmd_search,
        "s": cmd_search,
        "notifications": cmd_notifications,
        "notif": cmd_notifications,
        "n": cmd_notifications,
        "like": cmd_like,
        "unlike": cmd_unlike,
        "repost": cmd_repost,
        "boost": cmd_repost,
        "rt": cmd_repost,
        "unrepost": cmd_unrepost,
        "unboost": cmd_unrepost,
        "unrt": cmd_unrepost,
        "follow": cmd_follow,
        "unfollow": cmd_unfollow,
        "block": cmd_block,
        "unblock": cmd_unblock,
        "mute": cmd_mute,
        "unmute": cmd_unmute,
        "stats": cmd_stats,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
