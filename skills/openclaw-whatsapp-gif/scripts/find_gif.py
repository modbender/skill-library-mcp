#!/usr/bin/env python3
import argparse
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_BLOCKLIST = {
    "nsfw", "sex", "nude", "naked", "porn", "hentai", "gore", "blood", "kill", "hate"
}

DEFAULT_ALLOWED_HOSTS = {
    "media.giphy.com",
    "i.giphy.com",
    "media.tenor.com",
    "media1.tenor.com",
    "tenor.com",
}

INTENT_ALIASES = {
    "congrats": ["congrats", "congratulations", "celebration", "great job", "well done", "awesome"],
    "thanks": ["thanks", "thank you", "appreciate", "grateful"],
    "laugh": ["lol", "haha", "funny", "laugh"],
    "ack": ["ok", "got it", "noted", "done", "copy that"],
    "sorry": ["sorry", "apology", "my bad", "oops"],
    "love": ["love", "heart", "adorable", "cute"],
}

FALLBACK_CATALOG = [
    {"tags": ["congrats", "celebration", "great", "nice", "win", "awesome", "well", "done"], "provider": "catalog", "title": "Celebration confetti", "gif": "https://media.giphy.com/media/26u4cqiYI30juCOGY/giphy.gif", "mp4": "https://media.giphy.com/media/26u4cqiYI30juCOGY/giphy.mp4"},
    {"tags": ["thanks", "thank", "appreciate", "grateful"], "provider": "catalog", "title": "Thank you reaction", "gif": "https://media.giphy.com/media/3oEdva9BUHPIs2SkGk/giphy.gif", "mp4": "https://media.giphy.com/media/3oEdva9BUHPIs2SkGk/giphy.mp4"},
    {"tags": ["lol", "haha", "funny", "laugh"], "provider": "catalog", "title": "Laugh reaction", "gif": "https://media.giphy.com/media/10JhviFuU2gWD6/giphy.gif", "mp4": "https://media.giphy.com/media/10JhviFuU2gWD6/giphy.mp4"},
    {"tags": ["ok", "got", "ack", "noted", "done"], "provider": "catalog", "title": "Thumbs up", "gif": "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif", "mp4": "https://media.giphy.com/media/111ebonMs90YLu/giphy.mp4"},
    {"tags": ["sorry", "apology", "my", "bad", "oops"], "provider": "catalog", "title": "Sorry reaction", "gif": "https://media.giphy.com/media/l378giAZgxPw3eO52/giphy.gif", "mp4": "https://media.giphy.com/media/l378giAZgxPw3eO52/giphy.mp4"},
    {"tags": ["love", "heart", "cute", "adorable"], "provider": "catalog", "title": "Love reaction", "gif": "https://media.giphy.com/media/3oriO0OEd9QIDdllqo/giphy.gif", "mp4": "https://media.giphy.com/media/3oriO0OEd9QIDdllqo/giphy.mp4"},
]


def load_policy(script_dir: Path):
    path = script_dir.parent / "references" / "policy.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def http_get_json(url: str, retries: int = 3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "openclaw-whatsapp-gif/1.5"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            last = e
            time.sleep(0.6 * (i + 1))
    raise last


def http_get_text(url: str, retries: int = 3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "openclaw-whatsapp-gif/1.5"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.read().decode("utf-8", "ignore")
        except Exception as e:
            last = e
            time.sleep(0.6 * (i + 1))
    raise last


def tokenize(text: str):
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def normalize_allowed_hosts(value):
    if not isinstance(value, list):
        return set(DEFAULT_ALLOWED_HOSTS)
    hosts = set()
    for raw in value:
        if not isinstance(raw, str):
            continue
        host = raw.strip().lower()
        if host:
            hosts.add(host)
    return hosts or set(DEFAULT_ALLOWED_HOSTS)


def is_allowed_host(url: str, allowed_hosts):
    host = urllib.parse.urlparse(url).netloc.lower().split(":")[0]
    if not host:
        return False
    for allowed in allowed_hosts:
        if host == allowed or host.endswith("." + allowed):
            return True
    return False


def safe_text(text: str, blocklist):
    t = (text or "").lower()
    return not any(b in t for b in blocklist)


def expand_query(query: str) -> str:
    q_tokens = tokenize(query)
    expanded = [query.strip()]
    for aliases in INTENT_ALIASES.values():
        alias_tokens = set()
        for a in aliases:
            alias_tokens |= tokenize(a)
        if q_tokens & alias_tokens:
            expanded.extend(aliases[:3])
    seen, ordered = set(), []
    for part in expanded:
        k = part.lower()
        if k in seen:
            continue
        seen.add(k)
        ordered.append(part)
    return " ".join(ordered)


def compact_query(query: str, max_tokens: int = 6, max_chars: int = 80) -> str:
    """Keep provider API query short to avoid 414 URI Too Long."""
    tokens = re.findall(r"[a-z0-9]+", (query or "").lower())[:max_tokens]
    q = " ".join(tokens).strip()
    return q[:max_chars] if len(q) > max_chars else q


def score_candidate(query: str, title: str, size_hint: int = 0):
    overlap = len(tokenize(query) & tokenize(title))
    size_bonus = 2 if 0 < size_hint < 3_000_000 else 0
    return overlap * 10 + size_bonus


def search_tenor(query: str, limit: int, blocklist, allowed_hosts):
    key = os.getenv("TENOR_API_KEY")
    if not key:
        return []
    params = {"key": key, "q": compact_query(expand_query(query)), "limit": str(limit), "media_filter": "minimal", "contentfilter": "low"}
    try:
        data = http_get_json("https://tenor.googleapis.com/v2/search?" + urllib.parse.urlencode(params))
    except Exception:
        return []
    out = []
    for r in data.get("results", []):
        title = r.get("content_description") or r.get("title") or ""
        if not safe_text(title, blocklist):
            continue
        media_formats = r.get("media_formats", {})
        pick = media_formats.get("mp4") or media_formats.get("tinygif") or media_formats.get("gif") or {}
        u = pick.get("url")
        if not u:
            continue
        if not is_allowed_host(u, allowed_hosts):
            continue
        out.append({"provider": "tenor", "url": u, "preview": (media_formats.get("tinygif") or {}).get("url") or u, "title": title, "score": score_candidate(query, title, int(pick.get("size") or 0))})
    return out


def search_giphy(query: str, limit: int, blocklist, allowed_hosts):
    key = os.getenv("GIPHY_API_KEY")
    if not key:
        return []
    params = {"api_key": key, "q": compact_query(expand_query(query)), "limit": str(limit), "rating": "g", "lang": "en"}
    try:
        data = http_get_json("https://api.giphy.com/v1/gifs/search?" + urllib.parse.urlencode(params))
    except Exception:
        return []
    out = []
    for r in data.get("data", []):
        title = r.get("title") or ""
        if not safe_text(title, blocklist):
            continue
        images = r.get("images", {})
        mp4 = images.get("downsized_small", {}).get("mp4")
        pick = images.get("downsized_medium") or images.get("original") or images.get("fixed_height") or {}
        u = mp4 or pick.get("url")
        if not u:
            continue
        if not is_allowed_host(u, allowed_hosts):
            continue
        size_hint = int((pick.get("size") or "0").strip() or "0") if isinstance(pick.get("size"), str) else 0
        out.append({"provider": "giphy", "url": u, "preview": (images.get("fixed_width_small_still") or {}).get("url") or u, "title": title, "score": score_candidate(query, title, size_hint)})
    return out


def search_tenor_web(query: str, limit: int, allowed_hosts):
    try:
        html = http_get_text(f"https://tenor.com/search/{urllib.parse.quote(query.strip().replace(' ', '-'))}-gifs")
    except Exception:
        return []
    urls = re.findall(r"https://media[^\"']+?\.(?:mp4|gif)", html)
    seen, out = set(), []
    for u in urls:
        if u in seen:
            continue
        if not is_allowed_host(u, allowed_hosts):
            continue
        seen.add(u)
        out.append({"provider": "tenor-web", "url": u, "preview": u, "title": query, "score": 8 if u.lower().endswith(".mp4") else 6})
        if len(out) >= limit:
            break
    return out


def search_catalog(query: str, limit: int, prefer_mp4=True, allowed_hosts=None):
    q_tokens = tokenize(query)
    out = []
    allowed_hosts = allowed_hosts or set(DEFAULT_ALLOWED_HOSTS)
    for item in FALLBACK_CATALOG:
        overlap = len(q_tokens & set(item["tags"]))
        if overlap == 0:
            continue
        url = item.get("mp4") if prefer_mp4 else item.get("gif")
        final_url = url or item.get("gif") or item.get("mp4")
        if not final_url or not is_allowed_host(final_url, allowed_hosts):
            continue
        out.append({"provider": item["provider"], "url": url or item.get("gif") or item.get("mp4"), "preview": item.get("gif") or item.get("mp4"), "title": item["title"], "score": overlap * 10})
    if not out:
        fallback_url = "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.mp4"
        fallback_preview = "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif"
        if is_allowed_host(fallback_url, allowed_hosts):
            out.append({"provider": "catalog", "url": fallback_url, "preview": fallback_preview, "title": "Generic positive reaction", "score": 1})
    return out[:limit]


def dedupe_by_url(items):
    seen, out = set(), []
    for i in items:
        u = i.get("url")
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(i)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--json", action="store_true")
    p.add_argument("--target")
    args = p.parse_args()

    policy = load_policy(Path(__file__).resolve().parent)
    blocklist = set(policy.get("blockedKeywords", [])) or DEFAULT_BLOCKLIST
    prefer_mp4 = bool(policy.get("preferMp4", True))
    allow_web_scrape = bool(policy.get("allowWebScrapeFallback", False))
    allowed_hosts = normalize_allowed_hosts(policy.get("allowedMediaHosts"))
    limit = min(args.limit, int(policy.get("maxCandidates", 8)))

    results = []
    results += search_tenor(args.query, limit, blocklist, allowed_hosts)
    results += search_giphy(args.query, limit, blocklist, allowed_hosts)
    if not results and allow_web_scrape:
        results += search_tenor_web(args.query, limit, allowed_hosts)
    if not results:
        results += search_catalog(args.query, limit, prefer_mp4, allowed_hosts)

    results = sorted(dedupe_by_url(results), key=lambda x: x.get("score", 0), reverse=True)[:limit]

    if args.json:
        if args.target:
            payload = {"action": "send", "channel": "whatsapp", "target": args.target, "media": results[0]["url"], "gifPlayback": True, "caption": ""}
            print(json.dumps({"candidates": results, "messagePayload": payload}, indent=2))
        else:
            print(json.dumps(results, indent=2))
    else:
        print(results[0]["url"])


if __name__ == "__main__":
    main()
