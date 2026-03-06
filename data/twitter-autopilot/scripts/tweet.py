#!/usr/bin/env python3
"""Twitter/X automation for OpenClaw agents.

Supports: post, thread, reply, quote, retweet, delete, follow, unfollow, mentions, me.
Requires env vars: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, TWITTER_BEARER_TOKEN
"""
import os, sys, time
import tweepy

def get_client():
    return tweepy.Client(
        consumer_key=os.environ["TWITTER_API_KEY"],
        consumer_secret=os.environ["TWITTER_API_SECRET"],
        access_token=os.environ["TWITTER_ACCESS_TOKEN"],
        access_token_secret=os.environ["TWITTER_ACCESS_SECRET"],
    )

def get_bearer_client():
    return tweepy.Client(bearer_token=os.environ["TWITTER_BEARER_TOKEN"])

def post(text):
    """Post a single tweet. If >280 chars, auto-splits into a thread."""
    if len(text) <= 280:
        r = get_client().create_tweet(text=text)
        print(f"Posted: {r.data['id']}")
        return r.data['id']
    else:
        return thread_from_text(text)

def thread_from_text(text, max_len=280):
    """Split long text into a thread at sentence boundaries."""
    sentences = text.replace('\n\n', '\n').split('\n')
    chunks, current = [], ""
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if current and len(current) + len(s) + 1 > max_len:
            chunks.append(current.strip())
            current = s
        else:
            current = f"{current} {s}".strip() if current else s
    if current:
        chunks.append(current.strip())
    return thread(chunks)

def thread(tweets):
    """Post a list of tweets as a thread. Returns list of IDs."""
    client = get_client()
    ids = []
    reply_to = None
    for i, text in enumerate(tweets):
        kwargs = {"text": text}
        if reply_to:
            kwargs["in_reply_to_tweet_id"] = reply_to
        r = client.create_tweet(**kwargs)
        tid = r.data['id']
        ids.append(tid)
        reply_to = tid
        print(f"Tweet {i+1}/{len(tweets)}: {tid}")
        if i < len(tweets) - 1:
            time.sleep(1)
    return ids

def reply(tweet_id, text):
    r = get_client().create_tweet(text=text, in_reply_to_tweet_id=tweet_id)
    print(f"Replied: {r.data['id']}")

def quote(tweet_id, text):
    r = get_client().create_tweet(text=text, quote_tweet_id=tweet_id)
    print(f"Quoted: {r.data['id']}")

def retweet(tweet_id):
    client = get_client()
    me = client.get_me()
    client.retweet(tweet_id, user_auth=True)
    print(f"Retweeted: {tweet_id}")

def delete(tweet_id):
    get_client().delete_tweet(tweet_id)
    print(f"Deleted: {tweet_id}")

def follow(username):
    username = username.lstrip("@")
    user = get_bearer_client().get_user(username=username)
    if not user.data:
        print(f"Not found: {username}")
        return
    client = get_client()
    me = client.get_me()
    client.follow_user(user.data.id, user_auth=True)
    print(f"Followed: @{user.data.username}")

def unfollow(username):
    username = username.lstrip("@")
    user = get_bearer_client().get_user(username=username)
    if not user.data:
        print(f"Not found: {username}")
        return
    client = get_client()
    me = client.get_me()
    client.unfollow_user(user.data.id, user_auth=True)
    print(f"Unfollowed: @{user.data.username}")

def mentions(count=10):
    client = get_client()
    me = client.get_me()
    r = client.get_users_mentions(me.data.id, max_results=min(count, 100),
                                   tweet_fields=["created_at", "author_id"])
    if r.data:
        for t in r.data:
            print(f"[{t.created_at}] {t.id}: {t.text}")
    else:
        print("No mentions")

def me():
    r = get_client().get_me(user_fields=["public_metrics", "description"])
    u = r.data
    m = u.public_metrics
    print(f"@{u.username} | {m['followers_count']} followers | {m['following_count']} following | {m['tweet_count']} tweets")

def check_duplicate(text, log_path="twitter/posted-log.md"):
    """Check if a similar tweet was already posted (by exact substring match)."""
    if not os.path.exists(log_path):
        return False
    with open(log_path) as f:
        content = f.read().lower()
    # Check if first 60 chars of tweet text appear in log (catches reworded dupes)
    snippet = text.strip().lower()[:60]
    return snippet in content

def log_posted(tweet_id, text, source="auto", log_path="twitter/posted-log.md"):
    """Append posted tweet to the log file."""
    from datetime import datetime
    date = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    entry = f"\n**ID:** {tweet_id}\n**Text:** {text}\n**Source:** {source}\n**Date:** {date}\n"
    if not os.path.exists(log_path):
        with open(log_path, "w") as f:
            f.write(f"# Posted Tweets Log\n\n## {date}\n{entry}")
    else:
        with open(log_path, "a") as f:
            f.write(entry)

def post_from_queue(queue_path="twitter/queue.md", log_path="twitter/posted-log.md"):
    """Post first pending tweet from queue, check for duplicates, log result."""
    if not os.path.exists(queue_path):
        print("No queue file found")
        return
    with open(queue_path) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("- [ ]"):
            text = line.strip()[5:].strip()
            if check_duplicate(text, log_path):
                print(f"SKIP (duplicate): {text[:60]}...")
                lines[i] = line.replace("- [ ]", "- [SKIP-DUP]")
                with open(queue_path, "w") as f:
                    f.writelines(lines)
                continue
            tid = post(text)
            log_posted(tid, text, "queue", log_path)
            lines[i] = line.replace("- [ ]", f"- [x]").rstrip() + f" (ID: {tid})\n"
            with open(queue_path, "w") as f:
                f.writelines(lines)
            return
    print("No pending tweets in queue")

def get_mode(mode_path="twitter/MODE.md"):
    """Read posting mode: DRAFT or AUTO."""
    if os.path.exists(mode_path):
        return open(mode_path).read().strip().upper()
    return "DRAFT"

COMMANDS = {
    "post": lambda args: post(" ".join(args)),
    "thread": lambda args: thread(args),  # pipe JSON array or use post for auto-split
    "reply": lambda args: reply(args[0], " ".join(args[1:])),
    "quote": lambda args: quote(args[0], " ".join(args[1:])),
    "retweet": lambda args: retweet(args[0]),
    "delete": lambda args: delete(args[0]),
    "follow": lambda args: follow(args[0]),
    "unfollow": lambda args: unfollow(args[0]),
    "mentions": lambda args: mentions(int(args[0]) if args else 10),
    "me": lambda args: me(),
    "queue": lambda args: post_from_queue(args[0] if args else "twitter/queue.md"),
    "mode": lambda args: print(get_mode(args[0] if args else "twitter/MODE.md")),
    "check-dupe": lambda args: print("DUPLICATE" if check_duplicate(" ".join(args)) else "OK"),
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: tweet.py <{'|'.join(COMMANDS.keys())}> [args...]")
        sys.exit(1)
    try:
        COMMANDS[sys.argv[1]](sys.argv[2:])
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
