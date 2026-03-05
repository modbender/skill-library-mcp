#!/usr/bin/env python3
"""Memory salience scorer for heartbeat self-prompting.

Surfaces important-but-stale memory items. Scores: importance × staleness.
Factors: file type, size, access frequency, query gap correlation.

Usage:
    python3 memory_salience.py              # Top 3 human-readable prompts
    python3 memory_salience.py --json       # JSON output
    python3 memory_salience.py --top 5      # More items

Environment variables:
    MEMORY_DIR - Override memory directory path
"""

import json, os, sys, argparse
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(os.environ.get('MEMORY_DIR', Path(__file__).resolve().parent.parent.parent.parent)).resolve()
MEMORY_DIR = WORKSPACE / 'memory'
ACCESS_LOG = MEMORY_DIR / 'access_log.json'
QUERY_LOG = MEMORY_DIR / 'query_log.json'
NOW = datetime.now()


def load_json(path, default=None):
    if default is None:
        default = {}
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return default
    return default


def days_since_modified(path):
    try:
        return max(0, (NOW - datetime.fromtimestamp(os.path.getmtime(path))).days)
    except Exception:
        return 0


def get_memory_items():
    """Collect all scoreable memory items."""
    items = []

    # Topic files
    topics_dir = MEMORY_DIR / 'topics'
    if topics_dir.exists():
        for p in topics_dir.glob('*.md'):
            items.append({
                'path': str(p.relative_to(WORKSPACE)),
                'type': 'topic',
                'name': p.stem.replace('-', ' ').replace('_', ' '),
                'age_days': days_since_modified(p),
                'size': p.stat().st_size,
            })

    # Daily notes
    for p in MEMORY_DIR.glob('20??-??-??.md'):
        items.append({
            'path': str(p.relative_to(WORKSPACE)),
            'type': 'daily',
            'name': p.stem,
            'age_days': days_since_modified(p),
            'size': p.stat().st_size,
        })

    # MEMORY.md
    mem = WORKSPACE / 'MEMORY.md'
    if mem.exists():
        items.append({
            'path': 'MEMORY.md',
            'type': 'core',
            'name': 'Long-term memory',
            'age_days': days_since_modified(mem),
            'size': mem.stat().st_size,
        })

    return items


def get_query_gaps(query_log):
    """Find recent queries with low scores (potential knowledge gaps)."""
    if not query_log:
        return []
    return [e for e in query_log[-50:] if (e.get('top_score') or 0) < 0.4]


def score_salience(items, access_log, query_gaps):
    """Score each item: salience = importance × staleness."""
    scored = []
    for item in items:
        base = {'topic': 0.7, 'core': 0.8, 'daily': 0.4}[item['type']]
        size_bonus = min(0.1, item['size'] / 50000)
        accesses = access_log.get(item['path'], 0)
        access_penalty = min(0.2, accesses * 0.03)

        gap_bonus = 0
        for gap in query_gaps:
            if any(word in item['name'].lower() for word in gap['query'].lower().split()):
                gap_bonus = 0.15
                break

        importance = min(1.0, base + size_bonus - access_penalty + gap_bonus)
        age = item['age_days']
        staleness = min(1.0, age / (7 if item['type'] == 'daily' else 5))
        salience = importance * staleness

        scored.append({**item, 'importance': round(importance, 3),
                       'staleness': round(staleness, 3), 'salience': round(salience, 3),
                       'accesses': accesses})

    scored.sort(key=lambda x: -x['salience'])
    return scored


def generate_prompts(scored, top_n=3):
    """Generate natural-language prompts from top salient items."""
    prompts = []
    for item in scored[:top_n]:
        if item['salience'] < 0.05:
            continue
        if item['type'] == 'topic':
            if item['age_days'] > 3:
                prompts.append(f"📌 Topic '{item['name']}' hasn't been updated in {item['age_days']} days.")
            elif item['accesses'] == 0:
                prompts.append(f"📌 Topic '{item['name']}' was never accessed by search.")
        elif item['type'] == 'daily':
            prompts.append(f"📝 Daily notes from {item['name']} haven't been reviewed for MEMORY.md.")
        elif item['type'] == 'core' and item['age_days'] > 2:
            prompts.append(f"🧠 MEMORY.md last updated {item['age_days']} days ago.")
    return prompts


def main():
    parser = argparse.ArgumentParser(description='Memory salience scorer')
    parser.add_argument('--top', type=int, default=3)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    access_log = load_json(ACCESS_LOG, {})
    query_log = load_json(QUERY_LOG, [])
    items = get_memory_items()
    scored = score_salience(items, access_log, get_query_gaps(query_log))

    if args.json:
        print(json.dumps({
            'timestamp': NOW.isoformat(),
            'items': scored[:args.top],
            'prompts': generate_prompts(scored, args.top),
            'total_items': len(items),
        }, indent=2))
    else:
        prompts = generate_prompts(scored, args.top)
        for p in prompts:
            print(p)
        if not prompts:
            print("All memory items are fresh. Nothing to surface.")


if __name__ == '__main__':
    main()
