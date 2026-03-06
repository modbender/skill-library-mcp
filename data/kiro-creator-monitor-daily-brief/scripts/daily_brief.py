#!/usr/bin/env python3
# Plugin producer: kiroai.io
"""Creator monitor daily brief (MVP).

Sources: X, RSS, GitHub, Reddit
Pipeline: ingest -> dedupe -> score -> top 5 brief + social draft -> optional delivery
"""

from __future__ import annotations

import argparse
import datetime as dt
import email.message
import hashlib
import json
import os
import re
import smtplib
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any


UA = "kiro-creator-brief/0.1 (+https://kiroai.io)"


@dataclass
class Item:
    source: str
    title: str
    url: str
    snippet: str
    published_at: str
    score: float = 0.0


def http_json(url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def http_text(url: str, headers: dict[str, str] | None = None) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def parse_rfc3339(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    s = s.strip().replace("Z", "+00:00")
    try:
        return dt.datetime.fromisoformat(s)
    except ValueError:
        return None


def parse_rfc822(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    try:
        from email.utils import parsedate_to_datetime

        out = parsedate_to_datetime(s)
        return out if out.tzinfo else out.replace(tzinfo=dt.timezone.utc)
    except Exception:
        return None


def fetch_x(cfg: dict[str, Any]) -> list[Item]:
    if not cfg.get("enabled"):
        return []
    token = os.getenv("X_BEARER_TOKEN", "").strip()
    if not token:
        return []
    per_query = int(cfg.get("per_query", 20))
    out: list[Item] = []
    headers = {"Authorization": f"Bearer {token}"}
    for q in cfg.get("queries", []):
        params = {
            "query": q,
            "max_results": str(max(10, min(per_query, 100))),
            "tweet.fields": "created_at,public_metrics,lang",
            "expansions": "author_id",
        }
        url = f"https://api.x.com/2/tweets/search/recent?{urllib.parse.urlencode(params)}"
        try:
            data = http_json(url, headers=headers)
        except Exception:
            continue
        for t in data.get("data", []) or []:
            tid = t.get("id", "")
            text = (t.get("text") or "").strip()
            if not tid or not text:
                continue
            out.append(
                Item(
                    source="x",
                    title=(text[:120] + "...") if len(text) > 120 else text,
                    url=f"https://x.com/i/web/status/{tid}",
                    snippet=text,
                    published_at=t.get("created_at") or iso_now(),
                )
            )
    return out


def fetch_rss(cfg: dict[str, Any]) -> list[Item]:
    if not cfg.get("enabled"):
        return []
    per_feed = int(cfg.get("per_feed", 20))
    out: list[Item] = []
    for feed in cfg.get("feeds", []):
        try:
            xml = http_text(feed)
        except Exception:
            continue
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            continue
        items = root.findall(".//item") + root.findall(".//{http://www.w3.org/2005/Atom}entry")
        for it in items[:per_feed]:
            title = (it.findtext("title") or it.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
            link = (it.findtext("link") or "").strip()
            if not link:
                link_elem = it.find("{http://www.w3.org/2005/Atom}link")
                if link_elem is not None:
                    link = link_elem.attrib.get("href", "")
            desc = (
                it.findtext("description")
                or it.findtext("summary")
                or it.findtext("{http://www.w3.org/2005/Atom}summary")
                or ""
            ).strip()
            pub = (
                it.findtext("pubDate")
                or it.findtext("published")
                or it.findtext("updated")
                or it.findtext("{http://www.w3.org/2005/Atom}published")
                or it.findtext("{http://www.w3.org/2005/Atom}updated")
                or iso_now()
            )
            if title and link:
                out.append(
                    Item(
                        source="rss",
                        title=title,
                        url=link,
                        snippet=re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", desc)).strip()[:500],
                        published_at=pub,
                    )
                )
    return out


def fetch_github(cfg: dict[str, Any]) -> list[Item]:
    if not cfg.get("enabled"):
        return []
    per_repo = int(cfg.get("per_repo", 10))
    out: list[Item] = []
    for repo in cfg.get("repos", []):
        url = f"https://api.github.com/repos/{repo}/releases?per_page={max(1, min(per_repo, 100))}"
        try:
            data = http_json(url)
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        for rel in data:
            title = (rel.get("name") or rel.get("tag_name") or "").strip()
            link = rel.get("html_url") or ""
            body = (rel.get("body") or "").strip()
            pub = rel.get("published_at") or rel.get("created_at") or iso_now()
            if title and link:
                out.append(Item("github", title, link, body[:500], pub))
    return out


def fetch_reddit(cfg: dict[str, Any]) -> list[Item]:
    if not cfg.get("enabled"):
        return []
    per_sub = int(cfg.get("per_subreddit", 10))
    out: list[Item] = []
    for sub in cfg.get("subreddits", []):
        url = f"https://www.reddit.com/r/{sub}/new.json?limit={max(1, min(per_sub, 100))}"
        try:
            data = http_json(url)
        except Exception:
            continue
        posts = (((data or {}).get("data") or {}).get("children") or [])
        for p in posts:
            d = p.get("data", {})
            title = (d.get("title") or "").strip()
            permalink = d.get("permalink") or ""
            link = f"https://reddit.com{permalink}" if permalink else ""
            text = ((d.get("selftext") or "") or (d.get("url") or "")).strip()
            ts = d.get("created_utc")
            pub = (
                dt.datetime.fromtimestamp(float(ts), tz=dt.timezone.utc).isoformat()
                if ts is not None
                else iso_now()
            )
            if title and link:
                out.append(Item("reddit", title, link, text[:500], pub))
    return out


def normalize_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    q = urllib.parse.parse_qsl(parsed.query, keep_blank_values=False)
    q = [(k, v) for k, v in q if not k.lower().startswith("utm_")]
    query = urllib.parse.urlencode(sorted(q))
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", query, ""))


def dedupe(items: list[Item]) -> list[Item]:
    seen: set[str] = set()
    out: list[Item] = []
    for it in items:
        key = normalize_url(it.url) or hashlib.sha1((it.title + it.source).encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def score_item(it: Item, include: list[str], exclude: list[str], now: dt.datetime) -> float:
    txt = f"{it.title} {it.snippet}".lower()
    inc_hits = sum(1 for k in include if k.lower() in txt)
    exc_hits = sum(1 for k in exclude if k.lower() in txt)

    pub_dt = parse_rfc3339(it.published_at) or parse_rfc822(it.published_at) or now
    age_hours = max(0.0, (now - pub_dt).total_seconds() / 3600.0)
    freshness = max(0.0, 12.0 - min(age_hours, 72.0) / 6.0)

    source_weight = {"x": 2.0, "rss": 1.8, "github": 1.6, "reddit": 1.4}.get(it.source, 1.0)
    return (inc_hits * 2.5) + freshness + source_weight - (exc_hits * 3.0)


def summarize(items: list[Item]) -> str:
    lines = ["# Daily Creator Brief", "", f"Generated: {iso_now()}", "", "## Top 5"]
    for i, it in enumerate(items[:5], start=1):
        lines.append(f"{i}. [{it.title}]({it.url})")
        lines.append(f"   - source: {it.source} | score: {it.score:.2f}")
        if it.snippet:
            lines.append(f"   - note: {it.snippet[:220].replace(chr(10), ' ')}")
    return "\n".join(lines)


def social_draft(items: list[Item]) -> dict[str, str]:
    if not items:
        return {
            "x": "Today's signals are quiet. Reviewing AI/Web3 trends and watching for high-quality updates.",
            "linkedin": "Today's monitoring run found limited high-signal updates. We'll continue tracking AI/Web3 shifts and share actionable changes.",
        }
    topics = ", ".join([it.title[:60] for it in items[:2]])
    x_text = (
        f"Today's AI/Web3 signal snapshot: {topics}. "
        "Key theme: execution quality > hype. "
        "What are you seeing in your market today? #AI #Web3"
    )
    li_text = (
        "Daily AI/Web3 brief is in. Top signals indicate momentum around product execution, policy shifts, "
        f"and ecosystem updates ({topics}). "
        "If you build in this space, prioritize durable distribution and measurable outcomes this week."
    )
    return {"x": x_text[:280], "linkedin": li_text}


def deliver_telegram(text: str) -> str | None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return "telegram skipped: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"}).encode()
    req = urllib.request.Request(url, data=payload, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20):
            return None
    except Exception as e:
        return f"telegram error: {e}"


def deliver_slack(text: str) -> str | None:
    hook = os.getenv("SLACK_WEBHOOK_URL", "").strip()
    if not hook:
        return "slack skipped: SLACK_WEBHOOK_URL missing"
    req = urllib.request.Request(
        hook,
        data=json.dumps({"text": text}).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": UA},
    )
    try:
        with urllib.request.urlopen(req, timeout=20):
            return None
    except Exception as e:
        return f"slack error: {e}"


def deliver_email(subject: str, text: str) -> str | None:
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "").strip()
    pwd = os.getenv("SMTP_PASS", "").strip()
    to = os.getenv("EMAIL_TO", "").strip()
    if not (host and user and pwd and to):
        return "email skipped: SMTP or EMAIL_TO missing"

    msg = email.message.EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    msg.set_content(text)

    try:
        with smtplib.SMTP(host, port, timeout=20) as s:
            s.starttls()
            s.login(user, pwd)
            s.send_message(msg)
        return None
    except Exception as e:
        return f"email error: {e}"


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Creator monitor daily brief (kiroai.io)")
    ap.add_argument("--config", required=True, help="Path to JSON config")
    ap.add_argument("--out-dir", default="outputs/creator-brief", help="Output directory")
    ap.add_argument("--deliver", action="store_true", help="Deliver to configured channels")
    args = ap.parse_args()

    cfg = load_config(Path(args.config))
    include = cfg.get("topics", {}).get("include", []) or []
    exclude = cfg.get("topics", {}).get("exclude", []) or []
    sources = cfg.get("sources", {})

    items: list[Item] = []
    items.extend(fetch_x(sources.get("x", {})))
    items.extend(fetch_rss(sources.get("rss", {})))
    items.extend(fetch_github(sources.get("github", {})))
    items.extend(fetch_reddit(sources.get("reddit", {})))

    items = dedupe(items)
    now = dt.datetime.now(dt.timezone.utc)
    for it in items:
        it.score = score_item(it, include, exclude, now)

    ranked = sorted(items, key=lambda x: x.score, reverse=True)
    top5 = ranked[:5]
    draft = social_draft(top5)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": iso_now(),
        "total_items": len(items),
        "top5": [it.__dict__ for it in top5],
        "draft": draft,
    }
    (out_dir / "latest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md = summarize(top5) + "\n\n## Social Draft\n\n- X:\n\n" + draft["x"] + "\n\n- LinkedIn:\n\n" + draft["linkedin"] + "\n"
    (out_dir / "latest.md").write_text(md, encoding="utf-8")

    delivery_log: list[str] = []
    if args.deliver:
        text = md
        dcfg = cfg.get("delivery", {})
        if dcfg.get("telegram", {}).get("enabled"):
            err = deliver_telegram(text)
            delivery_log.append(err or "telegram ok")
        if dcfg.get("slack", {}).get("enabled"):
            err = deliver_slack(text)
            delivery_log.append(err or "slack ok")
        if dcfg.get("email", {}).get("enabled"):
            err = deliver_email("Kiro Daily Creator Brief", text)
            delivery_log.append(err or "email ok")

    print(json.dumps({"status": "ok", "out_dir": str(out_dir), "total": len(items), "delivery": delivery_log}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except urllib.error.HTTPError as e:
        print(f"HTTP error: {e.code} {e.reason}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)
