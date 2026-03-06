#!/usr/bin/env python3
import json
import os
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple

import requests
import xml.etree.ElementTree as ET

FEED_URL = "https://traffic.houstontranstar.org/data/rss/incidents_rss.xml"
STATE_DIR = os.path.join(
    os.path.expanduser("~"),
    ".openclaw",
    "skills",
    "houston-transtar-watch",
    "state",
)
STATE_FILE = os.path.join(STATE_DIR, "last_incidents.json")


@dataclass(frozen=True)
class Incident:
    id: str
    title: str
    description: str
    link: str
    pub_date: str

    @staticmethod
    def from_xml_item(item: ET.Element) -> "Incident":
        # RSS usually has title, description, link, guid, pubDate. [web:36][web:39]
        title = (item.findtext("title") or "").strip()
        description = (item.findtext("description") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()

        # Prefer guid if present, otherwise fall back to link or title+pub_date
        if guid:
            inc_id = guid
        elif link:
            inc_id = link
        else:
            inc_id = f"{title}|{pub_date}"

        return Incident(
            id=inc_id,
            title=title,
            description=description,
            link=link,
            pub_date=pub_date,
        )


def fetch_feed() -> bytes:
    resp = requests.get(FEED_URL, timeout=10)
    resp.raise_for_status()
    return resp.content


def parse_incidents(xml_bytes: bytes) -> List[Incident]:
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    if channel is None:
        return []
    items = channel.findall("item")
    incidents: List[Incident] = []
    for item in items:
        incidents.append(Incident.from_xml_item(item))
    return incidents


def load_last_snapshot() -> Dict[str, Dict]:
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # If corrupt, ignore and start fresh
        return {}


def save_snapshot(incidents: List[Incident]) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    data = {inc.id: asdict(inc) for inc in incidents}
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def diff_incidents(
    old: Dict[str, Dict], new: Dict[str, Dict]
) -> Tuple[List[Dict], List[Dict], List[Tuple[Dict, Dict]]]:
    old_ids = set(old.keys())
    new_ids = set(new.keys())

    added_ids = new_ids - old_ids
    removed_ids = old_ids - new_ids
    common_ids = old_ids & new_ids

    added = [new[i] for i in sorted(added_ids)]
    removed = [old[i] for i in sorted(removed_ids)]

    changed: List[Tuple[Dict, Dict]] = []
    for i in sorted(common_ids):
        if old[i] != new[i]:
            changed.append((old[i], new[i]))

    return added, removed, changed


def format_summary(
    added: List[Dict], removed: List[Dict], changed: List[Tuple[Dict, Dict]]
) -> str:
    if not added and not removed and not changed:
        return "NO_CHANGES"

    lines = []
    lines.append(
        f"Houston TranStar incidents update:\n"
        f"- New: {len(added)}\n"
        f"- Cleared: {len(removed)}\n"
        f"- Updated: {len(changed)}"
    )

    if added:
        lines.append("\nNew incidents:")
        for inc in added[:5]:
            title = inc.get("title", "")
            desc = inc.get("description", "")
            link = inc.get("link", "")
            lines.append(f"• {title}")
            if desc:
                lines.append(f"  {desc}")
            if link:
                lines.append(f"  {link}")

    if removed:
        lines.append("\nCleared incidents:")
        for inc in removed[:5]:
            title = inc.get("title", "")
            desc = inc.get("description", "")
            lines.append(f"• {title}")
            if desc:
                lines.append(f"  {desc}")

    if changed:
        lines.append("\nUpdated incidents:")
        for old_inc, new_inc in changed[:5]:
            title = new_inc.get("title") or old_inc.get("title", "")
            lines.append(f"• {title}")
            old_desc = (old_inc.get("description") or "").strip()
            new_desc = (new_inc.get("description") or "").strip()
            if old_desc != new_desc and new_desc:
                lines.append(f"  New details: {new_desc}")

    # If there are many, hint that list is truncated
    total_shown = (
        min(len(added), 5) + min(len(removed), 5) + min(len(changed), 5)
    )
    total = len(added) + len(removed) + len(changed)
    if total > total_shown:
        lines.append(f"\n(+ {total - total_shown} more changes not listed)")

    return "\n".join(lines)


def main() -> int:
    try:
        xml_bytes = fetch_feed()
    except Exception as e:
        # For OpenClaw: on error, print a short message so you see it in logs.
        print(f"ERROR fetching feed: {e}")
        return 1

    try:
        incidents = parse_incidents(xml_bytes)
    except Exception as e:
        print(f"ERROR parsing feed: {e}")
        return 1

    new_snapshot = {inc.id: asdict(inc) for inc in incidents}
    old_snapshot = load_last_snapshot()

    added, removed, changed = diff_incidents(old_snapshot, new_snapshot)
    summary = format_summary(added, removed, changed)

    # Save the new snapshot regardless, so next run compares against this.
    try:
        save_snapshot(incidents)
    except Exception as e:
        # Not fatal for current run.
        print(f"ERROR saving state: {e}", file=sys.stderr)

    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

