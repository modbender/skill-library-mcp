#!/usr/bin/env python3
"""
X hot pipeline (MVP)
- Discover hot tweets from X API
- Enrich tweet text via FxTwitter
- Score/rank
- Summarize
- Generate one tweet draft
- Optionally publish with X API OAuth 1.0a

Requires Python stdlib only.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import random
import re
import string
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


X_API_BASE = "https://api.x.com"
X_SEARCH_ENDPOINT = f"{X_API_BASE}/2/tweets/search/recent"
X_POST_ENDPOINT = f"{X_API_BASE}/2/tweets"
X_ME_ENDPOINT = f"{X_API_BASE}/2/users/me"

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "for",
    "in",
    "on",
    "with",
    "is",
    "are",
    "was",
    "were",
    "be",
    "this",
    "that",
    "it",
    "as",
    "at",
    "by",
    "from",
    "about",
    "you",
    "your",
    "we",
    "our",
    "they",
    "their",
    "ai",
}


@dataclass
class Candidate:
    tweet_id: str
    url: str
    author_id: str
    author_username: str
    author_name: str
    author_verified: bool
    text: str
    created_at: str
    lang: str
    metrics: Dict[str, int]
    score: float = 0.0
    enriched: Optional[Dict[str, Any]] = None


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def request_json(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None,
    timeout: int = 20,
) -> Dict[str, Any]:
    if params:
        query = urllib.parse.urlencode(
            {k: v for k, v in params.items() if v is not None},
            doseq=True,
            quote_via=urllib.parse.quote,
        )
        url = f"{url}?{query}"

    payload = None
    req_headers = {"User-Agent": "kiro-x-hot-publisher/0.1"}
    if headers:
        req_headers.update(headers)

    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=payload, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body_text = ""
        try:
            raw = exc.read()
            body_text = raw.decode("utf-8", errors="replace") if raw else ""
        except Exception:
            body_text = ""

        detail = ""
        if body_text:
            try:
                payload = json.loads(body_text)
                detail = json.dumps(payload, ensure_ascii=False)
            except Exception:
                detail = body_text[:600]

        msg = f"HTTP {exc.code} {exc.reason} @ {url}"
        if detail:
            msg += f" | response={detail}"
        raise RuntimeError(msg) from exc


def parse_tweet_url(url: str) -> Tuple[str, str]:
    m = re.search(r"(?:x\.com|twitter\.com)/([A-Za-z0-9_]+)/status/(\d+)", url)
    if not m:
        raise ValueError(f"invalid tweet url: {url}")
    return m.group(1), m.group(2)


def enrich_with_fxtwitter(url: str) -> Dict[str, Any]:
    username, tweet_id = parse_tweet_url(url)
    api_url = f"https://api.fxtwitter.com/{username}/status/{tweet_id}"
    req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("code") != 200:
        raise RuntimeError(f"fxtwitter non-200: {data.get('code')}")
    return data.get("tweet", {})


def to_int(value: Any) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except Exception:
        return 0


def parse_created_at(created_at: str) -> float:
    if not created_at:
        return time.time()
    # X v2 returns ISO8601: 2026-02-21T09:00:00.000Z
    try:
        if created_at.endswith("Z"):
            created_at = created_at.replace("Z", "+00:00")
        return datetime.fromisoformat(created_at).timestamp()
    except Exception:
        return time.time()


def hours_since(ts: float) -> float:
    return max(0.0, (time.time() - ts) / 3600.0)


def score_candidate(c: Candidate) -> float:
    m = c.metrics
    likes = to_int(m.get("like_count"))
    rts = to_int(m.get("retweet_count"))
    replies = to_int(m.get("reply_count"))
    quotes = to_int(m.get("quote_count"))
    bookmarks = to_int(m.get("bookmark_count"))
    impressions = to_int(m.get("impression_count"))

    weighted = (
        likes
        + 2.2 * rts
        + 2.6 * replies
        + 2.0 * quotes
        + 1.2 * bookmarks
        + 0.0015 * impressions
    )

    age_h = hours_since(parse_created_at(c.created_at))
    velocity = weighted / ((age_h + 2.0) ** 0.85)
    author_boost = 1.1 if c.author_verified else 1.0
    text_boost = 1.05 if len(c.text.strip()) > 60 else 1.0
    return velocity * author_boost * text_boost


def is_cjk_text(text: str) -> bool:
    if not text:
        return False
    cjk = 0
    for ch in text:
        code = ord(ch)
        if 0x4E00 <= code <= 0x9FFF:
            cjk += 1
    return cjk >= 8


def extract_keywords(texts: Iterable[str], max_items: int = 6) -> List[str]:
    counts: Dict[str, int] = {}
    for text in texts:
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_\-]{2,}", text.lower()):
            if token in STOPWORDS:
                continue
            counts[token] = counts.get(token, 0) + 1
    return [k for k, _ in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:max_items]]


def summarize(candidates: List[Candidate]) -> Dict[str, Any]:
    texts = []
    for c in candidates:
        enriched_text = ""
        if c.enriched:
            enriched_text = str(c.enriched.get("text") or "")
            if c.enriched.get("article") and isinstance(c.enriched["article"], dict):
                enriched_text += " " + str(c.enriched["article"].get("title") or "")
        texts.append((enriched_text or c.text or "").strip())

    keywords = extract_keywords(texts)
    top = candidates[:3]
    top_urls = [c.url for c in top]

    avg_score = round(sum(c.score for c in candidates) / max(1, len(candidates)), 2)
    top_score = round(top[0].score, 2) if top else 0.0

    return {
        "keywords": keywords,
        "avg_score": avg_score,
        "top_score": top_score,
        "top_urls": top_urls,
    }


def build_draft(candidates: List[Candidate], summary: Dict[str, Any]) -> str:
    if not candidates:
        return "AI on X is unusually quiet today. Watch for fast-moving shifts in tools, benchmarks, and distribution."

    kws = summary.get("keywords") or []
    k1 = kws[0] if len(kws) > 0 else "AI"
    k2 = kws[1] if len(kws) > 1 else "agents"
    k3 = kws[2] if len(kws) > 2 else "build"

    top = candidates[0]
    base = f"X signal today: {k1}, {k2}, and {k3} are leading the conversation. The strongest pattern is execution > hype. Builders who ship fast, explain clearly, and iterate in public are winning attention."

    # If top content is mostly CJK, produce Chinese draft.
    top_text = (top.enriched or {}).get("text") if top.enriched else top.text
    if is_cjk_text(str(top_text or "")):
        base = f"今天 X 的热门信号：{k1}、{k2}、{k3}。高分内容共同点不是口号，而是可执行、可验证、可复用。谁能持续交付并公开迭代，谁就更容易获得关注。"

    # Keep tweet under 260 chars for safety.
    if len(base) > 260:
        base = base[:257].rstrip() + "..."
    return base


def oauth_percent_encode(value: str) -> str:
    return urllib.parse.quote(value, safe="~-._")


def build_oauth1_auth_header(
    method: str,
    url: str,
    query_or_body_params: Dict[str, Any],
    consumer_key: str,
    consumer_secret: str,
    token: str,
    token_secret: str,
) -> str:
    nonce = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
    timestamp = str(int(time.time()))

    oauth_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": nonce,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": timestamp,
        "oauth_token": token,
        "oauth_version": "1.0",
    }

    sig_params: List[Tuple[str, str]] = []
    for k, v in oauth_params.items():
        sig_params.append((oauth_percent_encode(k), oauth_percent_encode(str(v))))
    for k, v in query_or_body_params.items():
        if v is None:
            continue
        sig_params.append((oauth_percent_encode(str(k)), oauth_percent_encode(str(v))))

    sig_params.sort(key=lambda kv: (kv[0], kv[1]))
    param_str = "&".join(f"{k}={v}" for k, v in sig_params)

    base_elems = [
        method.upper(),
        oauth_percent_encode(url),
        oauth_percent_encode(param_str),
    ]
    base_str = "&".join(base_elems)

    signing_key = f"{oauth_percent_encode(consumer_secret)}&{oauth_percent_encode(token_secret)}"
    digest = hmac.new(signing_key.encode("utf-8"), base_str.encode("utf-8"), hashlib.sha1).digest()
    signature = base64.b64encode(digest).decode("utf-8")

    oauth_params["oauth_signature"] = signature

    header = "OAuth " + ", ".join(
        f'{oauth_percent_encode(k)}="{oauth_percent_encode(str(v))}"'
        for k, v in sorted(oauth_params.items(), key=lambda kv: kv[0])
    )
    return header


def post_tweet(text: str) -> Dict[str, Any]:
    api_key = (os.getenv("X_API_KEY") or "").strip()
    api_secret = (os.getenv("X_API_SECRET") or "").strip()
    access_token = (os.getenv("X_ACCESS_TOKEN") or "").strip()
    access_secret = (os.getenv("X_ACCESS_TOKEN_SECRET") or "").strip()

    missing = [
        name
        for name, value in [
            ("X_API_KEY", api_key),
            ("X_API_SECRET", api_secret),
            ("X_ACCESS_TOKEN", access_token),
            ("X_ACCESS_TOKEN_SECRET", access_secret),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(f"missing env vars for post: {', '.join(missing)}")

    body = {"text": text}
    auth_header = build_oauth1_auth_header(
        method="POST",
        url=X_POST_ENDPOINT,
        query_or_body_params=body,
        consumer_key=api_key,
        consumer_secret=api_secret,
        token=access_token,
        token_secret=access_secret,
    )

    return request_json(
        method="POST",
        url=X_POST_ENDPOINT,
        headers={"Authorization": auth_header},
        body=body,
    )


def probe_write_auth() -> Dict[str, Any]:
    api_key = (os.getenv("X_API_KEY") or "").strip()
    api_secret = (os.getenv("X_API_SECRET") or "").strip()
    access_token = (os.getenv("X_ACCESS_TOKEN") or "").strip()
    access_secret = (os.getenv("X_ACCESS_TOKEN_SECRET") or "").strip()

    auth_header = build_oauth1_auth_header(
        method="GET",
        url=X_ME_ENDPOINT,
        query_or_body_params={},
        consumer_key=api_key,
        consumer_secret=api_secret,
        token=access_token,
        token_secret=access_secret,
    )

    return request_json(
        method="GET",
        url=X_ME_ENDPOINT,
        headers={"Authorization": auth_header},
    )


def discover_candidates(
    queries: List[str],
    max_results_per_query: int,
    hours_window: int,
    lang: str,
) -> List[Candidate]:
    bearer = (os.getenv("X_BEARER_TOKEN") or "").strip()
    if not bearer:
        raise RuntimeError("X_BEARER_TOKEN is required for search discovery")

    all_candidates: Dict[str, Candidate] = {}

    for raw_query in queries:
        q = raw_query.strip()
        if not q:
            continue

        query_parts = [q, "-is:retweet", "-is:reply"]
        if lang and lang != "any":
            query_parts.append(f"lang:{lang}")
        query_text = " ".join(query_parts)

        params = {
            "query": query_text,
            "max_results": max(10, min(100, max_results_per_query)),
            "tweet.fields": "created_at,public_metrics,lang,author_id",
            "user.fields": "name,username,verified",
            "expansions": "author_id",
        }

        payload = request_json(
            method="GET",
            url=X_SEARCH_ENDPOINT,
            headers={"Authorization": f"Bearer {bearer}"},
            params=params,
        )

        users = {u.get("id"): u for u in payload.get("includes", {}).get("users", [])}
        tweets = payload.get("data", [])

        cutoff = time.time() - (hours_window * 3600)

        for t in tweets:
            created_at = str(t.get("created_at") or "")
            if parse_created_at(created_at) < cutoff:
                continue

            tid = str(t.get("id") or "")
            aid = str(t.get("author_id") or "")
            if not tid or not aid:
                continue

            user = users.get(aid, {})
            username = str(user.get("username") or "unknown")

            candidate = Candidate(
                tweet_id=tid,
                url=f"https://x.com/{username}/status/{tid}",
                author_id=aid,
                author_username=username,
                author_name=str(user.get("name") or ""),
                author_verified=bool(user.get("verified")),
                text=str(t.get("text") or ""),
                created_at=created_at,
                lang=str(t.get("lang") or ""),
                metrics=dict(t.get("public_metrics") or {}),
            )
            candidate.score = score_candidate(candidate)

            prev = all_candidates.get(tid)
            if prev is None or candidate.score > prev.score:
                all_candidates[tid] = candidate

    return list(all_candidates.values())


def enrich_candidates(candidates: List[Candidate]) -> None:
    for c in candidates:
        try:
            c.enriched = enrich_with_fxtwitter(c.url)
        except Exception:
            c.enriched = None


def save_outputs(out_dir: Path, result: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "latest.json"
    txt_path = out_dir / "latest.txt"

    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append(f"Generated at: {result.get('generated_at')}")
    lines.append(f"Queries: {', '.join(result.get('queries', []))}")
    lines.append("")
    lines.append("Top signals:")
    s = result.get("summary", {})
    lines.append(f"- Keywords: {', '.join(s.get('keywords', []))}")
    lines.append(f"- Avg score: {s.get('avg_score')}")
    lines.append(f"- Top score: {s.get('top_score')}")
    lines.append("")
    lines.append("Final tweet draft:")
    lines.append(result.get("draft", ""))
    lines.append("")
    lines.append("Top URLs:")
    for url in s.get("top_urls", []):
        lines.append(f"- {url}")

    txt_path.write_text("\n".join(lines), encoding="utf-8")


def parse_queries(raw: str) -> List[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="X hot discovery -> analysis -> one tweet draft")
    parser.add_argument(
        "--queries",
        default="AI,OpenAI,DeepSeek,Claude,Gemini",
        help="Comma-separated search queries",
    )
    parser.add_argument("--batch-size", type=int, default=10, help="Final ranked batch size")
    parser.add_argument(
        "--max-results-per-query",
        type=int,
        default=30,
        help="X API fetch size per query (10..100)",
    )
    parser.add_argument("--hours-window", type=int, default=24, help="Keep tweets within N hours")
    parser.add_argument("--lang", default="any", help="Language filter, e.g. en/zh/ja, or any")
    parser.add_argument("--out-dir", default="outputs/x-hot", help="Output folder")
    parser.add_argument(
        "--draft-text",
        default=None,
        help="Override the generated tweet draft with this exact text",
    )
    parser.add_argument("--post", action="store_true", help="Post generated draft to X")

    args = parser.parse_args()

    queries = parse_queries(args.queries)
    if not queries:
        raise SystemExit("no queries provided")

    candidates = discover_candidates(
        queries=queries,
        max_results_per_query=args.max_results_per_query,
        hours_window=args.hours_window,
        lang=args.lang,
    )

    candidates.sort(key=lambda c: c.score, reverse=True)
    candidates = candidates[: max(1, args.batch_size)]

    enrich_candidates(candidates)

    summary = summarize(candidates)
    draft = build_draft(candidates, summary)

    # Allow overriding the generated draft (useful for book-specific messaging)
    if args.draft_text is not None and str(args.draft_text).strip():
        draft = str(args.draft_text).strip()

    auth_probe: Optional[Dict[str, Any]] = None
    auth_probe_error: Optional[str] = None
    post_result: Optional[Dict[str, Any]] = None
    post_error: Optional[str] = None
    if args.post:
        try:
            auth_probe = probe_write_auth()
        except Exception as exc:
            auth_probe_error = str(exc)
        try:
            post_result = post_tweet(draft)
        except Exception as exc:
            post_error = str(exc)

    result: Dict[str, Any] = {
        "generated_at": now_utc_iso(),
        "queries": queries,
        "batch_size": args.batch_size,
        "summary": summary,
        "draft": draft,
        "auth_probe": auth_probe,
        "auth_probe_error": auth_probe_error,
        "posted": bool(post_result and not post_error),
        "post_result": post_result,
        "post_error": post_error,
        "candidates": [
            {
                "tweet_id": c.tweet_id,
                "url": c.url,
                "author_username": c.author_username,
                "author_name": c.author_name,
                "author_verified": c.author_verified,
                "created_at": c.created_at,
                "lang": c.lang,
                "score": round(c.score, 4),
                "metrics": c.metrics,
                "text": c.text,
                "enriched": c.enriched,
            }
            for c in candidates
        ],
    }

    save_outputs(Path(args.out_dir), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
