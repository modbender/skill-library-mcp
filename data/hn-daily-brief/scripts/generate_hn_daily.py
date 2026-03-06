#!/usr/bin/env python3
import argparse
import datetime as dt
import html
import json
import re
import urllib.request
from pathlib import Path

HN = "https://hacker-news.firebaseio.com/v0"

ZH_SUMMARY_MIN_CHARS = 300
ZH_COMMENT_MIN_CHARS = 80
SHORT_SOURCE_MARKER = "source is short / info limited"


def get_json(url: str):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)


def item(item_id: int):
    return get_json(f"{HN}/item/{item_id}.json")


def clean_html(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<p>|</p>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_article_snippet(url: str, max_chars: int = 2500) -> str:
    if not url:
        return ""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read(300_000).decode("utf-8", errors="ignore")
    except Exception:
        return ""

    raw = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.I)
    raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.I)
    txt = re.sub(r"<[^>]+>", " ", raw)
    txt = html.unescape(txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    if len(txt) < 150:
        return ""
    return txt[:max_chars]


def collect_comments(story: dict, limit=20):
    kids = story.get("kids") or []
    out = []
    queue = list(kids[:80])
    seen = set()
    while queue and len(out) < limit:
        cid = queue.pop(0)
        if cid in seen:
            continue
        seen.add(cid)
        try:
            c = item(cid)
        except Exception:
            continue
        if not c or c.get("deleted") or c.get("dead"):
            continue
        txt = clean_html(c.get("text", ""))
        if len(txt) >= 40:
            out.append(
                {
                    "id": c.get("id"),
                    "user": c.get("by") or "unknown",
                    "time": c.get("time"),
                    "text": txt,
                }
            )
        for k in (c.get("kids") or [])[:3]:
            if len(queue) < 200:
                queue.append(k)
    return out


def collect_materials(top_n: int, style: str = "strict", lang: str = "zh"):
    window = max(top_n * 10, 100)
    ids = get_json(f"{HN}/topstories.json")[:window]
    stories = [item(i) for i in ids]
    stories = [s for s in stories if isinstance(s, dict) and s.get("title")]
    stories.sort(key=lambda s: s.get("score", 0), reverse=True)
    stories = stories[:top_n]

    comments_limit = 24 if style == "strict" else 12
    items = []
    for idx, st in enumerate(stories, 1):
        sid = st["id"]
        url = st.get("url") or f"https://news.ycombinator.com/item?id={sid}"
        snippet = fetch_article_snippet(url)
        comments_raw = collect_comments(st, limit=comments_limit)
        items.append(
            {
                "rank": idx,
                "id": sid,
                "title": st.get("title", "(no title)"),
                "url": url,
                "hn_url": f"https://news.ycombinator.com/item?id={sid}",
                "score": st.get("score", 0),
                "comments": st.get("descendants", 0),
                "by": st.get("by"),
                "time": st.get("time"),
                "snippet": snippet,
                "source_short": len(snippet) < 150,
                "comments_raw": comments_raw,
                "comments_short": len(comments_raw) == 0,
            }
        )

    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    date = now.strftime("%Y-%m-%d")
    return date, items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--style", choices=["strict", "lite"], default="strict")
    parser.add_argument("--language", default="zh")
    parser.add_argument("--materials", default="", help="write structured materials JSON for mandatory LLM rewrite")
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    date, items = collect_materials(args.top, style=args.style, lang=args.language)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    materials_path = Path(args.materials) if args.materials else (outdir / f"HN-materials-{date}.json")

    materials_path.write_text(
        json.dumps(
            {
                "date": date,
                "generated_at": dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(),
                "timezone": "Asia/Shanghai",
                "language": args.language,
                "style": args.style,
                "requirements": {
                    "zh_summary_min_chars": ZH_SUMMARY_MIN_CHARS,
                    "zh_comment_min_chars": ZH_COMMENT_MIN_CHARS,
                    "short_source_marker": SHORT_SOURCE_MARKER,
                    "comment_viewpoints_target": 5,
                },
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(materials_path)


if __name__ == "__main__":
    main()
