#!/usr/bin/env python3
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_opml(path: Path):
    tree = ET.parse(path)
    root = tree.getroot()
    feeds = []
    for o in root.findall('.//outline'):
        url = o.attrib.get('xmlUrl') or o.attrib.get('url')
        if not url:
            continue
        title = o.attrib.get('text') or o.attrib.get('title') or url
        feeds.append((title.strip(), url.strip()))
    # dedupe by url
    seen = set()
    out = []
    for t, u in feeds:
        if u in seen:
            continue
        seen.add(u)
        out.append((t, u))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--opml', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    feeds = parse_opml(Path(args.opml))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8') as f:
        for title, url in feeds:
            f.write(f"{title}\t{url}\n")
    print(f"wrote {len(feeds)} feeds -> {out}")


if __name__ == '__main__':
    main()
