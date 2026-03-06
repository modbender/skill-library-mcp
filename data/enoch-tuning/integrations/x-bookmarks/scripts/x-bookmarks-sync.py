#!/usr/bin/env python3
"""X bookmarks sync — pulls bookmarks, detects new ones, writes trigger file for research pipeline."""
import json, os, requests, sys
from datetime import datetime

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CREDS_DIR = os.path.join(os.path.expanduser("~"), ".openclaw", "credentials")
TOKEN_FILE = os.path.join(CREDS_DIR, "x-oauth-token.json")
CREDS_FILE = os.path.join(CREDS_DIR, "x-oauth-creds.json")
RAW_FILE = os.path.join(WORKSPACE, "research/x-bookmarks-raw.json")
MD_FILE = os.path.join(WORKSPACE, "research/x-bookmarks_latest.md")
NEW_FILE = os.path.join(WORKSPACE, "research/x-bookmarks-new.json")

def refresh_token():
    """Refresh the OAuth 2.0 access token using the refresh token."""
    with open(TOKEN_FILE) as f:
        token = json.load(f)
    with open(CREDS_FILE) as f:
        creds = json.load(f)

    import base64
    auth = base64.b64encode(f'{creds["client_id"]}:{creds["client_secret"]}'.encode()).decode()
    resp = requests.post("https://api.x.com/2/oauth2/token",
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
            "client_id": creds["client_id"]
        })

    if resp.status_code != 200:
        print(f"Token refresh failed: {resp.status_code} {resp.text}")
        sys.exit(1)

    new_token = resp.json()
    with open(TOKEN_FILE, "w") as f:
        json.dump(new_token, f, indent=2)
    print("Token refreshed successfully")
    return new_token

def fetch_bookmarks(token):
    """Fetch all bookmarks."""
    headers = {"Authorization": f'Bearer {token["access_token"]}'}

    # Get user ID
    r = requests.get("https://api.x.com/2/users/me", headers=headers)
    if r.status_code == 401:
        token = refresh_token()
        headers = {"Authorization": f'Bearer {token["access_token"]}'}
        r = requests.get("https://api.x.com/2/users/me", headers=headers)

    if r.status_code != 200:
        print(f"Failed to get user: {r.status_code} {r.text}")
        sys.exit(1)

    user_id = r.json()["data"]["id"]
    all_bookmarks = []
    pagination_token = None

    while True:
        url = f"https://api.x.com/2/users/{user_id}/bookmarks?max_results=100&tweet.fields=text,author_id,created_at&expansions=author_id&user.fields=username,name"
        if pagination_token:
            url += f"&pagination_token={pagination_token}"

        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print(f"Bookmarks error: {r.status_code} {r.text}")
            break

        data = r.json()
        users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}

        for tweet in data.get("data", []):
            author = users.get(tweet["author_id"], {})
            all_bookmarks.append({
                "text": tweet["text"],
                "author": author.get("name", ""),
                "username": author.get("username", ""),
                "created_at": tweet.get("created_at", ""),
                "id": tweet["id"],
                "article_title": tweet.get("article", {}).get("title", "")
            })

        pagination_token = data.get("meta", {}).get("next_token")
        if not pagination_token:
            break

    return all_bookmarks

def main():
    detect_new = "--detect-new" in sys.argv

    with open(TOKEN_FILE) as f:
        token = json.load(f)

    # Load existing
    existing_ids = set()
    if os.path.exists(RAW_FILE):
        with open(RAW_FILE) as f:
            existing = json.load(f)
            existing_ids = {b["id"] for b in existing}
    else:
        existing = []

    # Fetch current
    bookmarks = fetch_bookmarks(token)
    new_bookmarks = [b for b in bookmarks if b["id"] not in existing_ids]
    removed_ids = existing_ids - {b["id"] for b in bookmarks}

    print(f"Total: {len(bookmarks)} | New: {len(new_bookmarks)} | Removed: {len(removed_ids)}")

    # Save raw (full replace with current state)
    with open(RAW_FILE, "w") as f:
        json.dump(bookmarks, f, indent=2)

    # Save markdown
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(MD_FILE, "w") as f:
        f.write(f"# X Bookmarks\n\nLast sync: {now} | Total: {len(bookmarks)}\n\n")
        for b in bookmarks:
            author = f'@{b["username"]}' if b["username"] else "unknown"
            title = f' — {b["article_title"]}' if b["article_title"] else ""
            f.write(f"### {author}{title}\n")
            f.write(f'*{b["created_at"][:10]}* | https://x.com/{b["username"]}/status/{b["id"]}\n\n')
            f.write(f'{b["text"]}\n\n---\n\n')

    # Write trigger file for research pipeline (--detect-new mode)
    if detect_new:
        trigger_data = []
        for b in new_bookmarks:
            trigger_data.append({
                "id": b["id"],
                "text": b["text"],
                "author": b.get("author", ""),
                "username": b.get("username", ""),
                "url": f'https://x.com/{b["username"]}/status/{b["id"]}',
                "article_title": b.get("article_title", ""),
                "created_at": b.get("created_at", "")
            })
        with open(NEW_FILE, "w") as f:
            json.dump(trigger_data, f, indent=2)

        if new_bookmarks:
            print(f"\nWrote {len(new_bookmarks)} new bookmarks to trigger file")
        else:
            print("\nNo new bookmarks — trigger file is empty")
        sys.exit(0)

    # Legacy mode: just report
    if new_bookmarks:
        print("\n=== NEW BOOKMARKS ===")
        for b in new_bookmarks:
            print(f"  @{b['username']}: {b['text'][:80]}...")

    if removed_ids:
        print(f"\n{len(removed_ids)} bookmarks were removed since last sync")

if __name__ == "__main__":
    main()
