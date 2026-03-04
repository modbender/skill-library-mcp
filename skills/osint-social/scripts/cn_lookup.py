#!/usr/bin/env python3
"""
cn_lookup.py — Chinese platform username lookup for osint-social skill
Covers: Bilibili, Zhihu, Weibo (degraded)
Usage: python3 cn_lookup.py <username>
"""

import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error

USERNAME = sys.argv[1] if len(sys.argv) > 1 else ""

if not USERNAME:
    print("Usage: python3 cn_lookup.py <username>")
    sys.exit(1)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.bilibili.com/",
}

results = []

def fetch(url, extra_headers=None):
    headers = dict(HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return None


# ─── Bilibili ────────────────────────────────────────────────────────────────
def check_bilibili(username):
    """Search Bilibili for username, return matched user info if found."""
    url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=bili_user&keyword={urllib.parse.quote(username)}"
    data = fetch(url, {"Referer": "https://search.bilibili.com/"})

    if not data or data.get("code") != 0:
        return None

    items = data.get("data", {}).get("result", [])
    if not items:
        return None

    # Look for exact username match first, then close match
    exact = next((u for u in items if u.get("uname", "").lower() == username.lower()), None)
    best = exact or items[0]

    return {
        "platform": "Bilibili (哔哩哔哩)",
        "url": f"https://space.bilibili.com/{best.get('mid', '')}",
        "username": best.get("uname", ""),
        "fans": best.get("fans", 0),
        "videos": best.get("videos", 0),
        "bio": best.get("usign", ""),
        "avatar": best.get("upic", ""),
        "exact_match": exact is not None,
        "rate": 95 if exact else 60,
    }


# ─── Zhihu ────────────────────────────────────────────────────────────────────
def check_zhihu(username):
    """Search Zhihu for username via public search API."""
    url = f"https://www.zhihu.com/api/v4/search_v3?t=people&q={urllib.parse.quote(username)}&limit=5"
    data = fetch(url, {
        "Referer": "https://www.zhihu.com/search",
        "x-requested-with": "fetch",
    })

    if not data:
        return None

    items = data.get("data", [])
    if not items:
        return None

    for item in items:
        obj = item.get("object", {})
        url_token = obj.get("url_token", "")
        name = obj.get("name", "")

        if url_token.lower() == username.lower() or name.lower() == username.lower():
            return {
                "platform": "知乎 Zhihu",
                "url": f"https://www.zhihu.com/people/{url_token}",
                "username": name,
                "url_token": url_token,
                "followers": obj.get("follower_count", 0),
                "bio": obj.get("headline", ""),
                "rate": 92,
                "exact_match": True,
            }

    # No exact match but found similar
    first = items[0].get("object", {})
    url_token = first.get("url_token", "")
    return {
        "platform": "知乎 Zhihu",
        "url": f"https://www.zhihu.com/people/{url_token}",
        "username": first.get("name", ""),
        "url_token": url_token,
        "followers": first.get("follower_count", 0),
        "bio": first.get("headline", ""),
        "rate": 55,
        "exact_match": False,
    }


# ─── Weibo ────────────────────────────────────────────────────────────────────
def check_weibo(username):
    """Check Weibo via mobile search - degraded, existence check only."""
    url = f"https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D3%26q%3D{urllib.parse.quote(username)}&page_type=searchall"
    data = fetch(url, {"Referer": "https://m.weibo.cn/"})

    if not data or data.get("ok") != 1:
        return None

    cards = data.get("data", {}).get("cards", [])
    for card in cards:
        for card_group in card.get("card_group", []):
            user = card_group.get("user", {})
            screen_name = user.get("screen_name", "")
            if screen_name.lower() == username.lower():
                uid = user.get("id", "")
                return {
                    "platform": "微博 Weibo",
                    "url": f"https://weibo.com/u/{uid}" if uid else f"https://weibo.com/search?q={username}",
                    "username": screen_name,
                    "followers": user.get("followers_count", 0),
                    "bio": user.get("description", ""),
                    "verified": user.get("verified", False),
                    "rate": 88,
                    "exact_match": True,
                }

    # Existence uncertain but something was found
    return {
        "platform": "微博 Weibo",
        "url": f"https://s.weibo.com/user?q={urllib.parse.quote(username)}",
        "username": username,
        "note": "搜索结果存在，但未找到精确匹配，请手动确认",
        "rate": 40,
        "exact_match": False,
    }


# ─── Run all checks ───────────────────────────────────────────────────────────
print(f"\n[*] 正在查询国内平台用户名: {USERNAME}\n")

checks = [
    ("Bilibili", check_bilibili),
    ("Zhihu", check_zhihu),
    ("Weibo", check_weibo),
]

found = []
for name, fn in checks:
    print(f"  → 查询 {name}...", end=" ", flush=True)
    try:
        result = fn(USERNAME)
        if result:
            found.append(result)
            status = "✅ 找到" if result.get("exact_match") else "⚠️  疑似"
            print(status)
        else:
            print("❌ 未找到")
    except Exception as e:
        print(f"⚠️  请求失败 ({e})")
    time.sleep(0.5)  # polite delay

# ─── Output ───────────────────────────────────────────────────────────────────
print(f"\n{'─'*50}")
if not found:
    print(f"在国内平台未找到用户名 [{USERNAME}] 的公开账号。")
else:
    print(f"共找到 {len(found)} 个国内平台账号：\n")
    for r in sorted(found, key=lambda x: x.get("rate", 0), reverse=True):
        rate = r.get("rate", "?")
        plat = r["platform"]
        url = r["url"]
        uname = r.get("username", "")
        bio = r.get("bio", "")
        followers = r.get("followers", "")
        exact = "✅ 精确匹配" if r.get("exact_match") else "⚠️ 近似匹配"

        print(f"[{rate:>3}] {plat} — {exact}")
        print(f"      URL: {url}")
        if uname and uname != USERNAME:
            print(f"      显示名: {uname}")
        if followers:
            print(f"      粉丝/关注者: {followers}")
        if bio:
            print(f"      简介: {bio[:80]}")
        print()

print("⚠️  以上均为公开信息，请合法合理使用。")
print(f"{'─'*50}\n")
