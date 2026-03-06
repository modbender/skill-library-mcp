#!/usr/bin/env python3
"""Hacker News CLI: login, submit, comment, edit, profile."""

import argparse
import re
import sys
import urllib.parse
import urllib.request
import http.cookiejar
import os
import json

COOKIE_FILE = os.environ.get("HN_COOKIE_FILE", os.path.expanduser("~/.hn_cookies.txt"))
BASE = "https://news.ycombinator.com"

def get_opener():
    jar = http.cookiejar.MozillaCookieJar(COOKIE_FILE)
    if os.path.exists(COOKIE_FILE):
        jar.load(ignore_discard=True, ignore_expires=True)
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(jar),
        urllib.request.HTTPRedirectHandler()
    )
    opener.addheaders = [("User-Agent", "Mozilla/5.0")]
    return opener, jar

def save_cookies(jar):
    jar.save(ignore_discard=True, ignore_expires=True)

def fetch(opener, url, data=None):
    if data:
        encoded = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=encoded, method="POST")
    else:
        req = urllib.request.Request(url)
    resp = opener.open(req)
    return resp.read().decode("utf-8", errors="replace")

def cmd_login(args):
    opener, jar = get_opener()
    username = args.username or os.environ.get("HN_USERNAME")
    password = args.password or os.environ.get("HN_PASSWORD")
    if not username or not password:
        print("error: provide --username/--password or set HN_USERNAME/HN_PASSWORD env vars", file=sys.stderr)
        sys.exit(1)
    html = fetch(opener, f"{BASE}/login", {"acct": username, "pw": password, "goto": "news"})
    if "Bad login" in html:
        print("error: login failed. check credentials.", file=sys.stderr)
        sys.exit(1)
    save_cookies(jar)
    print(json.dumps({"ok": True, "user": username}))

def cmd_submit(args):
    opener, jar = get_opener()
    html = fetch(opener, f"{BASE}/submit")
    fnid = re.search(r'name="fnid" value="([^"]+)"', html)
    if not fnid:
        print("error: not logged in or can't get submit form", file=sys.stderr)
        sys.exit(1)
    data = {
        "fnid": fnid.group(1),
        "fnop": "submit-page",
        "title": args.title,
        "url": args.url or "",
        "text": args.text or "",
    }
    html = fetch(opener, f"{BASE}/r", data)
    save_cookies(jar)
    match = re.search(r'item\?id=(\d+)', html)
    if match:
        item_id = match.group(1)
        print(json.dumps({"ok": True, "id": item_id, "url": f"{BASE}/item?id={item_id}"}))
    else:
        if "slow down" in html.lower() or "too fast" in html.lower():
            print("error: rate limited. try again later.", file=sys.stderr)
            sys.exit(1)
        print("error: submission may have failed. check your profile.", file=sys.stderr)
        sys.exit(1)

def cmd_comment(args):
    opener, jar = get_opener()
    html = fetch(opener, f"{BASE}/item?id={args.parent}")
    hmac = re.search(r'name="hmac" value="([^"]+)"', html)
    if not hmac:
        print("error: not logged in or can't find comment form", file=sys.stderr)
        sys.exit(1)
    data = {
        "parent": args.parent,
        "goto": f"item?id={args.parent}",
        "hmac": hmac.group(1),
        "text": args.text,
    }
    html = fetch(opener, f"{BASE}/comment", data)
    save_cookies(jar)
    if "slow down" in html.lower() or "too fast" in html.lower():
        print("error: rate limited. try again later.", file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"ok": True, "parent": args.parent}))

def cmd_edit(args):
    opener, jar = get_opener()
    html = fetch(opener, f"{BASE}/edit?id={args.id}")
    hmac = re.search(r'name="hmac" value="([^"]+)"', html)
    if not hmac:
        print("error: can't edit. not logged in or edit window expired.", file=sys.stderr)
        sys.exit(1)
    data = {
        "id": args.id,
        "hmac": hmac.group(1),
        "text": args.text,
    }
    html = fetch(opener, f"{BASE}/xedit", data)
    save_cookies(jar)
    print(json.dumps({"ok": True, "id": args.id}))

def cmd_profile(args):
    opener, jar = get_opener()
    html = fetch(opener, f"{BASE}/user?id={args.username}")
    hmac = re.search(r'name="hmac" value="([^"]+)"', html)
    if not hmac:
        print("error: can't update profile. not logged in or not your account.", file=sys.stderr)
        sys.exit(1)
    data = {
        "id": args.username,
        "hmac": hmac.group(1),
        "about": args.about,
    }
    html = fetch(opener, f"{BASE}/xuser", data)
    save_cookies(jar)
    print(json.dumps({"ok": True, "user": args.username}))

def main():
    p = argparse.ArgumentParser(description="hacker news cli")
    sub = p.add_subparsers(dest="cmd", required=True)

    login = sub.add_parser("login", help="log in to hn")
    login.add_argument("--username", "-u")
    login.add_argument("--password", "-p")

    submit = sub.add_parser("submit", help="submit a story")
    submit.add_argument("--title", "-t", required=True)
    submit.add_argument("--url")
    submit.add_argument("--text")

    comment = sub.add_parser("comment", help="comment on a story/comment")
    comment.add_argument("--parent", "-p", required=True, help="parent item id")
    comment.add_argument("--text", "-t", required=True)

    edit = sub.add_parser("edit", help="edit a comment")
    edit.add_argument("--id", required=True, help="comment id")
    edit.add_argument("--text", "-t", required=True)

    profile = sub.add_parser("profile", help="update profile about")
    profile.add_argument("--username", "-u", required=True)
    profile.add_argument("--about", "-a", required=True)

    args = p.parse_args()
    {"login": cmd_login, "submit": cmd_submit, "comment": cmd_comment, "edit": cmd_edit, "profile": cmd_profile}[args.cmd](args)

if __name__ == "__main__":
    main()
