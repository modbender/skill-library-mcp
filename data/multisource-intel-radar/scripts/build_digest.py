#!/usr/bin/env python3
import argparse
import datetime as dt
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime


def read_feeds(path):
    feeds = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or '\t' not in line:
                continue
            title, url = line.split('\t', 1)
            feeds.append((title, url))
    return feeds


def extract_items(xml_text):
    items = []
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return items

    for it in root.findall('.//item'):
        items.append({
            'title': (it.findtext('title') or '').strip(),
            'link': (it.findtext('link') or '').strip(),
            'desc': (it.findtext('description') or '').strip(),
            'pub': (it.findtext('pubDate') or '').strip(),
        })

    for it in root.findall('{http://www.w3.org/2005/Atom}entry'):
        link_el = it.find('{http://www.w3.org/2005/Atom}link')
        items.append({
            'title': (it.findtext('{http://www.w3.org/2005/Atom}title') or '').strip(),
            'link': (link_el.attrib.get('href') if link_el is not None else '') or '',
            'desc': (it.findtext('{http://www.w3.org/2005/Atom}summary') or it.findtext('{http://www.w3.org/2005/Atom}content') or '').strip(),
            'pub': (it.findtext('{http://www.w3.org/2005/Atom}updated') or it.findtext('{http://www.w3.org/2005/Atom}published') or '').strip(),
        })

    return items


def parse_dt(s):
    if not s:
        return None
    try:
        return parsedate_to_datetime(s)
    except Exception:
        pass
    try:
        return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
    except Exception:
        return None


def score(text, keywords):
    t = text.lower()
    k_hits = sum(1 for k in keywords if k.lower() in t)
    if k_hits == 0:
        return 0
    rel = min(40, k_hits * 15)
    actionable = 20 if any(x in t for x in ['how', '模板', '步骤', 'framework', 'playbook', 'case', 'strategy']) else 8
    novelty = 15 if any(x in t for x in ['new', '首次', '发布', '开源', '融资', '增长']) else 6
    evidence = 10 if any(x in t for x in ['data', '数据', '%', 'million', '亿', '报告']) else 4
    return rel + actionable + novelty + evidence


def pct(n, d):
    return f"{(100*n/d):.1f}%" if d else '0.0%'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feeds', required=True)
    ap.add_argument('--keywords', default='创业,AI,增长,金融')
    ap.add_argument('--hours', type=int, default=48)
    ap.add_argument('--limit', type=int, default=10)
    ap.add_argument('--max-feeds', type=int, default=20)
    args = ap.parse_args()

    keywords = [k.strip() for k in args.keywords.split(',') if k.strip()]
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=args.hours)

    total_feeds = 0
    feed_ok = 0
    total_items = 0
    keyword_matched = 0
    time_filtered = 0

    candidates = []
    for src_title, url in read_feeds(args.feeds)[: args.max_feeds]:
        total_feeds += 1
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=12) as r:
                xml_text = r.read().decode('utf-8', errors='ignore')
            feed_ok += 1
        except Exception:
            continue

        items = extract_items(xml_text)
        total_items += len(items)

        for it in items:
            text = f"{it['title']} {it['desc']}"
            sc = score(text, keywords)
            if sc <= 0:
                continue
            keyword_matched += 1

            pub_dt = parse_dt(it['pub'])
            if pub_dt and pub_dt.tzinfo is None:
                pub_dt = pub_dt.replace(tzinfo=dt.timezone.utc)
            if pub_dt and pub_dt < cutoff:
                time_filtered += 1
                continue

            candidates.append({
                'score': sc,
                'source': src_title,
                'title': it['title'][:180],
                'link': it['link'],
            })

    candidates.sort(key=lambda x: x['score'], reverse=True)
    picked = candidates[: args.limit]
    top3 = picked[:3]

    print('=== FILTER TRANSPARENCY ===')
    print(f"feeds_scanned: {total_feeds}")
    print(f"feeds_reachable: {feed_ok} ({pct(feed_ok,total_feeds)})")
    print(f"items_collected: {total_items}")
    print(f"keyword_matched: {keyword_matched} ({pct(keyword_matched,total_items)})")
    print(f"time_window_kept: {len(candidates)} ({pct(len(candidates),keyword_matched)})")
    print(f"final_selected: {len(picked)} ({pct(len(picked),len(candidates))})")
    print(f"top3_selected: {len(top3)} ({pct(len(top3),len(candidates))} of candidates)")

    print('\n=== TOP 3 MUST-READ ===')
    for i, c in enumerate(top3, 1):
        print(f"{i}. [{c['score']}] {c['title']} ({c['source']}) -> {c['link']}")

    print('\n=== WATCHLIST ===')
    for i, c in enumerate(picked[3:8], 4):
        print(f"{i}. [{c['score']}] {c['title']} ({c['source']}) -> {c['link']}")


if __name__ == '__main__':
    main()
